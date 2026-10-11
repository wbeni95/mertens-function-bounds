"""Rigorous verification of the bounds on q(x) = M(x)/sqrt(x) stated in THEOREM.md.

Computes, in ball arithmetic (Arb, via python-flint), the value

    h(y, N) = 2 * Re( sum_{i=1}^{N} f(gamma_i / gamma_N) * c_i * exp(i * gamma_i * y) ),
    f(t)    = (1 - t) cos(pi t) + sin(pi t) / pi,
    c_i     = 1 / (rho_i * zeta'(rho_i)),   rho_i = 1/2 + i gamma_i  (i-th zero of zeta with positive imaginary part),

for N = 14400 at the two points y given in ../points/, and checks the claimed inequalities.  By Ingham's theorem
(see THEOREM.md), liminf q(x) <= h(y, N) <= limsup q(x) for every real y and every positive integer N, without any hypothesis.

Input data: ../data/zeta_zeros_14400.npz with gamma_i and Re/Im c_i as decimal midpoints and their radii (the stored decimal
midpoints are roundings; one unit in the last printed digit is added to every radius).  The data can be regenerated
independently with regenerate_zeros.py (or any other rigorous software).

Output: verify/output/certificate_<point>.json (the shipped results/ are never overwritten).
Usage:  python verify_bound.py            (both points)
        python verify_bound.py plus|minus
Requirements: Python 3.11+, numpy, python-flint (Arb).  Precision used: 16600 bits."""
import hashlib, json, os, sys, time

import numpy as np
from flint import acb, arb, ctx

sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
PREC = 16600
CLAIMS = {"plus": ("lower", "1.9203693129093421"), "minus": ("upper", "-1.9205369736317600")}   # h(y+) > claim, h(y-) < claim


def dec_ulp(s):
    """Place value of the last printed digit of a decimal string such as '-12.345e-6', as a string '1e<k>'."""
    s = s.strip().lower()
    mant, _, ex = s.partition("e")
    frac = mant.partition(".")[2]
    return f"1e{(int(ex) if ex else 0) - len(frac)}"


def ball(mid, rad):
    """A ball certainly containing the true value: decimal midpoint, stored radius, plus one unit of the last printed digit."""
    mid, rad = str(mid), str(rad)
    return arb(mid, rad) + arb(0, dec_ulp(mid))


def h_value(y_str, z, N):
    ctx.prec = PREC
    gam = [ball(m, r) for m, r in zip(z["gamma"][:N], z["gamma_rad"][:N])]
    cs = [acb(ball(a, ra), ball(b, rb)) for a, b, ra, rb in zip(z["c_re"][:N], z["c_im"][:N], z["c_re_rad"][:N], z["c_im_rad"][:N])]
    y = arb(y_str)
    pi = arb.pi()
    gN = gam[N - 1]
    tot = acb(0)
    for g, c in zip(gam, cs):
        t = g / gN
        f = (1 - t) * (pi * t).cos() + (pi * t).sin() / pi
        tot += f * c * acb(0, g * y).exp()
    return 2 * tot.real


def main():
    which = sys.argv[1:] or ["plus", "minus"]
    zpath = os.path.join(PKG, "data", "zeta_zeros_14400.npz")
    z = np.load(zpath)
    N = 14400
    assert len(z["gamma"]) >= N
    out = {}
    for w in which:
        y_path = os.path.join(PKG, "points", f"y_{w}.txt")
        y_str = open(y_path).read().strip()
        t0 = time.time()
        h = h_value(y_str, z, N)
        kind, claim = CLAIMS[w]
        ok = bool(h > arb(claim)) if kind == "lower" else bool(h < arb(claim))
        rec = {"point": w, "y_file_sha256": hashlib.sha256(open(y_path, "rb").read()).hexdigest(), "N": N, "precision_bits": PREC,
               "h_ball": h.str(60, radius=True), "h_mid_rounded_60": h.mid().str(60, radius=False), "h_rad": h.rad().str(3, radius=False),
               "claim": f"h(y_{w}, {N}) {'>' if kind == 'lower' else '<'} {claim}", "claim_verified": ok,
               "data_sha256": hashlib.sha256(open(zpath, "rb").read()).hexdigest()}
        out[w] = rec
        print(json.dumps(rec, indent=1)); print(f"({time.time() - t0:.1f} s)")
        os.makedirs(os.path.join(HERE, "output"), exist_ok=True)     # never overwrite the shipped results/ (checksums)
        json.dump(rec, open(os.path.join(HERE, "output", f"certificate_{w}.json"), "w", newline="\n"), indent=1)
    if not all(r["claim_verified"] for r in out.values()):
        print("CLAIM NOT VERIFIED"); sys.exit(1)
    print("all requested claims verified: " + ", ".join(out))


if __name__ == "__main__":
    main()
