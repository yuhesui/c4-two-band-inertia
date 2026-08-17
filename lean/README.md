# Lean verification

This Lake project is a proof-assistant formalization of the supplementary
algebraic certificate layer. It checks exact beta--Hermite identities, moment
expansions, shifted positivity certificates, exceptional coefficients, and the
universal rational-child square gap.

It does not formalize or assume the manuscript's graph-theoretic premises. The
precise boundary is documented in the repository's `VERIFICATION_README.md`.

## Build

Install Lean through `elan`, then run:

```bash
cd lean
lake exe cache get
lake build
```

The project pins Lean and Mathlib to version 4.33.0. The release CI additionally
checks the compiled declarations with Lean's checker and the independent
Rust-based `nanoda` type checker, with incomplete `sorry` proofs forbidden.
