#!/usr/bin/env python3
"""E175 (D1 pilot): is (deep-layer) routing predicted by the current input token or by the true next token,
and does that change along training?  CPU only; uses E167's routing cache S{l} (top-8 experts of the 29,551
word-final anchor tokens) plus a re-tokenisation of the UD EWT passages to get input / next token IDs.

Readouts (fixed in experiments/E175-d1-input-vs-next-token-routing.md before running):
  B  excess plug-in MI  dI(e; x) = I(e; x) - mean_20 I(e; shuffled x),  e = top-1 expert, and a top-8 version;
     x in {in_tok, next_tok, in_form, next_form, in_upos, next_upos, in_tok^next_tok};
     conditional dI(e; next | in), dI(e; in | next) with within-stratum shuffles as floor;
     frequency subset: anchors whose in_tok and next_tok both occur >= 20 times in the anchor set.
  A  OLMoE vocabulary specialization, k=1 and k=8, x with N_x >= 6; expert value = sample-weighted mean of
     N_{x,E}/N_x over samples routed to E; layer value = mean over 64 experts; raw and excess over shuffle.

Usage: e175_input_vs_next.py  -> results/e175/e175_readouts.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

WB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
TOKENIZER_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
OUT = WB / "results/e175"
E, K, NL = 64, 8, 12
N_SHUF, SEED = 20, 175
MIN_NX, MIN_FREQ = 6, 20
RUNS = ["I0D0", "I1D0", "I2D0", "I4D0", "I4D0R", "I3D0", "I5D0", "I0D1", "I1D1"]


def word_token_index(tok, passages, words):
    """Same rule as capture_routing.word_token_index; also returns the raw ids per passage."""
    enc, pos = [], np.full(len(words), -1, np.int64)
    for p in passages:
        e = tok(p["text"], add_special_tokens=False, return_offsets_mapping=True)
        enc.append((e["input_ids"], e["offset_mapping"]))
    for n, (pid, s, end, form, upos, split) in enumerate(words):
        ids, offs = enc[pid]
        for t, (a, b) in enumerate(offs):
            if a <= end - 1 < b:
                if b <= end:
                    pos[n] = t + 1
                break
    return enc, pos


def codes(v):
    return np.unique(np.asarray(v), return_inverse=True)[1].astype(np.int64)


def H(counts):
    c = counts[counts > 0].astype(np.float64)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def mi(e, x, nx):
    """plug-in I(e; x) in bits; e: (m,) in [0,E), x: (m,) codes in [0,nx)."""
    joint = np.bincount(x * E + e, minlength=nx * E)
    return H(np.bincount(e, minlength=E)) + H(np.bincount(x, minlength=nx)) - H(joint)


def shuffle_within(y, z, rng):
    """permute y within each stratum of z."""
    order = np.lexsort((rng.random(len(z)), z))  # sorted by z, random within z
    base = np.argsort(z, kind="stable")
    out = np.empty_like(y)
    out[base] = y[order]
    return out


def vocab_spec(e, x, nx, keep):
    """OLMoE eq. 8 aggregated per expert (sample-weighted) then averaged over experts with any sample."""
    e, x = e[keep], x[keep]
    joint = np.bincount(x * E + e, minlength=nx * E).reshape(nx, E).astype(np.float64)
    Nx = joint.sum(1, keepdims=True)
    spec = np.divide(joint, Nx, out=np.zeros_like(joint), where=Nx > 0)
    NE = joint.sum(0)
    val = (joint * spec).sum(0)
    ok = NE > 0
    return float((val[ok] / NE[ok]).mean())


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    P = json.loads((WB / "results/e167/passages.json").read_text())
    passages, words, sel = P["passages"], P["words"], P["sel"]
    enc, pos = word_token_index(tok, passages, words)
    sel_v = [n for n in sel if pos[n] >= 0]
    aw = np.load(CAP / "pairs.npz")["anchor_word"]
    assert len(sel_v) == len(aw) and np.array_equal(np.array(sel_v), aw), "anchor set mismatch with cache"
    ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())

    rows, in_tok, nx_tok, in_form, nx_form, in_upos, nx_upos = [], [], [], [], [], [], []
    for r, n in enumerate(aw):
        pid = words[n][0]
        ids = enc[pid][0]
        p = int(pos[n])  # model position (EOS prepended): input token = ids[p-1], next = ids[p]
        if p >= len(ids):
            continue
        nxt_word = words[n + 1] if n + 1 < len(words) and words[n + 1][0] == pid else None
        if nxt_word is None:
            continue
        rows.append(r)
        in_tok.append(ids[p - 1]); nx_tok.append(ids[p])
        in_form.append(words[n][3].lower()); nx_form.append(nxt_word[3].lower())
        in_upos.append(ann[n]["upos"]); nx_upos.append(ann[n]["next_upos"])
    rows = np.array(rows)
    m = len(rows)
    X = {"in_tok": codes(in_tok), "next_tok": codes(nx_tok), "in_form": codes(in_form), "next_form": codes(nx_form),
         "in_upos": codes(in_upos), "next_upos": codes(nx_upos)}
    X["in_tok^next_tok"] = codes(X["in_tok"] * 10 ** 6 + X["next_tok"])
    NX = {k: int(v.max()) + 1 for k, v in X.items()}
    cnt = {k: np.bincount(v)[v] for k, v in X.items()}
    sub = (cnt["in_tok"] >= MIN_FREQ) & (cnt["next_tok"] >= MIN_FREQ)
    data_meta = {
        "n_anchor_cache": int(len(aw)), "n_used": int(m), "dropped_no_next": int(len(aw) - m),
        "n_types": {k: NX[k] for k in X}, "H_x_bits": {k: H(np.bincount(v)) for k, v in X.items()},
        "freq_subset_n": int(sub.sum()), "min_freq_subset": MIN_FREQ, "min_nx_vocabspec": MIN_NX,
        "n_shuffles": N_SHUF, "seed": SEED, "same_next_word_as_tok_frac": None,
        "in_tok_examples": [tok.decode([i]) for i in in_tok[:8]], "next_tok_examples": [tok.decode([i]) for i in nx_tok[:8]],
    }
    print(json.dumps(data_meta, ensure_ascii=False), flush=True)

    single = ["in_tok", "next_tok", "in_form", "next_form", "in_upos", "next_upos", "in_tok^next_tok"]
    res = {"meta": data_meta, "runs": {}}
    for run in RUNS:
        files = sorted(CAP.glob(f"{run}__ckpt_*.npz"), key=lambda f: int(f.stem.split("_")[-1]))
        res["runs"][run] = {}
        for f in files:
            t = int(f.stem.split("_")[-1])
            Z = np.load(f)
            rng = np.random.default_rng([SEED, t % (2 ** 31)])
            per = []
            for l in range(NL):
                S = Z[f"S{l}"][rows].astype(np.int64)
                e1 = S[:, 0]
                d = {"H_e": H(np.bincount(e1, minlength=E))}
                perms = [rng.permutation(m) for _ in range(N_SHUF)]
                for name in single:
                    x = X[name]; nx = NX[name]
                    raw = mi(e1, x, nx)
                    fl = [mi(e1, x[pp], nx) for pp in perms]
                    d[f"I_{name}"] = raw; d[f"floor_{name}"] = float(np.mean(fl)); d[f"dI_{name}"] = raw - float(np.mean(fl))
                # top-8 version (each slot a sample)
                e8 = S.ravel()
                for name in ["in_tok", "next_tok", "in_upos", "next_upos"]:
                    x8 = np.repeat(X[name], K); nx = NX[name]
                    raw = mi(e8, x8, nx)
                    fl = [mi(e8, np.repeat(X[name][pp], K), nx) for pp in perms[:5]]
                    d[f"dI8_{name}"] = raw - float(np.mean(fl))
                # conditional: I(e; y | z) = I(e; y^z) - I(e; z); floor = shuffle y within z
                for y, z in [("next_tok", "in_tok"), ("in_tok", "next_tok"), ("next_upos", "in_upos"), ("in_upos", "next_upos")]:
                    yz = X["in_tok^next_tok"] if {y, z} == {"next_tok", "in_tok"} else codes(X[y] * 1000 + X[z])
                    nyz = int(yz.max()) + 1
                    raw = mi(e1, yz, nyz) - mi(e1, X[z], NX[z])
                    fl = []
                    for _ in range(N_SHUF):
                        ys = shuffle_within(X[y], X[z], rng)
                        yzs = codes(ys * 10 ** 6 + X[z])
                        fl.append(mi(e1, yzs, int(yzs.max()) + 1) - mi(e1, X[z], NX[z]))
                    d[f"cI_{y}|{z}"] = raw; d[f"cfloor_{y}|{z}"] = float(np.mean(fl)); d[f"dcI_{y}|{z}"] = raw - float(np.mean(fl))
                # frequency subset
                es = e1[sub]
                for name in ["in_tok", "next_tok"]:
                    xs = codes(X[name][sub]); nx = int(xs.max()) + 1
                    raw = mi(es, xs, nx)
                    ps = [np.random.default_rng([SEED, t % (2 ** 31), l, i]).permutation(len(xs)) for i in range(N_SHUF)]
                    d[f"dIsub_{name}"] = raw - float(np.mean([mi(es, xs[pp], nx) for pp in ps]))
                # readout A: OLMoE vocabulary specialization, k=1 and k=8
                for name in ["in_tok", "next_tok"]:
                    x = X[name]; nx = NX[name]; keep = cnt[name] >= MIN_NX
                    v1 = vocab_spec(e1, x, nx, keep)
                    f1 = np.mean([vocab_spec(e1, x[pp], nx, keep[pp]) for pp in perms[:5]])
                    keep8 = np.repeat(keep, K)
                    v8 = vocab_spec(e8, np.repeat(x, K), nx, keep8)
                    f8 = np.mean([vocab_spec(e8, np.repeat(x[pp], K), nx, np.repeat(keep[pp], K)) for pp in perms[:5]])
                    d[f"VS1_{name}"] = v1; d[f"VS1floor_{name}"] = float(f1)
                    d[f"VS8_{name}"] = v8; d[f"VS8floor_{name}"] = float(f8)
                per.append(d)
            res["runs"][run][str(t)] = per
            print(f"{run} {t:>11d} L11 dI in={per[11]['dI_in_tok']:.3f} next={per[11]['dI_next_tok']:.3f} "
                  f"next|in={per[11]['dcI_next_tok|in_tok']:.3f}  ({time.time() - t0:.0f}s)", flush=True)
        (OUT / "e175_readouts.json").write_text(json.dumps(res))
    (OUT / "e175_readouts.json").write_text(json.dumps(res))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
