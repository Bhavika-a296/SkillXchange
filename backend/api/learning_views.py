from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    LearningSession, UserPoints, PointTransaction, 
    PointConfiguration, SkillRating, Notification, Badge
)
from .serializers import (
    LearningSessionSerializer, PointTransactionSerializer,
    SkillRatingSerializer, BadgeSerializer
)


def get_point_config(config_name, default_value):
    """Helper function to get point configuration value"""
    try:
        config = PointConfiguration.objects.get(name=config_name)
        return config.value
    except PointConfiguration.DoesNotExist:
        return default_value


def check_and_award_badges(user):
    """Check if user has earned any new badges and award them"""
    badges_awarded = []
    
    # Count completed learning sessions as learner
    learner_count = LearningSession.objects.filter(
        learner=user,
        status='completed'
    ).values('skill_name').distinct().count()
    
    # Count completed learning sessions as teacher
    teacher_count = LearningSession.objects.filter(
        teacher=user,
        status='completed'
    ).values('skill_name').distinct().count()
    
    # Check learner badges
    learner_badges = [
        (3, 'learner_3'),
        (5, 'learner_5'),
        (10, 'learner_10'),
    ]
    
    for threshold, badge_type in learner_badges:
        if learner_count >= threshold:
            badge, created = Badge.objects.get_or_create(
                user=user,
                badge_type=badge_type
            )
            if created:
                badges_awarded.append(badge)
                # Create notification
                Notification.objects.create(
                    user=user,
                    notification_type='skill_match',
                    title='🏆 New Badge Earned!',
                    message=f'Congratulations! You earned the "{badge.get_badge_type_display()}" badge!',
                    link='/profile'
                )
    
    # Check teacher badges
    teacher_badges = [
        (3, 'teacher_3'),
        (5, 'teacher_5'),
        (10, 'teacher_10'),
    ]
    
    for threshold, badge_type in teacher_badges:
        if teacher_count >= threshold:
            badge, created = Badge.objects.get_or_create(
                user=user,
                badge_type=badge_type
            )
            if created:
                badges_awarded.append(badge)
                # Create notification
                Notification.objects.create(
                    user=user,
                    notification_type='skill_match',
                    title='🏆 New Badge Earned!',
                    message=f'Congratulations! You earned the "{badge.get_badge_type_display()}" badge!',
                    link='/profile'
                )
    
    return badges_awarded


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_learning(request):
    """
    Send a learning request to a teacher
    Expected payload:
    {
        "teacher_id": int,
        "skill_name": str,
        "total_days": int (optional, defaults to config or 30)
    }
    """
    teacher_id = request.data.get('teacher_id')
    skill_name = request.data.get('skill_name')
    total_days = request.data.get('total_days')
    
    if not teacher_id or not skill_name:
        return Response(
            {'error': 'teacher_id and skill_name are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or set default learning period
    if not total_days:
        total_days = get_point_config('default_learning_period_days', 30)
    
    try:
        teacher = User.objects.get(id=teacher_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Teacher not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    learner = request.user
    
    # Prevent self-learning
    if learner.id == teacher.id:
        return Response(
            {'error': 'You cannot start a learning session with yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get point deduction amount from configuration
    points_to_deduct = get_point_config('join_learning_cost', 100)
    
    # Check if learner has enough points (but don't deduct yet)
    user_points, created = UserPoints.objects.get_or_create(
        user=learner,
        defaults={'balance': 0}
    )
    
    if user_points.balance < points_to_deduct:
        return Response(
            {
                'error': 'Insufficient points',
                'current_balance': user_points.balance,
                'required': points_to_deduct
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for existing pending or active session with same teacher and skill
    existing_session = LearningSession.objects.filter(
        learner=learner,
        teacher=teacher,
        skill_name=skill_name,
        status__in=['pending', 'in_progress']
    ).first()
    
    if existing_session:
        return Response(
            {'error': f'You already have a {existing_session.status} session for this skill with this teacher'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create learning request (pending status, no points deducted yet)
    with transaction.atomic():
        learning_session = LearningSession.objects.create(
            learner=learner,
            teacher=teacher,
            skill_name=skill_name,
            status='pending',
            total_days=total_days,
            points_deducted=0  # Will be set when accepted
        )
        
        # Create notification for teacher
        Notification.objects.create(
            user=teacher,
            notification_type='skill_match',
            title=f'Learning Request from {learner.username}',
            message=f'{learner.username} wants to learn {skill_name} from you',
            link=f'/learning-requests',
            sender=learner
        )
    
    from .serializers import LearningSessionSerializer
    serializer = LearningSessionSerializer(learning_session)
    return Response({
        'message': 'Learning request sent successfully. Waiting for teacher approval.',
        'learning_session': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_learning(request, session_id):
    """
    End a learning session and award points
    Only learner or teacher can end the session
    """
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
    
    # Check if already completed
    if learning_session.status == 'completed':
        return Response(
            {'error': 'Learning session already completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get point reward amounts from configuration
    learner_reward = get_point_config('learning_completion_reward_learner', 50)
    teacher_reward = get_point_config('learning_completion_reward_teacher', 150)
    
    with transaction.atomic():
        # Update learning session
        learning_session.status = 'completed'
        learning_session.end_date = timezone.now()
        learning_session.points_awarded_learner = learner_reward
        learning_session.points_awarded_teacher = teacher_reward
        learning_session.save()
        
        # Award points to learner
        learner_points, _ = UserPoints.objects.get_or_create(
            user=learning_session.learner,
            defaults={'balance': 0}
        )
        learner_points.balance += learner_reward
        learner_points.total_earned += learner_reward
        learner_points.save()
        
        PointTransaction.objects.create(
            user=learning_session.learner,
            transaction_type='complete_learning_learner',
            amount=learner_reward,
            balance_after=learner_points.balance,
            description=f'Completed learning {learning_session.skill_name} with {learning_session.teacher.username}'
        )
        
        # Award points to teacher
        teacher_points, _ = UserPoints.objects.get_or_create(
            user=learning_session.teacher,
            defaults={'balance': 0}
        )
        teacher_points.balance += teacher_reward
        teacher_points.total_earned += teacher_reward
        teacher_points.save()
        
        PointTransaction.objects.create(
            user=learning_session.teacher,
            transaction_type='complete_learning_teacher',
            amount=teacher_reward,
            balance_after=teacher_points.balance,
            description=f'Taught {learning_session.skill_name} to {learning_session.learner.username}'
        )
        
        # Create notifications
        Notification.objects.create(
            user=learning_session.learner,
            notification_type='skill_match',
            title=f'Learning session completed!',
            message=f'You completed learning {learning_session.skill_name}. You earned {learner_reward} points!',
            link=f'/profile/{learning_session.learner.username}'
        )
        
        Notification.objects.create(
            user=learning_session.teacher,
            notification_type='skill_match',
            title=f'Teaching session completed!',
            message=f'Teaching session for {learning_session.skill_name} completed. You earned {teacher_reward} points!',
            link=f'/profile/{learning_session.teacher.username}'
        )
        
        # Check and award badges for both users
        learner_badges = check_and_award_badges(learning_session.learner)
        teacher_badges = check_and_award_badges(learning_session.teacher)
    
    serializer = LearningSessionSerializer(learning_session)
    return Response({
        'message': 'Learning session completed successfully',
        'learning_session': serializer.data,
        'learner_reward': learner_reward,
        'teacher_reward': teacher_reward,
        'new_badges': {
            'learner': [{'type': b.badge_type, 'icon': b.badge_icon, 'name': b.get_badge_type_display()} for b in learner_badges],
            'teacher': [{'type': b.badge_type, 'icon': b.badge_icon, 'name': b.get_badge_type_display()} for b in teacher_badges]
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_sessions(request):
    """
    Get all learning sessions for the current user
    Query params:
    - role: 'learner' | 'teacher' | 'all' (default: 'all')
    - status: 'in_progress' | 'completed' | 'cancelled' | 'all' (default: 'all')
    """
    role = request.query_params.get('role', 'all')
    session_status = request.query_params.get('status', 'all')
    
    # Base query
    if role == 'learner':
        sessions = LearningSession.objects.filter(learner=request.user)
    elif role == 'teacher':
        sessions = LearningSession.objects.filter(teacher=request.user)
    else:
        sessions = LearningSession.objects.filter(
            Q(learner=request.user) | Q(teacher=request.user)
        )
    
    # Filter by status
    if session_status != 'all':
        sessions = sessions.filter(status=session_status)
    
    serializer = LearningSessionSerializer(sessions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_session_detail(request, session_id):
    """Get details of a specific learning session"""
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
    
    serializer = LearningSessionSerializer(learning_session)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_learning_request(request, session_id):
    """Teacher accepts a learning request and starts the session"""
    try:
        learning_session = LearningSession.objects.get(
            id=session_id,
            teacher=request.user,
            status='pending'
        )
    except LearningSession.DoesNotExist:
        return Response(
            {'error': 'Learning request not found or already processed'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get point deduction amount from configuration
    points_to_deduct = get_point_config('join_learning_cost', 100)
    
    # Check if learner still has enough points
    user_points = UserPoints.objects.get(user=learning_session.learner)
    
    if user_points.balance < points_to_deduct:
        return Response(
            {'error': 'Learner no longer has sufficient points'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Accept the request and deduct points
    with transaction.atomic():
        # Deduct points from learner
        user_points.balance -= points_to_deduct
        user_points.total_spent += points_to_deduct
        user_points.save()
        
        # Create point transaction record
        PointTransaction.objects.create(
            user=learning_session.learner,
            transaction_type='join_learning',
            amount=-points_to_deduct,
            balance_after=user_points.balance,
            description=f'Started learning {learning_session.skill_name} with {learning_session.teacher.username}'
        )
        
        # Update session status and points
        learning_session.status = 'in_progress'
        learning_session.points_deducted = points_to_deduct
        learning_session.save()
        
        # Create notification for learner
        Notification.objects.create(
            user=learning_session.learner,
            notification_type='skill_match',
            title=f'Learning Request Accepted!',
            message=f'{request.user.username} accepted your request to learn {learning_session.skill_name}',
            link=f'/learning',
            sender=request.user
        )
    
    serializer = LearningSessionSerializer(learning_session)
    return Response({
        'message': 'Learning request accepted successfully',
        'learning_session': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_learning_request(request, session_id):
    """Teacher rejects a learning request"""
    try:
        learning_session = LearningSession.objects.get(
            id=session_id,
            teacher=request.user,
            status='pending'
        )
    except LearningSession.DoesNotExist:
        return Response(
            {'error': 'Learning request not found or already processed'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    with transaction.atomic():
        learning_session.status = 'rejected'
        learning_session.save()
        
        # Create notification for learner
        Notification.objects.create(
            user=learning_session.learner,
            notification_type='skill_match',
            title=f'Learning Request Declined',
            message=f'{request.user.username} declined your request to learn {learning_session.skill_name}',
            link=f'/learning',
            sender=request.user
        )
    
    serializer = LearningSessionSerializer(learning_session)
    return Response({
        'message': 'Learning request rejected',
        'learning_session': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_requests(request):
    """Get all pending learning requests for the current user (as teacher)"""
    requests = LearningSession.objects.filter(
        teacher=request.user,
        status='pending'
    ).order_by('-created_at')
    
    serializer = LearningSessionSerializer(requests, many=True)
    return Response({
        'requests': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_points(request):
    """Get current user's point balance and transaction history"""
    user_points, created = UserPoints.objects.get_or_create(
        user=request.user,
        defaults={'balance': 1000}
    )
    
    transactions = PointTransaction.objects.filter(user=request.user)[:20]
    transaction_serializer = PointTransactionSerializer(transactions, many=True)
    
    return Response({
        'balance': user_points.balance,
        'total_earned': user_points.total_earned,
        'total_spent': user_points.total_spent,
        'recent_transactions': transaction_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skills_learned(request, username=None):
    """Get all skills learned by a user (completed learning sessions as learner)"""
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
    
    sessions = LearningSession.objects.filter(
        learner=user,
        status='completed'
    ).select_related('teacher')
    
    serializer = LearningSessionSerializer(sessions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skills_taught(request, username=None):
    """Get all skills taught by a user (completed learning sessions as teacher)"""
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
    
    sessions = LearningSession.objects.filter(
        teacher=user,
        status='completed'
    ).select_related('learner')
    
    serializer = LearningSessionSerializer(sessions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_badges(request, username=None):
    """Get all badges earned by a user"""
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
    
    badges = Badge.objects.filter(user=user).order_by('-earned_at')
    serializer = BadgeSerializer(badges, many=True)
    
    return Response({
        'badges': serializer.data,
        'total_badges': badges.count()
    }, status=status.HTTP_200_OK)
