import Lake

open Lake DSL

package C4TwoBandInertia where
  version := v!"1.0.0"

require "leanprover-community" / "mathlib" @ git "v4.33.0"

@[default_target]
lean_lib C4TwoBandInertia
