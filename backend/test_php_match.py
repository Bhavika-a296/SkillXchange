"""Test PHP skill matching"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.utils_safe import get_skill_embedding, calculate_skill_similarity
from api.models import Skill

# Test PHP embedding
php_embedding = get_skill_embedding('php')
print(f"PHP embedding length: {len(php_embedding)}")
print(f"PHP embedding first 5 values: {php_embedding[:5] if php_embedding else 'None'}")

# Get all skills from database
all_skills = Skill.objects.all()
print(f"\nTotal skills in database: {all_skills.count()}")

# Check if anyone has PHP skill
php_skills = Skill.objects.filter(name__icontains='php')
print(f"Users with PHP skill: {php_skills.count()}")
for skill in php_skills:
    print(f"  - User: {skill.user.username}, Skill: {skill.name}, Has embedding: {len(skill.embedding) > 0 if skill.embedding else False}")

# Test similarity with a few skills
print("\n--- Testing PHP similarity with some skills ---")
test_skills = Skill.objects.all()[:10]
for skill in test_skills:
    if skill.embedding:
        similarity = calculate_skill_similarity(php_embedding, skill.embedding)
        print(f"User: {skill.user.username}, Skill: {skill.name}, Similarity: {similarity:.4f} ({int(similarity*100)}%)")
    else:
        print(f"User: {skill.user.username}, Skill: {skill.name}, No embedding")
