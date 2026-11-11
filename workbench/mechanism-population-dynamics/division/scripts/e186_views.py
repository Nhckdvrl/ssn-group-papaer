#!/usr/bin/env python3
"""E186: cut one E186 store into the two E185-compatible views (card: division/experiments/E186-atlas-capture-breadth.md).
  <VIEWS>/e184/<key>/  English: FLORES eng_Latn (corpus 0) + UD EWT (corpus 1); tokmeta like e184 (seq renumbered)
  <VIEWS>/e180/<key>/  the 20 E180 sides (side index = E180 lang index); tokmeta like e180 (lang, sid, pos, inp, pred,
                       sel with E180's per-sentence group equalisation, seed 180), plus nxt
Both carry 17 routers in the E185 layout (0 T | 1-8 N_A | 9-16 N_B): the multilingual view's N_B is the store's N_B
(calibrated on the 20 non-English sides); the English view's "N_B" columns are the store's N_Ben (same N1 matrices,
bias calibrated on FLORES eng + UD; 补登记 11-09 22:20). Original store is read-only.
usage: e186_views.py KEY [--views ~/mechpop_cache/e186_views]"""
import argparse, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("key")
ap.add_argument("--src", default=os.path.expanduser("~/mechpop_cache/e186"))
ap.add_argument("--views", default=os.path.expanduser("~/mechpop_cache/e186_views"))
a = ap.parse_args()
base = f"{a.src}/{a.key}"
meta = json.load(open(f"{base}/meta.json"))
tm = dict(np.load(f"{base}/tokmeta.npz"))
topk = np.load(f"{base}/topk.npy", mmap_mode="r")
L = meta["L"]
sides = meta["sides"]
eng = sides.index("eng_Latn")
side, corpus = tm["side"].astype(np.int64), tm["corpus"].astype(np.int64)


D = meta["draws"]
COLS_ML = list(range(0, 1 + 2 * D))
COLS_EN = list(range(0, 1 + D)) + list(range(1 + 2 * D, 1 + 3 * D)) if "N_Ben" in meta["router_index"] else COLS_ML


def write(sub, out, tmeta, extra, cols):
    os.makedirs(out, exist_ok=True)
    arr = np.lib.format.open_memmap(f"{out}/topk.npy", mode="w+", dtype=np.uint8,
                                    shape=(L, sub.size, len(cols), topk.shape[3]))
    for l in range(L):
        arr[l] = np.asarray(topk[l])[sub][:, cols]
    arr.flush()
    del arr
    np.savez(f"{out}/tokmeta.npz", **tmeta)
    m = {k: meta[k] for k in ("L", "E", "K", "d", "draws", "router_index", "moe_layers", "arch", "key")}
    m.update(extra)
    m["source_store"] = base
    m["source_router_columns"] = cols
    m["router_index"] = {"T": [0], "N_A": [1, D], "N_B": [1 + D, 2 * D]}
    json.dump(m, open(f"{out}/meta.json", "w"), indent=1)


# ---------------- English view (E184 layout)
sub = np.where((corpus == 1) | (side == eng))[0]
seq_old = tm["seq"][sub].astype(np.int64)
_, seq_new = np.unique(seq_old, return_inverse=True)
t184 = {"corpus": tm["corpus"][sub], "seq": seq_new.astype(np.int32), "pos": tm["pos"][sub], "inp": tm["inp"][sub],
        "pred": tm["pred"][sub], "nxt": tm["nxt"][sub], "upos": tm["upos"][sub], "word": tm["word"][sub],
        "pent": tm["pent"][sub], "nxt_lp": tm["nxt_lp"][sub]}
write(sub, f"{a.views}/e184/{a.key}", t184,
      {"upos": meta["upos"], "ntok": {"flores": int((tm["corpus"][sub] == 0).sum()), "ud": int((tm["corpus"][sub] == 1).sum())},
       "routers": ["T"] + [f"N_A{i}" for i in range(D)] + [f"N_B{i}" for i in range(D)],
       "N_B_is": "N_Ben (English-calibrated)" if COLS_EN != COLS_ML else "N_B"}, COLS_EN)
print("e184 view", sub.size, flush=True)

# ---------------- multilingual view (E180 layout; sides 0..19)
langs = [s for s in sides if s != "eng_Latn"]
assert sides[:len(langs)] == langs
sub = np.where((corpus == 0) & (side != eng))[0]
lang, sid, pos = side[sub], tm["sid"][sub].astype(np.int64), tm["pos"][sub].astype(np.int64)
NS = meta["n_sent"]
# E180 equalisation: n_s = min length of sentence s over the group's sides; uniform positions w/o replacement, seed 180
start = np.r_[True, (lang[1:] != lang[:-1]) | (sid[1:] != sid[:-1])]
st_idx = np.where(start)[0]
seg_len = np.diff(np.r_[st_idx, sub.size])
seg_of = {(int(lang[i]), int(sid[i])): (i, n) for i, n in zip(st_idx, seg_len)}
sel = np.zeros(sub.size, bool)
rs = np.random.default_rng(180)
nsel = {}
for g, gl in meta["groups"].items():
    gi = [langs.index(x) for x in gl]
    for s in range(NS):
        n_s = min(seg_of[(li, s)][1] for li in gi)
        for li in gi:
            i0, n = seg_of[(li, s)]
            sel[i0 + rs.choice(n, n_s, replace=False)] = True
    nsel[g] = int(sum(seg_of[(gi[0], s)][1] * 0 + min(seg_of[(li, s)][1] for li in gi) for s in range(NS)))
t180 = {"lang": lang.astype(np.int32), "sid": sid.astype(np.int32), "pos": pos.astype(np.int32),
        "inp": tm["inp"][sub].astype(np.int32), "pred": tm["pred"][sub].astype(np.int32), "nxt": tm["nxt"][sub],
        "sel": sel, "pent": tm["pent"][sub], "nxt_lp": tm["nxt_lp"][sub]}
write(sub, f"{a.views}/e180/{a.key}", t180,
      {"langs": langs, "groups": meta["groups"], "n_sent": NS, "nsel": nsel,
       "topk_routers": ["T"] + [f"N_A{i}" for i in range(D)] + [f"N_B{i}" for i in range(D)], "N_B_is": "N_B (multilingual-calibrated)",
       "ntok": {lg: int((lang == i).sum()) for i, lg in enumerate(langs)}}, COLS_ML)
print("e180 view", sub.size, nsel, flush=True)
