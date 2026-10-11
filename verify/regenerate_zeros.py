"""Independent regeneration / spot-check of the zero data used by verify_bound.py.

For the i-th zero rho_i = 1/2 + i gamma_i of zeta (i = 1..14400) it computes, with Arb (python-flint) at 16384 bits,
gamma_i and c_i = 1/(rho_i zeta'(rho_i)) as balls, and compares them with ../data/zeta_zeros_14400.npz:
the stored ball (decimal midpoint, radius + one unit in the last printed digit) must CONTAIN the freshly computed midpoint,
and the two balls must overlap.

Usage:
  python regenerate_zeros.py sample K [seed]   check K zeros at random indices (and always i = 1 and i = 14400)
  python regenerate_zeros.py range i0 i1       check the zeros with index i0..i1 (inclusive)
  python regenerate_zeros.py full out.npz      regenerate the whole data set (long: roughly 10 CPU-hours at 16384 bits)
Zeros are located by acb.zeta_zeros (FLINT/Arb: rigorous isolation of the n-th zero on the critical line)."""
import os, random, sys

import numpy as np
from flint import acb, acb_series, arb, ctx

sys.set_int_max_str_digits(0)
BITS = 16384
DIG = int(BITS * 0.30103) - 5


def compute(n0, count):
    ctx.prec = BITS
    zs = acb.zeta_zeros(n0, count)
    out = []
    for z in zs:
        zp = acb_series([z, 1], prec=2).zeta()[1]
        c = 1 / (z * zp)
        out.append((z.imag, c))
    return out


def dec_ulp(s):
    s = s.strip().lower(); mant, _, ex = s.partition("e"); frac = mant.partition(".")[2]
    return f"1e{(int(ex) if ex else 0) - len(frac)}"


def stored_ball(mid, rad):
    mid, rad = str(mid), str(rad)
    return arb(mid, rad) + arb(0, dec_ulp(mid))


def check(indices, z):
    bad = 0
    for i in indices:
        (g, c), = compute(i, 1)
        sg = stored_ball(z["gamma"][i - 1], z["gamma_rad"][i - 1])
        sr = stored_ball(z["c_re"][i - 1], z["c_re_rad"][i - 1]); si = stored_ball(z["c_im"][i - 1], z["c_im_rad"][i - 1])
        ok = sg.contains(g.mid()) and sg.overlaps(g) and sr.overlaps(c.real) and si.overlaps(c.imag) \
            and sr.contains(c.real.mid()) and si.contains(c.imag.mid())
        bad += (not ok)
        print(f"i={i:5d}  gamma {g.mid().str(25, radius=False)}  ok={ok}", flush=True)
    print("ALL OK" if bad == 0 else f"{bad} MISMATCHES")
    return bad


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("sample", "range"):
        z = np.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "zeta_zeros_14400.npz"))
        if mode == "sample":
            k = int(sys.argv[2]); rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
            idx = sorted(set([1, 14400] + rng.sample(range(2, 14400), k)))
        else:
            idx = list(range(int(sys.argv[2]), int(sys.argv[3]) + 1))
        sys.exit(1 if check(idx, z) else 0)
    elif mode == "full":
        rows = []
        for n0 in range(1, 14401, 100):
            for g, c in compute(n0, min(100, 14401 - n0)):
                rows.append((g.mid().str(DIG, radius=False), g.rad().str(6, radius=False), c.real.mid().str(60, radius=False),
                             c.imag.mid().str(60, radius=False), c.real.rad().str(6, radius=False), c.imag.rad().str(6, radius=False)))
            print(f"{len(rows)} zeros", flush=True)
        np.savez_compressed(sys.argv[2], gamma=np.array([r[0] for r in rows]), gamma_rad=np.array([r[1] for r in rows]),
                            c_re=np.array([r[2] for r in rows]), c_im=np.array([r[3] for r in rows]),
                            c_re_rad=np.array([r[4] for r in rows]), c_im_rad=np.array([r[5] for r in rows]))
    else:
        print(__doc__)
