#!/usr/bin/env python
"""
Test the match_skills API endpoint
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.utils_safe import get_model, get_skill_embedding

print("=" * 60)
print("Testing Model in Django Context")
print("=" * 60)

# Test 1: Check if model loads
print("\n1. Testing model load...")
model = get_model()
if model:
    print(f"   ✓ Model loaded: {model}")
else:
    print(f"   ✗ Model is None")

# Test 2: Check if embedding generation works
print("\n2. Testing embedding generation...")
embedding = get_skill_embedding("python")
if embedding and len(embedding) > 0:
    print(f"   ✓ Embedding created, dimension: {len(embedding)}")
else:
    print(f"   ✗ Embedding failed or empty")

# Test 3: Test with actual API logic
print("\n3. Testing match calculation...")
from api.models import Skill
from api.utils_safe import find_matching_users_for_skills

all_skills = list(Skill.objects.all().values_list('user_id', 'name', 'embedding'))
print(f"   Found {len(all_skills)} skills in database")

if len(all_skills) > 0:
    matches = find_matching_users_for_skills(['python'], all_skills)
    print(f"   Found {len(matches)} matches")
    if len(matches) > 0:
        print(f"   Top match score: {matches[0]['match_score']:.2%}")
        print("   ✓ Match calculation working")
    else:
        print("   ✗ No matches found")
else:
    print("   ⚠ No skills in database to test with")

print("\n" + "=" * 60)
