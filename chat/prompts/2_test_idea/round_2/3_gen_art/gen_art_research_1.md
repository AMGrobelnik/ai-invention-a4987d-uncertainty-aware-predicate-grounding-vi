# gen_art_research_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_art`
> Run: `4a015` — Neuro Symbolic Pipeline
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_art_research_1` (sdk_openhands_agent)

### [1] SYSTEM-USER prompt · 2026-06-15 05:19:30 UTC

````
Read and STRICTLY follow these skills: aii-web-tools.

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1/`:
GOOD: `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1/file.py`, `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/4a015/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>

<artifact_plan>
id: gen_plan_research_1_idx1
type: research
title: >-
  Bibliography Fix and Evaluation Metrics Research for Neuro-Symbolic Text-to-Logic Translation
summary: >-
  Comprehensive research plan to (1) locate the real arXiv ID for Kotelevskii et al. 2025 paper on optimal transport for uncertainty
  quantification, (2) identify evaluation metrics and scripts for RuleTaker and CLUTRR datasets, and (3) research ablation
  methods for comparing optimal transport against other uncertainty quantification approaches.
runpod_compute_profile: cpu_light
question: >-
  How to fix the bibliography reference for Kotelevskii et al. 2025, what are the standard evaluation metrics and scripts
  for RuleTaker/CLUTRR datasets in neuro-symbolic text-to-logic translation, and what ablation methods exist for uncertainty
  quantification that can be compared against optimal transport?
research_plan: |-
  ## EXECUTION INSTRUCTIONS FOR RESEARCH AGENT

  You are executing a RESEARCH artifact. Your job is to gather information via web tools (search, fetch, fetch_grep). You do NOT run code, download datasets, or implement algorithms. You produce two outputs:
  1. `research_out.json` - Structured JSON with your findings
  2. `research_report.md` - Comprehensive markdown report

  ---

  ## Phase 1: Locate Kotelevskii et al. 2025 Paper (Priority: HIGH)

  ### Step 1.1: Search for Kotelevskii et al. 2025
  **Execute**: Web search with query: `Kotelevskii multidimensional uncertainty optimal transport 2025 arXiv`

  **Tool**: aii-web-tools (web search)

  **What to look for**:
  - Paper title containing 'Multidimensional Uncertainty Quantification via Optimal Transport'
  - Author names: Kotelevskii (or variant spelling)
  - Year: 2025 (or possibly 2024 if published online in 2024 but officially 2025)
  - arXiv ID in format: arXiv:XXXX.XXXXX

  **If not found**: Try these alternative searches in parallel:
  1. `Kotelevskii uncertainty quantification optimal transport`
  2. `Kotelvskii optimal transport uncertainty` (alternate spelling)
  3. `multidimensional uncertainty quantification optimal transport` (without author name)

  **Success criteria**: Find at least one candidate paper with arXiv ID

  ### Step 1.2: Fetch Paper Page and Extract arXiv ID
  **Execute**: For the most promising search result, fetch the arXiv page or PDF

  **Tool**: aii-web-tools (web fetch)

  **What to extract**:
  - arXiv ID (look for format: `arXiv:2025.XXXXX` or `arXiv:240X.XXXXX`)
  - Full title
  - Author list (complete)
  - Publication venue (conference/journal if accepted)
  - Abstract

  **If arXiv page fetched**: Use fetch_grep to search for 'arXiv:', 'arXiv ID', or the submission number

  **Deliverable**: Verified paper metadata with correct arXiv ID

  ### Step 1.3: Generate BibTeX Entry
  **Execute**: Create BibTeX entry for the paper

  **Options**:
  1. If you found the arXiv ID, construct BibTeX manually:
     ```bibtex
     @article{kotelevskii2025multidimensional,
       title={Multidimensional Uncertainty Quantification via Optimal Transport},
       author={Kotelevskii, Nikita and [other authors]},
       journal={[venue if known]},
       year={2025},
       eprint={arXiv:XXXX.XXXXX},
       archivePrefix={arXiv},
       primaryClass={[subject]}
     }
     ```
  2. Or search for the paper on Semantic Scholar and extract BibTeX

  **Deliverable**: Complete, correctly formatted BibTeX entry

  ---

  ## Phase 2: Research RuleTaker and CLUTRR Evaluation Metrics (Priority: HIGH)

  ### Step 2.1: RuleTaker Dataset - Metrics and Evaluation
  **Execute in parallel**:
  1. Search: `RuleTaker dataset Clark 2020 evaluation metrics accuracy`
  2. Search: `RuleTaker neuro-symbolic evaluation GitHub`
  3. Search: `RuleTaker atomic fact extraction precision recall`

  **Tool**: aii-web-tools (web search)

  **From search results, fetch these key sources**:
  1. Original RuleTaker paper (Clark et al. 2020 - likely arXiv:2004.12298 or similar)
  2. CLOVER paper (mentioned in hypothesis - Ryu et al. 2024)
  3. LINC paper (Sherborne et al. 2023)
  4. Any GitHub repos with RuleTaker evaluation scripts

  **What to extract from fetched papers**:
  - **Primary metric**: Answer accuracy (%) - percentage of questions correctly answered
  - **Secondary metrics**: Proof correctness (if available), atomic fact precision/recall
  - **Evaluation protocol**: Train/validation/test splits, how answers are verified
  - **Baseline results**: What accuracy do current methods achieve?

  **Use fetch_grep to extract**:
  - Exact metric definitions (search for 'accuracy', 'metric', 'evaluation')
  - Numbers in tables (search for 'RuleTaker', 'accuracy', '%')
  - GitHub URLs in papers (search for 'github.com')

  **Deliverable**: Structured summary of RuleTaker metrics with sources

  ### Step 2.2: CLUTRR Dataset - Metrics and Evaluation
  **Execute in parallel**:
  1. Search: `CLUTRR dataset Sinha 2019 evaluation metrics`
  2. Search: `CLUTRR multi-hop reasoning accuracy`
  3. Search: `CLUTRR neuro-symbolic evaluation script`

  **From search results, fetch**:
  1. Original CLUTRR paper (Sinha et al. 2019 - likely from NeurIPS or ACL)
  2. Papers that use CLUTRR for neuro-symbolic evaluation

  **What to extract**:
  - **Primary metric**: Relation prediction accuracy (%) - correctly predicted missing relation
  - **Multi-hop accuracy**: Accuracy broken down by reasoning depth (2-hop, 3-hop, etc.)
  - **Evaluation protocol**: How queries are generated, how answers are verified
  - **Baseline results**: Current state-of-the-art accuracy

  **Deliverable**: Structured summary of CLUTRR metrics with sources

  ### Step 2.3: Hallucination Rate Measurement
  **Execute in parallel**:
  1. Search: `hallucination rate text-to-logic translation evaluation`
  2. Search: `neuro-symbolic hallucination detection metric`
  3. Search: `fact extraction hallucination benchmark`

  **What to extract**:
  - **Definition**: How is hallucination defined? (e.g., generated facts not in source text, or facts contradicting source)
  - **Metric**: Hallucination rate = (number of hallucinated facts) / (total generated facts)
  - **Evaluation method**: Human annotation? Automatic matching to source?
  - **Example calculations**: Any papers that report hallucination rates?

  **Deliverable**: Clear methodology for computing hallucination rate

  ---

  ## Phase 3: Research Ablation Methods for Uncertainty Quantification (Priority: MEDIUM)

  ### Step 3.1: Softmax with Temperature
  **Execute**: Search `softmax temperature uncertainty quantification language models`

  **What to extract**:
  - **Formula**: P(y|x) = softmax(z/T) where T is temperature
  - **How it works**: Higher T → softer probability distribution → higher uncertainty
  - **Implementation**: Apply to LLM token probabilities during text-to-FOL translation
  - **Tuning**: What T values to try (0.5, 1.0, 2.0, etc.)
  - **Pros/Cons**: Simple, fast, but may not capture epistemic uncertainty

  **Fetch these sources**:
  1. Papers on temperature scaling for uncertainty (e.g., Guo et al. 2017 on calibration)
  2. NLP papers using softmax temperature for uncertainty

  **Deliverable**: Implementation guide for softmax with temperature baseline

  ### Step 3.2: Monte Carlo Dropout
  **Execute**: Search `Monte Carlo dropout uncertainty estimation neural networks`

  **What to extract**:
  - **Formula**: Run forward pass K times with dropout enabled, compute variance of predictions
  - **How it works**: Dropout at test time approximates Bayesian inference
  - **Implementation for LLMs**: Challenge - LLMs don't typically use dropout; may need to apply to output layer only
  - **Computational cost**: K forward passes (K=10-100 typical)
  - **Pros/Cons**: Theoretically grounded, but computationally expensive for LLMs

  **Fetch these sources**:
  1. Original MC Dropout paper (Gal & Ghahramani 2016)
  2. Applications to NLP/LLMs

  **Deliverable**: Implementation guide for MC Dropout baseline (or note if infeasible for LLMs)

  ### Step 3.3: Alternative Uncertainty Methods
  **Execute**: Search `uncertainty quantification methods NLP comparison optimal transport`

  **What to look for**:
  - **Bayesian methods**: Variational inference, Bayes by Backprop
  - **Ensemble methods**: Multiple model predictions
  - **Density-based**: Uncertainty via embedding distance
  - **Comparisons**: Any papers comparing these to optimal transport?

  **Deliverable**: List of candidate ablation methods with recommendation

  ---

  ## Phase 4: Synthesize and Format Output

  ### Step 4.1: Create research_out.json
  **Format**:
  ```json
  {
    "answer": "<comprehensive answer to the research question>",
    "sources": [
      {"title": "...", "url": "...", "date": "..."},
      ...
    ],
    "follow_up_questions": [
      "...",
      ...
    ]
  }
  ```

  **Content**:
  - `answer`: Comprehensive narrative covering all findings from Phases 1-3
  - `sources`: All papers, websites, and resources consulted
  - `follow_up_questions`: Any unanswered questions or areas needing more research

  ### Step 4.2: Create research_report.md
  **Structure**:
  1. **Executive Summary**
  2. **Kotelevskii et al. 2025 Paper** (Phase 1 findings)
     - Verified arXiv ID and metadata
     - BibTeX entry
  3. **RuleTaker Evaluation Metrics** (Phase 2.1 findings)
     - Metric definitions
     - Evaluation protocol
     - Links to scripts
     - Baseline results
  4. **CLUTRR Evaluation Metrics** (Phase 2.2 findings)
     - Same structure as RuleTaker section
  5. **Hallucination Rate Measurement** (Phase 2.3 findings)
     - Definition and methodology
     - Example calculations
  6. **Ablation Methods** (Phase 3 findings)
     - Softmax with temperature guide
     - MC Dropout guide
     - Alternative methods
     - Recommendation
  7. **References**

  ---

  ## TOOL USAGE WORKFLOW

  ### Search → Fetch → Fetch_grep Pattern
  For each paper/resource of interest:
  1. **Search**: Discover relevant papers/URLs
  2. **Fetch**: Read the paper/page for gist
  3. **Fetch_grep**: Extract specific details (arXiv ID, metric formulas, numbers)

  ### Parallelization Strategy
  **Maximize parallel tool calls**:
  - Phase 1: Run 3 searches for Kotelevskii variants in parallel
  - Phase 2: Run 3 searches for RuleTaker AND 3 for CLUTRR in parallel (6 total)
  - Phase 3: Run 3 searches for ablation methods in parallel

  **Sequential only when needed**:
  - After searches complete → fetch the most promising results
  - After fetch → use fetch_grep for specific extractions

  ### Time Budget (3 hours)
  - Phase 1: 45 min (search 10 min → fetch 20 min → grep 15 min)
  - Phase 2: 90 min (search 20 min → fetch 40 min → grep 30 min)
  - Phase 3: 45 min (search 15 min → fetch 20 min → grep 10 min)
  - Phase 4: 30 min (synthesis and formatting)
  - Buffer: 30 min

  ---

  ## SPECIFIC SEARCH QUERIES TO EXECUTE

  ### Batch 1: Kotelevskii Paper (Phase 1)
  1. `Kotelevskii multidimensional uncertainty optimal transport 2025`
  2. `Kotelevskii uncertainty quantification optimal transport arXiv`
  3. `multidimensional uncertainty quantification optimal transport 2025`

  ### Batch 2: RuleTaker (Phase 2.1)
  1. `RuleTaker dataset Clark 2020 evaluation`
  2. `RuleTaker neuro-symbolic GitHub evaluation script`
  3. `RuleTaker atomic fact precision recall`

  ### Batch 3: CLUTRR (Phase 2.2)
  1. `CLUTRR dataset Sinha 2019 evaluation metrics`
  2. `CLUTRR multi-hop reasoning accuracy`
  3. `CLUTRR neuro-symbolic evaluation`

  ### Batch 4: Hallucination (Phase 2.3)
  1. `hallucination text-to-logic translation evaluation`
  2. `neuro-symbolic hallucination detection`
  3. `fact extraction hallucination metric`

  ### Batch 5: Ablation Methods (Phase 3)
  1. `softmax temperature uncertainty quantification`
  2. `Monte Carlo dropout uncertainty estimation`
  3. `uncertainty quantification methods NLP comparison`

  ---

  ## DELIVERABLES CHECKLIST

  Before completing the artifact, ensure you have:

  - [ ] **Phase 1**:
    - Verified arXiv ID for Kotelevskii et al. 2025 (not a placeholder)
    - Complete BibTeX entry
    - Paper title, authors, venue

  - [ ] **Phase 2**:
    - RuleTaker: Primary metric, evaluation protocol, script links, baseline numbers
    - CLUTRR: Primary metric, multi-hop breakdown, evaluation protocol, baseline numbers
    - Hallucination: Clear definition, measurement methodology, example

  - [ ] **Phase 3**:
    - Softmax with temperature: Formula, implementation steps, pros/cons
    - MC Dropout: Formula, implementation (or note infeasibility), pros/cons
    - Recommendation on which methods to ablate

  - [ ] **Output Files**:
    - `research_out.json` - Valid JSON, all fields complete
    - `research_report.md` - Well-structured markdown, all sections complete

  ---

  ## NOTES FOR EXECUTOR

  1. **Be thorough**: This research directly enables the experiment design. Incomplete research → poorly designed experiments.
  2. **Verify arXiv IDs**: Always fetch the arXiv page to verify the ID exists and matches the paper.
  3. **Extract exact numbers**: Use fetch_grep to get exact baseline numbers from tables in papers.
  4. **Check GitHub**: Many datasets have official evaluation scripts on GitHub - find and document them.
  5. **Think about feasibility**: For ablation methods (Phase 3), note if any are infeasible for LLMs (e.g., MC Dropout may not apply to transformer LLMs).

  ---

  ## EXPECTED OUTPUT STRUCTURE

  ### research_out.json
  ```json
  {
    "answer": "Comprehensive findings from all phases...",
    "sources": [
      {"title": "RuleTaker: Measuring and Narrowing the Gap Between Human and Machine Reasoning", "url": "https://arxiv.org/abs/2004.12298", "date": "2020"},
      ...
    ],
    "follow_up_questions": [
      "What is the exact Spearman correlation formula for evaluating uncertainty calibration?",
      ...
    ]
  }
  ```

  ### research_report.md
  (See structure in Step 4.2 above - approximately 2000-3000 words covering all findings)
explanation: >-
  This research is critical for the hypothesis validation because: (1) The bibliography must be accurate for academic rigor
  - the current hypothesis references 'Kotelevskii et al. 2025' but likely has a placeholder or incorrect arXiv ID that needs
  to be fixed before paper writing. (2) The evaluation metrics must be precisely defined to measure the success criteria (>5%
  improvement in multi-hop reasoning accuracy, >20% reduction in hallucination rate, Spearman correlation >0.3). Without knowing
  the exact metrics and evaluation protocols for RuleTaker and CLUTRR, the executor cannot properly evaluate the hypothesis.
  (3) The ablation methods (softmax with temperature, Monte Carlo Dropout) need to be researched to design proper comparison
  experiments - the hypothesis mentions comparing optimal transport against other uncertainty quantification methods, but
  the specifics of how to implement these baselines need to be determined. This research directly enables the subsequent experiment
  artifact to be properly designed and executed.
</artifact_plan>

<investigation_process>
1. DIVERGE: Brainstorm multiple angles/framings of the question before searching. Think across fields — what adjacent domains might have relevant insights?
2. SEARCH: Multiple queries per angle with different phrasings to discover the landscape
3. FETCH: Read promising URLs at high level. Snippets are NOT enough — fetch full pages
4. DETAIL: aii-web-tools fetch_grep for specifics from key pages/PDFs
5. CONTRAST: Actively try to disprove your emerging conclusions. Search with different phrasings, "[topic] criticism", "[topic] limitations". Check across fields — the same finding may exist under different names
6. SYNTHESIZE: Integrate into balanced conclusion
7. ITERATE: Expect to repeat steps 2-6 if findings are incomplete or one-sided. Don't settle on first results
8. SUMMARIZE: Output JSON must include 'title' and 'summary' fields
</investigation_process>

<output_requirements>
- Write research_out.json to your workspace with all findings
- Provide your finding as clear prose WITH NUMBERED CITATIONS
- EVERY factual claim must have a citation number in brackets: [1], [2], [1, 3], etc.
- Include BOTH supporting AND contradicting evidence
- Be explicit about confidence level and what would change it
- End with follow-up questions for further investigation
</output_requirements>

Research everything specified in the artifact plan, but you may also investigate additional relevant aspects beyond what's listed. Investigate this question thoroughly.

---

Output the result as JSON to: `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1/.sdk_openhands_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ResearchExpectedFiles": {
      "description": "All expected output files from research artifact.",
      "properties": {
        "output": {
          "description": "Path to research output JSON. Example: 'research_out.json'",
          "title": "Output",
          "type": "string"
        }
      },
      "required": [
        "output"
      ],
      "title": "ResearchExpectedFiles",
      "type": "object"
    },
    "Source": {
      "description": "A source used in the research.",
      "properties": {
        "index": {
          "description": "Citation number (1, 2, 3, ...)",
          "title": "Index",
          "type": "integer"
        },
        "url": {
          "description": "Full URL of the source",
          "title": "Url",
          "type": "string"
        },
        "title": {
          "description": "Title of the article/page",
          "title": "Title",
          "type": "string"
        },
        "summary": {
          "description": "Brief summary of what this source contributed",
          "title": "Summary",
          "type": "string"
        }
      },
      "required": [
        "index",
        "url",
        "title",
        "summary"
      ],
      "title": "Source",
      "type": "object"
    }
  },
  "description": "Research artifact \u2014 structured output + file metadata.\n\nConducts thorough web research using the aii-web-tools skill.\nReturns structured JSON output with citations.",
  "properties": {
    "title": {
      "default": "",
      "description": "Descriptive title (roughly 30-90 characters). Must describe content, NOT a status message.",
      "maxLength": 90,
      "minLength": 30,
      "title": "Title",
      "type": "string"
    },
    "layman_summary": {
      "default": "",
      "description": "One-sentence plain-language summary of what this artifact does, accessible to non-experts. Used only in the per-artifact README, not in downstream prompts.",
      "maxLength": 250,
      "minLength": 80,
      "title": "Layman Summary",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Summary for downstream artifacts: what this artifact provides",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/ResearchExpectedFiles",
      "description": "All output files you created. Must include research_out.json with your research findings."
    },
    "answer": {
      "description": "Comprehensive answer with NUMBERED CITATIONS. Cite sources by number: 'Claim [1].' or 'According to [2, 3]...'",
      "title": "Answer",
      "type": "string"
    },
    "sources": {
      "description": "All sources used, with index matching citation numbers in answer",
      "items": {
        "$ref": "#/$defs/Source"
      },
      "title": "Sources",
      "type": "array"
    },
    "follow_up_questions": {
      "description": "2-3 follow-up questions that emerged from the investigation",
      "items": {
        "type": "string"
      },
      "title": "Follow Up Questions",
      "type": "array"
    }
  },
  "required": [
    "out_expected_files",
    "answer",
    "sources",
    "follow_up_questions"
  ],
  "title": "ResearchArtifact",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `/ai-inventor/aii_data/runs/4a015/3_invention_loop/iter_2/gen_art/gen_art_research_1/.sdk_openhands_agent_struct_out.json`.
