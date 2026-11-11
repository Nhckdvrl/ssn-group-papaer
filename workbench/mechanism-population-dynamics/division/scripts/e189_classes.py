"""E189 readouts 6-7 (card: division/experiments/E189-training-axis-routing-decomposition.md): O / H / R (mid band
2-11, top-1 and top-8, vs release) by token class at t in {20B, 335B, 1.34T, 5.1T}, and raw per-id examples.
Inputs (node-local): /tmp/xiang_e186/e189/{pertok.npz, prep.npz, prep.json}.  Writes e189/classes.json."""
import json
import numpy as np

OUT = "/tmp/xiang_e186/e189"
PT = np.load(f"{OUT}/pertok.npz")["PT"]                      # [9, 5 comps, 2 (top1, top8), N]
P = np.load(f"{OUT}/prep.npz", allow_pickle=True)
J = json.load(open(f"{OUT}/prep.json"))
ctx, strs, langs = J["contexts"], J["strs"], J["langs"]
N = PT.shape[-1]
COMPS = ["O", "H", "R", "Hp", "Rp"]
TS = {"20B": 0, "335B": 2, "1.34T": 6, "5.1T": 7}
clus = P["clus"]; NC = int(clus.max()) + 1
rng = np.random.default_rng(1892)
BOOT = np.stack([np.bincount(rng.integers(0, NC, NC), minlength=NC) for _ in range(1000)]).astype(np.float64)


def ci(v, m):
    s = np.bincount(clus[m], v[m], NC); c = np.bincount(clus[m], None, NC)
    b = (BOOT @ s) / np.maximum(BOOT @ c, 1e-9)
    return [float(np.quantile(b, .025)), float(np.quantile(b, .975))]


script = P["script"]
scripts = sorted(set(script.tolist()))
classes = {
    "position": (P["posb"], ["0 句首", "1–3", "4–15", "16–63", "≥64"]),
    "letter": (P["cls"], ["字母", "非字母", "UTF-8 片段"]),
    "freq_quintile": (P["fq"], ["Q1 最稀", "Q2", "Q3", "Q4", "Q5 最常见"]),
    "language": (P["src"], langs),
    "script": (np.array([scripts.index(s) for s in script]), scripts),
    "Hid_tertile": (P["hter"], ["低 H(e|id)（词表式）", "中", "高 H(e|id)（上下文式）"]),
    "upos_group_UD": (P["upg"], ["功能词", "内容词", "标点"]),
}
out = {"classes": {}}
for cname, (lab, names) in classes.items():
    rows = []
    for v, nm in enumerate(names):
        m = lab == v
        if m.sum() == 0:
            continue
        r = {"class": nm, "n": int(m.sum())}
        for tn, t in TS.items():
            for ci_, c in enumerate(COMPS[:3]):
                r[f"{c}_top1@{tn}"] = float(PT[t, ci_, 0, m].mean())
                r[f"{c}_top8@{tn}"] = float(PT[t, ci_, 1, m].mean())
                if tn in ("20B", "1.34T"):
                    r[f"{c}_top8@{tn}_ci"] = ci(PT[t, ci_, 1], m)
        rows.append(r)
    out["classes"][cname] = rows
out["coverage"] = {"Hid": float((P["hter"] >= 0).mean()), "upos_UD": float((P["upg"] >= 0).mean())}

inp = P["inp"]
u, inv, cnt = np.unique(inp, return_inverse=True, return_counts=True)
ok = np.where(cnt >= 30)[0]
out["examples"] = {"n_ids_ge30": int(ok.size), "token_coverage": float(np.isin(inv, ok).mean())}
for tn in ("20B", "1.34T"):
    t = TS[tn]
    per = []
    for j in ok:
        m = inv == j
        idx = np.where(m)[0]
        O8, H8, R8 = (float(PT[t, c, 1, m].mean()) for c in range(3))
        # context snippets: lowest- and highest-O occurrences
        oo = PT[t, 0, 1, idx]
        per.append({"id": int(u[j]), "str": strs[str(int(u[j]))], "n": int(m.sum()), "O": O8, "H": H8, "R": R8,
                    "R_minus_H": R8 - H8, "langs": sorted({langs[int(a)] for a in P["src"][idx]})[:4],
                    "ctx_lowO": ctx[int(idx[np.argmin(oo)])], "ctx_highO": ctx[int(idx[np.argmax(oo)])]})
    per.sort(key=lambda d: d["O"])
    out["examples"][tn] = {"lowest_O": per[:20], "highest_O": per[-20:][::-1],
                           "R_gt_H": sorted(per, key=lambda d: -d["R_minus_H"])[:10],
                           "H_gt_R": sorted(per, key=lambda d: d["R_minus_H"])[:10]}
json.dump(out, open(f"{OUT}/classes.json", "w"), ensure_ascii=False, indent=0)
print("ok", out["coverage"], out["examples"]["n_ids_ge30"])
