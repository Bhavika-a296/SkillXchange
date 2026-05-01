#!/usr/bin/env python
"""
List users and attempt to test API authentication
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

print("Users in database:")
print("-" * 50)
for user in User.objects.all()[:10]:
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is active: {user.is_active}")
    print(f"  Is staff: {user.is_staff}")
    print()

# Now let's try to get/create a token for testing
from rest_framework_simplejwt.tokens import RefreshToken

user = User.objects.first()
if user:
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f"\nGenerated token for {user.username}:")
    print(f"Access token: {access_token[:100]}...")
    
    # Save to file for the test script
    with open('test_token.txt', 'w') as f:
        f.write(access_token)
    print("\nToken saved to test_token.txt")
