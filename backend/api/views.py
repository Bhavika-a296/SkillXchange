from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import PyPDF2.errors
import nltk
from django.db import models
from django.db.models import Q
from .models import UserProfile, Skill, Resume, SkillMatch
from .models import Connection, Message
from .serializers import (
    UserProfileSerializer,
    SkillSerializer,
    ResumeSerializer,
    SkillMatchSerializer
)
from .serializers import ConnectionSerializer, MessageSerializer, NotificationSerializer
from .utils_safe import (
    extract_text_from_pdf,
    extract_skills_from_text,
    get_skill_embedding,
    find_matching_users,
    find_matching_users_for_skills
)

class UserProfileView(APIView):
    """Handle GET and PATCH/PUT on /api/profile/ for current user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """GET /api/profile/ - Return the current user's profile"""
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """POST /api/profile/ - Update current user's profile (partial)"""
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """PATCH /api/profile/ - Partial update current user's profile"""
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """PUT /api/profile/ - Full update current user's profile"""
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(APIView):
    """Handle GET/PATCH/PUT on /api/profile/{id}/ for specific profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """Legacy ViewSet - keeping for compatibility"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Override to return current user's profile when no pk is provided"""
        # Check if pk is in the URL kwargs
        if self.kwargs.get('pk'):
            return super().get_object()
        # Otherwise return the current user's profile
        return self.get_queryset().first()
    
    def list(self, request):
        """GET /api/profile/ - Return the current user's profile"""
        profile = self.get_queryset().first()
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """POST /api/profile/ - Handle updates (POST acts as PATCH for compatibility)"""
        profile = self.get_queryset().first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='')
    def update_current_profile(self, request):
        """PATCH /api/profile/ - Update current user's profile"""
        profile = self.get_queryset().first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/profile/{pk}/ - Update specific profile by ID"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/profile/{pk}/ - Partial update with ID"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Skill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Get BERT embedding for the skill
        skill_name = serializer.validated_data['name']
        embedding = get_skill_embedding(skill_name)
        serializer.save(user=self.request.user, embedding=embedding)

