"""Second, independent rigorous verification of THEOREM.md with a different library: mpmath interval arithmetic (mpmath.iv).

Same quantity as verify_bound.py (no code shared with it):
    h(y) = 2 * sum_{i=1}^{N} f(gamma_i / T) * Re( c_i * exp(i * gamma_i * y) ),   N = 14400,  T = gamma_N,
    f(t) = (1 - t) cos(pi t) + sin(pi t) / pi,   c_i = 1/(rho_i zeta'(rho_i)).
Inputs are intervals: stored decimal midpoint +- (stored radius + one unit in the last printed digit).  The phase gamma_i*y is
formed with ~9900-digit interval arithmetic and taken modulo 2*pi by subtracting an exact integer multiple of 2*pi; that phase and the
rest of each term are then evaluated in 100-digit interval arithmetic (outward rounding throughout).
mpmath.iv is pure Python; if gmpy2 is installed mpmath uses it automatically and runs faster.
Usage:  python verify_bound_mpmath.py [plus|minus]
Requirements: Python 3.11+, numpy, mpmath >= 1.3."""
import json, os, sys, time

import numpy as np
from mpmath import iv, mp

sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
N = 14400
D_LO = 100
CLAIMS = {"plus": ("lower", "2.0617536514585282"), "minus": ("upper", "-2.0647155435291726")}


def ulp_str(s):
    s = s.strip().lower()
    mant, _, ex = s.partition("e")
    return f"1e{(int(ex) if ex else 0) - len(mant.partition('.')[2])}"


def interval(mid, rad):
    """[mid - r, mid + r] with r an upper bound of (stored radius + one unit in the last printed digit)."""
    mid, rad = str(mid), str(rad)
    radius = iv.mpf(rad) + iv.mpf(ulp_str(mid))                 # an interval whose upper end bounds the radius
    return iv.mpf(mid) + iv.mpf([-1, 1]) * radius              # = mid + [-radius.b, radius.b] (outward rounded)


def h_value(y_str, z):
    int_digits = len(y_str.strip().lstrip("-").split(".")[0])
    gam_s = [str(s) for s in z["gamma"][:N]]
    d_hi = max(int_digits + 130, max(len(s) for s in gam_s) + 20)
    iv.dps = d_hi; mp.dps = d_hi
    y = iv.mpf(y_str)
    twopi = 2 * iv.pi
    twopi_mid = 2 * mp.pi
    T = interval(gam_s[N - 1], z["gamma_rad"][N - 1])
    tot = iv.mpf(0)
    for i in range(N):
        iv.dps = d_hi; mp.dps = d_hi
        g = interval(gam_s[i], z["gamma_rad"][i])
        th = g * y
        k = int(mp.floor(mp.mpf(th.mid) / twopi_mid))       # an exact integer (any integer would do)
        red = th - k * twopi
        u = g / T
        iv.dps = D_LO                                        # operations below take the narrow intervals red, u exactly and
        pi = iv.pi                                           # round their results outward to D_LO digits
        f = (1 - u) * iv.cos(pi * u) + iv.sin(pi * u) / pi
        c_re = interval(z["c_re"][i], z["c_re_rad"][i]); c_im = interval(z["c_im"][i], z["c_im_rad"][i])
        tot = tot + 2 * f * (c_re * iv.cos(red) - c_im * iv.sin(red))
        if i % 2000 == 0:
            print(f"  term {i}/{N}", flush=True)
    return tot, d_hi


def main():
    which = sys.argv[1:] or ["plus", "minus"]
    z = np.load(os.path.join(PKG, "data", "zeta_zeros_14400.npz"), allow_pickle=False)
    ok_all = True
    for w in which:
        y_str = open(os.path.join(PKG, "points", f"y_{w}.txt")).read().strip()
        t0 = time.time()
        h, d_hi = h_value(y_str, z)
        iv.dps = D_LO
        kind, claim = CLAIMS[w]
        c = iv.mpf(claim)
        try:                                   # mpmath.iv: True/False if decided for the whole interval, ValueError if overlapping
            ok = bool(h > c) if kind == "lower" else bool(h < c)
        except ValueError:
            ok = False
        ok_all &= ok
        mp.dps = D_LO + 10                     # endpoints have D_LO-digit precision: exact conversion, printing only
        rec = {"point": w, "library": "mpmath.iv", "digits_phase": d_hi, "digits_terms": D_LO,
               "h_lower": mp.nstr(mp.mpf(h.a), 60), "h_upper": mp.nstr(mp.mpf(h.b), 60), "h_width": mp.nstr(mp.mpf(h.b) - mp.mpf(h.a), 3),
               "claim": f"h(y_{w}) {'>' if kind == 'lower' else '<'} {claim}", "claim_verified": ok}
        print(json.dumps(rec, indent=1)); print(f"({time.time() - t0:.1f} s)", flush=True)
        os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
        json.dump(rec, open(os.path.join(HERE, "output", f"certificate_mpmath_{w}.json"), "w"), indent=1)
    if not ok_all:
        print("CLAIM NOT VERIFIED"); sys.exit(1)
    print("all claims verified")


if __name__ == "__main__":
    main()
