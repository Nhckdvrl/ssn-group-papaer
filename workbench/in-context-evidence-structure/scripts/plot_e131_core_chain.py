"""Plot the same three operations across model sizes from verified E131 summaries.

Confirmation only. Missing stages are explicitly pending, never zero-valued.
This is a presentation of existing readouts, without fitting or new inference.
"""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODELS = [("qwen3", "Qwen3-8B"), ("qwen32", "Qwen3-32B"),
          ("llama", "Llama-3.1-8B"), ("llama70", "Llama-3.1-70B")]
STAGES = ["mechanism", "native", "function"]


def get_stat(item, stage):
    if stage == "mechanism":
        return item["analysis"]["contrasts"]["A_formation_B_shared"]["signed_rule_effect"]
    if stage == "native":
        return item["analysis"]["contrasts"]["shared_native_cross_answer_removal"]["rule_signed"]
    return item["full_output"]["contrasts"]["shared_answer_cross_off_minus_normal_native"]["both"]


def main():
    source = ROOT / "results/e131/summary.json"
    summary = json.loads(source.read_text())
    audit = json.loads((ROOT / "results/e131/independent_author_report_review_2026-10-12.json").read_text())
    assert audit["summary_json_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    rows = []
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.65), sharey=True)
    titles = ["Evidence formation", "Native operation", "Real-text source use"]
    labels = ["Formation effect (nats)", "Path removal effect (nats)",
              "Selective − native (pp)"]
    colors = ["#245B88", "#245B88", "#A75A22", "#A75A22"]
    for column, stage in enumerate(STAGES):
        ax = axes[column]
        ax.set_title(titles[column], fontweight="bold", pad=11)
        ax.axvline(0, color="#909090", linewidth=.8, zorder=0)
        ax.set_xlabel(labels[column])
        ax.set_ylim(-.55, 3.55)
        for i, (family, model) in enumerate(MODELS):
            name = f"{family}_confirmation_{stage}"
            y = 3 - i
            if name not in summary["runs"]:
                rows.append({"model": model, "stage": stage, "status": "PENDING",
                             "n_contexts": "", "mean": "", "ci_low": "", "ci_high": ""})
                ax.text(.5, y, "pending", color="#8A8A8A", va="center",
                        transform=ax.get_yaxis_transform())
                continue
            item = summary["runs"][name]
            assert item["run"]["args"]["n"] == 32
            stat = get_stat(item, stage)
            scale = 100 if stage == "function" else 1
            value = stat["mean"] * scale
            lo, hi = np.asarray(stat["ci95"]) * scale
            assert lo <= value <= hi
            ax.errorbar(value, y, xerr=[[value-lo], [hi-value]], fmt="o",
                        color=colors[i], markersize=5.5, capsize=3, linewidth=1.3)
            rows.append({"model": model, "stage": stage, "status": "COMPLETE",
                         "n_contexts": 32, "mean": value, "ci_low": lo, "ci_high": hi})
        ax.grid(axis="y", color="#EBEBEB", linewidth=.7)
        ax.set_axisbelow(True)
        ax.margins(x=.14)
    axes[0].set_yticks(range(4), [label for _, label in reversed(MODELS)])
    complete = sum(row["status"] == "COMPLETE" for row in rows)
    footer = "Within-family and stage matched contexts (n=32); 95% context-bootstrap intervals."
    if complete < 12:
        footer += f"\n{complete}/12 model-stage confirmations complete."
    fig.text(.5, .025, footer, ha="center", color="#555555", fontsize=7)
    fig.tight_layout(rect=(0, .11, 1, 1))
    dest = ROOT / "results/figs"
    dest.mkdir(exist_ok=True)
    base = dest / "fig_cross_size_core_chain"
    for ext in ["png", "pdf"]:
        fig.savefig(base.with_suffix("." + ext), dpi=220, bbox_inches="tight")
    data = ROOT / "results/e131/core_chain_figure_values.csv"
    with data.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "results/e131/core_chain_figure_manifest.json").write_text(json.dumps({
        "source_summary_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "status": "COMPLETE" if complete == 12 else "PARTIAL",
        "confirmation_points_complete": complete, "planned_confirmation_points": 12,
        "selection": "All four fixed models, fresh n32 confirmation, three original core readouts",
        "materials_scope": "Context matching is within each family and stage. Mechanism and function use separately sampled SST contexts; native uses controlled restaurant contexts. Families and stages are not one pooled dataset.",
        "function_scope": "Shared words, full-vocabulary correctness, two-Actor mean targeted-minus-native accuracy; not joint correctness.",
        "limits": "Other channels and restoration backgrounds remain in the full report. "
                  "This is not a controlled scaling law or a new fitted predictor.",
        "data_csv_sha256": hashlib.sha256(data.read_bytes()).hexdigest()
    }, indent=2) + "\n")
    print(f"Rendered {complete}/12 fixed confirmation points.")


if __name__ == "__main__":
    main()
