"""E40: lock-in curves of per-head role layout within single Pythia runs (E02 data; CPU). Protocol: experiments/E40-*.md."""
import itertools
import json
import re

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

E02 = mc.RESULTS / "e02"


def load(size):
    D = {}
    for f in E02.glob(f"pythia-{size}*__step*.json"):
        m = re.match(rf"(pythia-{size}(?:-seed\d+)?)__step(\d+)", f.stem)
        if not m:
            continue
        d = json.loads(f.read_text())
        flat = lambda S: np.array([S[k] for k in sorted(S, key=lambda x: [float(t) for t in x.split(".")])], float).ravel()
        D[(m.group(1), int(m.group(2)))] = {"S_prev": flat(d["S_prev"]), "S_ind": flat(d["S_ind"])}
    return D


def main():
    out = {}
    for size in ("70m", "31m", "160m"):
        D = load(size)
        runs = sorted({r for r, _ in D})
        steps = sorted({s for _, s in D})
        if not runs or 143000 not in steps:
            continue
        res = {"runs": len(runs), "steps": steps}
        for key in ("S_prev", "S_ind"):
            curves, lock = {}, []
            for r in runs:
                if (r, 143000) not in D:
                    continue
                c = {s: float(spearmanr(D[(r, s)][key], D[(r, 143000)][key])[0]) for s in steps if (r, s) in D}
                curves[r] = c
                ok = [s for s in sorted(c) if all(c[t] >= 0.8 for t in sorted(c) if t >= s)]
                lock.append(ok[0] if ok else None)
            cross = {s: float(np.nanmean([spearmanr(D[(a, s)][key], D[(b, s)][key])[0]
                                          for a, b in itertools.combinations(runs, 2) if (a, s) in D and (b, s) in D]))
                     for s in steps}
            pc = [curves[r].get(130000) for r in curves if 130000 in curves[r]]
            res[key] = {"lock_step_each": lock, "lock_step_median": float(np.median([x for x in lock if x is not None])) if any(lock) else None,
                        "mean_curve": {s: float(np.nanmean([curves[r][s] for r in curves if s in curves[r]])) for s in steps},
                        "cross_seed_same_step": cross, "pc_130k_vs_143k_min": float(min(pc)) if pc else None}
        out[size] = res
    (mc.RESULTS / "e40").mkdir(exist_ok=True)
    (mc.RESULTS / "e40" / "analysis.json").write_text(json.dumps(out, indent=1))
    for size, res in out.items():
        for key in ("S_prev", "S_ind"):
            r = res[key]
            print(size, key, "lock median", r["lock_step_median"], "each", r["lock_step_each"], "pc", r["pc_130k_vs_143k_min"])
            print("   curve", {s: round(v, 2) for s, v in r["mean_curve"].items()})
            print("   cross", {s: round(v, 2) for s, v in r["cross_seed_same_step"].items()})


if __name__ == "__main__":
    main()
