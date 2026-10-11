"""Paired bootstrap of native relay ablations and source perturbation effects."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / "run.json").read_text())
    assert run["sanity_max_error"] <= 0.1 and run["reconstruction_relative_rms_max"] < 0.02
    rows = [json.loads(l) for l in (d / "behavior.jsonl").read_text().splitlines()]
    values = {k: np.array([np.array(r["scores"][k]) * r["signs"] for r in rows]) for k in rows[0]["scores"]}
    means = {k: v.mean(1) for k, v in values.items()}
    acc = {k: (v > 0).mean(1) for k, v in values.items()}
    effect = means["base"] - means["sourceK"]
    rng = np.random.default_rng(650)
    ix = rng.integers(len(rows), size=(4000, len(rows)))
    out = {"run": run, "sourceK_effect": interval(effect), "conditions": {}, "native_contrasts": {}}
    for k, v in values.items():
        result = {"margin": interval(means[k]), "accuracy": interval(acc[k])}
        if k.startswith("freeze_"):
            num = means["base"] - means[k]
            result["remaining_raw_effect"] = interval(num)
            if effect.mean() > 0.2:
                r = num[ix].mean(1) / np.maximum(effect[ix].mean(1), 1e-6)
                result["remaining_fraction"] = {"mean": float(num.mean() / effect.mean()), "ci95": np.quantile(r, [0.025, 0.975]).tolist()}
        out["conditions"][k] = result
    for k in ("drop_direct", "drop_relay", "drop_both"):
        out["native_contrasts"][k] = {
            "accuracy_minus_base": interval(acc[k + ".base"] - acc["base"]),
            "margin_minus_base": interval(means[k + ".base"] - means["base"]),
            "source_effect": interval(means[k + ".base"] - means[k + ".sourceK"]),
            "source_effect_minus_native": interval(means[k + ".base"] - means[k + ".sourceK"] - effect)}
    out["native_contrasts"]["deletion_interaction"] = {
        "margin": interval(means["drop_both.base"] - means["drop_direct.base"] - means["drop_relay.base"] + means["base"]),
        "accuracy": interval(acc["drop_both.base"] - acc["drop_direct.base"] - acc["drop_relay.base"] + acc["base"])}
    (d / "analysis.json").write_text(json.dumps(out, indent=2))
    print("sourceK effect", out["sourceK_effect"])
    for k in ("freeze_p_label", "freeze_q_input", "freeze_q_source", "freeze_q_marker", "freeze_q_relay", "freeze_direct_and_relay"):
        print(k, out["conditions"][k].get("remaining_fraction"))
    print(json.dumps(out["native_contrasts"], indent=2))


if __name__ == "__main__":
    main()
