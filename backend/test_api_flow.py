"""
Simulate an actual API request to test the full flow
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Skill
from api.utils_safe import find_matching_users_for_skills

print("="*60)
print("SIMULATING API REQUEST")
print("="*60)

# Get a test user
user = User.objects.first()
print(f"Test user: {user.username}")

# Simulate search for "python"
desired_skills = ["python"]
print(f"Searching for: {desired_skills}")

# Get all skills from other users (same as API)
all_skills = list(Skill.objects.exclude(user=user).values_list(
    'user_id', 'name', 'embedding'
))
print(f"Found {len(all_skills)} skills from other users")

# Show first 3 skills
print("\nFirst 3 skills from database:")
for i, (uid, name, emb) in enumerate(all_skills[:3]):
    emb_len = len(emb) if emb else 0
    print(f"  {i+1}. User {uid}: '{name}' - embedding length: {emb_len}")

# Call the matching function
print("\n" + "="*60)
print("CALLING find_matching_users_for_skills")
print("="*60)
matches = find_matching_users_for_skills(desired_skills, all_skills)

print(f"\nReturned {len(matches)} matches:")
for m in matches[:5]:
    print(f"  User {m['user_id']}: score={m['match_score']:.4f} ({int(m['match_score']*100)}%)")
