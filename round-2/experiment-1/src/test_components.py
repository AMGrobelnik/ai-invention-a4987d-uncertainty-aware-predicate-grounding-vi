#!/usr/bin/env python3
"""Quick test script to verify all components work independently."""
import sys
import os

# Add venv to path
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages = os.path.join(venv_path, 'lib', 'python3.12', 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

print("=" * 60)
print("COMPONENT TEST SCRIPT")
print("=" * 60)

# Test 1: Data Loading
print("\n[Test 1] Data Loading...")
try:
    from method import load_datasets
    datasets = load_datasets(n_ruletaker=2, n_clutrr=2)
    print(f"  ✓ Loaded {len(datasets['ruletaker'])} ruletaker examples")
    print(f"  ✓ Loaded {len(datasets['clutrr'])} clutrr examples")
    print(f"  ✓ Sample ruletaker input: {datasets['ruletaker'][0]['input'][:50]}...")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 2: ProbLog
print("\n[Test 2] ProbLog Evaluation...")
try:
    from method import evaluate_problog
    test_code = "0.7::cat(alice). query(cat(alice))."
    result = evaluate_problog(test_code)
    print(f"  ✓ ProbLog result: {result}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 3: Optimal Transport
print("\n[Test 3] Optimal Transport (POT)...")
try:
    import numpy as np
    import ot
    a = np.array([0.5, 0.5])
    b = np.array([0.5, 0.5])
    M = np.array([[0.0, 1.0], [1.0, 0.0]])
    T = ot.sinkhorn(a, b, M, reg=0.1)
    print(f"  ✓ OT transport plan computed")
    print(f"  ✓ T shape: {T.shape}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 4: Sentence Transformers
print("\n[Test 4] Sentence Transformers...")
try:
    from method import setup_sentence_transformer
    model = setup_sentence_transformer()
    if model:
        print(f"  ✓ Model loaded")
        # Test encoding
        embeddings = model.encode(["test sentence"])
        print(f"  ✓ Encoding works, shape: {embeddings.shape}")
    else:
        print(f"  ✗ Model loading returned None")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 5: LLM Translation (mock mode)
print("\n[Test 5] LLM Translation (mock mode)...")
try:
    from method import translate_to_problog
    result = translate_to_problog("Alice is a cat.", "Is Alice a cat?", None)
    print(f"  ✓ Mock translation works")
    print(f"  ✓ Code: {result['problog_code'][:50]}...")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

print("\n" + "=" * 60)
print("All component tests completed!")
print("=" * 60)
