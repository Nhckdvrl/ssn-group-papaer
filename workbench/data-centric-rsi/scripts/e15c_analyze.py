"""E15c analysis (CPU): per cell (weights x materials x task x temperature) readouts of validated AZR proposals.

Cells come from file names val_prop_<tag>_<materials>_<task>_t<temp>_s<seed>.jsonl (output of e15c_validate.py).
Readouts per cell, pooled over seeds and at matched sample budgets (first B samples in (seed, idx) order):
  valid rate, parse / sandbox / AZR-banned rejects, behaviour-fingerprint coverage, unique fingerprints,
  new behaviours = unique fingerprints absent from the materials the cell used, and absent from seed U late
  materials (common reference), copy rates against the six prompt references (normalised AST / fingerprint),
  program size (AST nodes, characters), radon Halstead effort / volume, cyclomatic complexity and AZR's
  halstead_reward score (formula of rewards/code_reward.get_halstead_reward, without black formatting).
Cross-cell: overlap of unique-fingerprint sets at matched budget.

Usage: python e15c_analyze.py --val_dir <dir> --seed_mat seed.jsonl --late_mat late.jsonl --out <json> [--workers 12]
"""
import argparse
import collections
import glob
import importlib.util
import json
import os
import re
import statistics as st
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e15c_validate", os.path.join(HERE, "e15c_validate.py"))
V = importlib.util.module_from_spec(spec); sys.modules["e15c_validate"] = V; spec.loader.exec_module(V)
NAME = re.compile(r"val_prop_(init|final)_(seed|late)_(code_[io])_t([0-9.]+)_s(\d+)\.jsonl$")


def halstead(code):
    try:
        from radon.metrics import h_visit
        from radon.complexity import cc_visit
        h = h_visit(code).total
        cc = max((b.complexity for b in cc_visit(code)), default=1)
        score = 0.5 * min(h.effort / 10000, 1) + 0.3 * min(cc / 10, 1) + 0.2 * min(h.volume / 500, 1)
        return {"effort": h.effort, "volume": h.volume, "cc": cc, "azr_halstead": round(score, 3)}
    except Exception:
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def readouts(rows, used_fp, union_fp):
    n = len(rows)
    val = [r for r in rows if r.get("valid")]
    fps = [r["fp"] for r in val if r.get("fp")]
    ufp = set(fps)
    hs = [r["_h"] for r in val if r.get("_h")]
    return {
        "n": n, "parsed": sum(r["parsed"] for r in rows) / max(1, n),
        "sandbox_reject": sum(r["sandbox_reject"] for r in rows) / max(1, n),
        "azr_banned": sum(r["azr_banned"] for r in rows) / max(1, n),
        "valid": len(val) / max(1, n), "n_valid": len(val),
        "fp_coverage": len(fps) / max(1, len(val)),
        "unique_fp": len(ufp), "unique_ast": len({r.get("ast_hash") for r in val if r.get("ast_hash")}),
        "new_fp_vs_used": len(ufp - used_fp), "new_fp_vs_union": len(ufp - union_fp),
        "new_fp_vs_used_per_1k_samples": 1000 * len(ufp - used_fp) / max(1, n),
        "copy_of_ref_ast": sum(bool(r.get("copy_of_ref_ast")) for r in val) / max(1, len(val)),
        "same_fp_as_ref": sum(bool(r.get("same_fp_as_ref")) for r in val) / max(1, len(val)),
        "ast_nodes_median": med([r.get("ast_nodes") for r in val]),
        "code_chars_median": med([r.get("code_chars") for r in val]),
        "tokens_median_all": med([r.get("n_tokens") for r in rows]),
        "truncated": sum(r.get("finish") == "length" for r in rows) / max(1, n),
        "halstead_effort_median": med([h["effort"] for h in hs]), "halstead_volume_median": med([h["volume"] for h in hs]),
        "cc_median": med([h["cc"] for h in hs]), "azr_halstead_mean": st.mean([h["azr_halstead"] for h in hs]) if hs else None,
    }, ufp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val_dir", required=True); ap.add_argument("--seed_mat", required=True)
    ap.add_argument("--late_mat", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    mat_fp = {}
    for k, p in [("seed", a.seed_mat), ("late", a.late_mat)]:
        mat_fp[k] = {x["fp"] for x in V.material_keys(p, a.workers) if x["fp"]}
    union_fp = mat_fp["seed"] | mat_fp["late"]
    cells = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(a.val_dir, "val_prop_*.jsonl"))):
        m = NAME.search(p)
        if not m:
            continue
        tag, mat, task, temp, seed = m.groups()
        for l in open(p):
            r = json.loads(l); r["_seed"] = int(seed); cells[(tag, mat, task, temp)].append(r)
    allv = [r for rr in cells.values() for r in rr if r.get("valid")]
    with Pool(a.workers) as pool:
        hs = pool.map(halstead, [r["code"] for r in allv], chunksize=64)
    for r, h in zip(allv, hs):
        r["_h"] = h
    res = {"materials": {"seed_unique_fp": len(mat_fp["seed"]), "late_unique_fp": len(mat_fp["late"]),
                         "late_fp_not_in_seed": len(mat_fp["late"] - mat_fp["seed"])},
           "cells": {}, "budget": {}, "overlap": {}}
    sets = {}
    for (tag, mat, task, temp), rows in sorted(cells.items()):
        rows.sort(key=lambda r: (r["_seed"], r["idx"]))
        key = f"{tag}|{mat}|{task}|t{temp}"
        res["cells"][key], _ = readouts(rows, mat_fp[mat], union_fp)
        for s in sorted({r["_seed"] for r in rows}):
            res["cells"][f"{key}|seed{s}"], _ = readouts([r for r in rows if r["_seed"] == s], mat_fp[mat], union_fp)
        for b in (1024, 2048, 4096):
            if len(rows) >= b:
                res["budget"][f"{key}|B{b}"], sets[(key, b)] = readouts(rows[:b], mat_fp[mat], union_fp)
    # overlap of behaviour sets between cells at the same budget (same task and temperature)
    for (k1, b1), s1 in sets.items():
        for (k2, b2), s2 in sets.items():
            t1, t2 = k1.split("|")[2:], k2.split("|")[2:]
            if b1 == b2 and t1 == t2 and k1 < k2:
                res["overlap"][f"{k1} vs {k2}|B{b1}"] = {"jaccard": len(s1 & s2) / max(1, len(s1 | s2)),
                                                         "frac_of_first_in_second": len(s1 & s2) / max(1, len(s1)),
                                                         "frac_of_second_in_first": len(s1 & s2) / max(1, len(s2))}
    json.dump(res, open(a.out, "w"), indent=1)
    for k, v in res["budget"].items():
        print(k, {x: (round(v[x], 3) if isinstance(v[x], float) else v[x]) for x in
                  ("n", "valid", "unique_fp", "new_fp_vs_used", "new_fp_vs_union", "copy_of_ref_ast", "ast_nodes_median")})


if __name__ == "__main__":
    main()
