"""Collect lm-eval outputs into the preregistered primary table.

Primary statistic: macro mean over MMLU / BBH / LAMBADA / GSM8K.
Always prints the per-benchmark breakdown; reporting GSM8K alone is forbidden by
PILOT_CARD.md.
"""
import glob, json, os, sys, collections

BENCH = {"mmlu": "MMLU", "bbh_cot_fewshot": "BBH",
         "lambada_openai": "LAMBADA", "gsm8k_cot": "GSM8K"}
KEY = {"mmlu": "acc,none", "bbh_cot_fewshot": "exact_match,get-answer",
       "lambada_openai": "acc,none", "gsm8k_cot": "exact_match,strict-match"}


def read_run(d):
    out = {}
    for task, name in BENCH.items():
        hits = glob.glob(os.path.join(d, task, "**", "results_*.json"), recursive=True)
        if not hits:
            continue
        r = json.load(open(sorted(hits)[-1]))["results"]
        agg = r.get(task) or r.get(task.split("_")[0])
        if agg is None:
            continue
        v = agg.get(KEY[task])
        if v is None:                       # fall back to the single acc-like metric
            cands = [k for k in agg if k.startswith(("acc,", "exact_match,"))]
            v = agg[cands[0]] if cands else None
        if v is not None:
            out[name] = 100 * v
    return out


def main(root="results/eval"):
    runs = {os.path.basename(d): read_run(d)
            for d in sorted(glob.glob(os.path.join(root, "*"))) if os.path.isdir(d)}
    runs = {k: v for k, v in runs.items() if v}
    cols = ["MMLU", "BBH", "LAMBADA", "GSM8K"]
    print(f"{'run':28s}" + "".join(f"{c:>10s}" for c in cols) + f"{'MACRO':>10s}")
    macro = {}
    for k, v in runs.items():
        if not all(c in v for c in cols):
            print(f"{k:28s}  incomplete: {sorted(v)}"); continue
        m = sum(v[c] for c in cols) / 4
        macro[k] = m
        print(f"{k:28s}" + "".join(f"{v[c]:10.2f}" for c in cols) + f"{m:10.2f}")

    def arm(prefix):
        return [m for k, m in macro.items() if k.startswith(prefix)]
    print()
    if "BASE" in macro:
        print(f"untrained base anchor: macro {macro['BASE']:.2f}\n")
    for a, b, label in [("PC-UC-UC", "PC-UC-CHATQA2", "positive control (dataset swap)"),
                        ("SHORT-SUPPORT", "LONG-FULL", "matched-supervision length")]:
        xa, xb = arm(a), arm(b)
        if not (xa and xb):
            continue
        g = sum(xb)/len(xb) - sum(xa)/len(xa)
        sp = max([max(xa)-min(xa) if len(xa) > 1 else 0,
                  max(xb)-min(xb) if len(xb) > 1 else 0])
        flag = " *** seed spread >= gap -> outcome D" if sp and sp >= abs(g) else ""
        print(f"{label:34s} gap {g:+6.2f}   worst within-arm seed spread {sp:5.2f}{flag}")

    # preregistered CAP / CTX decomposition
    print()
    def sub(prefix, cols_):
        vs = [v for k, v in runs.items() if k.startswith(prefix) and all(c in v for c in cols_)]
        return sum(sum(v[c] for c in cols_)/len(cols_) for v in vs)/len(vs) if vs else None
    CAP, CTX = ["MMLU", "BBH", "GSM8K"], ["LAMBADA"]
    for a, b, label in [("PC-UC-UC", "PC-UC-CHATQA2", "positive control"),
                        ("SHORT-SUPPORT", "LONG-FULL", "matched length")]:
        ca, cb = sub(a, CAP), sub(b, CAP)
        ta, tb = sub(a, CTX), sub(b, CTX)
        if None in (ca, cb, ta, tb):
            continue
        print(f"{label:20s} CAP {cb-ca:+6.2f}   CTX {tb-ta:+6.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:])
