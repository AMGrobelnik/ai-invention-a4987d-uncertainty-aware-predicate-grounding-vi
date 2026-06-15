#!/usr/bin/env python3
"""Test imports for the neuro-symbolic experiment."""
import sys
import os

# Add the virtual environment site-packages to path
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages = os.path.join(venv_path, 'lib', 'python3.12', 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

print("Testing imports...")
try:
    import ot
    print(f"✓ POT (ot) imported successfully")
except ImportError as e:
    print(f"✗ Failed to import POT: {e}")

try:
    import problog
    print(f"✓ ProbLog imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ProbLog: {e}")

try:
    import numpy as np
    print(f"✓ NumPy imported successfully")
except ImportError as e:
    print(f"✗ Failed to import NumPy: {e}")

try:
    import sentence_transformers
    print(f"✓ Sentence-transformers imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sentence-transformers: {e}")

print("\nAll import tests completed.")
