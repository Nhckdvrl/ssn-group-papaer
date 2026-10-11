"""Shared helpers: join rows with LM scores, bootstrap CIs."""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load(rows_path, score_path):
    rows = {json.loads(l)["uid"]: json.loads(l) for l in open(rows_path)}
    recs = []
    for l in open(score_path):
        s = json.loads(l)
        r = rows[s["uid"]]
        lp = np.array(s["lp"])
        d = {k: v for k, v in r.items() if k not in ("prompt", "base", "oracle", "labels", "cands")}
        d.update(r.get("oracle", {}) or {})
        d["lp0"], d["lp1"] = lp
        d["mass"] = float(np.exp(lp).sum())          # prob mass on the two labels
        # log-odds of label 1 vs 0
        d["lo1"] = float(lp[1] - lp[0])
        recs.append(d)
    df = pd.DataFrame(recs)
    if "query_label_B" in df:
        sgn = np.where(df["query_label_B"] == 1, 1, -1)
        df["lo_B"] = sgn * df["lo1"]                  # LM log-odds for the reversed-rule label
    if "gold" in df:
        sg = np.where(df["gold"] == 1, 1, -1)
        df["lo_gold"] = sg * df["lo1"]
        df["acc"] = (df["lo_gold"] > 0).astype(float)
    return df


def boot_ci(x, n=2000, seed=0, stat=np.mean):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    bs = [stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n)]
    return float(stat(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def fmt(m, lo, hi, p=2):
    return f"{m:.{p}f} [{lo:.{p}f},{hi:.{p}f}]"
