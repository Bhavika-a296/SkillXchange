#!/usr/bin/env python
"""
Comprehensive debug script to identify why match score is 0
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Skill, User
from api.utils_safe import get_model, get_skill_embedding, find_matching_users_for_skills
import json

print("=" * 70)
print("COMPREHENSIVE MATCH SCORE DEBUG")
print("=" * 70)

# Check 1: Model Status
print("\n1. CHECKING MODEL STATUS")
print("-" * 70)
model = get_model()
if model:
    print(f"✓ Model loaded successfully")
    print(f"  Type: {type(model)}")
else:
    print(f"✗ MODEL IS NONE - THIS IS THE PROBLEM!")
    exit(1)

# Check 2: Embedding Generation
print("\n2. TESTING EMBEDDING GENERATION")
print("-" * 70)
test_embedding = get_skill_embedding("python")
if test_embedding and len(test_embedding) > 0:
    print(f"✓ Embedding generated successfully")
    print(f"  Dimension: {len(test_embedding)}")
    print(f"  First 5 values: {test_embedding[:5]}")
else:
    print(f"✗ EMBEDDING GENERATION FAILED - THIS IS THE PROBLEM!")
    exit(1)

# Check 3: Database Skills
print("\n3. CHECKING DATABASE SKILLS")
print("-" * 70)
total_skills = Skill.objects.count()
skills_with_embeddings = Skill.objects.exclude(embedding__isnull=True).count()
skills_without_embeddings = total_skills - skills_with_embeddings

print(f"Total skills: {total_skills}")
print(f"Skills with embeddings: {skills_with_embeddings}")
print(f"Skills WITHOUT embeddings: {skills_without_embeddings}")

if skills_without_embeddings > 0:
    print("\n⚠ WARNING: Some skills don't have embeddings!")
    no_embed_skills = Skill.objects.filter(embedding__isnull=True)[:5]
    for skill in no_embed_skills:
        print(f"  - {skill.name} (User: {skill.user.username}, ID: {skill.id})")

# Check 4: Empty Embeddings
print("\n4. CHECKING FOR EMPTY EMBEDDINGS")
print("-" * 70)
empty_embeddings = 0
for skill in Skill.objects.all():
    if skill.embedding is not None:
        if isinstance(skill.embedding, list) and len(skill.embedding) == 0:
            empty_embeddings += 1
            if empty_embeddings <= 3:
                print(f"  Empty embedding: {skill.name} (User: {skill.user.username})")

if empty_embeddings > 0:
    print(f"⚠ Found {empty_embeddings} skills with empty embedding arrays!")
else:
    print(f"✓ No empty embeddings found")

# Check 5: Match Calculation Test
print("\n5. TESTING MATCH CALCULATION")
print("-" * 70)
all_skills = list(Skill.objects.all().values_list('user_id', 'name', 'embedding'))
print(f"Retrieved {len(all_skills)} skills from database")

# Filter out skills with null or empty embeddings
valid_skills = [(uid, name, emb) for uid, name, emb in all_skills if emb and len(emb) > 0]
print(f"Valid skills (with non-empty embeddings): {len(valid_skills)}")

if len(valid_skills) > 0:
    test_query = ['python', 'java']
    print(f"\nSearching for: {test_query}")
    matches = find_matching_users_for_skills(test_query, valid_skills)
    
    print(f"\nFound {len(matches)} matches:")
    for i, match in enumerate(matches[:5], 1):
        user = User.objects.get(id=match['user_id'])
        print(f"  {i}. {user.username}: {match['match_score']:.4f} ({int(match['match_score']*100)}%)")
        print(f"     Matching skills: {match['matching_skills']}")
    
    if len(matches) == 0:
        print("✗ NO MATCHES FOUND - THIS IS THE PROBLEM!")
    elif matches[0]['match_score'] == 0:
        print("✗ MATCH SCORE IS 0 - THIS IS THE PROBLEM!")
        print("\nDebugging first match:")
        match = matches[0]
        user_skills = Skill.objects.filter(user_id=match['user_id'])
        print(f"User {match['user_id']} has {user_skills.count()} skills:")
        for skill in user_skills:
            has_emb = "✓" if skill.embedding and len(skill.embedding) > 0 else "✗"
            print(f"  {has_emb} {skill.name}")
    else:
        print("✓ Match calculation working correctly!")
else:
    print("✗ NO VALID SKILLS FOUND - THIS IS THE PROBLEM!")

# Check 6: Test with a specific user
print("\n6. TESTING WITH SPECIFIC USER")
print("-" * 70)
users = User.objects.all()[:3]
for user in users:
    user_skills = Skill.objects.filter(user=user)
    skills_info = []
    for skill in user_skills[:5]:
        has_emb = "✓" if skill.embedding and len(skill.embedding) > 0 else "✗"
        skills_info.append(f"{has_emb} {skill.name}")
    print(f"{user.username} ({user_skills.count()} skills): {', '.join(skills_info[:3])}")

print("\n" + "=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)
