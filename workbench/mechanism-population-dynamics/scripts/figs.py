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


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (fig_crossover, fig_scale, fig_benchmarks, fig_flan_scale):
        fn()
    print(sorted(p.name for p in OUT.glob("*.png")))
