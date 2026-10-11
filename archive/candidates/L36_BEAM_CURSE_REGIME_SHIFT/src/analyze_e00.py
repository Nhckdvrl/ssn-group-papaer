"""L36 E00 Gate B/D analysis — stratified beam-width effects with a paired bootstrap.

Reads the per-cell generation JSONL produced by `run_beam_sweep.py`, computes per-segment BLEU and
chrF statistics once, then aggregates them per uncertainty stratum. Everything downstream (corpus
BLEU per stratum, D, CURSE, bootstrap CIs) is a sum over those cached statistics.

Predeclared in `E00_INSTRUMENT_AND_PROVENANCE_AUDIT.md` §B.5/§B.6; the `u_char`/`u_word` double
reporting is amendment A.3'.
"""

import argparse
import json
import os

import numpy as np

import mt_metrics as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT_N = 1000
BOOT_SEED = 20260914


def load_cell(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    header = rows[0]
    body = sorted((r for r in rows[1:]), key=lambda r: r["idx"])
    return header, body


def segment_stats(hyps, refs_list):
    bleu = np.array([M.bleu_segment_stats(h, r) for h, r in zip(hyps, refs_list)], dtype=float)
    chrf = np.array([M.chrf_segment_stats(h, r) for h, r in zip(hyps, refs_list)], dtype=float)
    return bleu, chrf


def corpus_bleu_from(stats, idx):
    return M.bleu_from_stats(stats[idx].sum(axis=0))


def corpus_chrf_from(stats, idx):
    return M.chrf_from_stats(stats[idx].sum(axis=0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="fsmt")
    ap.add_argument("--gen-dir", default=os.path.join(ROOT, "results", "e00", "gen"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--beams", default="1,4,8,16,32,64")
    ap.add_argument("--b-ref", type=int, default=4)
    ap.add_argument("--b-large", type=int, default=64)
    args = ap.parse_args()

    data = os.path.join(ROOT, "data")
    src = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.en"), encoding="utf-8")]
    ref_wmt = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.wmtref.de"), encoding="utf-8")]
    ref_ar = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.arref.de"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(data, "uncertainty.jsonl"), encoding="utf-8")]
    refs_multi = [[a, b] for a, b in zip(ref_wmt, ref_ar)]
    refs_single = [[a] for a in ref_wmt]
    n = len(src)

    # strata under both readings (amendment A.3')
    strata = {}
    for reading in ("u_char", "u_word"):
        v = np.array([r[reading] for r in unc])
        cuts = np.quantile(v, [0.25, 0.5, 0.75])
        lab = np.digitize(v, cuts, right=True)  # 0..3
        strata[reading] = {"labels": lab, "cuts": cuts.tolist(),
                           "sizes": [int((lab == k).sum()) for k in range(4)]}

    beams = [int(b) for b in args.beams.split(",")]
    cells = {}
    for beam in beams:
        for sem in ("RAW", "NORM"):
            fn = os.path.join(args.gen_dir, f"{args.tag}_b{beam}_{sem}.jsonl")
            if beam == 1 and not os.path.exists(fn):
                fn = os.path.join(args.gen_dir, f"{args.tag}_b1_RAW.jsonl")  # greedy shared
            if not os.path.exists(fn):
                print(f"[missing] {fn}")
                continue
            header, body = load_cell(fn)
            assert len(body) == n, (fn, len(body))
            hyps = [r["hyp"] for r in body]
            b_multi, c_multi = segment_stats(hyps, refs_multi)
            b_single, _ = segment_stats(hyps, refs_single)
            cells[(beam, sem)] = {
                "header": header,
                "hyps": hyps,
                "bleu_multi": b_multi,
                "chrf_multi": c_multi,
                "bleu_single": b_single,
                "gen_tokens": np.array([r["gen_tokens"] for r in body], float),
                "truncated": np.array([r["truncated"] for r in body], float),
                "empty": np.array([1.0 if not r["hyp"].strip() else 0.0 for r in body]),
                "sum_logprob": np.array([r.get("sum_logprob", np.nan) for r in body], float),
                "mean_logprob": np.array([r.get("mean_logprob", np.nan) for r in body], float),
            }
            print(f"[loaded] beam={beam:3d} {sem:4s} n={len(body)}")

    ref_len_words = np.array([len(r.split()) for r in ref_wmt], float)

    report = {"tag": args.tag, "n": n, "bootstrap": {"n": BOOT_N, "seed": BOOT_SEED},
              "strata": {k: {"cuts": v["cuts"], "sizes": v["sizes"]} for k, v in strata.items()},
              "cells": {}, "estimands": {}}

    # descriptive table -----------------------------------------------------------------------
    all_idx = np.arange(n)
    for (beam, sem), c in sorted(cells.items()):
        row = {
            "bleu_multi_all": corpus_bleu_from(c["bleu_multi"], all_idx),
            "bleu_single_all": corpus_bleu_from(c["bleu_single"], all_idx),
            "chrf_multi_all": corpus_chrf_from(c["chrf_multi"], all_idx),
            "mean_gen_tokens": float(c["gen_tokens"].mean()),
            "len_ratio_words": float(np.mean([len(h.split()) for h in c["hyps"]]) / ref_len_words.mean()),
            "empty_rate": float(c["empty"].mean()),
            "truncation_rate": float(c["truncated"].mean()),
            "mean_sum_logprob": float(np.nanmean(c["sum_logprob"])),
            "mean_logprob_per_token": float(np.nanmean(c["mean_logprob"])),
        }
        for reading in ("u_char", "u_word"):
            lab = strata[reading]["labels"]
            for q in range(4):
                idx = np.where(lab == q)[0]
                row[f"bleu_multi_{reading}_Q{q+1}"] = corpus_bleu_from(c["bleu_multi"], idx)
                row[f"chrf_multi_{reading}_Q{q+1}"] = corpus_chrf_from(c["chrf_multi"], idx)
        report["cells"][f"b{beam}_{sem}"] = row

    # estimands with paired bootstrap ---------------------------------------------------------
    rng = np.random.default_rng(BOOT_SEED)

    def boot_indices(idx):
        return rng.integers(0, len(idx), size=(BOOT_N, len(idx)))

    for sem in ("RAW", "NORM"):
        key_ref, key_large = (args.b_ref, sem), (args.b_large, sem)
        if key_ref not in cells or key_large not in cells:
            continue
        cr, cl = cells[key_ref], cells[key_large]
        for reading in ("u_char", "u_word"):
            lab = strata[reading]["labels"]
            idx_hi = np.where(lab == 3)[0]
            idx_lo = np.where(lab == 0)[0]
            idx_all = all_idx

            def D(idx, draws=None):
                if draws is None:
                    return (corpus_bleu_from(cl["bleu_multi"], idx)
                            - corpus_bleu_from(cr["bleu_multi"], idx))
                out = np.empty(len(draws))
                for k, d in enumerate(draws):
                    sel = idx[d]
                    out[k] = (M.bleu_from_stats(cl["bleu_multi"][sel].sum(axis=0))
                              - M.bleu_from_stats(cr["bleu_multi"][sel].sum(axis=0)))
                return out

            d_hi_draws, d_lo_draws = boot_indices(idx_hi), boot_indices(idx_lo)
            d_all_draws = boot_indices(idx_all)
            D_hi, D_lo, D_all = D(idx_hi), D(idx_lo), D(idx_all)
            Bhi, Blo, Ball = D(idx_hi, d_hi_draws), D(idx_lo, d_lo_draws), D(idx_all, d_all_draws)
            curse = D_hi - D_lo
            Bcurse = Bhi - Blo

            def ci(a):
                return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]

            report["estimands"][f"{sem}_{reading}"] = {
                "b_ref": args.b_ref, "b_large": args.b_large,
                "D_all": float(D_all), "D_all_ci": ci(Ball),
                "D_Uhigh": float(D_hi), "D_Uhigh_ci": ci(Bhi), "D_Uhigh_se": float(Bhi.std(ddof=1)),
                "D_Ulow": float(D_lo), "D_Ulow_ci": ci(Blo),
                "CURSE": float(curse), "CURSE_ci": ci(Bcurse),
                "MDE_D_Uhigh_80pct": float(2.802 * Bhi.std(ddof=1)),
                "gate_B61_pass": bool(D_hi <= -2.0 and np.percentile(Bhi, 97.5) < -1.0),
                "gate_B62_pass": bool(curse <= -1.0 and np.percentile(Bcurse, 97.5) < 0.0),
            }
            print(f"[{sem}/{reading}] D_all={D_all:+.2f} D_high={D_hi:+.2f} {ci(Bhi)} "
                  f"D_low={D_lo:+.2f} CURSE={curse:+.2f} {ci(Bcurse)}")

    out = args.out or os.path.join(ROOT, "results", "e00", f"gateB_{args.tag}.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main()
