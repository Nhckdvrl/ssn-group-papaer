"""E185 residual follow-up (CPU, read-only on ~/mechpop_cache/e179): router-side per-layer statistics.
For each layer: router-input norm / anisotropy / PCA, between-group variance fractions (position bucket, pos==0,
language), trained-gate alignment with the input's top PCs and mean direction, T vs Haar-rotated gate (N_A-style)
per-token softmax entropy, top-1 usage entropy, and floor-corrected MI(top-1; position bucket / language).
Also E179 tallies (all measured tokens): top-k load entropy for T, N_A, N_B, N_G per layer.
usage: e185x_layerstats.py <key> -> ~/mechpop_cache/atlas_e185/resid/ls_<key>.json"""
import json, os, sys
import numpy as np
import torch

key = sys.argv[1]
base = f"/home/xiang/mechpop_cache/e179/{key}"
meta = json.load(open(f"{base}/meta.json"))
L, E, K, d = meta["L"], meta["E"], meta["K"], meta["d"]
X = np.load(f"{base}/toksub.npy", mmap_mode="r")
W = np.load(f"{base}/gateW.npy")
ids = np.load(os.path.expanduser(f"~/mechpop_cache/atlas_e185/toksub_ids_{key}.npz"))
pos, lang = ids["pos"], ids["lang"]
posb = np.where(pos < 4, pos, np.minimum(np.floor(np.log2(np.maximum(pos, 1))).astype(np.int64) + 2, 10))
torch.set_num_threads(8)
rng = np.random.default_rng(1851)
NROT = 3
gen = torch.Generator().manual_seed(1852)
ROT = []
for _ in range(NROT):
    Q, Rr = torch.linalg.qr(torch.randn(d, d, generator=gen, dtype=torch.float64))
    ROT.append((Q * torch.sign(torch.diagonal(Rr))).float())


def H(c):
    c = c[c > 0].astype(np.float64); p = c / c.sum(); return float(-(p * np.log2(p)).sum())


def mi_floor(e, x, nsh=5):
    def mi(xx):
        n = e.size; j = xx.astype(np.int64) * E + e
        return H(np.bincount(e, minlength=E)) + H(np.bincount(xx)) - H(np.bincount(j))
    I = mi(x); fl = np.mean([mi(rng.permutation(x)) for _ in range(nsh)])
    return float(I - fl)


def between_frac(Hc, g):
    """fraction of total (centered) variance explained by group means of g."""
    tot = float((Hc ** 2).sum())
    b = 0.0
    for v in np.unique(g):
        m = g == v
        b += m.sum() * float((Hc[m].mean(0) ** 2).sum())
    return b / tot


out = {k: [] for k in ["norm_mean", "norm_cv", "meandir_share", "pc1_share", "pc5_share", "pr", "pos_frac",
                       "pos0_frac", "pos_frac_excl0", "lang_frac", "gate_pc1_align", "gate_pc5_align",
                       "gate_meandir_align", "T_tok_entropy", "R_tok_entropy", "T_usage_H", "R_usage_H",
                       "T_logit_sd", "R_logit_sd", "T_mi_pos", "R_mi_pos", "T_mi_lang", "R_mi_lang",
                       "T_mi_pos_excl0", "R_mi_pos_excl0", "pos0_T_top1_mode_frac", "pos0_norm_ratio"]}
for l in range(L):
    Hh = np.asarray(X[l], dtype=np.float32)
    n = np.linalg.norm(Hh, axis=1)
    out["norm_mean"].append(float(n.mean())); out["norm_cv"].append(float(n.std() / n.mean()))
    mu = Hh.mean(0)
    out["meandir_share"].append(float((mu ** 2).sum() / (n ** 2).mean()))
    Hc = Hh - mu
    C = torch.from_numpy(Hc).double()
    ev, U = torch.linalg.eigh(C.T @ C / C.shape[0])
    ev, U = ev.flip(0).numpy(), U.flip(1).numpy()
    out["pc1_share"].append(float(ev[0] / ev.sum())); out["pc5_share"].append(float(ev[:5].sum() / ev.sum()))
    out["pr"].append(float(ev.sum() ** 2 / (ev ** 2).sum()))
    out["pos_frac"].append(between_frac(Hc, posb)); out["pos0_frac"].append(between_frac(Hc, (pos == 0).astype(int)))
    m1 = pos > 0
    out["pos_frac_excl0"].append(between_frac(Hc[m1] - Hc[m1].mean(0), posb[m1]))
    out["lang_frac"].append(between_frac(Hc, lang))
    out["pos0_norm_ratio"].append(float(n[pos == 0].mean() / n[pos > 0].mean()))
    Wl = W[l].astype(np.float64); wf = (Wl ** 2).sum()
    out["gate_pc1_align"].append(float(((Wl @ U[:, :1]) ** 2).sum() / wf * d / 1))
    out["gate_pc5_align"].append(float(((Wl @ U[:, :5]) ** 2).sum() / wf * d / 5))
    mh = mu / np.linalg.norm(mu)
    out["gate_meandir_align"].append(float(((Wl @ mh) ** 2).sum() / wf * d))
    Ht = torch.from_numpy(Hh)
    Wt = torch.from_numpy(W[l]).float()
    res = {}
    for tag, Ws in [("T", [Wt])] + [("R", [Wt @ R for R in ROT])]:
        te, ue, sd, mp, ml, mp1 = [], [], [], [], [], []
        for Wx in Ws:
            Z = Ht @ Wx.T
            P = torch.softmax(Z, -1)
            te.append(float((-(P * P.clamp_min(1e-30).log2()).sum(-1)).mean()))
            sd.append(float(Z.std(0).mean()))
            top = Z.topk(K, -1).indices.numpy()
            ue.append(H(np.bincount(top.ravel(), minlength=E)))
            e1 = top[:, 0].astype(np.int64)
            mp.append(mi_floor(e1, posb)); ml.append(mi_floor(e1, lang)); mp1.append(mi_floor(e1[m1], posb[m1]))
            if tag == "T":
                c = np.bincount(e1[pos == 0], minlength=E); out["pos0_T_top1_mode_frac"].append(float(c.max() / c.sum()))
        res[tag] = [np.mean(v) for v in (te, ue, sd, mp, ml, mp1)]
    for tag in "TR":
        a = res[tag]
        out[f"{tag}_tok_entropy"].append(a[0]); out[f"{tag}_usage_H"].append(a[1]); out[f"{tag}_logit_sd"].append(a[2])
        out[f"{tag}_mi_pos"].append(a[3]); out[f"{tag}_mi_lang"].append(a[4]); out[f"{tag}_mi_pos_excl0"].append(a[5])
    print(key, l, {k: round(v[-1], 3) for k, v in out.items()}, flush=True)

tl = np.load(f"{base}/tallies.npz")
cnt = tl["counts"].sum(2)  # [L, NR, E]
ri = meta["router_index"]
def loadH(r):
    return [H(cnt[l, r]) for l in range(L)]
out["load_H_T"] = loadH(0)
for fam in ["N_A", "N_B", "N_G"]:
    a, b = ri[fam]
    out[f"load_H_{fam}"] = [float(np.mean([H(cnt[l, r]) for r in range(a, b + 1)])) for l in range(L)]
for k in ["entT_full", "entB_full", "loadtv_B", "sT"]:
    v = tl[k]; out["cal_" + k] = (v.mean(1) if v.ndim == 2 else v).tolist()
json.dump(out, open(os.path.expanduser(f"~/mechpop_cache/atlas_e185/resid/ls_{key}.json"), "w"))
print("done")