class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Check if file was uploaded
            if 'file' not in request.FILES:
                return Response({
                    'error': 'No file uploaded'
                }, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']
            
            # Validate file type
            if not file.name.lower().endswith('.pdf'):
                return Response({
                    'error': 'Only PDF files are accepted'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                return Response({
                    'error': 'File size cannot exceed 5MB'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = ResumeSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the resume
            resume = serializer.save(user=request.user)
            
            try:
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(resume.file)
                
                # Extract skills from text
                skills = extract_skills_from_text(pdf_text)
                
                if not skills:
                    resume.file.delete()
                    resume.delete()
                    return Response({
                        'error': 'No skills could be extracted from the resume'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Save extracted skills, avoiding duplicates
                saved_skills = []
                for skill_name in skills:
                    skill, created = Skill.objects.get_or_create(
                        user=request.user,
                        name=skill_name,
                        defaults={
                            'embedding': get_skill_embedding(skill_name)
                        }
                    )
                    saved_skills.append({
                        'name': skill.name,
                        'id': skill.id,
                        'isNew': created
                    })
                
                resume.processed = True
                resume.save()
                
                return Response({
                    'message': 'Resume processed successfully',
                    'skills_extracted': saved_skills,
                    'total_skills': len(saved_skills)
                }, status=status.HTTP_200_OK)
            
            except (PyPDF2.errors.PdfReadError, PyPDF2.errors.EmptyFileError):
                if resume:
                    resume.file.delete()
                    resume.delete()
                return Response({
                    'error': 'Could not read the PDF file. Please ensure it is not corrupted or password protected.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                if resume:
                    resume.file.delete()
                    resume.delete()
                import traceback
                print(traceback.format_exc())  # Log the full error
                return Response({
                    'error': 'An error occurred while processing the resume. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Log the full error
            return Response({
                'error': 'An error occurred while processing your request. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SkillMatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Support either a single 'skill' string or a list of 'skills'
        skills = request.data.get('skills') or request.data.get('skill')
        if not skills:
            return Response({
                'error': 'Skill parameter is required (provide "skill" or "skills")'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Normalize to list
        if isinstance(skills, str):
            desired_skills = [skills]
        else:
            desired_skills = list(skills)

        print(f"[SkillMatch] User {request.user.username} searching for: {desired_skills}")

        # Get all skills from other users
        all_skills = list(Skill.objects.exclude(user=request.user).values_list(
            'user_id', 'name', 'embedding'
        ))
        print(f"[SkillMatch] Found {len(all_skills)} skills from other users")

        # If multiple desired skills provided, compute aggregated matches
        matches = find_matching_users_for_skills(desired_skills, all_skills)
        print(f"[SkillMatch] Computed {len(matches)} matches")

        # Enrich matches with provider username
        user_ids = [m['user_id'] for m in matches]
        from django.contrib.auth.models import User
        from django.db import transaction
        import time
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        user_map = {u['id']: u['username'] for u in users}

        response_matches = []
        saved_count = 0
        
        # Use atomic transaction to prevent database locks
        max_retries = 3
        retry_delay = 0.1  # Start with 100ms delay
        
        for retry in range(max_retries):
            try:
                with transaction.atomic():
                    for m in matches:
                        username = user_map.get(m['user_id'], 'Unknown')
                        print(f"[SkillMatch] User {m['user_id']} ({username}): score={m['match_score']:.4f}")
                        
                        # Save match to database (lowered threshold to 0.3 to capture more matches)
                        if m['match_score'] > 0.3:
                            for skill in desired_skills:
                                obj, created = SkillMatch.objects.update_or_create(
                                    seeker=request.user,
                                    provider_id=m['user_id'],
                                    desired_skill=skill,
                                    defaults={'similarity_score': m['match_score']}
                                )
                                action = 'Created' if created else 'Updated'
                                print(f"[SkillMatch] {action} match: {request.user.username} -> User({m['user_id']}) for '{skill}' score={m['match_score']:.4f}")
                                saved_count += 1
                        else:
                            print(f"[SkillMatch] Skipped saving (score <= 0.3)")
                        
                        response_matches.append({
                            'user_id': m['user_id'],
                            'username': username,
                            'match_score': m['match_score'],
                            'match_percentage': int(m['match_score'] * 100),  # Add percentage for frontend
                            'matching_skills': m.get('matching_skills', [])
                        })
                
                # Transaction successful, break out of retry loop
                print(f"[SkillMatch] Saved {saved_count} matches to database")
                break
                
            except Exception as e:
                if 'database is locked' in str(e).lower():
                    if retry < max_retries - 1:
                        wait_time = retry_delay * (2 ** retry)  # Exponential backoff
                        print(f"[SkillMatch] Database locked, retrying in {wait_time:.2f}s (attempt {retry + 1}/{max_retries})")
                        time.sleep(wait_time)
                        response_matches = []  # Reset matches for retry
                        saved_count = 0
                    else:
                        print(f"[SkillMatch] Database locked after {max_retries} retries, returning error")
                        return Response({
                            'error': 'Database busy, please try again',
                            'matches': []
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    # Re-raise non-lock errors
                    raise
        
        return Response({'matches': response_matches})


class ConnectionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        # Create a connection request (or accept existing request)
        try:
            from django.contrib.auth.models import User
            receiver = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if receiver == request.user:
            return Response({'error': 'Cannot connect to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a connection already exists
        conn, created = Connection.objects.get_or_create(requester=request.user, receiver=receiver)
        if not created:
            # If pending, mark connected; if connected, return existing
            if conn.status == 'pending':
                conn.status = 'connected'
                conn.save()
        else:
            # For simplicity, immediately mark as connected
            conn.status = 'connected'
            conn.save()

        serializer = ConnectionSerializer(conn)
        return Response(serializer.data)


class ConnectionsListView(APIView):
    """List all connections for the authenticated user where status='connected'."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get connections where user is either requester or receiver with status 'connected'
        connections = Connection.objects.filter(
            (Q(requester=request.user) | Q(receiver=request.user)),
            status='connected'
        ).select_related('requester', 'receiver')

        # Build list of connected users (not including the current user)
        # Use a set to track user IDs and avoid duplicates
        seen_user_ids = set()
        connected_users = []
        
        for conn in connections:
            other_user = conn.receiver if conn.requester == request.user else conn.requester
            
            # Skip if we've already added this user
            if other_user.id in seen_user_ids:
                continue
                
            seen_user_ids.add(other_user.id)
            connected_users.append({
                'id': other_user.id,
                'username': other_user.username,
                'email': other_user.email,
                'connection_id': conn.id,
                'connected_at': conn.created_at
            })

        return Response({'connections': connected_users})


class ConnectionAcceptView(APIView):
    """Accept a pending connection request."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, connection_id, *args, **kwargs):
        try:
            connection = Connection.objects.get(id=connection_id)
        except Connection.DoesNotExist:
            return Response({'error': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)

        # Only the receiver can accept
        if connection.receiver != request.user:
            return Response({'error': 'You are not authorized to accept this connection'}, status=status.HTTP_403_FORBIDDEN)

        if connection.status != 'pending':
            return Response({'error': 'Connection is not pending'}, status=status.HTTP_400_BAD_REQUEST)

        connection.status = 'connected'
        connection.save()

        serializer = ConnectionSerializer(connection)
        return Response(serializer.data)


class ConnectionRejectView(APIView):
    """Reject a pending connection request."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, connection_id, *args, **kwargs):
        try:
            connection = Connection.objects.get(id=connection_id)
        except Connection.DoesNotExist:
            return Response({'error': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)

        # Only the receiver can reject
        if connection.receiver != request.user:
            return Response({'error': 'You are not authorized to reject this connection'}, status=status.HTTP_403_FORBIDDEN)

        if connection.status != 'pending':
            return Response({'error': 'Connection is not pending'}, status=status.HTTP_400_BAD_REQUEST)

        connection.status = 'rejected'
        connection.save()

        serializer = ConnectionSerializer(connection)
        return Response(serializer.data)


class MessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # ?with=<user_id>
        other_id = request.GET.get('with')
        if not other_id:
            return Response({'error': 'Query parameter "with" required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from django.contrib.auth.models import User
            other = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get messages between request.user and other
        msgs = Message.objects.filter(
            (models.Q(sender=request.user, receiver=other)) |
            (models.Q(sender=other, receiver=request.user))
        ).order_by('created_at')

        serializer = MessageSerializer(msgs, many=True)
        return Response({'messages': serializer.data})

    def post(self, request, *args, **kwargs):
        # Send a message { receiver: id, content: str }
        receiver_id = request.data.get('receiver')
        content = request.data.get('content')
        if not receiver_id or not content:
            return Response({'error': 'receiver and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from django.contrib.auth.models import User
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        msg = Message.objects.create(sender=request.user, receiver=receiver, content=content)
        serializer = MessageSerializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginStreakView(APIView):
    """Track and retrieve login streaks"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user's login streak data"""
        from datetime import date, timedelta
        from .models import DailyLogin
        
        user = request.user
        today = date.today()
        
        # Record today's login if not already recorded
        DailyLogin.objects.get_or_create(user=user, login_date=today)
        
        # Get all login dates for this user
        login_dates = list(DailyLogin.objects.filter(user=user).values_list('login_date', flat=True).order_by('login_date'))
        
        if not login_dates:
            return Response({
                'current_streak': 0,
                'max_streak': 0,
                'total_days': 0,
                'contributions': []
            })
        
        # Calculate streaks
        current_streak = 0
        max_streak = 0
        temp_streak = 0
        
        # Check current streak (must include today or yesterday)
        login_dates_set = set(login_dates)
        check_date = today
        while check_date in login_dates_set:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # If no login today, check if there was login yesterday
        if current_streak == 0 and (today - timedelta(days=1)) in login_dates_set:
            check_date = today - timedelta(days=1)
            while check_date in login_dates_set:
                current_streak += 1
                check_date -= timedelta(days=1)
        
        # Calculate max streak
        for i in range(len(login_dates)):
            if i == 0:
                temp_streak = 1
            else:
                # Check if consecutive days
                if (login_dates[i] - login_dates[i-1]).days == 1:
                    temp_streak += 1
                else:
                    max_streak = max(max_streak, temp_streak)
                    temp_streak = 1
        
        max_streak = max(max_streak, temp_streak, current_streak)
        
        # Generate contribution data for past 365 days
        contributions = []
        start_date = today - timedelta(days=364)
        
        for i in range(365):
            check_date = start_date + timedelta(days=i)
            count = 1 if check_date in login_dates_set else 0
            contributions.append({
                'date': check_date.isoformat(),
                'count': count
            })
        
        return Response({
            'current_streak': current_streak,
            'max_streak': max_streak,
            'total_days': len(login_dates),
            'contributions': contributions
        })
    
    def post(self, request):
        """Manually record a login (called on user login)"""
        from datetime import date
        from .models import DailyLogin
        
        today = date.today()
        login, created = DailyLogin.objects.get_or_create(
            user=request.user,
            login_date=today
        )
        
        return Response({
            'success': True,
            'created': created,
            'date': today.isoformat()
        })


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Return only unread notifications for the current user"""
        from .models import Notification
        return Notification.objects.filter(user=self.request.user, read=False)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications count"""
        from .models import Notification
        count = Notification.objects.filter(user=request.user, read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        from .models import Notification
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read"""
        from .models import Notification
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class ModelReloadView(APIView):
    """Debug endpoint to force reload the SentenceTransformer model"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Force reload the model"""
        from .utils_safe import get_model
        
        # Force reload the model
        model = get_model(force_reload=True)
        
        if model is not None:
            return Response({
                'success': True,
                'message': 'Model reloaded successfully'
            })
        else:
            return Response({
                'success': False,
                'message': 'Model failed to load'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)