#!/usr/bin/env python3
"""Run both independent verification methods with the current interpreter."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERIFIERS = (
    ROOT / "software" / "verify_exact_symbolics.py",
    ROOT / "software" / "verify_independent_coefficients.py",
)


def main() -> None:
    for verifier in VERIFIERS:
        subprocess.run(
            [sys.executable, "-B", str(verifier)],
            cwd=ROOT,
            check=True,
        )
    print("TWO-METHOD VERIFICATION PASS: SymPy and independent exact checks agree")


if __name__ == "__main__":
    main()
