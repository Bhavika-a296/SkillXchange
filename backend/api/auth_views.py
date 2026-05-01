from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from .auth_serializers import RegisterSerializer, LoginSerializer
from .models import UserProfile, UserActivitySession, DailyLogin


def _close_open_activity_sessions(user, end_time):
    """Close any previously open sessions for a user."""
    max_session_seconds = 12 * 3600
    open_sessions = UserActivitySession.objects.filter(user=user, logout_time__isnull=True)
    for session in open_sessions:
        duration = max(0, int((end_time - session.login_time).total_seconds()))
        duration = min(duration, max_session_seconds)
        session.logout_time = end_time
        session.duration_seconds = duration
        session.save(update_fields=['logout_time', 'duration_seconds'])

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        print("Request method:", request.method)
        print("Content type:", request.content_type)
        print("Received data:", request.data)
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username
                }, status=status.HTTP_201_CREATED)
        
        print("Validation errors:", serializer.errors)
        return Response({
            'status': 'error',
            'errors': serializer.errors,
            'message': 'Invalid registration data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("Exception during registration:", str(e))
        # If there's an error, make sure we clean up any partially created data
        with transaction.atomic():
            user = User.objects.filter(username=request.data.get('username')).first()
            if user:
                user.delete()
        return Response({
            'status': 'error',
            'message': 'Registration failed. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_username(request, username):
    exists = User.objects.filter(username=username).exists()
    if exists:
        # Generate suggestion by adding a random number
        import random
        suggestion = f"{username}_{random.randint(1, 999)}"
        while User.objects.filter(username=suggestion).exists():
            suggestion = f"{username}_{random.randint(1, 999)}"
        
        return Response({
            'available': False,
            'suggestion': suggestion
        })
    return Response({'available': True})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        print("Login Request Data:", request.data)  # Debug print
        
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)  # Debug print
            return Response({
                'status': 'error',
                'errors': serializer.errors,
                'message': 'Invalid login data'
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        print(f"Attempting login for user: {username}")  # Debug print
        
        # Try case-insensitive username lookup
        user_obj = User.objects.filter(username__iexact=username).first()
        if user_obj:
            # Use the actual username for authentication
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None
        
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            # Start a fresh tracked activity session at login.
            now = timezone.now()
            _close_open_activity_sessions(user, now)
            UserActivitySession.objects.create(user=user, login_time=now)
            
            # Create daily login record for days active tracking
            DailyLogin.objects.get_or_create(user=user, login_date=now.date())

            return Response({
                'status': 'success',
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            print(f"Authentication failed for user: {username}")  # Debug print
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug print
        return Response({
            'status': 'error',
            'message': 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete the currently authenticated user's account permanently."""
    try:
        username = request.user.username
        request.user.delete()
        return Response({
            'status': 'success',
            'message': f'Account {username} deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Delete account error: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Could not delete account. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout current user and close tracked activity session."""
    try:
        now = timezone.now()
        _close_open_activity_sessions(request.user, now)

        # Invalidate token for current session.
        Token.objects.filter(user=request.user).delete()

        return Response({'status': 'success', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return Response({'status': 'error', 'message': 'Logout failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)