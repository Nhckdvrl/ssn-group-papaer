"""Parallel ranged HTTP download (HF per-connection throughput here is ~0.1-0.3 MB/s).
usage: pdl.py <url> <dst> <size> [nconn]"""
import os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

url, dst, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 64
part = 8 * 1024 * 1024
ranges = [(s, min(s + part, size) - 1) for s in range(0, size, part)]
os.makedirs(os.path.dirname(dst), exist_ok=True)
tmp = dst + ".parts"
os.makedirs(tmp, exist_ok=True)


def get(r):
    s, e = r
    p = f"{tmp}/{s}"
    if os.path.exists(p) and os.path.getsize(p) == e - s + 1:
        return
    for _ in range(20):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={s}-{e}"})
            data = urllib.request.urlopen(req, timeout=120).read()
            if len(data) == e - s + 1:
                open(p, "wb").write(data)
                return
        except Exception:
            pass
    raise RuntimeError(f"failed {s}")


with ThreadPoolExecutor(n) as ex:
    list(ex.map(get, ranges))
with open(dst, "wb") as out:
    for s, e in ranges:
        out.write(open(f"{tmp}/{s}", "rb").read())
import shutil
shutil.rmtree(tmp)
print("ok", dst, os.path.getsize(dst) == size)
