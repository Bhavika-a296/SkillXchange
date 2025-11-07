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
from .serializers import ConnectionSerializer, MessageSerializer
from .utils_safe import (
    extract_text_from_pdf,
    extract_skills_from_text,
    get_skill_embedding,
    find_matching_users,
    find_matching_users_for_skills
)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Added 'post'

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def list(self, request):
        """GET /api/profile/ - Return the current user's profile"""
        profile = self.get_queryset().first()
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """Override create to handle updates (POST will act as PATCH)"""
        profile = self.get_queryset().first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH /api/profile/{pk}/"""
        profile = self.get_object()
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/profile/{pk}/"""
        return self.update(request, *args, **kwargs)

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

        # Get all skills from other users
        all_skills = list(Skill.objects.exclude(user=request.user).values_list(
            'user_id', 'name', 'embedding'
        ))

        # If multiple desired skills provided, compute aggregated matches
        matches = find_matching_users_for_skills(desired_skills, all_skills)

        # Enrich matches with provider username
        user_ids = [m['user_id'] for m in matches]
        from django.contrib.auth.models import User
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        user_map = {u['id']: u['username'] for u in users}

        response_matches = []
        for m in matches:
            response_matches.append({
                'user_id': m['user_id'],
                'username': user_map.get(m['user_id'], 'Unknown'),
                'match_score': m['match_score'],
                'matching_skills': m.get('matching_skills', [])
            })

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