import Mathlib

set_option autoImplicit false

/-!
# Exact certificates for the two-band inertia supplement

This file formalizes the load-bearing polynomial identities and universal
inequalities in the supplementary verification package. It deliberately does
not assert the graph-theoretic premises established in the associated paper.
-/

namespace C4TwoBandInertia

section BetaHermite

/-- The degree-five beta--Hermite polynomial in its Taylor and monomial forms. -/
theorem degreeFivePolynomial (y : ℚ) :
    y * (1 - (1 / 2 : ℚ) * (y ^ 2 - 1)
        + (3 / 8 : ℚ) * (y ^ 2 - 1) ^ 2) =
      (15 / 8 : ℚ) * y - (5 / 4 : ℚ) * y ^ 3
        + (3 / 8 : ℚ) * y ^ 5 := by
  ring

/-- The degree-seven beta--Hermite polynomial in its Taylor and monomial forms. -/
theorem degreeSevenPolynomial (y : ℚ) :
    y * (1 - (1 / 2 : ℚ) * (y ^ 2 - 1)
        + (3 / 8 : ℚ) * (y ^ 2 - 1) ^ 2
        - (5 / 16 : ℚ) * (y ^ 2 - 1) ^ 3) =
      (35 / 16 : ℚ) * y - (35 / 16 : ℚ) * y ^ 3
        + (21 / 16 : ℚ) * y ^ 5 - (5 / 16 : ℚ) * y ^ 7 := by
  ring

/-- Coefficient identity for the derivative of the degree-five polynomial. -/
theorem degreeFiveDerivativeIdentity (y : ℚ) :
    (15 / 8 : ℚ) - (15 / 4 : ℚ) * y ^ 2
        + (15 / 8 : ℚ) * y ^ 4 =
      (15 / 8 : ℚ) * (1 - y ^ 2) ^ 2 := by
  ring

/-- Coefficient identity for the derivative of the degree-seven polynomial. -/
theorem degreeSevenDerivativeIdentity (y : ℚ) :
    (35 / 16 : ℚ) - (105 / 16 : ℚ) * y ^ 2
        + (105 / 16 : ℚ) * y ^ 4 - (35 / 16 : ℚ) * y ^ 6 =
      (35 / 16 : ℚ) * (1 - y ^ 2) ^ 3 := by
  ring

theorem degreeFiveErrorConstant :
    (5 / 2 : ℚ) * (3 / 8 : ℚ) / 3 = 5 / 16 := by
  norm_num

theorem degreeFiveBandErrorConstant :
    (5 / 16 : ℚ) * 3 ^ 3 = 135 / 16 := by
  norm_num

theorem degreeSevenErrorConstant :
    (7 / 2 : ℚ) * (5 / 16 : ℚ) / 4 = 35 / 128 := by
  norm_num

end BetaHermite

section Moments

/-- Formal sixth-moment binomial expansion. -/
theorem sixthMomentExpansion (s tau : ℚ) :
    s ^ 3 * (s ^ 2 + s + 4 - 1)
        - 3 * s ^ 2 * (-3)
        + 3 * s * (3 * (s ^ 2 + s + 4) - 9)
        - (6 * tau - 27) =
      s ^ 5 + s ^ 4 + 12 * s ^ 3 + 18 * s ^ 2
        + 9 * s + 27 - 6 * tau := by
  ring

/-- Formal seventh-moment binomial expansion. -/
theorem seventhMomentExpansion (s kappa lambda : ℚ) :
    s ^ 3 * (-s - 1)
        - 3 * s ^ 2 * (s - 1) ^ 2
        + 3 * s * (2 * kappa - 9 * (s + 1))
        - (lambda - 27 * (s + 1)) =
      6 * kappa * s - lambda - 4 * s ^ 4 + 5 * s ^ 3
        - 30 * s ^ 2 + 27 := by
  ring

/-- Formal eighth-moment binomial expansion. -/
theorem eighthMomentExpansion (s tau c4 : ℚ) :
    s ^ 4 * (s ^ 2 + s + 4 - 1)
        - 4 * s ^ 3 * (-3)
        + 6 * s ^ 2 * (3 * (s ^ 2 + s + 4) - 9)
        - 4 * s * (6 * tau - 27)
        + (15 * (s ^ 2 + s + 4) + 8 * c4 - 81) =
      s ^ 4 * (s ^ 2 + s + 4 - 1) + 12 * s ^ 3
        + 18 * s ^ 2 * (s ^ 2 + s + 4) - 54 * s ^ 2
        - 24 * s * tau + 108 * s + 15 * (s ^ 2 + s + 4)
        + 8 * c4 - 81 := by
  ring

