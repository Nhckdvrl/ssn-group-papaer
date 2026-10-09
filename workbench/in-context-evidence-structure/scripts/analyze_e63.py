"""Message mediation; reject failed native reconstruction before inference."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_e58 import interval


def load(d):
    run = json.loads((d / "run.json").read_text())
    assert run["sanity_max_logit_error"] <= 0.10, run
    assert run["reconstruction_relative_rms_max"] < 0.02, run
    rows = [json.loads(s) for s in (d / "behavior.jsonl").read_text().splitlines()]
    values = {c: np.array([np.array(r["scores"][c]) * r["signs"] for r in rows]) for c in rows[0]["scores"]}
    return run, rows, values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--compare", help="The paired all_query run for E64")
    a = ap.parse_args()
    d = Path(a.directory)
    run, rows, values = load(d)
    means = {k: v.mean(1) for k, v in values.items()}
    den = means["base"] - means["sourceK"]
    rng = np.random.default_rng(630)
    ix = rng.integers(len(rows), size=(4000, len(rows)))
    out = {"run": run, "sourceK_effect": interval(den), "conditions": {}}
    for c, v in values.items():
        num = means["base"] - means[c]
        q = {"correct_margin": interval(means[c]), "accuracy": interval((v > 0).mean(1)), "remaining_raw_effect": interval(num)}
        if den.mean() > 0.2:
            rat = num[ix].mean(1) / np.maximum(den[ix].mean(1), 1e-6)
            q["remaining_fraction"] = {"mean": float(num.mean() / den.mean()), "ci95": np.quantile(rat, [0.025, 0.975]).tolist()}
        else:
            q["remaining_fraction"] = {"undefined": "Complete sourceK effect<=0.20 nats"}
        out["conditions"][c] = q
    out["attention"] = {}
    for key in ("fractions", "name_fractions"):
        if key not in rows[0]:
            continue
        base = np.array([r[key]["base"] for r in rows])
        swapped = np.array([r[key]["sourceK"] for r in rows])
        for l in range(base.shape[1]):
            out["attention"][f"{key}.layer{l}"] = {"base": interval(base[:, l].mean(1)),
                                                      "sourceK_minus_base": interval((swapped[:, l] - base[:, l]).mean(1))}
    if a.compare:
        other, rows2, v2 = load(Path(a.compare))
        assert [r["context"] for r in rows] == [r["context"] for r in rows2]
        for c in ("base", "sourceK"):
            assert np.array_equal(values[c], v2[c]), f"scope changed {c}"
        out["paired_all_query"] = {}
        for c in values:
            contrast = v2[c].mean(1) - means[c]
            q = {"all_minus_final_margin": interval(contrast)}
            if den.mean() > 0.2:
                rat = contrast[ix].mean(1) / np.maximum(den[ix].mean(1), 1e-6)
                q["final_minus_all_remaining_fraction"] = {"mean": float(contrast.mean() / den.mean()),
                                                             "ci95": np.quantile(rat, [0.025, 0.975]).tolist()}
            out["paired_all_query"][c] = q
    (d / "analysis.json").write_text(json.dumps(out, indent=2))
    print("source effect", out["sourceK_effect"])
    for c in ("freeze_label", "freeze_early_label", "freeze_late_label", "freeze_name", "freeze_all"):
        print(c, out["conditions"][c]["remaining_fraction"])
    if a.compare:
        print(json.dumps(out["paired_all_query"], indent=2))


if __name__ == "__main__":
    main()
