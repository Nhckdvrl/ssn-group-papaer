"""E61: anatomical seed fingerprint. Can the seed of a model trained on an unseen corpus be identified from its head-role
layout alone? Leave-one-corpus-out nearest-seed classification: a query model (corpus r, seed s) is compared with all
reference models trained on OTHER corpora; score(seed s') = mean within-layer Spearman with the references of seed s'
(averaged over role maps M1 / M2 / M4, M1 only when induction heads exist); predict argmax. Chance = 1 / n_seeds.
Also: identification from a single role map, and Pythia (deduped query vs std + 9 PolyPythias seeds as candidates)."""
import collections
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc
from e45_analyze import EXCLUDE, SIZES


def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def identify(M, roles):
    from fastsim import within_matrix
    seeds = sorted({s for _, s in M})
    keys = sorted(M)
    sims = []
    for m in roles:
        S = within_matrix([M[k]["maps"][m] for k in keys])
        if m == "M1":
            ok = np.array([M[k]["M1_max"] > 0.3 for k in keys])
            S = np.where(ok[:, None] & ok[None, :], S, np.nan)
        sims.append(S)
    S = np.nanmean(np.stack(sims), 0)
    hits, margins = [], []
    for i, q in enumerate(keys):
        score = {}
        for s in seeds:
            v = [S[i, j] for j, r in enumerate(keys) if r[1] == s and r[0] != q[0]]
            score[s] = np.nanmean(v) if v else np.nan
        if any(np.isnan(v) for v in score.values()):
            continue
        pred = max(score, key=score.get)
        hits.append(pred == q[1])
        margins.append(score[q[1]] - max(v for s, v in score.items() if s != q[1]))
    return {"accuracy": float(np.mean(hits)), "n": len(hits), "n_seeds": len(seeds), "chance": 1 / len(seeds),
            "median_margin": float(np.median(margins))}


def main():
    out = {}
    for size in SIZES:
        M = {tuple(f.stem.split("__")[1:]): json.loads(f.read_text()) for f in sorted((mc.RESULTS / "e45").glob(f"{size}__*.json"))
             if (size, *f.stem.split("__")[1:]) not in EXCLUDE}
        if len({s for _, s in M}) < 2:
            continue
        row = {"all": identify(M, ("M1", "M2", "M4"))}
        for m in ("M1", "M2", "M4"):
            row[m] = identify(M, (m,))
        out[size] = row
        print(f"{size:8s} all {row['all']['accuracy']:.2f} (chance {row['all']['chance']:.2f}, n {row['all']['n']}) | " +
              " ".join(f"{m} {row[m]['accuracy']:.2f}" for m in ("M1", "M2", "M4")), flush=True)
    # 1B, 3 seeds x 25 corpora (E35)
    M = {}
    for f in sorted((mc.RESULTS / "e35").glob("*-1B__*.json")):
        if "step" in f.name:
            continue
        r, s = f.stem.split("-1B__")
        d = json.loads(f.read_text())
        M[(r, s)] = d
    row = {"all": identify(M, ("M1", "M2", "M4"))}
    for m in ("M1", "M2", "M4"):
        row[m] = identify(M, (m,))
    out["1B_E35"] = row
    print(f"1B E35   all {row['all']['accuracy']:.2f} (chance {row['all']['chance']:.2f}, n {row['all']['n']}) | " +
          " ".join(f"{m} {row[m]['accuracy']:.2f}" for m in ("M1", "M2", "M4")))
    # Pythia: deduped query vs candidates std + seed1..9 (PolyPythias); std shares the deduped init
    for size in ("70m", "160m", "410m"):
        D = mc.RESULTS / "e44"
        q = json.loads((D / f"pythia-{size}-deduped.json").read_text())
        cands = {"std": D / f"pythia-{size}-std.json", **{f"seed{i}": D / f"pythia-{size}-seed{i}.json" for i in range(1, 10)}}
        sc = {}
        for k, f in cands.items():
            if f.exists():
                c = json.loads(f.read_text())
                sc[k] = float(np.mean([within(np.array(q["maps"][m]), np.array(c["maps"][m])) for m in ("M1", "M2", "M4")
                                       if m != "M1" or (q["M1_max"] > 0.3 and c["M1_max"] > 0.3)]))
        rank = sorted(sc, key=sc.get, reverse=True)
        out[f"pythia-{size}"] = {"scores": sc, "rank_of_std": rank.index("std") + 1, "n_candidates": len(sc)}
        print(f"pythia-{size}: true seed (std) ranked {rank.index('std') + 1} / {len(sc)}; "
              f"score std {sc['std']:.3f}, best other {max(v for k, v in sc.items() if k != 'std'):.3f}")
    (mc.RESULTS / "e61_seed_id.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
