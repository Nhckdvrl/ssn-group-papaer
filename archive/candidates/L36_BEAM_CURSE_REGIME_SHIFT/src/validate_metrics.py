"""E00 §B.4 — validate `src/mt_metrics.py` against upstream sacrebleu (vendored, not installed).

Compares corpus BLEU (single- and multi-reference) and chrF2 on real system outputs, plus a
random-subset check, and writes `results/e00/metric_validation.json`.
Tolerance: |dBLEU| <= 0.05, |dchrF2| <= 0.05.
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M  # noqa: E402

from sacrebleu.metrics import BLEU, CHRF  # noqa: E402  (vendored via PYTHONPATH)

TOL = 0.05


def main():
    data = os.path.join(ROOT, "data")
    ref_wmt = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.wmtref.de"), encoding="utf-8")]
    ref_ar = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.arref.de"), encoding="utf-8")]

    gen_dir = os.path.join(ROOT, "results", "e00", "gen")
    cells = sorted(f for f in os.listdir(gen_dir) if f.endswith(".jsonl"))
    checks = []
    rng = np.random.default_rng(0)

    for fn in cells:
        rows = [json.loads(l) for l in open(os.path.join(gen_dir, fn), encoding="utf-8")][1:]
        rows.sort(key=lambda r: r["idx"])
        hyps = [r["hyp"] for r in rows]
        subsets = {"full": np.arange(len(hyps)),
                   "rand500": rng.choice(len(hyps), 500, replace=False)}
        for sname, idx in subsets.items():
            h = [hyps[i] for i in idx]
            rw = [ref_wmt[i] for i in idx]
            ra = [ref_ar[i] for i in idx]

            ours_single = M.corpus_bleu(h, [[a] for a in rw])
            ours_multi = M.corpus_bleu(h, [[a, b] for a, b in zip(rw, ra)])
            ours_chrf = M.corpus_chrf(h, [[a, b] for a, b in zip(rw, ra)])

            sb_single = BLEU().corpus_score(h, [rw]).score
            sb_multi = BLEU().corpus_score(h, [rw, ra]).score
            sb_chrf = CHRF().corpus_score(h, [rw, ra]).score

            checks.append({
                "cell": fn, "subset": sname,
                "bleu_single": [ours_single, sb_single, ours_single - sb_single],
                "bleu_multi": [ours_multi, sb_multi, ours_multi - sb_multi],
                "chrf2_multi": [ours_chrf, sb_chrf, ours_chrf - sb_chrf],
            })
            print(f"{fn:26s} {sname:8s} BLEU1 {ours_single:6.2f}/{sb_single:6.2f} "
                  f"BLEUm {ours_multi:6.2f}/{sb_multi:6.2f} chrF2 {ours_chrf:6.2f}/{sb_chrf:6.2f}")

    b, c = BLEU(), CHRF()
    b.corpus_score(["a"], [["a"]])
    c.corpus_score(["a"], [["a"]])

    worst = max(max(abs(c[k][2]) for k in ("bleu_single", "bleu_multi", "chrf2_multi"))
                for c in checks)
    out = {
        "tolerance": TOL,
        "sacrebleu_version": "2.4.3 (vendored source, not installed)",
        "bleu_signature": str(b.get_signature()),
        "chrf_signature": str(c.get_signature()),
        "max_abs_diff": worst,
        "pass": bool(worst <= TOL),
        "checks": checks,
    }
    with open(os.path.join(ROOT, "results", "e00", "metric_validation.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nmax |diff| = {worst:.4f}  ->  {'PASS' if out['pass'] else 'FAIL'}")
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
