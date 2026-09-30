"""Pull a whole HF repo with parallel ranged downloads for large files (per-connection HF throughput here ~0.1-0.3 MB/s).
usage: hf_pull.py <repo> <local_dir> [nconn]"""
import json, os, subprocess, sys, urllib.request
repo, dst = sys.argv[1], sys.argv[2]
n = sys.argv[3] if len(sys.argv) > 3 else "32"
fs = json.load(urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/tree/main?recursive=true", timeout=60))
procs = []
for f in fs:
    if f["type"] != "file":
        continue
    p = os.path.join(dst, f["path"])
    if os.path.exists(p) and os.path.getsize(p) == f["size"]:
        continue
    url = f"https://huggingface.co/{repo}/resolve/main/{f['path']}"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if f["size"] > 200_000_000:
        procs.append(subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "pdl.py"), url, p, str(f["size"]), n]))
    else:
        urllib.request.urlretrieve(url, p)
for pr in procs:
    pr.wait()
print("done", repo)
