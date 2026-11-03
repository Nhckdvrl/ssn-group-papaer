#!/usr/bin/env python3
"""E170 stage 1b check of the POST-HOC reading "runs divide a word's contexts by the grammatical function that
the LEFT context already determines": for every multi-function form, how predictable is the function label
from the left context alone (prev-1/prev-2 UPOS, prev-1 word, sentence-initial flag) versus from the right
context alone (next-1/next-2 UPOS, next-1 word)? Logistic regression, 5-fold CV, balanced accuracy above the
majority baseline. Then correlate with the runs' separation (sep) from ambiguous_<TOKENS>.json.

Usage: e170_context_predictability.py TOKENS   -> results/e170/context_predictability_<TOKENS>.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

WB = Path(__file__).resolve().parents[1]
tok = int(float(sys.argv[1])) if len(sys.argv) > 1 else 3999793152
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
AMB = json.loads((WB / f"results/e170/ambiguous_{tok}.json").read_text())
runs = ["I0D0", "I1D0", "I2D0", "I3D0", "I0D1", "I1D1"]
# sentence neighbours: words are stored sequentially per sentence
def nb(n, k):
    a = ann[n]
    m = n + k
    if 0 <= m < len(ann) and ann[m]["doc_id"] == a["doc_id"] and ann[m]["sent_pos"] == a["sent_pos"] + k and ann[m]["sent_len"] == a["sent_len"]:
        return ann[m]
    return None


def feats(n, side):
    a = ann[n]; f = {}
    if side == "left":
        f["init"] = str(a["sent_init"])
        for k in (1, 2):
            b = nb(n, -k); f[f"p{k}u"] = b["upos"] if b else "BOS"
        b = nb(n, -1); f["p1w"] = b["form"].lower() if b else "BOS"
    else:
        f["final"] = str(a["sent_final"])
        for k in (1, 2):
            b = nb(n, k); f[f"n{k}u"] = b["upos"] if b else "EOS"
        b = nb(n, 1); f["n1w"] = b["form"].lower() if b else "EOS"
    return f


forms = defaultdict(list)
for n, a in enumerate(ann):
    if a["split"] == "anchor":
        forms[a["form"].lower()].append(n)
out = {"tokens": tok, "forms": {}}
rows = []
for f, rec in AMB["forms"].items():
    keep = set(rec["functions"])
    idx = [n for n in forms[f] if f"{ann[n]['upos']}:{ann[n]['deprel']}" in keep]
    y = np.array([f"{ann[n]['upos']}:{ann[n]['deprel']}" for n in idx])
    if len(idx) < 40 or Counter(y).most_common()[-1][1] < 5:
        continue
    res = {"n": len(idx), "majority": max(Counter(y).values()) / len(y)}
    for side in ("left", "right"):
        X = [feats(n, side) for n in idx]
        clf = make_pipeline(DictVectorizer(), LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"))
        cv = StratifiedKFold(5, shuffle=True, random_state=0)
        pred = cross_val_predict(clf, X, y, cv=cv)
        res[f"bacc_{side}"] = float(balanced_accuracy_score(y, pred))
    res["chance_bacc"] = 1.0 / len(keep)
    sep = {l: float(np.mean([rec["layers"][l]["sep"][r] for r in runs])) for l in rec["layers"]}
    res["sep"] = sep
    out["forms"][f] = res
    rows.append((f, len(idx), res["bacc_left"] - res["chance_bacc"], res["bacc_right"] - res["chance_bacc"], sep["11"], sep["5"]))
rows.sort(key=lambda r: -r[1])
print(f"{'form':8s} {'n':>5s} {'left+':>6s} {'right+':>6s} {'sep11':>6s} {'sep5':>6s}")
for r in rows:
    print(f"{r[0]:8s} {r[1]:5d} {r[2]:6.2f} {r[3]:6.2f} {r[4]:6.2f} {r[5]:6.2f}")
L = np.array([r[2] for r in rows]); R = np.array([r[3] for r in rows]); S11 = np.array([r[4] for r in rows]); S5 = np.array([r[5] for r in rows])
from scipy.stats import spearmanr
out["summary"] = {"n_forms": len(rows),
                  "spearman_sep11_left": float(spearmanr(S11, L).correlation), "spearman_sep11_right": float(spearmanr(S11, R).correlation),
                  "spearman_sep5_left": float(spearmanr(S5, L).correlation), "spearman_sep5_right": float(spearmanr(S5, R).correlation),
                  "spearman_sep11_left_minus_right": float(spearmanr(S11, L - R).correlation),
                  "partial_note": "left and right predictability are themselves correlated; see pearson below",
                  "pearson_left_right": float(np.corrcoef(L, R)[0, 1])}
print(json.dumps(out["summary"], indent=1))
(WB / f"results/e170/context_predictability_{tok}.json").write_text(json.dumps(out))
print("saved")
