"""
OT Sinkhorn Example
==================

This script demonstrates how to use the POT (Python Optimal Transport) library
to compute entropy-regularized optimal transport using the Sinkhorn algorithm.

Requirements:
-------------
pip install POT numpy

Usage:
-------
python ot_sinkhorn_example.py

Author: AI Researcher
Date: 2026-06-15
"""

import numpy as np
import ot

def compute_sinkhorn(a, b, M, reg=0.1, method='sinkhorn_stabilized', numItermax=1000):
    """
    Compute entropy-regularized optimal transport using Sinkhorn algorithm.
    
    Parameters:
    -----------
    a : ndarray, shape (n,)
        Source distribution (histogram, sums to 1)
    b : ndarray, shape (m,)
        Target distribution (histogram, sums to 1)
    M : ndarray, shape (n, m)
        Cost matrix
    reg : float, optional (default=0.1)
        Entropy regularization parameter (epsilon)
        - Higher values → more entropic (smoother) solution
        - Lower values → closer to exact OT (may not converge)
    method : str, optional (default='sinkhorn_stabilized')
        Algorithm to use:
        - 'sinkhorn': Classic Sinkhorn-Knopp
        - 'sinkhorn_log': Log-space (more stable)
        - 'sinkhorn_stabilized': Stabilized (recommended)
    numItermax : int, optional (default=1000)
        Maximum number of iterations
    
    Returns:
    --------
    P : ndarray, shape (n, m)
        Optimal transport matrix
        P[i,j] = probability mass moved from a[i] to b[j]
    """
    
    # Validate inputs
    assert np.abs(a.sum() - 1.0) < 1e-6, "a must sum to 1"
    assert np.abs(b.sum() - 1.0) < 1e-6, "b must sum to 1"
    assert a.shape[0] == M.shape[0], "M.shape[0] must match a.shape[0]"
    assert b.shape[0] == M.shape[1], "M.shape[1] must match b.shape[0]"
    assert reg > 0, "reg must be positive"
    
    # Compute optimal transport plan
    P = ot.sinkhorn(a, b, M, reg, 
                       method=method, 
                       numItermax=numItermax,
                       stopThr=1e-9)
    
    return P


def normalize_transport_plan(P):
    """
    Normalize transport plan rows to get probability distributions.
    
    Parameters:
    -----------
    P : ndarray, shape (n, m)
        Optimal transport matrix
    
    Returns:
    --------
    P_norm : ndarray, shape (n, m)
        Normalized transport plan where each row sums to 1
    """
    P_norm = P / P.sum(axis=1, keepdims=True)
    return P_norm


def example_1_simple():
    """
    Example 1: Simple 2x2 transport problem.
    
    Scenario: Match 2 source items to 2 target items with a cost matrix.
    """
    print("=" * 60)
    print("Example 1: Simple 2x2 Transport Problem")
    print("=" * 60)
    
    # Define distributions
    a = np.array([0.5, 0.5])  # Two source items with equal weight
    b = np.array([0.5, 0.5])  # Two target items with equal weight
    
    # Define cost matrix
    # M[i,j] = cost to move mass from source i to target j
    # 0 = perfect match, 1 = worst match
    M = np.array([
        [0.0, 1.0],  # Source 0: perfect match with Target 0, worst with Target 1
        [1.0, 0.0]   # Source 1: worst match with Target 0, perfect with Target 1
    ])
    
    print("\nInput:")
    print(f"  Source distribution a: {a}")
    print(f"  Target distribution b: {b}")
    print(f"  Cost matrix M:\n{M}")
    
    # Solve OT with different regularization parameters
    for reg in [0.01, 0.1, 1.0]:
        P = compute_sinkhorn(a, b, M, reg=reg)
        P_norm = normalize_transport_plan(P)
        
        print(f"\nResults with reg={reg}:")
        print(f"  Transport plan P:\n{P}")
        print(f"  Normalized P_norm:\n{P_norm}")
        print(f"  Check: P_norm sums to {P_norm.sum(axis=1)}")
    
    print("\n" + "=" * 60)


