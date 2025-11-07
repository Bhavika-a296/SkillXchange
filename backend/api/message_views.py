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
            other = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get messages between request.user and other
        messages = Message.objects.filter(
            (models.Q(sender=request.user, receiver=other)) |
            (models.Q(sender=other, receiver=request.user))
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response({'messages': serializer.data})

    def post(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver')
        content = request.data.get('content')
        if not receiver_id or not content:
            return Response({'error': 'receiver and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create and save the message (synchronous)
        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        serializer = MessageSerializer(msg)

        # Publish to Ably synchronously so we don't return a coroutine
        channel_name = get_channel_name(request.user.id, receiver.id)
        message_data = {'type': 'message', 'message': serializer.data}
        try:
            publish_message_sync(channel_name, message_data)
        except Exception:
            # Don't fail the request if publish fails; log in real app
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)