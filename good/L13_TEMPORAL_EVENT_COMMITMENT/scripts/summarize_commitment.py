#!/usr/bin/env python
"""Summarise L13 commitment runs with paired bootstrap CIs over base scenarios."""
import argparse
import collections
import json
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

CONDS = [
    "after",
    "before_neutral",
    "before_confirm",
    "before_cancel",
    "nontemporal_neutral",
]
LABELS = ["YES", "NO", "NOT_DETERMINED"]
N_BOOT = 10000


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def per_base_tables(rows):
    """{(task_order, condition): {base_id: {label: mean prob over permutations}}}"""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        acc[(r["task_order"], r["condition"])][r["base_id"]].append(r["probs"])
    out = {}
    for key, bases in acc.items():
        out[key] = {
            b: {lab: statistics.fmean(p[lab] for p in ps) for lab in LABELS}
            for b, ps in bases.items()
        }
    return out


def boot(values_by_base, bases, rng, stat):
    """Paired bootstrap over bases. `stat` maps a list of per-base values -> float."""
    idx = rng.integers(0, len(bases), size=(N_BOOT, len(bases)))
    arr = np.array([values_by_base[b] for b in bases], dtype=float)
    samples = stat(arr[idx])
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return float(stat(arr[None, :])[0]), float(lo), float(hi)


def mean_stat(a):
    return a.mean(axis=1)


