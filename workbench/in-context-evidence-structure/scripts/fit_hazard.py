"""Fit the LM's implicit (hazard lam, noise eps) by profile regression.
usage: fit_hazard.py DATA_DIR "RESULT_GLOB" FORMAT_PREFIX [--out JSON]
For each fixed (lam, eps) on a grid: oracle P_B per row (rule oracle with that single hyper-
parameter pair), then lo_LM ~ a + b*logit(P_B) (OLS over condition means, paired-free).
Reports R^2 surface and the best pair; lam=0 is the exchangeable (set) model.
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import Grid, oracle_fast  # noqa


def logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9); return np.log(p / (1 - p))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("res"); ap.add_argument("fmt")
    ap.add_argument("--out"); ap.add_argument("--max_rows", type=int, default=3000)
    a = ap.parse_args()
    sc = {}
    for f in glob.glob(a.res):
        for l in open(f):
            s = json.loads(l); sc[s["uid"]] = s["lp"]
    rows = []
    for l in open(Path(a.data) / "rows.jsonl"):
        r = json.loads(l)
        if r["uid"] in sc and r["cond"].startswith(a.fmt + ":"):
            rows.append(r)
    rng = np.random.default_rng(0)
    if len(rows) > a.max_rows:
        rows = [rows[i] for i in rng.choice(len(rows), a.max_rows, replace=False)]
    y = []; spec = []
    for r in rows:
        lp = sc[r["uid"]]; lo1 = lp[1] - lp[0]; qb = r["query_label_B"]
        y.append(lo1 if qb == 1 else -lo1)
        b = r["base"]
        if "X" in b and r["cond"].startswith("rule"):
            X = np.array(b["X"]); xq = np.array(b["xq"]); n = X.shape[1]
        else:                                      # label stream: constant input
            T = len(r["labels"]); X = np.ones((T, 1), int); xq = np.array([1]); n = 1
        spec.append((X, r["labels"], xq, n, qb, r["cond"]))
    y = np.array(y); conds = np.array([s[5] for s in spec])
    lams = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]; epss = [0.01, 0.03, 0.05, 0.1, 0.2, 0.3]
    R = np.zeros((len(lams), len(epss))); Rc = np.zeros_like(R)
    for i, lam in enumerate(lams):
        for j, eps in enumerate(epss):
            g = Grid(lams=(lam,), lam_prior=(1.0,), epss=(eps,), eps_prior=(1.0,))
            x = []
            for X, labs, xq, n, qb, _ in spec:
                p = oracle_fast(X, labs, xq, n, g).p_rule_query
                x.append(logit(p if qb == 1 else 1 - p))
            x = np.array(x)
            A = np.c_[np.ones_like(x), x]; c, *_ = np.linalg.lstsq(A, y, rcond=None)
            R[i, j] = 1 - np.mean((y - A @ c) ** 2) / y.var()
            cy = np.array([y[conds == k].mean() for k in np.unique(conds)])
            cx = np.array([x[conds == k].mean() for k in np.unique(conds)])
            Rc[i, j] = np.corrcoef(cy, cx)[0, 1] ** 2
    print(f"format {a.fmt}: rows {len(y)}")
    print("row-level R^2 (rows lam, cols eps):", epss)
    for i, lam in enumerate(lams):
        print(f"  lam={lam:<5} " + " ".join(f"{v:.3f}" for v in R[i]))
    print("condition-mean R^2:")
    for i, lam in enumerate(lams):
        print(f"  lam={lam:<5} " + " ".join(f"{v:.3f}" for v in Rc[i]))
    bi = np.unravel_index(np.argmax(Rc), Rc.shape)
    print(f"best (cond means): lam={lams[bi[0]]} eps={epss[bi[1]]} R2={Rc[bi]:.3f};  best set(lam=0): {Rc[0].max():.3f}")
    if a.out:
        json.dump({"lams": lams, "epss": epss, "R2_rows": R.tolist(), "R2_cond": Rc.tolist()}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
