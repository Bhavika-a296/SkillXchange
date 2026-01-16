from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from .models import LearningSession, SkillRating, Notification
from .serializers import SkillRatingSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_rating(request, session_id):
    """
    Submit rating and feedback for a completed learning session
    Expected payload:
    {
        "rating": int (1-5),
        "feedback": str (optional)
    }
    """
    rating_value = request.data.get('rating')
    feedback = request.data.get('feedback', '')
    
    if not rating_value or rating_value not in [1, 2, 3, 4, 5]:
        return Response(
            {'error': 'Rating must be between 1 and 5'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        learning_session = LearningSession.objects.get(id=session_id)
    except LearningSession.DoesNotExist:
        return Response(
            {'error': 'Learning session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is part of the session
    if request.user not in [learning_session.learner, learning_session.teacher]:
        return Response(
            {'error': 'You are not part of this learning session'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if session is completed
    if learning_session.status != 'completed':
        return Response(
            {'error': 'Can only rate completed learning sessions'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Determine who is being rated
    if request.user == learning_session.learner:
        rated_user = learning_session.teacher
    else:
        rated_user = learning_session.learner
    
    # Check if already rated
    existing_rating = SkillRating.objects.filter(
        learning_session=learning_session,
        rater=request.user
    ).first()
    
    if existing_rating:
        return Response(
            {'error': 'You have already rated this learning session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create rating
    with transaction.atomic():
        skill_rating = SkillRating.objects.create(
            learning_session=learning_session,
            rater=request.user,
            rated_user=rated_user,
            rating=rating_value,
            feedback=feedback
        )
        
        # Create notification
        Notification.objects.create(
            user=rated_user,
            notification_type='skill_match',
            title=f'{request.user.username} rated you {rating_value}/5',
            message=feedback[:100] if feedback else f'You received a {rating_value}-star rating',
            sender=request.user,
            link=f'/profile/{request.user.username}'
        )
    
    serializer = SkillRatingSerializer(skill_rating)
    return Response({
        'message': 'Rating submitted successfully',
        'rating': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_ratings(request, session_id):
    """Get all ratings for a specific learning session"""
    try:
        from django.db.models import Q
        learning_session = LearningSession.objects.get(
            Q(id=session_id) & 
            (Q(learner=request.user) | Q(teacher=request.user))
        )
    except LearningSession.DoesNotExist:
        return Response(
            {'error': 'Learning session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ratings = SkillRating.objects.filter(learning_session=learning_session)
    serializer = SkillRatingSerializer(ratings, many=True)
    
    # Check if current user has rated
    user_has_rated = ratings.filter(rater=request.user).exists()
    can_rate = learning_session.status == 'completed' and not user_has_rated
    
    return Response({
        'ratings': serializer.data,
        'can_rate': can_rate,
        'session_status': learning_session.status
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_ratings(request, username=None):
    """
    Get all ratings received by a user
    Query params:
    - as_learner: true/false (filter ratings received as learner)
    - as_teacher: true/false (filter ratings received as teacher)
    """
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = request.user
    
    ratings = SkillRating.objects.filter(rated_user=user).select_related(
        'learning_session', 'rater'
    )
    
    # Filter by role if specified
    as_learner = request.query_params.get('as_learner')
    as_teacher = request.query_params.get('as_teacher')
    
    if as_learner == 'true':
        ratings = ratings.filter(learning_session__learner=user)
    elif as_teacher == 'true':
        ratings = ratings.filter(learning_session__teacher=user)
    
    serializer = SkillRatingSerializer(ratings, many=True)
    
    # Calculate average rating
    if ratings.exists():
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
    else:
        avg_rating = 0
    
    return Response({
        'ratings': serializer.data,
        'average_rating': round(avg_rating, 2),
        'total_ratings': len(ratings)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_can_rate(request, session_id):
    """Check if current user can rate a learning session"""
    try:
        from django.db.models import Q
        learning_session = LearningSession.objects.get(
            Q(id=session_id) & 
            (Q(learner=request.user) | Q(teacher=request.user))
        )
    except LearningSession.DoesNotExist:
        return Response(
            {'error': 'Learning session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already rated
    has_rated = SkillRating.objects.filter(
        learning_session=learning_session,
        rater=request.user
    ).exists()
    
    can_rate = learning_session.status == 'completed' and not has_rated
    
    return Response({
        'can_rate': can_rate,
        'session_status': learning_session.status,
        'has_rated': has_rated,
        'reason': 'Session not completed' if learning_session.status != 'completed' 
                  else ('Already rated' if has_rated else 'Can rate')
    }, status=status.HTTP_200_OK)
