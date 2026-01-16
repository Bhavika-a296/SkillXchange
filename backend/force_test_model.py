"""
Force test model loading outside Django to verify it works
"""
import os
import sys

# Test 1: Can we load the model at all?
print("="*60)
print("TEST: Loading SentenceTransformer model")
print("="*60)

try:
    from sentence_transformers import SentenceTransformer
    
    print("Loading model...")
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2', trust_remote_code=True)
    print(f"✓ Model loaded: {model}")
    
    print("\nTesting encoding...")
    embedding = model.encode("python programming")
    print(f"✓ Encoding works: {len(embedding)} dimensions")
    print(f"  First 5 values: {embedding[:5]}")
    
    print("\nTesting moving to CPU...")
    model = model.to('cpu')
    print(f"✓ Model on CPU")
    
    embedding2 = model.encode("javascript")
    print(f"✓ Still works after .to('cpu'): {len(embedding2)} dimensions")
    
    print("\n" + "="*60)
    print("SUCCESS: Model works perfectly!")
    print("="*60)
    print("\nThe issue must be with Django's module caching.")
    print("Solution: COMPLETELY STOP Django (Ctrl+C) and restart fresh.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
