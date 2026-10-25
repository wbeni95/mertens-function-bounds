"""Rigorous verification of the bounds on q(x) = M(x)/sqrt(x) stated in THEOREM.md (FLINT/Arb ball arithmetic via python-flint).

Computes an enclosure of

    h(y) = 2 * sum_{i=1}^{N} f(gamma_i / T) * Re( c_i * exp(i * gamma_i * y) ),     N = 14400,  T = gamma_N,
    f(t) = (1 - t) cos(pi t) + sin(pi t) / pi,      c_i = 1 / (rho_i * zeta'(rho_i)),   rho_i = 1/2 + i gamma_i,

at the two points given in ../points/ and checks the claimed inequalities.  By Ingham's theorem in the form of Hurst (2018),
Theorem 4.2 (see THEOREM.md), liminf q(x) <= h(y) <= limsup q(x) for every real y.

Every input is a ball: gamma_i, Re c_i, Im c_i are read from ../data/zeta_zeros_14400.npz as decimal midpoint +- (stored radius
+ one unit in the last printed digit); the point y is an exact decimal number; T = gamma_N is the same ball as gamma_N.
Because |y| ~ 10^9627, each phase gamma_i*y is formed at high precision (P_HI bits, chosen from the size of y) and taken
modulo 2*pi by subtracting an exact integer multiple of 2*pi; the resulting phase is a narrow ball, and the rest of the term is then evaluated at 320
bits.  All steps are ball operations, so the final ball rigorously contains h(y).

Output: verify/output/certificate_<point>.json (the shipped results/ are never overwritten).
Usage:  python verify_bound.py            (both points)
        python verify_bound.py plus|minus
Requirements: Python 3.11+, numpy, python-flint >= 0.6 (ships FLINT with Arb)."""
import hashlib, json, os, sys, time

import numpy as np
from flint import acb, arb, ctx

sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
N = 14400
P_LO = 320
CLAIMS = {"plus": ("lower", "2.0617536514585282"), "minus": ("upper", "-2.0647155435291726")}   # h(y+) > claim, h(y-) < claim


def dec_ulp(s):
    """Place value of the last printed digit of a decimal string such as '-12.345e-6', as a string '1e<k>'."""
    s = s.strip().lower()
    mant, _, ex = s.partition("e")
    frac = mant.partition(".")[2]
    return f"1e{(int(ex) if ex else 0) - len(frac)}"


def ball(mid, rad):
    """A ball certainly containing the true value: decimal midpoint, stored radius, plus one unit of the last printed digit
    (both radius terms are added as balls, so their own rounding is accounted for)."""
    mid, rad = str(mid), str(rad)
    return arb(mid) + arb(0, arb(rad).upper()) + arb(0, arb(dec_ulp(mid)).upper())


def h_value(y_str, z):
    int_digits = len(y_str.strip().lstrip("-").split(".")[0])
    gam_s = [str(s) for s in z["gamma"][:N]]
    # bits: |gamma_i * y| < 2^(log2|y| + 14), so ~380 bits remain after taking it modulo 2*pi; and enough bits to hold every stored
    # gamma midpoint (9860 digits) without an extra conversion radius
    p_hi = max(int(int_digits * 3.3220) + 400, int(max(len(s) for s in gam_s) * 3.3220) + 64)
    ctx.prec = p_hi
    y = arb(y_str)
    twopi = 2 * arb.pi()
    T = ball(gam_s[N - 1], z["gamma_rad"][N - 1])
    ctx.prec = P_LO
    pi = arb.pi()
    tot = arb(0)
    for i in range(N):
        ctx.prec = p_hi
        g = ball(gam_s[i], z["gamma_rad"][i])
        th = g * y
        qm, qe = (th.mid() / twopi.mid()).mid().man_exp()   # q = qm * 2^qe ~ gamma_i*y/(2 pi); only needs to be AN integer
        qm, qe = int(qm), int(qe)
        k = arb(qm >> (-qe) if qe < 0 else qm << qe)          # exact integer (it has < p_hi bits)
        assert k.rad() == 0 and k.is_exact()
        red = th - k * twopi                                 # rigorous ball for gamma_i*y - 2*pi*k
        u = g / T
        ctx.prec = P_LO
        red = +red; u = +u                                   # round the (already narrow) balls outward to P_LO bits
        f = (1 - u) * (pi * u).cos() + (pi * u).sin() / pi
        c_re = ball(z["c_re"][i], z["c_re_rad"][i]); c_im = ball(z["c_im"][i], z["c_im_rad"][i])
        tot += 2 * f * (c_re * red.cos() - c_im * red.sin())   # 2 Re(c e^{i red})
    return tot, p_hi


def check_data(z):
    assert all(len(z[k]) >= N for k in ("gamma", "gamma_rad", "c_re", "c_im", "c_re_rad", "c_im_rad"))
    ctx.prec = 128
    g = [arb(str(s)[:60]) for s in z["gamma"][:N]]
    assert all(g[i] < g[i + 1] for i in range(N - 1)), "gamma midpoints not strictly increasing"
    assert abs(g[0] - arb("14.134725141734693790457")) < arb("1e-15")


def main():
    which = sys.argv[1:] or ["plus", "minus"]
    zpath = os.path.join(PKG, "data", "zeta_zeros_14400.npz")
    z = np.load(zpath, allow_pickle=False)
    check_data(z)
    data_sha = hashlib.sha256(open(zpath, "rb").read()).hexdigest()
    out = {}
    for w in which:
        y_path = os.path.join(PKG, "points", f"y_{w}.txt")
        y_str = open(y_path).read().strip()
        t0 = time.time()
        h, p_hi = h_value(y_str, z)
        kind, claim = CLAIMS[w]
        ctx.prec = P_LO
        ok = bool(h > arb(claim)) if kind == "lower" else bool(h < arb(claim))
        rec = {"point": w, "y_file_sha256": hashlib.sha256(open(y_path, "rb").read()).hexdigest(), "N": N, "T": "gamma_N",
               "precision_bits_phase": p_hi, "precision_bits_terms": P_LO,
               "h_ball": h.str(60, radius=True), "h_mid_rounded_60": h.mid().str(60, radius=False), "h_rad": h.rad().str(3, radius=False),
               "claim": f"h(y_{w}) {'>' if kind == 'lower' else '<'} {claim}", "claim_verified": ok, "data_sha256": data_sha}
        out[w] = rec
        print(json.dumps(rec, indent=1)); print(f"({time.time() - t0:.1f} s)", flush=True)
        os.makedirs(os.path.join(HERE, "output"), exist_ok=True)     # never overwrite the shipped results/ (checksums)
        json.dump(rec, open(os.path.join(HERE, "output", f"certificate_{w}.json"), "w"), indent=1)
    if not all(r["claim_verified"] for r in out.values()):
        print("CLAIM NOT VERIFIED"); sys.exit(1)
    print("all claims verified")


if __name__ == "__main__":
    main()
