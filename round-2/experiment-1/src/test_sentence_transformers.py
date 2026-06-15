#!/usr/bin/env python3
"""Test sentence-transformers with a small model."""
import sys
import os
import numpy as np

# Add venv to path
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages = os.path.join(venv_path, 'lib', 'python3.12', 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

print("Testing sentence-transformers...")
try:
    from sentence_transformers import SentenceTransformer
    print("Loading model: all-MiniLM-L6-v2")
    
    # Try to load model with caching disabled to avoid hang
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')
    print(f"Model loaded successfully: {model}")
    
    # Test encoding
    sentences = ['This is a test', 'Another test sentence']
    embeddings = model.encode(sentences)
    print(f"Encoded {len(sentences)} sentences into shape {embeddings.shape}")
    
    print("Sentence-transformers test PASSED")
    
except Exception as e:
    print(f"Sentence-transformers test FAILED: {e}")
    import traceback
    traceback.print_exc()