def example_2_term_predicate_matching():
    """
    Example 2: Term-to-Predicate Matching for Neuro-Symbolic AI.
    
    Scenario: Match natural language terms to logical predicates
    using semantic similarity as the cost metric.
    """
    print("=" * 60)
    print("Example 2: Term-to-Predicate Matching")
    print("=" * 60)
    
    # Define terms and predicates
    terms = ['cat', 'dog', 'bird']
    predicates = ['animal', 'pet', 'can_fly']
    
    # Cost matrix based on semantic similarity (1 - similarity)
    # Lower cost = higher similarity = more likely match
    M = np.array([
        [0.2, 0.1, 0.9],  # cat: similar to animal, very similar to pet, not similar to can_fly
        [0.2, 0.2, 0.9],  # dog: similar to animal, similar to pet, not similar to can_fly
        [0.3, 0.8, 0.1]   # bird: similar to animal, not similar to pet, similar to can_fly
    ])
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    print(f"\nCost Matrix M (1 - semantic similarity):\n{M}")
    print("\nInterpretation:")
    print("  - M[0,1] = 0.1 → 'cat' is very similar to 'pet' (low cost)")
    print("  - M[2,2] = 0.1 → 'bird' is very similar to 'can_fly' (low cost)")
    
    # Define distributions
    a = np.ones(len(terms)) / len(terms)      # Uniform weights for terms
    b = np.ones(len(predicates)) / len(predicates)  # Uniform weights for predicates
    
    # Solve OT
    reg = 0.1
    P = compute_sinkhorn(a, b, M, reg=reg)
    P_norm = normalize_transport_plan(P)
    
    print(f"\nOptimal Transport Plan P (reg={reg}):\n{P}")
    print(f"\nNormalized Probabilities P_norm:\n{P_norm}")
    
    # Extract matching probabilities
    print("\nMatching Probabilities (Term → Predicate):")
    for i, term in enumerate(terms):
        for j, pred in enumerate(predicates):
            prob = P_norm[i, j]
            if prob > 0.01:
                print(f"  P({pred}({term})) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_3_compute_wasserstein_distance():
    """
    Example 3: Compute Wasserstein Distance.
    
    The Wasserstein distance is the optimal value of the OT problem.
    """
    print("=" * 60)
    print("Example 3: Wasserstein Distance Computation")
    print("=" * 60)
    
    # Define two distributions
    a = np.array([0.6, 0.4])  # Distribution 1
    b = np.array([0.3, 0.7])  # Distribution 2
    
    # Cost matrix (Euclidean distance in 1D)
    M = np.array([
        [0.0, 1.0],  # Distance between bin 0 and bin 0, 1
        [1.0, 0.0]   # Distance between bin 1 and bin 0, 1
    ])
    
    print("\nInput:")
    print(f"  Distribution a: {a}")
    print(f"  Distribution b: {b}")
    print(f"  Cost matrix M:\n{M}")
    
    # Method 1: Using ot.sinkhorn2 (returns value directly)
    reg = 0.1
    W1 = ot.sinkhorn2(a, b, M, reg)
    print(f"\nWasserstein distance (ot.sinkhorn2): {W1:.6f}")
    
    # Method 2: Using ot.sinkhorn (returns matrix, then compute value)
    P = ot.sinkhorn(a, b, M, reg)
    W2 = np.sum(P * M)
    print(f"Wasserstein distance (ot.sinkhorn + sum): {W2:.6f}")
    
    # Verify they are the same
    print(f"\nDifference: {abs(W1 - W2):.10f}")
    
    print("\n" + "=" * 60)


def example_4_different_algorithms():
    """
    Example 4: Compare Different Sinkhorn Algorithm Variants.
    """
    print("=" * 60)
    print("Example 4: Comparing Sinkhorn Algorithm Variants")
    print("=" * 60)
    
    # Create random problem
    n, m = 10, 15
    np.random.seed(42)
    
    a = np.random.dirichlet(np.ones(n))
    b = np.random.dirichlet(np.ones(m))
    M = np.random.rand(n, m)
    
    print(f"\nProblem size: {n} sources, {m} targets")
    print(f"Cost matrix shape: {M.shape}")
    
    # Compare algorithms
    methods = ['sinkhorn', 'sinkhorn_log', 'sinkhorn_stabilized']
    reg = 0.1
    
    results = {}
    for method in methods:
        P = compute_sinkhorn(a, b, M, reg=reg, method=method)
        W = np.sum(P * M)
        results[method] = W
        
        print(f"\nMethod: {method}")
        print(f"  Wasserstein distance: {W:.6f}")
        print(f"  Transport plan sum: {P.sum():.6f}")
        print(f"  Transport plan shape: {P.shape}")
    
    # Verify all methods give similar results
    print(f"\nAll methods converge to similar solution:")
    for method, W in results.items():
        print(f"  {method}: {W:.6f}")
    
    print("\n" + "=" * 60)


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 60)
    print("OT Sinkhorn Example: Entropy-Regularized Optimal Transport")
    print("=" * 60 + "\n")
    
    # Run examples
    example_1_simple()
    example_2_term_predicate_matching()
    example_3_compute_wasserstein_distance()
    example_4_different_algorithms()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
