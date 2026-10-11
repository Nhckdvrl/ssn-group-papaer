"""E19: run-vs-snapshot variance of E18 adoption margins (410M, steps 123k/133k/138k/143k). Protocol: experiments/E19-*.md."""
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

E18 = mc.RESULTS / "e18"
STEPS = [123000, 133000, 138000, 143000]
RUNS = ["pythia-410m"] + [f"pythia-410m-seed{i}" for i in range(1, 10)]


def load(run, step):
    f = E18 / (f"{run}.json" if step == 143000 else f"{run}__step{step}.json")
    return json.loads(f.read_text())["conditions"]


def main():
    D = {(r, s): load(r, s) for r in RUNS for s in STEPS}
    conds = sorted(D[(RUNS[0], 143000)])
    conds = [c for c in conds if all(D[k][c].get("n_known", 0) >= 30 for k in D)]
    icc = {}
    for c in conds:
        X = np.array([[D[(r, s)][c]["margin"] for s in STEPS] for r in RUNS])  # [run, step]
        resid = X - X.mean(1, keepdims=True) - X.mean(0, keepdims=True) + X.mean()
        between = X.mean(1).var(ddof=1)
        within = (resid ** 2).sum() / ((X.shape[0] - 1) * (X.shape[1] - 1))  # run x step interaction = snapshot noise
        icc[c] = float((between - within / X.shape[1]) / (between - within / X.shape[1] + within))
    M = {s: np.array([np.mean([D[(r, s)][c]["margin"] for c in conds]) for r in RUNS]) for s in STEPS}
    no4 = [i for i, r in enumerate(RUNS) if not r.endswith("seed4")]
    out = {"conditions": conds, "icc": icc, "icc_median": float(np.median(list(icc.values()))),
           "rank_rho_133_143": float(spearmanr(M[133000], M[143000])[0]),
           "rank_rho_133_143_no_seed4": float(spearmanr(M[133000][no4], M[143000][no4])[0]),
           "run_mean_margin": {s: dict(zip(RUNS, M[s].round(3).tolist())) for s in STEPS}}
    (mc.RESULTS / "e19").mkdir(exist_ok=True)
    (mc.RESULTS / "e19" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
