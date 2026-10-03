"""Draft paper figures from finished analyses (results/figs/*.png). Each panel is skipped if its analysis file is missing.
  fig_crossover   E43: index-matched vs permutation/rotation-invariant similarity, SI / SD / DD
  fig_scale       E45 (+E35/E38 at 1B/300M final): within-layer SI vs SD per size
  fig_benchmarks  E51: init vs data variance components per size
  fig_flan_scale  E47 (+E32 at 1B): Flan delta per cue cell per size
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

import mp_common as mc

R = mc.RESULTS
OUT = R / "figs"
C = {"SI": "#1b6ca8", "SD": "#d1495b", "DD": "#8d8d8d"}


def fig_crossover():
    f = R / "e43" / "analysis.json"
    if not f.exists():
        return
    d = json.loads(f.read_text())["metrics"]
    rows = [("resid_index_corr", "residual dims\n(index)"), ("massive_dims_jaccard", "massive dims\n(index)"),
            ("head_out_cka_index", "head outputs\n(index)"), ("neuron_index_corr", "MLP neurons\n(index)"),
            ("resid_cka", "residual\n(CKA)"), ("head_out_cka_best", "head outputs\n(best match)"),
            ("neuron_best_corr", "MLP neurons\n(best match)")]
    fig, ax = plt.subplots(figsize=(9, 3.2))
    x = np.arange(len(rows))
    for j, c in enumerate(("SI", "SD", "DD")):
        ax.bar(x + (j - 1) * 0.27, [d[k][c] for k, _ in rows], 0.27, color=C[c],
               label={"SI": "same init, diff data", "SD": "same data, diff init", "DD": "both differ"}[c])
    ax.axvline(3.5, color="k", lw=0.8, ls=":")
    ax.text(1.5, ax.get_ylim()[1] * 0.95, "where (coordinates)", ha="center", va="top")
    ax.text(5, ax.get_ylim()[1] * 0.95, "what (content)", ha="center", va="top")
    ax.set_xticks(x, [r for _, r in rows], fontsize=8)
    ax.set_ylabel("similarity")
    ax.legend(fontsize=7, frameon=False, loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_crossover_e43.png", dpi=160)


def fig_scale():
    f = R / "e45" / "analysis.json"
    if not f.exists():
        return
    d = json.loads(f.read_text())
    params = {"4M": 3.7e6, "6M": 6e6, "8M": 8.5e6, "10M": 9.9e6, "14M": 14.4e6, "16M": 16e6, "20M": 19.1e6, "60M": 57e6,
              "90M": 97.9e6, "150M": 151e6, "300M": 320e6, "530M": 530e6, "750M": 750e6, "1B@7500": 1.18e9}
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for ax, m, title in zip(axs, ("M1", "M2", "M4"), ("induction", "previous-token", "retrieval")):
        S = [s for s in params if s in d and d[s][m]["decidable"]]
        for c in ("SI", "SD", "DD"):
            ax.plot([params[s] for s in S], [d[s][m]["within_layer"][c] for s in S], "o-", color=C[c], label=c, ms=4)
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:g}M" if v < 1e9 else f"{v / 1e9:g}B"))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_title(title)
        ax.set_xlabel("non-embedding parameters")
        ax.axhline(0, color="k", lw=0.5)
    axs[0].set_ylabel("within-layer Spearman\n(which head in the layer)")
    axs[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_scale_e45.png", dpi=160)


def fig_benchmarks():
    f = R / "e51" / "analysis.json"
    if not f.exists():
        return
    d = json.loads(f.read_text())["summary"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3), sharey=True)
    for ax, m in zip(axs, ("primary_metric", "correct_logit_per_byte")):
        bs = d[m]["by_size"]
        S = list(bs)
        ax.plot(range(len(S)), [bs[s]["median_frac_data"] for s in S], "o-", color="#2a9d8f", label="data")
        ax.plot(range(len(S)), [bs[s]["median_frac_init"] for s in S], "o-", color="#e76f51", label="init")
        ax.set_xticks(range(len(S)), S, rotation=60, fontsize=7)
        ax.set_title(m)
    axs[0].set_ylabel("median variance fraction\n(11 benchmarks)")
    axs[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_benchmarks_e51.png", dpi=160)


def fig_flan_scale():
    f = R / "e47" / "analysis.json"
    if not f.exists():
        return
    d = json.loads(f.read_text())
    cells = (("QA", '"Question: … Answer:"'), ("Q_only", '"Question:"'), ("A_only", '"Answer:"'),
             ("QA_short", '"Q: … A:"'), ("novel", '"Query: … Response:"'))
    S = list(d)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for j, (c, lab) in enumerate(cells):
        y = [d[s]["cells"][c]["delta"] for s in S]
        e = [2 * d[s]["cells"][c]["se"] for s in S]
        ax.errorbar(np.arange(len(S)) + (j - 2) * 0.12, y, e, fmt="o", ms=4, capsize=2, label=lab)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(range(len(S)), S)
    ax.set_ylabel("Flan − no-Flan\ncue effect (nats, ±2SE)")
    ax.legend(fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig_flan_scale_e47.png", dpi=160)


# Determination map (Fig 2). Each row: property, determining factor, key statistic, experiment. Numbers are copied from
# the result files cited in CLAIMS.md (C04 / C05) and the experiment cards.
MAP = [
    ("Algorithm (prev-token → induction composition)", "universal", "75 / 75 models", "E55"),
    ("Layer hosting each role", "universal", "layer profile SI ≈ SD ≈ 0.54–0.83", "E35"),
    ("Developmental time: previous-token heads", "universal", "corpus 0.01, seed 0.07 (n.s.)", "E54"),
    ("Which head within the layer takes the role", "seed", "within-layer SI 0.30 vs SD 0.00; data comp. 0", "E35/E45"),
    ("Residual-stream coordinates / outlier dims", "seed", "0.20 vs 0.00", "E43"),
    ("Representation content (CKA, best match)", "data", "SD ≥ SI ≈ DD", "E43"),
    ("Circuit strength", "data", "data sig. 4/6 metrics; seed comp. ≈ 0", "E35"),
    ("Developmental time: induction heads", "data", "corpus 0.81, seed 0.00", "E54"),
    ("Knowledge-conflict behaviour", "data", "seed main effect 0 / 12", "E36"),
    ("Benchmarks (11 tasks × 14 sizes)", "data", "seed sig. in 4–8% of cells (= FPR)", "E51"),
    ("“Question:” context-trust switch", "data", "+2.4 nats from ~1% Flan data", "C04"),
    ("MLP neuron identity", "none", "0.008", "E43"),
    ("Weight values", "none", "final vs init r = 0.04", "audit"),
]


def fig_determination_map():
    cols = ["universal", "seed", "data", "none"]
    head = ["Universal", "Seed (nature)", "Data (nurture)", "Neither"]
    colour = {"universal": "#4C72B0", "seed": "#DD8452", "data": "#55A868", "none": "#8C8C8C"}
    fig, ax = plt.subplots(figsize=(11.5, 0.42 * len(MAP) + 1.2))
    for i, (prop, who, stat, exp) in enumerate(MAP):
        y = len(MAP) - 1 - i
        if i % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="#f2f2f2", zorder=0)
        ax.text(-0.3, y, prop, ha="right", va="center", fontsize=9)
        for j, c in enumerate(cols):
            ax.scatter(j, y, s=170 if c == who else 25, color=colour[c] if c == who else "#d0d0d0", zorder=2)
        ax.text(len(cols) - 0.4, y, f"{stat}  [{exp}]", ha="left", va="center", fontsize=8, color="#333333")
    ax.set_xticks(range(len(cols)), head, fontsize=9)
    ax.xaxis.tick_top()
    ax.set_xlim(-0.5, len(cols) + 2.6)
    ax.set_ylim(-0.7, len(MAP) - 0.3)
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.subplots_adjust(left=0.36, right=0.99, top=0.9, bottom=0.03)
    fig.savefig(OUT / "fig_determination_map.png", dpi=160)


def fig_critical_period():
    """E46 C/D: within-layer similarity to the unbranched parent after a perturbation at step k (S models, 10k steps)."""
    import re
    d = json.loads((mc.RESULTS / "e46" / "analysis.json").read_text())
    A = d["A"]
    arms = {"switch corpus to code": "tocode", "noise as large as the weights (ε = 1)": "eps1$", "noise ε = 0.1": "eps0.1$"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, m in zip(axes, ("M1", "M2")):
        for lab, pat in arms.items():
            pts = {}
            for k, v in d["D"].items():
                mm = re.search(r"_b(\d+)_", k)
                if mm and re.search(pat, k) and m in v:
                    pts.setdefault(int(mm.group(1)), []).append(v[m][1])
            # k = 0: same init trained on code from scratch (A, code pairs ≈ SI) or perturbed at init (C)
            if pat == "tocode":
                pts[0] = [A[m]["SI"]["within"]]
            else:
                eps = pat.strip("eps$")
                pts[0] = [v[m][1] for k, v in d["C"].items() if k.endswith(f"_eps{eps}") and m in v]
            ks = sorted(pts)
            x = [max(k, 30) for k in ks]
            ax.plot(x, [np.mean(pts[k]) for k in ks], "o-", label=lab)
        rr = [v[m][1] for k, v in d["C"].items() if k.endswith("rerun1") and m in v]
        ax.axhline(np.mean(rr), color="k", ls=":", lw=1, label="rerun (same seed, same data)")
        ax.axvspan(100, 250, color="#f4cccc", alpha=0.6, lw=0)
        ax.set_xscale("log")
        ax.set_xticks([30, 100, 250, 1000, 4000], ["0", "100", "250", "1k", "4k"])
        ax.set_xlabel("branch step k (of 10k)")
        ax.set_title({"M1": "induction heads", "M2": "previous-token heads"}[m])
    axes[0].set_ylabel("within-layer similarity to parent")
    axes[1].legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_critical_period_e46.png", dpi=160)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (fig_crossover, fig_scale, fig_benchmarks, fig_flan_scale, fig_determination_map, fig_critical_period):
        fn()
    print(sorted(p.name for p in OUT.glob("*.png")))
