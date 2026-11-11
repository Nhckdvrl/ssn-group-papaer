"""E186: T-only top-k + N_F top-k + tokmeta/meta of one store -> /tmp/xiang_e186/store_sat/<key> (saturation readout input)."""
import json, os, shutil, sys
import numpy as np
k = sys.argv[1]
src, dst = f"/tmp/xiang_e186/store/{k}", f"/tmp/xiang_e186/store_sat/{k}"
os.makedirs(dst, exist_ok=True)
a = np.load(f"{src}/topk.npy", mmap_mode="r")
out = np.lib.format.open_memmap(f"{dst}/topk.npy", mode="w+", dtype=np.uint8, shape=(a.shape[0], a.shape[1], 1, a.shape[3]))
for l in range(a.shape[0]):
    out[l, :, 0] = a[l, :, 0]
out.flush()
for f in ("topk_fix.npy", "tokmeta.npz", "meta.json"):
    shutil.copy(f"{src}/{f}", dst)
print("sat extract", k, out.shape)
