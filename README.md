# Certified bounds for the Mertens function: lim sup M(x)/√x > 2.06175 and lim inf M(x)/√x < −2.06471

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23298194.svg)](https://doi.org/10.5281/zenodo.23298194)

Let M(x) = Σ_{n≤x} μ(n) be the Mertens function. This repository proves

> **lim sup_{x→∞} M(x)/√x > 2.0617536514585282   and   lim inf_{x→∞} M(x)/√x < −2.0647155435291726,**

unconditionally. It improves the best previously published bounds, 1.826054 and −1.837625 (Hurst, 2018), on both sides.

| Year | Authors | lim sup M(x)/√x > | lim inf M(x)/√x < |
|---|---|---|---|
| 1985 | Odlyzko, te Riele | 1.06 | −1.009 |
| 2006 | Kotnik, te Riele | 1.218 | −1.229 |
| 2015 | Best, Trudgian | 1.6383 | −1.6383 |
| 2018 | Hurst | 1.826054 | −1.837625 |
| 2026 | this work, version 1.0.0 (not peer reviewed) | 1.920369 | −1.920536 |
| **2026** | **this work, version 2.0.0** | **2.061753** | **−2.064715** |

Best and Trudgian state their bounds with ≥ and ≤; the others are strict. Sources and locations: [THEOREM.md](THEOREM.md#references).

**Both bounds exceed 2.** There are arbitrarily large x with M(x) > 2√x, and arbitrarily large x with M(x) < −2√x. So |M(x)| ≤ 2√x does not hold for all x. This answers the question in Pintz, arXiv:2608.24878, §2: "We even do not know today whether |M(x)| ≤ 2√x for all x". Like every proof by Ingham's method, this one does not exhibit an explicit such x.

## Check it yourself

```bash
pip install numpy python-flint mpmath     # FLINT/Arb ball arithmetic; mpmath for the second verifier
cd verify && python verify_bound.py       # two rigorous enclosures, then "all claims verified"
python verify_bound_mpmath.py             # the same check with mpmath interval arithmetic, no FLINT
python regenerate_zeros.py sample 10      # recomputes random zeros of ζ and compares them with the data
```

Measured on a desktop computer (AMD Ryzen 7 9700X): `verify_bound.py` about 90 s per point, `verify_bound_mpmath.py` about 3–3.5 min per point.

Expected output (Arb, 60 digits):
- h(y₊) ∈ [2.0617536514585282157830679158150887214080897256322036948605 ± 1.30·10⁻⁵⁹]
- h(y₋) ∈ [−2.0647155435291726514920038268907360718361372493174447898790 ± 5.59·10⁻⁵⁹]

The scripts write to `verify/output/` and never overwrite the shipped `results/`. `sha256sum -c SHA256SUMS.txt` checks every other file (all except .gitattributes and .gitignore).

## How the proof works

1. **Ingham's theorem** (1942; in the form of Odlyzko and te Riele 1985, and Hurst 2018, Theorem 4.2). For every real y,
   lim inf M(x)/√x ≤ h(y) ≤ lim sup M(x)/√x. Here h is a finite, explicitly weighted sum over the first N = 14 400 zeros of the Riemann zeta function.
2. **No hypothesis is needed.** If the Riemann hypothesis failed, or ζ had a multiple zero, both limits would be infinite.
3. **The certificate.** Two explicit points y₊ and y₋ (decimal numbers of about 9 600 digits, in [points/](points/)) and the first 14 400 zeros of ζ with ζ′ at each, as rigorous balls (in [data/](data/)).
4. **The check.** h(y±) is evaluated in ball arithmetic. Every rounding error is enclosed, so the printed inequality is a proof.

Any point y gives a valid bound. The bound is simply whatever h evaluates to there, so verifying it does not require knowing how the points were found. The full statement, hypotheses and references are in [THEOREM.md](THEOREM.md). A checklist for independent validators, including how to re-check with other software, is in [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md).

**Sign convention.** Hurst's printed formula for h is h(−y) in the notation used here. If you code his formula literally, evaluate it at −y± (see THEOREM.md).

## Contents

```
README.md               this page
THEOREM.md              statement, the theorem used with its hypotheses, proof, references
VALIDATION_GUIDE.md     how to check every part independently
points/                 y₊ and y₋ as exact decimal numbers
data/                   first 14 400 zeros γ and c = 1/(ρζ′(ρ)) as balls (32 768-bit computation), and their format
verify/verify_bound.py  rigorous evaluation of h(y±) with FLINT/Arb; checks the two claims
verify/verify_bound_mpmath.py  the same check with mpmath interval arithmetic (different library, no shared code)
verify/regenerate_zeros.py  regenerates or spot-checks the zero data with FLINT/Arb
results/                the certificates the two verifiers produced (JSON)
SHA256SUMS.txt          checksums of every other file (except .gitattributes and .gitignore)
```

## Earlier version

Version 1.0.0 (2026-10-11) proved lim sup M(x)/√x > 1.9203693129093421 and lim inf M(x)/√x < −1.9205369736317600. It also contained a second, timed certificate (1.918889 / −1.915021) with RFC 3161 and OpenTimestamps evidence that it was produced at most 65 min 52 s after an unpredictable public challenge. Version 1.0.0, including the timing evidence and its verifiers, stays available unchanged at the git tag [v1.0.0](https://github.com/wbeni95/mertens-function-bounds/tree/v1.0.0) and as Zenodo version [doi:10.5281/zenodo.23298195](https://doi.org/10.5281/zenodo.23298195).

## What is not included

The search procedure that found y₊ and y₋ is not part of this repository. It is not needed to verify the result.

## How this was made

This work is directed by Benjamin Weisz, who sets its goals, decides on publication and is responsible for its content. Nearly all of the code, computations and documentation were produced by an AI system (Claude, by Anthropic) working under that direction. The result does not rest on trusting the AI:
- the bound is checked by ball arithmetic;
- the same claims are verified a second time with a different library and no shared code (mpmath interval arithmetic, `verify/verify_bound_mpmath.py`);
- both verifiers were run again on a second installation, with results identical to the shipped certificates;
- the zero data can be regenerated or spot-checked (`verify/regenerate_zeros.py`), and compared with published tables of zeros.

**Review status.** This work has not been peer reviewed. Its proofs have been checked only by the verification scripts and by AI agents; no human has reviewed them, and the owner does not count himself as a reviewer.

## Licence and citation

Code (verify/) under the Apache License 2.0; data and documentation under CC BY 4.0: see [NOTICE](NOTICE). Please cite the Zenodo record: [doi:10.5281/zenodo.23298194](https://doi.org/10.5281/zenodo.23298194) for all versions; the metadata is also in [CITATION.cff](CITATION.cff).