/-- Degree-seven signature cancellation after clearing all denominators. -/
theorem degreeSevenSignatureCancellation (s kappa lambda : ℚ) :
    35 * s ^ 3 * (-s - 1)
        - 35 * s ^ 2 * (-2 * s ^ 2 + s - 1)
        + 21 * s * (2 * kappa - 3 * s ^ 3 + 3 * s ^ 2 - 11 * s - 9)
        - 5 * (6 * kappa * s - lambda - 4 * s ^ 4
          + 5 * s ^ 3 - 30 * s ^ 2 + 27) =
      -2 * s * (4 * s ^ 3 + 16 * s ^ 2 + 23 * s + 27)
        + 12 * s * kappa + 5 * (lambda - 27 * (s + 1)) := by
  ring

end Moments

section SquareDefect

/-- The squared error-bound certificate is positive throughout `s >= 1296`. -/
theorem squareDefectErrorGap {s : ℚ} (hs : 1296 ≤ s) :
    18496 * s ^ 3 * (s - 3)
        - 18225 * (s ^ 2 + s + 3) ^ 2 > 0 := by
  let y : ℚ := s - 1296
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have hs' : s = y + 1296 := by
    dsimp [y]
    ring
  rw [hs']
  calc
    18496 * (y + 1296) ^ 3 * (y + 1296 - 3)
          - 18225 * ((y + 1296) ^ 2 + (y + 1296) + 3) ^ 2 =
        271 * y ^ 4 + 1312926 * y ^ 3 + 2373473097 * y ^ 2
          + 1896039661050 * y + 564177351620583 := by ring
    _ > 0 := by positivity

/-- The lower square-defect localization polynomial is positive for `x >= 36`. -/
theorem squareDefectLowerGap {x : ℚ} (hx : 36 ≤ x) :
    2 * x ^ 4 - 68 * x ^ 3 + 17 * x ^ 2 + 3 > 0 := by
  let y : ℚ := x - 36
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have hx' : x = y + 36 := by
    dsimp [y]
    ring
  rw [hx']
  calc
    2 * (y + 36) ^ 4 - 68 * (y + 36) ^ 3
          + 17 * (y + 36) ^ 2 + 3 =
        2 * y ^ 4 + 220 * y ^ 3 + 8225 * y ^ 2
          + 110088 * y + 208659 := by ring
    _ > 0 := by positivity

/-- The upper square-defect localization polynomial is positive for `x >= 36`. -/
theorem squareDefectUpperGap {x : ℚ} (hx : 36 ≤ x) :
    2 * x ^ 4 - 68 * x ^ 3 - 23 * x ^ 2 - 27 > 0 := by
  let y : ℚ := x - 36
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have hx' : x = y + 36 := by
    dsimp [y]
    ring
  rw [hx']
  calc
    2 * (y + 36) ^ 4 - 68 * (y + 36) ^ 3
          - 23 * (y + 36) ^ 2 - 27 =
        2 * y ^ 4 + 220 * y ^ 3 + 8185 * y ^ 2
          + 107208 * y + 156789 := by ring
    _ > 0 := by positivity

theorem squareDefectUpperSlack :
    16 * (81 / 64 : ℚ) / 1296 < 1 := by
  norm_num

end SquareDefect

section QuarticFamily

/-- Polynomial certificate for the radical estimate used when `t >= 4`. -/
theorem quarticRadicalGap {t : ℚ} (ht : 4 ≤ t) :
    31 * t ^ 2 - 192 > 0 := by
  let y : ℚ := t - 4
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have ht' : t = y + 4 := by
    dsimp [y]
    ring
  rw [ht']
  calc
    31 * (y + 4) ^ 2 - 192 = 31 * y ^ 2 + 248 * y + 304 := by ring
    _ > 0 := by positivity

/-- The lower quartic interval margin is positive for `t >= 4`. -/
theorem quarticLowerMargin {t : ℚ} (ht : 4 ≤ t) :
    160 * t ^ 5 - 576 * t ^ 4 + 68 * t ^ 3
        - 144 * t ^ 2 + 3 * t - 108 > 0 := by
  let y : ℚ := t - 4
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have ht' : t = y + 4 := by
    dsimp [y]
    ring
  rw [ht']
  calc
    160 * (y + 4) ^ 5 - 576 * (y + 4) ^ 4
          + 68 * (y + 4) ^ 3 - 144 * (y + 4) ^ 2
          + 3 * (y + 4) - 108 =
        160 * y ^ 5 + 2624 * y ^ 4 + 16452 * y ^ 3
          + 47776 * y ^ 2 + 59459 * y + 18336 := by ring
    _ > 0 := by positivity

/-- The upper quartic interval margin is positive for `t >= 4`. -/
theorem quarticUpperMargin {t : ℚ} (ht : 4 ≤ t) :
    256 * t ^ 6 - 256 * t ^ 5 - 576 * t ^ 4
        - 92 * t ^ 3 - 144 * t ^ 2 - 27 * t - 108 > 0 := by
  let y : ℚ := t - 4
  have hy : 0 ≤ y := by
    dsimp [y]
    linarith
  have ht' : t = y + 4 := by
    dsimp [y]
    ring
  rw [ht']
  calc
    256 * (y + 4) ^ 6 - 256 * (y + 4) ^ 5
          - 576 * (y + 4) ^ 4 - 92 * (y + 4) ^ 3
          - 144 * (y + 4) ^ 2 - 27 * (y + 4) - 108 =
        256 * y ^ 6 + 5888 * y ^ 5 + 55744 * y ^ 4
          + 277412 * y ^ 3 + 762656 * y ^ 2
          + 1092133 * y + 630568 := by ring
    _ > 0 := by positivity

/-- Exact reduction of the lower rational interval bound to its margin. -/
theorem quarticLowerReduction {t : ℚ} (ht : t ≠ 0) :
    (5 / 16 : ℚ) / t - (9 / 8 : ℚ) / t ^ 2
        + (17 / 128 : ℚ) / t ^ 3 - (9 / 32 : ℚ) / t ^ 4
        + (3 / 512 : ℚ) / t ^ 5 - (27 / 128 : ℚ) / t ^ 6 =
      (160 * t ^ 5 - 576 * t ^ 4 + 68 * t ^ 3
        - 144 * t ^ 2 + 3 * t - 108) / (512 * t ^ 6) := by
  field_simp [ht] <;> ring

/-- Exact reduction of the upper rational interval bound to its margin. -/
theorem quarticUpperReduction {t : ℚ} (ht : t ≠ 0) :
    (1 / 2 : ℚ) - (1 / 2 : ℚ) / t - (9 / 8 : ℚ) / t ^ 2
        - (23 / 128 : ℚ) / t ^ 3 - (9 / 32 : ℚ) / t ^ 4
        - (27 / 512 : ℚ) / t ^ 5 - (27 / 128 : ℚ) / t ^ 6 =
      (256 * t ^ 6 - 256 * t ^ 5 - 576 * t ^ 4
        - 92 * t ^ 3 - 144 * t ^ 2 - 27 * t - 108) /
          (512 * t ^ 6) := by
  field_simp [ht] <;> ring

end QuarticFamily

section ExceptionalFamily

theorem exceptionalDelta8QuadraticCoefficient :
    (8 / 3 : ℚ) - 8 / 3 = 0 := by
  norm_num

theorem exceptionalDelta6QuadraticCoefficient :
    (8 / 3 : ℚ) - 6 / 3 = 2 / 3 := by
  norm_num

theorem exceptionalDelta8Length5LinearCoefficient :
    -(5 / 12 : ℚ) * 5 + 8 ^ 2 / 12 + 23 / 6 = 85 / 12 := by
  norm_num

theorem exceptionalDelta8Length17LinearCoefficient :
    -(5 / 12 : ℚ) * 17 + 8 ^ 2 / 12 + 23 / 6 = 25 / 12 := by
  norm_num

theorem exceptionalDelta6Length5LinearCoefficient :
    -(5 / 12 : ℚ) * 5 + 6 ^ 2 / 12 + 23 / 6 = 19 / 4 := by
  norm_num

theorem exceptionalDelta6Length17LinearCoefficient :
    -(5 / 12 : ℚ) * 17 + 6 ^ 2 / 12 + 23 / 6 = -1 / 4 := by
  norm_num

theorem exceptionalScaledErrorConstant :
    (4 / 3 : ℚ) * (35 / 128 : ℚ) * 3 ^ 4 = 945 / 32 := by
  norm_num

end ExceptionalFamily

section RationalChild

/--
For every permitted offset, `a^2 - (delta + mu)` lies strictly between the
consecutive squares `(a - 1)^2` and `a^2` once `a >= 10`.
-/
theorem rationalChildSquareGap {a delta mu : ℤ}
    (ha : 10 ≤ a)
    (hdelta : delta = 6 ∨ delta = 8)
    (hmuLower : -3 ≤ mu)
    (hmuUpper : mu ≤ 3) :
    (a - 1) ^ 2 < a ^ 2 - (delta + mu) ∧
      a ^ 2 - (delta + mu) < a ^ 2 := by
  rcases hdelta with rfl | rfl
  · constructor <;> nlinarith
  · constructor <;> nlinarith

/-- The permitted rational-child value cannot be an integer square. -/
theorem rationalChildNotSquare {a delta mu b : ℤ}
    (ha : 10 ≤ a)
    (hdelta : delta = 6 ∨ delta = 8)
    (hmuLower : -3 ≤ mu)
    (hmuUpper : mu ≤ 3)
    (hb : 0 ≤ b) :
    b ^ 2 ≠ a ^ 2 - (delta + mu) := by
  intro heq
  obtain ⟨hlower, hupper⟩ :=
    rationalChildSquareGap ha hdelta hmuLower hmuUpper
  rw [← heq] at hlower hupper
  have hbLower : a - 1 < b := by
    nlinarith
  have hbUpper : b < a := by
    nlinarith
  omega

end RationalChild

end C4TwoBandInertia
