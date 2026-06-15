"""
Cost Matrix Embeddings Example
=============================

This script demonstrates how to compute the cost matrix for optimal transport
using sentence embeddings and semantic similarity.

Requirements:
-------------
pip install sentence-transformers scikit-learn numpy

Usage:
-------
python cost_matrix_embeddings.py

Author: AI Researcher
Date: 2026-06-15
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_cost_matrix_embeddings(terms, predicates, model_name='all-MiniLM-L6-v2'):
    """
    Compute cost matrix using sentence embeddings and cosine similarity.
    
    Parameters:
    -----------
    terms : list of str
        List of terms to match
    predicates : list of str
        List of predicates to match against
    model_name : str, optional (default='all-MiniLM-L6-v2')
        Sentence transformer model to use
        Options: 'all-MiniLM-L6-v2' (fast), 'all-mpnet-base-v2' (accurate)
    
    Returns:
    --------
    cost_matrix : ndarray, shape (len(terms), len(predicates))
        Cost matrix where cost[i,j] = 1 - cosine_similarity(term[i], predicate[j])
    term_embeddings : ndarray
        Embeddings for terms
    predicate_embeddings : ndarray
        Embeddings for predicates
    """
    
    print(f"\nLoading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"\nEncoding {len(terms)} terms...")
    term_embeddings = model.encode(terms)
    
    print(f"Encoding {len(predicates)} predicates...")
    predicate_embeddings = model.encode(predicates)
    
    print("\nComputing cosine similarity...")
    similarity = cosine_similarity(term_embeddings, predicate_embeddings)
    
    print("Computing cost matrix (1 - similarity)...")
    cost_matrix = 1 - similarity
    
    return cost_matrix, term_embeddings, predicate_embeddings


def compute_cost_matrix_euclidean(terms, predicates, model_name='all-MiniLM-L6-v2'):
    """
    Compute cost matrix using sentence embeddings and Euclidean distance.
    
    Parameters:
    -----------
    terms : list of str
        List of terms to match
    predicates : list of str
        List of predicates to match against
    model_name : str, optional (default='all-MiniLM-L6-v2')
        Sentence transformer model to use
    
    Returns:
    --------
    cost_matrix : ndarray, shape (len(terms), len(predicates))
        Cost matrix where cost[i,j] = euclidean_distance(term[i], predicate[j])
    """
    from sklearn.metrics.pairwise import euclidean_distances
    
    print(f"\nLoading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"\nEncoding {len(terms)} terms...")
    term_embeddings = model.encode(terms)
    
    print(f"Encoding {len(predicates)} predicates...")
    predicate_embeddings = model.encode(predicates)
    
    print("\nComputing Euclidean distance...")
    distances = euclidean_distances(term_embeddings, predicate_embeddings)
    
    # Normalize to [0, 1] range (optional)
    cost_matrix = distances / np.max(distances)
    
    return cost_matrix, term_embeddings, predicate_embeddings


def visualize_cost_matrix(cost_matrix, terms, predicates, title="Cost Matrix"):
    """
    Visualize cost matrix as a heatmap.
    
    Parameters:
    -----------
    cost_matrix : ndarray, shape (n, m)
        Cost matrix to visualize
    terms : list of str
        Row labels
    predicates : list of str
        Column labels
    title : str, optional
        Title for the heatmap
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(cost_matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(predicates)))
        ax.set_xticklabels(predicates, rotation=45, ha='right')
        ax.set_yticks(range(len(terms)))
        ax.set_yticklabels(terms)
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Cost (1 - cosine_similarity)')
        
        # Add text annotations
        for i in range(len(terms)):
            for j in range(len(predicates)):
                text = f"{cost_matrix[i,j]:.2f}"
                ax.text(j, i, text, ha='center', va='center', fontsize=8)
        
        ax.set_title(title)
        plt.tight_layout()
        plt.savefig('cost_matrix_heatmap.png', dpi=150)
        print(f"\nHeatmap saved to 'cost_matrix_heatmap.png'")
        plt.show()
        
    except ImportError:
        print("\nMatplotlib not installed. Cannot visualize heatmap.")
        print("Install with: pip install matplotlib")


def example_1_basic_usage():
    """
    Example 1: Basic usage of cost matrix computation.
    """
    print("=" * 60)
    print("Example 1: Basic Cost Matrix Computation")
    print("=" * 60)
    
    # Define terms and predicates
    terms = ['is a cat', 'is a dog', 'can fly']
    predicates = ['cat(X)', 'dog(X)', 'can_fly(X)']
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    
    # Compute cost matrix
    cost_matrix, _, _ = compute_cost_matrix_embeddings(terms, predicates)
    
    print("\nCost Matrix (1 - cosine_similarity):")
    print(cost_matrix)
    
    print("\nInterpretation:")
    print("  - Lower cost = higher similarity = more likely match")
    print(f"  - cat ↔ cat(X): cost = {cost_matrix[0,0]:.4f} (low = good match)")
    print(f"  - cat ↔ dog(X): cost = {cost_matrix[0,1]:.4f}")
    print(f"  - cat ↔ can_fly(X): cost = {cost_matrix[0,2]:.4f} (high = bad match)")
    
    print("\n" + "=" * 60)


