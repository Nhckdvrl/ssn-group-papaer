#!/usr/bin/env python3
"""E175 POST-HOC A + B (added 2026-11-06, after seeing E175 results; main-session request). CPU only.

B  natural word stream: top-1 routing recomputed from the hidden cache (H_l W_l^T + b_l) on ALL valid UD words
   (113,118 word-final tokens; no per-type cap), endpoint + untrained, 3 init seeds (+ rerun pair at 3.2B).
A  predicted next token: from e175_predict_cpu.py (CPU fp32 forward) -> argmax prediction and top-1 routing on
   the same words, endpoint + 800M + 200M of the 3 init seeds.
Estimator = the E175 cross-fitted predictive information (scripts/e175_crossfit.py: 2-fold, seed 175, smoothing
A=8 toward the marginal; conditionals back off to the conditioning variable's table).
  G(x)          x in {in_tok, next_tok, pred_tok}
  G(y | z)      = CE[p(e|z)] - CE[p(e|y,z) backoff z]
Usage: e175_posthoc_ab.py B|A  -> results/e175/posthoc_B.json | posthoc_A.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from capture_routing import TOKENIZER_DIR, PASSAGES, word_token_index  # noqa: E402

WB = Path(__file__).resolve().parents[1]
HID = Path.home() / "mechpop_cache/e167_analysis/hidden"
PRED = Path.home() / "mechpop_cache/e175_predict"
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e175"
E, NL, A, SEED = 64, 12, 8.0, 175


def codes(v):
    return np.unique(np.asarray(v), return_inverse=True)[1].astype(np.int64)


def ce(p):
    return float(-np.log2(p).mean())


def table(e, x, nx, prior):
    N = np.bincount(x * E + e, minlength=nx * E).reshape(nx, E).astype(np.float64)
    return (N + A * prior) / (N.sum(1, keepdims=True) + A)


def crossfit(e, X, singles, conds, folds):
    """X: name -> codes. singles: names; conds: list of (y, z). Returns dict of bits averaged over 2 folds."""
    out = {}
    for k in range(2):
        tr, te = folds[k], folds[1 - k]
        etr, ete = e[tr], e[te]
        pm = (np.bincount(etr, minlength=E) + 1.0) / (len(etr) + E)
        base = ce(pm[ete])
        T, CE = {}, {}
        for nm in set(singles) | {z for _, z in conds}:
            x = X[nm]; nx = int(x.max()) + 1
            T[nm] = table(etr, x[tr], nx, pm)
            CE[nm] = ce(T[nm][x[te], ete])
        for nm in singles:
            out[f"G_{nm}"] = out.get(f"G_{nm}", 0) + (base - CE[nm]) / 2
        for y, z in conds:
            jj = codes(X[y] * 10 ** 6 + X[z]); n2 = int(jj.max()) + 1
            jz = np.zeros(n2, np.int64); jz[jj] = X[z]
            Tj = table(etr, jj[tr], n2, T[z][jz])
            out[f"G_{y}|{z}"] = out.get(f"G_{y}|{z}", 0) + (CE[z] - ce(Tj[jj[te], ete])) / 2
        out["H_e"] = out.get("H_e", 0) + base / 2
    return out


def word_tokens():
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    P = json.loads(PASSAGES.read_text())
    passages, words = P["passages"], P["words"]
    enc, pos = word_token_index(tok, passages, words)
    return words, enc, pos


def main():
    mode = sys.argv[1]
    words, enc, pos = word_tokens()
    if mode == "B":
        files = ["I0D0__ckpt_3999793152", "I1D0__ckpt_3999793152", "I2D0__ckpt_3999793152",
                 "I0D0__ckpt_0", "I1D0__ckpt_0", "I4D0__ckpt_3200000000", "I4D0R__ckpt_3200000000"]
        src = {f: HID / f"{f}.npz" for f in files}
    else:
        src = {f.stem: f for f in sorted(PRED.glob("*.npz"))}
    res = {"mode": mode, "A_smooth": A, "seed": SEED, "ckpts": {}}
    word_idx = None
    for name, path in src.items():
        Z = np.load(path)
        if word_idx is None:
            word_idx = Z["word_idx"]
            keep, tin, tnx = [], [], []
            for r, n in enumerate(word_idx):
                ids = enc[words[n][0]][0]; p = int(pos[n])
                if p < len(ids):
                    keep.append(r); tin.append(ids[p - 1]); tnx.append(ids[p])
            keep = np.array(keep)
            X0 = {"in_tok": codes(tin), "next_tok": codes(tnx)}
            rng = np.random.default_rng(SEED)
            perm = rng.permutation(len(keep))
            folds = [np.sort(perm[: len(keep) // 2]), np.sort(perm[len(keep) // 2:])]
            res["n_words"] = int(len(keep)); res["n_types_in"] = int(X0["in_tok"].max() + 1)
            res["n_types_next"] = int(X0["next_tok"].max() + 1)
            tnx_arr = np.array(tnx)
        assert np.array_equal(Z["word_idx"], word_idx)
        X = dict(X0)
        singles, conds = ["in_tok", "next_tok"], [("next_tok", "in_tok"), ("in_tok", "next_tok")]
        extra = {}
        if mode == "A":
            pr = Z["pred"][keep]
            X["pred_tok"] = codes(pr)
            singles += ["pred_tok"]
            conds += [("pred_tok", "in_tok"), ("in_tok", "pred_tok"), ("pred_tok", "next_tok"), ("next_tok", "pred_tok")]
            extra["top1_pred_acc"] = float((pr == tnx_arr).mean())
            extra["n_types_pred"] = int(X["pred_tok"].max() + 1)
        per = []
        for l in range(NL):
            if mode == "B":
                H = Z[f"H{l}"][keep].astype(np.float32)
                e = (H @ Z[f"W{l}"].T + Z[f"b{l}"]).argmax(1).astype(np.int64)
            else:
                e = Z["top1"][l][keep].astype(np.int64)
            per.append(crossfit(e, X, singles, conds, folds))
        if mode == "B" and name.startswith(("I0D0__ckpt_3999793152", "I0D0__ckpt_0")):
            # sanity: hidden-recomputed top-1 vs routing cache S_l[:,0] on the cached anchor subset
            Pz = np.load(CAP / "pairs.npz"); R = np.load(CAP / f"{name}.npz")
            rowof = {int(n): r for r, n in enumerate(word_idx)}
            rows = np.array([rowof[int(n)] for n in Pz["anchor_word"]])
            agree = []
            for l in range(NL):
                H = Z[f"H{l}"][rows].astype(np.float32)
                e = (H @ Z[f"W{l}"].T + Z[f"b{l}"]).argmax(1)
                agree.append(float((e == R[f"S{l}"][:, 0]).mean()))
            extra["top1_agree_with_routing_cache"] = agree
        res["ckpts"][name] = {"layers": per, **extra}
        print(name, json.dumps(extra)[:200], "L11 in=%.3f next=%.3f" % (per[11]["G_in_tok"], per[11]["G_next_tok"]),
              ("pred=%.3f" % per[11]["G_pred_tok"]) if mode == "A" else "", flush=True)
        (OUT / f"posthoc_{mode}.json").write_text(json.dumps(res))


if __name__ == "__main__":
    main()
