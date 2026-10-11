# Validation guide (for an independent validator)

The claim (`THEOREM.md`) rests on three things:
1. a published theorem (Ingham);
2. the zero data;
3. a finite, rigorous computation.

Each can be checked independently.

## 1. Integrity
- `sha256sum -c SHA256SUMS.txt`: all files must match.

## 2. The mathematical argument
- Check Ingham's theorem and its use, as stated in `THEOREM.md`, against the sources:
  - Hurst 2018, Theorem 4.2;
  - Odlyzko–te Riele 1985;
  - Ingham 1942.
- **Sign convention (important).** h(y, N) here uses Re(c_i e^{iγ_i y}) = |c_i| cos(γ_i y − arg(ρ_i ζ′(ρ_i))), as in Odlyzko–te Riele (2.20)–(2.21).
  - Hurst's printed formula (arXiv v2, p. 5, eq. (3) and the display defining h(y, N)), cos(γ_i y + ψ_i) with ψ_i = arg(ρ_i ζ′(ρ_i)), equals h(−y, N).
  - If you implement Hurst's printed form, evaluate it at −y±.
- Check that h(y, N) in `verify_bound.py` matches the definition:
  - kernel f(t) = (1−t)cos(πt) + sin(πt)/π;
  - argument γ_i/γ_N;
  - terms 2·Re(c_i e^{iγ_i y});
  - c_i = 1/(ρ_i ζ′(ρ_i)).
- Points to confirm:
  - **Hypotheses:** check those of Odlyzko–te Riele's theorem (p. 144):
    - the weight vanishes for |t| ≥ T and k(0) = 1;
    - the transform K is C², nonnegative, even and O((1+y²)⁻¹);
    - the zeros with |γ| < γ_N are simple and on the line (van de Lune–te Riele–Winter 1986).
  - **Unconditional:** if RH fails or a multiple zero exists, then lim sup q = +∞ and lim inf q = −∞ (Odlyzko–te Riele p. 141).
  - **Zero list:** the zeros used must be exactly the first N = 14400 zeros with positive imaginary part, ordered by height. Completeness of the list follows from the rigorous zero counting in FLINT/Arb's `zeta_zeros`. It can be cross-checked against tables of zeros, e.g. the LMFDB or Odlyzko's tables, at lower precision.

## 3. The data
- `python verify/regenerate_zeros.py sample K`: recompute random zeros and compare with the stored balls.
- `python verify/regenerate_zeros.py range i0 i1`: recompute a contiguous block.
- `python verify/regenerate_zeros.py full out.npz`: regenerate everything (several CPU-hours). Then run `verify_bound.py` on the regenerated file: replace `data/zeta_zeros_14400.npz` with it.
- Optional, strongest: compute γ_i and ζ′(ρ_i) with different software (e.g. mpmath at high precision, PARI/GP, or Mathematica) for a sample of indices.

## 4. The computation
- `python verify/verify_bound.py`. Expected: the enclosures in `README.md` (Arb `str(60, radius=True)`, radii ≤ 5.1e-52), and "all requested claims verified: plus, minus". Output goes to `verify/output/`; the shipped `results/` are not touched.
- Optional, strongest: re-implement h(y, N) independently (e.g. PARI/GP, Mathematica, Arb in C, or mpmath with ≥ 16600-bit precision) and evaluate it at the given decimal points y±.
  - The values must agree with the midpoints in `results/` to many digits.
  - `python verify/verify_bound_mpmath.py` does this with mpmath interval arithmetic (no FLINT; about 15 minutes per point in pure-Python mpmath). Its enclosures lie inside the Arb balls.
  - Note that γ_i·y needs ~4900 significant digits (|y±| ≈ 10^4870).

## 5. Timing evidence (not part of the proof)
- `python timing/verify_timing.py --online` re-checks the drand beacon, the challenge (M, r), the required form of the timed points, their rigorous bounds and the four RFC 3161 tokens.
- README.md, section "Time evidence", states what this evidence shows and what it does not.

## 6. What is deliberately not included
The method that produced the points y± is not part of the package. It is not needed: the inequality lim inf q ≤ h(y, N) ≤ lim sup q holds for every real y, so any point with a large |h| certifies a bound.
