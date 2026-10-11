"""The public rule that turns a drand beacon round into the challenge (M, r).

The beacon is the League of Entropy drand mainnet ("default" chain, scheme pedersen-bls-chained, one round every 30 s).
For a round with randomness R (32 bytes; R = SHA-256 of the round's BLS signature):

    M = 10^13 + ( int(SHA-256(b"mertens-function-bounds challenge M " + R)) mod 9*10^13 )      (14 digits)
    r =          int(SHA-256(b"mertens-function-bounds challenge r " + R)) mod M

A certificate point for this challenge must have the form  y = r + M*z/1024 + d  with an integer z and |d| <= 1/20.
A point computed before the round was published satisfies this with probability about 0.1*1024/M < 10^-11, and moving
such a point to the required form shifts it by up to M/2048, which destroys the phase alignment the bound depends on.

Usage: python derive_challenge.py beacon.json      (prints M, r and the round's publication time)"""
import hashlib, json, sys

DRAND_CHAIN = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
DRAND_GENESIS = 1595431050
DRAND_PERIOD = 30


def round_time(rnd):
    """UNIX time at which drand round `rnd` is published (genesis + (round - 1) * period)."""
    return DRAND_GENESIS + (int(rnd) - 1) * DRAND_PERIOD


def check_beacon(b):
    """Consistency checks that need no network: chain, scheme, randomness = SHA-256(signature)."""
    assert b["chain_hash"] == DRAND_CHAIN, "not the drand mainnet default chain"
    assert hashlib.sha256(bytes.fromhex(b["signature"])).hexdigest() == b["randomness"], "randomness != SHA-256(signature)"


def derive(randomness_hex):
    R = bytes.fromhex(randomness_hex)
    assert len(R) == 32
    M = 10 ** 13 + int(hashlib.sha256(b"mertens-function-bounds challenge M " + R).hexdigest(), 16) % (9 * 10 ** 13)
    r = int(hashlib.sha256(b"mertens-function-bounds challenge r " + R).hexdigest(), 16) % M
    return M, r


if __name__ == "__main__":
    b = json.load(open(sys.argv[1]))
    check_beacon(b)
    M, r = derive(b["randomness"])
    print(json.dumps({"round": b["round"], "round_time_unix": round_time(b["round"]), "M": M, "r": r}, indent=1))
