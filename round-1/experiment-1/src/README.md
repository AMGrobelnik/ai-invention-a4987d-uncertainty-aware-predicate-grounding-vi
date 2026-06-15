# Neuro-Symbolic Pipeline with Optimal Transport-based Predicate Grounding

## Experiment Overview

This experiment implements and evaluates a neuro-symbolic text-to-logic translation pipeline that uses entropy-regularized optimal transport (OT) for uncertainty-aware predicate grounding.

### Key Components

1. **Semantic Similarity Module**: Computes similarity between text terms and predicate vocabulary (uses simple character-level similarity by default; can optionally use sentence-transformers)

2. **Optimal Transport Module**: Solves entropy-regularized OT using Sinkhorn algorithm (uses POT library if available, otherwise manual implementation)

3. **Text Parser**: Extracts predicate-relevant terms from text documents

4. **Baseline Pipeline**: Deterministic predicate assignment (each term -> most similar predicate)

5. **OT-Enhanced Pipeline**: Uncertainty-aware predicate grounding using OT (soft assignment with entropy as uncertainty measure)

6. **Evaluation Framework**: Evaluates both pipelines on reasoning datasets

### Metrics

- Multi-hop reasoning accuracy
- Hallucination rate
- Uncertainty calibration (Spearman correlation between OT entropy and actual error)
- Reasoning trace quality

## Installation

```bash
# Create virtual environment
uv venv .venv --python=3.12

# Install dependencies
uv pip install --python=.venv/bin/python numpy scipy POT sentence-transformers datasets problog loguru psutil jsonschema
```

## Usage

### Quick Test (Dummy Data)

```bash
.venv/bin/python method.py --dataset dummy --num-examples 5 --output method_out.json --no-transformers
```

### Run with Sentence Transformers (Better Similarity)

```bash
.venv/bin/python method.py --dataset dummy --num-examples 10 --output method_out.json
```

### Validate Output Against Schema

```bash
SKILL_DIR="/ai-inventor/.claude/skills/aii-json"
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_gen_sol_out --file method_out.json
```

## Output Format

The output follows the `exp_gen_sol_out.json` schema:

```json
{
  "datasets": [
    {
      "dataset": "dummy",
      "examples": [
        {
          "input": "document text",
          "output": "expected answer",
          "predict_baseline": "ProbLog code from baseline",
          "predict_ot_enhanced": "ProbLog code from OT-enhanced"
        }
      ]
    }
  ]
}
```

A full output file with additional metadata is also saved as `full_method_out.json`.

## Results

The experiment logs:
- Baseline success rate
- OT-enhanced success rate  
- Uncertainty calibration (Spearman correlation)
- OT uncertainty statistics (mean, std, min, max)

## Files

- `method.py`: Main experiment script
- `method_out.json`: Schema-compliant output
- `full_method_out.json`: Full output with metadata
- `logs/run.log`: Detailed experiment logs

## Notes

- The current implementation uses simple character-level similarity by default (fast, no model download)
- For better similarity, use `--no-transformers` flag to enable sentence-transformers (requires model download)
- POT library is used for optimal transport if available; otherwise falls back to manual Sinkhorn implementation
- ProbLog is used for logic program execution
