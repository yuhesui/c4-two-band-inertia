#!/usr/bin/env bash
set -euo pipefail

if [[ "${NANODA_ALLOW_SORRY:-}" != "false" ]]; then
  echo "NANODA_ALLOW_SORRY must be explicitly set to false" >&2
  exit 1
fi

readonly LEAN4EXPORT_REV="15f6055e299ad5b89345e533cc2192f4cc00f659"
readonly NANODA_REV="418320295890faed83a96fd97907b12a3b6728c2"
readonly WORK_DIR="$(mktemp -d)"
readonly EXPORT_DIR="${WORK_DIR}/lean4export"
readonly NANODA_DIR="${WORK_DIR}/nanoda_lib"
readonly EXPORT_FILE="${WORK_DIR}/c4-two-band-inertia.export"
readonly CONFIG_FILE="${WORK_DIR}/nanoda.json"

cleanup() {
  rm -rf -- "${WORK_DIR}"
}
trap cleanup EXIT

git init --quiet "${EXPORT_DIR}"
git -C "${EXPORT_DIR}" remote add origin \
  https://github.com/leanprover/lean4export.git
git -C "${EXPORT_DIR}" fetch --quiet --depth 1 origin "${LEAN4EXPORT_REV}"
git -C "${EXPORT_DIR}" checkout --quiet --detach FETCH_HEAD
cp lean-toolchain "${EXPORT_DIR}/lean-toolchain"
lake --dir "${EXPORT_DIR}" build

git init --quiet "${NANODA_DIR}"
git -C "${NANODA_DIR}" remote add origin \
  https://github.com/ammkrn/nanoda_lib.git
git -C "${NANODA_DIR}" fetch --quiet --depth 1 origin "${NANODA_REV}"
git -C "${NANODA_DIR}" checkout --quiet --detach FETCH_HEAD
cargo build --quiet --release --manifest-path "${NANODA_DIR}/Cargo.toml"

lake env "${EXPORT_DIR}/.lake/build/bin/lean4export" \
  C4TwoBandInertia -- \
  C4TwoBandInertia.degreeFivePolynomial \
  C4TwoBandInertia.degreeSevenPolynomial \
  C4TwoBandInertia.degreeFiveDerivativeIdentity \
  C4TwoBandInertia.degreeSevenDerivativeIdentity \
  C4TwoBandInertia.degreeFiveErrorConstant \
  C4TwoBandInertia.degreeFiveBandErrorConstant \
  C4TwoBandInertia.degreeSevenErrorConstant \
  C4TwoBandInertia.sixthMomentExpansion \
  C4TwoBandInertia.seventhMomentExpansion \
  C4TwoBandInertia.eighthMomentExpansion \
  C4TwoBandInertia.degreeSevenSignatureCancellation \
  C4TwoBandInertia.squareDefectErrorGap \
  C4TwoBandInertia.squareDefectLowerGap \
  C4TwoBandInertia.squareDefectUpperGap \
  C4TwoBandInertia.squareDefectUpperSlack \
  C4TwoBandInertia.quarticRadicalGap \
  C4TwoBandInertia.quarticLowerMargin \
  C4TwoBandInertia.quarticUpperMargin \
  C4TwoBandInertia.quarticLowerReduction \
  C4TwoBandInertia.quarticUpperReduction \
  C4TwoBandInertia.exceptionalDelta8QuadraticCoefficient \
  C4TwoBandInertia.exceptionalDelta6QuadraticCoefficient \
  C4TwoBandInertia.exceptionalDelta8Length5LinearCoefficient \
  C4TwoBandInertia.exceptionalDelta8Length17LinearCoefficient \
  C4TwoBandInertia.exceptionalDelta6Length5LinearCoefficient \
  C4TwoBandInertia.exceptionalDelta6Length17LinearCoefficient \
  C4TwoBandInertia.exceptionalScaledErrorConstant \
  C4TwoBandInertia.rationalChildSquareGap \
  C4TwoBandInertia.rationalChildNotSquare \
  > "${EXPORT_FILE}"

cat > "${CONFIG_FILE}" <<EOF
{
  "export_file_path": "${EXPORT_FILE}",
  "use_stdin": false,
  "permitted_axioms": [
    "propext",
    "Classical.choice",
    "Quot.sound",
    "Lean.trustCompiler"
  ],
  "unpermitted_axiom_hard_error": false,
  "nat_extension": true,
  "string_extension": true,
  "print_success_message": true
}
EOF

"${NANODA_DIR}/target/release/nanoda_bin" "${CONFIG_FILE}"