````

### [2] HUMAN-USER prompt · 2026-06-15 05:19:30 UTC

```
### Goal

Develop an operational translation pipeline that converts unstructured
textual content (e.g., short legal documents, news articles, kids'
stories) into a formal first-order logic representation. The output
must be capable of (probabilistic) reasoning using a logic reasoner
(like Prolog), leveraging LLMs to dynamically resolve terminology,
concepts, and relations that are not well defined in the explicit text.

### Reviewer Scope

Limit the technical core to areas the reviewer can deeply evaluate.
Other fields are welcome for inspiration but should not host the
substantive contribution.

Reviewer-evaluable areas: semantic technologies, logic programming,
inductive logic programming, information retrieval, machine learning,
LLMs, deep learning, knowledge extraction, knowledge graphs,
reasoning, and text data analytics.

The pipeline should ingest a short document (approx. 3000 characters)
and parse it into a structured, computable format. Methods may combine
an LLM acting as a semantic translation engine (mapping natural text
to first-order logic or Prolog predicates), a running logic
interpreter (like SWI-Prolog) for symbolic execution, and the
integration of upper ontologies like OpenCyc to supply necessary
background structure and taxonomic grounding. Furthermore, an LLM
should be deployed as a probabilistic reasoning engine to handle fuzzy
unifications, semantic similarities, and logical gaps where strict
symbolic matching fails due to language ambiguity.

Evaluation must be rigorous and compare the neuro-symbolic pipeline
against purely neural baselines (e.g., standard RAG, chain-of-thought
prompting) on standard logical reasoning benchmarks (e.g., RuleTaker,
CLUTRR) or custom annotated datasets. It must specifically measure:
(i) the precision and recall of atomic fact extraction directly from
the original document, and (ii) the accuracy of multi-hop fact
extraction and logical deductions that require synthesizing explicit
document facts with implicit common-sense knowledge.

Outputs must provide human-auditable trace-graphs of the reasoning
steps to clearly demonstrate the logical path taken.

Constraints: The pipeline must be highly reproducible on any short,
professionally written documents. Inference must be executable on
commodity hardware, and the system must report a quantified reduction
in hallucination rates compared to raw LLM generation.

### Publication

Target ACL Knowledge Extraction track as the primary venue, with
EMNLP or specialized neuro-symbolic AI conference tracks (e.g., NeSy)
as fallback targets.

### Things to Avoid

Avoid simplistic propositional logic translations of the text. Avoid
purely neural black-box systems that lack interpretable reasoning
traces. The substantive contribution must be an operational, hybrid
method for reasoning with textual content that explicitly minimizes
hallucinations.
```

