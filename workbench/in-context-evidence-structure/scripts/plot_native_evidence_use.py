"""Display completed, frozen E113/E114 evidence. No parameters are fitted.

The native crossing factors are cached states at A/B positions, not independent
global writer/reader modules. Data and interval provenance accompany each figure.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read(path):
    return json.loads(Path(path).read_text())


def completed(path):
    p = Path(path)
    run = read(p / "run.json")
    assert run["args"]["n"] == 32
    rows = [json.loads(line) for line in (p / "behavior.jsonl").read_text().splitlines()]
    assert len(rows) == 32
    return read(p / "analysis.json"), rows


def main():
    out = Path("results/figs")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(10.3, 8.1), layout="constrained")
    provenance = []
    for col, (directory, label) in enumerate([
        ("results/e114/qwen3_confirmation", "Qwen3-8B"),
        ("results/e114/mistral_confirmation", "Mistral-7B-v0.3"),
    ]):
        data, rows = completed(directory)
        ax = axes[0, col]
        for r, color, style in [(0, "#2166ac", "o-"), (1, "#b35806", "s-")]:
            points = [data["rule_dependence"][f"f{f}r{r}"]["signed"] for f in [0, 1]]
            mean = np.array([p["mean"] for p in points])
            ci = np.array([p["ci95"] for p in points])
            ax.errorbar([0, 1], mean, yerr=np.stack([mean-ci[:, 0], ci[:, 1]-mean]),
                        fmt=style, color=color, capsize=3,
                        label=f"B cached environment: {'shared' if r == 0 else 'far'}")
        interaction = data["contrasts"]["stage_interaction"]["signed_rule_effect"]
        ax.set(xticks=[0, 1], xticklabels=["shared", "far"],
               xlabel="Namespace used to form A-position states",
               ylabel="Signed dependence on B's pairing (nats)",
               title=f"{'a' if col == 0 else 'b'}  Native full-source query / {label}")
        ax.axhline(0, lw=.7, color="#999999")
        ax.legend(fontsize=8, loc="upper right")
        ax.text(.03, .10, f"Signed interaction: {interaction['mean']:.3f}\n"
                f"95% CI [{interaction['ci95'][0]:.3f}, {interaction['ci95'][1]:.3f}]",
                transform=ax.transAxes, fontsize=9, va="bottom")
        z = {k: np.array([row["conditions"][k]["z"] for row in rows])
             for k in rows[0]["conditions"]}
        ax = axes[1, col]
        correlations = []
        for r, color in [(0, "#2166ac"), (1, "#b35806")]:
            base = z[f"cross_f0r{r}"] - z[f"origin_f0r{r}"]
            target = z[f"cross_label_r{r}"] - z[f"origin_label_r{r}"] - base
            prediction = z[f"cross_edge_kv_r{r}"] - z[f"origin_edge_kv_r{r}"] - base
            ax.scatter(target.ravel(), prediction.ravel(), s=12, alpha=.48,
                       color=color, linewidths=0, label=f"B {'shared' if r == 0 else 'far'}")
            correlations.append(data["reconstruction"][f"label_interface_B{r}_kv"]["rule_double_contrast"])
        limits = [min(*ax.get_xlim(), *ax.get_ylim()), max(*ax.get_xlim(), *ax.get_ylim())]
        ax.plot(limits, limits, linestyle="--", color="#444444", lw=1)
        ax.set(xlim=limits, ylim=limits, xlabel="Own-label namespace effect (nats)",
               ylabel="Historical-answer KV effect (nats)",
               title=f"{'c' if col == 0 else 'd'}  Frozen native reconstruction / {label}")
        ax.text(.04, .96, f"r (B shared / far): {correlations[0]['correlation']:.3f} / "
                f"{correlations[1]['correlation']:.3f}\nCoefficient = 1; no fit",
                transform=ax.transAxes, va="top", fontsize=9)
        provenance.append({"directory": directory, "signed_interaction": interaction,
                           "native_label_reconstruction": correlations})
    fig.suptitle("Evidence formation contributes to native source-conditioned prediction", fontsize=13)
    for suffix in ["png", "pdf"]:
        fig.savefig(out / f"fig_native_evidence_use.{suffix}", dpi=190)
    (out / "fig_native_evidence_use_data.json").write_text(json.dumps({
        "sources": provenance,
        "caption": "Each model has 32 independently sampled validation contexts. "
        "Top: the signed B-rule contrast changes when A-position caches are drawn "
        "from shared/far namespace formation, under both fixed B cache environments. "
        "Nonparallel lines are supported by a paired signed interaction, rather than "
        "an absolute-value interaction alone. Bottom: donor-assisted coefficient-one "
        "historical-answer KV reconstruction of the native A-label intervention. "
        "All query positions may read all sources. Factors are token-position cache "
        "groups; both groups are contextualized and the live reader can evolve. "
        "Mistral uses the explicitly recorded block-tokenized stream with its extra "
        "SentencePiece separator spaces, not literal whole-string tokenization."
    }, indent=2) + "\n")

    fig, ax = plt.subplots(figsize=(7.3, 4.5), layout="constrained")
    measurements = []
    for j, (label, gated, native) in enumerate([
        ("Qwen3-8B", "results/e111/qwen3_validation", "results/e114/qwen3_confirmation"),
        ("Mistral-7B-v0.3", "results/e113/mistral_confirmation", "results/e114/mistral_confirmation"),
    ]):
        gate_data, _ = completed(gated); native_data, _ = completed(native)
        values = [gate_data["contrasts"]["answer_cross_kv_minus_answer_within_kv"]["absolute_effect"],
                  native_data["relation"]["answer_native"]["absolute_effect"]]
        measurements.append({"model": label, "gated_run": gated, "native_run": native,
                             "gated": values[0], "native": values[1]})
        for i, (value, color, scope) in enumerate(zip(values, ["#2166ac", "#00876c"],
                                                    ["A-only query", "Native full-source query"])):
            x = j + (i-.5)*.32
            ax.bar(x, value["mean"], width=.29, color=color, label=scope if j == 0 else None)
            lo, hi = value["ci95"]
            ax.errorbar(x, value["mean"], yerr=[[value["mean"]-lo], [hi-value["mean"]]],
                        fmt="none", color="black", capsize=3)
    ax.set(xticks=[0, 1], xticklabels=["Qwen3-8B", "Mistral-7B-v0.3"],
           ylabel="Cross-polarity minus within-polarity effect (nats)",
           title="Partial association transfer through historical-answer messages", ylim=(0, 1.04))
    ax.legend(loc="upper right", fontsize=9)
    ax.text(.03, .95, "Fixed label words and positions\n32 validation contexts per run; 95% CI",
            transform=ax.transAxes, va="top", fontsize=9)
    for suffix in ["png", "pdf"]:
        fig.savefig(out / f"fig_relation_transfer_interfaces.{suffix}", dpi=190)
    (out / "fig_relation_transfer_interfaces_data.json").write_text(json.dumps({
        "measurements": measurements,
        "caption": "Association contrast through the B-answer KV edge during A-label "
        "formation, relative to same-polarity text permutations. All output words, "
        "positions and input multisets are fixed within each experiment. Different "
        "runs use independently sampled contexts: bar-height differences between "
        "gated and native interfaces are descriptive, not a matched causal gate "
        "effect. Positive transfer does not explain the complete label effect, prove "
        "an abstract program, or make K/V interventions independent modules."
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
