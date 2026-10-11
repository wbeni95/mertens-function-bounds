# Data format: `zeta_zeros_14400.npz`

A NumPy `.npz` archive. All arrays have length 14400; index i − 1 corresponds to the zero ρ_i = 1/2 + iγ_i (i = 1 … 14400, ordered by height).

| Array | Content |
|---|---|
| `gamma` | γ_i, decimal midpoint (string, 4927 significant digits) |
| `gamma_rad` | radius of the ball for γ_i (string) |
| `c_re`, `c_im` | real and imaginary parts of c_i = 1/(ρ_i ζ′(ρ_i)), decimal midpoints (strings, 60 significant digits) |
| `c_re_rad`, `c_im_rad` | radii (strings) |
| `readme` | short description |

**Ball rule.** The true value lies in [mid − r − u, mid + r + u]. Here r is the stored radius and u is one unit in the last printed digit of the midpoint, which covers the decimal rounding of the midpoint.

**Computation.** FLINT/Arb at 16384-bit precision:
- zeros via `acb.zeta_zeros(n, count)`, which rigorously isolates the n-th zero;
- ζ′(ρ) via the first-order Taylor coefficient of ζ at ρ;
- c = 1/(ρ ζ′(ρ)) in ball arithmetic.
