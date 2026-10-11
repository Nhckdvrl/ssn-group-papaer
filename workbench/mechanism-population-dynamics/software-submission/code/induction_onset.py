"""induction_onset: is the emergence time of induction / previous-token heads set by the corpus or by the initialization?  Uses the controlled_pretraining A-arm runs (S size, 6 inits x 4 corpora, order = init).
"""
import json

import numpy as np
from scipy.stats import f as fdist

import common as mc
D = mc.RESULTS / "controlled"
INITS = range(1, 7)
CORPORA = ("c4", "code", "papers", "books")


def onset(measures, key, thr):
    """First training step at which measures[step][key] >= thr, linearly interpolated on the measurement grid;
    None if never reached (right-censored)."""
    steps = sorted(int(s) for s in measures)
    vals = [measures[str(s)][key] for s in steps]
    for j in range(1, len(steps)):
        if vals[j] >= thr > vals[j - 1]:
            s0, s1, v0, v1 = steps[j - 1], steps[j], vals[j - 1], vals[j]
            return s0 + (thr - v0) * (s1 - s0) / (v1 - v0)
        if j == 1 and vals[0] >= thr:
            return float(steps[0])
    return None


def components(Y):
    a, b = Y.shape
    gm = Y.mean()
    msr_d = b * ((Y.mean(1) - gm) ** 2).sum() / (a - 1)
    msr_i = a * ((Y.mean(0) - gm) ** 2).sum() / (b - 1)
    msr = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum() / ((a - 1) * (b - 1))
    vd, vi = max((msr_d - msr) / b, 0.0), max((msr_i - msr) / a, 0.0)
    tot = vd + vi + msr
    return {"frac_corpus": vd / tot, "frac_init": vi / tot, "frac_resid": msr / tot,
            "p_corpus": float(fdist.sf(msr_d / msr, a - 1, (a - 1) * (b - 1))),
            "p_init": float(fdist.sf(msr_i / msr, b - 1, (a - 1) * (b - 1)))}


def main():
    runs = {}
    for i in INITS:
        for c in CORPORA:
            f = D / f"S_i{i}_{c}_o{i}.json"
            if f.exists():
                runs[(c, i)] = json.loads(f.read_text())["measures"]
    out = {"n_runs": len(runs)}
    for name, key, thr, corpora in (("induction", "copy_gain", 1.0, ("c4", "code", "papers")),
                                    ("prev_token", "M2_max", 0.5, CORPORA)):
        T = {k: onset(m, key, thr) for k, m in runs.items() if k[0] in corpora}
        grid = sorted(int(s) for s in next(iter(runs.values())))
        ok = [t for t in T.values() if t is not None]
        resolvable = float(np.mean([grid[1] < t < grid[-1] for t in ok])) if ok else 0.0
        row = {"onsets": {f"{c}_i{i}": t for (c, i), t in T.items()}, "n_censored": sum(t is None for t in T.values()),
               "frac_resolvable": resolvable,
               "median_by_corpus": {c: float(np.median([t for (cc, _), t in T.items() if cc == c and t is not None]))
                                    for c in corpora if any(t is not None for (cc, _), t in T.items() if cc == c)}}
        full = [c for c in corpora if all(T.get((c, i)) is not None for i in INITS)]
        if len(full) >= 2:
            Y = np.log(np.array([[T[(c, i)] for i in INITS] for c in full]))
            row["decomposition_log_steps"] = components(Y)
            row["corpora_used"] = full
        out[name] = row
    (D / "induction_onset.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v if not isinstance(v, dict) else {a: b for a, b in v.items() if a != "onsets"}) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
