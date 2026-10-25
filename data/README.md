# Data format: `zeta_zeros_14400.npz`

A NumPy `.npz` archive (load with `numpy.load(path, allow_pickle=False)`). All arrays have length 14400; index i − 1 corresponds to the zero ρ_i = 1/2 + iγ_i (i = 1 … 14400, ordered by height).

| Array | Content |
|---|---|
| `gamma` | γ_i, decimal midpoint (string, 9860 significant digits) |
| `gamma_rad` | radius of the ball for γ_i (string; all ≤ 8.6·10⁻⁹⁸⁴⁰) |
| `c_re`, `c_im` | real and imaginary parts of c_i = 1/(ρ_i ζ′(ρ_i)), decimal midpoints (strings, 60 significant digits) |
| `c_re_rad`, `c_im_rad` | radii (strings; all ≤ 1.9·10⁻¹²⁹) |
| `readme` | short description |

**Ball rule.** The true value lies in [mid − r − u, mid + r + u]. Here r is the stored radius and u is one unit in the last printed digit of the midpoint, which covers the decimal rounding of the midpoint.

**Computation.**
- Isolation: FLINT/Arb `acb.zeta_zeros(n, count)` at 16384 bits. It rigorously isolates the n-th zero on the critical line and verifies the zero count by Turing's method.
- Refinement to 32768 bits: one certified complex interval Newton step N(B) = s₀ − ζ(s₀)/ζ′(B) per zero. The inclusion N(B) ⊂ B was verified for every zero.
- ζ′(ρ) is the first-order Taylor coefficient of ζ at ρ; c = 1/(ρ ζ′(ρ)) is computed in ball arithmetic.

**Independent check.** `verify/regenerate_zeros.py` recomputes any subset of the zeros directly with `acb.zeta_zeros` at 33300 bits and checks it against the stored balls. The first 14400 ordinates can also be compared with published tables of zeros (e.g. A. Odlyzko's tables or the LMFDB) at lower precision.
