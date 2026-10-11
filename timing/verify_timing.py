"""Verifies the timed run: a fresh challenge from a public beacon at T0, and a certificate for it timestamped at T1.

Checks, in order:
 1. the beacon (beacon.json) is a drand mainnet round and randomness = SHA-256(signature); T0 = the round's publication time;
 2. the challenge (M, r) in certificate.json follows derive_challenge.py from that round;
 3. each certificate point has the required form y = r + M*z/1024 + d with integer z and |d| <= 1/20 (exact arithmetic);
 4. h(y, 14400) is evaluated rigorously with ../verify/verify_bound.py (Arb) and the stated claims hold;
 5. the RFC 3161 tokens on commit.json and certificate.json are valid (openssl, CA files in ca/), giving their times;
 6. commit time < T0 < certificate time; prints the elapsed time T1 - T0 for each time-stamping authority.
With --online, the beacon round is also fetched from two public drand endpoints and compared.
The OpenTimestamps proofs (*.ots) can be checked with the official client or at https://opentimestamps.org.
Usage: python verify_timing.py [--online]        (about 30 seconds; needs numpy, python-flint, openssl)"""
import datetime, json, os, re, subprocess, sys, urllib.request
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(PKG, "verify"))
sys.set_int_max_str_digits(0)
import derive_challenge as DC

CA = {"freetsa": os.path.join(HERE, "ca", "freetsa_cacert.pem"), "digicert": os.path.join(HERE, "ca", "digicert_root_g4.pem")}


def frac(s):
    s = s.strip(); neg = s.startswith("-"); s = s.lstrip("+-")
    ip, _, fp = s.partition(".")
    v = Fraction(int(ip + fp), 10 ** len(fp))
    return -v if neg else v


def tsa_time(data_path, name):
    tsr = f"{data_path}.{name}.tsr"
    v = subprocess.run(["openssl", "ts", "-verify", "-in", tsr, "-data", data_path, "-CAfile", CA[name]],
                       capture_output=True, text=True)
    ok = "Verification: OK" in (v.stdout + v.stderr)
    txt = subprocess.run(["openssl", "ts", "-reply", "-in", tsr, "-text"], capture_output=True, text=True).stdout
    t = next(l.split(":", 1)[1].strip() for l in txt.splitlines() if l.startswith("Time stamp:"))
    t = re.sub(r"\.\d+", "", t.replace(" GMT", ""))
    when = datetime.datetime.strptime(" ".join(t.split()), "%b %d %H:%M:%S %Y").replace(tzinfo=datetime.timezone.utc)
    return ok, when


def main():
    global HERE
    online = "--online" in sys.argv
    if "--dir" in sys.argv:                # verify a copy of the timing files elsewhere (same layout)
        HERE = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1])
    fails = []
    b = json.load(open(os.path.join(HERE, "beacon.json")))
    DC.check_beacon(b)
    T0 = datetime.datetime.fromtimestamp(DC.round_time(b["round"]), datetime.timezone.utc)
    print(f"[1] beacon: drand round {b['round']}, published {T0:%Y-%m-%d %H:%M:%S} UTC; randomness = SHA-256(signature) (BLS signature not verified here)")
    if online:
        seen = 0
        for url in ("https://api.drand.sh", "https://api2.drand.sh", "https://api3.drand.sh", "https://drand.cloudflare.com"):
            try:
                req = urllib.request.Request(f"{url}/public/{b['round']}", headers={"User-Agent": "verify_timing/1.0"})
                r = json.load(urllib.request.urlopen(req, timeout=30))
            except Exception as e:
                print(f"    {url}: not reachable ({e})"); continue
            same = r["randomness"] == b["randomness"]; seen += 1
            print(f"    {url}: {'same randomness' if same else 'DIFFERENT'}")
            fails += [] if same else [f"beacon differs at {url}"]
        fails += [] if seen >= 2 else ["fewer than two drand endpoints reachable for the online check"]
    c = json.load(open(os.path.join(HERE, "certificate.json")))
    M, r = DC.derive(b["randomness"])
    if (M, r) != (int(c["M"]), int(c["r"])) or int(c["beacon_round"]) != int(b["round"]):
        fails.append("challenge (M, r) does not follow from the beacon")
    print(f"[2] challenge from the beacon: M = {M}, r = {r}")
    import numpy as np
    import verify_bound as V
    zd = np.load(os.path.join(PKG, "data", "zeta_zeros_14400.npz"))
    from flint import arb
    for side, key, claim_key in (("sup", "y_sup", "limsup_greater_than"), ("inf", "y_inf", "liminf_less_than")):
        y = frac(c[key])
        q = (y - r) * 1024 / M
        z = round(q)
        d = y - r - Fraction(M) * z / 1024
        form_ok = abs(d) <= Fraction(1, 20)
        h = V.h_value(c[key], zd, 14400)
        claim = c["claims"][claim_key]
        holds = bool(h > arb(claim)) if side == "sup" else bool(h < arb(claim))
        print(f"[3] {side}: y = r + M*z/1024 + d with |d| = {float(abs(d)):.3e} <= 0.05: {form_ok}")
        print(f"[4] {side}: h(y, 14400) in {h.str(25, radius=True)}; claim {'>' if side == 'sup' else '<'} {claim}: {holds}")
        fails += [] if form_ok else [f"{side}: point not of the challenge form"]
        fails += [] if holds else [f"{side}: claim does not hold"]
    times = {}
    for f in ("commit.json", "certificate.json"):
        for name in CA:
            ok, when = tsa_time(os.path.join(HERE, f), name)
            times[(f, name)] = when
            print(f"[5] {f} {name}: token {'valid' if ok else 'INVALID'}, time {when:%Y-%m-%d %H:%M:%S} UTC")
            fails += [] if ok else [f"{f} {name} token invalid"]
    for name in CA:
        tc, t1 = times[("commit.json", name)], times[("certificate.json", name)]
        order = tc < T0 < t1
        el = (t1 - T0).total_seconds()
        print(f"[6] {name}: commit {tc:%Y-%m-%d %H:%M:%S} < beacon {T0:%Y-%m-%d %H:%M:%S} < certificate "
              f"{t1:%Y-%m-%d %H:%M:%S}: {order}; "
              f"elapsed T1 - T0 = {el:.0f} s = {el / 60:.1f} min")
        fails += [] if order else [f"{name}: time order wrong"]
    if fails:
        print("NOT VERIFIED:", "; ".join(fails)); sys.exit(1)
    print("timed run verified")


if __name__ == "__main__":
    main()
