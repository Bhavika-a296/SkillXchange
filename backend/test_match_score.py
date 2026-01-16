import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.utils_safe import get_model, get_skill_embedding, find_matching_users_for_skills
from api.models import Skill, User
import pickle

print('Loading model...')
model = get_model()
print('Model loaded successfully\n')

# Load all skills with embeddings
skills_data = [(s.user_id, s.name, s.embedding) for s in Skill.objects.all() if s.embedding]
print(f'Loaded {len(skills_data)} skills with embeddings\n')

# Test with some desired skills
desired = ['python', 'java']
print(f'Searching for users with: {desired}')

results = find_matching_users_for_skills(desired, skills_data)
print(f'\nFound {len(results)} matches:')
for r in results[:10]:
    username = User.objects.get(id=r['user_id']).username
    print(f'  User {r["user_id"]} ({username}): score={r["match_score"]:.4f} ({int(r["match_score"]*100)}%)')
    print(f'    Matching skills: {r["matching_skills"]}')
