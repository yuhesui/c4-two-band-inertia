# Verification supplement for cubic children and two-band inertia

Exact verification artifacts accompanying the manuscript **Cubic children and two-band inertia in near-extremal $C_4$-free graphs**.

## Authors

- Yuhe Sui — Nanyang Technological University — [ORCID 0009-0002-7456-0804](https://orcid.org/0009-0002-7456-0804) — [@yuhesui](https://github.com/yuhesui)
- Xiaotong Li — Dalian University of Technology — [ORCID 0009-0005-2622-8120](https://orcid.org/0009-0005-2622-8120) — [@ClzHhhhhhh](https://github.com/ClzHhhhhhh)

The repository contains the [manuscript abstract](ABSTRACT.md), two independent Python verification methods, a Lean formalization of the algebraic certificate layer, regression tests, and publication metadata. It intentionally does not contain the full manuscript.

## Scope

The package checks the algebraic identities and analytic inequality certificates used by the manuscript:

- beta--Hermite coefficient, integral, derivative, endpoint, and remainder identities;
- sixth-, seventh-, and eighth-moment expansions and the degree-seven cancellation;
- the $s\ge1296$ square-defect threshold inequalities;
- exceptional-family asymptotic coefficients and propagated error scaling;
- the explicit quartic-family interval exclusion for $t\ge4$;
- the rational-child square obstruction for every $a\ge10$;
- diagnostic interval and congruence values at $s=28,30$.

It does not formalize the graph-theoretic local counting, structural cycle arguments, Capelli theorem, or Ramsey translation. See [VERIFICATION_README.md](VERIFICATION_README.md) for the exact proof boundary.

## Quick start

```bash
python -m pip install --require-hashes -r requirements.txt
python software/run_all.py
python -m unittest discover -s tests -v
cd lean
lake exe cache get
lake build
```

The successful final lines are:

```text
SYMPY VERIFIER: ALL DECLARED ALGEBRAIC CHECKS PASSED
INDEPENDENT VERIFIER: ALL DECLARED ALGEBRAIC CHECKS PASSED
TWO-METHOD VERIFICATION PASS: SymPy and independent exact checks agree
```

The POSIX wrapper `software/run_all.sh` is retained for convenience. Set `PYTHON` if `python3` is not the desired interpreter.

## Independent methods

1. `software/verify_exact_symbolics.py` uses SymPy for symbolic expansion, differentiation, series, and polynomial positivity.
2. `software/verify_independent_coefficients.py` uses only the Python standard library, with its own rational polynomial arithmetic and Decimal diagnostics. It does not import SymPy or the first verifier.

Both Python methods use explicit runtime checks that remain active under `python -O`. The regression suite also triggers deliberate failures in normal and optimized modes.

3. `lean/C4TwoBandInertia/Certificates.lean` formalizes the principal exact polynomial identities and universal inequalities in Lean. GitHub Actions builds it, invokes Lean's checker, and invokes the independent Rust-based `nanoda` type checker with incomplete `sorry` proofs forbidden.

## Contents

- `ABSTRACT.md` — abstract of the associated manuscript
- `software/verify_exact_symbolics.py` — SymPy verification method
- `software/verify_independent_coefficients.py` — independent standard-library method
- `software/run_all.py` — cross-platform two-method runner
- `lean/` — pinned Lean 4 and Mathlib proof-assistant project
- `tests/test_verifiers.py` — optimized-mode and independence regression tests
- `certificates/verification_certificates.json` — structured expected values and scope limits
- `VERIFICATION_README.md` — verification coverage and trust boundary
- `requirements.txt` — pinned runtime dependencies

## Archival release

Follow [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Reserve the archival DOI before the final tag, add it to the citation metadata and manuscript, regenerate `SHA256SUMS`, and archive the exact tagged commit.

## License

Code and associated documentation in this repository are released under the MIT License.
