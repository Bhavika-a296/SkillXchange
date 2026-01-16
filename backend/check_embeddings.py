"""
Check what's in the embedding field for skills
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Skill

skills = Skill.objects.all()[:10]

print("First 10 skills:")
for s in skills:
    emb_info = f"NULL" if not s.embedding else f"Type: {type(s.embedding)}, Len: {len(s.embedding) if hasattr(s.embedding, '__len__') else 'N/A'}"
    print(f"{s.id}: '{s.name}' (User: {s.user.username}) - Embedding: {emb_info}")
    if s.embedding:
        print(f"   First few values: {s.embedding[:5] if isinstance(s.embedding, list) else str(s.embedding)[:100]}")
