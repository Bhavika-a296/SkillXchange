"""Test PHP skill matching via API logic"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.utils_safe import get_skill_embedding, find_matching_users_for_skills
from api.models import Skill
from django.contrib.auth.models import User

# Simulate searching for PHP
desired_skills = ['php']
print(f"Searching for: {desired_skills}")

# Get all skills from other users (simulating a user searching)
# For testing, let's exclude user 'xyz'
test_user = User.objects.filter(username='xyz').first()
if test_user:
    all_skills = list(Skill.objects.exclude(user=test_user).values_list(
        'user_id', 'name', 'embedding'
    ))
    print(f"Found {len(all_skills)} skills from other users")
    
    # Run the matching algorithm
    matches = find_matching_users_for_skills(desired_skills, all_skills)
    print(f"\nFound {len(matches)} matches:")
    
    for m in matches:
        user = User.objects.get(id=m['user_id'])
        print(f"  User: {user.username}")
        print(f"    match_score: {m['match_score']:.4f}")
        print(f"    match_percentage: {int(m['match_score'] * 100)}%")
        print(f"    matching_skills: {m.get('matching_skills', [])}")
        print()
else:
    print("Test user not found")