def example_2_compare_metrics():
    """
    Example 2: Compare cosine similarity vs Euclidean distance.
    """
    print("=" * 60)
    print("Example 2: Cosine vs Euclidean Cost Matrix")
    print("=" * 60)
    
    # Define terms and predicates
    terms = ['is a cat', 'is a dog', 'bird can fly']
    predicates = ['cat(X)', 'dog(X)', 'can_fly(X)']
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    
    # Compute cost matrices using both metrics
    cost_cosine, _, _ = compute_cost_matrix_embeddings(terms, predicates)
    cost_euclidean, _, _ = compute_cost_matrix_euclidean(terms, predicates)
    
    print("\nCost Matrix (Cosine: 1 - similarity):")
    print(cost_cosine)
    
    print("\nCost Matrix (Euclidean distance, normalized):")
    print(cost_euclidean)
    
    print("\nComparison:")
    print("  - Cosine: Measures angle similarity (1 = identical, 0 = orthogonal)")
    print("  - Euclidean: Measures absolute distance in embedding space")
    print("  - Recommendation: Use cosine for semantic similarity tasks")
    
    print("\n" + "=" * 60)


def example_3_realistic_scenario():
    """
    Example 3: Realistic scenario with multiple terms and predicates.
    """
    print("=" * 60)
    print("Example 3: Realistic Term-Predicate Matching")
    print("=" * 60)
    
    # Define realistic terms extracted from text
    terms = [
        'has fur',
        'barks loudly',
        'flies in the sky',
        'likes to purr',
        'is a domestic animal'
    ]
    
    # Define predicates in FOL
    predicates = [
        'cat(X)',
        'dog(X)',
        'can_fly(X)',
        'makes_sound(X, Y)',
        'domestic_animal(X)'
    ]
    
    print(f"\nTerms (n={len(terms)}):")
    for i, t in enumerate(terms):
        print(f"  {i}: '{t}'")
    
    print(f"\nPredicates (m={len(predicates)}):")
    for j, p in enumerate(predicates):
        print(f"  {j}: '{p}'")
    
    # Compute cost matrix
    cost_matrix, _, _ = compute_cost_matrix_embeddings(terms, predicates)
    
    print("\nCost Matrix:")
    print("        " + "  ".join([f"P{j}" for j in range(len(predicates))]))
    for i in range(len(terms)):
        row = f"T{i}: "
        for j in range(len(predicates)):
            row += f"{cost_matrix[i,j]:6.3f}  "
        print(row)
    
    print("\nBest Matches (lowest cost per term):")
    for i in range(len(terms)):
        best_j = np.argmin(cost_matrix[i, :])
        print(f"  Term '{terms[i]}' → Predicate '{predicates[best_j]}' (cost={cost_matrix[i, best_j]:.4f})")
    
    # Visualize
    visualize_cost_matrix(cost_matrix, terms, predicates, title="Term-Predicate Matching Cost Matrix")
    
    print("\n" + "=" * 60)


def example_4_ot_integration():
    """
    Example 4: Integrate cost matrix with Optimal Transport (OT).
    """
    print("=" * 60)
    print("Example 4: Optimal Transport Integration")
    print("=" * 60)
    
    # Define terms and predicates
    terms = ['cat', 'dog', 'bird']
    predicates = ['animal', 'pet', 'can_fly']
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    
    # Compute cost matrix
    cost_matrix, _, _ = compute_cost_matrix_embeddings(terms, predicates)
    
    print("\nCost Matrix M:")
    print(cost_matrix)
    
    # Define distributions
    a = np.ones(len(terms)) / len(terms)      # Uniform weights for terms
    b = np.ones(len(predicates)) / len(predicates)  # Uniform weights for predicates
    
    print("\nDistributions:")
    print(f"  a (terms): {a}")
    print(f"  b (predicates): {b}")
    
    # Solve OT with entropy regularization
    import ot
    
    reg = 0.1  # Entropy regularization parameter
    print(f"\nSolving OT with Sinkhorn (reg={reg})...")
    
    P = ot.sinkhorn(a, b, cost_matrix, reg)
    
    print("\nTransport Plan P:")
    print(P)
    
    # Normalize to get probabilities
    P_norm = P / P.sum(axis=1, keepdims=True)
    
    print("\nNormalized Probabilities P_norm (rows sum to 1):")
    print(P_norm)
    
    print("\nMatching Probabilities (Term → Predicate):")
    for i in range(len(terms)):
        for j in range(len(predicates)):
            prob = P_norm[i, j]
            if prob > 0.01:
                print(f"  P({predicates[j]}({terms[i]})) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_5_different_models():
    """
    Example 5: Compare different sentence transformer models.
    """
    print("=" * 60)
    print("Example 5: Comparing Sentence Transformer Models")
    print("=" * 60)
    
    # Define terms and predicates
    terms = ['is a cat', 'can fly']
    predicates = ['cat(X)', 'can_fly(X)']
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    
    # Compare models
    models = [
        'all-MiniLM-L6-v2',    # Fast, lightweight (80MB)
        'all-mpnet-base-v2'     # Accurate, larger (420MB)
    ]
    
    for model_name in models:
        print(f"\nModel: {model_name}")
        print("-" * 40)
        
        cost_matrix, _, _ = compute_cost_matrix_embeddings(terms, predicates, model_name=model_name)
        
        print(f"Cost Matrix:")
        print(cost_matrix)
        
        # Check if 'cat' matches 'cat(X)' and 'can fly' matches 'can_fly(X)'
        print(f"\nMatching Quality:")
        print(f"  'is a cat' ↔ 'cat(X)': cost = {cost_matrix[0,0]:.4f} (lower = better)")
        print(f"  'can fly' ↔ 'can_fly(X)': cost = {cost_matrix[1,1]:.4f} (lower = better)")
    
    print("\nRecommendation:")
    print("  - Use all-MiniLM-L6-v2 for fast prototyping")
    print("  - Use all-mpnet-base-v2 for best quality")
    
    print("\n" + "=" * 60)


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 60)
    print("Cost Matrix Embeddings Example")
    print("=" * 60 + "\n")
    
    # Run examples
    example_1_basic_usage()
    example_2_compare_metrics()
    example_3_realistic_scenario()
    example_4_ot_integration()
    example_5_different_models()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
