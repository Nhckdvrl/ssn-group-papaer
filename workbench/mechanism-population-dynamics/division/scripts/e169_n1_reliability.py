#!/usr/bin/env python3
"""E169 addendum: Monte-Carlo reliability of the N1 residual D = C - E_N1[C] (32 draws in E167).

From the hidden-state captures (H, W, b) recompute the N1 expectation twice with independent draw seeds
(B1: seed 167 as in E167, B2: seed 1167) for a few models and layers, on E167's pre-registered word pairs:
  rel_D   : corr(D1, D2) within one model  (how much of D is Monte-Carlo noise of the null)
  corr_B  : corr(B1, B2) within one model
  check   : corr(B1 recomputed, B captured in E167)  (same seed; differences come from fp16 H vs bf16 in-situ)
  T_D     : cross-model corr using 32-draw residuals (D1_A, D1_B), mixed seeds (D1_A, D2_B), and 64-draw
            residuals (D64_A, D64_B)  -> if MC noise limited T_D, the 64-draw value is higher.
Usage: e169_n1_reliability.py TOKENS [LAYERS] [MODELS]   -> results/e169/n1_reliability_<TOKENS>.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
import moe_measure as mm  # noqa: E402

torch.set_num_threads(4)
WB = Path(__file__).resolve().parents[1]
AN = Path.home() / "mechpop_cache/e167_analysis"
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
LAYERS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [2, 5, 8, 11]
MODELS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["I0D0", "I1D0", "I0D1", "I1D1"]
TOPK, N_DRAWS = 8, 32
P = np.load(AN / "routing/pairs.npz")
pi, pj, ptype, aw = P["i"], P["j"], P["type"], P["anchor_word"]
nT = int(ptype.max()) + 1
pairs_t = (torch.tensor(pi), torch.tensor(pj))


def cw(x):
    s = np.bincount(ptype, x, nT); c = np.bincount(ptype, None, nT)
    return x - (s / np.maximum(c, 1))[ptype]


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))


Z = {r: np.load(AN / f"hidden/{r}__ckpt_{tok}.npz") for r in MODELS}
R = {r: np.load(AN / f"routing/{r}__ckpt_{tok}.npz") for r in MODELS}
rows = {int(w): n for n, w in enumerate(Z[MODELS[0]]["word_idx"])}
sel = np.array([rows[int(w)] for w in aw]); n_anchor = int(Z[MODELS[0]]["n_anchor"])
out = {"tokens": tok, "n_draws": N_DRAWS, "layers": []}
for l in LAYERS:
    t0 = time.time()
    per = {}
    for r in MODELS:
        H = Z[r][f"H{l}"].astype(np.float32)
        Ha = torch.tensor(H[sel]).double(); Hc = torch.tensor(H[n_anchor:]).double()
        W = torch.tensor(Z[r][f"W{l}"]).double(); b = torch.tensor(Z[r][f"b{l}"]).double()
        S = (Ha @ W.T + b).topk(TOPK, -1).indices
        C = mm.coroute(S, W.shape[0], TOPK, pairs_t).numpy().astype(float)
        B1 = mm.null_expectation(W, b, Hc, Ha, TOPK, "N1", n_draws=N_DRAWS, seed=167, pairs=pairs_t)["B"].numpy().astype(float)
        B2 = mm.null_expectation(W, b, Hc, Ha, TOPK, "N1", n_draws=N_DRAWS, seed=1167, pairs=pairs_t)["B"].numpy().astype(float)
        Bcap = R[r][f"B{l}"].astype(float); Ccap = R[r][f"C{l}"].astype(float)
        per[r] = {"C": cw(C), "D1": cw(C - B1), "D2": cw(C - B2), "D64": cw(C - (B1 + B2) / 2), "Dcap": cw(Ccap - Bcap),
                  "rel_D": corr(cw(C - B1), cw(C - B2)), "corr_B": corr(cw(B1), cw(B2)), "check_B": corr(cw(B1), cw(Bcap)), "check_C": corr(cw(C), cw(Ccap))}
    row = {"layer": l, "per_model": {r: {k: per[r][k] for k in ("rel_D", "corr_B", "check_B", "check_C")} for r in MODELS}}
    groups = {"init": [(a, b) for a in MODELS for b in MODELS if a < b and a[:2] != b[:2] and a[2:] == b[2:] == "D0"],
              "order": [(a, b) for a in MODELS for b in MODELS if a < b and a[:2] == b[:2]]}
    for g, prs in groups.items():
        if not prs:
            continue
        row[f"T_D32_{g}"] = float(np.mean([corr(per[a]["D1"], per[b]["D1"]) for a, b in prs]))
        row[f"T_Dmix_{g}"] = float(np.mean([corr(per[a]["D1"], per[b]["D2"]) for a, b in prs]))
        row[f"T_D64_{g}"] = float(np.mean([corr(per[a]["D64"], per[b]["D64"]) for a, b in prs]))
        row[f"T_Dcap_{g}"] = float(np.mean([corr(per[a]["Dcap"], per[b]["Dcap"]) for a, b in prs]))
        row[f"pairs_{g}"] = prs
    out["layers"].append(row)
    pm = row["per_model"]
    print(f"L{l:2d} ({time.time()-t0:.0f}s) rel_D {np.mean([pm[r]['rel_D'] for r in MODELS]):.3f} corr_B {np.mean([pm[r]['corr_B'] for r in MODELS]):.3f} check_B {np.mean([pm[r]['check_B'] for r in MODELS]):.3f} check_C {np.mean([pm[r]['check_C'] for r in MODELS]):.3f} | "
          + " | ".join(f"{g}: T_D32 {row[f'T_D32_{g}']:.3f} mix {row[f'T_Dmix_{g}']:.3f} T_D64 {row[f'T_D64_{g}']:.3f} cap {row[f'T_Dcap_{g}']:.3f}" for g in groups if f"T_D32_{g}" in row), flush=True)
    (WB / "results/e169").mkdir(exist_ok=True)
    (WB / f"results/e169/n1_reliability_{tok}.json").write_text(json.dumps(out))
print("saved")
