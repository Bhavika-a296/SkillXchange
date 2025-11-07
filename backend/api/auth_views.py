from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from .auth_serializers import RegisterSerializer, LoginSerializer
from .models import UserProfile

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
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
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