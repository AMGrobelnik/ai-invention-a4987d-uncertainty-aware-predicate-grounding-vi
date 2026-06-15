"""
ProbLog Dynamic Example
====================

This script demonstrates how to use ProbLog programmatically from Python,
including dynamic probability assignment from OT output.

Requirements:
-------------
pip install problog

Usage:
-------
python problog_dynamic_example.py

Author: AI Researcher
Date: 2026-06-15
"""

from problog.program import PrologString
from problog import get_evaluatable
from problog.engine import DefaultEngine
from problog.logic import Term
import numpy as np
import ot


def example_1_basic_problog():
    """
    Example 1: Basic ProbLog Usage.
    
    Demonstrates creating a ProbLog program as a string and evaluating it.
    """
    print("=" * 60)
    print("Example 1: Basic ProbLog Usage")
    print("=" * 60)
    
    # Create ProbLog program as string
    program = """
    0.7::cat(tom).
    0.3::dog(tom).
    animal(X) :- cat(X).
    animal(X) :- dog(X).
    query(animal(tom)).
    """
    
    print("\nProbLog Program:")
    print(program)
    
    # Parse and evaluate
    pl = PrologString(program)
    result = get_evaluatable().create_from(pl).evaluate()
    
    print("Result:")
    for query, prob in result.items():
        print(f"  P({query}) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_2_dynamic_probabilities():
    """
    Example 2: Dynamic Probability Assignment from OT Output.
    
    Demonstrates generating a ProbLog program with probabilities
    derived from optimal transport.
    """
    print("=" * 60)
    print("Example 2: Dynamic Probability Assignment from OT")
    print("=" * 60)
    
    # Step 1: Define terms and predicates
    terms = ['cat', 'dog', 'bird']
    predicates = ['animal', 'pet', 'can_fly']
    
    print("\nTerms:", terms)
    print("Predicates:", predicates)
    
    # Step 2: Compute cost matrix (simulated with embeddings)
    # In practice, this would use sentence-transformers
    M = np.array([
        [0.2, 0.1, 0.9],  # cat: similar to animal, pet, not fly
        [0.2, 0.2, 0.9],  # dog: similar to animal, pet, not fly
        [0.3, 0.8, 0.1]   # bird: similar to animal, not pet, can fly
    ])
    
    print("\nCost Matrix M (1 - cosine_similarity):")
    print(M)
    
    # Step 3: Define distributions
    a = np.ones(len(terms)) / len(terms)      # Uniform weights for terms
    b = np.ones(len(predicates)) / len(predicates)  # Uniform weights for predicates
    
    # Step 4: Solve OT with entropy regularization
    reg = 0.1
    P = ot.sinkhorn(a, b, M, reg)  # Transport plan matrix
    
    print(f"\nTransport Plan P (reg={reg}):")
    print(P)
    
    # Step 5: Normalize to get probabilities
    P_norm = P / P.sum(axis=1, keepdims=True)
    
    print(f"\nNormalized Probabilities P_norm (rows sum to 1):")
    print(P_norm)
    
    # Step 6: Generate ProbLog program
    program_lines = []
    ot_probabilities = {}
    
    for i, term in enumerate(terms):
        for j, pred in enumerate(predicates):
            prob = P_norm[i, j]
            ot_probabilities[(term, pred)] = prob
            if prob > 0.01:  # Only include significant probabilities
                program_lines.append(f"{prob:.4f}::{pred}({term}).")
    
    # Add rules
    program_lines.append("flying(X) :- can_fly(X).")
    program_lines.append("query(flying(bird)).")
    
    program_str = "\n".join(program_lines)
    
    print("\nGenerated ProbLog Program:")
    print(program_str)
    
    # Step 7: Evaluate
    pl = PrologString(program_str)
    result = get_evaluatable().create_from(pl).evaluate()
    
    print("\nResult:")
    for query, prob in result.items():
        print(f"  P({query}) = {prob:.4f}")
    
    print("\nOT Probabilities Dictionary:")
    for (term, pred), prob in ot_probabilities.items():
        print(f"  P({pred}({term})) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_3_problog_with_evidence():
    """
    Example 3: Adding Evidence Programmatically.
    
    Demonstrates setting evidence using the ProbLog engine.
    """
    print("=" * 60)
    print("Example 3: Adding Evidence Programmatically")
    print("=" * 60)
    
    # Create ProbLog program
    program = """
    0.4::heads(C); 0.6::tails(C) :- coin(C).
    coin(c1). coin(c2).
    win :- heads(C).
    query(win).
    """
    
    print("\nProbLog Program:")
    print(program)
    
    # Parse
    pl = PrologString(program)
    engine = DefaultEngine()
    db = engine.prepare(pl)
    
    # Evaluate without evidence
    lf = engine.ground_all(db)
    result_no_evidence = get_evaluatable().create_from(lf).evaluate()
    
    print("Result WITHOUT evidence:")
    for query, prob in result_no_evidence.items():
        print(f"  P({query}) = {prob:.4f}")
    
    # Add evidence: heads(c1) is true
    evidence_term = Term('heads', Term('c1'))
    lf = engine.ground_all(db, evidence=[(evidence_term, True)])
    result_with_evidence = get_evaluatable().create_from(lf).evaluate()
    
    print("\nResult WITH evidence(heads(c1)=True):")
    for query, prob in result_with_evidence.items():
        print(f"  P({query}) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_4_step_by_step_pipeline():
    """
    Example 4: Step-by-Step ProbLog Pipeline.
    
    Demonstrates the internal steps of ProbLog compilation.
    """
    print("=" * 60)
    print("Example 4: Step-by-Step ProbLog Pipeline")
    print("=" * 60)
    
    from problog.formula import LogicFormula, LogicDAG
    from problog.ddnnf_formula import DDNNF
    from problog.cnf_formula import CNF
    
    # Step 1: Create program
    program = """
    0.4::heads(C); 0.6::tails(C) :- coin(C).
    coin(c1). coin(c2).
    win :- heads(C).
    query(win).
    """
    
    print("\nStep 1: Create ProbLog Program")
    print(program)
    
    # Step 2: Parse
    pl = PrologString(program)
    print("Step 2: Parse with PrologString ✓")
    
    # Step 3: Ground the program
    lf = LogicFormula.create_from(pl)
    print("Step 3: Ground program → LogicFormula ✓")
    print(f"  Ground program has {len(lf)} nodes")
    
    # Step 4: Break cycles
    dag = LogicDAG.create_from(lf)
    print("Step 4: Break cycles → LogicDAG ✓")
    
    # Step 5: Convert to CNF
    cnf = CNF.create_from(dag)
    print("Step 5: Convert to CNF ✓")
    
    # Step 6: Compile to d-DNNF
    ddnnf = DDNNF.create_from(cnf)
    print("Step 6: Compile to d-DNNF ✓")
    
    # Step 7: Evaluate
    result = ddnnf.evaluate()
    print("Step 7: Evaluate ✓")
    
    print("\nResult:")
    for query, prob in result.items():
        print(f"  P({query}) = {prob:.4f}")
    
    print("\n" + "=" * 60)


def example_5_annotated_disjunction():
    """
    Example 5: Annotated Disjunction for Mutually Exclusive Events.
    
    Demonstrates using annotated disjunction for probabilistic clauses.
    """
    print("=" * 60)
    print("Example 5: Annotated Disjunction")
    print("=" * 60)
    
    # Using annotated disjunction (mutually exclusive events)
    program = """
    0.4::heads(C); 0.6::tails(C) :- coin(C).
    coin(c1).
    win :- heads(c1).
    query(heads(c1)).
    query(tails(c1)).
    query(win).
    """
    
    print("\nProbLog Program (Annotated Disjunction):")
    print(program)
    
    print("\nInterpretation:")
    print("  - heads(c1) and tails(c1) are mutually exclusive")
    print("  - P(heads(c1)) = 0.4")
    print("  - P(tails(c1)) = 0.6")
    print("  - P(win) = P(heads(c1)) = 0.4")
    
    # Evaluate
    pl = PrologString(program)
    result = get_evaluatable().create_from(pl).evaluate()
    
    print("\nResult:")
    for query, prob in result.items():
        print(f"  P({query}) = {prob:.4f}")
    
    # Verify mutual exclusivity
    p_heads = result.get('heads(c1)', 0)
    p_tails = result.get('tails(c1)', 0)
    print(f"\nVerification:")
    print(f"  P(heads(c1)) + P(tails(c1)) = {p_heads + p_tails:.4f} (should be 1.0)")
    
    print("\n" + "=" * 60)


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 60)
    print("ProbLog Dynamic Example: Programmatic Control of ProbLog")
    print("=" * 60 + "\n")
    
    # Run examples
    example_1_basic_problog()
    example_2_dynamic_probabilities()
    example_3_problog_with_evidence()
    example_4_step_by_step_pipeline()
    example_5_annotated_disjunction()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
