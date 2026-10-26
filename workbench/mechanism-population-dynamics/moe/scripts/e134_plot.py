#!/usr/bin/env python3
"""Plot E134 native-relative NLL/KL effects after all six settings complete."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results/e134/necessity.json"
DEFAULT_OUTPUT = ROOT / "results/e134"
MODEL_ORDER = [
    "seed0_anchor",
    "seed1_order0",
    "seed2_order0",
    "seed3_order0",
    "seed4_order0",
    "public_olmoe_main",
]
MODEL_LABELS = {
    "seed0_anchor": "Controlled seed0\nanchor",
    "seed1_order0": "Controlled seed1",
    "seed2_order0": "Controlled seed2",
    "seed3_order0": "Controlled seed3",
    "seed4_order0": "Controlled seed4",
    "public_olmoe_main": "Public OLMoE\nmain",
}
MODEL_KIND = {name: ("public native" if name == "public_olmoe_main" else "controlled seed") for name in MODEL_ORDER}
CONDITION_ORDER = ["c", "gamma_c", "r", "zero"]
CONDITION_LABELS = {"c": "c", "gamma_c": "γc", "r": "r", "zero": "zero"}
COLORS = {"c": "#4C78A8", "gamma_c": "#F58518", "r": "#54A24B", "zero": "#E45756"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_summary(data: dict) -> None:
    if data.get("experiment") != "E134" or data.get("status") != "complete":
        raise ValueError(f"E134 summary is not complete (status={data.get('status')!r}); no outputs written")
    if data.get("settings_order") != MODEL_ORDER:
        raise ValueError(f"Unexpected E134 model order: {data.get('settings_order')!r}")
    settings = data.get("settings")
    if not isinstance(settings, dict) or set(settings) != set(MODEL_ORDER):
        raise ValueError("E134 summary must contain exactly the six registered settings")
    for model_name in MODEL_ORDER:
        setting = settings[model_name]
        if setting.get("status") != "complete":
            raise ValueError(f"{model_name} is not complete")
        conditions = setting.get("conditions", {})
        for condition in (*CONDITION_ORDER, "native", "recompose"):
            record = conditions.get(condition)
            if not isinstance(record, dict) or record.get("status") != "complete":
                raise ValueError(f"{model_name}/{condition} is not complete")
            metrics = record.get("metrics", {}).get("global", {})
            for metric in ("nll_gap", "kl_teacher_to_student"):
                value = metrics.get(metric)
                if not isinstance(value, dict) or not isinstance(value.get("ci95"), list) or len(value["ci95"]) != 2:
                    raise ValueError(f"Missing file-level 95% CI for {model_name}/{condition}/{metric}")
                nums = [value.get("mean"), *value["ci95"]]
                if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in nums):
                    raise ValueError(f"Non-finite metric for {model_name}/{condition}/{metric}")


def metric_view(setting: dict, condition: str) -> dict:
    global_metrics = setting["conditions"][condition]["metrics"]["global"]
    nll = global_metrics["nll_gap"]
    kl = global_metrics["kl_teacher_to_student"]
    return {
        "delta_nll_nats_per_token": {"mean": nll["mean"], "file_95_ci": nll["ci95"]},
        "kl_native_to_condition_nats_per_token": {"mean": kl["mean"], "file_95_ci": kl["ci95"]},
        "files": global_metrics["files"],
        "sequences": global_metrics["sequences"],
        "tokens": global_metrics["tokens"],
        "file_bootstrap_iterations": global_metrics["file_bootstrap_iterations"],
    }


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    os.replace(partial, path)


def plot(data: dict, output_dir: Path, table: dict) -> tuple[Path, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    settings = data["settings"]
    fig, axes = plt.subplots(2, 6, figsize=(22, 8), sharey="row", squeeze=False)
    ypos = np.arange(len(CONDITION_ORDER))
    for col, model_name in enumerate(MODEL_ORDER):
        setting = settings[model_name]
        title = MODEL_LABELS[model_name]
        axes[0, col].set_title(title, fontsize=10, pad=8)
        for row, metric_key, metric_label in (
            (0, "delta_nll_nats_per_token", "ΔNLL vs native (nats/token; per-model scale)"),
            (1, "kl_native_to_condition_nats_per_token", "KL native→condition (nats/token; per-model scale)"),
        ):
            ax = axes[row, col]
            means, lows, highs = [], [], []
            for condition in CONDITION_ORDER:
                metric = table["models"][col]["conditions"][condition][metric_key]
                means.append(metric["mean"])
                lows.append(metric["file_95_ci"][0])
                highs.append(metric["file_95_ci"][1])
            means = np.asarray(means, dtype=float)
            lows = np.asarray(lows, dtype=float)
            highs = np.asarray(highs, dtype=float)
            for i, condition in enumerate(CONDITION_ORDER):
                color = COLORS[condition]
                ax.hlines(ypos[i], lows[i], highs[i], color=color, linewidth=1.8, zorder=2)
                ax.plot(means[i], ypos[i], marker="o", color=color, markersize=4.6, zorder=3)
            ax.axvline(0.0, color="#555555", linestyle="--", linewidth=0.8, zorder=1)
            ax.grid(axis="x", alpha=0.2, linewidth=0.6)
            low = min(0.0, float(lows.min()))
            high = max(0.0, float(highs.max()))
            span = high - low
            margin = max(span * 0.12, 1e-5)
            ax.set_xlim(low - margin, high + margin)
            ax.set_yticks(ypos, [CONDITION_LABELS[x] for x in CONDITION_ORDER])
            ax.set_ylim(len(CONDITION_ORDER) - 0.5, -0.5)
            ax.tick_params(axis="both", labelsize=8)
            ax.set_xlabel(metric_label, fontsize=8)
            if col == 0:
                ax.set_ylabel("Replacement", fontsize=9)
            else:
                ax.tick_params(axis="y", labelleft=False)
    fig.suptitle("E134 — Native-relative predictive effects", fontsize=14, y=0.985)
    fig.text(
        0.5,
        0.012,
        "Each column is paired to that model's own native reference; x-scales are independent by model. Points and bars show means and file-level 95% CIs. Native/recompose controls are in readout_table.json.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=[0.01, 0.055, 1, 0.94], w_pad=0.8, h_pad=1.0)
    output_dir.mkdir(parents=True, exist_ok=True)
    png = output_dir / "necessity.png"
    pdf = output_dir / "necessity.pdf"
    for path, fmt in ((png, "png"), (pdf, "pdf")):
        partial = path.with_name(path.stem + ".partial" + path.suffix)
        fig.savefig(partial, format=fmt, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        os.replace(partial, path)
    plt.close(fig)
    return png, pdf


def build_table(data: dict, input_path: Path) -> dict:
    models = []
    for name in MODEL_ORDER:
        setting = data["settings"][name]
        models.append({
            "id": name,
            "display_name": MODEL_LABELS[name].replace("\n", " "),
            "model_class": MODEL_KIND[name],
            "native_reference": "This model's own native readout",
            "calibration_gamma_c": setting.get("calibration", {}).get("fit", {}).get("gamma"),
            "conditions": {condition: metric_view(setting, condition) for condition in CONDITION_ORDER},
            "controls": {name: metric_view(setting, name) for name in ("native", "recompose")},
        })
    return {
        "experiment": "E134",
        "input_summary": str(input_path),
        "input_summary_sha256": sha256(input_path),
        "readout": "Within-model native-relative NLL gap and KL; file-level CIs only",
        "kl_direction": "KL(native || condition)",
        "conditions_in_plot": CONDITION_ORDER,
        "models": models,
        "plot_note": "Each model column has its own x-axis scale. Native and recomposition are controls, shown here but not plotted as interventions.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    validate_summary(data)
    table = build_table(data, args.input)
    # Commit the compact table first; plots use exactly this validated table.
    table_path = args.output_dir / "readout_table.json"
    write_json_atomic(table_path, table)
    png, pdf = plot(data, args.output_dir / "figures", table)
    print(json.dumps({"status": "complete", "table": str(table_path), "png": str(png), "pdf": str(pdf)}, indent=2))


if __name__ == "__main__":
    main()
