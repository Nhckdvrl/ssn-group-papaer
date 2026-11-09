"""E185 residual follow-up: reconstruct (lang, sid, pos, cur id, prev id, next id) for every row of E179 toksub.npy.
E179 saved only (lang, sid); the selection is deterministic (default_rng(179), same tokenizer call), so we replay it
and check against toksub_meta.npz.  CPU only; writes ~/mechpop_cache/atlas_e185/toksub_ids_<model>.npz."""
import json, os, sys
import numpy as np
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer

FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
key = sys.argv[1]
base = f"/home/xiang/mechpop_cache/e179/{key}"
meta = json.load(open(f"{base}/meta.json"))
tm = np.load(f"{base}/toksub_meta.npz")
tok = AutoTokenizer.from_pretrained(meta["model"])
rs = np.random.default_rng(179)
rows = []
for li, lg in enumerate(meta["langs"]):
    ss = [x.rstrip("\n") for x in open(f"{FLORES}/dev/{lg}.dev", encoding="utf-8")][:meta["n_sent"]]
    seqs = [tok(s, add_special_tokens=False)["input_ids"] for s in ss]
    lens = np.array([len(x) for x in seqs])
    off = np.concatenate([[0], np.cumsum(lens)])
    pick = np.sort(rs.choice(off[-1], 1000, replace=False))
    for g in pick:
        sid = int(np.searchsorted(off, g, side="right") - 1)
        p = int(g - off[sid]); s = seqs[sid]
        rows.append((li, sid, p, s[p], s[p - 1] if p > 0 else -1, s[p + 1] if p + 1 < len(s) else -1, len(s)))
a = np.array(rows, np.int64)
assert (a[:, 0] == tm["lang"]).all() and (a[:, 1] == tm["sid"]).all(), "replay mismatch"
out = os.path.expanduser(f"~/mechpop_cache/atlas_e185/toksub_ids_{key}.npz")
np.savez(out, lang=a[:, 0], sid=a[:, 1], pos=a[:, 2], cur=a[:, 3], prev=a[:, 4], nxt=a[:, 5], slen=a[:, 6])
print(key, "ok", a.shape, "pos0 frac", (a[:, 2] == 0).mean())
