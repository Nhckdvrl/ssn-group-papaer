"""E187 读数 5 (weights): lag test on Instruct and Base, same rule as e185x_weights.py: flattened cosine of q / o / v
between every layer pair, averaged per lag.  Writes results/e187/base_lagtest.json."""
import json, os
import numpy as np
C = os.path.expanduser("~/mechpop_cache/e187")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e187")
out = {}
for key in ("instruct", "base"):
    a = np.load(f"{C}/w_{key}/attn.npz")
    sims = {}
    for p in "qov":
        M = a[p].reshape(48, -1).astype(np.float32); M /= np.linalg.norm(M, axis=1, keepdims=True)
        sims[p] = M @ M.T
    lag = {t: [float(np.mean([sims[p][i, i + t] for i in range(48 - t)])) for p in "qov"] for t in range(1, 47)}
    other = max(abs(v) for t, vs in lag.items() if t not in (12, 24) for v in vs)
    pairs12 = [float(sims["q"][i, i + 12]) for i in range(36)]
    out[key] = {"12": lag[12], "24": lag[24], "other_max": other, "q_lag12_by_l": pairs12}
    print(key, lag[12], lag[24], other)
json.dump(out, open(f"{RES}/base_lagtest.json", "w"), indent=0)
