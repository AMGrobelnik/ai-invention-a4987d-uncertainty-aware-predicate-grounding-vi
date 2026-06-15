# Dataset Collection Summary

## Selected Datasets

### 1. tasksource/ruletaker
- **Size**: 268.92 MB
- **Rows**: 480,152
- **Task**: Logical reasoning over natural language rules
- **Format**: context, question, label (entailment/not entailment), config
- **Provenance**: Allen Institute for AI (AI2), Clark et al. 2020
- **Downloads**: 775+
- **Status**: ✓ Downloaded successfully

### 2. tasksource/clutrr
- **Size**: 3.29 MB
- **Rows**: 12,064
- **Task**: Relational reasoning over family relationships
- **Format**: sentence1 (story), sentence2 (entity pair), labels (relationship)
- **Provenance**: Sinha et al. 2019 (EMNLP), Facebook Research
- **Downloads**: 114+
- **Status**: ✓ Downloaded successfully

### 3. tasksource/proofwriter (100K subset)
- **Size**: 117.06 MB
- **Rows**: 100,000
- **Task**: Proof generation and logical reasoning
- **Format**: theory, question, answer, proof, metadata
- **Provenance**: Tafjord et al. 2021
- **Downloads**: 2,132+
- **Status**: ✓ Downloaded successfully (subset to meet 300MB limit)

### 4. flaitenberger/LogicalReasoning-hard-v3 (50K subset)
- **Size**: 225.23 MB
- **Rows**: 50,000
- **Task**: Hard logical reasoning challenges
- **Format**: constants, predicates, premises, proof, question, answer, metadata
- **Provenance**: Referenced in arXiv:2404.15522
- **Downloads**: 1,617+
- **Status**: ✓ Downloaded successfully (subset to meet 300MB limit)

## Dataset Quality Verification

All datasets have been verified for:
- ✓ Clear provenance (papers, official sources)
- ✓ >100 downloads (popularity indicator)
- ✓ Clear documentation (dataset cards, papers)
- ✓ Meaningful features (not anonymized)
- ✓ Suitable structure for logical/relational reasoning tasks
- ✓ Under 300MB size limit

## Files Created

- `temp/datasets/full_tasksource_ruletaker.json` (268.92 MB)
- `temp/datasets/full_tasksource_clutrr.json` (3.29 MB)
- `temp/datasets/full_tasksource_proofwriter_100K.json` (117.06 MB)
- `temp/datasets/full_LogicalReasoning_hard_v3_50K.json` (225.23 MB)
- Preview files for all datasets

## Next Steps

These datasets are ready for use in the research experiment evaluating logical reasoning and relational reasoning capabilities.
