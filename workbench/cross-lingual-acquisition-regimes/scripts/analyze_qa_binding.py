"""Pair-clustered question binding, context contribution and answer-language contrasts."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import numpy as np


def read(path):
    metadata = json.loads(path.with_suffix(".meta.json").read_text())
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == metadata["expected_items"]
    indexed = {(r["pair"], r["context_lang"], r["question_lang"], r["answer_lang"], r["question_index"]): r for r in rows}
    assert len(indexed) == len(rows)
    assert len(rows) == 16 * len({r["pair"] for r in rows})
    excluded = {"scores", "question_only_scores", "generated_raw", "generated_answer", "em", "f1"}
    items = [{k: v for k, v in r.items() if k not in excluded} for r in rows]
    digest = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert digest == metadata["items_sha256"], "Actual items do not match manifest hash"
    assert all(len(r[field]) == 2 and all(np.isfinite(s["ll"]) and s["tokens"] > 0 for s in r[field]) for r in rows for field in ["scores", "question_only_scores"])
    return indexed, metadata


def measurements(rows, ids, cell):
    result = collections.defaultdict(list)
    for identifier in ids:
        pair = [rows[(identifier, *cell, q)] for q in [0, 1]]
        result["language_sensitive"].append(pair[0]["answer_language_sensitive"])
        for field, prefix in [("scores", "full"), ("question_only_scores", "question_only")]:
            margins = [r[field][q]["ll"] - r[field][1-q]["ll"] for q, r in enumerate(pair)]
            correct = [int(np.argmax([s["ll"] for s in r[field]]) == q) for q, r in enumerate(pair)]
            result[prefix + "_accuracy"].append(np.mean(correct))
            result[prefix + "_both_correct"].append(int(all(correct)))
            # Fixed answer options: averaging opposite gold margins cancels an additive answer prior.
            result[prefix + "_binding_margin"].append(np.mean(margins))
        result["context_binding_contribution"].append(result["full_binding_margin"][-1] - result["question_only_binding_margin"][-1])
        for metric in ["em", "f1"]:
            if metric in pair[0]:
                result[metric].append(np.mean([r[metric] for r in pair]))
        if "em" in pair[0]:
            result["generation_both_exact"].append(int(all(r["em"] for r in pair)))
        if "generated_answer" in pair[0]:
            result["empty_generation"].append(np.mean([not r["generated_answer"] for r in pair]))
    return {k: np.array(v) for k, v in result.items()}


def contrast(a, b, indices):
    delta = b - a
    return {"control": float(a.mean()), "treated": float(b.mean()), "delta": float(delta.mean()),
            "pair_bootstrap_95ci": np.quantile(delta[indices].mean(axis=1), [.025, .975]).tolist()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("control", type=Path)
    parser.add_argument("treated", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--early-control", type=Path)
    parser.add_argument("--early-treated", type=Path)
    args = parser.parse_args()
    control, cm = read(args.control)
    treated, tm = read(args.treated)
    assert cm["items_sha256"] == tm["items_sha256"]
    assert set(control) == set(treated)
    ids = sorted({k[0] for k in control})
    cells = sorted({k[1:4] for k in control})
    rng = np.random.default_rng(20260930)
    arrays = {cell: (measurements(control, ids, cell), measurements(treated, ids, cell)) for cell in cells}
    assert bool(args.early_control) == bool(args.early_treated)
    early_arrays = None
    if args.early_control:
        ec, ecm = read(args.early_control)
        et, etm = read(args.early_treated)
        assert ecm["items_sha256"] == etm["items_sha256"] == cm["items_sha256"]
        assert set(ec) == set(et) == set(control)
        early_arrays = {cell: (measurements(ec, ids, cell), measurements(et, ids, cell)) for cell in cells}
    result = {"control": cm, "treated": tm, "pairs": len(ids), "cells": {}, "answer_language_interactions": {}}
    if early_arrays:
        result.update({"early_control": ecm, "early_treated": etm, "late_minus_early_parallel_effect": {}})
    for stratum in ["all", "language_sensitive", "language_invariant"]:
        mask = np.ones(len(ids), dtype=bool) if stratum == "all" else arrays[cells[0]][0]["language_sensitive"] == (stratum == "language_sensitive")
        n = int(mask.sum())
        if not n:
            continue
        bootstrap = rng.integers(n, size=(10000, n))
        for cell, (a, b) in arrays.items():
            result["cells"][stratum + "/" + "/".join(cell)] = {"pairs": n, "metrics": {k: contrast(a[k][mask], b[k][mask], bootstrap) for k in a if k != "language_sensitive"}}
            if early_arrays:
                ea, eb = early_arrays[cell]
                result["late_minus_early_parallel_effect"][stratum + "/" + "/".join(cell)] = {
                    k: contrast((eb[k]-ea[k])[mask], (b[k]-a[k])[mask], bootstrap)
                    for k in ea if k != "language_sensitive" and k in a}
        for context, question in sorted({c[:2] for c in cells}):
            en_a, en_b = arrays[(context, question, "en")]
            de_a, de_b = arrays[(context, question, "de")]
            result["answer_language_interactions"][stratum + "/" + context + "/" + question] = {
                k: contrast((de_a[k]-en_a[k])[mask], (de_b[k]-en_b[k])[mask], bootstrap)
                for k in en_a if k != "language_sensitive"}
    result["limits"] = "Exploratory uncorrected CIs; paragraph-pair resampling, one training seed. Fact retrieval, not logical reasoning. Five demonstrations differ with answer language; English frame; no-context target retains demonstration contexts. Raw LL question binding cancels additive answer priors but not question-type guessing."
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"pairs": len(ids), "output": str(args.output), "cell_count": len(result["cells"]), "time_interaction": bool(early_arrays)}))


if __name__ == "__main__":
    main()
