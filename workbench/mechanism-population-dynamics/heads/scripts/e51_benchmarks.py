"""E51: init vs data variance components of DataDecide downstream benchmarks (released eval results). Protocol: E51 card."""
import json

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from scipy.stats import f as fdist

import mp_common as mc

EVALS = "/home/xiang/mechpop_cache/datadecide/evals/data/macro_avg-00000-of-00001.parquet"
PLAN = "/home/xiang/mechpop_cache/datadecide/e45_plan.json"
SIZES = ("4M", "6M", "8M", "10M", "14M", "16M", "20M", "60M", "90M", "150M", "300M", "530M", "750M", "1B")
METRICS = ("primary_metric", "correct_logit_per_byte")
NAMES = {  # eval-table data names -> HF recipe names (DataDecide-<recipe>-<size>)
    "DCLM-Baseline": "dclm-baseline", "C4": "c4", "DCLM-Baseline (QC 7%, FW2)": "dclm-baseline-qc-7p-fw2",
    "DCLM-Baseline (QC 7%, FW3)": "dclm-baseline-qc-7p-fw3", "DCLM-Baseline (QC FW 10%)": "dclm-baseline-qc-fw-10p",
    "DCLM-Baseline (QC FW 3%)": "dclm-baseline-qc-fw-3p", "Dolma1.6++": "dolma1_6plus", "Dolma1.7": "dolma1_7",
    "DCLM-Baseline 75% / Dolma 25%": "dclm-baseline-75p-dolma1.7-25p",
    "DCLM-Baseline 50% / Dolma 50%": "dclm-baseline-50p-dolma1.7-50p",
    "DCLM-Baseline 25% / Dolma 75%": "dclm-baseline-25p-dolma1.7-75p", "Falcon": "falcon", "Falcon+CC": "falcon-and-cc",
    "Falcon+CC (QC 10%)": "falcon-and-cc-qc-10p", "Falcon+CC (QC 20%)": "falcon-and-cc-qc-20p",
    "Falcon+CC (QC Orig 10%)": "falcon-and-cc-qc-orig-10p", "Falcon+CC (QC Tulu 10%)": "falcon-and-cc-qc-tulu-10p",
    "FineWeb-Edu": "fineweb-edu", "Dolma1.7 (no code)": "dolma1_7-no-code", "Dolma1.7 (no Flan)": "dolma1_7-no-flan",
    "Dolma1.7 (no math, code)": "dolma1_7-no-math-code", "Dolma1.7 (no Reddit)": "dolma1_7-no-reddit",
    "DCLM-Baseline (QC 10%)": "dclm-baseline-qc-10p", "DCLM-Baseline (QC 20%)": "dclm-baseline-qc-20p",
    "FineWeb-Pro": "fineweb-pro"}


def components(Y):
    """Y [data, init], one observation per cell -> unbiased variance components and F-test p-values (as E35, P08)."""
    a, b = Y.shape
    gm = Y.mean()
    msd = b * ((Y.mean(1) - gm) ** 2).sum() / (a - 1)
    msi = a * ((Y.mean(0) - gm) ** 2).sum() / (b - 1)
    msr = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum() / ((a - 1) * (b - 1))
    vd, vi = max((msd - msr) / b, 0.0), max((msi - msr) / a, 0.0)
    tot = vd + vi + msr
    return {"frac_data": vd / tot, "frac_init": vi / tot, "frac_resid": msr / tot,
            "p_data": float(fdist.sf(msd / msr, a - 1, (a - 1) * (b - 1))),
            "p_init": float(fdist.sf(msi / msr, b - 1, (a - 1) * (b - 1)))}


def main():
    df = pd.read_parquet(EVALS, columns=["params", "data", "task", "step", "seed", "metrics"])
    df["recipe"] = df["data"].map(NAMES)
    assert df["recipe"].notna().all(), set(df.loc[df["recipe"].isna(), "data"])
    plan = json.load(open(PLAN))
    out = {"cells": {}, "summary": {}}
    for size in SIZES:
        if size == "1B":
            seeds, step, recs = ("default", "large aux 2", "large aux 3"), 69369, sorted(set(NAMES.values()))
        else:
            seeds, step, recs = ("default", "small aux 2", "small aux 3"), plan[size]["step"], plan[size]["recipes"]
        # the eval table does not contain every checkpoint: use the largest evaluated step <= the E45 step that all
        # three seeds have (only changes 14M: 21953 -> 20000 and 750M: 27500 -> 26250)
        ev = [set(df[(df.params == size) & (df.seed == s)].step.unique()) for s in seeds]
        step = max(x for x in set.intersection(*ev) if x <= step)
        sub = df[(df.params == size) & (df.step == step) & df.seed.isin(seeds) & df.recipe.isin(recs)]
        for task in sorted(sub.task.unique()):
            t = sub[sub.task == task]
            for m in METRICS:
                vals = {(r.recipe, r.seed): json.loads(r.metrics).get(m) for r in t.itertuples()}
                ok = [rc for rc in recs if all(vals.get((rc, s)) is not None for s in seeds)]
                if len(ok) < 5:
                    continue
                Y = np.array([[vals[(rc, s)] for s in seeds] for rc in ok], dtype=float)
                out["cells"][f"{size}|{task}|{m}"] = {**components(Y), "n_recipes": len(ok), "step": int(step)}
    for m in METRICS:
        C = [v for k, v in out["cells"].items() if k.endswith(m)]
        n = len(C)
        ki, kd = sum(c["p_init"] < 0.05 for c in C), sum(c["p_data"] < 0.05 for c in C)
        out["summary"][m] = {"n_cells": n, "frac_init_sig": ki / n, "frac_data_sig": kd / n,
                             "binom_p_init_vs_5pct": float(binomtest(ki, n, 0.05, alternative="greater").pvalue),
                             "median_frac_init": float(np.median([c["frac_init"] for c in C])),
                             "median_frac_data": float(np.median([c["frac_data"] for c in C])),
                             "median_frac_resid": float(np.median([c["frac_resid"] for c in C]))}
        by_size = {}
        for s in SIZES:
            Cs = [v for k, v in out["cells"].items() if k.startswith(s + "|") and k.endswith(m)]
            if Cs:
                by_size[s] = {"init_sig": sum(c["p_init"] < 0.05 for c in Cs), "data_sig": sum(c["p_data"] < 0.05 for c in Cs),
                              "n": len(Cs), "median_frac_init": float(np.median([c["frac_init"] for c in Cs])),
                              "median_frac_data": float(np.median([c["frac_data"] for c in Cs]))}
        out["summary"][m]["by_size"] = by_size
    (mc.RESULTS / "e51").mkdir(exist_ok=True)
    (mc.RESULTS / "e51" / "analysis.json").write_text(json.dumps(out, indent=1))
    for m, s in out["summary"].items():
        print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k != "by_size"})
        for size, r in s["by_size"].items():
            print("   ", size, r)


if __name__ == "__main__":
    main()
