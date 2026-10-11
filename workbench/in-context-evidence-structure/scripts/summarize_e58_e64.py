"""Compact, source-linked E58-E64 measurements and scientific figures."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read(relative):
    return json.loads((RESULTS / relative).read_text())


def main():
    summary = {"scope": "Fixed model/checkpoint and context-bootstrap intervals; not uncertainty over model or training seeds.",
               "source_rule": "Synthetic opposite rules over real comments, not actual individual annotator ground truth.",
               "e64": {}, "runtime": {}}
    pairs = [("Qwen3 / synthetic discovery", "qwen3_synthetic_discovery"),
             ("Qwen3 / synthetic confirmation", "qwen3_synthetic_confirmation"),
             ("Qwen3 / real-text discovery", "qwen3_real_discovery"),
             ("Qwen3 / real-text confirmation", "qwen3_real_confirmation"),
             ("Mistral / synthetic replication", "mistral_synthetic_discovery")]
    for label, stem in pairs:
        f = read(f"e64/{stem}_final/analysis.json")
        a = read(f"e64/{stem}_all/analysis.json")
        summary["e64"][stem] = {
            "label": label, "source_effect_nats": f["sourceK_effect"],
            "final_label_remaining": f["conditions"]["freeze_label"]["remaining_fraction"],
            "all_query_label_remaining": a["conditions"]["freeze_label"]["remaining_fraction"],
            "paired_scope_difference": f["paired_all_query"]["freeze_label"]["final_minus_all_remaining_fraction"],
            "final_name_remaining": f["conditions"]["freeze_name"]["remaining_fraction"],
            "all_query_name_remaining": a["conditions"]["freeze_name"]["remaining_fraction"],
            "sources": [f"results/e64/{stem}_{s}/analysis.json" for s in ("final", "all")]}
    total = 0
    invalid = 0
    for e in range(58, 65):
        runs = list((RESULTS / f"e{e}").glob("*/run.json"))
        valid = [p for p in runs if "invalid" not in p.parent.name]
        seconds = sum(json.loads(p.read_text())["seconds"] for p in valid)
        bad = sum(json.loads(p.read_text())["seconds"] for p in runs if "invalid" in p.parent.name)
        summary["runtime"][f"e{e}"] = {"successful_process_wall_gpu_hours": seconds / 3600,
                                         "invalid_process_wall_gpu_hours": bad / 3600,
                                         "completed_runs": len(valid)}
        total += seconds
        invalid += bad
    summary["runtime"]["total_successful_process_wall_gpu_hours"] = total / 3600
    summary["runtime"]["total_invalid_process_wall_gpu_hours"] = invalid / 3600
    summary["runtime"]["definition"] = "Sum of single-GPU process timers, including model load/data prep; excluding model staging, startup failures without run.json, and CPU analysis. Not integrated GPU utilization."
    (RESULTS / "e58_e64_summary.json").write_text(json.dumps(summary, indent=2))
    # Scope comparison: both runs use exactly the same native baseline and source-K perturbation.
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    y = np.arange(len(pairs))
    colors = ["#ca6b30", "#26729d"]
    for off, key, color, legend in [(-0.13, "final_label_remaining", colors[0], "Freeze label messages at final query token"),
                                    (0.13, "all_query_label_remaining", colors[1], "Freeze label messages at all query tokens")]:
        stats = [summary["e64"][stem][key] for _, stem in pairs]
        means = np.array([s["mean"] for s in stats])
        ci = np.array([s["ci95"] for s in stats])
        ax.errorbar(means, y + off, xerr=np.stack([means - ci[:, 0], ci[:, 1] - means]),
                    fmt="o", color=color, capsize=3, label=legend)
    ax.axvline(0, color="#333333", lw=0.8)
    ax.axvline(1, color="#aaaaaa", lw=0.8, ls="--")
    ax.set_yticks(y, [s for s, _ in pairs])
    ax.invert_yaxis()
    ax.set_xlim(-0.08, 1.06)
    ax.set_xlabel("Remaining source-K effect / original source-K effect")
    ax.set_title("Label-message mediation depends on model and query scope")
    ax.grid(axis="x", alpha=0.2)
    ax.legend(loc="lower right", fontsize=8)
    fig.text(0.02, 0.015, "95% context-bootstrap CIs. Effect ratios are intervention-specific, not additive causal shares.", fontsize=8)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    figs = RESULTS / "figs"
    figs.mkdir(exist_ok=True)
    fig.savefig(figs / "e64_query_scope.png", dpi=180)
    fig.savefig(figs / "e64_query_scope.pdf")
    plt.close(fig)
    # Crossed interventions show why value-only payload is an incomplete explanation.
    names = ["base", "K", "V", "K+V", "YKV", "K+YKV"]
    fig, axes = plt.subplots(1, 2, figsize=(9.3, 4), sharex=True)
    for ax, stem, label in zip(axes, ["qwen3_synthetic_confirmation", "qwen3_real_confirmation"],
                                ["Independent synthetic task", "Independent real-text pool"]):
        d = read(f"e61/{stem}/analysis.json")
        stats = [d["conditions"][n]["correct_margin"] for n in names]
        means = np.array([s["mean"] for s in stats])
        ci = np.array([s["ci95"] for s in stats])
        ax.bar(names, means, color=["#555555", "#ca6b30", "#ca6b30", "#7fa2b8", "#ca6b30", "#26729d"])
        ax.errorbar(names, means, yerr=np.stack([means - ci[:, 0], ci[:, 1] - means]), fmt="none", ecolor="#222", capsize=3)
        ax.axhline(0, color="#333", lw=0.8)
        ax.set_title(label)
        ax.set_ylabel("Base-correct label margin (nats)")
    fig.text(0.02, 0.015, "K: source-name keys swapped; V/YKV: label-anchor values / keys and values flipped. 95% context CIs.", fontsize=8)
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(figs / "e61_crossed_cache.png", dpi=180)
    fig.savefig(figs / "e61_crossed_cache.pdf")


if __name__ == "__main__":
    main()
