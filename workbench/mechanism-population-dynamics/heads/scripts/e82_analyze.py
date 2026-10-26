"""E82 analysis: when are IOI carriers fixed, vs attention roles; when do same-init siblings diverge.

Usage: e82_analyze.py -> results/e82/analysis.json + printed tables
"""
import glob
import json

import numpy as np

import mp_common as mc
from e81_analyze import SB, within, top

OUT = mc.RESULTS / "e82"
STEPS = [512, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 12000, 16000, 24000, 33000, 48000, 66000, 100000, 143000]


def load():
    D = {}
    for f in glob.glob(str(OUT / "*.npz")):
        z = np.load(f)
        _, model, step = f.split("/")[-1][:-4].split("__")
        D[(model, int(step))] = {k: z[k] for k in z.files}
    J = {}
    for f in glob.glob(str(OUT / "pythia__*.json")):
        d = json.loads(open(f).read())
        _, model, step = d["tag"].split("__")
        J[(model, int(step))] = d
    return D, J


def additive_transfer(src_abl, tgt_abl):
    own = sum(tgt_abl[l, h] for l, h in top(tgt_abl))
    return float(sum(tgt_abl[l, h] for l, h in top(src_abl)) / own) if own > 0 else None


def freeze(series, ok):
    """Earliest step from which ok(step) holds for every later step."""
    steps = sorted(series)
    for i, s in enumerate(steps):
        if all(ok(t) for t in steps[i:]):
            return s
    return None


def main():
    D, J = load()
    res = {"runs": {}, "siblings": {}}
    for model in ("pythia-410m", "pythia-410m-deduped", "pythia-160m", "pythia-160m-deduped"):
        S = {s: D[(model, s)] for s in STEPS if (model, s) in D}
        if 143000 not in S:
            continue
        fin = S[143000]
        ftop = set(top(fin["dla"].mean(0)))
        rows = {}
        for s, d in S.items():
            rows[s] = {"logit_diff": J[(model, s)]["logit_diff"],
                       "top3_dla": [f"{l}.{h}" for l, h in top(d["dla"].mean(0))],
                       "top3_overlap_final": len(set(top(d["dla"].mean(0))) & ftop),
                       "transfer_final_top3": additive_transfer(fin["abl"].mean(0), d["abl"].mean(0)),
                       "ind_vs_final": within(d["ind"].mean(0), fin["ind"].mean(0)),
                       "attio_vs_final": within(d["att_io"].mean(0), fin["att_io"].mean(0))}
        carrier = freeze(rows, lambda t: rows[t]["top3_overlap_final"] == 3 and (rows[t]["transfer_final_top3"] or 0) >= 0.9)
        role = freeze(rows, lambda t: rows[t]["ind_vs_final"] >= 0.9 and rows[t]["attio_vs_final"] >= 0.9)
        emerge = next((s for s in sorted(rows) if rows[s]["logit_diff"] > 1), None)
        res["runs"][model] = {"rows": rows, "carrier_freeze": carrier, "role_freeze": role, "ioi_emerges": emerge}
    for a, b in (("pythia-410m", "pythia-410m-deduped"), ("pythia-160m", "pythia-160m-deduped")):
        cur = {}
        for s in STEPS:
            if (a, s) in D and (b, s) in D:
                x, y = D[(a, s)], D[(b, s)]
                rel = lambda d, k: SB(within(d[k][0], d[k][1]))  # noqa: E731
                ab = within(x["abl"].mean(0), y["abl"].mean(0))
                cur[s] = {"ind": within(x["ind"].mean(0), y["ind"].mean(0)),
                          "att_io": within(x["att_io"].mean(0), y["att_io"].mean(0)),
                          "abl_corrected": ab / np.sqrt(max(rel(x, "abl"), 1e-3) * max(rel(y, "abl"), 1e-3)),
                          "top3_overlap": len(set(top(x["dla"].mean(0))) & set(top(y["dla"].mean(0)))),
                          "transfer": additive_transfer(x["abl"].mean(0), y["abl"].mean(0))}
        res["siblings"][f"{a} vs {b}"] = cur
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    for m, r in res["runs"].items():
        print(f"\n{m}: IOI emerges {r['ioi_emerges']}, role freeze {r['role_freeze']}, carrier freeze {r['carrier_freeze']}")
        for s, x in sorted(r["rows"].items()):
            print(f"  {s:6d} LD {x['logit_diff']:5.2f} ind~fin {x['ind_vs_final']:.2f} attIO~fin {x['attio_vs_final']:.2f} "
                  f"top3 {x['top3_dla']} overlap {x['top3_overlap_final']} transfer {x['transfer_final_top3'] and round(x['transfer_final_top3'], 2)}")
    for k, cur in res["siblings"].items():
        print(f"\n{k}")
        for s, x in sorted(cur.items()):
            print(f"  {s:6d} ind {x['ind']:.2f} attIO {x['att_io']:.2f} abl(corr) {x['abl_corrected']:.2f} top3 {x['top3_overlap']} transfer {x['transfer'] and round(x['transfer'], 2)}")


if __name__ == "__main__":
    main()
