#!/usr/bin/env python
"""
Script to reload the SentenceTransformer model in the running Django server
"""
import requests
import json

# Get token from user
print("=" * 60)
print("Model Reload Script")
print("=" * 60)

# You'll need to provide the authentication token
# You can get this from your browser's developer tools (check localStorage or cookies)
token = input("\nEnter your auth token (or press Enter to try without auth): ").strip()

url = "http://127.0.0.1:8000/api/debug/reload-model/"

headers = {}
if token:
    headers['Authorization'] = f'Bearer {token}'

print(f"\nSending POST request to {url}...")

try:
    response = requests.post(url, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✓ Model reloaded successfully!")
    else:
        print("\n✗ Failed to reload model")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 60)
