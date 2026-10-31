#!/usr/bin/env python3
"""E168 v3: token-level causal-role correspondence of experts across models (no basis maps).

capture: for one checkpoint and layers, disable each expert e (tokens that chose e use the (k+1)-th
         expert, gate kept) and store the per-token dNLL vector d_e over a fixed text (Dolma held-out
         eval windows, shared by all models), plus each token's top-k set at that layer.
compare: for models A, B and a layer, correlate d vectors between experts. Windows are split in two
         halves; Hungarian matching on half 1, evaluation on half 2 (and the reverse), against random
         matching. Also reported: the same correlation restricted to tokens routed to both e (in A) and
         pi(e) (in B), i.e. whether damage agrees beyond simply firing on the same tokens.

Usage: token_roles.py capture OUT_DIR LAYERS N_WIN CKPT [CKPT ...]
       token_roles.py compare DIR OUT_JSON LAYERS A_NAME:B_NAME [...]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).parent))
from transplant import load, windows, layer_states, BATCH, SEQ  # noqa: E402
from moe_model import rope_cache  # noqa: E402


@torch.no_grad()
def per_token_nll(model, rin, data, l, device, override=None):
    moe = model.blocks[l].moe
    moe.expert_override = override
    cos, sin = rope_cache(SEQ, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, device)
    out = []
    for i in range(0, len(data), BATCH):
        ids = data[i:i + BATCH].to(device)
        with torch.autocast("cuda", torch.bfloat16):
            x = rin[i:i + BATCH]
            for blk in model.blocks[l:]:
                x, *_ = blk(x, cos, sin)
            logits = model.head(model.norm(x))
        out.append(F.cross_entropy(logits.float().transpose(1, 2), ids[:, 1:], reduction="none"))
    moe.expert_override = None
    return torch.cat(out)  # n_win, SEQ


def capture(out_dir, layers, n_win, ckpts):
    device = torch.device("cuda")
    _, ev = windows(n_win)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ck in map(Path, ckpts):
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        model, tok = load(ck, device)
        res = {"tokens": tok, "n_win": n_win}
        for l in layers:
            _, _, rin = layer_states(model, ev, l, device)
            base = per_token_nll(model, rin, ev, l, device)
            moe = model.blocks[l].moe
            # top-k sets for every token at layer l
            topis = []
            for i in range(0, len(ev), BATCH):
                x = rin[i:i + BATCH]
                cos, sin = rope_cache(SEQ, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, device)
                blk = model.blocks[l]
                with torch.autocast("cuda", torch.bfloat16):
                    h = blk.n2(x + blk.attn(blk.n1(x), cos, sin))
                logits = F.linear(h.reshape(-1, h.shape[-1]).float(), moe.router.weight.float())
                topis.append((logits + moe.sel_bias).topk(moe.k, -1).indices.view(h.shape[0], h.shape[1], -1))
            topi = torch.cat(topis)
            D = np.zeros((moe.E, n_win, SEQ), np.float16)
            for e in range(moe.E):
                def drop(ti, tv, probs, scores, e=e):
                    nxt = scores.topk(moe.k + 1, -1).indices[:, moe.k:moe.k + 1]
                    return torch.where(ti == e, nxt, ti), tv
                D[e] = (per_token_nll(model, rin, ev, l, device, drop) - base).cpu().numpy().astype(np.float16)
            res[f"D{l}"] = D
            res[f"topi{l}"] = topi.cpu().numpy().astype(np.int8)
            res[f"base{l}"] = base.cpu().numpy().astype(np.float32)
            del rin
        np.savez_compressed(target, **res)
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1)}), flush=True)
        del model
        torch.cuda.empty_cache()


def corr_matrix(X, Y):
    X = X - X.mean(1, keepdims=True)
    Y = Y - Y.mean(1, keepdims=True)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    Y /= np.linalg.norm(Y, axis=1, keepdims=True) + 1e-12
    return X @ Y.T


def compare(d, out, layers, specs):
    rng = np.random.default_rng(168)
    results = []
    for spec in specs:
        a, b = spec.split(":")
        A, B = np.load(d / a), np.load(d / b)
        rec = {"A": a, "B": b, "layers": []}
        for l in layers:
            DA, DB = A[f"D{l}"].astype(np.float32), B[f"D{l}"].astype(np.float32)
            E, W, T = DA.shape
            h1, h2 = np.arange(W) < W // 2, np.arange(W) >= W // 2
            row = {"layer": l}
            for name, fit, ev in (("1to2", h1, h2), ("2to1", h2, h1)):
                Cf = corr_matrix(DA[:, fit].reshape(E, -1), DB[:, fit].reshape(E, -1))
                Ce = corr_matrix(DA[:, ev].reshape(E, -1), DB[:, ev].reshape(E, -1))
                ri, ci = linear_sum_assignment(-Cf)
                row[f"matched_{name}"] = float(Ce[ri, ci].mean())
                row[f"insample_{name}"] = float(Cf[ri, ci].mean())
                rand = [float(Ce[np.arange(E), rng.permutation(E)].mean()) for _ in range(200)]
                row[f"random95_{name}"] = [float(np.percentile(rand, 2.5)), float(np.percentile(rand, 97.5))]
                # beyond co-firing: correlation on tokens routed to both e (A) and pi(e) (B), eval half
                ta, tb = A[f"topi{l}"][ev].reshape(-1, A[f"topi{l}"].shape[-1]), B[f"topi{l}"][ev].reshape(-1, B[f"topi{l}"].shape[-1])
                cond = []
                for e, j in zip(ri, ci):
                    m = (ta == e).any(1) & (tb == j).any(1)
                    if m.sum() >= 50:
                        x, y = DA[e][ev].reshape(-1)[m], DB[j][ev].reshape(-1)[m]
                        cond.append(float(np.corrcoef(x, y)[0, 1]))
                row[f"cofire_corr_{name}"] = float(np.nanmean(cond)) if cond else None
                row[f"cofire_n_{name}"] = len(cond)
                row[f"per_unit_{name}"] = Ce[ri, ci].round(4).tolist()
            row["matched"] = (row["matched_1to2"] + row["matched_2to1"]) / 2
            rec["layers"].append(row)
            print(a, b, l, round(row["matched"], 3), row["random95_1to2"], row["cofire_corr_1to2"], flush=True)
        results.append(rec)
    Path(out).write_text(json.dumps({"results": results}, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "capture":
        capture(Path(sys.argv[2]), [int(x) for x in sys.argv[3].split(",")], int(sys.argv[4]), sys.argv[5:])
    else:
        compare(Path(sys.argv[2]), sys.argv[3], [int(x) for x in sys.argv[4].split(",")], sys.argv[5:])
