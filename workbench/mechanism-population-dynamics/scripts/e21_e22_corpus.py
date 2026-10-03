"""E21 (rare-fact divergence, Pythia-410M) and E22 (corpus-level context prior, DataDecide 1B). CPU only.
Protocols: experiments/E21-*.md, experiments/E22-*.md.  Usage: e21_e22_corpus.py e21 | e22
"""
import json
import sys

import numpy as np
from scipy.stats import rankdata, spearmanr

import dd_common as dd
import mp_common as mc

TOKENS = {"pile": 383_299_322_520, "dclm": 4_341_627_197_578, "dolma17": 2_604_642_372_173, "c4": 198_079_554_945}
COUNTS = mc.RESULTS / "corpus_counts"


def load_counts(cat="World Capital"):
    return json.loads((COUNTS / f"{cat.replace(' ', '_')}.json").read_text())


def partial_spearman(x, y, covs):
    """Spearman partial correlation: residualize ranks of x and y on ranks of covariates."""
    R = lambda v: rankdata(v)
    C = np.column_stack([np.ones(len(x))] + [R(c) for c in covs])
    rx = R(x) - C @ np.linalg.lstsq(C, R(x), rcond=None)[0]
    ry = R(y) - C @ np.linalg.lstsq(C, R(y), rcond=None)[0]
    return float(np.corrcoef(rx, ry)[0, 1])


def e21():
    rows = {r["subj"]: r for r in load_counts()}
    runs = ["pythia-410m"] + [f"pythia-410m-seed{i}" for i in range(1, 10)]
    pc = {r: json.loads((mc.RESULTS / "e13" / f"{r}__step143000.json").read_text())["per_country"] for r in runs}
    cs = sorted(set.intersection(*[set(v) for v in pc.values()]) & set(rows))
    M = np.array([[pc[r][c]["margin"] for r in runs] for c in cs])  # [country, run]; lp(true)-lp(dist), memory-ward
    f_phrase = np.log1p([rows[c]["pile"]["phrase_ans"] or 0 for c in cs])
    f_subj = np.log1p([rows[c]["pile"]["subj"] or 0 for c in cs])
    out = {"n_countries": len(cs)}
    mean, D = M.mean(1), M.std(1, ddof=1)
    no4 = [i for i, r in enumerate(runs) if not r.endswith("seed4")]
    D4 = M[:, no4].std(1, ddof=1)
    out["positive_control_rho"] = float(spearmanr(f_phrase, mean)[0])
    out["partial_rho_phrase"] = partial_spearman(D, f_phrase, [mean, np.abs(mean)])
    out["partial_rho_phrase_no_seed4"] = partial_spearman(D4, f_phrase, [M[:, no4].mean(1), np.abs(M[:, no4].mean(1))])
    out["partial_rho_subject_freq"] = partial_spearman(D, f_subj, [mean, np.abs(mean)])
    out["raw_rho_D_phrase"] = float(spearmanr(D, f_phrase)[0])
    out["frac_zero_phrase"] = float(np.mean(f_phrase == 0))
    (mc.RESULTS / "e21").mkdir(exist_ok=True)
    (mc.RESULTS / "e21" / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


DOSE = {"dolma1_7-1B": 0.0, "dclm-baseline-25p-dolma1.7-75p-1B": 0.25, "dclm-baseline-50p-dolma1.7-50p-1B": 0.5,
        "dclm-baseline-75p-dolma1.7-25p-1B": 0.75, "dclm-baseline-1B": 1.0}


def rel_freq(row, recipe):
    if recipe == "c4-1B":
        return row["c4"]["phrase_ans"] / TOKENS["c4"]
    w = DOSE[recipe]
    return w * row["dclm"]["phrase_ans"] / TOKENS["dclm"] + (1 - w) * row["dolma17"]["phrase_ans"] / TOKENS["dolma17"]


def e22(cat="World Capital"):
    rows = load_counts(cat)
    recipes = list(DOSE) + ["c4-1B"]
    data = {(r, s): json.loads((mc.RESULTS / "e20" / f"{r}__{s}.json").read_text()) for r in recipes for s in dd.SEEDS}
    import e18_trait as e18
    R = e18.rows()
    idx = {i: (x["subj"], x["ans"], x["dist"]) for i, x in enumerate(R) if x["cat"] == cat}
    key = {(r["subj"], r["ans"], r["dist"]): r for r in rows}
    items = [i for i, k in idx.items() if k in key and all(key[k][c]["phrase_ans"] is not None for c in TOKENS)]
    out = {"category": cat, "n_items": len(items)}
    for form in e18.FORMS:
        y, item, rec, seed, lf = [], [], [], [], []
        for (r, s), d in data.items():
            m = d["conditions"][f"{cat}|{form}"]["margin_all_items"]
            for i in items:
                y.append(m[str(i)]); item.append(i); rec.append(r); seed.append(s)
                lf.append(np.log1p(rel_freq(key[idx[i]], r) * 1e9))
        y, lf = np.array(y), np.array(lf)
        ui, ur = sorted(set(item)), recipes

        def fit(mask):
            X = [lf[mask]]
            X += [(np.array(item)[mask] == i).astype(float) for i in ui]
            X += [(np.array(rec)[mask] == r).astype(float) for r in ur[1:]]  # baseline = dolma1_7
            b = np.linalg.lstsq(np.column_stack(X), y[mask], rcond=None)[0]
            return b[0], dict(zip(ur, [0.0] + list(b[1 + len(ui):])))

        gamma, beta = fit(np.ones(len(y), bool))
        rng = np.random.default_rng(0)
        boots = []
        for _ in range(200):  # cluster bootstrap: resample seeds within each recipe
            pick = {r: rng.choice(dd.SEEDS, 3) for r in ur}
            ys, ms = [], []
            mask = np.zeros(len(y), bool)
            sel = np.concatenate([np.where((np.array(rec) == r) & (np.array(seed) == s))[0] for r in ur for s in pick[r]])
            yb, lfb = y[sel], lf[sel]
            itb, rcb = np.array(item)[sel], np.array(rec)[sel]
            X = [lfb] + [(itb == i).astype(float) for i in ui] + [(rcb == r).astype(float) for r in ur[1:]]
            b = np.linalg.lstsq(np.column_stack(X), yb, rcond=None)[0]
            boots.append([b[0]] + [0.0] + list(b[1 + len(ui):]))
        B = np.array(boots)
        se = dict(zip(["gamma"] + ur, B.std(0)))
        diff = beta["dclm-baseline-1B"] - beta["dolma1_7-1B"]
        dose_rho = spearmanr([DOSE[r] for r in DOSE], [beta[r] for r in DOSE])[0]
        out[form] = {"gamma": float(gamma), "gamma_ci95": np.percentile(B[:, 0], [2.5, 97.5]).tolist(),
                     "beta": beta, "beta_se": {r: float(se[r]) for r in ur},
                     "dclm_minus_dolma": float(diff), "dclm_minus_dolma_se": float(np.std(B[:, 1 + ur.index("dclm-baseline-1B")] - B[:, 1])),
                     "dose_rho": float(dose_rho)}
    (mc.RESULTS / "e22").mkdir(exist_ok=True)
    (mc.RESULTS / "e22" / f"analysis_{cat.replace(' ', '_')}.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    {"e21": e21, "e22": e22}[sys.argv[1]](*sys.argv[2:])
