"""E35 on the verified 1B crossing (P12): the six runs whose published step 0 is not their seed's shared step 0 are
excluded. (1) Within-layer which-head agreement, same seed / other corpus (SI), other seed / same corpus (SD) and both
different (DD), per role, with recipe-bootstrap CIs. (2) Unbiased two-way variance components (seed, corpus, residual)
of every head's within-layer rank on the balanced crossing of recipes verified for all three seeds, with F tests."""
import itertools
import json

import numpy as np
from scipy.stats import f as fdist, rankdata

import mp_common as mc
from fastsim import within_matrix

SEEDS = ["default", "large-aux-2", "large-aux-3"]


def load():
    D = {}
    for f in sorted((mc.RESULTS / "e35").glob("*-1B__*.json")):
        if "step" in f.name:
            continue
        k = tuple(f.stem.split("-1B__"))
        if k not in mc.UNVERIFIED_1B:
            D[k] = json.loads(f.read_text())
    return D


def agreement(D, rng):
    keys = sorted(D)
    recs = sorted({r for r, _ in keys})
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    out = {}
    for m in ("M1", "M2", "M3", "M4"):
        ok = [k for k in keys if m != "M1" or D[k]["M1_max"] > 0.3]
        W = within_matrix([D[k]["maps"][m] for k in ok])
        sims = {(a, b): W[i, j] for (i, a), (j, b) in itertools.combinations(enumerate(ok), 2)}
        g = {c: [v for p, v in sims.items() if cls(*p) == c] for c in ("SI", "SD", "DD")}
        boots = []
        for _ in range(1000):
            w = rng.choice(recs, len(recs))
            cnt = {r: int((w == r).sum()) for r in recs}
            gg = {"SI": [], "SD": []}
            for (a, b), v in sims.items():
                c = cls(a, b)
                if c in gg and cnt[a[0]] and cnt[b[0]]:
                    gg[c] += [v] * (cnt[a[0]] * cnt[b[0]])
            boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        out[m] = {c: float(np.mean(v)) for c, v in g.items()} | {"n_models": len(ok),
                                                              "ci95_SI_minus_SD": np.percentile(boots, [2.5, 97.5]).tolist()}
        print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[m].items()}, flush=True)
    return out


def variance_components(D):
    recs = sorted(r for r in {r for r, _ in D} if all((r, s) in D for s in SEEDS))
    out = {"n_recipes_balanced": len(recs)}
    for m in ("M1", "M2", "M4"):
        X = np.stack([[np.array(D[(r, s)]["maps"][m]) for s in SEEDS] for r in recs])  # recipes x seeds x L x H
        X = rankdata(X, axis=-1)  # within-layer rank of each head
        a, b = X.shape[0], X.shape[1]
        g = X.mean((0, 1))
        mr, ms = X.mean(1), X.mean(0)
        ss_r = b * ((mr - g) ** 2).sum(0)
        ss_s = a * ((ms - g) ** 2).sum(0)
        ss_e = ((X - mr[:, None] - ms[None] + g) ** 2).sum((0, 1))
        df_r, df_s, df_e = a - 1, b - 1, (a - 1) * (b - 1)
        MSr, MSs, MSe = ss_r / df_r, ss_s / df_s, ss_e / df_e
        p_r = fdist.sf(MSr / MSe, df_r, df_e)
        p_s = fdist.sf(MSs / MSe, df_s, df_e)
        vr, vs = np.maximum((MSr - MSe) / b, 0), np.maximum((MSs - MSe) / a, 0)
        tot = vr + vs + MSe
        out[m] = {"frac_heads_seed_sig": float((p_s < 0.05).mean()), "frac_heads_corpus_sig": float((p_r < 0.05).mean()),
                  "median_share_seed": float(np.median(vs / tot)), "median_share_corpus": float(np.median(vr / tot))}
        print(m, {k: round(v, 3) for k, v in out[m].items()}, flush=True)
    return out


def main():
    rng = np.random.default_rng(0)
    D = load()
    print("verified 1B models:", len(D), flush=True)
    out = {"n_models": len(D), "excluded": sorted("|".join(k) for k in mc.UNVERIFIED_1B),
           "agreement": agreement(D, rng), "variance_components": variance_components(D)}
    (mc.RESULTS / "e35_verified.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
