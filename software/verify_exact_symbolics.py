#!/usr/bin/env python3
"""SymPy verification of the manuscript's exact algebraic calculations.

This is one of two independent implementations in the supplementary
package. It verifies symbolic polynomial identities, exact rational
constants, and sufficient polynomial-positivity certificates. It does not
formalize the graph-theoretic arguments in the associated manuscript.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / "certificates" / "verification_certificates.json"
SCHEMA = "c4-two-band-inertia-verification-v1"
SCOPE = (
    "Exact algebraic supplement; "
    "graph-theoretic arguments remain human-verified."
)


class VerificationError(RuntimeError):
    """Raised when an exact verification condition fails."""


def require(condition: object, label: str) -> None:
    """Enforce a verification condition even when Python optimization is on."""
    if condition is not True and condition != sp.true:
        raise VerificationError(label)


def require_zero(expression: sp.Expr, label: str) -> None:
    require(sp.simplify(expression) == 0, label)


def positive_on_ray(
    expression: sp.Expr,
    variable: sp.Symbol,
    start: int,
    label: str,
) -> None:
    """Certify positivity for variable >= start in a shifted monomial basis."""
    shifted = sp.Poly(
        sp.expand(expression.subs(variable, variable + start)),
        variable,
    )
    coefficients = shifted.all_coeffs()
    require(
        all(coefficient >= 0 for coefficient in coefficients),
        f"{label}: shifted coefficients",
    )
    require(shifted.eval(0) > 0, f"{label}: strict endpoint")


def central(j: int) -> sp.Rational:
    return sp.Rational(comb(2 * j, j), 4**j)


def parse_rationals(values: list[str]) -> list[sp.Rational]:
    return [sp.Rational(value) for value in values]


def load_certificate() -> dict[str, object]:
    certificate = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    require(
        set(certificate)
        == {
            "schema",
            "scope",
            "limits",
            "beta_hermite",
            "exceptional_coefficients",
            "diagnostics",
        },
        "certificate top-level fields",
    )
    require(certificate["schema"] == SCHEMA, "certificate schema")
    require(
        certificate["scope"] == SCOPE,
        "certificate scope",
    )
    return certificate


def check_beta_hermite(certificate: dict[str, object]) -> None:
    limits = certificate["limits"]
    require(
        set(limits)
        == {
            "sympy_max_r",
            "independent_max_r",
            "square_defect_min_s",
            "rational_child_min_a",
            "quartic_min_t",
        },
        "certificate limit fields",
    )
    max_r = int(limits["sympy_max_r"])
    require(max_r == 12, "SymPy hierarchy limit")

    x, s, u, t = sp.symbols("x s u t", positive=True)
    for r in range(max_r + 1):
        coefficients = [central(j) for j in range(r + 1)]
        polynomial = sum(
            (-1) ** j * coefficients[j] * u**j for j in range(r + 1)
        )
        h_taylor = sp.expand(
            (x / sp.sqrt(s)) * polynomial.subs(u, x**2 / s - 1)
        )

        c_r = sp.Rational(2 * r + 1) * central(r)
        h_integral = sp.expand(
            c_r
            * sum(
                (-1) ** ell
                * sp.binomial(r, ell)
                * (x / sp.sqrt(s)) ** (2 * ell + 1)
                / sp.Rational(2 * ell + 1)
                for ell in range(r + 1)
            )
        )
        require_zero(h_taylor - h_integral, f"Taylor/integral identity r={r}")

        for ell in range(r + 1):
            lhs = sum(
                central(j) * sp.binomial(j, ell)
                for j in range(ell, r + 1)
            )
            rhs = (
                sp.Rational(2 * r + 1, 2 * ell + 1)
                * central(r)
                * sp.binomial(r, ell)
            )
            require_zero(lhs - rhs, f"coefficient identity r={r}, ell={ell}")

        derivative = sp.diff(h_integral, x)
        target_derivative = c_r / sp.sqrt(s) * (1 - x**2 / s) ** r
        require_zero(derivative - target_derivative, f"derivative identity r={r}")
        require_zero(
            h_integral.subs(x, sp.sqrt(s)) - 1,
            f"positive endpoint r={r}",
        )
        require_zero(
            h_integral.subs(x, -sp.sqrt(s)) + 1,
            f"negative endpoint r={r}",
        )
        for order in range(1, r + 1):
            endpoint_derivative = sp.diff(h_integral, x, order)
            require_zero(
                endpoint_derivative.subs(x, sp.sqrt(s)),
                f"positive Hermite derivative r={r}, order={order}",
            )
            require_zero(
                endpoint_derivative.subs(x, -sp.sqrt(s)),
                f"negative Hermite derivative r={r}, order={order}",
            )

        normalization = sp.integrate((1 - t**2) ** r, (t, 0, 1))
        require_zero(c_r * normalization - 1, f"normalization r={r}")

        remainder_polynomial = sp.expand(sp.sqrt(1 + u) * polynomial)
        target_remainder = (
            sp.Rational(2 * r + 1, 2)
            * (-1) ** r
            * central(r)
            * u**r
            / sp.sqrt(1 + u)
        )
        require_zero(
            sp.diff(remainder_polynomial, u) - target_remainder,
            f"remainder derivative r={r}",
        )

    metadata = certificate["beta_hermite"]
    require(
        set(metadata)
        == {
            "degree_five_coefficients",
            "degree_seven_coefficients",
            "degree_five_error_constant",
            "degree_five_band_error_constant",
            "degree_seven_error_constant",
        },
        "beta-Hermite certificate fields",
    )

    def h_coefficients(r: int) -> list[sp.Rational]:
        return [
            sp.Rational(
                (-1) ** ell * (2 * r + 1) * comb(r, ell),
                2 * ell + 1,
            )
            * central(r)
            for ell in range(r + 1)
        ]

    require(
        h_coefficients(2)
        == parse_rationals(metadata["degree_five_coefficients"]),
        "degree-five coefficients",
    )
    require(
        h_coefficients(3)
        == parse_rationals(metadata["degree_seven_coefficients"]),
        "degree-seven coefficients",
    )

    rho = sp.symbols("rho", positive=True)
    r2_bound = (
        sp.Rational(5, 2)
        * central(2)
        * rho**3
        / (3 * sp.sqrt(1 - rho))
    )
    require_zero(
        r2_bound
        - sp.Rational(metadata["degree_five_error_constant"])
        * rho**3
        / sp.sqrt(1 - rho),
        "degree-five error constant",
    )
    require_zero(
        r2_bound.subs(rho, sp.Rational(3, 1) / s)
        - sp.Rational(metadata["degree_five_band_error_constant"])
        / (s**3 * sp.sqrt(1 - 3 / s)),
        "degree-five band error constant",
    )
    r3_bound = (
        sp.Rational(7, 2)
        * central(3)
        * rho**4
        / (4 * sp.sqrt(1 - rho))
    )
    require_zero(
        r3_bound
        - sp.Rational(metadata["degree_seven_error_constant"])
        * rho**4
        / sp.sqrt(1 - rho),
        "degree-seven error constant",
    )


def check_moment_hierarchy() -> None:
    s, kappa, lam, tau, c4 = sp.symbols("s kappa lam tau c4")
    n = s**2 + s + 4

    child_traces = [
        n - 1,
        -3,
        3 * n - 9,
        6 * tau - 27,
        15 * n + 8 * c4 - 81,
    ]
    mixed_traces = [
        -s - 1,
        (s - 1) ** 2,
        2 * kappa - 9 * (s + 1),
        lam - 27 * (s + 1),
    ]

    m6 = sp.expand(
        sum(
            (-1) ** j
            * sp.binomial(3, j)
            * s ** (3 - j)
            * child_traces[j]
            for j in range(4)
        )
    )
    m6_target = sp.expand(
        s**5
        + s**4
        + 12 * s**3
        + 18 * s**2
        + 9 * s
        + 27
        - 6 * tau
    )
    require_zero(m6 - m6_target, "M6 expansion")

    m7 = sp.expand(
        sum(
            (-1) ** j
            * sp.binomial(3, j)
            * s ** (3 - j)
            * mixed_traces[j]
            for j in range(4)
        )
    )
    m7_target = sp.expand(
        6 * kappa * s
        - lam
        - 4 * s**4
        + 5 * s**3
        - 30 * s**2
        + 27
    )
    require_zero(m7 - m7_target, "M7 expansion")

    m8 = sp.expand(
        sum(
            (-1) ** j
            * sp.binomial(4, j)
            * s ** (4 - j)
            * child_traces[j]
            for j in range(5)
        )
    )
    m8_target = sp.expand(
        s**4 * (n - 1)
        + 12 * s**3
        + 18 * s**2 * n
        - 54 * s**2
        - 24 * s * tau
        + 108 * s
        + 15 * n
        + 8 * c4
        - 81
    )
    require_zero(m8 - m8_target, "M8 expansion")

    m1 = -s - 1
    m3 = -2 * s**2 + s - 1
    m5 = 2 * kappa - 3 * s**3 + 3 * s**2 - 11 * s - 9
    h3 = sp.expand(
        (
            sp.Rational(35, 16) * m1
            - sp.Rational(35, 16) * m3 / s
            + sp.Rational(21, 16) * m5 / s**2
            - sp.Rational(5, 16) * m7_target / s**3
        )
        / sp.sqrt(s)
    )
    baseline = -(4 * s**3 + 16 * s**2 + 23 * s + 27) / (
        8 * s ** sp.Rational(5, 2)
    )
    h3_target = (
        baseline
        + sp.Rational(3, 4) * kappa / s ** sp.Rational(5, 2)
        + sp.Rational(5, 16)
        * (lam - 27 * (s + 1))
        / s ** sp.Rational(7, 2)
    )
    require_zero(h3 - h3_target, "degree-seven signature cancellation")


def check_square_defect_inequalities(
    certificate: dict[str, object],
) -> None:
    minimum_s = int(certificate["limits"]["square_defect_min_s"])
    require(minimum_s == 1296, "square-defect threshold")
    require(minimum_s > 3, "square-defect radical domain")
    require(36**2 == minimum_s, "square-defect square-root threshold")

    s = sp.symbols("s", real=True)
    error_gap = (
        18496 * s**3 * (s - 3)
        - 18225 * (s**2 + s + 3) ** 2
    )
    positive_on_ray(
        error_gap,
        s,
        minimum_s,
        "squared certificate for E_s < 17/(4s)",
    )

    x = sp.symbols("x", real=True)
    lower_gap = 2 * x**4 - 68 * x**3 + 17 * x**2 + 3
    upper_gap = 2 * x**4 - 68 * x**3 - 23 * x**2 - 27
    positive_on_ray(
        lower_gap,
        x,
        36,
        "lower square-defect localization",
    )
    positive_on_ray(
        upper_gap,
        x,
        36,
        "upper square-defect localization",
    )

    # If e=d-b is in (1/(2sqrt(s)), 9/(8sqrt(s))), then
    # a=sqrt(s)+4e satisfies 4<a^2-s<10. The upper estimate uses s>=1296.
    require(
        16 * sp.Rational(81, 64) / minimum_s < 1,
        "defect upper slack",
    )


def check_quartic_family(certificate: dict[str, object]) -> None:
    minimum_t = int(certificate["limits"]["quartic_min_t"])
    require(minimum_t == 4, "quartic threshold")
    require(minimum_t > 0, "quartic radical domain")
    t = sp.symbols("t", real=True)

    # For t>=4, sqrt(4t^2-3)>15t/8. Substituting the reciprocal
    # upper bound into the exact inertia interval yields these polynomials.
    positive_on_ray(
        31 * t**2 - 192,
        t,
        minimum_t,
        "quartic radical bound",
    )
    lower_margin = (
        160 * t**5
        - 576 * t**4
        + 68 * t**3
        - 144 * t**2
        + 3 * t
        - 108
    )
    upper_margin = (
        256 * t**6
        - 256 * t**5
        - 576 * t**4
        - 92 * t**3
        - 144 * t**2
        - 27 * t
        - 108
    )
    lower_rational_bound = (
        sp.Rational(5, 16) / t
        - sp.Rational(9, 8) / t**2
        + sp.Rational(17, 128) / t**3
        - sp.Rational(9, 32) / t**4
        + sp.Rational(3, 512) / t**5
        - sp.Rational(27, 128) / t**6
    )
    upper_rational_bound = (
        sp.Rational(1, 2)
        - sp.Rational(1, 2) / t
        - sp.Rational(9, 8) / t**2
        - sp.Rational(23, 128) / t**3
        - sp.Rational(9, 32) / t**4
        - sp.Rational(27, 512) / t**5
        - sp.Rational(27, 128) / t**6
    )
    require_zero(
        lower_rational_bound - lower_margin / (512 * t**6),
        "quartic lower margin reduction",
    )
    require_zero(
        upper_rational_bound - upper_margin / (512 * t**6),
        "quartic upper margin reduction",
    )
    positive_on_ray(
        lower_margin,
        t,
        minimum_t,
        "quartic lower interval margin",
    )
    positive_on_ray(
        upper_margin,
        t,
        minimum_t,
        "quartic upper interval margin",
    )


def check_exceptional_asymptotics(
    certificate: dict[str, object],
) -> None:
    s, delta, length_density = sp.symbols("s delta L", positive=True)
    n = s**2 + s + 4
    root = sp.sqrt(s + delta)
    baseline = -(4 * s**3 + 16 * s**2 + 23 * s + 27) / (
        8 * s ** sp.Rational(5, 2)
    )
    center = sp.simplify(
        sp.Rational(4, 3)
        * s ** sp.Rational(5, 2)
        * (
            -root / 2
            - baseline
            - sp.Rational(5, 16)
            * (length_density * n - 27 * (s + 1))
            / s ** sp.Rational(7, 2)
        )
    )
    exact_center = sp.simplify(
        (
            -5 * length_density * s**2
            - 5 * length_density * s
            - 20 * length_density
            - 8 * s ** sp.Rational(7, 2) * sp.sqrt(s + delta)
            + 8 * s**4
            + 32 * s**3
            + 46 * s**2
            + 189 * s
            + 135
        )
        / (12 * s)
    )
    require_zero(center - exact_center, "exact exceptional center")

    z = sp.symbols("z", positive=True)
    series = sp.series(center.subs(s, 1 / z), z, 0, 1).removeO()
    series_target = (
        (sp.Rational(8, 3) - delta / 3) / z**2
        + (
            -sp.Rational(5, 12) * length_density
            + delta**2 / 12
            + sp.Rational(23, 6)
        )
        / z
        + sp.Rational(63, 4)
        - delta**3 / 24
        - sp.Rational(5, 12) * length_density
    )
    require_zero(series - series_target, "exceptional asymptotic expansion")

    metadata = certificate["exceptional_coefficients"]
    require(
        set(metadata)
        == {
            "delta8_s2",
            "delta6_s2",
            "delta8_s_at_L5",
            "delta8_s_at_L17",
            "delta6_s_at_L5",
            "delta6_s_at_L17",
            "scaled_error_constant",
        },
        "exceptional certificate fields",
    )
    coefficient_s2 = sp.Rational(8, 3) - delta / 3
    coefficient_s = (
        -sp.Rational(5, 12) * length_density
        + delta**2 / 12
        + sp.Rational(23, 6)
    )
    derived = {
        "delta8_s2": coefficient_s2.subs(delta, 8),
        "delta6_s2": coefficient_s2.subs(delta, 6),
        "delta8_s_at_L5": coefficient_s.subs(
            {delta: 8, length_density: 5}
        ),
        "delta8_s_at_L17": coefficient_s.subs(
            {delta: 8, length_density: 17}
        ),
        "delta6_s_at_L5": coefficient_s.subs(
            {delta: 6, length_density: 5}
        ),
        "delta6_s_at_L17": coefficient_s.subs(
            {delta: 6, length_density: 17}
        ),
        "scaled_error_constant": (
            sp.Rational(4, 3) * sp.Rational(35, 128) * 3**4
        ),
    }
    for key, value in derived.items():
        require(
            value == sp.Rational(metadata[key]),
            f"exceptional value {key}",
        )

    scaled_error = sp.simplify(
        sp.Rational(4, 3)
        * s ** sp.Rational(5, 2)
        * (n - 1)
        * sp.Rational(35, 128)
        * (sp.Rational(3, 1) / s) ** 4
        / sp.sqrt(1 - 3 / s)
    )
    target_error = (
        sp.Rational(metadata["scaled_error_constant"])
        * (n - 1)
        / (s ** sp.Rational(3, 2) * sp.sqrt(1 - 3 / s))
    )
    require_zero(
        scaled_error - target_error,
        "scaled exceptional error",
    )


def diagnostic_interval(s_value: int, signature: int) -> dict[str, object]:
    s = sp.Integer(s_value)
    n = s**2 + s + 4
    rank = n - 1
    baseline = -(4 * s**3 + 16 * s**2 + 23 * s + 27) / (
        8 * s ** sp.Rational(5, 2)
    )
    kappa_coefficient = sp.Rational(3, 4) / s ** sp.Rational(5, 2)
    lambda_coefficient = sp.Rational(5, 16) / s ** sp.Rational(7, 2)
    error = (
        rank
        * sp.Rational(35, 128)
        * (sp.Rational(3, 1) / s) ** 4
        / sp.sqrt(1 - 3 / s)
    )
    lambda_low, lambda_high = 5 * n, 17 * n
    kappa_low = sp.N(
        (
            signature
            - error
            - baseline
            - lambda_coefficient * (lambda_high - 27 * (s + 1))
        )
        / kappa_coefficient,
        30,
    )
    kappa_high = sp.N(
        (
            signature
            + error
            - baseline
            - lambda_coefficient * (lambda_low - 27 * (s + 1))
        )
        / kappa_coefficient,
        30,
    )

    parity_polynomial = s**5 + 2 * s**3 - 7 * s**2 - 6 * s - 8
    residues = [
        residue
        for residue in range(5)
        if (2 * residue + int(parity_polynomial)) % 10 == 0
    ]
    return {
        "s": s_value,
        "n": int(n),
        "signature": signature,
        "kappa_real_interval": [str(kappa_low), str(kappa_high)],
        "kappa_mod_5": residues,
    }


def check_diagnostics(certificate: dict[str, object]) -> None:
    expected = certificate["diagnostics"]
    require(
        set(expected) == {"s28", "s30"},
        "diagnostic certificate fields",
    )
    actual = {
        "s28": diagnostic_interval(28, -3),
        "s30": diagnostic_interval(30, -3),
    }
    require(actual == expected, "diagnostic values")


def check_rational_child_obstruction(
    certificate: dict[str, object],
) -> None:
    minimum_a = int(certificate["limits"]["rational_child_min_a"])
    require(minimum_a == 10, "rational-child threshold")
    minimum_offset = 6 - 3
    maximum_offset = 8 + 3
    require(minimum_offset > 0, "rational-child lower offset")
    require(
        maximum_offset < 2 * minimum_a - 1,
        "rational-child upper offset",
    )

    a = sp.symbols("a", real=True)
    positive_on_ray(
        2 * a - 1 - maximum_offset,
        a,
        minimum_a,
        "rational-child universal square gap",
    )


def run_verification() -> None:
    certificate = load_certificate()
    check_beta_hermite(certificate)
    print(
        "SYMPY BETA-HERMITE PASS: exact identities verified for r=0,...,12"
    )
    check_moment_hierarchy()
    print(
        "SYMPY MOMENT PASS: M6, M7, M8 and degree-seven cancellation verified"
    )
    check_square_defect_inequalities(certificate)
    print(
        "SYMPY SQUARE-DEFECT PASS: threshold inequalities verified for s>=1296"
    )
    check_quartic_family(certificate)
    print("SYMPY QUARTIC PASS: interval exclusion verified for t>=4")
    check_exceptional_asymptotics(certificate)
    print(
        "SYMPY EXCEPTIONAL PASS: delta=6 and delta=8 coefficients verified"
    )
    check_rational_child_obstruction(certificate)
    print(
        "SYMPY RATIONAL-CHILD PASS: universal obstruction verified for all a>=10"
    )
    check_diagnostics(certificate)
    print("SYMPY DIAGNOSTIC PASS: s=28 and s=30 values verified")
    print("SYMPY VERIFIER: ALL DECLARED ALGEBRAIC CHECKS PASSED")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test-failure",
        action="store_true",
        help="Intentionally fail before verification for the regression harness.",
    )
    arguments = parser.parse_args()
    if arguments.self_test_failure:
        require(False, "intentional verifier self-test")
    run_verification()


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print(f"SYMPY VERIFICATION FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
