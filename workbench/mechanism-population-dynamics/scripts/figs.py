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
    ("Layer hosting each role", "universal", "layer profile SI ≈ SD ≈ 0.4–0.7 (9 roles)", "E35/E59"),
    ("Developmental time: previous-token heads", "universal", "corpus 0.01, seed 0.07 (n.s.)", "E54"),
    ("Which head takes each role (9 roles, incl. weight-only)", "seed", "within-layer SI 0.16–0.36 vs SD ≈ 0; data comp. 0", "E35/E45/E59"),
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


def fig_hook():
    """Fig 1: for each seed (rows) and role (columns), how often each head of the role's main layer is the layer's strongest
    head across all 25 corpora of the 1B crossing (E35). Chance = 1/16. Role layer = the population's strongest layer."""
    import glob
    seeds = ["default", "large-aux-2", "large-aux-3"]
    roles = (("M2", "previous-token"), ("M1", "induction"), ("M4", "retrieval"))
    fig, axes = plt.subplots(3, 3, figsize=(11, 5.6), sharex=True, sharey=True)
    for j, (m, name) in enumerate(roles):
        allmaps = {s: [np.array(json.loads(open(f).read())["maps"][m])
                       for f in sorted(glob.glob(str(mc.RESULTS / "e35" / f"*-1B__{s}.json"))) if "step" not in f] for s in seeds}
        layer = int(np.argmax(np.mean([a.max(1) for v in allmaps.values() for a in v], 0)))
        for i, s in enumerate(seeds):
            top = np.bincount([int(a[layer].argmax()) for a in allmaps[s]], minlength=16) / len(allmaps[s])
            ax = axes[i, j]
            ax.bar(range(16), top, color=["#DD8452" if t == top.max() else "#9a9a9a" for t in top])
            ax.axhline(1 / 16, color="k", ls=":", lw=1)
            if i == 0:
                ax.set_title(f"{name} heads (layer {layer})", fontsize=9)
            if j == 0:
                ax.set_ylabel(f"seed {i + 1}\nshare of corpora", fontsize=8)
            if i == 2:
                ax.set_xlabel("head index", fontsize=8)
            ax.set_xticks(range(0, 16, 3))
    fig.suptitle("Which head is the strongest, across 25 pretraining corpora (1B; dotted line = chance)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_hook_1b_prevtoken.png", dpi=160)


