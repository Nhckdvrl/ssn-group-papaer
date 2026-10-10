"""E77 analysis: per-checkpoint arbitration readouts and developmental decomposition.

Usage: e77_analyze.py            -> results/e77/analysis.json (+ printed tables)
"""
import glob
import json
import re

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e77"
CELLS = ("clean_decl", "clean_qa", "c1_decl", "c1_qa", "c1_Q", "c3_decl", "c3_qa", "agree_decl", "agree_qa",
         "nonce_clean", "nonce_c1_decl", "nonce_c1_qa")
CI = {c: i for i, c in enumerate(CELLS)}
EDGES = np.array([-2, 0, 1, 2, 4, 6, 9, 13])  # global k bins (nats)


def slope(x, y):
    x = x - x.mean()
    return float((x * (y - y.mean())).sum() / (x * x).sum())


def iv_slope(z, x, y):
    z = z - z.mean()
    return float((z * (y - y.mean())).sum() / (z * (x - x.mean())).sum())


def readouts(m):
    c, n0 = m[:, CI["clean_decl"]], m[:, CI["nonce_clean"]]
    k = c - n0
    z = m[:, CI["clean_qa"]] - n0
    out = {"k_mean": float(k.mean()), "known_frac_k2": float((k > 2).mean())}
    for f, ctx, nctx in (("decl", "c1_decl", "nonce_c1_decl"), ("qa", "c1_qa", "nonce_c1_qa")):
        d = m[:, CI[ctx]] - m[:, CI[nctx]]
        b = np.digitize(k, EDGES)
        out[f] = {"gamma": slope(k, d), "gamma_iv": iv_slope(z, k, d), "d_mean": float(d.mean()),
                  "gamma0": slope(n0, m[:, CI[nctx]]),
                  "nonce_ctx_mean": float(m[:, CI[nctx]].mean()),
                  "mem_wins_known": float((m[k > 2, CI[ctx]] > 0).mean()) if (k > 2).sum() else None,
                  "curve": [float(d[b == j].mean()) if (b == j).sum() >= 20 else None for j in range(len(EDGES) + 1)]}
    return out


def curve_fn(k, d):
    b = np.digitize(k, EDGES)
    means = np.array([d[b == j].mean() if (b == j).sum() >= 10 else np.nan for j in range(len(EDGES) + 1)])
    # fill empty bins by linear fit
    a1, a0 = np.polyfit(k, d, 1)
    centers = np.array([k[b == j].mean() if (b == j).sum() else 0 for j in range(len(EDGES) + 1)])
    means = np.where(np.isnan(means), a1 * centers + a0, means)
    return lambda kk: means[np.digitize(kk, EDGES)]


def decompose(m1, m2, ctx="c1_decl", nctx="nonce_c1_decl"):
    k1 = m1[:, CI["clean_decl"]] - m1[:, CI["nonce_clean"]]
    k2 = m2[:, CI["clean_decl"]] - m2[:, CI["nonce_clean"]]
    d1 = m1[:, CI[ctx]] - m1[:, CI[nctx]]
    d2 = m2[:, CI[ctx]] - m2[:, CI[nctx]]
    f1, f2 = curve_fn(k1, d1), curve_fn(k2, d2)
    total = float(d2.mean() - d1.mean())
    along = float((f1(k2) - f1(k1)).mean())
    shift = float((f2(k2) - f1(k2)).mean())
    return {"total": total, "along_curve": along, "curve_change": shift, "resid": total - along - shift}


def load_all():
    R = {}
    for f in sorted(glob.glob(str(OUT / "runs" / "*.npz"))):
        t = f.split("/")[-1][:-4]
        lp = np.load(f)["lp"]
        R[t] = lp[..., 0] - lp[..., 1]
    return R


def series(R):
    """Group checkpoints into developmental series: key -> sorted [(step, tag)]."""
    S = {}
    for t in R:
        fam, model, rev = t.split("__")
        if fam == "pythia":
            S.setdefault(f"pythia/{model}", []).append((int(rev), t))
        elif fam == "dd":
            st, seed = re.match(r"step(\d+)-seed-(.+)", rev).groups()
            S.setdefault(f"dd/{model}/{seed}", []).append((int(st), t))
        elif model == "OLMo-2-0425-1B":
            st = int(re.search(r"tokens(\d+)B", rev).group(1))
            stage = rev.split("-")[0] + ("-" + rev.split("-")[1] if rev.startswith("stage2") else "")
            S.setdefault(f"olmo/{stage}", []).append((st, t))
    return {k: sorted(v) for k, v in S.items()}


def main():
    R = load_all()
    per = {t: readouts(m) for t, m in R.items()}
    S = series(R)
    dev = {}
    for key, v in S.items():
        if len(v) < 2:
            continue
        rows = []
        for (s1, t1), (s2, t2) in zip(v[:-1], v[1:]):
            rows.append({"from": s1, "to": s2, **decompose(R[t1], R[t2])})
        first_last = decompose(R[v[0][1]], R[v[-1][1]])
        dev[key] = {"steps": [s for s, _ in v], "gamma": [per[t]["decl"]["gamma"] for _, t in v],
                    "gamma_iv": [per[t]["decl"]["gamma_iv"] for _, t in v],
                    "gamma_qa": [per[t]["qa"]["gamma"] for _, t in v],
                    "k_mean": [per[t]["k_mean"] for _, t in v], "d_mean": [per[t]["decl"]["d_mean"] for _, t in v],
                    "mem_wins_known": [per[t]["decl"]["mem_wins_known"] for _, t in v],
                    "adjacent": rows, "first_last": first_last}
    (OUT / "analysis.json").write_text(json.dumps({"per_checkpoint": per, "development": dev}, indent=1))
    for key, d in sorted(dev.items()):
        print(f"\n{key}  steps {d['steps']}")
        print("  k_mean ", [round(x, 2) for x in d["k_mean"]])
        print("  gamma  ", [round(x, 2) for x in d["gamma"]])
        print("  gammaIV", [round(x, 2) for x in d["gamma_iv"]])
        print("  memwins", [None if x is None else round(x, 2) for x in d["mem_wins_known"]])
        fl = d["first_last"]
        print(f"  first->last: total {fl['total']:.2f} = along {fl['along_curve']:.2f} + change {fl['curve_change']:.2f} + resid {fl['resid']:.2f}")


if __name__ == "__main__":
    main()
