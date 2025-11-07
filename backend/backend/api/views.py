from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Skill, UserSkill, Resume
from .serializers import SkillSerializer, UserSkillSerializer, ResumeSerializer
from .utils import extract_skills_from_resume, get_sentence_bert_embedding, compute_match_scores

# Upload Resume & Extract Skills
class ResumeUploadView(APIView):
    def post(self, request):
        user = request.user
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        resume = Resume.objects.create(user=user, file=file)
        skills = extract_skills_from_resume(file)
        # Save skills in DB
        for skill_name in skills:
            skill_obj, created = Skill.objects.get_or_create(name=skill_name)
            UserSkill.objects.get_or_create(user=user, skill=skill_obj, offering=True)

        serializer = ResumeSerializer(resume)
        return Response({"resume": serializer.data, "skills": skills}, status=201)


# Skill Matching API
class SkillMatchView(APIView):
    def post(self, request):
        user = request.user
        skill_query = request.data.get('skill')  # Skill user wants to learn
        if not skill_query:
            return Response({"error": "No skill provided"}, status=400)

        results = compute_match_scores(skill_query, user)
        return Response({"matches": results}, status=200)