def fig_corpus_distance():
    """E60: (a) 1B, 300 recipe pairs: unigram JS vs same-seed within-layer similarity (mean of M1/M2/M4), source-disjoint
    pairs highlighted; (b) Spearman rho by size (all pairs and source-disjoint pairs)."""
    import glob
    from fastsim import within_matrix
    d = json.loads((mc.RESULTS / "e60" / "recipe_distance.json").read_text())
    dist = {tuple(sorted(k.split("|"))): v["js_uni"] for k, v in d["pairs"].items()}
    fs = [f for f in sorted(glob.glob(str(mc.RESULTS / "e35" / "*-1B__*.json"))) if "step" not in f]
    keys = [tuple(f.split("/")[-1][:-5].split("-1B__")) for f in fs]
    J = [json.loads(open(f).read()) for f in fs]
    S = np.nanmean(np.stack([within_matrix([j["maps"][m] for j in J]) for m in ("M1", "M2", "M4")]), 0)
    acc = {}
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            if keys[a][1] == keys[b][1] and keys[a][0] != keys[b][0]:
                acc.setdefault(tuple(sorted((keys[a][0], keys[b][0]))), []).append(S[a, b])
    dc = json.loads((mc.RESULTS / "e60" / "disjoint_control.json").read_text())
    import collections, sys
    sys.path.insert(0, "/home/xiang/mechpop_cache/datadecide")
    import named_data_mixes as ndm
    from e23_corpus_stats import RECIPES, sizes
    sz = sizes()
    W = {}
    for name, key in RECIPES.items():
        g = collections.defaultdict(float)
        for p in ndm.DATA_PATHS[key]:
            g[p.rsplit("/", 1)[0]] += sz.get(p, 0) or 0
        t = sum(g.values())
        W[name] = {k: v / t for k, v in g.items()}
    ov = lambda a, b: sum(min(W[a].get(k, 0), W[b].get(k, 0)) for k in set(W[a]) | set(W[b]))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    pts = [(dist[p], np.mean(v), ov(*p) < 1e-9) for p, v in acc.items() if p in dist]
    for dis, col, lab in ((True, "#4C72B0", "no shared sources"), (False, "#c0c0c0", "shared sources")):
        x = [p[0] for p in pts if p[2] == dis]; y = [p[1] for p in pts if p[2] == dis]
        ax.scatter(x, y, s=10, color=col, label=lab, alpha=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("corpus distance (unigram Jensen–Shannon)")
    ax.set_ylabel("same-seed head-role similarity")
    ax.set_title("1B: 300 corpus pairs × 3 seeds", fontsize=9)
    ax.legend(fontsize=7)
    ax = axes[1]
    order = ["90M", "150M", "300M", "530M", "750M", "1B@7500"]
    params = [97.9e6, 151e6, 320e6, 530e6, 750e6, 1.18e9]
    for m, mk in (("M1", "o"), ("M2", "s"), ("M4", "^")):
        ax.plot(params, [-dc[s][m]["disjoint"][0] for s in order], mk + "-", label=f"{dict(M1='induction', M2='prev-token', M4='retrieval')[m]}")
    ax.set_xscale("log")
    ax.set_xlabel("parameters")
    ax.set_ylabel("−Spearman(distance, inheritance)\n(source-disjoint pairs)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=7)
    ax.set_title("stronger at larger scale (E45 recipe sets)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_corpus_distance_e60.png", dpi=160)


PYTHIA_PARAMS = {"70m": 19e6, "160m": 85e6, "410m": 302e6, "1b": 805e6, "1.4b": 1.21e9, "2.8b": 2.52e9, "6.9b": 6.44e9,
                 "12b": 11.3e9}


def pythia_within():
    """Within-layer similarity of Pythia std vs deduped (same init), mean over M1 / M2 / M4, final checkpoints."""
    from fastsim import within_matrix
    out = {}
    for s in PYTHIA_PARAMS:
        for d in ("e44", "e58"):
            a, b = R / d / f"pythia-{s}-std.json", R / d / f"pythia-{s}-deduped.json"
            if a.exists() and b.exists():
                A, B = json.loads(a.read_text()), json.loads(b.read_text())
                v = [within_matrix([A["maps"][m], B["maps"][m]])[0, 1] for m in ("M1", "M2", "M4")
                     if m != "M1" or (A["M1_max"] > 0.3 and B["M1_max"] > 0.3)]
                out[s] = float(np.mean(v))
    return out


def fig_scale_v2():
    """Fig 4: (a) same-seed vs different-seed within-layer similarity by size (DataDecide, mean of roles) with Pythia
    std-vs-deduped pairs; (b) anatomical seed-identification accuracy by size (E61)."""
    d = json.loads((R / "e45" / "analysis.json").read_text())
    params = {"4M": 3.7e6, "6M": 6e6, "8M": 8.5e6, "10M": 9.9e6, "14M": 14.4e6, "16M": 16e6, "20M": 19.1e6, "60M": 57e6,
              "90M": 97.9e6, "150M": 151e6, "300M": 320e6, "530M": 530e6, "750M": 750e6, "1B@7500": 1.18e9}
    S = [s for s in params if s in d]
    mean_c = lambda s, c: np.mean([d[s][m]["within_layer"][c] for m in ("M1", "M2", "M4") if d[s][m]["decidable"]])
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))
    ax = axes[0]
    ax.plot([params[s] for s in S], [mean_c(s, "SI") for s in S], "o-", color=C["SI"], label="DataDecide: same seed, other corpus")
    ax.plot([params[s] for s in S], [mean_c(s, "SD") for s in S], "o-", color=C["SD"], label="DataDecide: other seed, same corpus")
    pw = pythia_within()
    if pw:
        ax.plot([PYTHIA_PARAMS[s] for s in pw], list(pw.values()), "D--", color="#8172B2", label="Pythia: same seed, Pile vs dedup")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("parameters")
    ax.set_ylabel("which-head similarity (within layer)")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("the slot is inherited, more so at scale", fontsize=9)
    ax = axes[1]
    e = json.loads((R / "e61_seed_id.json").read_text())
    S2 = [s for s in params if s in e]
    ax.plot([params[s] for s in S2], [e[s]["all"]["accuracy"] for s in S2], "o-", color="#C44E52", label="identify the seed from the head layout")
    ax.plot([params[s] for s in S2], [e[s]["all"]["chance"] for s in S2], ":", color="k", label="chance")
    ax.set_xscale("log")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("parameters")
    ax.set_ylabel("accuracy (leave-one-corpus-out)")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.set_title("the anatomy identifies the seed", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_scale_v2.png", dpi=160)


def fig_lockin():
    """Fig 5b: how close the role layout is to its own final layout, vs fraction of training: Pythia 31M/70M/160M
    (E40, previous-token maps, 10 seeds each), controlled S models (E46, parent runs), and the 1B same-seed effect (E37:
    SI - SD relative to its final value). Shaded: the controlled critical period (1-2.5%)."""
    e40 = json.loads((R / "e40" / "analysis.json").read_text())
    e46 = json.loads((R / "e46" / "analysis.json").read_text())["lockin"]
    e37 = json.loads((R / "e37" / "analysis.json").read_text())["steps"]
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for size, col in (("31m", "#9ecae1"), ("70m", "#4292c6"), ("160m", "#08519c")):
        c = e40[size]["S_prev"]["mean_curve"]
        st = [int(s) for s in c if int(s) > 0]
        ax.plot([s / 143000 for s in st], [c[str(s)] for s in st], "-", color=col, label=f"Pythia-{size} (own final)")
    runs = [v for k, v in e46.items() if "M2" in next(iter(v.values()))]
    st = sorted({int(s) for v in runs for s in v})
    ax.plot([s / 10000 for s in st], [np.mean([v[str(s)]["M2"] for v in runs if str(s) in v]) for s in st], "-",
            color="#DD8452", label="controlled S models (own final)")
    fin = {m: e37["final"][m]["SI_minus_SD"] for m in ("M1", "M2", "M4")}
    for s, frac in (("2500", 2500 / 69369), ("10000", 10000 / 69369)):
        ax.scatter([frac], [np.mean([e37[s][m]["SI_minus_SD"] / fin[m] for m in fin])], color="#C44E52", zorder=3,
                   label="1B: same-seed effect / its final value" if s == "2500" else None)
    ax.axvspan(0.01, 0.025, color="#f4cccc", alpha=0.6, lw=0)
    ax.set_xscale("log")
    ax.set_xlabel("fraction of training")
    ax.set_ylabel("similarity to the final layout")
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_lockin.png", dpi=160)


def fig_development_e57():
    """E57: same-seed within-layer similarity (mean of M1/M2/M4) at the earliest shared checkpoint vs the final step,
    per size, plus seed-identification accuracy at both (E61 early)."""
    d = json.loads((R / "e57" / "analysis.json").read_text())
    params = {"10M": 9.9e6, "20M": 19.1e6, "60M": 57e6, "150M": 151e6, "300M": 320e6, "750M": 750e6}
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for size, p in params.items():
        cells = {k: v for k, v in d.items() if k.startswith(size + "@")}
        if not cells:
            continue
        val = lambda v: np.nanmean([v[m]["SI"] for m in ("M1", "M2", "M4") if v.get(m)])
        early = min(cells, key=lambda k: cells[k]["frac"])
        final = max(cells, key=lambda k: cells[k]["frac"])
        ax.plot([p, p], [val(cells[early]), val(cells[final])], "-", color="#bbbbbb", zorder=1)
        ax.scatter([p], [val(cells[early])], color="#55A868", zorder=2, label="earliest checkpoint (3–9% of training)" if size == "10M" else None)
        ax.scatter([p], [val(cells[final])], color="#1b6ca8", marker="s", zorder=2, label="end of training" if size == "10M" else None)
    ax.set_xscale("log")
    ax.set_xlabel("parameters")
    ax.set_ylabel("same-seed which-head similarity")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("the scale effect is present from the earliest checkpoint", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_development_e57.png", dpi=160)


DD_RECIPE = {  # DataDecide Table 2: (batch sequences of 2048 tokens, peak LR)
    "4M": (32, 1.4e-2), "6M": (32, 1.2e-2), "8M": (32, 1.1e-2), "10M": (32, 1.0e-2), "14M": (32, 9.2e-3),
    "16M": (32, 8.9e-3), "20M": (64, 8.4e-3), "60M": (96, 5.8e-3), "90M": (160, 4.9e-3), "150M": (192, 4.2e-3),
    "300M": (320, 3.3e-3), "530M": (448, 2.8e-3), "750M": (576, 2.5e-3), "1B@7500": (704, 2.1e-3)}


def fig_temperature():
    """E62 / E62b + E45: inheritance vs SGD temperature (peak LR / tokens per batch). (a) controlled S models: same-seed
    c4-papers inheritance and order-only similarity at step 2000; (b) DataDecide sizes: same-seed within-layer similarity."""
    e = json.loads((R / "e62_analysis.json").read_text())
    d = json.loads((R / "e45" / "analysis.json").read_text())
    tok = {"bs16": 16 * 512, "bs64": 64 * 512, "bs512": 512 * 512, "lr3e-3": 64 * 512, "lr3e-4": 64 * 512}
    lr = {"bs16": 1e-3, "bs64": 1e-3, "bs512": 1e-3, "lr3e-3": 3e-3, "lr3e-4": 3e-4}
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6), sharex=True)
    ax = axes[0]
    pts = [(lr[k] / tok[k], v["M2"]["inherit_c4_papers"], v["M2"]["order_only"], k) for k, v in e.items()
           if v["M2"]["inherit_c4_papers"] is not None]
    pts.sort()
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=C["SI"], label="same seed, c4 vs papers")
    po = [p for p in pts if p[2] is not None]
    ax.plot([p[0] for p in po], [p[2] for p in po], "s--", color="#55A868", label="same seed & corpus, other batch order")
    for p in pts:
        ax.annotate(p[3], (p[0], p[1]), fontsize=6, xytext=(3, -9), textcoords="offset points")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("SGD temperature: peak LR / tokens per batch")
    ax.set_ylabel("which-head similarity (step 2000)")
    ax.set_title("controlled: lower temperature, the seed decides", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    S = [s for s in DD_RECIPE if s in d]
    x = [DD_RECIPE[s][1] / (DD_RECIPE[s][0] * 2048) for s in S]
    y = [np.mean([d[s][m]["within_layer"]["SI"] for m in ("M1", "M2", "M4") if d[s][m]["decidable"]]) for s in S]
    ax.plot(x, y, "o", color=C["SI"])
    for xi, yi, s in zip(x, y, S):
        ax.annotate(s.replace("@7500", ""), (xi, yi), fontsize=6, xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("SGD temperature: peak LR / tokens per batch")
    ax.set_ylabel("same seed, other corpus")
    ax.set_title("DataDecide: the scaling recipe cools as models grow", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig_temperature_e62.png", dpi=160)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (fig_crossover, fig_scale, fig_benchmarks, fig_flan_scale, fig_determination_map, fig_critical_period, fig_hook, fig_corpus_distance, fig_scale_v2, fig_lockin, fig_development_e57, fig_temperature):
        fn()
    print(sorted(p.name for p in OUT.glob("*.png")))