### [3] SKILL-INPUT — aii-web-tools · 2026-06-15 05:19:36 UTC

The agent loaded the **aii-web-tools** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-web-tools
description: "Web research toolkit: web search (Serper/Google), web page fetch as markdown (HTML and PDF), and regex grep over full page/PDF text. Use whenever a task needs to search the web, read a page, mine a paper/PDF, verify citations, or extract exact quotes, numbers, or methodology from a URL."
---

## Web tools

You have three web capabilities: **search**, **fetch**, and **grep** (exact
regex extraction over a full page or PDF).

**Pick where they come from, in this order:**

1. **If you have built-in `WebSearch` / `WebFetch` tools, PREFER those over the
   scripts below.** They may be **deferred tools** (listed by name but with
   schemas not yet loaded) — if so, call `ToolSearch("select:WebSearch,WebFetch")`
   ONCE to load them, then use them normally. Do not skip them just because they
   need that one extra load step; they are the preferred path. Pair them with the
   `aii_web_tools__fetch_grep` script below when you need exact text / numbers /
   methodology that a summary would miss, or when reading a PDF.
2. **Only if you have NO built-in `WebSearch` / `WebFetch`** (e.g. the OpenHands
   backend), use the scripts in this skill (below). They are our own
   implementations — Serper.dev for search, html2text + PyMuPDF for fetch, and
   regex grep over the full document text. They work without any built-in web
   tools.

