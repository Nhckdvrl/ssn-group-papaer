"""Summarize E01 results: per-checkpoint R1/R2/R3 and causal specificity (top-k vs 20 random k-sets).

Writes results/e01/summary.json, results/e01/summary.md and results/e01/e01_trajectory.png.
"""
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
D = WB / "results" / "e01"
REPOS = ["pythia-70m-deduped", "pythia-70m"]
STEPS = [0, 256, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 143000]
KS = [1, 2, 3, 4, 7, 9]
METHODS = ["parent", "zero", "mean"]
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"


def load(repo, step):
    p = D / f"{repo}__step{step}.json"
    return json.loads(p.read_text()) if p.exists() else None


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def ablation_stats(res):
    """Effect = clean - ablated (positive = ablation hurts). Specificity = fraction of random sets beaten."""
    out = {}
    abl = res["ablation"]
    c3, c2 = res["R3_clean"]["drop"]["mean"], res["R2_clean"]["mean"]
    for k in KS:
        for m in METHODS:
            ind = abl[f"k{k}|induction|{m}|0"]
            rnd = [abl[f"k{k}|random|{m}|{j}"] for j in range(20)]
            e3 = c3 - ind["R3_drop"]
            r3 = [c3 - r["R3_drop"] for r in rnd]
            e2 = c2 - ind["R2"]
            r2 = [c2 - r["R2"] for r in rnd]
            # POST-HOC: random sets whose effect >= the induction set, and whether they contain a top-3 R1 head
            top3 = sorted(res["R1"], key=lambda h: -res["R1"][h])[:3]
            beaters = [{"heads": r["heads"], "effect": c3 - r["R3_drop"],
                        "contains_top3_induction": bool(set(r["heads"]) & set(top3))}
                       for r in rnd if c3 - r["R3_drop"] >= e3]
            out[f"k{k}|{m}"] = {
                "POSTHOC_R3_random_sets_not_beaten": beaters,
                "R3_effect": e3, "R3_random_median": float(np.median(r3)), "R3_random_max": float(np.max(r3)),
                "R3_frac_random_beaten": float(np.mean([e3 > x for x in r3])),
                "R3_effect_rel": e3 / c3 if c3 > 0.5 else None,
                "R2_effect": e2, "R2_random_median": float(np.median(r2)), "R2_random_max": float(np.max(r2)),
                "R2_frac_random_beaten": float(np.mean([e2 > x for x in r2])),
            }
    return out


