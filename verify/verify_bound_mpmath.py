"""Independent verification of the bounds in THEOREM.md with mpmath interval arithmetic (no FLINT/Arb).

This evaluates the same function as verify_bound.py, with different software, so that the result does not rest on the
library that produced the zero data:

    h(y, N) = 2 * sum_{i=1}^{N} f(gamma_i / gamma_N) * Re( c_i * exp(i * gamma_i * y) ),
    f(t)    = (1 - t) cos(pi t) + sin(pi t) / pi,

for N = 14400 at the points in ../points/, in mpmath.iv at 16600 bits. Every input is an interval: each stored decimal
midpoint is widened by its stored radius plus one unit in its last printed digit (the ball rule of data/README.md).
The final comparison with the claimed threshold is exact (rational endpoints).

Usage:   python verify_bound_mpmath.py            (both points; about 15 minutes per point in pure-Python mpmath)
         python verify_bound_mpmath.py plus|minus
Output:  verify/output/mpmath_<point>.json; prints the enclosure and whether each requested claim holds.
Requirements: Python 3.11+, numpy (to read the .npz file), mpmath 1.3+.
The rigour rests on mpmath.iv's outward-rounded interval operations."""
import json, os, sys, time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from mpmath.libmp import to_str

sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
PREC = 16600
N = 14400
CLAIMS = {"plus": ("lower", "1.9203693129093421"), "minus": ("upper", "-1.9205369736317600")}


def dec_to_fraction(s):
    """Exact rational value of a decimal string such as '-12.345e-6'."""
    s = s.strip().lower()
    mant, _, ex = s.partition("e")
    e = int(ex) if ex else 0
    neg = mant.startswith("-")
    ip, _, fp = mant.lstrip("+-").partition(".")
    v = Fraction(int((ip or "0") + fp)) * Fraction(10) ** (e - len(fp))
    return -v if neg else v


def ulp_exp(s):
    """Exponent k such that one unit in the last printed digit of the decimal string s is 10^k."""
    s = s.strip().lower()
    mant, _, ex = s.partition("e")
    return (int(ex) if ex else 0) - len(mant.partition(".")[2])


def ball(mid, rad):
    """Interval [mid - (rad + u), mid + (rad + u)], u = one unit in the last printed digit, rounded outward."""
    e = (iv.mpf(rad) + iv.mpf("1e%d" % ulp_exp(mid))).b
    return iv.mpf(mid) + iv.mpf([-e, e])


def mpf_to_fraction(x):
    sign, man, exp, bc = x
    if bc < 0:
        raise ValueError("non-finite interval endpoint")
    v = Fraction(man) * Fraction(2) ** exp if exp >= 0 else Fraction(man, 1 << (-exp))
    return -v if sign else v


def main():
    which = sys.argv[1:] or ["plus", "minus"]
    iv.prec = PREC
    z = np.load(os.path.join(PKG, "data", "zeta_zeros_14400.npz"), allow_pickle=False)
    D = {k: [str(s) for s in z[k]] for k in ["gamma", "gamma_rad", "c_re", "c_im", "c_re_rad", "c_im_rad"]}
    G = [ball(D["gamma"][i], D["gamma_rad"][i]) for i in range(N)]
    CR = [ball(D["c_re"][i], D["c_re_rad"][i]) for i in range(N)]
    CI = [ball(D["c_im"][i], D["c_im_rad"][i]) for i in range(N)]
    GN, PI = G[N - 1], iv.pi
    results = {}
    for w in which:
        t0 = time.time()
        Y = iv.mpf(open(os.path.join(PKG, "points", f"y_{w}.txt")).read().strip())
        tot = iv.mpf(0)
        for i in range(N):
            t = G[i] / GN
            f = (1 - t) * iv.cos(PI * t) + iv.sin(PI * t) / PI
            th = G[i] * Y
            tot = tot + 2 * f * (CR[i] * iv.cos(th) - CI[i] * iv.sin(th))
        a, b = tot._mpi_
        A, B = mpf_to_fraction(a), mpf_to_fraction(b)
        kind, claim = CLAIMS[w]
        ok = (A > dec_to_fraction(claim)) if kind == "lower" else (B < dec_to_fraction(claim))
        mp.prec = 400
        rec = {"point": w, "N": N, "precision_bits": PREC, "terms": N, "interval_cos_sin_calls": 4 * N,
               "lower": to_str(a, 60), "upper": to_str(b, 60),
               "radius": mp.nstr(mp.mpf((B - A).numerator) / (B - A).denominator / 2, 3),
               "claim": f"h(y_{w}, {N}) {'>' if kind == 'lower' else '<'} {claim}", "claim_holds": bool(ok),
               "seconds": round(time.time() - t0, 1)}
        results[w] = rec
        print(json.dumps(rec, indent=1))
        os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
        json.dump(rec, open(os.path.join(HERE, "output", f"mpmath_{w}.json"), "w", newline="\n"), indent=1)
    if not all(r["claim_holds"] for r in results.values()):
        print("CLAIM NOT VERIFIED"); sys.exit(1)
    print("verified with mpmath.iv: " + ", ".join(results))


if __name__ == "__main__":
    main()
