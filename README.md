# Certified bounds for the Mertens function: lim sup M(x)/√x > 1.92036 and lim inf M(x)/√x < −1.92053

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23298194.svg)](https://doi.org/10.5281/zenodo.23298194)

Let M(x) = Σ_{n≤x} μ(n) be the Mertens function. This repository proves

> **lim sup_{x→∞} M(x)/√x > 1.9203693129093421   and   lim inf_{x→∞} M(x)/√x < −1.9205369736317600,**

unconditionally. It improves the best previously published bounds, 1.826054 and −1.837625 (Hurst, 2018), on both sides.

| Year | Authors | lim sup M(x)/√x > | lim inf M(x)/√x < |
|---|---|---|---|
| 1985 | Odlyzko, te Riele | 1.06 | −1.009 |
| 2006 | Kotnik, te Riele | 1.218 | −1.229 |
| 2015 | Best, Trudgian | 1.6383 | −1.6383 |
| 2018 | Hurst | 1.826054 | −1.837625 |
| **2026** | **this work** | **1.920369** | **−1.920536** |

Best and Trudgian state their bounds with ≥ and ≤; the others are strict. Sources and locations: [THEOREM.md](THEOREM.md#references).

## Two certificates

The search was run twice: once for the main result (2026-10-09, without time evidence), and once on a fresh public challenge that nobody could know in advance (2026-10-11, with timestamps). Each certificate is a proof on its own; the main result is the stronger one.

| | Main certificate | Timed certificate |
|---|---|---|
| Found | 2026-10-09 | 2026-10-11, on drand round 6542728 |
| lim sup M(x)/√x > | 1.9203693129093421 | 1.918889 |
| lim inf M(x)/√x < | −1.9205369736317600 | −1.915021 |
| Files | [points/](points/), [results/](results/) | [timing/certificate.json](timing/certificate.json) |
| Time evidence | none | at most 65 min 52 s from the challenge; RFC 3161 timestamps and Bitcoin anchors ([Time evidence](#time-evidence)) |
| Machine | the same machine (time not verified) | AMD Ryzen 7 9700X, NVIDIA GeForce RTX 4070 SUPER, 31 GB RAM |
| Check | `python verify/verify_bound.py` (and `verify_bound_mpmath.py`) | `python timing/verify_timing.py --online` |

For the 2026-10-09 run we have only internal, unverified timing, and the step times listed there did not include a step of about 13 minutes. The only time we report is therefore the timestamped one.

## Check it yourself (main check about 25 seconds)

```bash
pip install numpy python-flint mpmath     # FLINT/Arb ball arithmetic; mpmath for the second verifier
cd verify && python verify_bound.py       # two rigorous enclosures, then "all requested claims verified: plus, minus"
python regenerate_zeros.py sample 20      # recomputes random zeros of ζ and compares them with the data
python verify_bound_mpmath.py            # optional: the same check with mpmath, no FLINT (about 30 minutes)
```

Expected output:
- h(y₊) ∈ [1.920369312909342168759… ± 5.1·10⁻⁵²]
- h(y₋) ∈ [−1.920536973631760094552… ± 4.5·10⁻⁵³]

`sha256sum -c SHA256SUMS.txt` checks every other file (all except .gitattributes and .gitignore).

## How the proof works

1. **Ingham's theorem** (1942; in the form of Odlyzko and te Riele 1985, and Hurst 2018, Theorem 4.2). For every real y,
   lim inf M(x)/√x ≤ h(y, N) ≤ lim sup M(x)/√x. Here h is a finite, explicitly weighted sum over the first N zeros of the Riemann zeta function.
2. **No hypothesis is needed.** If the Riemann hypothesis failed, or ζ had a multiple zero, both limits would be infinite.
3. **The certificate.** Two explicit points y₊ and y₋ (decimal numbers of about 4900 digits, in [points/](points/)) and the first 14 400 zeros of ζ with ζ′ at each, as rigorous balls (in [data/](data/)).
4. **The check.** h(y±, 14400) is evaluated in ball arithmetic. Every rounding error is enclosed, so the printed inequality is a proof.

Any point y gives a valid bound. The bound is simply whatever h evaluates to there, so verifying it does not require knowing how the points were found. The full statement, hypotheses and references are in [THEOREM.md](THEOREM.md). A checklist for independent validators, including how to re-check with other software, is in [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md).

## Contents

```
README.md               this page
THEOREM.md              statement, the theorem used with its hypotheses, proof, references
VALIDATION_GUIDE.md     how to check every part independently
points/                 y₊ and y₋ as exact decimal numbers
data/                   first 14 400 zeros γ and c = 1/(ρζ′(ρ)) as balls (16 384-bit computation), and their format
verify/verify_bound.py  rigorous evaluation of h(y±, 14400), checks the two claims
verify/verify_bound_mpmath.py  the same check with mpmath interval arithmetic (no FLINT)
verify/regenerate_zeros.py  regenerates or spot-checks the zero data with FLINT/Arb
results/                the certificates the verifier produced (JSON)
timing/                 the timed run: challenge, certificate, timestamps, CA certificates, verifiers
SHA256SUMS.txt          checksums of every other file (except .gitattributes and .gitignore)
```

## Time evidence

The search that found y₊ and y₋ was run once more, on a fresh challenge that nobody could know in advance. A certificate for that challenge existed **at most 3952 seconds (65 min 52 s)** after the challenge was published.

| | |
|---|---|
| Challenge | drand mainnet round 6542728, published 2026-10-11 10:01:00 UTC ([timing/beacon.json](timing/beacon.json)) |
| Committed before it | SHA-256 of the unpublished search code and of the zero-data file the search reads, timestamped 10:00:39 UTC ([timing/commit.json](timing/commit.json)). That file is a higher-precision version of the zero data, not the published `data/zeta_zeros_14400.npz`, so its hash differs from `SHA256SUMS.txt`; the certificate is checked with the published data. |
| Certificate | lim sup M(x)/√x > 1.918889 and lim inf M(x)/√x < −1.915021, at two points of the required form ([timing/certificate.json](timing/certificate.json)) |
| Timestamps | 11:06:51 UTC (FreeTSA) and 11:06:52 UTC (DigiCert), RFC 3161, one-second resolution. Both files are also anchored in Bitcoin through OpenTimestamps: commit.json in block 970906 (header time 10:13:16 UTC), certificate.json in block 970918 (11:15:22 UTC); check with `python timing/verify_ots.py commit.json.ots certificate.json.ots` from inside timing/, or at opentimestamps.org. |
| Machine (as reported) | AMD Ryzen 7 9700X (8 cores; 4 threads used in the main step), 31 GB RAM, NVIDIA GeForce RTX 4070 SUPER (used in one step), Windows 11 |

**How the challenge works.** The round's random value fixes two integers, M (14 digits) and r ([timing/derive_challenge.py](timing/derive_challenge.py)). Both certificate points must have the form y = r + M·z/1024 + d, with the same M and r, an integer z and |d| ≤ 1/20. For this round, a fixed point computed before the round has this form with probability below 2·10⁻¹² (at most 112 of the M possible values of r). Moving such a point into the form shifts it by up to M/2048 ≈ 3·10¹⁰, which changes every phase γ_i·y by more than 10¹¹ radians; unless the shift happens to be an approximate common period of the γ_i, the bound is lost.

**What this shows, and what it does not.** At most 65 min 52 s of wall-clock time (65 min 51 s by FreeTSA, 65 min 52 s by DigiCert) passed between an unpredictable challenge and a certified bound above Hurst's on both sides. That bound is slightly weaker than the main result, whose own search time is not covered. The evidence bounds only work done after the round: anything that does not depend on the challenge could have been prepared earlier. It does not show which or how much hardware was used; the machine above is as reported. The search code is not published. commit.json records its SHA-256 before the round, so a later release of that code could be matched to it, but the hash alone does not show that this code produced the certificate. The evidence rests on drand (no threshold of League of Entropy members revealed the round early) and on the clocks and keys of the two time-stamping authorities. Only commit.json and certificate.json carry independent timestamps; the challenge rule itself does not.

Check it: `python timing/verify_timing.py --online` (about 30 seconds). Without `--online` the beacon is only checked for internal consistency; this script does not verify its BLS signature.

## What is not included

The search procedure that found y₊ and y₋ is not part of this repository. It is not needed to verify the result.

## How this was made

This work is directed by Benjamin Weisz, who sets its goals, decides on publication and is responsible for its content. Nearly all of the code, computations and documentation were produced by an AI system (Claude, by Anthropic) working under that direction. The result does not rest on trusting the AI:
- the bound is checked by ball arithmetic;
- the zero data can be regenerated;
- the same claims are verified a second time with different software, mpmath interval arithmetic without FLINT (`verify/verify_bound_mpmath.py`);
- two independent referee passes re-derived the computation with separate code, checked the zero data against Odlyzko's published table, checked the theorem and its hypotheses against Odlyzko–te Riele (1985) and Hurst (2018) (Ingham (1942) was not accessible to them), and re-checked the timing evidence. The referees were AI agents, not human reviewers; this work has not yet been peer reviewed.

**Review status.** Unless a result is published in a peer-reviewed venue, its proofs have been checked only by the verification scripts and by AI agents; no human has reviewed them, and the owner does not count himself as a reviewer.

## Licence and citation

Code (verify/ and timing/*.py) under the Apache License 2.0, data and documentation under CC BY 4.0, third-party timing files under their issuers' terms: see [NOTICE](NOTICE). Please cite the Zenodo record: [doi:10.5281/zenodo.23298194](https://doi.org/10.5281/zenodo.23298194) for all versions, or [doi:10.5281/zenodo.23298195](https://doi.org/10.5281/zenodo.23298195) for version 1.0.0; the metadata is also in [CITATION.cff](CITATION.cff). Improved bounds, if any, will be released as new Zenodo versions of this record.
