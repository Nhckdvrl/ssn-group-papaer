"""Verify downloaded safetensors against the sha256 recorded by the HF API (LFS oid) for the pinned revision.
Usage: python3 verify_models.py <model_dir> [...]   (dir written by fetch_models.sh, contains REVISION)"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path


def lfs_shas(repo, rev):
    url = f"https://huggingface.co/api/models/{repo}/tree/{rev}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return {x["path"]: x["lfs"]["oid"] for x in json.loads(r.read()) if "lfs" in x}


def main():
    ok = True
    for d in map(Path, sys.argv[1:]):
        repo = d.name.replace("__", "/", 1)
        shas = lfs_shas(repo, (d / "REVISION").read_text().strip())
        for f, want in sorted(shas.items()):
            p = d / f
            if not p.exists():
                print("MISSING", repo, f); ok = False; continue
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for blk in iter(lambda: fh.read(1 << 24), b""):
                    h.update(blk)
            good = h.hexdigest() == want
            ok &= good
            print("OK " if good else "BAD", repo, f)
    print("ALL OK" if ok else "SOME BAD")


if __name__ == "__main__":
    main()
