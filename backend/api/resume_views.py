from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import PyPDF2.errors
import nltk
import os
from .models import UserProfile, Skill, Resume, SkillMatch
from .serializers import (
    UserProfileSerializer,
    SkillSerializer,
    ResumeSerializer,
    SkillMatchSerializer
)
from .utils_safe import (
    extract_text_from_pdf,
    extract_skills_from_text,
    get_skill_embedding,
    find_matching_users
)

class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user's resume"""
        try:
            resume = Resume.objects.get(user=request.user)
            serializer = ResumeSerializer(resume)
            return Response(serializer.data)
        except Resume.DoesNotExist:
            return Response({
                'message': 'No resume found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request):
        """Delete current user's resume"""
        try:
            resume = Resume.objects.get(user=request.user)
            resume.file.delete()
            resume.delete()
            return Response({
                'message': 'Resume deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except Resume.DoesNotExist:
            return Response({
                'error': 'No resume found'
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        try:
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

            # Check if user already has a resume
            try:
                existing_resume = Resume.objects.get(user=request.user)
                # Delete old resume file (with error handling for file locks)
                try:
                    existing_resume.file.delete()
                except PermissionError as pe:
                    print(f"Warning: Could not delete old resume file (may be locked): {pe}")
                    # Continue anyway - the database entry will be deleted and new file will be saved
                except Exception as e:
                    print(f"Warning: Error deleting old resume file: {e}")
                existing_resume.delete()
            except Resume.DoesNotExist:
                pass

            # Create a new Resume instance
            serializer = ResumeSerializer(data={'file': file})
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
                # Clean up the invalid file
                resume.file.delete()
                resume.delete()
                return Response({
                    'error': 'Could not read the PDF file. Please ensure it is not corrupted or password protected.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                # Clean up on error
                resume.file.delete()
                resume.delete()
                import traceback
                print('Resume processing error:', str(e))
                print(traceback.format_exc())
                return Response({
                    'error': 'An error occurred while processing the resume. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            import traceback
            print('Resume upload error:', str(e))
            print(traceback.format_exc())
            return Response({
                'error': 'An error occurred while uploading the resume. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)