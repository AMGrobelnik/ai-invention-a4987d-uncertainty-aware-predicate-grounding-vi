#!/usr/bin/env python3
"""Helper imports for method.py - avoid timeout on repeated imports."""
from pathlib import Path
import json
import sys
import os
import re
import time
import numpy as np
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

def load_and_sample_datasets(n_ruletaker: int = 100, n_clutrr: int = 100):
    """Load and sample datasets."""
    data_path = Path("full_data_out")
    
    datasets = {'ruletaker': [], 'clutrr': []}
    
    # Load RuleTaker
    ruletaker_files = sorted(data_path.glob("full_data_out_ruletaker_*.json"))
    for rf in ruletaker_files:
        with open(rf, 'r') as f:
            part_data = json.load(f)
            datasets['ruletaker'].extend(part_data['datasets'][0]['examples'])
    
    # Load CLUTRR
    clutrr_file = data_path / "full_data_out_clutrr.json"
    if clutrr_file.exists():
        with open(clutrr_file, 'r') as f:
            clutrr_data = json.load(f)
        datasets['clutrr'] = clutrr_data['datasets'][0]['examples']
    
    # Sample
    if n_ruletaker < len(datasets['ruletaker']):
        datasets['ruletaker'] = datasets['ruletaker'][:n_ruletaker]
    
    if n_clutrr < len(datasets['clutrr']):
        datasets['clutrr'] = datasets['clutrr'][:n_clutrr]
    
    return datasets


def evaluate_problog_safe(problog_code: str):
    """Evaluate ProbLog code safely."""
    try:
        from problog.program import PrologString
        from problog import get_evaluatable
        
        program = PrologString(problog_code)
        result = get_evaluatable().create_from(program).evaluate()
        
        serialized = {}
        for key, value in result.items():
            serialized[str(key)] = float(value)
        
        return serialized
        
    except Exception as e:
        return {'error': str(e)}
