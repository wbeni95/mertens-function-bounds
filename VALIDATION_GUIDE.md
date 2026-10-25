# Validation guide (for an independent validator)

The claim (`THEOREM.md`) rests on three things:
1. a published theorem (Ingham; in the form of Hurst 2018, Theorem 4.2);
2. the zero data;
3. a finite, rigorous computation.

Each can be checked independently.

## 1. Integrity
- `sha256sum -c SHA256SUMS.txt`: all files must match.

## 2. The mathematical argument
- Check Ingham's theorem and its use, as stated in `THEOREM.md`, against the sources:
  - Hurst 2018, Theorem 4.2 (arXiv v2 numbering);
  - Odlyzko–te Riele 1985;
  - Ingham 1942.
- **Sign convention (important).** h(y) here uses Re(c_i e^{iγ_i y}) = |c_i| cos(γ_i y − arg(ρ_i ζ′(ρ_i))), as in Odlyzko–te Riele (2.20)–(2.21).
  - Hurst's printed formula, cos(γ_i y + ψ_i) with ψ_i = arg(ρ_i ζ′(ρ_i)), equals h(−y).
  - If you implement Hurst's printed form, evaluate it at −y±.
- Check that h(y) in both verification scripts matches the definition:
  - kernel f(t) = (1−t)cos(πt) + sin(πt)/π;
  - argument γ_i/T with T = γ_N, N = 14400;
  - terms 2·Re(c_i e^{iγ_i y});
  - c_i = 1/(ρ_i ζ′(ρ_i)).
- Points to confirm:
  - **Hypotheses:** check those of Odlyzko–te Riele's theorem (p. 144):
    - the weight vanishes for |t| ≥ T and k(0) = 1;
    - the transform K is C², nonnegative, even and O((1+y²)⁻¹);
    - the zeros with |γ| < γ_N are simple and on the line (van de Lune–te Riele–Winter 1986).
  - **Unconditional:** if RH fails or a multiple zero exists, then lim sup q = +∞ and lim inf q = −∞ (Odlyzko–te Riele p. 141).
  - **Zero list:** the zeros used must be exactly the first N = 14400 zeros with positive imaginary part, ordered by height.
    - Completeness follows from the rigorous zero counting (Turing's method) in FLINT/Arb's `zeta_zeros`.
    - It can be cross-checked against tables of zeros at lower precision, e.g. the LMFDB or A. Odlyzko's tables.

## 3. The data
- `python verify/regenerate_zeros.py sample K [seed]`: recompute K random zeros (plus i = 1 and i = 14400) and compare with the stored balls.
- `python verify/regenerate_zeros.py range i0 i1`: recompute a contiguous block.
- `python verify/regenerate_zeros.py full out.npz`: regenerate everything. This is long at 33300 bits: we measured 7–17 s per zero (zero plus ζ′), so on the order of two CPU-days in total. Afterwards, run the verification scripts on the regenerated file in place of `data/zeta_zeros_14400.npz`.
- Optional, strongest: compute γ_i and ζ′(ρ_i) for a sample of indices with different software, e.g. mpmath at high precision, PARI/GP, or Mathematica. About 9700 correct significant digits of γ_i are needed (see §4).

## 4. The computation
- `python verify/verify_bound.py` (FLINT/Arb). Expected: the enclosures in `README.md` and "all claims verified". Output goes to `verify/output/`; the shipped `results/` are not touched.
- `python verify/verify_bound_mpmath.py` (mpmath interval arithmetic, independent code and library). Expected: enclosures that contain the Arb midpoints, and "all claims verified".
- Optional, strongest: re-implement h(y) yourself (e.g. PARI/GP, Mathematica, Arb in C) and evaluate it at the given decimal points y±.
  - Note that |y±| ≈ 10^9626, so each product γ_i·y needs about 9700 significant digits before it is taken modulo 2π. After that, about 30 digits suffice for each term.
  - Use T = γ_N exactly, as stated. Other admissible choices of T change h slightly.

## 5. What is deliberately not included
The procedure that produced the points y± is not part of the package. It is not needed: the inequality lim inf q ≤ h(y) ≤ lim sup q holds for every real y, so any point with a large |h(y)| certifies a bound.
