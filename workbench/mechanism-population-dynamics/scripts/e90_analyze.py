"""E90 trajectories: per seed and checkpoint, the label-free readouts of experiments/E90-*.md.

Usage: e90_analyze.py -> prints a table per seed and writes results/e90/analysis.json
Readouts per checkpoint
  loss       pile-10k NLL (fixed 48 documents)
  metric     clean task metric per task
  hub        induction's top head under all-position ablation: layer, prev-token score, end-only share, its antonym effect;
             early_hub = layer <= 8 and prev >= 0.6
  com        centre-of-mass layer of |effect| per task
  bundles    do greater_than & successor (ordinal) / induction & antonym (ICL) share a top-3 head
  onset      for each bundle's final shared head: first checkpoint where its effect on each task reaches 50% of the final value
"""
import glob
import json
import re

import numpy as np

import mp_common as mc
from e89_analyze import load

DIR = mc.RESULTS / "e90"
BUNDLES = {"ordinal": ("greater_than", "successor"), "icl": ("induction", "antonym")}


def com(m):
    p = np.abs(m).sum(1)
    return float((np.arange(len(p)) * p).sum() / p.sum())


def top3(m):
    return set(np.argsort(-m.ravel())[:3].tolist())


def main():
    runs = {}
    for f in glob.glob(str(DIR / "*.npz")):
        _, model, rev = f.split("/")[-1][:-4].split("__")
        runs.setdefault(model, {})[int(re.search(r"step(\d+)", rev).group(1))] = f
    out = {}
    for model in sorted(runs):
        steps = sorted(runs[model])
        rows = {}
        for st in steps:
            d = load(runs[model][st])
            j = json.loads(open(runs[model][st][:-4] + ".json").read())
            H = d["maps"][("induction", "all")].shape[2]
            P = d["roles"]["prev"].mean(0).ravel()
            I = d["maps"][("induction", "all")].mean(0).ravel()
            Ie = d["maps"][("induction", "end")].mean(0).ravel()
            h = int(np.argmax(I))
            r = {"loss": j.get("lm_loss"), "metric": {t: round(v["metric"], 2) for t, v in j["tasks"].items()},
                 "hub": {"head": f"{h // H}.{h % H}", "layer": h // H, "prev": round(float(P[h]), 2),
                         "end_share": round(float(Ie[h] / max(I[h], 1e-6)), 2), "eff": round(float(I[h]), 2),
                         "antonym_eff": round(float(d["maps"][("antonym", "all")].mean(0).ravel()[h]), 2),
                         "top_prev_head": f"{int(np.argmax(P)) // H}.{int(np.argmax(P)) % H}", "top_prev": round(float(P.max()), 2)},
                 "com": {t: round(com(d["maps"][(t, "all")].mean(0)), 1) for t in j["tasks"]},
                 "bundle_shared": {b: bool(top3(d["maps"][(x, "all")].mean(0)) & top3(d["maps"][(y, "all")].mean(0)))
                                   for b, (x, y) in BUNDLES.items()}}
            r["hub"]["early_hub"] = bool(r["hub"]["layer"] <= 8 and r["hub"]["prev"] >= 0.6)
            rows[st] = (r, d)
        # onset of each bundle's final shared head
        onset = {}
        fin = rows[steps[-1]][1]
        for b, (x, y) in BUNDLES.items():
            shared = top3(fin["maps"][(x, "all")].mean(0)) & top3(fin["maps"][(y, "all")].mean(0))
            if not shared:
                onset[b] = None
                continue
            hh = max(shared, key=lambda k: fin["maps"][(x, "all")].mean(0).ravel()[k] + fin["maps"][(y, "all")].mean(0).ravel()[k])
            o = {}
            for t in (x, y):
                final = fin["maps"][(t, "all")].mean(0).ravel()[hh]
                o[t] = next((st for st in steps if final > 0 and rows[st][1]["maps"][(t, "all")].mean(0).ravel()[hh] >= .5 * final), None)
            onset[b] = {"head": int(hh), **o}
        out[model] = {"steps": {st: rows[st][0] for st in steps}, "onset_final_step_available": steps[-1], "onset": onset}
        print(f"\n== {model}  (onset of final shared heads: {onset})")
        for st in steps:
            r = rows[st][0]
            print(f"{st:>7d} loss={r['loss'] or 0:.3f} hub={r['hub']['head']:>6s} L{r['hub']['layer']:<2d} prev={r['hub']['prev']:.2f} "
                  f"end={r['hub']['end_share']:+.2f} ant_on_hub={r['hub']['antonym_eff']:+.2f} topprev={r['hub']['top_prev_head']}({r['hub']['top_prev']:.2f}) "
                  f"early={int(r['hub']['early_hub'])} ord={int(r['bundle_shared']['ordinal'])} icl={int(r['bundle_shared']['icl'])} | "
                  + " ".join(f"{t[:4]}={v:+.2f}" for t, v in r["metric"].items()))
    (DIR / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
