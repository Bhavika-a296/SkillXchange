"""Test the full API flow for PHP search"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Skill, UserProfile
from api.serializers import UserProfileSerializer

# First, let's check a user who has PHP
php_users = User.objects.filter(skills__name__iexact='php').distinct()
print(f"Users with PHP skill: {php_users.count()}")

for user in php_users:
    print(f"\n=== User: {user.username} ===")
    profile = UserProfile.objects.filter(user=user).first()
    if profile:
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        print(f"Profile data keys: {data.keys()}")
        print(f"User data: {data.get('user')}")
        print(f"Skills: {data.get('skills')}")
        print(f"Bio: {data.get('bio', '')[:50]}...")
    else:
        print("No profile found")
    
    # Check their skills
    skills = Skill.objects.filter(user=user)
    print(f"Total skills: {skills.count()}")
    for skill in skills:
        print(f"  - {skill.name} (embedding: {len(skill.embedding) if skill.embedding else 0} dims)")
