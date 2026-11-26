"""Range-parallel, resumable download of the safetensors of one HF repo revision, with sha256 check.

Each file is split into byte ranges fetched by independent curl processes (stalled ranges are retried and
resumed), then concatenated and verified against the HF LFS sha256. Source mirror is selectable because the
HF CDN stalls on these hosts while ModelScope (official Qwen mirror) is steadier; the HF sha256 is always the check.

Usage: python3 fetch_ranges.py <dest_dir> <repo> [--mirror hf|modelscope] [--parts 8] [--jobs 16]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def hf_tree(repo, rev):
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/tree/{rev}", timeout=60) as r:
        return json.loads(r.read())


def url_for(mirror, repo, rev, f):
    if mirror == "modelscope":
        return f"https://modelscope.cn/models/{repo}/resolve/master/{f}"
    return f"https://huggingface.co/{repo}/resolve/{rev}/{f}"


def fetch_part(url, out, lo, hi):
    want = hi - lo + 1
    for _ in range(200):
        have = out.stat().st_size if out.exists() else 0
        if have >= want:
            return True
        subprocess.run(["curl", "-sL", "--connect-timeout", "20", "--speed-limit", "100000", "--speed-time", "30",
                        "-r", f"{lo + have}-{hi}", "-o", "-", url], stdout=open(out, "ab"), check=False)
        time.sleep(1)
    return False


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 24), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest"); ap.add_argument("repo")
    ap.add_argument("--rev", default="main"); ap.add_argument("--mirror", default="hf")
    ap.add_argument("--parts", type=int, default=8); ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{a.repo}/revision/{a.rev}", timeout=60) as r:
        sha = json.loads(r.read())["sha"]
    d = Path(a.dest) / a.repo.replace("/", "__"); d.mkdir(parents=True, exist_ok=True)
    (d / "REVISION").write_text(sha + "\n")
    tree = hf_tree(a.repo, sha)
    small = [x["path"] for x in tree if x["type"] == "file" and "lfs" not in x and not x["path"].endswith(".md")]
    for f in small:
        if not (d / f).exists():
            subprocess.run(["curl", "-sfL", "--max-time", "120", "-o", str(d / f), url_for("hf", a.repo, sha, f)], check=True)
    big = [x for x in tree if "lfs" in x and x["path"].endswith(".safetensors")]
    tasks, plan = [], {}
    for x in big:
        f, size, want = x["path"], x["lfs"]["size"], x["lfs"]["oid"]
        if (d / f).exists() and (d / f).stat().st_size == size and sha256(d / f) == want:
            print("ok (cached)", f, flush=True); continue
        step = -(-size // a.parts)
        parts = []
        for i in range(a.parts):
            lo, hi = i * step, min(size, (i + 1) * step) - 1
            p = d / f".{f}.part{i}"
            parts.append(p); tasks.append((url_for(a.mirror, a.repo, sha, f), p, lo, hi))
        plan[f] = (parts, size, want)
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(lambda t: fetch_part(*t), tasks))
    bad = False
    for f, (parts, size, want) in plan.items():
        with open(d / f, "wb") as out:
            for p in parts:
                out.write(p.read_bytes())
        good = (d / f).stat().st_size == size and sha256(d / f) == want
        print("ok" if good else "BAD", f, flush=True)
        if good:
            for p in parts:
                p.unlink()
        bad |= not good
    print("ALLDONE" if not bad else "FAILED", a.repo, sha)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
