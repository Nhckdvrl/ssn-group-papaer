"""Arm-wise IFEval results and the three pre-registered contrasts.

Uncertainty follows notes/E01_DESIGN.md §6:

  * the inferential unit is the PROMPT. A prompt carries 1-3 constraints and
    those are never counted as independent samples; instruction-level rates are
    reported but their interval is still clustered by prompt.
  * the primary interval resamples prompts AND training seeds, so it covers
    evaluation variance and training variance together.
  * a secondary interval resamples prompts only, holding the three seeds fixed,
    to show how much of the width is training noise.
  * arms are resampled with the SAME prompt draw, because they share the
    evaluation set; that pairing is what makes a difference interval tight
    enough to be informative.
"""
import argparse
import itertools
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARMS = ["P", "S", "D_mask", "D_rt"]
CONTRASTS = [
    ("Delta_corr", "P", "S", "same-marginal value of correct vs wrong correspondence"),
    ("Delta_pair", "P", "D_mask", "correct correspondence vs no correspondence"),
    ("Delta_wrong", "D_mask", "S", "wrong correspondence vs no correspondence"),
    ("Delta_pair_rt", "P", "D_rt", "correct correspondence vs Response Tuning"),
    ("Delta_wrong_rt", "D_rt", "S", "wrong correspondence vs Response Tuning"),
    ("construct_D", "D_mask", "D_rt", "construct check: budget-matched vs RT"),
]
METRICS = ["strict_prompt", "loose_prompt", "strict_instruction", "loose_instruction"]


def load(evals, epoch):
    """-> {arm: {seed: {metric: per-prompt vector}}}, keyed by prompt order."""
    data, keys = {}, None
    for arm in ARMS:
        data[arm] = {}
        for d in sorted(pathlib.Path(evals).glob(f"{arm}_s*_ep{epoch}")):
            rows = [json.loads(l) for l in (d / "per_prompt.jsonl").open()]
            rows.sort(key=lambda r: r["key"])
            k = [r["key"] for r in rows]
            if keys is None:
                keys = k
            assert k == keys, f"prompt set mismatch in {d}"
            seed = int(d.name.split("_s")[1].split("_ep")[0])
            data[arm][seed] = {
                "strict_prompt": np.array([float(r["strict_prompt"]) for r in rows]),
                "loose_prompt": np.array([float(r["loose_prompt"]) for r in rows]),
                # per-prompt instruction rates; the prompt stays the cluster
                "strict_instruction": np.array([np.mean(r["strict_follow_list"]) for r in rows]),
                "loose_instruction": np.array([np.mean(r["loose_follow_list"]) for r in rows]),
                "n_instructions": np.array([len(r["instruction_ids"]) for r in rows], float),
            }
    return data, keys


def arm_mean(data, arm, metric, prompt_idx, seeds):
    """Instruction-level metrics are weighted by constraints per prompt."""
    vals = []
    for s in seeds:
        d = data[arm][s]
        v = d[metric][prompt_idx]
        if metric.endswith("instruction"):
            w = d["n_instructions"][prompt_idx]
            vals.append(float(np.sum(v * w) / np.sum(w)))
        else:
            vals.append(float(np.mean(v)))
    return float(np.mean(vals))


def bootstrap(data, metric, n_boot, resample_seeds, rng):
    seeds = sorted(set(itertools.chain.from_iterable(data[a] for a in ARMS)))
    n = len(data[ARMS[0]][seeds[0]][metric])
    point = {a: arm_mean(data, a, metric, np.arange(n), seeds) for a in ARMS}
    draws = {a: [] for a in ARMS}
    for _ in range(n_boot):
        pi = rng.integers(0, n, n)
        sd = list(rng.choice(seeds, len(seeds), replace=True)) if resample_seeds else seeds
        for a in ARMS:
            draws[a].append(arm_mean(data, a, metric, pi, sd))
    draws = {a: np.array(v) for a, v in draws.items()}
    out = {"point": point, "arm_ci": {}, "contrasts": {}}
    for a in ARMS:
        lo, hi = np.percentile(draws[a], [2.5, 97.5])
        out["arm_ci"][a] = [float(lo), float(hi)]
    for name, x, y, desc in CONTRASTS:
        d = draws[x] - draws[y]
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["contrasts"][name] = {
            "arms": f"{x} - {y}",
            "meaning": desc,
            "point_pp": 100 * (point[x] - point[y]),
            "ci95_pp": [100 * float(lo), 100 * float(hi)],
            "excludes_zero": bool(lo > 0 or hi < 0),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evals", default=str(ROOT / "results" / "evals"))
    ap.add_argument("--epoch", type=int, default=3)
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    data, keys = load(args.evals, args.epoch)
    rng = np.random.default_rng(20260913)

    report = {"epoch": args.epoch, "n_prompts": len(keys),
              "seeds": {a: sorted(data[a]) for a in ARMS}, "per_seed": {}, "metrics": {}}
    for a in ARMS:
        report["per_seed"][a] = {
            str(s): {m: 100 * arm_mean(data, a, m, np.arange(len(keys)), [s]) for m in METRICS}
            for s in sorted(data[a])
        }
    for m in METRICS:
        report["metrics"][m] = {
            "primary_prompt_and_seed_resampled": bootstrap(data, m, args.n_boot, True, rng),
            "secondary_prompt_resampled_only": bootstrap(data, m, args.n_boot, False, rng),
        }

    base = pathlib.Path(args.evals) / "base" / "summary.json"
    if base.exists():
        report["untuned_base"] = json.loads(base.read_text())

    txt = json.dumps(report, indent=2)
    if args.out:
        pathlib.Path(args.out).write_text(txt + "\n")

    pm = report["metrics"]["strict_prompt"]["primary_prompt_and_seed_resampled"]
    print(f"\nIFEval strict prompt-level accuracy, epoch {args.epoch} "
          f"({len(keys)} prompts, seeds {report['seeds']['P']}):\n")
    for a in ARMS:
        lo, hi = pm["arm_ci"][a]
        per = [report["per_seed"][a][str(s)]["strict_prompt"] for s in sorted(data[a])]
        print(f"  {a:8s} {100*pm['point'][a]:6.2f}  [{100*lo:5.2f}, {100*hi:5.2f}]"
              f"   seeds: {', '.join(f'{v:.2f}' for v in per)}")
    print("\n  contrasts (percentage points, prompt-clustered + seed-resampled):")
    for name, _, _, _ in CONTRASTS:
        c = pm["contrasts"][name]
        flag = "*" if c["excludes_zero"] else " "
        print(f"   {flag} {name:15s} {c['arms']:18s} {c['point_pp']:+6.2f}  "
              f"[{c['ci95_pp'][0]:+6.2f}, {c['ci95_pp'][1]:+6.2f}]   {c['meaning']}")
    print()


if __name__ == "__main__":
    main()