Workflow either way: **search** (discover) → **fetch** (read for the gist) →
**grep** (pull exact details / read PDFs).

---

## Running the scripts

Run every script with the skill's pre-provisioned interpreter (it already has
`requests`, `html2text`, `pymupdf`, `python-dotenv`). Set `PY` once:

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-web-tools"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

### 1. Search the web (Serper.dev / Google)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation LLM" --max-results 10
```

Returns ranked title / URL / snippet lines. Use it first to scan the
landscape; snippets are for discovery only — fetch a page before judging it.

### 2. Fetch a page as markdown (HTML or PDF)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" fetch --url "https://arxiv.org/abs/2303.11366" --max-chars 10000
```

`--max-chars` caps output (default 10000); `--char-offset N` pages further in.
Handles PDFs transparently via PyMuPDF.

### 3. Grep a page or PDF (exact regex extraction)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url "https://arxiv.org/pdf/2303.11366" --pattern "verbal reinforcement" --max-matches 20 --context-chars 200
```

Returns only the matching sections with surrounding context — the right tool
for exact numbers, table values, methodology, or long PDFs where a summary
would lose the detail. `-i` for case-insensitive.

**Parallelize** independent searches/fetches in one turn; only sequence a
fetch after the search that produced its URL.

---

## Notes

- The scripts call our ability server. If a script prints
  `Ability service not available`, the server is down — say so rather than
  silently improvising a different search method.
- Do **not** hand-roll your own `requests`/scraping for search when these
  tools are available: Serper returns clean Google results and the fetch/grep
  scripts already handle HTML, PDFs, and encoding.
````

### [4] SYSTEM-USER prompt · 2026-06-15 05:23:10 UTC

```
<validation-feedback>
Attempt 1 failed validation.

