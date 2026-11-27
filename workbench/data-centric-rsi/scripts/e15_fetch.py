"""E15: resumable, range-parallel download of (part of) one HF model repo to a node-local dir, verified against
the Hugging Face LFS sha256.

HF throttles single streams on these hosts (measured 2026-11-28: ~0.7 MB/s per stream), so large files are split
into byte ranges fetched in parallel, optionally from a mirror: `modelscope` (official Qwen mirror) or `hfmirror`
(hf-mirror.com). The file list and sha256 always come from the HF API, so a mirror cannot change the content.
FSDP shards (*.pt) are skipped. Files land in <dest>/<repo with / -> __>/<path relative to --prefix>.

Usage: python3 e15_fetch.py <dest_dir> <repo> [--prefix P] [--mirror hf|hfmirror|modelscope] [--parts 12]
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def tree(repo, rev, prefix):
    path = f"/{urllib.parse.quote(prefix)}" if prefix else ""
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/tree/{rev}{path}?recursive=true", timeout=60) as r:
        return [x for x in json.loads(r.read()) if x["type"] == "file"]


def url_for(mirror, repo, rev, f):
    q = urllib.parse.quote(f)
    if mirror == "modelscope":
        return f"https://modelscope.cn/models/{repo}/resolve/master/{q}"
    if mirror == "hfmirror":
        return f"https://hf-mirror.com/{repo}/resolve/{rev}/{q}"
    return f"https://huggingface.co/{repo}/resolve/{rev}/{q}"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 24), b""):
            h.update(blk)
    return h.hexdigest()


def fetch_range(url, out, lo, hi):
    want = hi - lo + 1
    for _ in range(400):
        have = out.stat().st_size if out.exists() else 0
        if have >= want:
            return True
        with open(out, "ab") as fh:
            subprocess.run(["curl", "-sL", "--connect-timeout", "20", "--speed-limit", "50000", "--speed-time", "30",
                            "-r", f"{lo + have}-{hi}", "-o", "-", url], stdout=fh, check=False)
        time.sleep(1)
    return False


def fetch_file(url, out, size, parts):
    if size is None or size < 64 << 20:
        for _ in range(100):
            subprocess.run(["curl", "-sL", "--connect-timeout", "20", "-o", str(out), url], check=False)
            if out.exists() and (size is None or out.stat().st_size == size):
                return
            time.sleep(2)
        raise RuntimeError(f"failed {url}")
    pdir = out.parent / (out.name + ".parts"); pdir.mkdir(exist_ok=True)
    step = -(-size // parts)
    ranges = [(i, i * step, min(size, (i + 1) * step) - 1) for i in range(parts)]
    with ThreadPoolExecutor(parts) as ex:
        ok = list(ex.map(lambda r: fetch_range(url, pdir / f"{r[0]:03d}", r[1], r[2]), ranges))
    if not all(ok):
        raise RuntimeError(f"ranges incomplete for {url}")
    with open(out, "wb") as fh:
        for i, _, _ in ranges:
            with open(pdir / f"{i:03d}", "rb") as ph:
                while blk := ph.read(1 << 24):
                    fh.write(blk)
    for p in pdir.iterdir():
        p.unlink()
    pdir.rmdir()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest"); ap.add_argument("repo")
    ap.add_argument("--prefix", default=""); ap.add_argument("--rev", default="main")
    ap.add_argument("--mirror", default="hf", choices=["hf", "hfmirror", "modelscope"])
    ap.add_argument("--parts", type=int, default=12)
    a = ap.parse_args()
    root = Path(a.dest) / a.repo.replace("/", "__"); root.mkdir(parents=True, exist_ok=True)
    for f in [f for f in tree(a.repo, a.rev, a.prefix) if not f["path"].endswith(".pt")]:
        rel = f["path"][len(a.prefix):].lstrip("/") if a.prefix else f["path"]
        out = root / rel; out.parent.mkdir(parents=True, exist_ok=True)
        want = (f.get("lfs") or {}).get("oid")
        if out.exists() and out.stat().st_size == f.get("size") and (not want or sha256(out) == want):
            print("ok  ", rel, flush=True); continue
        if out.exists():
            out.unlink()  # partial single-stream file from an earlier version of this script
        t0 = time.time()
        mirror = a.mirror if want else "hf"  # small non-LFS files: always from HF itself
        fetch_file(url_for(mirror, a.repo, a.rev, f["path"]), out, f.get("size"), a.parts)
        if want and sha256(out) != want:
            out.unlink(); sys.exit(f"sha256 mismatch for {rel} (mirror {mirror})")
        print(f"got  {rel} {f.get('size', 0) / 1e9:.2f}GB {time.time() - t0:.0f}s via {mirror}", flush=True)
    print("DONE", root, flush=True)


if __name__ == "__main__":
    main()
