"""
Script to generate embeddings for all existing skills in the database.
This will populate the 'embedding' field for all Skill records that don't have one.
"""
import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Skill
from api.utils_safe import get_skill_embedding, get_model

def generate_all_embeddings():
    """Generate embeddings for all skills without embeddings."""
    print("[Embeddings] Starting embedding generation...")
    
    # Test model first
    model = get_model()
    if model is None:
        print("[Embeddings] ERROR: Model failed to load! Cannot generate embeddings.")
        return
    
    print(f"[Embeddings] Model loaded successfully!")
    
    # Get all skills
    all_skills = Skill.objects.all()
    print(f"[Embeddings] Found {all_skills.count()} total skills in database")
    
    # Count skills needing embeddings
    needs_embedding = []
    for skill in all_skills:
        if not skill.embedding or len(skill.embedding) == 0:
            needs_embedding.append(skill)
    
    print(f"[Embeddings] {len(needs_embedding)} skills need embeddings")
    
    if len(needs_embedding) == 0:
        print("[Embeddings] All skills already have embeddings!")
        return
    
    # Generate embeddings
    success_count = 0
    fail_count = 0
    
    for i, skill in enumerate(needs_embedding, 1):
        try:
            print(f"[Embeddings] Processing {i}/{len(needs_embedding)}: '{skill.name}' (User: {skill.user.username})")
            
            # Generate embedding
            embedding = get_skill_embedding(skill.name)
            
            if embedding and len(embedding) > 0:
                skill.embedding = embedding
                skill.save()
                success_count += 1
                print(f"[Embeddings] ✓ Generated embedding for '{skill.name}' (length: {len(embedding)})")
            else:
                fail_count += 1
                print(f"[Embeddings] ✗ Failed to generate embedding for '{skill.name}'")
                
        except Exception as e:
            fail_count += 1
            print(f"[Embeddings] ✗ Error processing '{skill.name}': {e}")
    
    print("\n" + "="*60)
    print(f"[Embeddings] Embedding generation complete!")
    print(f"[Embeddings] Success: {success_count}")
    print(f"[Embeddings] Failed: {fail_count}")
    print("="*60)

if __name__ == '__main__':
    generate_all_embeddings()
