#!/usr/bin/env python3
"""L15 E01/E02 analysis.

Reads results/<tag>/<model>/raw.jsonl, applies the preregistered parsing and the
preregistered KNI definition, and writes summary.json / summary.md.
"""
from __future__ import annotations

import argparse, collections, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scoring import (KNI_OBS_TOL, KNI_POST_TOL, cluster_bootstrap_ci,
                     monotonicity_violations, parse_numeric, parse_yesno, spearman)
from stimuli import SENSITIVITIES


def load(tag: str, model: str):
    path = ROOT / "results" / tag / model / "raw.jsonl"
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def score_rows(rows):
    for r in rows:
        if r["condition"] == "P3_DECIDE":
            r["pred"] = parse_yesno(r["raw"])
            r["valid"] = r["pred"] is not None
            r["correct"] = (r["pred"] == r["gold"]) if r["valid"] else None
        else:
            r["pred"] = parse_numeric(r["raw"])
            r["valid"] = r["pred"] is not None
            r["err"] = abs(r["pred"] - r["gold"]) if r["valid"] else None
    return rows


def mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(xs)) if xs else float("nan")


def analyse(rows, mode):
    rows = [r for r in rows if r["mode"] == mode]
    by_cond = collections.defaultdict(list)
    for r in rows:
        by_cond[r["condition"]].append(r)

    out = {"mode": mode, "coverage": {}, "mae": {}, "n": {}}
    for cond, rs in sorted(by_cond.items()):
        out["n"][cond] = len(rs)
        out["coverage"][cond] = round(sum(r["valid"] for r in rs) / len(rs), 4)
        if cond != "P3_DECIDE":
            out["mae"][cond] = round(mean([r.get("err") for r in rs]), 4)

    # --- detectability response: per (scenario, prior, wording) curve over s -------
    curves = collections.defaultdict(dict)
    for r in by_cond["P2_NULL"]:
        if r["valid"]:
            curves[(r["scenario"], r["p"], r["wording"])][r["s"]] = r["pred"]
    rho, comp, viol_bad, viol_tot, slopes, clusters = [], [], 0, 0, [], []
    gold_range = {}
    for p in sorted({k[1] for k in curves}):
        from stimuli import posterior_null
        gold_range[p] = posterior_null(p, min(SENSITIVITIES)) - posterior_null(p, max(SENSITIVITIES))
    for (sc, p, w), d in curves.items():
        ss = sorted(d)
        if len(ss) < 4:
            continue
        preds = [d[s] for s in ss]
        from stimuli import posterior_null
        golds = [posterior_null(p, s) for s in ss]
        rho.append(spearman(preds, golds))
        b, t = monotonicity_violations(preds)
        viol_bad += b; viol_tot += t
        rng = preds[0] - preds[-1]
        slopes.append(rng)
        comp.append(rng / gold_range[p] if gold_range[p] > 0 else float("nan"))
        clusters.append(sc)
    out["detectability"] = {
        "n_curves": len(rho),
        "mean_spearman_vs_gold": round(mean(rho), 4),
        "spearman_ci95_scenario_bootstrap": [round(x, 4) for x in cluster_bootstrap_ci(rho, clusters)],
        "mean_observed_range": round(mean(slopes), 4),
        "mean_compression_ratio": round(mean(comp), 4),
        "compression_ci95_scenario_bootstrap": [round(x, 4) for x in cluster_bootstrap_ci(comp, clusters)],
        "adjacent_monotonicity_violations": f"{viol_bad}/{viol_tot}",
    }

    # --- KNI: same item, same wording, same mode ----------------------------------
    p1 = {(r["item_id"], r["wording"]): r for r in by_cond["P1_NULL"] if r["valid"]}
    p2 = {(r["item_id"], r["wording"]): r for r in by_cond["P2_NULL"] if r["valid"]}
    keys = sorted(set(p1) & set(p2))
    known = [k for k in keys if p1[k]["err"] <= KNI_OBS_TOL]
    kni = [k for k in known if p2[k]["err"] >= KNI_POST_TOL]
    kni_flags = [1.0 if k in set(kni) else 0.0 for k in known]
    out["kni"] = {
        "n_paired": len(keys),
        "obs_known_rate": round(len(known) / len(keys), 4) if keys else float("nan"),
        "kni_rate": round(len(kni) / len(known), 4) if known else float("nan"),
        "kni_ci95_scenario_bootstrap": [
            round(x, 4) for x in cluster_bootstrap_ci(kni_flags, [k[0].split("|")[0] for k in known])
        ],
        "mean_err_obs": round(mean([p1[k]["err"] for k in keys]), 4),
        "mean_err_post": round(mean([p2[k]["err"] for k in keys]), 4),
    }

    # --- frame split on the primary condition -------------------------------------
    frames = collections.defaultdict(list)
    for r in by_cond["P2_NULL"]:
        frames[r["frame"]].append(r)
    out["p2_mae_by_frame"] = {f: round(mean([r.get("err") for r in rs]), 4)
                              for f, rs in sorted(frames.items())}
    kni_by_frame = collections.defaultdict(list)
    for k in known:
        kni_by_frame[p2[k]["frame"]].append(1.0 if k in set(kni) else 0.0)
    out["kni_rate_by_frame"] = {f: round(mean(v), 4) for f, v in sorted(kni_by_frame.items())}

    # --- controls -----------------------------------------------------------------
    arith = {(r["p"], r["s"]): r for r in by_cond["P2_ARITH"] if r["valid"]}
    framed = collections.defaultdict(list)
    for r in by_cond["P2_NULL"]:
        if r["valid"]:
            framed[(r["p"], r["s"])].append(r["err"])
    paired = [(arith[k]["err"], mean(framed[k])) for k in sorted(arith) if k in framed]
    out["controls"] = {
        "arith_mae": round(mean([a for a, _ in paired]), 4),
        "framed_mae_same_cells": round(mean([f for _, f in paired]), 4),
        "framed_minus_arith": round(mean([f - a for a, f in paired]), 4),
        "handed_mae": out["mae"].get("P2_HANDED"),
        "null_mae": out["mae"].get("P2_NULL"),
        "positive_control_mae": out["mae"].get("P2_POS"),
        "prior_only_mae": out["mae"].get("P0_PRIOR"),
    }

    # --- P3 decision ---------------------------------------------------------------
    d3 = [r for r in by_cond["P3_DECIDE"] if r["valid"]]
    out["decision"] = {
        "n": len(d3),
        "accuracy_vs_gold": round(mean([1.0 if r["correct"] else 0.0 for r in d3]), 4),
    }
    # consistency with the model's own stated posterior
    own = 0; tot = 0
    for r in d3:
        m = p2.get((r["item_id"], r["wording"]))
        if m:
            tot += 1
            own += 1.0 if ((m["pred"] > r["threshold"]) == (r["pred"] == "yes")) else 0.0
    out["decision"]["consistency_with_own_posterior"] = round(own / tot, 4) if tot else float("nan")
    return out