def paired_r2(repo, step):
    """Paired bootstrap CI (over the 2000 Pile sequences) of R2 effect = clean - ablated, induction top-k."""
    import torch

    ps = torch.load(D / f"{repo}__step{step}.perseq.pt")
    rng = np.random.default_rng(0)
    out = {}
    for k in (1, 3, 9):
        for m in METHODS:
            d = (ps["R2_clean"] - ps[f"R2_{k}_{m}"]).numpy().astype(np.float64)
            idx = rng.integers(0, len(d), (1000, len(d)))
            b = d[idx].mean(1)
            out[f"k{k}|{m}"] = [float(d.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
    return out


def main():
    summary = {}
    for repo in REPOS:
        for step in STEPS:
            r = load(repo, step)
            if r is None:
                continue
            heads = list(r["R1"])
            s1 = np.array([r["R1"][h] for h in heads])
            s1rep = np.array([r["R1rep"][h] for h in heads])
            s1b = np.array([r["R1b"][h] for h in heads])
            top = sorted(heads, key=lambda h: -r["R1"][h])
            toprep = sorted(heads, key=lambda h: -r["R1rep"][h])
            row = {
                "top3": [(h, round(r["R1"][h], 3)) for h in top[:3]],
                "R1_max": float(s1.max()), "R1_mean_all": float(s1.mean()),
                "R1b_max": float(s1b.max()), "R1b_top3": sorted(heads, key=lambda h: -r["R1b"][h])[:3],
                "R1_vs_R1b_spearman": spearman(s1, s1b), "R1_seed_top3_same": top[:3] == toprep[:3],
                "R1_seed_top3_overlap": len(set(top[:3]) & set(toprep[:3])),
                "R2_clean": r["R2_clean"], "R3_clean_drop": r["R3_clean"]["drop"],
                "R3_second_half_loss": r["R3_clean"]["second_half_loss"]["mean"],
            }
            if "ablation" in r:
                row["ablation"] = ablation_stats(r)
                row["R2_paired_ci"] = paired_r2(repo, step)
            summary[f"{repo}@{step}"] = row
    (D / "summary.json").write_text(json.dumps(summary, indent=1))

    lines = ["| model@step | top-3 heads (R1) | R1 max | R1b max | R2 clean [95% CI] | R3 drop (nats) | "
             "k=1 R3 effect: zero / mean / parent (frac random beaten) | k=3 same | k=3 R2 effect ind vs rand-median (zero) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for key, row in summary.items():
        a = row.get("ablation", {})

        def cell(k):
            if not a:
                return "—"
            return " / ".join(f"{a[f'k{k}|{m}']['R3_effect']:.2f} ({a[f'k{k}|{m}']['R3_frac_random_beaten']:.2f})"
                              for m in ("zero", "mean", "parent"))
        r2c = row["R2_clean"]
        r2e = (f"{a['k3|zero']['R2_effect']:.3f} vs {a['k3|zero']['R2_random_median']:.3f}" if a else "—")
        lines.append(f"| {key} | {', '.join(h for h, _ in row['top3'])} | {row['R1_max']:.3f} | {row['R1b_max']:.3f} | "
                     f"{r2c['mean']:.3f} [{r2c['ci95'][0]:.3f}, {r2c['ci95'][1]:.3f}] | "
                     f"{row['R3_clean_drop']['mean']:.2f} | {cell(1)} | {cell(3)} | {r2e} |")
    (D / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    plot(summary)


def plot(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#c3c2b7", "axes.grid": True, "grid.color": "#e8e7e2",
                         "grid.linewidth": 0.6})
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.4))
    xs = [s if s > 0 else 64 for s in STEPS]  # step 0 drawn at 64 on the log axis
    for repo, col in zip(REPOS, (BLUE, ORANGE)):
        rows = [summary.get(f"{repo}@{s}") for s in STEPS]
        ok = [(x, r) for x, r in zip(xs, rows) if r]
        if not ok:
            continue
        x = [p[0] for p in ok]
        axes[0].plot(x, [r["R1_max"] for _, r in ok], color=col, lw=2, marker="o", ms=4, label=repo)
        axes[1].plot(x, [r["R3_clean_drop"]["mean"] for _, r in ok], color=col, lw=2, marker="o", ms=4, label=repo)
        axes[2].plot(x, [r["R2_clean"]["mean"] for _, r in ok], color=col, lw=2, marker="o", ms=4, label=repo)
        okab = [(xx, r) for xx, r in ok if "ablation" in r]
        if okab:
            xa = [p[0] for p in okab]
            axes[3].plot(xa, [r["ablation"]["k3|zero"]["R3_effect"] for _, r in okab], color=col, lw=2, marker="o",
                         ms=4, label=f"{repo}: top-3 induction")
            axes[3].plot(xa, [r["ablation"]["k3|zero"]["R3_random_max"] for _, r in okab], color=col, lw=1,
                         ls="--", label=f"{repo}: max of 20 random 3-sets")
    titles = ["R1 max induction score (parent)", "R3 induction loss drop (nats, held-out)",
              "R2 token-loss diff loss@50−loss@500", "Zero-ablate 3 heads: fall in R3 drop"]
    for ax, t in zip(axes, titles):
        ax.set_xscale("log")
        ax.set_title(t, fontsize=9, color="#0b0b0b", loc="left")
        ax.set_xlabel("training step (0 plotted at 64)", color="#52514e")
    axes[0].legend(frameon=False, fontsize=8)
    axes[3].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(D / "e01_trajectory.png", dpi=150)


if __name__ == "__main__":
    main()
