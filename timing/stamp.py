"""Timestamps a file: RFC 3161 tokens from two independent time-stamping authorities, and an OpenTimestamps proof.

Only the SHA-256 hash of the file is sent to the services; the file itself never leaves the machine.
  <file>.freetsa.tsr    RFC 3161 token from https://freetsa.org/tsr
  <file>.digicert.tsr   RFC 3161 token from http://timestamp.digicert.com
  <file>.ots            OpenTimestamps proof (pending until a calendar's Bitcoin transaction confirms;
                        complete it later with `python stamp.py --upgrade <file>.ots`)
Usage: python stamp.py <file>   |   python stamp.py --upgrade <file>.ots
Requires: openssl on PATH, Python package `opentimestamps` (core library)."""
import hashlib, os, subprocess, sys, urllib.request

TSAS = {"freetsa": "https://freetsa.org/tsr", "digicert": "http://timestamp.digicert.com"}
CALENDARS = ["https://a.pool.opentimestamps.org", "https://b.pool.opentimestamps.org",
             "https://a.pool.eternitywall.com", "https://ots.btc.catallaxy.com"]


def rfc3161(path):
    q = path + ".tsq"
    subprocess.run(["openssl", "ts", "-query", "-data", path, "-sha256", "-cert", "-out", q], check=True, capture_output=True)
    out = {}
    for name, url in TSAS.items():
        req = urllib.request.Request(url, data=open(q, "rb").read(), headers={"Content-Type": "application/timestamp-query"})
        tsr = urllib.request.urlopen(req, timeout=60).read()
        open(f"{path}.{name}.tsr", "wb").write(tsr)
        txt = subprocess.run(["openssl", "ts", "-reply", "-in", f"{path}.{name}.tsr", "-text"], capture_output=True, text=True).stdout
        out[name] = next((l.split(":", 1)[1].strip() for l in txt.splitlines() if l.startswith("Time stamp:")), None)
    os.remove(q)
    return out


def ots_stamp(path):
    from opentimestamps.calendar import RemoteCalendar
    from opentimestamps.core.op import OpAppend, OpSHA256
    from opentimestamps.core.serialize import StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
    digest = hashlib.sha256(open(path, "rb").read()).digest()
    dtf = DetachedTimestampFile(OpSHA256(), Timestamp(digest))
    tip = dtf.timestamp.ops.add(OpAppend(os.urandom(16))).ops.add(OpSHA256())
    ok = 0
    for url in CALENDARS:
        try:
            tip.merge(RemoteCalendar(url).submit(tip.msg, timeout=30)); ok += 1
        except Exception as e:
            print(f"calendar {url}: {e}", file=sys.stderr)
    with open(path + ".ots", "wb") as f:
        dtf.serialize(StreamSerializationContext(f))
    return ok


def ots_upgrade(ots_path):
    from opentimestamps.calendar import RemoteCalendar
    from opentimestamps.core.notary import PendingAttestation
    from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile
    dtf = DetachedTimestampFile.deserialize(StreamDeserializationContext(open(ots_path, "rb")))
    changed = 0
    for msg, att in list(dtf.timestamp.all_attestations()):
        if isinstance(att, PendingAttestation):
            sub = dtf.timestamp
            stack = [dtf.timestamp]
            while stack:                      # find the sub-timestamp that carries this attestation
                t = stack.pop()
                if att in t.attestations:
                    sub = t; break
                stack.extend(t.ops.values())
            try:
                sub.merge(RemoteCalendar(att.uri).get_timestamp(sub.msg, timeout=30)); changed += 1
            except Exception as e:
                print(f"{att.uri}: not yet ({e})", file=sys.stderr)
    if changed:
        with open(ots_path, "wb") as f:
            dtf.serialize(StreamSerializationContext(f))
    return changed


if __name__ == "__main__":
    if sys.argv[1] == "--upgrade":
        print("upgraded attestations:", ots_upgrade(sys.argv[2]))
    else:
        p = sys.argv[1]
        print("sha256:", hashlib.sha256(open(p, "rb").read()).hexdigest())
        print("RFC 3161:", rfc3161(p))
        print("OpenTimestamps calendars reached:", ots_stamp(p))
