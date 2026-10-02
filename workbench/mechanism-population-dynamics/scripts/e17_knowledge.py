"""E17: clean-prompt knowledge confidence per (run, country) on the shared-known countries.

Usage: e17_knowledge.py --repo EleutherAI/pythia-410m-seed3 -> results/e17/<model>.json ; --analyze aggregates.
"""
import argparse
import json

import numpy as np
import torch
from scipy.stats import spearmanr

import mp_common as mc
import e13_arbitration as e13
import e16_knob as e16

OUT = mc.RESULTS / "e17"


def compute(repo):
    torch.set_grad_enabled(False)
    model = mc.load_tl_model(repo, 143000)
    caps = e13.capitals()
    dist = e16.distractors(caps)
    calib, held = e16.countries_split()
    cs = sorted(calib + held)
    P, C = [], []
    for c in cs:
        for x in [caps[c]] + dist[c]:
            P.append(e13.CLEAN.format(country=c)), C.append(x)
    lp = e13.cand_logprob(model, P, C).reshape(len(cs), e13.K_DIST + 1)
    conf = {c: float(row[0] - row[1:].max()) for c, row in zip(cs, lp)}
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('/')[-1]}.json").write_text(json.dumps({"repo": repo, "confidence": conf}, indent=1))
    print(repo, "mean conf", round(float(np.mean(list(conf.values()))), 2), flush=True)


def analyze():
    runs = sorted(f.stem for f in OUT.glob("pythia-410m*.json"))
    conf = {r: json.loads((OUT / f"{r}.json").read_text())["confidence"] for r in runs}
    adopt = {r: json.loads((mc.RESULTS / "e13" / f"{r}__step143000.json").read_text())["per_country"] for r in runs}
    cs = sorted(set.intersection(*[set(conf[r]) for r in runs]) & set.intersection(*[set(adopt[r]) for r in runs]))
    A = np.array([[adopt[r][c]["adoption"] for c in cs] for r in runs])
    K = np.array([[conf[r][c] for c in cs] for r in runs])
    within = [spearmanr(K[i], A[i])[0] for i in range(len(runs))]
    dA, dK = A - A.mean(0), K - K.mean(0)
    rho_pool = spearmanr(dK.ravel(), dA.ravel())
    run_rho = spearmanr(K.mean(1), A.mean(1))
    beta = float((dK.ravel() @ dA.ravel()) / (dK.ravel() @ dK.ravel()))
    resid = dA - beta * dK
    var_before, var_after = float(np.var(A.mean(1))), float(np.var(resid.mean(1)))
    out = {"n_countries": len(cs), "runs": runs, "within_run_rho": within, "pooled_rho": [rho_pool[0], rho_pool[1]],
           "run_level_rho": [run_rho[0], run_rho[1]], "beta": beta,
           "run_var_before": var_before, "run_var_after": var_after,
           "explained_fraction": 1 - var_after / var_before,
           "run_mean_adopt": A.mean(1).tolist(), "run_mean_conf": K.mean(1).tolist()}
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (np.round(v, 3).tolist() if isinstance(v, list) else round(v, 3) if isinstance(v, float) else v)
                      for k, v in out.items() if k != "runs"}, indent=0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo)
