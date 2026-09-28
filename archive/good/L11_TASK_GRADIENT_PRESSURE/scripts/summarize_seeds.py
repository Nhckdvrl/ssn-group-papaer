#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
paths = [ROOT / f"results/pilot_seed{seed}_len512/summary.json" for seed in [17, 18, 19]]
reports = [json.loads(path.read_text()) for path in paths]
tasks = ["arithmetic", "math500_numeric"]
summary = {"seeds": [17, 18, 19], "source_summaries": [str(p) for p in paths], "tasks": {}}
for task in tasks:
    rows = [report["tasks"][task] for report in reports]
    primary = np.asarray([row["full_last_block_squared_norm_cross_product"] for row in rows])
    summary["tasks"][task] = {
        "primary_cross_products": primary.tolist(),
        "primary_mean": float(primary.mean()),
        "positive_seeds": int((primary > 0).sum()),
        "reward_means": [row["reward_mean"] for row in rows],
        "individual_norms": [row["attention_anatomy"]["mean_individual_norm"] for row in rows],
        "coherence_ratios": [row["attention_anatomy"]["coherence_ratio"] for row in rows],
    }
ratios = []
for report in reports:
    numerator = max(report["tasks"]["arithmetic"]["full_last_block_squared_norm_cross_product"], 0)
    denominator = max(report["tasks"]["math500_numeric"]["full_last_block_squared_norm_cross_product"], 0)
    ratios.append(None if denominator == 0 else numerator / denominator)
summary["arithmetic_over_math_nonnegative_ratio_by_seed"] = ratios
(ROOT / "results/pilot_multiseed_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