def summarise_model(model_dir, rng):
    import glob

    rows = []
    for path in sorted(glob.glob(os.path.join(model_dir, "strict*.jsonl"))):
        rows.extend(read_jsonl(path))
    tables = per_base_tables(rows)
    orders = sorted({r["task_order"] for r in rows})
    bases = sorted({r["base_id"] for r in rows})

    res = {"orders": orders, "n_bases": len(bases), "conditions": {}, "contrasts": {}}

    for order in orders:
        for cond in CONDS:
            t = tables[(order, cond)]
            for lab in LABELS:
                m, lo, hi = boot({b: t[b][lab] for b in bases}, bases, rng, mean_stat)
                res["conditions"].setdefault(order, {}).setdefault(cond, {})[
                    f"p_{lab}"
                ] = [round(m, 4), round(lo, 4), round(hi, 4)]
            gold = {
                "after": "YES",
                "before_neutral": "NOT_DETERMINED",
                "before_confirm": "YES",
                "before_cancel": "NO",
                "nontemporal_neutral": "NOT_DETERMINED",
            }[cond]
            acc = {b: float(max(t[b], key=t[b].get) == gold) for b in bases}
            m, lo, hi = boot(acc, bases, rng, mean_stat)
            res["conditions"][order][cond]["accuracy"] = [
                round(m, 4),
                round(lo, 4),
                round(hi, 4),
            ]

    def commit(order, cond, b):
        return tables[(order, cond)][b]["YES"]

    def mass(order, cond, b, label):
        return tables[(order, cond)][b][label]

    ff = "fact_first"
    if ff in orders:
        res["contrasts"]["neutral_gap"] = boot(
            {b: commit(ff, "before_neutral", b) - commit(ff, "nontemporal_neutral", b) for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["veridicality_gap"] = boot(
            {b: commit(ff, "after", b) - commit(ff, "before_neutral", b) for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["confirm_update"] = boot(
            {b: commit(ff, "before_confirm", b) - commit(ff, "before_neutral", b) for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["cancel_update"] = boot(
            {b: commit(ff, "before_neutral", b) - commit(ff, "before_cancel", b) for b in bases},
            bases, rng, mean_stat,
        )
        # floor-aware version: movement of probability mass onto the label the
        # continuation newly licenses. `update_asymmetry` alone is confounded by the
        # floor when commit(before_neutral) is already near zero.
        res["contrasts"]["gold_update_confirm"] = boot(
            {b: mass(ff, "before_confirm", b, "YES") - mass(ff, "before_neutral", b, "YES") for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["gold_update_cancel"] = boot(
            {b: mass(ff, "before_cancel", b, "NO") - mass(ff, "before_neutral", b, "NO") for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["gold_update_asymmetry"] = boot(
            {
                b: (mass(ff, "before_confirm", b, "YES") - mass(ff, "before_neutral", b, "YES"))
                - (mass(ff, "before_cancel", b, "NO") - mass(ff, "before_neutral", b, "NO"))
                for b in bases
            },
            bases, rng, mean_stat,
        )
        res["contrasts"]["update_asymmetry"] = boot(
            {
                b: abs(commit(ff, "before_confirm", b) - commit(ff, "before_neutral", b))
                - abs(commit(ff, "before_neutral", b) - commit(ff, "before_cancel", b))
                for b in bases
            },
            bases, rng, mean_stat,
        )

    for order in orders:
        if order == ff:
            continue
        for cond in CONDS:
            res["contrasts"][f"{order}_effect__{cond}"] = boot(
                {b: commit(order, cond, b) - commit(ff, cond, b) for b in bases},
                bases, rng, mean_stat,
            )
    if "timeline_first" in orders and "paraphrase_first" in orders:
        for cond in CONDS:
            res["contrasts"][f"timeline_minus_paraphrase__{cond}"] = boot(
                {
                    b: commit("timeline_first", cond, b) - commit("paraphrase_first", cond, b)
                    for b in bases
                },
                bases, rng, mean_stat,
            )

    if "timeline_first" in orders and "paraphrase_first" in orders:
        # is the timeline effect specific to the unresolved *temporal* condition?
        def did(cond, b):
            return commit("timeline_first", cond, b) - commit("paraphrase_first", cond, b)

        res["contrasts"]["timeline_specificity_vs_nontemporal"] = boot(
            {b: did("before_neutral", b) - did("nontemporal_neutral", b) for b in bases},
            bases, rng, mean_stat,
        )
        res["contrasts"]["timeline_specificity_vs_after"] = boot(
            {b: did("before_neutral", b) - did("after", b) for b in bases},
            bases, rng, mean_stat,
        )

    # E05: a non-generative temporal demand vs a matched non-temporal demand.
    if "order_mc_first" in orders and "topic_mc_first" in orders:
        for cond in CONDS:
            res["contrasts"][f"order_minus_topic_mc__{cond}"] = boot(
                {
                    b: commit("order_mc_first", cond, b) - commit("topic_mc_first", cond, b)
                    for b in bases
                },
                bases, rng, mean_stat,
            )
    # E04: does the effect survive an explicit "only events that actually happened"?
    if "timeline_strict_first" in orders and "timeline_first" in orders:
        for cond in CONDS:
            res["contrasts"][f"strict_minus_open_timeline__{cond}"] = boot(
                {
                    b: commit("timeline_strict_first", cond, b)
                    - commit("timeline_first", cond, b)
                    for b in bases
                },
                bases, rng, mean_stat,
            )

    lik_path = os.path.join(model_dir, "likelihood.jsonl")
    if os.path.exists(lik_path):
        lik = read_jsonl(lik_path)
        by = collections.defaultdict(dict)
        for r in lik:
            by[r["condition"]][r["base_id"]] = r["expected_rating"]
        res["likelihood"] = {
            cond: [round(v, 4) for v in boot(by[cond], bases, rng, mean_stat)]
            for cond in CONDS
            if cond in by
        }

    for k, v in res["contrasts"].items():
        res["contrasts"][k] = [round(x, 4) for x in v]
    return res


def fmt(triple):
    m, lo, hi = triple
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))
    tag_dir = os.path.join(PROJ, "results", cfg["tag"])

    rng = np.random.default_rng(cfg["seed"])
    out = {"tag": cfg["tag"], "n_boot": N_BOOT, "models": {}}
    for spec in cfg["models"]:
        d = os.path.join(tag_dir, spec["slug"])
        if not os.path.exists(os.path.join(d, "strict.jsonl")):
            continue
        out["models"][spec["slug"]] = summarise_model(d, rng)
        out["models"][spec["slug"]]["family"] = spec["family"]

    with open(os.path.join(tag_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    lines = [f"# L13 summary — {cfg['tag']}", ""]
    for slug, r in out["models"].items():
        lines += [f"## {slug} ({r['family']}), {r['n_bases']} bases", ""]
        lines += ["| condition | P(YES) | P(NO) | P(ND) | acc |", "|---|---|---|---|---|"]
        for cond in CONDS:
            c = r["conditions"]["fact_first"][cond]
            lines.append(
                f"| {cond} | {c['p_YES'][0]:.3f} | {c['p_NO'][0]:.3f} | "
                f"{c['p_NOT_DETERMINED'][0]:.3f} | {c['accuracy'][0]:.3f} |"
            )
        lines += ["", "| contrast | mean [95% CI] |", "|---|---|"]
        for k, v in r["contrasts"].items():
            lines.append(f"| {k} | {fmt(v)} |")
        if "likelihood" in r:
            lines += ["", "| condition | E[rating 1-5] |", "|---|---|"]
            for cond, v in r["likelihood"].items():
                lines.append(f"| {cond} | {v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}] |")
        lines.append("")
    with open(os.path.join(tag_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
