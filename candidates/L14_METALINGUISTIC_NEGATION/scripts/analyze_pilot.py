#!/usr/bin/env python3
"""Analyze L14 E01/E02 JSONL outputs.

Independent resampling unit is lexical/discourse base_id. Reports DN and MN
separately; the DN-minus-MN intervention contrast is a decision aid, not a new
headline metric.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("results", nargs="+", type=Path)
    p.add_argument("--bootstrap", type=int, default=10000)
    p.add_argument("--seed", type=int, default=20260911)
    p.add_argument("--out", type=Path, default=None)
    return p.parse_args()


def load(paths):
    rows = []
    for path in paths:
        with path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def ci(xs, alpha=0.05):
    ys = sorted(xs)
    if not ys:
        return (float("nan"), float("nan"))
    lo = ys[int((alpha / 2) * (len(ys) - 1))]
    hi = ys[int((1 - alpha / 2) * (len(ys) - 1))]
    return lo, hi


def summarize_model(rows, n_boot, rng):
    # one record per base x condition x arm is expected after mapping averaging
    by_key = {}
    for r in rows:
        key = (r["base_id"], r["condition"], r["arm"])
        if key in by_key:
            raise ValueError(f"duplicate record: {key}")
        by_key[key] = r

    bases = sorted({r["base_id"] for r in rows})

    # A base passes controls only when baseline POS and PARAPHRASE are present and correct.
    def control_pass(b):
        need = [(b, "POS", "baseline"), (b, "PARAPHRASE", "baseline")]
        return all(k in by_key and by_key[k]["correct"] for k in need)

    valid = [b for b in bases if control_pass(b)]

    def get(b, cond, arm, field="p_gold"):
        return by_key[(b, cond, arm)][field]

    complete = [
        b for b in valid
        if all((b, c, a) in by_key for c in ("DN", "MN") for a in ("baseline", "warning"))
    ]
    if not complete:
        raise ValueError("no control-passing complete bases")

    non_scalar = [
        b for b in complete
        if by_key[(b, "MN", "baseline")].get("subtype") != "scalar_diagnostic"
    ]

    def stats(sample):
        dn_b = mean(get(b, "DN", "baseline") for b in sample)
        mn_b = mean(get(b, "MN", "baseline") for b in sample)
        dn_w = mean(get(b, "DN", "warning") for b in sample)
        mn_w = mean(get(b, "MN", "warning") for b in sample)
        ddn = dn_w - dn_b
        dmn = mn_w - mn_b
        return {
            "dn_baseline_p_correct": dn_b,
            "mn_baseline_p_correct": mn_b,
            "dn_warning_p_correct": dn_w,
            "mn_warning_p_correct": mn_w,
            "delta_dn": ddn,
            "delta_mn": dmn,
            "delta_dn_minus_delta_mn": ddn - dmn,
        }

    def boot(sample):
        point = stats(sample)
        draws = defaultdict(list)
        for _ in range(n_boot):
            bs = [rng.choice(sample) for _ in sample]
            s = stats(bs)
            for k, v in s.items():
                draws[k].append(v)
        return {
            k: {"estimate": point[k], "ci95": list(ci(draws[k]))}
            for k in point
        }

    out = {
        "n_bases_total": len(bases),
        "n_control_passing": len(valid),
        "n_complete_control_passing": len(complete),
        "all_complete": boot(complete),
    }
    if non_scalar:
        out["non_scalar_only"] = {
            "n_bases": len(non_scalar),
            "stats": boot(non_scalar),
        }

    # Discrete rates for readability, secondary to probability-mass estimates.
    def discrete(sample, cond, arm):
        return mean(float(get(b, cond, arm, "correct")) for b in sample)

    out["discrete_accuracy"] = {
        f"{cond.lower()}_{arm}": discrete(complete, cond, arm)
        for cond in ("DN", "MN") for arm in ("baseline", "warning")
    }
    return out


def main():
    args = parse_args()
    rows = load(args.results)
    models = sorted({r["model"] for r in rows})
    report = {
        "bootstrap_unit": "base_id",
        "n_bootstrap": args.bootstrap,
        "models": {},
    }
    for i, model in enumerate(models):
        rng = random.Random(args.seed + i)
        model_rows = [r for r in rows if r["model"] == model]
        report["models"][model] = summarize_model(model_rows, args.bootstrap, rng)

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")


if __name__ == "__main__":
    main()
