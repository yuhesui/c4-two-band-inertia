#!/usr/bin/env python3
"""Independent exact checks using only the Python standard library.

This verifier does not import SymPy or the principal verifier. It uses
fractions, a small formal-polynomial implementation, shifted positivity
certificates, and high-precision Decimal arithmetic for non-load-bearing
diagnostics.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from math import comb
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / "certificates" / "verification_certificates.json"
SCHEMA = "c4-two-band-inertia-verification-v1"
SCOPE = (
    "Exact algebraic supplement; "
    "graph-theoretic arguments remain human-verified."
)
VARIABLE_COUNT = 5
Monomial = tuple[int, int, int, int, int]
Polynomial = dict[Monomial, Fraction]


class VerificationError(RuntimeError):
    """Raised when an exact verification condition fails."""


def require(condition: bool, label: str) -> None:
    """Enforce a verification condition even when Python optimization is on."""
    if not condition:
        raise VerificationError(label)


def fraction(value: str | int) -> Fraction:
    return Fraction(value)


def central(j: int) -> Fraction:
    return Fraction(comb(2 * j, j), 4**j)


def clean(polynomial: Polynomial) -> Polynomial:
    return {
        monomial: coefficient
        for monomial, coefficient in polynomial.items()
        if coefficient
    }


def constant(value: int | Fraction) -> Polynomial:
    coefficient = Fraction(value)
    if coefficient == 0:
        return {}
    return {(0, 0, 0, 0, 0): coefficient}


def variable(index: int) -> Polynomial:
    powers = [0] * VARIABLE_COUNT
    powers[index] = 1
    return {tuple(powers): Fraction(1)}


def add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for monomial, coefficient in polynomial.items():
            result[monomial] = result.get(monomial, Fraction()) + coefficient
    return clean(result)


def scale(polynomial: Polynomial, scalar: int | Fraction) -> Polynomial:
    factor = Fraction(scalar)
    return clean(
        {
            monomial: coefficient * factor
            for monomial, coefficient in polynomial.items()
        }
    )


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[index] + right_monomial[index]
                for index in range(VARIABLE_COUNT)
            )
            result[monomial] = (
                result.get(monomial, Fraction())
                + left_coefficient * right_coefficient
            )
    return clean(result)


def power(polynomial: Polynomial, exponent: int) -> Polynomial:
    require(exponent >= 0, "nonnegative polynomial exponent")
    result = constant(1)
    factor = polynomial
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = multiply(result, factor)
        factor = multiply(factor, factor)
        remaining //= 2
    return result


def subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    return add(left, scale(right, -1))


def polynomial_sum(terms: list[Polynomial]) -> Polynomial:
    return add(*terms)


def uadd(
    left: list[Fraction],
    right: list[Fraction],
) -> list[Fraction]:
    size = max(len(left), len(right))
    result = [Fraction() for _ in range(size)]
    for index, coefficient in enumerate(left):
        result[index] += coefficient
    for index, coefficient in enumerate(right):
        result[index] += coefficient
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def uscale(
    polynomial: list[Fraction],
    scalar: int | Fraction,
) -> list[Fraction]:
    factor = Fraction(scalar)
    return [coefficient * factor for coefficient in polynomial]


def umultiply(
    left: list[Fraction],
    right: list[Fraction],
) -> list[Fraction]:
    result = [Fraction() for _ in range(len(left) + len(right) - 1)]
    for left_index, left_coefficient in enumerate(left):
        for right_index, right_coefficient in enumerate(right):
            result[left_index + right_index] += (
                left_coefficient * right_coefficient
            )
    return result


def upower(
    polynomial: list[Fraction],
    exponent: int,
) -> list[Fraction]:
    require(exponent >= 0, "nonnegative univariate exponent")
    result = [Fraction(1)]
    factor = polynomial
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = umultiply(result, factor)
        factor = umultiply(factor, factor)
        remaining //= 2
    return result


def uderivative(
    polynomial: list[Fraction],
    order: int = 1,
) -> list[Fraction]:
    result = polynomial
    for _ in range(order):
        if len(result) == 1:
            return [Fraction()]
        result = [
            exponent * result[exponent]
            for exponent in range(1, len(result))
        ]
    return result


def uevaluate(
    polynomial: list[Fraction],
    value: int | Fraction,
) -> Fraction:
    point = Fraction(value)
    result = Fraction()
    for coefficient in reversed(polynomial):
        result = result * point + coefficient
    return result


def shift_coefficients(
    coefficients: list[Fraction],
    start: int,
) -> list[Fraction]:
    """Return coefficients of p(y+start), in ascending powers of y."""
    shifted = [Fraction() for _ in coefficients]
    for exponent, coefficient in enumerate(coefficients):
        for new_exponent in range(exponent + 1):
            shifted[new_exponent] += (
                coefficient
                * comb(exponent, new_exponent)
                * start ** (exponent - new_exponent)
            )
    return shifted


def positive_on_ray(
    coefficients: list[int | Fraction],
    start: int,
    label: str,
) -> None:
    shifted = shift_coefficients(
        [Fraction(coefficient) for coefficient in coefficients],
        start,
    )
    require(all(coefficient >= 0 for coefficient in shifted), label)
    require(shifted[0] > 0, f"{label}: strict endpoint")


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
    require(
        set(certificate["limits"])
        == {
            "sympy_max_r",
            "independent_max_r",
            "square_defect_min_s",
            "rational_child_min_a",
            "quartic_min_t",
        },
        "certificate limit fields",
    )
    return certificate


def h_coefficients(r: int) -> list[Fraction]:
    return [
        Fraction(
            (-1) ** ell * (2 * r + 1) * comb(r, ell),
            2 * ell + 1,
        )
        * central(r)
        for ell in range(r + 1)
    ]


def check_beta_hermite(certificate: dict[str, object]) -> None:
    max_r = int(certificate["limits"]["independent_max_r"])
    require(max_r == 20, "independent hierarchy limit")
    for r in range(max_r + 1):
        for ell in range(r + 1):
            lhs = sum(
                (
                    central(j) * comb(j, ell)
                    for j in range(ell, r + 1)
                ),
                Fraction(),
            )
            rhs = (
                Fraction(2 * r + 1, 2 * ell + 1)
                * central(r)
                * comb(r, ell)
            )
            require(lhs == rhs, f"coefficient identity r={r}, ell={ell}")

        # Verify the Taylor and integral forms as exact polynomials in
        # y=x/sqrt(s), independently of the SymPy construction.
        taylor_sum = [Fraction()]
        for j in range(r + 1):
            term = uscale(
                upower([Fraction(-1), Fraction(), Fraction(1)], j),
                (-1) ** j * central(j),
            )
            taylor_sum = uadd(taylor_sum, term)
        h_taylor = umultiply([Fraction(), Fraction(1)], taylor_sum)

        c_r = Fraction(2 * r + 1) * central(r)
        h_integral = [Fraction() for _ in range(2 * r + 2)]
        for ell in range(r + 1):
            h_integral[2 * ell + 1] = (
                c_r
                * (-1) ** ell
                * comb(r, ell)
                / (2 * ell + 1)
            )
        require(h_taylor == h_integral, f"Taylor/integral form r={r}")

        derivative_target = uscale(
            upower([Fraction(1), Fraction(), Fraction(-1)], r),
            c_r,
        )
        require(
            uderivative(h_integral) == derivative_target,
            f"derivative identity r={r}",
        )
        require(
            uevaluate(h_integral, 1) == 1,
            f"positive endpoint r={r}",
        )
        require(
            uevaluate(h_integral, -1) == -1,
            f"negative endpoint r={r}",
        )
        for order in range(1, r + 1):
            endpoint_derivative = uderivative(h_integral, order)
            require(
                uevaluate(endpoint_derivative, 1) == 0,
                f"positive Hermite derivative r={r}, order={order}",
            )
            require(
                uevaluate(endpoint_derivative, -1) == 0,
                f"negative Hermite derivative r={r}, order={order}",
            )

        # Multiplying the exact remainder derivative by 2*sqrt(1+u)
        # turns it into this rational polynomial identity.
        remainder_polynomial = [
            (-1) ** j * central(j) for j in range(r + 1)
        ]
        remainder_left = uadd(
            remainder_polynomial,
            uscale(
                umultiply(
                    [Fraction(1), Fraction(1)],
                    uderivative(remainder_polynomial),
                ),
                2,
            ),
        )
        remainder_target = [Fraction() for _ in range(r + 1)]
        remainder_target[r] = (
            (2 * r + 1) * (-1) ** r * central(r)
        )
        require(
            remainder_left == remainder_target,
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
    require(
        h_coefficients(2)
        == [fraction(value) for value in metadata["degree_five_coefficients"]],
        "degree-five coefficients",
    )
    require(
        h_coefficients(3)
        == [fraction(value) for value in metadata["degree_seven_coefficients"]],
        "degree-seven coefficients",
    )

    degree_five_error = Fraction(5, 2) * central(2) / 3
    degree_seven_error = Fraction(7, 2) * central(3) / 4
    require(
        degree_five_error
        == fraction(metadata["degree_five_error_constant"]),
        "degree-five error constant",
    )
    require(
        degree_five_error * 3**3
        == fraction(metadata["degree_five_band_error_constant"]),
        "degree-five band error constant",
    )
    require(
        degree_seven_error
        == fraction(metadata["degree_seven_error_constant"]),
        "degree-seven error constant",
    )


def check_moment_hierarchy() -> None:
    s = variable(0)
    kappa = variable(1)
    lam = variable(2)
    tau = variable(3)
    c4 = variable(4)
    one = constant(1)
    n = add(power(s, 2), s, constant(4))

    child_traces = [
        subtract(n, one),
        constant(-3),
        add(scale(n, 3), constant(-9)),
        add(scale(tau, 6), constant(-27)),
        add(scale(n, 15), scale(c4, 8), constant(-81)),
    ]
    mixed_traces = [
        add(scale(s, -1), constant(-1)),
        power(add(s, constant(-1)), 2),
        add(scale(kappa, 2), scale(add(s, one), -9)),
        add(lam, scale(add(s, one), -27)),
    ]

    m6 = polynomial_sum(
        [
            scale(
                multiply(power(s, 3 - j), child_traces[j]),
                (-1) ** j * comb(3, j),
            )
            for j in range(4)
        ]
    )
    m6_target = add(
        power(s, 5),
        power(s, 4),
        scale(power(s, 3), 12),
        scale(power(s, 2), 18),
        scale(s, 9),
        constant(27),
        scale(tau, -6),
    )
    require(m6 == m6_target, "M6 formal polynomial expansion")

    m7 = polynomial_sum(
        [
            scale(
                multiply(power(s, 3 - j), mixed_traces[j]),
                (-1) ** j * comb(3, j),
            )
            for j in range(4)
        ]
    )
    m7_target = add(
        scale(multiply(kappa, s), 6),
        scale(lam, -1),
        scale(power(s, 4), -4),
        scale(power(s, 3), 5),
        scale(power(s, 2), -30),
        constant(27),
    )
    require(m7 == m7_target, "M7 formal polynomial expansion")

    m8 = polynomial_sum(
        [
            scale(
                multiply(power(s, 4 - j), child_traces[j]),
                (-1) ** j * comb(4, j),
            )
            for j in range(5)
        ]
    )
    m8_target = add(
        multiply(power(s, 4), subtract(n, one)),
        scale(power(s, 3), 12),
        scale(multiply(power(s, 2), n), 18),
        scale(power(s, 2), -54),
        scale(multiply(s, tau), -24),
        scale(s, 108),
        scale(n, 15),
        scale(c4, 8),
        constant(-81),
    )
    require(m8 == m8_target, "M8 formal polynomial expansion")

    m1 = add(scale(s, -1), constant(-1))
    m3 = add(scale(power(s, 2), -2), s, constant(-1))
    m5 = add(
        scale(kappa, 2),
        scale(power(s, 3), -3),
        scale(power(s, 2), 3),
        scale(s, -11),
        constant(-9),
    )
    scaled_h3_left = add(
        scale(multiply(power(s, 3), m1), 35),
        scale(multiply(power(s, 2), m3), -35),
        scale(multiply(s, m5), 21),
        scale(m7_target, -5),
    )
    baseline_polynomial = add(
        scale(power(s, 3), 4),
        scale(power(s, 2), 16),
        scale(s, 23),
        constant(27),
    )
    scaled_h3_target = add(
        scale(multiply(s, baseline_polynomial), -2),
        scale(multiply(kappa, s), 12),
        scale(add(lam, scale(add(s, one), -27)), 5),
    )
    require(
        scaled_h3_left == scaled_h3_target,
        "degree-seven cancellation as an integer polynomial",
    )


def check_square_defect_inequalities(
    certificate: dict[str, object],
) -> None:
    minimum_s = int(certificate["limits"]["square_defect_min_s"])
    require(minimum_s == 1296, "square-defect threshold")
    require(minimum_s > 3, "square-defect radical domain")
    require(36**2 == minimum_s, "square-defect square-root threshold")

    first = uscale([0, 0, 0, -3, 1], 18496)
    second = uscale(umultiply([3, 1, 1], [3, 1, 1]), -18225)
    error_gap = uadd(first, second)
    positive_on_ray(
        error_gap,
        minimum_s,
        "squared certificate for E_s < 17/(4s)",
    )

    positive_on_ray(
        [3, 0, 17, -68, 2],
        36,
        "lower square-defect localization",
    )
    positive_on_ray(
        [-27, 0, -23, -68, 2],
        36,
        "upper square-defect localization",
    )
    require(
        Fraction(16 * 81, 64 * minimum_s) < 1,
        "defect upper slack",
    )


def check_quartic_family(certificate: dict[str, object]) -> None:
    minimum_t = int(certificate["limits"]["quartic_min_t"])
    require(minimum_t == 4, "quartic threshold")
    require(minimum_t > 0, "quartic radical domain")
    positive_on_ray(
        [-192, 0, 31],
        minimum_t,
        "quartic radical bound",
    )
    positive_on_ray(
        [-108, 3, -144, 68, -576, 160],
        minimum_t,
        "quartic lower interval margin",
    )
    positive_on_ray(
        [-108, -27, -144, -92, -576, -256, 256],
        minimum_t,
        "quartic upper interval margin",
    )


def check_exceptional_asymptotics(
    certificate: dict[str, object],
) -> None:
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

    def coefficient_s2(delta: int) -> Fraction:
        return Fraction(8, 3) - Fraction(delta, 3)

    def coefficient_s(delta: int, length_density: int) -> Fraction:
        return (
            -Fraction(5 * length_density, 12)
            + Fraction(delta**2, 12)
            + Fraction(23, 6)
        )

    derived = {
        "delta8_s2": coefficient_s2(8),
        "delta6_s2": coefficient_s2(6),
        "delta8_s_at_L5": coefficient_s(8, 5),
        "delta8_s_at_L17": coefficient_s(8, 17),
        "delta6_s_at_L5": coefficient_s(6, 5),
        "delta6_s_at_L17": coefficient_s(6, 17),
        "scaled_error_constant": (
            Fraction(4, 3) * Fraction(35, 128) * 3**4
        ),
    }
    for key, value in derived.items():
        require(value == fraction(metadata[key]), f"exceptional value {key}")


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
    positive_on_ray(
        [-(1 + maximum_offset), 2],
        minimum_a,
        "rational-child universal square gap",
    )


def decimal_diagnostic(s_value: int, signature: int) -> dict[str, object]:
    with localcontext() as context:
        context.prec = 80
        s = Decimal(s_value)
        n = s**2 + s + 4
        root_s = s.sqrt()
        s_five_halves = s**2 * root_s
        s_seven_halves = s**3 * root_s
        baseline = -(
            4 * s**3 + 16 * s**2 + 23 * s + 27
        ) / (8 * s_five_halves)
        kappa_coefficient = Decimal(3) / (4 * s_five_halves)
        lambda_coefficient = Decimal(5) / (16 * s_seven_halves)
        error = (
            (n - 1)
            * Decimal(35)
            / Decimal(128)
            * (Decimal(3) / s) ** 4
            / (1 - Decimal(3) / s).sqrt()
        )
        lambda_low = 5 * n
        lambda_high = 17 * n
        kappa_low = (
            Decimal(signature)
            - error
            - baseline
            - lambda_coefficient * (lambda_high - 27 * (s + 1))
        ) / kappa_coefficient
        kappa_high = (
            Decimal(signature)
            + error
            - baseline
            - lambda_coefficient * (lambda_low - 27 * (s + 1))
        ) / kappa_coefficient

    parity_polynomial = (
        s_value**5
        + 2 * s_value**3
        - 7 * s_value**2
        - 6 * s_value
        - 8
    )
    residues = [
        residue
        for residue in range(5)
        if (2 * residue + parity_polynomial) % 10 == 0
    ]
    return {
        "s": s_value,
        "n": int(n),
        "signature": signature,
        "kappa_real_interval": [
            format(kappa_low, ".30g"),
            format(kappa_high, ".30g"),
        ],
        "kappa_mod_5": residues,
    }


def check_diagnostics(certificate: dict[str, object]) -> None:
    expected = certificate["diagnostics"]
    require(
        set(expected) == {"s28", "s30"},
        "diagnostic certificate fields",
    )
    actual = {
        "s28": decimal_diagnostic(28, -3),
        "s30": decimal_diagnostic(30, -3),
    }
    require(actual == expected, "independent diagnostic values")


def run_verification() -> None:
    certificate = load_certificate()
    check_beta_hermite(certificate)
    print(
        "INDEPENDENT BETA-HERMITE PASS: exact coefficients verified for r=0,...,20"
    )
    check_moment_hierarchy()
    print(
        "INDEPENDENT MOMENT PASS: formal M6, M7, M8 and H3 polynomials verified"
    )
    check_square_defect_inequalities(certificate)
    print(
        "INDEPENDENT SQUARE-DEFECT PASS: threshold inequalities verified for s>=1296"
    )
    check_quartic_family(certificate)
    print(
        "INDEPENDENT QUARTIC PASS: interval exclusion verified for t>=4"
    )
    check_exceptional_asymptotics(certificate)
    print(
        "INDEPENDENT EXCEPTIONAL PASS: exact rational coefficients verified"
    )
    check_rational_child_obstruction(certificate)
    print(
        "INDEPENDENT RATIONAL-CHILD PASS: universal obstruction verified for all a>=10"
    )
    check_diagnostics(certificate)
    print(
        "INDEPENDENT DIAGNOSTIC PASS: "
        "independent Decimal intervals and residues verified"
    )
    print(
        "INDEPENDENT VERIFIER: ALL DECLARED ALGEBRAIC CHECKS PASSED"
    )


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
        print(
            f"INDEPENDENT VERIFICATION FAILED: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1)
