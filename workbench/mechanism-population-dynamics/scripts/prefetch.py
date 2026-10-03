"""Download checkpoints listed in census job files (lines: family repo rev out name) ahead of the GPU workers.
Rate-limit friendly: few threads, exponential backoff on HTTP 429. Usage: prefetch.py <jobfile> [threads]"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from huggingface_hub import snapshot_download

import mp_common as mc

jobs = [l.split() for l in open(sys.argv[1]) if l.strip()]
threads = int(sys.argv[2]) if len(sys.argv) > 2 else 4


def one(j):
    fam, repo, rev, out, name = j
    if (mc.RESULTS / out / f"{name}.json").exists():
        return
    pat = ["*.json", "*.safetensors"] if fam == "dd" else None
    for t in range(10):
        try:
            snapshot_download(repo, revision=rev, cache_dir=str(mc.HF_CACHE), allow_patterns=pat)
            print("ok", name, flush=True)
            return
        except Exception as e:
            time.sleep(min(30 * (t + 1), 300) if "429" in str(e) else 20)
    print("FAILED", name, flush=True)


with ThreadPoolExecutor(threads) as ex:
    list(ex.map(one, jobs))
print("prefetch done")
