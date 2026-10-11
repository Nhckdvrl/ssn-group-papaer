"""Do ACL-2022's *actual* sentence-level claims replicate on our instrument?

Stahlberg et al. (2022) claim that intrinsic uncertainty `u` predicts **search difficulty**
(greedy/beam search errors relative to a better search), not that it predicts beam-induced quality
damage. This script separates the two on the same generations:

- `search_error(b)` = fraction of segments where a wider beam finds a hypothesis with strictly
  higher raw cumulative log-probability than beam `b` (reference = the widest RAW cell available).
  This is their quantity with beam-`B_max` standing in for exact search.
- `D(b_ref -> b_large)` = the quality damage already reported in Gate B.

Both are then broken down by the frozen uncertainty quartiles.
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M  # noqa: E402


def load(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")][1:]
    rows.sort(key=lambda r: r["idx"])
    return rows


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "fsmt"
    data = os.path.join(ROOT, "data")
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]
    refs = [[a, b] for a, b in zip(ref_w, ref_a)]

    cells = {}
    for d in (os.path.join(ROOT, "results", "e00", "gen"), os.path.join(ROOT, "results", "ext", "gen")):
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.startswith(f"{tag}_b") or "_RAW" not in fn:
                continue
            beam = int(fn.split("_b")[1].split("_")[0])
            cells[beam] = load(os.path.join(d, fn))
    beams = sorted(cells)
    if not beams:
        print(f"no RAW cells for {tag}")
        return
    bmax = beams[-1]
    lp = {b: np.array([r["sum_logprob"] for r in cells[b]]) for b in beams}
    best = np.max(np.stack([lp[b] for b in beams]), axis=0)  # best hypothesis score found anywhere

    out = {"tag": tag, "beams": beams, "reference_beam": bmax, "by_reading": {}}
    print(f"== {tag} == search errors vs the best RAW hypothesis found at any beam (max b={bmax})")
    for reading in ("u_char", "u_word"):
        v = np.array([r[reading] for r in unc])
        lab = np.digitize(v, np.quantile(v, [.25, .5, .75]), right=True)
        rows = []
        print(f"\n-- {reading} --")
        header = f"{'beam':>5} {'all':>7} " + " ".join(f"{'Q'+str(q+1):>7}" for q in range(4))
        print(header)
        for b in beams:
            err = (lp[b] < best - 1e-6).astype(float)
            line = f"{b:5d} {100*err.mean():6.1f}% " + " ".join(
                f"{100*err[lab == q].mean():6.1f}%" for q in range(4))
            print(line)
            rows.append({"beam": b, "search_error_all": float(err.mean()),
                         "search_error_by_stratum": [float(err[lab == q].mean()) for q in range(4)]})
        # quality damage for the same strata, beam 4 -> bmax
        if 4 in cells:
            st4 = np.array([M.bleu_segment_stats(r["hyp"], rf) for r, rf in zip(cells[4], refs)], float)
            stB = np.array([M.bleu_segment_stats(r["hyp"], rf) for r, rf in zip(cells[bmax], refs)], float)
            dmg = []
            for q in range(4):
                idx = np.where(lab == q)[0]
                dmg.append(M.bleu_from_stats(stB[idx].sum(0)) - M.bleu_from_stats(st4[idx].sum(0)))
            print(f"  quality damage D(4->{bmax}) by stratum: " + " ".join(f"{d:+7.2f}" for d in dmg))
            out["by_reading"][reading] = {"search_errors": rows, "damage_4_to_max": dmg}
        else:
            out["by_reading"][reading] = {"search_errors": rows}

    with open(os.path.join(ROOT, "results", "ext", f"search_errors_{tag}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote", os.path.join("results", "ext", f"search_errors_{tag}.json"))


if __name__ == "__main__":
    main()
