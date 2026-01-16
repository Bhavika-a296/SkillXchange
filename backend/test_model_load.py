#!/usr/bin/env python
"""Test if SentenceTransformer model can be loaded"""

import sys
import os

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing SentenceTransformer Model Loading")
print("=" * 60)

try:
    print("\n1. Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("   ✓ Successfully imported SentenceTransformer")
    
    print("\n2. Importing PyTorch...")
    import torch
    print(f"   ✓ PyTorch version: {torch.__version__}")
    print(f"   ✓ CUDA available: {torch.cuda.is_available()}")
    
    print("\n3. Loading model 'paraphrase-MiniLM-L6-v2'...")
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    print("   ✓ Model loaded successfully")
    
    print("\n4. Testing model encoding...")
    test_embedding = model.encode("test sentence", show_progress_bar=False)
    print(f"   ✓ Encoding successful, dimension: {test_embedding.shape[0]}")
    
    print("\n5. Testing with actual skill...")
    skill_embedding = model.encode("python programming", show_progress_bar=False)
    print(f"   ✓ Skill encoding successful, dimension: {skill_embedding.shape[0]}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Model is working correctly")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ MODEL LOADING FAILED")
    print("=" * 60)
    sys.exit(1)
