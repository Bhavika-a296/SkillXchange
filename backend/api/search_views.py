from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Skill, UserProfile
from .serializers import UserProfileSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    q = request.GET.get('q', '')
    skill_level = request.GET.get('skill_level', 'all')
    category = request.GET.get('category', 'all')

    # Start with all users except the current user
    queryset = User.objects.exclude(id=request.user.id)

    # Apply search query if provided
    if q:
        # If the query exactly matches a username (case-insensitive), return that profile only.
        try:
            exact_user = User.objects.get(username__iexact=q)
            if exact_user.id != request.user.id:
                profile = UserProfile.objects.filter(user=exact_user).first()
                if profile:
                    serializer = UserProfileSerializer(profile)
                    return Response({
                        'results': [serializer.data],
                        'count': 1
                    })
        except User.DoesNotExist:
            # No exact username match, continue with broader search
            pass

        queryset = queryset.filter(
            Q(username__icontains=q) |
            Q(userprofile__bio__icontains=q) |
            Q(skills__name__icontains=q)
        ).distinct()

    # Apply skill level filter
    if skill_level != 'all':
        queryset = queryset.filter(skills__proficiency_level=skill_level)

    # Apply category filter if provided
    if category != 'all':
        # You can add category filtering logic here based on your needs
        pass

    # Get the profiles for the filtered users
    profiles = UserProfile.objects.filter(user__in=queryset)
    serializer = UserProfileSerializer(profiles, many=True)

    return Response({
        'results': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_by_username(request, username):
    """Return the public profile for a given username."""
    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)