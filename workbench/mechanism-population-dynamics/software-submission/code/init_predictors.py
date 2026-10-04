"""init_predictors: do step-0 weight statistics predict the initialization-set role layout? (CPU)."""
import itertools
import json

import numpy as np
from safetensors.torch import load_file
from scipy.stats import spearmanr

import datadecide as dd
import common as mc
crossing_1b = mc.RESULTS / "crossing_1b"
ROLES = ("M1", "M2", "M4")


def head_features(seed):
    path = dd.fetch("allenai/DataDecide-c4-1B", dd.rev(0, seed))
    cfg = json.loads((path / "config.json").read_text())
    d, L, H = cfg["d_model"], cfg["n_layers"], cfg["n_heads"]
    dh = d // H
    sd = {}
    for f in sorted(path.glob("*.safetensors")):
        sd.update(load_file(str(f)))
    feats = {k: np.zeros((L, H)) for k in ("nQ", "nK", "nV", "nO", "QK", "OV")}
    for l in range(L):
        b = f"model.transformer.blocks.{l}."
        q, k, v = sd[b + "att_proj.weight"].float().split(d, 0)
        o = sd[b + "attn_out.weight"].float()
        for h in range(H):
            sl = slice(h * dh, (h + 1) * dh)
            Wq, Wk, Wv, Wo = q[sl], k[sl], v[sl], o[:, sl]
            feats["nQ"][l, h], feats["nK"][l, h] = Wq.norm(), Wk.norm()
            feats["nV"][l, h], feats["nO"][l, h] = Wv.norm(), Wo.norm()
            feats["QK"][l, h] = float(np.sqrt(np.trace(((Wq @ Wq.T) @ (Wk @ Wk.T)).numpy())))   # ||Wq^T Wk||_F
            feats["OV"][l, h] = float(np.sqrt(np.trace(((Wo.T @ Wo) @ (Wv @ Wv.T)).numpy())))   # ||Wo Wv||_F
    return feats


def main():
    D = {}
    for f in crossing_1b.glob("*__*.json"):
        if "__step" in f.stem:
            continue
        r, s = f.stem.split("__")
        D[(r, s)] = json.loads(f.read_text())["maps"]
    recs = sorted({r for r, _ in D})
    rng = np.random.default_rng(0)
    perm = rng.permutation(recs)
    halves = (set(perm[:12]), set(perm[12:]))
    target, rel = {}, {}
    for s in dd.SEEDS:
        for m in ROLES:
            target[(s, m)] = np.mean([D[(r, s)][m] for r in recs], 0)
            a = np.mean([D[(r, s)][m] for r in halves[0]], 0).ravel()
            b = np.mean([D[(r, s)][m] for r in halves[1]], 0).ravel()
            rel[(s, m)] = float(spearmanr(a, b)[0])
    F = {s: head_features(s) for s in dd.SEEDS}
    out = {"target_reliability": {f"{s}|{m}": v for (s, m), v in rel.items()},
           "positive_control": bool(all(v >= 0.6 for v in rel.values())), "tests": {}}
    for m in ROLES:
        for feat in F[dd.SEEDS[0]]:
            match = [spearmanr(F[s][feat].ravel(), target[(s, m)].ravel())[0] for s in dd.SEEDS]
            mism = [spearmanr(F[s][feat].ravel(), target[(t, m)].ravel())[0] for s, t in itertools.permutations(dd.SEEDS, 2)]
            rm, rmm = float(np.mean(match)), float(np.mean(mism))
            out["tests"][f"{m}|{feat}"] = {"rho_match_each": [float(x) for x in match], "rho_match": rm, "rho_mismatch": rmm,
                                           "candidate": bool(rm >= 0.3 and rm - rmm >= 0.2 and len({np.sign(x) for x in match}) == 1)}
    T = out["tests"]
    out["decision"] = ("init weights predict roles: " + ",".join(k for k, v in T.items() if v["candidate"])
                       if any(v["candidate"] for v in T.values()) else
                       "not predictable" if all(abs(v["rho_match"] - v["rho_mismatch"]) < 0.1 for v in T.values()) else "other (report)")
    (mc.RESULTS / "init_predictors").mkdir(exist_ok=True)
    (mc.RESULTS / "init_predictors" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "tests"}, indent=1))
    for k, v in T.items():
        print(f"{k:10s} match {v['rho_match']:+.3f} {[round(x, 2) for x in v['rho_match_each']]} mismatch {v['rho_mismatch']:+.3f}")


if __name__ == "__main__":
    main()
