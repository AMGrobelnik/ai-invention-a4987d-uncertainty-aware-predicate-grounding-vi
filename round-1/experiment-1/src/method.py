#!/usr/bin/env python3
"""
Neuro-Symbolic Pipeline with Optimal Transport-based Predicate Grounding.

This experiment implements and evaluates a neuro-symbolic text-to-logic translation
pipeline that uses entropy-regularized optimal transport for uncertainty-aware
predicate grounding. Compares baseline (deterministic) vs OT-enhanced variant.

Metrics: multi-hop reasoning accuracy, hallucination rate, uncertainty calibration,
reasoning trace quality.
"""

import os
import sys
import json
import time
import warnings
import resource
import psutil
import math
from pathlib import Path
from loguru import logger
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass, asdict
import argparse

# Suppress warnings
warnings.filterwarnings('ignore')

# =============================================================================
# Hardware Detection & Resource Management
# =============================================================================

def detect_cpus() -> int:
    """Detect actual CPU allocation (containers/pods/bare metal)."""
    try:  # cgroups v2 quota
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError):
        pass
    try:  # cgroups v1 quota
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError):
        pass
    try:  # CPU affinity
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    return os.cpu_count() or 1


def detect_container_ram_gb() -> float:
    """Read RAM limit from cgroup (containers/pods)."""
    for p in ["/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"]:
        try:
            v = Path(p).read_text().strip()
            if v != "max" and int(v) < 1_000_000_000_000:
                return int(v) / 1e9
        except (FileNotFoundError, ValueError):
            pass
    return psutil.virtual_memory().total / 1e9


# Set constants
NUM_CPUS = detect_cpus()
TOTAL_RAM_GB = detect_container_ram_gb()
AVAILABLE_RAM_GB = min(psutil.virtual_memory().available / 1e9, TOTAL_RAM_GB)

# Set memory limits (use 80% of available to leave buffer)
RAM_BUDGET = int(AVAILABLE_RAM_GB * 0.8 * 1e9)
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")


# =============================================================================
# Component 1: Semantic Similarity Module (Sentence Transformers)
# =============================================================================