def render(summary) -> str:
    L = [f"# L15 pilot summary — {summary['model']} ({summary['tag']})", ""]
    L.append(f"- cells: {summary['n_cells']}  |  raw: `results/{summary['tag']}/{summary['model']}/raw.jsonl`")
    L.append("")
    for m in summary["modes"]:
        L.append(f"## mode = {m['mode']}")
        L.append("")
        L.append("| condition | n | coverage | MAE |")
        L.append("|---|---:|---:|---:|")
        for c in sorted(m["n"]):
            L.append(f"| {c} | {m['n'][c]} | {m['coverage'][c]:.3f} | "
                     f"{m['mae'].get(c, float('nan')):.4f} |")
        L.append("")
        d = m["detectability"]
        L.append(f"**Detectability response (P2_NULL):** mean Spearman vs gold "
                 f"{d['mean_spearman_vs_gold']:.3f} "
                 f"(95% CI {d['spearman_ci95_scenario_bootstrap']}), "
                 f"compression ratio {d['mean_compression_ratio']:.3f} "
                 f"(95% CI {d['compression_ci95_scenario_bootstrap']}), "
                 f"monotonicity violations {d['adjacent_monotonicity_violations']}.")
        k = m["kni"]
        L.append("")
        L.append(f"**KNI:** obs-known rate {k['obs_known_rate']:.3f}, "
                 f"KNI rate {k['kni_rate']:.3f} "
                 f"(95% CI {k['kni_ci95_scenario_bootstrap']}), "
                 f"mean Err_obs {k['mean_err_obs']:.4f}, mean Err_post {k['mean_err_post']:.4f}.")
        L.append("")
        L.append(f"**P2 MAE by frame:** {m['p2_mae_by_frame']}")
        L.append("")
        L.append(f"**KNI by frame:** {m['kni_rate_by_frame']}")
        L.append("")
        L.append(f"**Controls:** {m['controls']}")
        L.append("")
        L.append(f"**Decision (P3):** {m['decision']}")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pilot_v1")
    ap.add_argument("--model", required=True)
    a = ap.parse_args()
    rows = score_rows(load(a.tag, a.model))
    summary = {
        "tag": a.tag,
        "model": a.model,
        "n_cells": len(rows),
        "modes": [analyse(rows, m) for m in ("direct", "cot")],
    }
    out = ROOT / "results" / a.tag / a.model
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "summary.md").write_text(render(summary) + "\n")
    scored = out / "scored.jsonl"
    with scored.open("w") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if k != "prompt"}) + "\n")
    print(render(summary))


if __name__ == "__main__":
    main()
