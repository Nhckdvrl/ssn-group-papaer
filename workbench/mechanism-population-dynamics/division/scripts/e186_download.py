#!/usr/bin/env python3
"""E186: download one HF repo revision to a node-local dir with parallel curl (HF Xet / hub downloads stall on these
hosts). Only config / tokenizer / safetensors files. Usage: e186_download.py REPO REVISION OUTDIR [--par 4]
Verifies sizes and LFS sha256 of every safetensors shard; writes OUTDIR/_download.json (repo, revision sha, files)."""
import argparse, hashlib, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import HfApi

ap = argparse.ArgumentParser()
ap.add_argument("repo"); ap.add_argument("revision"); ap.add_argument("out")
ap.add_argument("--par", type=int, default=4)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
tokf = os.path.expanduser("~/.cache/huggingface/token")
TOKEN = open(tokf).read().strip() if os.path.exists(tokf) else None
info = HfApi().model_info(a.repo, revision=a.revision, files_metadata=True, token=TOKEN)
keep = [s for s in info.siblings if s.rfilename.endswith((".json", ".safetensors", ".model", ".txt", ".tiktoken"))
        and "/" not in s.rfilename and not s.rfilename.startswith("consolidated")]
t0 = time.time()


def get(s):
    dst = os.path.join(a.out, s.rfilename)
    if os.path.exists(dst) and s.size and os.path.getsize(dst) == s.size:
        return s.rfilename, "cached"
    url = f"https://huggingface.co/{a.repo}/resolve/{info.sha}/{s.rfilename}"
    cmd = ["curl", "-sSL", "--retry", "20", "--retry-delay", "5", "--retry-all-errors", "-C", "-", "-o", dst, url]
    if TOKEN:
        cmd[1:1] = ["-H", f"Authorization: Bearer {TOKEN}"]
    for attempt in range(5):
        r = subprocess.run(cmd)
        if r.returncode == 0 and (not s.size or os.path.getsize(dst) == s.size):
            break
        time.sleep(10)
    if s.lfs:
        h = hashlib.sha256()
        with open(dst, "rb") as f:
            for blk in iter(lambda: f.read(1 << 24), b""):
                h.update(blk)
        assert h.hexdigest() == s.lfs.sha256, ("sha mismatch", s.rfilename)
    print(f"[{time.time() - t0:6.0f}s] {s.rfilename} {os.path.getsize(dst) / 1e9:.2f} GB", flush=True)
    return s.rfilename, "ok"


with ThreadPoolExecutor(a.par) as ex:
    res = list(ex.map(get, sorted(keep, key=lambda s: -(s.size or 0))))
json.dump({"repo": a.repo, "revision": a.revision, "sha": info.sha, "files": res, "wall_s": time.time() - t0},
          open(os.path.join(a.out, "_download.json"), "w"), indent=1)
print("done", a.repo, a.revision, info.sha, f"{time.time() - t0:.0f}s", flush=True)
