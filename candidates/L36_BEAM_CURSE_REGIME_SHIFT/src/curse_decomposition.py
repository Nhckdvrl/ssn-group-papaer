"""E00 Gate B diagnostic — what *is* the classic curse on this substrate?

Decomposes the beam-4 -> beam-64 quality drop under RAW scoring into the empty-hypothesis channel
and everything else, per uncertainty stratum, for both classic systems and both `u` readings.
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M  # noqa: E402


def load(tag, beam, sem):
    fn = os.path.join(ROOT, "results", "e00", "gen", f"{tag}_b{beam}_{sem}.jsonl")
    rows = [json.loads(l) for l in open(fn, encoding="utf-8")][1:]
    rows.sort(key=lambda r: r["idx"])
    return [r["hyp"] for r in rows]


def main():
    data = os.path.join(ROOT, "data")
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]
    refs = [[a, b] for a, b in zip(ref_w, ref_a)]
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    ref_words = np.array([len(r.split()) for r in ref_w], float)

    out = {}
    for tag in ("fsmt", "marian"):
        h4, h64 = load(tag, 4, "RAW"), load(tag, 64, "RAW")
        st4 = np.array([M.bleu_segment_stats(h, r) for h, r in zip(h4, refs)], float)
        st64 = np.array([M.bleu_segment_stats(h, r) for h, r in zip(h64, refs)], float)
        e4 = np.array([1.0 if not h.strip() else 0.0 for h in h4])
        e64 = np.array([1.0 if not h.strip() else 0.0 for h in h64])
        for reading in ("u_char", "u_word"):
            v = np.array([r[reading] for r in unc])
            lab = np.digitize(v, np.quantile(v, [.25, .5, .75]), right=True)
            rows = []
            for q in range(4):
                idx = np.where(lab == q)[0]
                keep = idx[(e4[idx] == 0) & (e64[idx] == 0)]
                rows.append({
                    "stratum": f"Q{q+1}", "n": int(len(idx)),
                    "mean_u": float(v[idx].mean()),
                    "mean_ref_words": float(ref_words[idx].mean()),
                    "empty_rate_b4": float(e4[idx].mean()),
                    "empty_rate_b64": float(e64[idx].mean()),
                    "len_ratio_b64": float(np.mean([len(h64[i].split()) for i in idx]) / ref_words[idx].mean()),
                    "bleu_b4": M.bleu_from_stats(st4[idx].sum(0)),
                    "bleu_b64": M.bleu_from_stats(st64[idx].sum(0)),
                    "D": M.bleu_from_stats(st64[idx].sum(0)) - M.bleu_from_stats(st4[idx].sum(0)),
                    "D_relative_pct": 100 * (M.bleu_from_stats(st64[idx].sum(0)) / M.bleu_from_stats(st4[idx].sum(0)) - 1),
                    "D_nonempty_only": M.bleu_from_stats(st64[keep].sum(0)) - M.bleu_from_stats(st4[keep].sum(0)),
                    "n_nonempty_both": int(len(keep)),
                })
            out[f"{tag}_{reading}"] = rows
            print(f"\n== {tag} / {reading} (RAW, beam 4 -> 64) ==")
            print(f"{'':4s} {'n':>4} {'u':>6} {'refW':>6} {'empty%@64':>10} {'lenratio':>9} "
                  f"{'BLEU4':>7} {'BLEU64':>7} {'D':>7} {'D%':>7} {'D|nonempty':>11}")
            for r in rows:
                print(f"{r['stratum']:4s} {r['n']:4d} {r['mean_u']:6.3f} {r['mean_ref_words']:6.1f} "
                      f"{100*r['empty_rate_b64']:10.2f} {r['len_ratio_b64']:9.3f} {r['bleu_b4']:7.2f} "
                      f"{r['bleu_b64']:7.2f} {r['D']:+7.2f} {r['D_relative_pct']:+6.1f}% {r['D_nonempty_only']:+11.2f}")

    with open(os.path.join(ROOT, "results", "e00", "curse_decomposition.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
