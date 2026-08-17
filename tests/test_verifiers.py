"""Regression tests for the supplementary verification methods."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFIERS = (
    ROOT / "software" / "verify_exact_symbolics.py",
    ROOT / "software" / "verify_independent_coefficients.py",
)
LEAN_ROOT = ROOT / "lean"


class VerifierTests(unittest.TestCase):
    def run_verifier(
        self,
        verifier: Path,
        *,
        optimized: bool,
        self_test_failure: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-B"]
        if optimized:
            command.append("-O")
        command.append(str(verifier))
        if self_test_failure:
            command.append("--self-test-failure")
        return subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_both_methods_pass_normally_and_when_optimized(self) -> None:
        for verifier in VERIFIERS:
            for optimized in (False, True):
                with self.subTest(
                    verifier=verifier.name,
                    optimized=optimized,
                ):
                    result = self.run_verifier(
                        verifier,
                        optimized=optimized,
                    )
                    self.assertEqual(
                        result.returncode,
                        0,
                        result.stdout + result.stderr,
                    )
                    self.assertIn(
                        "ALL DECLARED ALGEBRAIC CHECKS PASSED",
                        result.stdout,
                    )

    def test_failure_paths_survive_python_optimization(self) -> None:
        for verifier in VERIFIERS:
            for optimized in (False, True):
                with self.subTest(
                    verifier=verifier.name,
                    optimized=optimized,
                ):
                    result = self.run_verifier(
                        verifier,
                        optimized=optimized,
                        self_test_failure=True,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("VERIFICATION FAILED", result.stderr)
                    self.assertNotIn(
                        "ALL DECLARED ALGEBRAIC CHECKS PASSED",
                        result.stdout,
                    )

    def test_verifier_sources_contain_no_assert_statements(self) -> None:
        for verifier in VERIFIERS:
            tree = ast.parse(
                verifier.read_text(encoding="utf-8"),
                filename=str(verifier),
            )
            assert_nodes = [
                node for node in ast.walk(tree) if isinstance(node, ast.Assert)
            ]
            self.assertEqual(assert_nodes, [], verifier.name)

    def test_independent_method_does_not_import_sympy(self) -> None:
        source = VERIFIERS[1].read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(VERIFIERS[1]))
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)
        self.assertNotIn("sympy", imported_modules)

    def test_lean_sources_have_no_incomplete_proof_placeholders(self) -> None:
        lean_sources = sorted(LEAN_ROOT.rglob("*.lean"))
        self.assertGreaterEqual(len(lean_sources), 2)
        forbidden = re.compile(r"\b(?:admit|axiom|sorry)\b")
        for source_path in lean_sources:
            source = source_path.read_text(encoding="utf-8")
            self.assertIsNone(
                forbidden.search(source),
                f"forbidden Lean placeholder in {source_path}",
            )

    def test_nanoda_covers_every_certificate_theorem(self) -> None:
        certificates = (
            LEAN_ROOT / "C4TwoBandInertia" / "Certificates.lean"
        ).read_text(encoding="utf-8")
        nanoda_script = (LEAN_ROOT / "run_nanoda.sh").read_text(
            encoding="utf-8"
        )
        declared = set(
            re.findall(r"^theorem ([A-Za-z0-9_]+)", certificates, re.M)
        )
        selected = set(
            re.findall(
                r"^  C4TwoBandInertia\.([A-Za-z0-9_]+)",
                nanoda_script,
                re.M,
            )
        )
        self.assertEqual(selected, declared)

    def test_lean_and_mathlib_versions_are_pinned(self) -> None:
        toolchain = (LEAN_ROOT / "lean-toolchain").read_text(
            encoding="utf-8"
        )
        with (LEAN_ROOT / "lakefile.toml").open("rb") as lakefile:
            lake_config = tomllib.load(lakefile)
        self.assertEqual(toolchain.strip(), "leanprover/lean4:v4.33.0")
        self.assertEqual(lake_config["defaultTargets"], ["C4TwoBandInertia"])
        self.assertEqual(
            lake_config["lean_lib"], [{"name": "C4TwoBandInertia"}]
        )
        self.assertEqual(
            lake_config["require"],
            [
                {
                    "name": "mathlib",
                    "scope": "leanprover-community",
                    "rev": "v4.33.0",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
