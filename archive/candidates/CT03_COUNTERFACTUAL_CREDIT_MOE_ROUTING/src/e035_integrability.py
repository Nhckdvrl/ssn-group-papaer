"""CT03 E03.5 -- is counterfactual routing utility expressible by a scalar router?

A standard router emits one scalar per expert. For it to represent the
counterfactual landscape exactly there must exist expert potentials z with

    u_ij = -dL(i->j)  ~=  z_j - z_i

This is an ASSUMPTION nothing in CT03 has tested, and Qwen's norm_topk_prob=true
gives a reason to doubt it: the swap renormalises by Z' = Z - p_i + p_j, so u_ij
depends on the (i,j) pair jointly, not only on i and on j separately.

Pure analysis of the exact utilities already measured. No GPU, no training.
"""
import json, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_report import spearman


def fit_potentials(pairs):
    """Least squares for z minimising sum_ij [(z_j - z_i) - u_ij]^2, gauge sum z = 0.
    Returns z, R^2, and the fitted values."""
    experts = sorted({e for p in pairs for e in (p[0], p[1])})
    idx = {e: k for k, e in enumerate(experts)}
    n = len(experts)
    A = np.zeros((len(pairs) + 1, n))
    b = np.zeros(len(pairs) + 1)
    for r, (i, j, u) in enumerate(pairs):
        A[r, idx[j]] = 1.0
        A[r, idx[i]] = -1.0
        b[r] = u
    A[-1, :] = 1.0                      # gauge
    z, *_ = np.linalg.lstsq(A, b, rcond=None)
    pred = np.array([z[idx[j]] - z[idx[i]] for i, j, _ in pairs])
    u = np.array([p[2] for p in pairs])
    ss_res = float(((u - pred) ** 2).sum())
    ss_tot = float(((u - u.mean()) ** 2).sum())
    return z, idx, (1 - ss_res / ss_tot if ss_tot > 0 else float("nan")), pred, u


def cycle_frustration(pairs, rng):
    """u_ij + u_jk should equal u_ik under an additive potential. With only
    i-in-selected / j-in-candidate pairs available we instead test the 4-cycle
    u_i1j1 - u_i1j2 - u_i2j1 + u_i2j2 == 0, which additivity forces to zero."""
    by = {(i, j): u for i, j, u in pairs}
    iset = sorted({i for i, _, _ in pairs}); jset = sorted({j for _, j, _ in pairs})
    res = []
    for _ in range(200):
        i1, i2 = rng.choice(iset, 2, replace=False)
        j1, j2 = rng.choice(jset, 2, replace=False)
        try:
            v = by[(i1, j1)] - by[(i1, j2)] - by[(i2, j1)] + by[(i2, j2)]
        except KeyError:
            continue
        res.append(abs(v))
    scale = float(np.mean([abs(u) for _, _, u in pairs]))
    return float(np.mean(res)) if res else float("nan"), scale


def main(path):
    recs = [json.loads(l) for l in open(path)]
    groups = defaultdict(list)
    for r in recs:
        groups[(r["q"], r["layer"], r["pos"])].append((r["i"], r["j"], -r["dL"]))
    rng = np.random.default_rng(0)

    per_layer = defaultdict(list)
    for (q, l, t), pairs in groups.items():
        if len(pairs) < 8:
            continue
        z, idx, r2, pred, u = fit_potentials(pairs)
        rho = spearman(pred, u)
        sign = float(((pred > 0) == (u > 0)).mean())
        frust, scale = cycle_frustration(pairs, rng)
        per_layer[l].append(dict(r2=r2, rho=rho, sign=sign,
                                 frust=frust, scale=scale,
                                 resid=float(np.abs(u - pred).mean())))

    print(f"source: {path}   tokens: {sum(len(v) for v in per_layer.values())}")
    print("\nCan a per-expert scalar potential reproduce the 32 pairwise utilities?")
    print(f"{'layer':>6}{'n':>6}{'R^2 med':>10}{'rho med':>10}{'sign acc':>10}"
          f"{'|resid|':>10}{'|u|':>10}{'4-cycle':>10}{'cyc/|u|':>9}")
    out = {}
    for l in sorted(per_layer):
        v = per_layer[l]
        g = lambda k: float(np.median([x[k] for x in v]))
        row = dict(n=len(v), r2=g("r2"), rho=g("rho"), sign=g("sign"),
                   resid=g("resid"), scale=g("scale"), frust=g("frust"))
        row["frust_rel"] = row["frust"] / row["scale"] if row["scale"] else float("nan")
        out[str(l)] = row
        print(f"{l:>6}{row['n']:>6}{row['r2']:>10.3f}{row['rho']:>10.3f}"
              f"{row['sign']:>10.3f}{row['resid']:>10.4f}{row['scale']:>10.4f}"
              f"{row['frust']:>10.4f}{row['frust_rel']:>9.3f}")
    json.dump(out, open("results/e035_integrability.json", "w"), indent=1)
    print("\nwrote results/e035_integrability.json")
    print("\nReading: R^2 near 1 => the landscape IS a scalar potential and a "
          "listwise/utility router target is well posed.\nR^2 low, or 4-cycle "
          "residual comparable to |u| => utility is genuinely pair/set dependent "
          "and NO scalar router can express it.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/c0_eval_base_pairs.jsonl")
