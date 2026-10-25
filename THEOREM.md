# Improved bounds for M(x)/√x

*Benjamin Weisz (https://github.com/wbeni95), version 2.0.0, 2026-10-25. Licence: CC BY 4.0 (see NOTICE).*

## Statement

Let M(x) = Σ_{n ≤ x} μ(n) be the Mertens function and q(x) = M(x)/√x. Then

> **lim sup_{x→∞} q(x) > 2.0617536514585282**  and  **lim inf_{x→∞} q(x) < −2.0647155435291726.**

In particular, lim sup |q(x)| > 2.0647 and both one-sided bounds exceed 2: there are arbitrarily large x with M(x) > 2√x, and arbitrarily large x with M(x) < −2√x. So the inequality |M(x)| ≤ 2√x does not hold for all x. This answers a question raised by Pintz [11, §2]: "We even do not know today whether |M(x)| ≤ 2√x for all x". Like every proof by Ingham's method, ours does not exhibit an explicit such x.

The best previously published bounds known to us are lim sup q(x) > 1.826054 and lim inf q(x) < −1.837625 (G. Hurst, Math. Comp. 2018). Kim and Nguyen (Research in Number Theory, 2025) still refer to them as the record. This result supersedes version 1.0.0 of this work (1.9203693129093421 and −1.9205369736317600; Zenodo, doi:10.5281/zenodo.23298195), which was not peer reviewed.

| Source | lim sup q(x) > | lim inf q(x) < |
|---|---|---|
| Odlyzko–te Riele 1985 | 1.06 | −1.009 |
| Kotnik–te Riele 2006 | 1.218 | −1.229 |
| Best–Trudgian 2015 | 1.6383 | −1.6383 |
| Hurst 2018 | 1.826054 | −1.837625 |
| This work, version 1.0.0 (2026-10-11; not peer reviewed) | 1.9203693129093421 | −1.9205369736317600 |
| **This work, version 2.0.0** | **2.0617536514585282** | **−2.0647155435291726** |

## Notation

- 0 < γ_1 < γ_2 < … < γ_N are the ordinates of the first N nontrivial zeros of ζ(s) in the upper half-plane, with N = 14400 and γ_N ≈ 13550.64.
  - All these zeros lie on the critical line and are simple (van de Lune, te Riele and Winter 1986, for the first 1.5·10⁹ zeros). So ρ_i = 1/2 + iγ_i for i ≤ N.
- c_i = 1/(ρ_i ζ′(ρ_i)).
- f(t) = (1 − t) cos(πt) + sin(πt)/π for 0 ≤ t ≤ 1. This is the Jurkat–Peyerimhoff kernel: f(0) = 1, f(t) > 0 for 0 ≤ t < 1, and f(1) = 0.
- T = γ_N. For a real y:

  **h(y) = 2 Σ_{i=1}^{N} f(γ_i/T) · Re( c_i · e^{iγ_i y} ) = 2 Σ_{i=1}^{N} f(γ_i/T) · |c_i| · cos(γ_i y − arg(ρ_i ζ′(ρ_i))).**

  The term i = N vanishes because f(1) = 0, so the sum runs over the zeros with 0 < γ < T, as in Hurst's theorem. Each term is the smoothed contribution of the zero pair ρ_i, ρ̄_i in the explicit formula, since x^ρ/(ρζ′(ρ)) + conjugate = 2√x·Re(c_i e^{iγ_i log x}).

### Sign convention: please read

- This form, with phase −arg(ρζ′(ρ)), is the one in Odlyzko and te Riele (1985), formulas (2.20)–(2.21).
- Hurst (2018) prints the same function as cos(γ_i y + ψ_i) with ψ_i = arg(ρ_i ζ′(ρ_i)). That is h(−y) in our notation; it is a sign slip that does not affect his results, because the theorem below holds for every real y.
- **If you code Hurst's printed formula literally, evaluate it at −y±, not at y±.**

## The theorem used

**Theorem (Ingham 1942; Odlyzko–te Riele 1985, Theorem on p. 144 with the kernel (4.1); Hurst 2018, Theorem 4.2 of arXiv v2).** For every real y,

  lim inf_{x→∞} q(x) ≤ h(y) ≤ lim sup_{x→∞} q(x).

**Hypotheses, as in Odlyzko–te Riele.** For the weight k(t) on the zeros and its Fourier transform K(y):
- k(t) = 0 for |t| ≥ T, and k(0) = 1;
- K ∈ C², K ≥ 0, K even, and K(y) = O((1 + y²)⁻¹);
- the zeros with |γ| < T lie on the critical line and are simple.

The Jurkat–Peyerimhoff weight k(t) = f(|t|/T) satisfies these conditions:
- It vanishes for |t| ≥ T, and k(0) = 1.
- In Odlyzko–te Riele's normalisation (2.9) its transform is K(y) = (T/π)·φ̂(Ty)² with φ̂(ω) = 2π cos(ω/2)/(π² − ω²). This is nonnegative, even, C², and O(y⁻⁴).
- Equivalently, the weight is the autocorrelation 2·(φ ∗ φ) of φ(t) = cos(πt) on [−½, ½], suitably scaled.
- The zero conditions hold for i ≤ N (see Notation).

**Why the statement is unconditional.** If the Riemann hypothesis failed, or ζ had a multiple zero, then lim sup q(x) = +∞ and lim inf q(x) = −∞ (Odlyzko–te Riele, p. 141), and the bounds hold trivially. Otherwise the theorem above applies.

## Proof of the statement

We apply the theorem with N = 14400 and T = γ_N at the two points
- y₊ = the decimal number in `points/y_plus.txt` (y₊ ≈ −1.2705·10^9625; 9626 integer digits and 32 fractional digits),
- y₋ = the decimal number in `points/y_minus.txt` (y₋ ≈ 4.9566·10^9626; 9627 integer digits and 32 fractional digits).

h(y±) was evaluated rigorously in ball arithmetic from certified enclosures of γ_i and c_i (i ≤ N), with two independent programs:
- `verify/verify_bound.py` (FLINT/Arb);
- `verify/verify_bound_mpmath.py` (mpmath interval arithmetic).

| Point | h(y): rigorous enclosure (Arb, `verify_bound.py`) | Consequence |
|---|---|---|
| y₊ | [2.0617536514585282157830679158150887214080897256322036948605 ± 1.30·10⁻⁵⁹] | lim sup q(x) ≥ h(y₊) > 2.0617536514585282 |
| y₋ | [−2.0647155435291726514920038268907360718361372493174447898790 ± 5.59·10⁻⁵⁹] | lim inf q(x) ≤ h(y₋) < −2.0647155435291726 |

The mpmath interval evaluation gives enclosures that agree with these (see `results/`).

**Input data** (`data/zeta_zeros_14400.npz`):
- γ_i (9860 significant digits, radii ≤ 8.6·10⁻⁹⁸⁴⁰) and c_i (60 significant digits, radii ≤ 1.9·10⁻¹²⁹), as decimal midpoints with rigorous radii.
- One unit in the last printed decimal digit is added to every radius, to cover the decimal rounding of the midpoints.
- How the data were computed:
  - each zero was rigorously isolated and computed to 16384 bits with FLINT/Arb (`acb.zeta_zeros`, which verifies the zero count by Turing's method);
  - each was then refined to 32768 bits by one certified interval Newton step, N(B) = s₀ − ζ(s₀)/ζ′(B). The inclusion N(B) ⊂ B proves that the box B contains exactly one zero of ζ, by the integral form of the mean value theorem on the convex box B;
  - c_i = 1/(ρ_i ζ′(ρ_i)) was computed in ball arithmetic.
- The data can be regenerated or spot-checked independently with `verify/regenerate_zeros.py`, which calls `acb.zeta_zeros` directly at 33300 bits. They can also be checked with any other rigorous software (see `VALIDATION_GUIDE.md`).

**Precision.** |y±| < 10^9627 and γ_i < 1.4·10⁴. With the stored radii, every phase γ_i·y± is known to about 10⁻²¹², so the phases are far more accurate than needed. The final radii (≈ 10⁻⁵⁹) come mainly from the 60-digit precision of the c_i.

**How y± were obtained.** The certificate does not depend on it: the theorem holds for every real y, and the bound is whatever h evaluates to at the given points. The procedure that produced y± is not part of this package.

## References

1. A. E. Ingham, *On two conjectures in the theory of numbers*, Amer. J. Math. 64 (1942), 313–319.
2. A. M. Odlyzko and H. J. J. te Riele, *Disproof of the Mertens conjecture*, J. reine angew. Math. 357 (1985), 138–160.
3. T. Kotnik and H. te Riele, *The Mertens conjecture revisited*, in: Algorithmic Number Theory (ANTS VII), Lecture Notes in Comput. Sci. 4076, Springer, 2006, 156–167.
4. D. G. Best and T. S. Trudgian, *Linear relations of zeroes of the zeta-function*, Math. Comp. 84 (2015), 2047–2058; arXiv:1209.3843.
5. G. Hurst, *Computations of the Mertens function and improved bounds on the Mertens conjecture*, Math. Comp. 87 (2018), no. 310, 1013–1028, doi:10.1090/mcom/3275; arXiv:1610.08551 (theorem numbering as in arXiv v2).
6. J. van de Lune, H. J. J. te Riele and D. T. Winter, *On the zeros of the Riemann zeta function in the critical strip. IV*, Math. Comp. 46 (1986), no. 174, 667–681.
7. S. Kim and P. Q. Nguyen, *On counterexamples to the Mertens conjecture*, Research in Number Theory 11 (2025), article 3, doi:10.1007/s40993-024-00603-9; arXiv:2502.21021.
8. F. Johansson, *Arb: efficient arbitrary-precision midpoint-radius interval arithmetic*, IEEE Trans. Comput. 66 (2017), no. 8, 1281–1292.
9. The FLINT team, *FLINT: Fast Library for Number Theory* (includes Arb), https://flintlib.org.
10. The mpmath development team, *mpmath: a Python library for arbitrary-precision floating-point arithmetic*, https://mpmath.org.
11. J. Pintz, *Oscillation of partial sums of the Möbius function and zeros of Riemann's zeta function*, arXiv:2608.24878 (v2, 2026), §2.
