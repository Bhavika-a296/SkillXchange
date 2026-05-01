#!/usr/bin/env python
"""
Test the actual API endpoint by making HTTP requests
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# First, try to login or get a token
print("=" * 70)
print("TESTING ACTUAL API ENDPOINT")
print("=" * 70)

# Test if server is running
print("\n1. Checking if server is running...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=2)
    print(f"✓ Server is responding (status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("✗ Server is NOT running!")
    print("  Please start the server with: python manage.py runserver")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Try to create a session or login
print("\n2. Attempting to login...")
login_data = {
    "username": "xyz",
    "password": "xyz123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get('access') or data.get('token')
        print(f"✓ Login successful")
        print(f"  Token: {token[:50]}..." if token else "  No token received")
    else:
        print(f"✗ Login failed (status: {response.status_code})")
        print(f"  Response: {response.text[:200]}")
        # Try to continue anyway
        token = None
except Exception as e:
    print(f"✗ Login error: {e}")
    token = None

# Test the match_skills endpoint
print("\n3. Testing /api/match_skills/ endpoint...")
headers = {}
if token:
    headers['Authorization'] = f'Bearer {token}'

test_data = {
    "skills": ["python", "java"]
}

try:
    response = requests.post(f"{BASE_URL}/match_skills/", json=test_data, headers=headers)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        print(f"  ✓ Request successful")
        print(f"  Found {len(matches)} matches")
        
        if len(matches) > 0:
            for i, match in enumerate(matches[:3], 1):
                score = match.get('match_score', 0)
                percentage = match.get('match_percentage', int(score * 100))
                username = match.get('username', 'Unknown')
                print(f"    {i}. {username}: {score:.4f} ({percentage}%)")
            
            # Check if scores are 0
            if matches[0].get('match_score', 0) == 0:
                print("\n  ✗ PROBLEM FOUND: Match score is 0!")
                print("  This means the API is working but returning 0 scores")
            else:
                print("\n  ✓ Match scores look good!")
        else:
            print("  ⚠ No matches returned")
    elif response.status_code == 401:
        print("  ✗ Authentication required")
        print("  Please make sure you're logged in")
    else:
        print(f"  ✗ Request failed")
        print(f"  Response: {response.text[:500]}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
