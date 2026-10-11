# Improved bounds for M(x)/√x

*Benjamin Weisz (https://github.com/wbeni95). Version 1.0.0, 2026-10-11. Licence: see NOTICE.*

## Statement

Let M(x) = Σ_{n ≤ x} μ(n) be the Mertens function and q(x) = M(x)/√x. Then

> **lim sup_{x→∞} q(x) > 1.9203693129093421**  and  **lim inf_{x→∞} q(x) < −1.9205369736317600.**

The previously best published bounds known to us are lim sup q(x) > 1.826054 and lim inf q(x) < −1.837625 (G. Hurst, 2018). Kim and Nguyen (arXiv:2502.21021v1, §4.2, p. 14; journal version Res. Number Theory 11 (2025), Paper No. 3, not checked) still refer to them as the record, stated there as ≥ and ≤.

## Notation

- 0 < γ_1 < γ_2 < … < γ_N are the ordinates of the first N nontrivial zeros of ζ(s) in the upper half-plane, with N = 14400 and γ_N ≈ 13550.64.
  - All these zeros lie on the critical line and are simple (van de Lune, te Riele and Winter 1986, for the first 1.5·10⁹ zeros). So ρ_i = 1/2 + iγ_i for i ≤ N.
- c_i = 1/(ρ_i ζ′(ρ_i)).
- f(t) = (1 − t) cos(πt) + sin(πt)/π for 0 ≤ t ≤ 1. This is the Jurkat–Peyerimhoff kernel: f(0) = 1, f(t) > 0 for 0 ≤ t < 1, and f(1) = 0.
- For a real y:

  **h(y, N) = 2 Σ_{i=1}^{N} f(γ_i/γ_N) · Re( c_i · e^{iγ_i y} ) = 2 Σ_{i=1}^{N} f(γ_i/γ_N) · |c_i| · cos(γ_i y − arg(ρ_i ζ′(ρ_i))).**

  Each term is the smoothed contribution of the zero pair ρ_i, ρ̄_i in the explicit formula, since x^ρ/(ρζ′(ρ)) + conjugate = 2√x·Re(c_i e^{iγ_i log x}).

### Sign convention: please read

- This form, with phase −arg(ρζ′(ρ)), is the one in Odlyzko and te Riele (1985), formulas (2.20)–(2.21).
- Hurst (2018; arXiv v2, p. 5, eq. (3) and the display defining h(y, N)) prints the same function as cos(γ_i y + ψ_i) with ψ_i = arg(ρ_i ζ′(ρ_i)). That is h(−y, N) in our notation: a sign slip that does not affect the validity of his bounds, because the theorem below holds for every real y. The journal version was not checked.
- **If you code Hurst's printed formula literally, evaluate it at −y±, not at y±.** At +y± it gives unrelated values, about −0.767 and +0.764.

## The theorem used

**Theorem (Ingham 1942; Odlyzko–te Riele 1985, Theorem on p. 144 with the kernel (4.1); Hurst 2018, Theorem 4.2 of arXiv v2).** For every real y,

  lim inf_{x→∞} q(x) ≤ h(y, N) ≤ lim sup_{x→∞} q(x).

**Hypotheses, as in Odlyzko–te Riele.** For the weight k(t) on the zeros and its Fourier transform K(y):
- k(t) = 0 for |t| ≥ T, with T = γ_N, and k(0) = 1;
- K ∈ C², K ≥ 0, K even, and K(y) = O((1 + y²)⁻¹);
- the zeros with |γ| < T lie on the critical line and are simple.

The Jurkat–Peyerimhoff weight k(t) = f(|t|/T) satisfies these conditions:
- It vanishes for |t| ≥ T, and k(0) = 1.
- In Odlyzko–te Riele's normalisation (2.9) its transform is K(y) = (T/π)·φ̂(Ty)² with φ̂(ω) = 2π cos(ω/2)/(π² − ω²). This is nonnegative, even, C², and O(y⁻⁴).
- Equivalently, the weight is the autocorrelation 2·(φ ∗ φ) of φ(t) = cos(πt) on [−½, ½], suitably scaled.
- The zero conditions hold for i ≤ N (see Notation).

**Why the statement is unconditional.** If the Riemann hypothesis failed, or ζ had a multiple zero, then lim sup q(x) = +∞ and lim inf q(x) = −∞ (Odlyzko–te Riele, p. 141), and the bounds hold trivially. Otherwise the theorem above applies.

## Proof of the statement

We apply the theorem with N = 14400 at the two points
- y₊ = the decimal number in `points/y_plus.txt` (y₊ ≈ −5.0283·10^4870),
- y₋ = the decimal number in `points/y_minus.txt` (y₋ ≈ −1.8902·10^4870),

each with 4871 integer digits and 32 fractional digits.

h(y±, 14400) was evaluated rigorously in ball arithmetic (Arb, 16600-bit working precision) from certified enclosures of γ_i and c_i (i ≤ 14400), with `verify/verify_bound.py`:

| Point | h(y, 14400): rigorous enclosure (Arb, `str(60, radius=True)`) | Consequence |
|---|---|---|
| y₊ | [1.920369312909342168759269842741009965003445539842055 ± 5.06·10⁻⁵²] | lim sup q(x) ≥ h(y₊, 14400) > 1.9203693129093421 |
| y₋ | [−1.9205369736317600945527269900033846829567417080526514 ± 4.47·10⁻⁵³] | lim inf q(x) ≤ h(y₋, 14400) < −1.9205369736317600 |

The same two claims are also verified with different software: `verify/verify_bound_mpmath.py` evaluates h(y±, 14400) in mpmath interval arithmetic (16600 bits, no FLINT), and its enclosures lie inside the Arb balls above.

**Input data** (`data/zeta_zeros_14400.npz`):
- γ_i (4927 significant digits) and c_i (60 digits), as decimal midpoints with rigorous radii. They were computed with FLINT/Arb at 16384 bits: rigorous isolation of the n-th zero by `acb.zeta_zeros`, and ζ′(ρ_i) from the Taylor expansion of ζ at ρ_i.
- One unit in the last printed decimal digit is added to every radius, to cover the decimal rounding of the midpoints.
- The data can be regenerated or spot-checked with `verify/regenerate_zeros.py`, or checked with any other rigorous software (see `VALIDATION_GUIDE.md`).

**Precision.** |y±| ≈ 10^4870 and γ_i < 1.4·10⁴. The data determine each phase γ_i·y to about 4927 − 4875 ≈ 52 decimal digits, which is consistent with the rigorous radii of h (≤ 5.1·10⁻⁵²).

**How y± were found.** The certificate does not depend on it: the theorem holds for every real y, and the bound is whatever h(y, N) evaluates to at the given points. The search procedure is not part of this package.

## References

1. A. E. Ingham, *On two conjectures in the theory of numbers*, Amer. J. Math. 64 (1942), 313–319.
2. A. M. Odlyzko and H. J. J. te Riele, *Disproof of the Mertens conjecture*, J. reine angew. Math. 357 (1985), 138–160.
3. G. Hurst, *Computations of the Mertens function and improved bounds on the Mertens conjecture*, Math. Comp. 87 (2018), no. 310, 1013–1028, doi:10.1090/mcom/3275; arXiv:1610.08551 (theorem numbering as in arXiv v2).
4. J. van de Lune, H. J. J. te Riele and D. T. Winter, *On the zeros of the Riemann zeta function in the critical strip. IV*, Math. Comp. 46 (1986), no. 174, 667–681.
5. S. Kim and P. Q. Nguyen, *On counterexamples to the Mertens conjecture*, Res. Number Theory 11 (2025), no. 1, Paper No. 3, doi:10.1007/s40993-024-00603-9 (published online 4 Dec 2024); arXiv:2502.21021.
6. F. Johansson, *Arb: efficient arbitrary-precision midpoint-radius interval arithmetic*, IEEE Trans. Comput. 66 (2017), no. 8, 1281–1292.
7. The FLINT team, *FLINT: Fast Library for Number Theory* (includes Arb), https://flintlib.org.
8. T. Kotnik and H. te Riele, *The Mertens conjecture revisited*, in: Algorithmic Number Theory (ANTS VII), Lecture Notes in Comput. Sci. 4076, Springer, 2006, 156–167, doi:10.1007/11792086_12.
9. D. G. Best and T. S. Trudgian, *Linear relations of zeroes of the zeta-function*, Math. Comp. 84 (2015), no. 294, 2047–2058, doi:10.1090/S0025-5718-2014-02916-5; arXiv:1209.3843.

**Sources of the table in README.md.**
- 1.06 / −1.009: Odlyzko–te Riele [2]; checked in their preprint (CWI Report NM-R8412, 1984, p. 2 and Table 3, p. 14); the journal page was not checked.
- 1.218 / −1.229: Kotnik–te Riele [8], abstract.
- ≥ 1.6383 / ≤ −1.6383: Best–Trudgian [9], Theorem 1 (arXiv v3, p. 2).
- 1.826054 / −1.837625: Hurst [3], abstract and Theorem 6.1 (arXiv v2, p. 11).
