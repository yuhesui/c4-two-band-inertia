# Verification coverage and proof boundary

## Purpose

This supplementary package independently checks the manuscript's exact algebraic calculations. It includes two Python implementations and a Lean proof-assistant formalization of the principal algebraic certificates. It does not claim to machine-formalize every combinatorial statement in the manuscript.

The package includes only the [manuscript abstract](ABSTRACT.md), not the full paper.

## Run

From the package root:

```bash
python -m pip install --require-hashes -r requirements.txt
python software/run_all.py
python -m unittest discover -s tests -v
cd lean
lake exe cache get
lake build
```

The release workflow runs the Python checks on Python 3.12 and 3.13. Runtime dependencies are pinned with wheel hashes to SymPy 1.14.0 and mpmath 1.3.0. It separately builds the Lean project with Lean and Mathlib 4.33.0.

## Three machine-verification methods

### Method A: symbolic derivation

`software/verify_exact_symbolics.py` uses SymPy to derive and compare exact expressions. It checks symbolic derivatives, integrals, expansions, series coefficients, and polynomial-positivity certificates.

### Method B: independent exact arithmetic

`software/verify_independent_coefficients.py` imports neither SymPy nor Method A. It implements separate:

- exact rational arithmetic with `fractions.Fraction`;
- univariate polynomial differentiation, evaluation, and translation;
- multivariate formal-polynomial addition and multiplication;
- positivity proofs using nonnegative coefficients after shifting the domain;
- high-precision `decimal.Decimal` diagnostics.

This implementation uses deterministic coefficient-by-coefficient polynomial equality rather than sampling.

### Method C: Lean proof assistant

`lean/C4TwoBandInertia/Certificates.lean` states and proves the principal certificate identities and universal inequalities over exact rational or integer types. `lake build` elaborates the proof terms and checks them with Lean's kernel. Release CI also runs Lean's checker and the independent Rust-based `nanoda` checker, with incomplete `sorry` proofs forbidden.

## Machine-verified coverage

| Claim group | Method A | Method B | Method C (Lean) |
|---|---|---|---|
| Beta--Hermite coefficient identity | exact for $r=0,\ldots,12$ | exact for $r=0,\ldots,20$ | degree five and seven forms |
| Taylor and integral polynomial forms | symbolic equality | rational coefficient equality | degree five and seven polynomial forms |
| Derivative, endpoint, and Hermite conditions | symbolic differentiation | independent polynomial differentiation | derivative coefficient identities |
| Exact scalar remainder derivative | symbolic identity | cleared-radical polynomial identity | not encoded |
| Degree-five and degree-seven constants | exact rationals | exact rationals | exact rational proofs |
| $M_6$, $M_7$, and $M_8$ expansions | symbolic polynomials | independent formal polynomials | exact polynomial proofs |
| Degree-seven signature cancellation | symbolic expression | cleared-denominator integer polynomial | cleared-denominator proof |
| Square-defect inequalities for $s\ge1296$ | shifted polynomial certificates | independently shifted coefficient certificates | universal shifted-polynomial proofs |
| Quartic-family exclusion for $t\ge4$ | shifted polynomial certificates | independently shifted coefficient certificates | universal shifted-polynomial proofs |
| Exceptional-family center, expansion, and error scale | symbolic identity and series | independent rational coefficient checks | listed coefficients and error constant |
| Rational-child obstruction for all $a\ge10$ | universal inequality certificate | independent universal inequality certificate | universal integer proof |
| Diagnostics at $s=28,30$ | SymPy algebraic evaluation | independent Decimal evaluation | not encoded |

The finite checks at $r\le12$ and $r\le20$ support the manuscript's all-orders identities; the manuscript's induction and analytic proof establish the universal statement.

## Runtime integrity tests

The regression suite verifies that:

- both methods pass in normal and `python -O` modes;
- a deliberate failure exits nonzero in both modes;
- neither verifier contains a Python `assert` statement;
- the independent method does not import SymPy;
- the Lean sources contain no `sorry`, `admit`, or custom `axiom` declarations;
- the Lean and Mathlib versions are pinned.

The certificate file contains only structured limits and expected numerical values. Both verifiers consume every top-level certificate section and reject missing or unexpected sections.

## Not machine-formalized

The programs do not encode:

- the local codegree-counting identity and forced regularity;
- the odd local obstruction;
- the construction and decomposition $D=M\mathbin{\dot\cup}F$;
- commutation of $A$ and $D$ from the graph construction;
- constancy of the activity label on each $F$-cycle;
- the neighborhood matching theorem;
- the combinatorial proof of $5n\le\lambda\le17n$;
- Capelli's composition theorem and its factorwise application;
- the Ramsey translation.

Those statements have conventional proofs in the associated manuscript. Consequently, this package verifies every declared supplementary calculation through two independent Python implementations and formalizes its principal algebraic certificates in Lean, but it is not a machine-checked proof of the complete paper. An end-to-end mechanical proof would additionally require formalizing the graph-theoretic and analytic arguments listed above.

## Trust boundary

The verification depends on:

1. human review of the graph-theoretic and analytic proof steps listed above;
2. two independent Python implementations for the exact supplementary calculations;
3. a Lean proof term checked by Lean and, in release CI, independently by `nanoda`;
4. the Python runtime and, for Method A only, SymPy;
5. no hidden data, SAT solver, numerical linear program, or floating-point theorem step.

Decimal intervals are diagnostic only. All load-bearing comparisons use integer, rational, symbolic, or certified polynomial arithmetic.
