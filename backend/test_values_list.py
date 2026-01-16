"""
Test how values_list returns embeddings
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Skill

print("Test 1: Get single skill object")
skill = Skill.objects.first()
print(f"Skill: {skill.name}")
print(f"Embedding type: {type(skill.embedding)}")
print(f"Embedding length: {len(skill.embedding) if skill.embedding else 0}")

print("\nTest 2: Using values_list")
result = list(Skill.objects.filter(id=skill.id).values_list('user_id', 'name', 'embedding'))
print(f"Result: {result}")
user_id, name, embedding = result[0]
print(f"Embedding type from values_list: {type(embedding)}")
print(f"Embedding length from values_list: {len(embedding) if embedding else 0}")
print(f"First 5 values: {embedding[:5] if embedding else 'None'}")
