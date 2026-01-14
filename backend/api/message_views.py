from rest_framework import permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from .models import Message
from .serializers import MessageSerializer
from .ably_utils import get_channel_name, publish_message, publish_message_sync, generate_client_token
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

@method_decorator(csrf_protect, name='dispatch')
class AsyncAuthAPIView(APIView):
    """Base class for async API views that handles authentication properly"""
    
    async def get_authenticated_user(self, request):
        if not hasattr(request, "_authenticator"):
            # Get the user asynchronously from the session
            user = await sync_to_async(lambda: request.user)()
            if not isinstance(user, AnonymousUser):
                return user

            # Try token authentication
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Token '):
                token = auth_header.split(' ')[1]
                # Use sync_to_async to handle token authentication
                try:
                    from rest_framework.authtoken.models import Token
                    token_obj = await sync_to_async(Token.objects.select_related('user').get)(key=token)
                    return token_obj.user
                except Token.DoesNotExist:
                    return None
        return None

    async def initial(self, request, *args, **kwargs):
        user = await self.get_authenticated_user(request)
        if user is None or isinstance(user, AnonymousUser):
            raise exceptions.NotAuthenticated()
        request.user = user
        return None

class AblyTokenView(APIView):
    """Synchronous view that returns an Ably token for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        token_request = generate_client_token(request.user.id)
        # token_request is a dict-like object with keys: keyName, timestamp, nonce, mac, capability, clientId
        # The frontend Ably client can use this token request directly
        return Response(token_request)


class MessageView(APIView):
    """Synchronous message list/create endpoint.

    This view uses the synchronous Django ORM and a synchronous helper to
    publish to Ably so it will always return a real Response object
    (not a coroutine).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        other_id = request.GET.get('with')
        if not other_id:
            return Response({'error': 'Query parameter "with" required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to get by ID first, if it fails, try by username
            try:
                other = User.objects.get(id=int(other_id))
            except (ValueError, TypeError):
                # If other_id is not a number, try to get by username
                other = User.objects.get(username=other_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check connection status
        from .models import Connection
        connection = Connection.objects.filter(
            models.Q(requester=request.user, receiver=other) |
            models.Q(requester=other, receiver=request.user)
        ).first()

        # Get messages between request.user and other
        messages = Message.objects.filter(
            (models.Q(sender=request.user, receiver=other)) |
            (models.Q(sender=other, receiver=request.user))
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        
        # Include connection status in response
        connection_status = connection.status if connection else None
        connection_id = connection.id if connection else None
        is_requester = connection.requester.id == request.user.id if connection else None
        
        return Response({
            'messages': serializer.data,
            'connection_status': connection_status,
            'connection_id': connection_id,
            'is_requester': is_requester
        })

    def post(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver')
        content = request.data.get('content', '')
        file = request.FILES.get('file')
        
        if not receiver_id:
            return Response({'error': 'receiver is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not content and not file:
            return Response({'error': 'content or file is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if connection exists between users
        from .models import Connection
        connection = Connection.objects.filter(
            models.Q(requester=request.user, receiver=receiver) |
            models.Q(requester=receiver, receiver=request.user)
        ).first()

        # If no connection exists, create a pending one (first message = connection request)
        if not connection:
            connection = Connection.objects.create(
                requester=request.user,
                receiver=receiver,
                status='pending'
            )
        # If connection was rejected, don't allow messaging
        elif connection.status == 'rejected':
            return Response(
                {'error': 'Connection request was rejected. You cannot message this user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # If connection is pending and current user is not the requester, don't allow
        elif connection.status == 'pending' and connection.requester != request.user:
            return Response(
                {'error': 'You must accept the connection request before messaging.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create and save the message (synchronous)
        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            file=file
        )
        serializer = MessageSerializer(msg, context={'request': request})

        # Publish to Ably synchronously so we don't return a coroutine
        channel_name = get_channel_name(request.user.id, receiver.id)
        message_data = {'type': 'message', 'message': serializer.data}
        try:
            publish_message_sync(channel_name, message_data)
        except Exception:
            # Don't fail the request if publish fails; log in real app
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationsListView(APIView):
    """Get list of all users the authenticated user has messaged with."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from django.db.models import Q, Max, OuterRef, Subquery
        
        # Get all users that current user has exchanged messages with
        sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True).distinct()
        received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True).distinct()
        
        # Combine and get unique user IDs
        user_ids = set(list(sent_to) + list(received_from))
        
        if not user_ids:
            return Response({'conversations': []})
        
        # Get users and their last message
        users = User.objects.filter(id__in=user_ids)
        
        conversations = []
        for user in users:
            # Get last message between current user and this user
            last_message = Message.objects.filter(
                Q(sender=request.user, receiver=user) |
                Q(sender=user, receiver=request.user)
            ).order_by('-created_at').first()
            
            conversations.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_message': last_message.content if last_message else None,
                'last_message_time': last_message.created_at if last_message else None
            })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message_time'] if x['last_message_time'] else '', reverse=True)
        
        return Response({'conversations': conversations})
