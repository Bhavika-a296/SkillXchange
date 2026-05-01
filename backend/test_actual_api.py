"""Test the actual API endpoint to see what's being returned"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from api.views import SkillMatchView
from rest_framework.test import force_authenticate

# Create a test request
factory = RequestFactory()
user = User.objects.get(username='anish_nale')  # Use a user who doesn't have PHP

# Create POST request
request = factory.post('/api/match_skills/', 
    {'skills': ['php']},
    content_type='application/json'
)
force_authenticate(request, user=user)

# Call the view
view = SkillMatchView.as_view()
response = view(request)

print(f"Status: {response.status_code}")
print(f"\nResponse data:")
print(json.dumps(response.data, indent=2))

# Check what matches we got
if 'matches' in response.data:
    print(f"\n=== MATCHES ANALYSIS ===")
    for match in response.data['matches']:
        print(f"\nUser: {match['username']}")
        print(f"  match_score: {match['match_score']}")
        print(f"  match_percentage: {match['match_percentage']}")
        print(f"  matching_skills: {match['matching_skills']}")
