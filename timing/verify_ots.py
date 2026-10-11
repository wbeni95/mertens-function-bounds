"""Checks the OpenTimestamps proofs in this folder against Bitcoin block headers from a public block explorer.

For each <file>.ots: the proof commits to SHA-256(<file>), and every Bitcoin attestation in it must equal the
merkle root of the named block. Block headers are read from https://blockstream.info (read-only).
Usage: python verify_ots.py commit.json.ots certificate.json.ots   (needs the Python package `opentimestamps`)"""
import datetime, hashlib, json, sys, urllib.request
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
from opentimestamps.core.serialize import StreamDeserializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ots-check/1.0"}), timeout=30).read()


for f in sys.argv[1:]:
    d = DetachedTimestampFile.deserialize(StreamDeserializationContext(open(f, "rb")))
    target = open(f[:-4], "rb").read()
    assert d.file_digest == hashlib.sha256(target).digest(), "file digest mismatch"
    for msg, att in d.timestamp.all_attestations():
        if not isinstance(att, BitcoinBlockHeaderAttestation):
            continue
        h = get(f"https://blockstream.info/api/block-height/{att.height}").decode().strip()
        blk = json.loads(get(f"https://blockstream.info/api/block/{h}"))
        ok = msg[::-1].hex() == blk["merkle_root"]
        t = datetime.datetime.fromtimestamp(blk["timestamp"], datetime.timezone.utc)
        print(f"{f}: block {att.height} {h[:16]}... merkle root {'MATCHES' if ok else 'DIFFERS'}; block time {t:%Y-%m-%d %H:%M:%S} UTC")
