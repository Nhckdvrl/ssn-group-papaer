"""Replicate ACL-2022 Figure 6 for MT: greedy search errors by (reference length x uncertainty).

Their claim is conditional on length: within a length bucket, higher `u` means more search errors.
Our search-error indicator is conservative: a segment counts as a search error at beam `b` if ANY
beam in our grid found a hypothesis with a strictly higher raw cumulative log-probability, which is
a lower bound on the true (exact-search) search-error rate.
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")][1:]
    rows.sort(key=lambda r: r["idx"])
    return rows


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "marian"
    beam_of_interest = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    dirs = [os.path.join(ROOT, "results", "ext", "scored"),
            os.path.join(ROOT, "results", "e00", "gen"),
            os.path.join(ROOT, "results", "ext", "gen")]
    cells = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.startswith(f"{tag}_b") or "_RAW" not in fn:
                continue
            beam = int(fn.split("_b")[1].split("_")[0])
            if beam in cells:          # earlier directories win (scored cells first)
                continue
            cells[beam] = load(os.path.join(d, fn))
    beams = sorted(cells)
    lp = {b: np.array([r["sum_logprob"] for r in cells[b]]) for b in beams}
    best = np.max(np.stack([lp[b] for b in beams]), axis=0)
    err = (lp[beam_of_interest] < best - 1e-6).astype(float)

    data = os.path.join(ROOT, "data")
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    L = np.array([len(r.split()) for r in ref_w])

    out = {"tag": tag, "beam": beam_of_interest, "beams_in_grid": beams, "cells": {}}
    print(f"== {tag}, beam {beam_of_interest}: search errors (lower bound) by length x uncertainty ==")
    for reading in ("u_char", "u_word"):
        v = np.array([r[reading] for r in unc])
        bins = [(0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 10)]    # ACL-2022 Fig. 6 bins
        print(f"\n-- {reading} --")
        print(f"{'length':>10} {'n':>5}  " + "  ".join(f"u in ({a:.2f},{b:.2f}]" for a, b in bins))
        rows = []
        for lo, hi, name in [(0, 10, "[0,10]"), (10, 20, "(10,20]"), (20, 30, "(20,30]"),
                             (30, 10 ** 9, "(30,)")]:
            m = (L > lo) & (L <= hi) if lo else (L <= hi)
            cells_row, ns = [], []
            for a, b in bins:
                sel = m & (v > a) & (v <= b) if a > 0 else m & (v <= b)
                cells_row.append(float(err[sel].mean()) if sel.sum() else float("nan"))
                ns.append(int(sel.sum()))
            print(f"{name:>10} {int(m.sum()):5d}  " +
                  "  ".join(f"{100*c:12.1f}% (n={n})" for c, n in zip(cells_row, ns)))
            rows.append({"length_bucket": name, "n": int(m.sum()),
                         "search_error_by_u_bin": cells_row, "n_by_u_bin": ns})
        out["cells"][reading] = rows
    with open(os.path.join(ROOT, "results", "ext", f"fig6_{tag}_b{beam_of_interest}.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
