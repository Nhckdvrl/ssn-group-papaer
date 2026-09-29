"""List / download public tau-bench leaderboard trajectories (s3://sierra-tau-bench-public, no auth)."""
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

BASE = "https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com"
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}


def list_keys(prefix, delimiter=None):
    out, token = [], None
    while True:
        q = {"list-type": "2", "prefix": prefix}
        if delimiter:
            q["delimiter"] = delimiter
        if token:
            q["continuation-token"] = token
        x = urllib.request.urlopen(f"{BASE}/?{urllib.parse.urlencode(q)}", timeout=60).read()
        r = ET.fromstring(x)
        for c in r.findall("s:Contents", NS):
            out.append((c.find("s:Key", NS).text, int(c.find("s:Size", NS).text)))
        for p in r.findall("s:CommonPrefixes", NS):
            out.append((p.find("s:Prefix", NS).text, -1))
        if r.find("s:IsTruncated", NS).text == "true":
            token = r.find("s:NextContinuationToken", NS).text
        else:
            return out


def download(keys, root):
    def one(k):
        dst = os.path.join(root, k)
        if os.path.exists(dst):
            return
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        urllib.request.urlretrieve(f"{BASE}/{urllib.parse.quote(k)}", dst)

    with ThreadPoolExecutor(16) as ex:
        list(ex.map(one, keys))


if __name__ == "__main__":
    cmd, prefix = sys.argv[1], sys.argv[2]
    if cmd == "ls":
        for k, s in list_keys(prefix, "/"):
            print(s, k)
    elif cmd == "du":
        import collections

        c, n = collections.Counter(), collections.Counter()
        for k, s in list_keys(prefix):
            base = k.rsplit("/", 1)[-1]
            e = base.rsplit(".", 1)[-1] if "." in base else "(none)"
            c[e] += s
            n[e] += 1
        for e in c:
            print(e, n[e], f"{c[e]/1e6:.1f}MB")
    elif cmd == "get":  # get <prefix> <root> [ext,ext]
        exts = sys.argv[4].split(",") if len(sys.argv) > 4 else ["json"]
        ks = [k for k, s in list_keys(prefix) if k.rsplit(".", 1)[-1] in exts]
        download(ks, sys.argv[3])
        print("downloaded", len(ks))
