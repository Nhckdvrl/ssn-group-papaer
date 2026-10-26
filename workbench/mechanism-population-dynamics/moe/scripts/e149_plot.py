"""All eight E149 source combinations and predeclared loss interactions."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1] / "results/e149"


def interval(ax, x, row, color, marker="o", offset=0):
    low, high = row["input_file_ci95"]
    ax.vlines(x+offset, low, high, color=color, linewidth=1)
    ax.plot(x+offset, row["point"], marker, color=color, markersize=4)


def main():
    d = json.loads((ROOT / "summary.json").read_text())
    if d["status"] != "complete": raise ValueError("Complete eight-cell results required")
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), dpi=150)
    blue, red, gray = "#2166AC", "#B2182B", "#666666"
    names = list(d["cases"])
    for i, name in enumerate(names):
        color = blue if name == "AAA" else red if name == "BBB" else gray
        interval(axes[0], i, d["cases"][name]["nll_minus_AAA"], color)
        for ref, color, offset in (("A", blue, -.1), ("B", red, .1)):
            interval(axes[1], i, d["cases"][name][f"{ref}_to_variant_KL"], color, offset=offset)
    for ax in axes[:2]:
        ax.set_xticks(range(8), names, rotation=45)
        ax.set_xlabel("Sources: backbone / all gates / all banks")
    axes[0].set(title="A  Native and mixed-source prediction", ylabel="NLL minus AAA (nats / token)")
    axes[1].set(title="B  Distributional change from both native corners", ylabel="Full-vocabulary KL (nats / token)")
    for ref, color in (("A", blue), ("B", red)):
        axes[1].plot([], [], "o", color=color, label=f"{ref} to variant")
    axes[1].legend(frameon=False, fontsize=8)
    contrast = [
        ("all_gates_x_all_expert_banks_other_0", "G/E crossed\nbackbone A"),
        ("all_gates_x_all_expert_banks_other_1", "G/E crossed\nbackbone B"),
        ("backbone_x_complete_MoE", "Backbone/MoE\ncrossed"),
    ]
    for i, (key, label) in enumerate(contrast):
        row = d["interactions"][key]
        low, high = row["input_file_ci95"]
        # Algebraic re-expression of the preregistered four-cell difference:
        # mean(crossed pairs) - mean(coherent pairs) = -interaction / 2.
        transformed = {"point": -row["point"]/2, "input_file_ci95": [-high/2, -low/2]}
        interval(axes[2], i, transformed, gray)
    axes[2].set_xticks(range(3), [x[1] for x in contrast])
    axes[2].set(title="C  Pairing cost from four-cell contrasts", ylabel="Crossed minus paired NLL (nats / token)")
    for ax in axes:
        ax.axhline(0, color="#BBBBBB", linewidth=.7)
        ax.grid(axis="y", alpha=.15)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
    fig.tight_layout(rect=(0, .14, 1, 1), w_pad=2)
    fig.text(.5, .025, "One common pretrained parent, two order-history endpoints; no extra training or alignment.\n"
             "Intervals resample 20 input-file clusters, not training seeds. All eight legal networks are retained.",
             ha="center", color=gray, fontsize=8)
    out = ROOT / "figures"; out.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"): fig.savefig(out / ("native_system_source_cube."+suffix), bbox_inches="tight")
    print(out / "native_system_source_cube.png")


if __name__ == "__main__": main()
