"""strongest_head (POST-HOC, reviewer questions): agreement on the strongest head, not only on the within-layer ranking.
  - 1B verified crossing, nine roles: in the three layers where a role is strongest (mean over models of the layer's
    maximum score), top-1 head match and top-3 overlap for seed-matched / same-corpus / unrelated pairs, against
    chance 1/H and 3/H; within-layer Spearman restricted to those layers and to the remaining layers.
  - The induction example of the introduction for each of the three initializations.
  - Template specificity of the Flan habit pooled over the seven sizes (inverse-variance weights).
Writes results/strongest_head.json."""
import collections
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import common as mc
R = mc.RESULTS
ROLES = ["M1", "M2", "M3", "M4", "R1", "R2", "R3", "R4", "R5"]


def load_1b():
    D = {}
    for f in sorted((R / "crossing_1b").glob("*-1B__*.json")):
        if "step" in f.stem:
            continue
        r, s = f.stem.split("-1B__")
        if (r, s) in mc.UNVERIFIED_1B:
            continue
        d = json.loads(f.read_text())
        m = {k: np.array(v) for k, v in d["maps"].items() if k != "M1" or d["M1_max"] > 0.3}
        f59 = R / "more_roles" / f"{r}__{s}.json"
        if f59.exists():
            m.update({k: np.array(v) for k, v in json.loads(f59.read_text())["maps"].items()})
        D[(r, s)] = m
    return D


def strongest_head(D):
    out = {}
    for role in ROLES:
        ks = sorted(k for k in D if role in D[k])
        H = D[ks[0]][role].shape[1]
        mean_max = np.mean([D[k][role].max(1) for k in ks], 0)
        top, rest = np.argsort(-mean_max)[:3], np.argsort(-mean_max)[3:]
        g = {c: {"top1": [], "top3": [], "rho_role": [], "rho_other": []} for c in ("SI", "SD", "DD")}
        for a, b in itertools.combinations(ks, 2):
            c = "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
            A, B = D[a][role], D[b][role]
            g[c]["top1"].append(np.mean([A[l].argmax() == B[l].argmax() for l in top]))
            g[c]["top3"].append(np.mean([len(set(np.argsort(-A[l])[:3]) & set(np.argsort(-B[l])[:3])) / 3 for l in top]))
            if c != "DD":
                g[c]["rho_role"].append(np.nanmean([spearmanr(A[l], B[l])[0] for l in top]))
                g[c]["rho_other"].append(np.nanmean([spearmanr(A[l], B[l])[0] for l in rest]))
        out[role] = {"layers": sorted(int(x) for x in top), "chance_top1": 1 / H, "chance_top3": 3 / H,
                     **{c: {k: float(np.mean(v)) for k, v in g[c].items() if v} for c in g}}
        print(role, {c: {k: round(v, 2) for k, v in out[role][c].items()} for c in ("SI", "SD")}, flush=True)
    # the introduction's induction example, for each initialization
    ex = {}
    for s in ("default", "large-aux-2", "large-aux-3"):
        ks = [k for k in D if k[1] == s and "M1" in D[k]]
        L = D[ks[0]]["M1"].shape[0]
        best = max(((l, collections.Counter(int(D[k]["M1"][l].argmax()) for k in ks).most_common(1)[0])
                    for l in range(L)), key=lambda x: x[1][1])
        ex[s] = {"n_corpora": len(ks), "layer": best[0], "head": best[1][0], "wins": best[1][1]}
    out["induction_example"] = ex
    print(ex)
    return out


def template_pooled():
    habit_sizes = json.loads((R / "habit_sizes" / "analysis.json").read_text())
    habit_templates = json.loads((R / "habit_templates" / "analysis.json").read_text())["cells"]
    out = {}
    for other in ("QA_short", "novel"):
        d, se = [], []
        for s in list(habit_sizes) + ["1B"]:
            c = habit_sizes[s]["cells"] if s != "1B" else habit_templates
            d.append(c["QA"]["delta"] - c[other]["delta"])
            se.append(np.hypot(c["QA"]["se"], c[other]["se"]))
        d, se = np.array(d), np.array(se)
        w = 1 / se ** 2
        m, sm = float((w * d).sum() / w.sum()), float(1 / np.sqrt(w.sum()))
        out[f"QA_minus_{other}"] = {"per_size": d.round(3).tolist(), "pooled": m, "se": sm, "z": m / sm,
                                    "n_positive": int((d > 0).sum())}
        print(other, out[f"QA_minus_{other}"])
    return out


def main():
    res = {"strongest_head_1b": strongest_head(load_1b()), "template_pooled": template_pooled()}
    (R / "strongest_head.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
