#!/usr/bin/env python3
"""E172 readout 2: Antoine et al. 2024 (arXiv 2412.16971) single-model readouts on our runs, and their
cross-seed stability.
 (a) Spec_{POS,l}: share of the routing slots of all tokens of a UPOS taken by the k=8 experts that take most
     of them; U = 8/64; dUpp = (Spec - U) * 100.  Model-level = n_p-weighted mean over UPOS.
 (b) routing-path probe: 12 x 64 multi-hot of top-8 experts -> UPOS, multinomial logistic regression,
     fixed 2/3 : 1/3 token split (seed 172, same for every run); baseline = most common UPOS of the word form
     in the training split (unseen forms -> majority class). Per-layer 64-d probes as a depth profile.
Uses S{l} (top-8 expert ids of the 29,551 anchor tokens) only.

Usage: e172_antoine_readouts.py [TOKENS]   -> results/e172/antoine_<TOKENS>.json
"""
import collections
import itertools
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")
WB = Path(__file__).resolve().parents[1]
CAP = Path.home() / "mechpop_cache/e167_analysis/routing"
OUT = WB / "results/e172"
K, E, NL = 8, 64, 12
U = K / E
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3200000000

P = np.load(CAP / "pairs.npz")
upos = P["anchor_upos"]
form = np.char.lower(P["anchor_type"].astype(str))
n = len(upos)
UP = sorted(set(upos))
cnt = collections.Counter(upos)
PROF = [u for u in UP if cnt[u] >= 200]
yi = np.array([UP.index(u) for u in upos])
rng = np.random.default_rng(172)
perm = rng.permutation(n)
tr, te = np.sort(perm[: 2 * n // 3]), np.sort(perm[2 * n // 3:])

# word-form baseline
fm = collections.defaultdict(collections.Counter)
for f, u in zip(form[tr], upos[tr]):
    fm[f][u] += 1
maj = collections.Counter(upos[tr]).most_common(1)[0][0]
base_pred = np.array([fm[f].most_common(1)[0][0] if f in fm else maj for f in form[te]])
base = {"acc": float((base_pred == upos[te]).mean()), "macro_f1": float(f1_score(upos[te], base_pred, average="macro")),
        "unseen_form_frac": float(np.mean([f not in fm for f in form[te]]))}


def spec(S):
    """S: (n, 8) expert ids for one layer -> {upos: Spec}"""
    out = {}
    for u in UP:
        c = np.bincount(S[upos == u].ravel().astype(np.int64), minlength=E)
        out[u] = float(np.sort(c)[::-1][:K].sum() / c.sum())
    return out


def multihot(S):
    X = np.zeros((n, E), np.float32)
    np.put_along_axis(X, S.astype(np.int64), 1.0, 1)
    return X


def probe(X):
    clf = LogisticRegression(C=1.0, max_iter=500, n_jobs=8)
    clf.fit(X[tr], yi[tr])
    p = clf.predict(X[te])
    return {"acc": float((p == yi[te]).mean()), "macro_f1": float(f1_score(yi[te], p, average="macro"))}


def have(r, t):
    return (CAP / f"{r}__ckpt_{t}.npz").exists()


inits = [f"I{i}D0" for i in range(6) if have(f"I{i}D0", tok)]
others = [r for r in ("I0D1", "I1D1", "I4D0R", "I0D0R") if have(r, tok)]
runs = inits + others
models = {f"{r}@{tok}": (r, tok) for r in runs}
models.update({f"{r}@0": (r, 0) for r in ("I0D0", "I1D0")})
res = {}
for name, (r, t) in models.items():
    Z = np.load(CAP / f"{r}__ckpt_{t}.npz")
    S = [Z[f"S{l}"] for l in range(NL)]
    sp = [spec(S[l]) for l in range(NL)]
    w = np.array([cnt[u] for u in UP], float)
    model_spec = [float(np.dot([sp[l][u] for u in UP], w) / w.sum()) for l in range(NL)]
    Xs = [multihot(S[l]) for l in range(NL)]
    full = probe(np.concatenate(Xs, 1))
    per_layer = [probe(X)["acc"] for X in Xs]
    res[name] = {"spec": sp, "model_spec": model_spec, "probe_all": full, "probe_layer_acc": per_layer}
    print(f"{name:18s} Spec(model) L0 {model_spec[0]:.3f} L5 {model_spec[5]:.3f} L11 {model_spec[11]:.3f} mean {np.mean(model_spec):.3f} | "
          f"probe {full['acc']:.3f} (F1 {full['macro_f1']:.3f}) | per-layer " + " ".join(f"{a:.2f}" for a in per_layer), flush=True)


def prof(name, l):
    return np.array([res[name]["spec"][l][u] for u in PROF])


def pair_stats(pairs):
    pr, ps = [], []
    for a, b in pairs:
        pr.append([float(np.corrcoef(prof(a, l), prof(b, l))[0, 1]) for l in range(NL)])
        ps.append([float(spearmanr(prof(a, l), prof(b, l))[0]) for l in range(NL)])
    return {"pearson_by_layer": np.mean(pr, 0).tolist(), "spearman_by_layer": np.mean(ps, 0).tolist(),
            "pearson_deep_per_pair": [float(np.mean(x[6:])) for x in pr], "spearman_deep_per_pair": [float(np.mean(x[6:])) for x in ps],
            "pearson_deep_mean": float(np.mean([np.mean(x[6:]) for x in pr])), "spearman_deep_mean": float(np.mean([np.mean(x[6:]) for x in ps])),
            "pearson_all_layers_mean": float(np.mean(pr))}


T = lambda r: f"{r}@{tok}"
pairsets = {"init": [(T(a), T(b)) for a, b in itertools.combinations(inits, 2)],
            "order": [(T(f"I{i}D0"), T(f"I{i}D1")) for i in (0, 1) if f"I{i}D1" in runs],
            "rerun": [(T(a), T(b)) for a, b in (("I4D0", "I4D0R"), ("I0D0", "I0D0R")) if a in runs and b in runs],
            "floor": [("I0D0@0", "I1D0@0")]}
stab = {k: pair_stats(v) for k, v in pairsets.items() if v}

# spread across the init runs
IN = [T(r) for r in inits]
ms = np.array([res[x]["model_spec"] for x in IN])
pa = np.array([res[x]["probe_all"]["acc"] for x in IN])
pl = np.array([res[x]["probe_layer_acc"] for x in IN])
spec_upos_deep = np.array([[np.mean([res[x]["spec"][l][u] for l in range(6, 12)]) for u in PROF] for x in IN])
spread = {
    "model_spec_by_layer_mean": ms.mean(0).tolist(), "model_spec_by_layer_sd": ms.std(0, ddof=1).tolist(),
    "model_spec_by_layer_range": (ms.max(0) - ms.min(0)).tolist(),
    "dU_pp_layer_mean_over_layers": float((ms.mean() - U) * 100), "dU_pp_sd_over_runs_of_layer_mean": float(ms.mean(1).std(ddof=1) * 100),
    "probe_acc_mean": float(pa.mean()), "probe_acc_sd": float(pa.std(ddof=1)), "probe_acc_range": [float(pa.min()), float(pa.max())],
    "probe_layer_acc_mean": pl.mean(0).tolist(), "probe_layer_acc_sd": pl.std(0, ddof=1).tolist(),
    "spec_upos_deep_mean": dict(zip(PROF, spec_upos_deep.mean(0).tolist())), "spec_upos_deep_sd": dict(zip(PROF, spec_upos_deep.std(0, ddof=1).tolist())),
    "spec_upos_deep_between_upos_sd": float(spec_upos_deep.mean(0).std(ddof=1)),
    "spec_upos_deep_mean_within_run_sd": float(spec_upos_deep.std(0, ddof=1).mean()),
}
diffs = {}
for k in ("rerun", "order"):
    diffs[k] = [{"pair": p, "model_spec_deep_diff": float(np.mean(res[p[0]]["model_spec"][6:]) - np.mean(res[p[1]]["model_spec"][6:])),
                 "probe_acc_diff": res[p[0]]["probe_all"]["acc"] - res[p[1]]["probe_all"]["acc"]} for p in pairsets.get(k, [])]
out = {"tokens": tok, "U": U, "k": K, "n_experts": E, "upos": UP, "profile_upos": PROF, "n_per_upos": {u: cnt[u] for u in UP},
       "split": {"seed": 172, "n_train": int(len(tr)), "n_test": int(len(te))}, "baseline_word_form": base,
       "models": res, "stability": stab, "init_spread": spread, "pair_diffs": diffs}
(OUT / f"antoine_{tok}.json").write_text(json.dumps(out))
print("\nbaseline (word-form majority UPOS):", base)
print("init spread: probe acc %.3f ± %.3f (range %.3f–%.3f); dU (mean over layers) %.1f pp ± %.2f" % (
    pa.mean(), pa.std(ddof=1), pa.min(), pa.max(), spread["dU_pp_layer_mean_over_layers"], spread["dU_pp_sd_over_runs_of_layer_mean"]))
print("model Spec by layer (mean ± sd):", " ".join(f"{m:.3f}±{s:.3f}" for m, s in zip(ms.mean(0), ms.std(0, ddof=1))))
print("deep Spec per UPOS: between-UPOS sd %.3f vs mean across-run sd %.3f" % (spread["spec_upos_deep_between_upos_sd"], spread["spec_upos_deep_mean_within_run_sd"]))
for u in PROF:
    print(f"   {u:6s} n={cnt[u]:5d} deep Spec {spread['spec_upos_deep_mean'][u]:.3f} ± {spread['spec_upos_deep_sd'][u]:.3f}")
for k, s in stab.items():
    print(f"profile corr {k:6s}: pearson by layer " + " ".join(f"{x:.2f}" for x in s["pearson_by_layer"]) + f" | deep P {s['pearson_deep_mean']:.3f} S {s['spearman_deep_mean']:.3f}"
          + (f" (pair range {min(s['pearson_deep_per_pair']):.3f}–{max(s['pearson_deep_per_pair']):.3f})" if k == 'init' else ""))
print("diffs:", json.dumps(diffs))
