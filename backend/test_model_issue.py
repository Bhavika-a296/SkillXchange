"""
Test to diagnose the model loading and similarity calculation issue
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("="*60)
print("TEST 1: Check if model can load")
print("="*60)
from api.utils_safe import get_model, get_skill_embedding, calculate_skill_similarity

model = get_model()
print(f"Model loaded: {model is not None}")

if model:
    print("\n" + "="*60)
    print("TEST 2: Create embedding for search term")
    print("="*60)
    search_embedding = get_skill_embedding("python")
    print(f"Search embedding length: {len(search_embedding)}")
    print(f"First 5 values: {search_embedding[:5] if search_embedding else 'EMPTY'}")
    
    print("\n" + "="*60)
    print("TEST 3: Get skill from database")
    print("="*60)
    from api.models import Skill
    skill = Skill.objects.exclude(name__iexact='python').first()
    if skill:
        print(f"Database skill: '{skill.name}' (User: {skill.user.username})")
        print(f"Database embedding length: {len(skill.embedding) if skill.embedding else 0}")
        print(f"First 5 values: {skill.embedding[:5] if skill.embedding else 'EMPTY'}")
        
        print("\n" + "="*60)
        print("TEST 4: Calculate similarity")
        print("="*60)
        if search_embedding and skill.embedding:
            similarity = calculate_skill_similarity(skill.embedding, search_embedding)
            print(f"Similarity score: {similarity}")
            print(f"Match percentage: {int(similarity * 100)}%")
        else:
            print("ERROR: One of the embeddings is empty!")
            print(f"  Search embedding: {len(search_embedding) if search_embedding else 0}")
            print(f"  Skill embedding: {len(skill.embedding) if skill.embedding else 0}")
    else:
        print("No skills found in database!")
else:
    print("ERROR: Model failed to load!")
    from api.utils_safe import _model_load_failed, _model_load_attempts
    print(f"Load failed: {_model_load_failed}")
    print(f"Attempts: {_model_load_attempts}")