Schema validation found 1 problem — fix ALL of them at once:
  - at `title`: 'Bibliography Fix and Evaluation Metrics Research for Neuro-Symbolic Text-to-Logic Translation' is too long (at most 90 characters, got 93)
Every required field must be present and every field type must match the schema.

Please use the Write tool to overwrite `.sdk_openhands_agent_struct_out.json` with corrected JSON. Do not invent new fields; match the schema you were given.
</validation-feedback>
```

### [5] SYSTEM-USER prompt · 2026-06-15 05:23:46 UTC

```
<verification_failed>
Your research output failed verification (attempt 1/10).
</verification_failed>

<schema_errors>
JSON SCHEMA ERRORS:
  - research_out.json: Missing required 'title' field
  - research_out.json: Missing required 'summary' field

Fix: research_out.json must have:
     {
       "answer": "comprehensive answer with [1], [2] citations",
       "sources": [{"index": 1, "url": "...", "title": "...", "summary": "..."}],
       "follow_up_questions": ["Question 1?", "Question 2?"],
       "summary": "what was found"
     }

     Each citation [N] in answer MUST match a source with that index.
</schema_errors>

<content_warnings>
CONTENT ISSUES:
  - research_out.json: 'title' is too short

Fix: Ensure answer is comprehensive, has proper citations, and all sources are cited.
</content_warnings>

<task>
FIX ISSUES:
1. Output valid research_out.json with all required fields
2. Ensure every factual claim has a numbered citation [1], [2], etc.
3. Ensure every source has a matching citation in the answer
</task>
```
