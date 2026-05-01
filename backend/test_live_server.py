"""Test the live running API server via HTTP"""
import requests
import json

# Get a token first
login_response = requests.post('http://localhost:8000/api/auth/login/', 
    json={'username': 'anish_nale', 'password': 'anish123'})

if login_response.status_code == 200:
    token = login_response.json()['token']
    print(f"✓ Logged in successfully, token: {token[:20]}...")
    
    # Now test the match_skills endpoint
    headers = {'Authorization': f'Token {token}'}
    match_response = requests.post('http://localhost:8000/api/match_skills/',
        json={'skills': ['php']},
        headers=headers)
    
    print(f"\n=== LIVE API RESPONSE ===")
    print(f"Status: {match_response.status_code}")
    print(f"\nResponse:")
    response_data = match_response.json()
    print(json.dumps(response_data, indent=2))
    
    if 'matches' in response_data:
        print(f"\n=== MATCH SCORES ===")
        for match in response_data['matches']:
            print(f"{match['username']}: {match['match_score']} ({match['match_percentage']}%)")
else:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
