#!/usr/bin/env python
"""
Test the match_skills view directly without HTTP
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.views import SkillMatchView
from rest_framework.test import APIRequestFactory
from api.models import Skill

print("=" * 70)
print("TESTING SKILLMATCHVIEW DIRECTLY")
print("=" * 70)

# Get a user
user = User.objects.first()
print(f"\nUsing user: {user.username}")

# Check user's skills and other users' skills
user_skills = Skill.objects.filter(user=user).count()
other_skills = Skill.objects.exclude(user=user).count()
print(f"User's skills: {user_skills}")
print(f"Other users' skills: {other_skills}")

# Create a request
factory = APIRequestFactory()
request = factory.post('/api/match_skills/', {
    'skills': ['python', 'java']
}, format='json')

# Attach user to request
request.user = user

# Call the view
view = SkillMatchView.as_view()
response = view(request)

print(f"\nResponse status: {response.status_code}")
print(f"Response data keys: {list(response.data.keys())}")

if 'matches' in response.data:
    matches = response.data['matches']
    print(f"\nFound {len(matches)} matches:")
    for i, match in enumerate(matches[:5], 1):
        score = match.get('match_score', 0)
        percentage = match.get('match_percentage', int(score * 100))
        username = match.get('username', 'Unknown')
        matching_skills = match.get('matching_skills', [])
        print(f"  {i}. {username}: {score:.4f} ({percentage}%) - Skills: {matching_skills}")
    
    # Check for 0 scores
    if len(matches) > 0 and matches[0].get('match_score', 0) == 0:
        print("\n✗ PROBLEM: Match score is 0!")
        print("This suggests an issue in the matching logic or embeddings")
    elif len(matches) > 0:
        print("\n✓ Match scores look correct!")
    else:
        print("\n⚠ No matches found")
elif 'error' in response.data:
    print(f"\n✗ Error: {response.data['error']}")
else:
    print(f"\n✗ Unexpected response: {response.data}")

print("\n" + "=" * 70)
