"""Plot frozen causal reconstructions and the independently validated relation contrast.

Run from the ICES workbench with the verl-clean conda Python. This script reads
completed runs only and fits no coefficients. All five reconstruction predictors
remain reported in the source audits; KV is displayed as the joint-message view.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(path):
    return json.loads(Path(path).read_text())


def reconstruction(directory):
    p = Path(directory)
    assert load(p / "run.json")["args"]["n"] == 32
    rows = [json.loads(line) for line in (p / "behavior.jsonl").read_text().splitlines()]
    assert len(rows) == 32
    z = {k: np.array([r["conditions"][k]["z"] for r in rows])
         for k in rows[0]["conditions"]}
    base = z["aligned_shared_gate"] - z["conflict_shared_gate"]
    target = z["aligned_far_label"] - z["conflict_far_label"] - base
    prediction = z["aligned_answer_kv"] - z["conflict_answer_kv"] - base
    stats = load(p / "reconstruction_audit.json")
    assert stats["fit"] is False and stats["coefficient"] == 1
    return target, prediction, stats["models"]["answer_kv"]["rule_double_contrast"]


def main():
    out = Path("results/figs")
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.25), layout="constrained")
    sources = []
    for ax, directory, title, color in [
        (axes[0], "results/e109/qwen3_confirmation", "a  Qwen3-8B / MHS", "#2166ac"),
        (axes[1], "results/e112/mistral_confirmation", "b  Mistral-7B / MHS", "#00876c"),
    ]:
        target, prediction, stats = reconstruction(directory)
        ax.scatter(target.ravel(), prediction.ravel(), s=12, alpha=.55,
                   color=color, linewidths=0)
        lower = min(target.min(), prediction.min())
        upper = max(target.max(), prediction.max())
        padding = .07 * (upper - lower)
        limits = [lower - padding, upper + padding]
        ax.plot(limits, limits, color="#444444", lw=1, linestyle="--")
        ax.set(xlim=limits, ylim=limits, xlabel="Own-label interface effect (nats)",
               ylabel="Historical-answer KV effect (nats)", title=title)
        ax.set_aspect("equal", adjustable="box")
        ax.text(.04, .96, f"r = {stats['correlation']:.3f}\n"
                f"RMSE = {stats['rmse']:.3f}\n"
                f"Zero-prediction RMSE = {stats['zero_rmse']:.3f}",
                transform=ax.transAxes, va="top", fontsize=9)
        sources.append({"directory": directory, "predictor": "answer_kv",
                        "contrast": "rule_double_contrast", "statistics": stats})

    analysis_path = "results/e111/qwen3_validation/analysis.json"
    data = load(analysis_path)
    contrasts = ["label_cross_minus_label_within",
                 "answer_cross_kv_minus_answer_within_kv"]
    measurements = [data["contrasts"][key]["absolute_effect"] for key in contrasts]
    means = np.array([m["mean"] for m in measurements])
    intervals = np.array([m["ci95"] for m in measurements])
    axes[2].bar([0, 1], means, width=.56, color=["#5b5b5b", "#b35806"])
    axes[2].errorbar([0, 1], means,
                    yerr=np.stack([means - intervals[:, 0], intervals[:, 1] - means]),
                    fmt="none", color="black", capsize=4)
    axes[2].set(xticks=[0, 1], xticklabels=["Own-label KV", "B answer → A label KV"],
                ylabel="Cross-polarity minus within-polarity effect (nats)",
                title="c  Fixed labels / new polarity materials", ylim=(0, 2.8))
    axes[2].tick_params(axis="x", labelsize=8)
    for i, mean in enumerate(means):
        axes[2].text(i, intervals[i, 1] + .06, f"{mean:.3f}", ha="center")
    axes[2].text(.04, .95, "Partial association transfer\n32 new contexts; bootstrap 95% CI",
                 transform=axes[2].transAxes, va="top", fontsize=9)
    fig.suptitle("Evidence formation before source-conditioned query retrieval", fontsize=13)
    for suffix in ["png", "pdf"]:
        fig.savefig(out / f"fig_evidence_formation.{suffix}", dpi=200)
    sources.append({"analysis": analysis_path, "contrasts": contrasts,
                    "measurements": measurements})
    (out / "fig_evidence_formation_data.json").write_text(json.dumps({
        "fit": False, "coefficient": 1, "sources": sources,
        "caption": "All query positions cannot read B. Panels a/b compare the frozen "
        "coefficient-one reconstruction from B historical-answer KV during A-label "
        "formation against the full far-namespace own-label interface, after removing "
        "rule-independent shifts with an aligned-minus-conflict double contrast. Each "
        "point is one query within 32 contexts. Panel c uses fixed output words and "
        "token positions: cross-polarity pairing is contrasted with within-polarity "
        "text permutations on disjoint adjective/template materials. The historical "
        "answer edge transfers part of the complete own-label effect. These are "
        "donor-assisted causal reconstructions, not a donor-free behavior model or "
        "proof of a unique necessary pathway."
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
