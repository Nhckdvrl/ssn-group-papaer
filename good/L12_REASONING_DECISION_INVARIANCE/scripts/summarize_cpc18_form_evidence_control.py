#!/usr/bin/env python3
"""Summarize E20 evidence control separately for raw and summary forms."""

import json

import numpy as np
import pandas as pd

from cpc18_form_evidence_common import CONFIG, ROOT


def bootstrap(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def effects(frame):
    keys = ["problem", "form", "order", "a_sample_index", "b_sample_index"]
    cells = frame.pivot(index=keys, columns=["prompt_evidence", "trajectory_evidence"], values="p_a_choice")
    result = pd.DataFrame(index=cells.index)
    result["delta_r"] = (
        cells[("A", "A")] - cells[("A", "B")]
        + cells[("B", "A")] - cells[("B", "B")]
    ) / 2
    result["delta_p"] = (
        cells[("A", "A")] - cells[("B", "A")]
        + cells[("A", "B")] - cells[("B", "B")]
    ) / 2
    result["delta_control"] = result.delta_r - result.delta_p
    return result.reset_index()


def metric(values, seed):
    return {
        "mean": float(values.mean()),
        "base_decision_bootstrap_ci95": bootstrap(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def main():
    output = ROOT / CONFIG["result_dir"]
    units = {}
    summary = {"design": "L12-E20 evidence prompt-by-trajectory factorial within form"}
    for offset, spec in enumerate(CONFIG["regimes"]):
        name = spec["name"]
        frame = pd.read_json(output / "raw" / "control" / f"{name}.jsonl", lines=True)
        units[name] = effects(frame)
        summary[name] = {"pair": spec["pair"], "role": spec["role"], "forms": {}}
        for form_index, form in enumerate(("raw", "summary")):
            base = units[name][units[name].form == form].groupby("problem")[["delta_p", "delta_r", "delta_control"]].mean()
            summary[name]["forms"][form] = {
                "n_base_decisions": int(len(base)),
                **{key: metric(base[key], CONFIG["seed"] + offset * 10 + form_index * 3 + i) for i, key in enumerate(("delta_p", "delta_r", "delta_control"))},
            }
    rows = []
    summary["reasoning_minus_standard"] = {}
    for pair_index, pair in enumerate(("olmo_sft", "qwen_mode")):
        specs = [item for item in CONFIG["regimes"] if item["pair"] == pair]
        reasoning = next(item["name"] for item in specs if item["role"] == "reasoning")
        standard = next(item["name"] for item in specs if item["role"] == "standard")
        pair_summary = {"reasoning_regime": reasoning, "standard_regime": standard, "forms": {}}
        for form_index, form in enumerate(("raw", "summary")):
            r = units[reasoning][units[reasoning].form == form].groupby("problem")[["delta_p", "delta_r", "delta_control"]].mean()
            s = units[standard][units[standard].form == form].groupby("problem")[["delta_p", "delta_r", "delta_control"]].mean()
            joined = r.join(s, lsuffix="_reasoning", rsuffix="_standard", how="inner")
            form_summary = {"n_paired_base_decisions": int(len(joined))}
            for index, key in enumerate(("delta_p", "delta_r", "delta_control")):
                values = joined[f"{key}_reasoning"] - joined[f"{key}_standard"]
                form_summary[f"{key}_difference"] = metric(values, CONFIG["seed"] + 100 + pair_index * 10 + form_index * 3 + index)
            pair_summary["forms"][form] = form_summary
            rows.extend({"pair": pair, "form": form, **row} for row in joined.reset_index().to_dict(orient="records"))
        summary["reasoning_minus_standard"][pair] = pair_summary
    with (output / "control_unit_metrics.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    (output / "control_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
