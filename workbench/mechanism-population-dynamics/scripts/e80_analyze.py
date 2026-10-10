"""E80 analysis: format decomposition (O1), Flan effect, nonce validity, fixed-k curves (O2).

Usage: e80_analyze.py   -> results/e80/analysis.json + printed decision readouts
"""
import glob
import json

import numpy as np

import mp_common as mc
from e80_audit import CELLS, ITEMS, NV

OUT = mc.RESULTS / "e80"
CI = {c: i for i, c in enumerate(CELLS)}
READ = {"full": 0, "first": 1}
SEEDS = ("default", "large-aux-2", "large-aux-3")


def load():
    R = {}
    for f in sorted(glob.glob(str(OUT / "runs" / "*.npz"))):
        lp = np.load(f)["lp"]  # [item, cell, cand, read]
        R[f.split("/")[-1][:-4]] = lp[:, :, 0, :] - lp[:, :, 1, :]  # margin ans - dist, [item, cell, read]
    return R


def ds_masks():
    I = json.loads(ITEMS.read_text())
    ds = np.array([x["ds"] for x in I])
    return {"popqa": ds == "popqa", "paraconflict": ds == "paraconflict"}


def fmt(m, mask, r):
    """Format decomposition for one model: returns F_total, F_nonce (mean over 3 nonces), F_spec, per-nonce F."""
    x = m[mask, :, r]
    ft = float(((-x[:, CI["c1_qa"]]) - (-x[:, CI["c1_decl"]])).mean())
    fn = [float(((-x[:, CI[f"n{v}_c1_qa"]]) - (-x[:, CI[f"n{v}_c1_decl"]])).mean()) for v in NV]
    k = x[:, CI["clean_decl"]] - np.mean([x[:, CI[f"n{v}_clean"]] for v in NV], 0)
    low = np.abs(k) < 0.5
    f_low = float(((-x[low, CI["c1_qa"]]) - (-x[low, CI["c1_decl"]])).mean()) if low.sum() >= 30 else None
    return {"F_total": ft, "F_nonce": float(np.mean(fn)), "F_spec": ft - float(np.mean(fn)), "F_nonce_each": fn,
            "F_real_lowk": f_low, "n_lowk": int(low.sum())}


def flan_effect(R, step=69369):
    out = {}
    M = ds_masks()
    for dsn, mask in M.items():
        for rn, r in READ.items():
            vals = {}
            for rec in ("dolma1_7-1B", "dolma1_7-no-flan-1B"):
                rows = [fmt(R[t], mask, r) for s in SEEDS if (t := f"dd__DataDecide-{rec}__step{step}-seed-{s}") in R]
                vals[rec] = rows
            if min(len(v) for v in vals.values()) < 3:
                continue
            res = {}
            for key in ("F_total", "F_nonce", "F_spec"):
                a = np.array([x[key] for x in vals["dolma1_7-1B"]])
                b = np.array([x[key] for x in vals["dolma1_7-no-flan-1B"]])
                se = float(np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 3))
                res[key] = {"flan": float(a.mean()), "noflan": float(b.mean()), "delta": float(a.mean() - b.mean()), "se": se}
            # nonce validity: spread of Flan delta across the three nonce variants
            dn = [np.mean([x["F_nonce_each"][i] for x in vals["dolma1_7-1B"]]) -
                  np.mean([x["F_nonce_each"][i] for x in vals["dolma1_7-no-flan-1B"]]) for i in range(3)]
            res["delta_F_nonce_by_variant"] = [float(v) for v in dn]
            res["lowk_real_F"] = {"flan": [x["F_real_lowk"] for x in vals["dolma1_7-1B"]],
                                  "noflan": [x["F_real_lowk"] for x in vals["dolma1_7-no-flan-1B"]]}
            dt, dnn, ds_ = res["F_total"]["delta"], res["F_nonce"]["delta"], res["F_spec"]
            res["verdict"] = {"ratio_nonce": dnn / dt if dt else None,
                              "total_sig": dt > 2 * res["F_total"]["se"],
                              "spec_small": abs(ds_["delta"]) < 2 * ds_["se"],
                              "O1_holds_here": bool(dt > 2 * res["F_total"]["se"] and dt and dnn / dt >= 0.7
                                                   and abs(ds_["delta"]) < 2 * ds_["se"])}
            out[f"{dsn}/{rn}"] = res
    return out


def olmo_midtrain(R):
    out = {}
    base = "hf__OLMo-2-0425-1B__stage1-step1907359-tokens4001B"
    ends = [f"hf__OLMo-2-0425-1B__stage2-ingredient{i}-step23852-tokens51B" for i in (1, 2, 3)]
    if base not in R or not all(e in R for e in ends):
        return out
    for dsn, mask in ds_masks().items():
        for rn, r in READ.items():
            b = fmt(R[base], mask, r)
            d = [{k: fmt(R[e], mask, r)[k] - b[k] for k in ("F_total", "F_nonce", "F_spec")} for e in ends]
            out[f"{dsn}/{rn}"] = {k: [round(x[k], 3) for x in d] for k in ("F_total", "F_nonce", "F_spec")}
    return out


def describe(R):
    out = {}
    for t, m in R.items():
        out[t] = {f"{dsn}/{rn}": fmt(m, mask, r) for dsn, mask in ds_masks().items() for rn, r in READ.items()}
    return out


def main():
    R = load()
    res = {"n_runs": len(R), "flan_final": flan_effect(R), "olmo_midtrain": olmo_midtrain(R), "per_model": describe(R)}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    print("runs", len(R))
    for k, v in res["flan_final"].items():
        print(f"\nFlan - noFlan finals  [{k}]")
        for key in ("F_total", "F_nonce", "F_spec"):
            x = v[key]
            print(f"  {key:8s} flan {x['flan']:6.2f} noflan {x['noflan']:6.2f}  delta {x['delta']:+.2f}  SE {x['se']:.2f}")
        print("  delta F_nonce by nonce variant", [round(a, 2) for a in v["delta_F_nonce_by_variant"]])
        print("  verdict", v["verdict"])
    for k, v in res["olmo_midtrain"].items():
        print(f"OLMo stage2 - stage1 [{k}]", v)


if __name__ == "__main__":
    main()