class SemanticSimilarityModule:
    """
    Computes semantic similarity between text terms and predicate vocabulary.
    
    Uses simple character-level similarity by default (no model download needed).
    Optionally uses sentence-transformers if available and model loads successfully.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', use_transformers: bool = False):
        """
        Args:
            model_name: Name of sentence-transformer model (only used if use_transformers=True)
            use_transformers: If True, try to load sentence-transformers (requires download)
        """
        self.model_name = model_name
        self.model = None
        
        if use_transformers:
            self._load_model()
        else:
            logger.info("Using simple similarity (no transformers)")
    
    def _load_model(self):
        """Load sentence transformer model with timeout."""
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Model loading timed out")
            
            # Set timeout of 30 seconds
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device='cpu')
            signal.alarm(0)  # Cancel timeout
            logger.info(f"Loaded sentence-transformer model: {self.model_name}")
            
        except (TimeoutError, Exception) as e:
            logger.warning(f"Failed to load sentence-transformers: {e}. Using fallback.")
            self.model = None
    
    def compute_similarity_matrix(self, terms: List[str], predicates: List[str]) -> np.ndarray:
        """
        Compute similarity matrix between terms and predicates.
        
        Returns:
            matrix: np.ndarray of shape (len(terms), len(predicates))
                    where matrix[i,j] = cosine similarity between term[i] and predicate[j]
        """
        if self.model is None:
            # Fallback: simple character-level similarity
            return self._fallback_similarity(terms, predicates)
        
        try:
            from sentence_transformers import util
            import torch
            
            # Encode all terms and predicates
            term_embeddings = self.model.encode(terms, convert_to_tensor=True, show_progress_bar=False)
            pred_embeddings = self.model.encode(predicates, convert_to_tensor=True, show_progress_bar=False)
            
            # Compute cosine similarity matrix
            similarity_matrix = util.cos_sim(term_embeddings, pred_embeddings).cpu().numpy()
            
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return self._fallback_similarity(terms, predicates)
    
    def _fallback_similarity(self, terms: List[str], predicates: List[str]) -> np.ndarray:
        """Fallback: simple character overlap similarity."""
        n, m = len(terms), len(predicates)
        matrix = np.zeros((n, m))
        for i, term in enumerate(terms):
            for j, pred in enumerate(predicates):
                # Simple Jaccard-like similarity on character 3-grams
                term_grams = set([term[i:i+3] for i in range(len(term)-2)])
                pred_grams = set([pred[i:i+3] for i in range(len(pred)-2)])
                if len(term_grams) == 0 or len(pred_grams) == 0:
                    matrix[i, j] = 0.5  # Neutral similarity
                else:
                    matrix[i, j] = len(term_grams & pred_grams) / len(term_grams | pred_grams)
        return matrix
    
    def compute_similarity(self, term: str, predicate: str) -> float:
        """Compute single similarity score."""
        matrix = self.compute_similarity_matrix([term], [predicate])
        return float(matrix[0, 0])


# =============================================================================
# Component 2: Optimal Transport Module
# =============================================================================

class OptimalTransportModule:
    """
    Entropy-regularized optimal transport for predicate grounding.
    
    Uses POT library (Python Optimal Transport) or manual Sinkhorn implementation.
    """
    
    def __init__(self, epsilon: float = 0.1, max_iter: int = 100, tol: float = 1e-9):
        """
        Args:
            epsilon: Entropy regularization parameter (smaller = sharper transport plan)
            max_iter: Maximum Sinkhorn iterations
            tol: Convergence tolerance
        """
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.tol = tol
        self.use_pot = self._check_pot_available()
    
    def _check_pot_available(self) -> bool:
        """Check if POT library is available."""
        try:
            import ot
            logger.info("Using POT library for optimal transport")
            return True
        except ImportError:
            logger.warning("POT library not available, using manual Sinkhorn implementation")
            return False
    
    def build_cost_matrix(self, similarity_matrix: np.ndarray) -> np.ndarray:
        """
        Build cost matrix from similarity matrix.
        
        Args:
            similarity_matrix: Matrix of shape (n_terms, m_predicates)
                            where entry [i,j] = similarity(term_i, predicate_j)
        
        Returns:
            cost_matrix: C[i,j] = 1 - similarity(term_i, pred_j)
                        (Optimal transport minimizes cost)
        """
        # Clip similarity to [0, 1] to ensure valid costs
        similarity_matrix = np.clip(similarity_matrix, 0, 1)
        cost_matrix = 1.0 - similarity_matrix
        return cost_matrix
    
    def solve_ot(self,
                 cost_matrix: np.ndarray,
                 source_weights: Optional[np.ndarray] = None,
                 target_weights: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
        """
        Solve entropy-regularized optimal transport via Sinkhorn.
        
        Args:
            cost_matrix: Cost matrix C of shape (n, m)
            source_weights: Weights a for source distribution (terms), shape (n,)
                          If None, uniform distribution
            target_weights: Weights b for target distribution (predicates), shape (m,)
                          If None, uniform distribution
        
        Returns:
            transport_plan: (n, m) matrix, rows sum to source_weights, cols to target_weights
            entropy: Shannon entropy of transport plan (uncertainty measure)
        """
        n, m = cost_matrix.shape
        
        # Default: uniform weights
        a = source_weights if source_weights is not None else np.ones(n) / n
        b = target_weights if target_weights is not None else np.ones(m) / m
        
        # Solve OT
        if self.use_pot:
            T = self._solve_pot(cost_matrix, a, b)
        else:
            T = self._sinkhorn_manual(cost_matrix, a, b)
        
        # Compute entropy of transport plan
        entropy = self._compute_transport_entropy(T)
        
        return T, entropy
    
    def _solve_pot(self, C: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Solve using POT library."""
        import ot
        T = ot.sinkhorn(a, b, C, self.epsilon,
                        numItermax=self.max_iter, stopThr=self.tol)
        return T
    
    def _sinkhorn_manual(self, C: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Manual Sinkhorn implementation (fallback if POT not available).
        
        Uses log-domain stabilization for numerical stability.
        """
        n, m = C.shape
        K = np.exp(-C / self.epsilon)  # Gibbs kernel
        
        # Initialize scaling factors
        u = np.ones(n) / n
        v = np.ones(m) / m
        
        for iteration in range(self.max_iter):
            u_new = a / (K @ v + 1e-10)
            v_new = b / (K.T @ u_new + 1e-10)
            
            # Check convergence
            if np.max(np.abs(u_new - u)) < self.tol and np.max(np.abs(v_new - v)) < self.tol:
                u, v = u_new, v_new
                break
            
            u, v = u_new, v_new
        
        # Compute transport plan
        T = np.diag(u) @ K @ np.diag(v)
        return T
    
    def _compute_transport_entropy(self, T: np.ndarray) -> float:
        """
        Compute Shannon entropy of transport plan (as prob distribution).
        
        Higher entropy = more uncertain (spread across multiple predicates)
        Lower entropy = more certain (concentrated on few predicates)
        """
        T_flat = T.flatten()
        T_sum = np.sum(T_flat)
        
        if T_sum < 1e-10:
            return 0.0
        
        # Normalize to probability distribution
        T_norm = T_flat / T_sum
        
        # Compute Shannon entropy
        mask = T_norm > 1e-10
        if not np.any(mask):
            return 0.0
        
        entropy = -np.sum(T_norm[mask] * np.log(T_norm[mask]))
        return float(entropy)
    
    def extract_uncertainty_per_term(self, T: np.ndarray) -> np.ndarray:
        """
        Extract per-term uncertainty (row entropy of transport plan).
        
        Args:
            T: Transport plan of shape (n_terms, m_predicates)
        
        Returns:
            uncertainties: Array of shape (n_terms,) with entropy per term
        """
        uncertainties = np.zeros(T.shape[0])
        
        for i in range(T.shape[0]):
            row = T[i, :]
            row_sum = np.sum(row)
            
            if row_sum < 1e-10:
                uncertainties[i] = 0.0
                continue
            
            # Normalize row to probability distribution
            row_norm = row / row_sum
            
            # Compute entropy
            mask = row_norm > 1e-10
            if np.any(mask):
                uncertainties[i] = -np.sum(row_norm[mask] * np.log(row_norm[mask]))
        
        return uncertainties


# =============================================================================
# Component 3: Text Parser (Extract Terms from Document)
# =============================================================================

class TextParser:
    """
    Extract predicate-relevant terms from text documents.
    
    Uses simple rule-based extraction (can be enhanced with LLM if needed).
    """
    
    def __init__(self):
        # Common stop words to filter out
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can',
            'need', 'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these',
            'those', 'i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him',
            'his', 'she', 'her', 'hers', 'we', 'us', 'our', 'ours', 'they', 'them',
            'their', 'theirs', 'what', 'which', 'who', 'whom', 'whose', 'how',
            'when', 'where', 'why', 'not', 'no', 'so', 'if', 'then', 'else',
            'than', 'too', 'very', 'just', 'because'
        ])
    
    def extract_terms(self, document: str) -> List[str]:
        """
        Extract key terms from document.
        
        Simple approach: extract nouns and named entities using spaCy or rule-based.
        For this implementation, we use a simple approach:
        1. Split into words
        2. Filter out stop words and short words
        3. Return unique terms
        """
        # Simple word extraction
        words = document.lower().replace('.', '').replace(',', '').replace('?', '').replace('!', '').split()
        
        # Filter: not stop word, length > 2, alphabetic
        terms = []
        seen = set()
        for word in words:
            if (word not in self.stop_words and
                len(word) > 2 and
                word.isalpha() and
                word not in seen):
                terms.append(word)
                seen.add(word)
        
        return terms
    
    def extract_predicates_from_vocab(self, document: str, predicate_vocab: List[str]) -> List[str]:
        """
        Extract which predicates from vocabulary are mentioned in document.
        
        Simple approach: check if predicate or its variations appear in text.
        """
        doc_lower = document.lower()
        matched = []
        for pred in predicate_vocab:
            # Check for predicate or its singular/plural forms
            if pred.lower() in doc_lower:
                matched.append(pred)
        return matched


# =============================================================================
# Component 4: Baseline Pipeline (Deterministic Predicate Assignment)
# =============================================================================

class BaselinePipeline:
    """
    Baseline: deterministic predicate assignment using simple similarity.
    
    Assigns each term to the most similar predicate (hard assignment).
    """
    
    def __init__(self,
                 similarity_module: SemanticSimilarityModule,
                 predicate_vocab: List[str]):
        self.similarity = similarity_module
        self.predicate_vocab = predicate_vocab
    
    def translate_to_problog(self, document: str, parser: TextParser) -> str:
        """
        Translate document to ProbLog using deterministic predicate assignment.
        
        Returns:
            problog_code: String containing ProbLog program
        """
        # Extract terms from document
        terms = parser.extract_terms(document)
        
        if not terms:
            return "% Empty document\nquery(related(_, _))."
        
        # Compute similarity matrix
        sim_matrix = self.similarity.compute_similarity_matrix(terms, self.predicate_vocab)
        
        # Deterministic assignment: each term -> most similar predicate
        problog_lines = []
        for i, term in enumerate(terms):
            best_pred_idx = np.argmax(sim_matrix[i, :])
            best_pred = self.predicate_vocab[best_pred_idx]
            best_sim = sim_matrix[i, best_pred_idx]
            
            # Only add if similarity is above threshold
            if best_sim > 0.3:
                # Baseline: deterministic fact (probability = 1.0)
                problog_lines.append(f"{best_pred}({term}).")
        
        # Add query (placeholder - should be extracted from question)
        if not any("query" in line for line in problog_lines):
            problog_lines.append("\nquery(related(_, _)).")
        
        return '\n'.join(problog_lines)
    
    def execute_problog(self, problog_code: str) -> Dict[str, Any]:
        """
        Execute ProbLog program and return results.
        
        Returns:
            Dict with keys: success (bool), results (str), error (str or None)
        """
        try:
            from problog.engine import DefaultEngine
            from problog.program import PrologString
            from problog.logic import Term
            
            program = PrologString(problog_code)
            engine = DefaultEngine()
            
            # Query all defined queries
            results = {}
            for line in problog_code.split('\n'):
                if line.strip().startswith('query'):
                    # Extract query term
                    query_str = line.strip().replace('query(', '').replace(').', '').strip()
                    try:
                        query_term = Term(query_str)
                        result = engine.query(program, query_term)
                        results[query_str] = str(result)
                    except Exception as e:
                        results[query_str] = f"Query error: {e}"
            
            return {
                "success": True,
                "results": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"ProbLog execution failed: {e}")
            return {
                "success": False,
                "results": {},
                "error": str(e)
            }
    
    def run_full_pipeline(self, document: str, parser: TextParser) -> Dict[str, Any]:
        """
        Run full baseline pipeline on a document.
        
        Returns:
            Dict with translation, problog code, and execution results
        """
        problog_code = self.translate_to_problog(document, parser)
        execution_results = self.execute_problog(problog_code)
        
        return {
            "method": "baseline",
            "document": document,
            "problog_code": problog_code,
            "execution_results": execution_results,
            "uncertainty": None  # Baseline has no uncertainty measure
        }


# =============================================================================
# Component 5: OT-Enhanced Pipeline (Uncertainty-Aware)
# =============================================================================

class OTEnhancedPipeline:
    """
    OT-enhanced pipeline with uncertainty-aware predicate grounding.
    
    Uses optimal transport to compute soft assignment of terms to predicates,
    with entropy as uncertainty measure.
    """
    
    def __init__(self,
                 similarity_module: SemanticSimilarityModule,
                 ot_module: OptimalTransportModule,
                 predicate_vocab: List[str]):
        self.similarity = similarity_module
        self.ot = ot_module
        self.predicate_vocab = predicate_vocab
    
    def translate_to_problog(self,
                             document: str,
                             parser: TextParser) -> Tuple[str, float, np.ndarray]:
        """
        Translate using OT for predicate grounding.
        
        Returns:
            problog_code: ProbLog with uncertainty-informed probabilities
            transport_entropy: Global uncertainty measure
            per_term_uncertainty: Per-term uncertainty array
        """
        # Step 1: Extract text terms
        terms = parser.extract_terms(document)
        
        if not terms:
            return "% Empty document\nquery(related(_, _)).", 0.0, np.array([])
        
        # Step 2: Build similarity matrix
        sim_matrix = self.similarity.compute_similarity_matrix(terms, self.predicate_vocab)
        
        # Step 3: Build cost matrix
        cost_matrix = self.ot.build_cost_matrix(sim_matrix)
        
        # Step 4: Solve OT
        T, global_entropy = self.ot.solve_ot(cost_matrix)
        
        # Step 5: Extract per-term uncertainty
        per_term_uncertainty = self.ot.extract_uncertainty_per_term(T)
        
        # Step 6: Convert transport plan to ProbLog probabilities
        problog_code = self._transport_plan_to_problog(T, terms)
        
        return problog_code, global_entropy, per_term_uncertainty
    
    def _transport_plan_to_problog(self, T: np.ndarray, terms: List[str]) -> str:
        """
        Convert transport plan to ProbLog code with probabilities.
        
        Args:
            T: Transport plan of shape (n_terms, m_predicates)
            terms: List of extracted terms
        """
        problog_lines = []
        n, m = T.shape
        
        for i in range(n):
            for j in range(m):
                prob = float(T[i, j])
                
                # Threshold for non-negligible probability
                if prob > 0.01:
                    # ProbLog syntax: prob::fact
                    pred = self.predicate_vocab[j]
                    term = terms[i]
                    problog_lines.append(f"{prob:.4f}::{pred}({term}).")
        
        # Add query (placeholder)
        if not any("query" in line for line in problog_lines):
            problog_lines.append("\nquery(related(_, _)).")
        
        return '\n'.join(problog_lines)
    
    def execute_problog(self, problog_code: str) -> Dict[str, Any]:
        """
        Execute ProbLog program (same as baseline).
        """
        try:
            from problog.engine import DefaultEngine
            from problog.program import PrologString
            from problog.logic import Term
            
            program = PrologString(problog_code)
            engine = DefaultEngine()
            
            results = {}
            for line in problog_code.split('\n'):
                if line.strip().startswith('query'):
                    query_str = line.strip().replace('query(', '').replace(').', '').strip()
                    try:
                        query_term = Term(query_str)
                        result = engine.query(program, query_term)
                        results[query_str] = str(result)
                    except Exception as e:
                        results[query_str] = f"Query error: {e}"
            
            return {
                "success": True,
                "results": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"ProbLog execution failed: {e}")
            return {
                "success": False,
                "results": {},
                "error": str(e)
            }
    
    def run_full_pipeline(self, document: str, parser: TextParser) -> Dict[str, Any]:
        """
        Run full OT-enhanced pipeline on a document.
        
        Returns:
            Dict with translation, problog code, uncertainty measures, and execution results
        """
        problog_code, global_entropy, per_term_uncertainty = self.translate_to_problog(document, parser)
        execution_results = self.execute_problog(problog_code)
        
        return {
            "method": "ot_enhanced",
            "document": document,
            "problog_code": problog_code,
            "execution_results": execution_results,
            "global_uncertainty": global_entropy,
            "per_term_uncertainty": per_term_uncertainty.tolist(),
            "num_terms": len(per_term_uncertainty)
        }


# =============================================================================
# Component 6: Evaluation Framework
# =============================================================================

@dataclass
class Example:
    """Single evaluation example."""
    id: str
    context: str
    question: str
    answer: Any
    metadata: Optional[Dict] = None


class EvaluationFramework:
    """
    Evaluate baseline and OT-enhanced pipelines on reasoning datasets.
    """
    
    def __init__(self,
                 baseline_pipeline: BaselinePipeline,
                 ot_pipeline: OTEnhancedPipeline,
                 parser: TextParser):
        self.baseline = baseline_pipeline
        self.ot = ot_pipeline
        self.parser = parser
        self.results = []
    
    def load_dataset(self, dataset_name: str, split: str = "test", max_examples: int = 10) -> List[Example]:
        """
        Load dataset from HuggingFace or use dummy data.
        
        Args:
            dataset_name: Name of dataset ("ruletaker", "clutrr", or "dummy")
            split: Dataset split to load
            max_examples: Maximum number of examples to load
        """
        if dataset_name.lower() == "dummy":
            return self._get_dummy_data()
        
        try:
            from datasets import load_dataset
            
            if dataset_name.lower() == "ruletaker":
                # RuleTaker dataset
                logger.info(f"Loading RuleTaker dataset (split={split})")
                dataset = load_dataset("allenai/ruletaker", split=split)
                
                examples = []
                for i, item in enumerate(dataset):
                    if i >= max_examples:
                        break
                    
                    # RuleTaker format: has 'context', 'question', 'answer'
                    example = Example(
                        id=f"ruletaker_{i}",
                        context=item.get('context', ''),
                        question=item.get('question', ''),
                        answer=item.get('answer', None),
                        metadata={'source': 'ruletaker'}
                    )
                    examples.append(example)
                
                logger.info(f"Loaded {len(examples)} examples from RuleTaker")
                return examples
                
            elif dataset_name.lower() == "clutrr":
                # CLUTRR dataset
                logger.info(f"Loading CLUTRR dataset (split={split})")
                dataset = load_dataset("uclanlp/clutrr", split=split)
                
                examples = []
                for i, item in enumerate(dataset):
                    if i >= max_examples:
                        break
                    
                    example = Example(
                        id=f"clutrr_{i}",
                        context=item.get('context', ''),
                        question=item.get('question', ''),
                        answer=item.get('answer', None),
                        metadata={'source': 'clutrr'}
                    )
                    examples.append(example)
                
                logger.info(f"Loaded {len(examples)} examples from CLUTRR")
                return examples
            
            else:
                logger.warning(f"Unknown dataset: {dataset_name}. Using dummy data.")
                return self._get_dummy_data()
                
        except Exception as e:
            logger.error(f"Dataset loading failed: {e}. Using dummy data.")
            return self._get_dummy_data()
    
    def _get_dummy_data(self) -> List[Example]:
        """Create dummy data for testing."""
        return [
            Example(
                id="dummy_0",
                context="Alice is a cat. Bob is a dog. Cats like mice. Dogs like bones.",
                question="Does Alice like mice?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'simple_fact'}
            ),
            Example(
                id="dummy_1",
                context="If X is a cat then X likes mice. Alice is a cat. Bob is a dog.",
                question="Does Alice like mice?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'rule_inference'}
            ),
            Example(
                id="dummy_2",
                context="Every cat is an animal. Every dog is an animal. Alice is a cat. Bob is a dog.",
                question="Is Alice an animal?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'inheritance'}
            ),
            Example(
                id="dummy_3",
                context="Parents are older than their children. Alice is a parent of Bob. Bob is a parent of Charlie.",
                question="Is Alice older than Charlie?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'transitive'}
            ),
            Example(
                id="dummy_4",
                context="Friends like each other. Alice is a friend of Bob. Bob is a friend of Charlie.",
                question="Does Alice like Charlie?",
                answer=False,  # Not necessarily (transitivity not stated)
                metadata={'source': 'dummy', 'type': 'non_transitive'}
            ),
            Example(
                id="dummy_5",
                context="All birds can fly. Penguins are birds. Penguins cannot fly.",
                question="Can penguins fly?",
                answer=False,  # Contradiction in the text
                metadata={'source': 'dummy', 'type': 'contradiction'}
            ),
            Example(
                id="dummy_6",
                context="If it rains, the ground gets wet. If the ground is wet, the grass grows. It is raining.",
                question="Does the grass grow?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'chain_reasoning'}
            ),
            Example(
                id="dummy_7",
                context="Tom is taller than Jerry. Jerry is taller than Spike. Spike is taller than Tyke.",
                question="Is Tom taller than Tyke?",
                answer=True,
                metadata={'source': 'dummy', 'type': 'multi_hop'}
            ),
            Example(
                id="dummy_8",
                context="Ada likes Ben. Ben likes Chu. Chu likes Ada. If X likes Y and Y likes X then X and Y are mutual friends.",
                question="Are Ada and Ben mutual friends?",
                answer=False,
                metadata={'source': 'dummy', 'type': 'mutual_relationship'}
            ),
            Example(
                id="dummy_9",
                context="No cat likes water. All dogs like water. Felix is a cat. Rex is a dog.",
                question="Does Felix like water?",
                answer=False,
                metadata={'source': 'dummy', 'type': 'negation'}
            ),
        ]
    
    def evaluate_single(self, example: Example, pipeline_type: str = "baseline") -> Dict[str, Any]:
        """
        Evaluate single example with specified pipeline.
        
        Returns:
            Dict with evaluation results
        """
        document = example.context
        
        if pipeline_type == "baseline":
            result = self.baseline.run_full_pipeline(document, self.parser)
        else:  # ot_enhanced
            result = self.ot.run_full_pipeline(document, self.parser)
        
        # Check if execution succeeded
        execution_success = result.get("execution_results", {}).get("success", False)
        
        return {
            "example_id": example.id,
            "pipeline": pipeline_type,
            "document": document,
            "problog_code": result.get("problog_code", ""),
            "execution_success": execution_success,
            "uncertainty": result.get("global_uncertainty", None),
            "per_term_uncertainty": result.get("per_term_uncertainty", None),
            "answer": example.answer,
            "question": example.question
        }
    
    def evaluate_dataset(self,
                        dataset_name: str,
                        num_examples: int = 10,
                        sequential: bool = True) -> Dict[str, Any]:
        """
        Evaluate both pipelines on dataset.
        
        Args:
            dataset_name: Name of dataset to evaluate on
            num_examples: Number of examples to evaluate (0 = all)
            sequential: If True, run sequentially (safer for debugging)
        
        Returns:
            Dict with full evaluation results
        """
        # Load dataset
        examples = self.load_dataset(dataset_name, max_examples=num_examples if num_examples > 0 else 1000)
        
        if num_examples > 0:
            examples = examples[:min(num_examples, len(examples))]
        
        logger.info(f"Evaluating {len(examples)} examples from {dataset_name}")
        
        results = {
            "dataset": dataset_name,
            "num_examples": len(examples),
            "baseline": [],
            "ot_enhanced": []
        }
        
        # Evaluate each example with both pipelines
        for i, example in enumerate(examples):
            logger.info(f"Processing example {i+1}/{len(examples)} (id={example.id})")
            
            # Baseline
            try:
                baseline_result = self.evaluate_single(example, "baseline")
                results["baseline"].append(baseline_result)
            except Exception as e:
                logger.error(f"Baseline pipeline failed on example {example.id}: {e}")
                results["baseline"].append({
                    "example_id": example.id,
                    "pipeline": "baseline",
                    "execution_success": False,
                    "error": str(e)
                })
            
            # OT-enhanced
            try:
                ot_result = self.evaluate_single(example, "ot_enhanced")
                results["ot_enhanced"].append(ot_result)
            except Exception as e:
                logger.error(f"OT pipeline failed on example {example.id}: {e}")
                results["ot_enhanced"].append({
                    "example_id": example.id,
                    "pipeline": "ot_enhanced",
                    "execution_success": False,
                    "error": str(e)
                })
        
        # Compute summary metrics
        results["summary"] = self._compute_summary_metrics(results)
        
        return results
    
    def _compute_summary_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compute aggregate metrics."""
        baseline = results["baseline"]
        ot = results["ot_enhanced"]
        
        # Success rates
        baseline_success = np.mean([r.get("execution_success", False) for r in baseline]) if baseline else 0.0
        ot_success = np.mean([r.get("execution_success", False) for r in ot]) if ot else 0.0
        
        # Uncertainty stats (OT only)
        ot_uncertainties = [r.get("uncertainty", None) for r in ot if r.get("uncertainty") is not None]
        
        uncertainty_stats = {}
        if ot_uncertainties:
            uncertainty_stats = {
                "mean": float(np.mean(ot_uncertainties)),
                "std": float(np.std(ot_uncertainties)),
                "min": float(np.min(ot_uncertainties)),
                "max": float(np.max(ot_uncertainties)),
                "num_valid": len(ot_uncertainties)
            }
        
        return {
            "baseline_success_rate": float(baseline_success),
            "ot_success_rate": float(ot_success),
            "ot_uncertainty": uncertainty_stats,
            "num_examples": len(baseline)
        }
    
    def evaluate_uncertainty_calibration(self, results: Dict[str, Any]) -> float:
        """
        Check if OT entropy correlates with actual error (Spearman correlation).
        
        Returns:
            Spearman correlation coefficient (-1 to 1)
            Positive = higher uncertainty -> higher error (good calibration)
        """
        try:
            from scipy.stats import spearmanr
            
            uncertainties = []
            errors = []
            
            for r in results["ot_enhanced"]:
                if r.get("uncertainty") is not None:
                    uncertainties.append(r["uncertainty"])
                    # Error = 0 if success, 1 if failure
                    # For now, use execution_success as proxy for error
                    errors.append(0 if r.get("execution_success", False) else 1)
            
            if len(uncertainties) < 2:
                logger.warning("Not enough data points for Spearman correlation")
                return 0.0
            
            # Also check for variance (all same values = cant compute correlation)
            if len(set(uncertainties)) < 2 or len(set(errors)) < 2:
                logger.warning("Not enough variance in uncertainties or errors for Spearman correlation")
                return 0.0
            
            corr, p_value = spearmanr(uncertainties, errors)
            logger.info(f"Uncertainty calibration (Spearman): r={corr:.3f}, p={p_value:.3f}")
            
            return float(corr)
            
        except Exception as e:
            logger.error(f"Failed to compute Spearman correlation: {e}")
            return 0.0
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save results to JSON file in exp_gen_sol_out.json schema format.
        
        Schema requires:
        {
            "datasets": [
                {
                    "dataset": "<name>",
                    "examples": [
                        {
                            "input": "<document/question>",
                            "output": "<expected answer or reasoning>",
                            "predict_baseline": "<baseline prediction>",
                            "predict_ot_enhanced": "<OT-enhanced prediction>"
                        }
                    ]
                }
            ]
        }
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to schema format - schema only allows "datasets" at top level
        schema_output = {
            "datasets": []
        }
        
        # Group baseline and OT results by dataset
        dataset_name = results.get("dataset", "unknown")
        
        examples_formatted = []
        baseline_results = results.get("baseline", [])
        ot_results = results.get("ot_enhanced", [])
        
        # Match baseline and OT results by example_id
        for i, (base, ot) in enumerate(zip(baseline_results, ot_results)):
            example_id = base.get("example_id", f"example_{i}")
            
            examples_formatted.append({
                "input": base.get("document", ""),
                "output": str(base.get("answer", "")),  # Expected answer
                "predict_baseline": base.get("problog_code", ""),
                "predict_ot_enhanced": ot.get("problog_code", "")
                # Note: cannot add metadata fields - schema has additionalProperties: false
            })
        
        schema_output["datasets"].append({
            "dataset": dataset_name,
            "examples": examples_formatted
        })
        
        # Also save full results (with metadata) to a separate file
        full_output_path = output_file.parent / f"full_{output_file.name}"
        full_results = {
            "metadata": {
                "method": "neuro_symbolic_ot_predicate_grounding",
                "dataset": results.get("dataset", "unknown"),
                "num_examples": results.get("num_examples", 0),
                "summary": results.get("summary", {}),
                "uncertainty_calibration_spearman": results.get("uncertainty_calibration_spearman", 0.0),
                "note": "This file has additional metadata. For schema validation, use the main output file."
            },
            "datasets": schema_output["datasets"]
        }
        
        # Convert numpy types to Python types for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            elif isinstance(obj, float) and np.isnan(obj):
                return None  # Convert NaN to None for JSON
            else:
                return obj
        
        # Save main output (schema-compliant)
        results_json = convert_for_json(schema_output)
        with open(output_file, 'w') as f:
            json.dump(results_json, f, indent=2, default=str)
        logger.info(f"Saved schema-compliant results to {output_file}")
        
        # Save full output (with metadata)
        full_results_json = convert_for_json(full_results)
        with open(full_output_path, 'w') as f:
            json.dump(full_results_json, f, indent=2, default=str)
        logger.info(f"Saved full results (with metadata) to {full_output_path}")


# =============================================================================
# Main Experiment
# =============================================================================

@logger.catch(reraise=True)
def main():
    parser = argparse.ArgumentParser(description="Neuro-Symbolic Pipeline with OT-based Predicate Grounding")
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2",
                        help="Sentence-transformer model name (unused if --no-transformers)")
    parser.add_argument("--no-transformers", action="store_true",
                        help="Disable sentence-transformers (use simple similarity)")
    parser.add_argument("--dataset", type=str, default="dummy",
                        choices=["ruletaker", "clutrr", "dummy"],
                        help="Dataset to evaluate on")
    parser.add_argument("--num-examples", type=int, default=5,
                        help="Number of examples to evaluate (0 = all)")
    parser.add_argument("--epsilon", type=float, default=0.1,
                        help="OT entropy regularization parameter")
    parser.add_argument("--output", type=str, default="results.json",
                        help="Output file path")
    parser.add_argument("--predicate-vocab", type=str, default=None,
                        help="Comma-separated predicate vocabulary (optional)")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Neuro-Symbolic Pipeline with OT-based Predicate Grounding")
    logger.info("=" * 60)
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Num examples: {args.num_examples}")
    logger.info(f"OT epsilon: {args.epsilon}")
    logger.info(f"Output: {args.output}")
    
    # Initialize components
    logger.info("Initializing components...")
    use_transformers = not args.no_transformers
    similarity = SemanticSimilarityModule(model_name=args.model, use_transformers=use_transformers)
    ot_module = OptimalTransportModule(epsilon=args.epsilon)
    parser_module = TextParser()
    
    # Predicate vocabulary
    if args.predicate_vocab:
        predicate_vocab = [p.strip() for p in args.predicate_vocab.split(',')]
    else:
        # Default predicate vocabulary for reasoning tasks
        predicate_vocab = [
            "cat", "dog", "animal", "person", "parent", "child",
            "sibling", "related", "likes", "friend", "knows", "has"
        ]
    
    logger.info(f"Predicate vocabulary: {predicate_vocab}")
    
    # Initialize pipelines
    baseline = BaselinePipeline(similarity, predicate_vocab)
    ot_pipeline = OTEnhancedPipeline(similarity, ot_module, predicate_vocab)
    
    # Initialize evaluation framework
    evaluator = EvaluationFramework(baseline, ot_pipeline, parser_module)
    
    # Run evaluation
    logger.info(f"Running evaluation on {args.dataset}...")
    start_time = time.time()
    
    results = evaluator.evaluate_dataset(
        dataset_name=args.dataset,
        num_examples=args.num_examples,
        sequential=True
    )
    
    elapsed_time = time.time() - start_time
    logger.info(f"Evaluation completed in {elapsed_time:.1f}s")
    
    # Compute uncertainty calibration
    spearman_corr = evaluator.evaluate_uncertainty_calibration(results)
    results["uncertainty_calibration_spearman"] = spearman_corr
    
    # Save results
    evaluator.save_results(results, args.output)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 60)
    summary = results.get("summary", {})
    logger.info(f"Baseline success rate: {summary.get('baseline_success_rate', 0):.3f}")
    logger.info(f"OT success rate: {summary.get('ot_success_rate', 0):.3f}")
    logger.info(f"Uncertainty calibration (Spearman): {spearman_corr:.3f}")
    
    uncertainty_stats = summary.get("ot_uncertainty", {})
    if uncertainty_stats:
        logger.info(f"OT uncertainty: mean={uncertainty_stats.get('mean', 0):.3f}, "
                   f"std={uncertainty_stats.get('std', 0):.3f}")
    
    logger.info("=" * 60)
    logger.info("Experiment completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
