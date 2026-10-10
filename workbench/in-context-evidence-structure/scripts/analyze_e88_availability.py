"""Discovery-posthoc, confirmation-frozen explicit/inferred transfer comparison."""
import argparse
import json
from pathlib import Path
import numpy as np
from e88_criterion_transfer import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    a = ap.parse_args()
    dest = Path(a.directory)
    rows = [json.loads(line) for line in (dest / "behavior.jsonl").read_text().splitlines()]
    run = json.loads((dest / "run.json").read_text())
    assert len(rows) == run["args"]["n"]
    columns = []
    for patch, base in [("criterion_patch", "base"), ("flip", "base"),
                        ("explicit_criterion_patch", "explicit"), ("explicit_flip", "explicit")]:
        columns.append(np.array([np.mean([
            (score[patch]["z"] - score[base]["z"]) * (q["donor_gold"] - q["recipient_gold"]) / 2
            for q, score in zip(row["queries"], row["scores"]) if q["food"] != q["service"]]) for row in rows]))
    ip, inn, ep, en = columns
    indices = np.random.default_rng(880).integers(len(rows), size=(10000, len(rows)))
    boot = np.array([c[indices].mean(1) for c in columns])
    means = np.array([c.mean() for c in columns])
    out = {"stage": run["args"]["stage"], "protocol": "POST-HOC discovery; frozen before confirmation",
           "absolute_explicit_minus_inferred_transfer": interval(ep - ip),
           "native_denominators": {"inferred": interval(inn), "explicit": interval(en)},
           "bootstrap_min_abs_native_denominator": [float(np.abs(boot[i]).min()) for i in (1, 3)],
           "bootstrap_native_denominator_below_point1_fraction": [float((np.abs(boot[i]) < .1).mean()) for i in (1, 3)]}
    if np.all(np.abs(means[[1, 3]]) > .1) and np.all(boot[[1, 3]] != 0):
        ratios = boot[[0, 2]] / boot[[1, 3]]
        out["relative_transfer"] = {
            "inferred": {"mean_ratio": float(means[0] / means[1]), "ci95": np.quantile(ratios[0], [.025, .975]).tolist()},
            "explicit": {"mean_ratio": float(means[2] / means[3]), "ci95": np.quantile(ratios[1], [.025, .975]).tolist()},
            "explicit_minus_inferred": {"mean_ratio_difference": float(means[2]/means[3] - means[0]/means[1]),
                                         "ci95": np.quantile(ratios[1] - ratios[0], [.025, .975]).tolist()}}
    else:
        out["relative_transfer"] = None
    (dest / "availability_comparison.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
