"""more_roles analysis: within-layer SI / SD / DD and layer-profile similarity for the extra head roles (R1-R5) on the
1B 3-init x 25-corpus crossing; M1-M4 from crossing_1b alongside for reference."""
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import common as mc
def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def main():
    rng = np.random.default_rng(0)
    M = {tuple(f.stem.split("__")): json.loads(f.read_text()) for f in (mc.RESULTS / "more_roles").glob("*__*.json")
         if tuple(f.stem.split("__")) not in mc.UNVERIFIED_1B}
    crossing_1b = {}
    for k in M:
        f = mc.RESULTS / "crossing_1b" / f"{k[0]}-1B__{k[1]}.json"
        if f.exists():
            crossing_1b[k] = json.loads(f.read_text())["maps"]
    recs = sorted({r for r, _ in M})
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    out = {"n_models": len(M), "n_recipes": len(recs)}
    for m in ("R1", "R2", "R3", "R4", "R5", "M1", "M2", "M3", "M4"):
        src = M if m.startswith("R") else crossing_1b
        V = {k: np.array(src[k]["maps"][m] if m.startswith("R") else src[k][m]) for k in src}
        keys = list(V)
        from similarity import within_matrix
        W = within_matrix([V[k] for k in keys])
        P = np.corrcoef(np.stack([np.argsort(np.argsort(V[k].max(1))) for k in keys]).astype(float))
        idx = {k: i for i, k in enumerate(keys)}
        sims = {(a, b): (W[idx[a], idx[b]], P[idx[a], idx[b]]) for a, b in itertools.combinations(keys, 2)}
        g = {c: [v for p, v in sims.items() if cls(*p) == c] for c in ("SI", "SD", "DD")}
        boots = []
        for _ in range(500):
            w = rng.choice(recs, len(recs))
            cnt = {r: int((w == r).sum()) for r in recs}
            gg = {"SI": [], "SD": []}
            for (a, b), v in sims.items():
                c = cls(a, b)
                if c in gg and cnt[a[0]] and cnt[b[0]]:
                    gg[c] += [v[0]] * (cnt[a[0]] * cnt[b[0]])
            boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        row = {c: {"within": float(np.mean([x[0] for x in v])), "layer_profile": float(np.nanmean([x[1] for x in v])),
                   "n": len(v)} for c, v in g.items()}
        row["SI_minus_SD"] = row["SI"]["within"] - row["SD"]["within"]
        row["ci95"] = np.percentile(boots, [2.5, 97.5]).tolist()
        if m.startswith("R") and m != "R1" and m != "R5":
            row["reliability"] = float(np.mean([M[k][f"reliability_{m}"] for k in M]))
        out[m] = row
        print(f"{m}: within SI {row['SI']['within']:.3f} SD {row['SD']['within']:.3f} DD {row['DD']['within']:.3f} "
              f"diff CI [{row['ci95'][0]:.3f}, {row['ci95'][1]:.3f}] | layer profile SI {row['SI']['layer_profile']:.2f} "
              f"SD {row['SD']['layer_profile']:.2f} DD {row['DD']['layer_profile']:.2f} | n {len(keys)}", flush=True)
    (mc.RESULTS / "more_roles" / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
