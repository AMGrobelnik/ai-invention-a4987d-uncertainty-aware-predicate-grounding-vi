#!/usr/bin/env python3
"""Data preparation script for logical reasoning datasets.

This script loads datasets from full_data_out/ directory (split files),
standardizes them to the exp_sel_data_out.json schema, and saves to output.
"""

from pathlib import Path
import json
import sys
import glob

# Add logging
from loguru import logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")


@logger.catch(reraise=True)
def main():
    """Load and standardize datasets."""
    
    # Create output directory
    output_dir = Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize result structure
    result = {"datasets": []}
    
    # Process tasksource/ruletaker (read from split files)
    logger.info("Processing tasksource/ruletaker...")
    ruletaker_files = sorted(glob.glob("full_data_out/full_data_out_ruletaker_*.json"))
    ruletaker_examples = []
    for rf in ruletaker_files:
        with open(rf, 'r') as f:
            part_data = json.load(f)
            ruletaker_examples.extend(part_data['datasets'][0]['examples'])
    
    if ruletaker_examples:
        result["datasets"].append({
            "dataset": "ruletaker",
            "examples": ruletaker_examples
        })
        logger.info(f"Loaded {len(ruletaker_examples)} examples from ruletaker")
    
    # Process tasksource/clutrr
    logger.info("Processing tasksource/clutrr...")
    clutrr_file = Path("full_data_out/full_data_out_clutrr.json")
    if clutrr_file.exists():
        with open(clutrr_file, 'r') as f:
            clutrr_data = json.load(f)
        result["datasets"].append(clutrr_data['datasets'][0])
        logger.info(f"Loaded {len(clutrr_data['datasets'][0]['examples'])} examples from clutrr")
    
    # Save output (combined)
    output_file = Path("full_data_out_combined.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Saved {len(result['datasets'])} datasets to {output_file}")
    total_examples = sum(len(d["examples"]) for d in result["datasets"])
    logger.info(f"Total examples: {total_examples}")


if __name__ == "__main__":
    main()
