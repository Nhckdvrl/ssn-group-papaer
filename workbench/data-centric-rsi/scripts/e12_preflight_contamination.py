"""CPU-only E12 selection and official QA-overlap audit before Arrow materialization.

The result is an early gate, not a substitute for the official audit on the
saved Arrow subsets. Both use the same 10k positions from e12_make_subsets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from e12_index_audit import expected_turns
from e12_make_subsets import POLICIES, hash_lines, policies_from_sources, select_positions


BENCHMARKS = (
    "HallusionBench", "LLaVABench", "MMBench", "MMMU_DEV_VAL",
    "MMStar", "MMVet", "MathVista_MINI", "OCRBench",
)
CB_SRC = Path("/home/xiang/.cache/research/data-centric-rsi/CurationBench/src")
sys.path.insert(0, str(CB_SRC))
from benchmark.tools.contamination import (  # noqa: E402
    EVAL_REGISTRY,
    _load_eval_qa_pairs,
    _make_qa_pair,
    hash_exact_duplicates,
    ngram_near_duplicates,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--policies", nargs="+", choices=POLICIES, default=list(POLICIES))
    args = parser.parse_args()
    original = json.loads((args.root / "llava_json/llava_v1_5_mix665k.json").read_text())
    policy_pools = policies_from_sources(original, args.root)
    eval_dir = args.root / "LMUData"
    eval_pairs = {
        bench: _load_eval_qa_pairs(eval_dir, EVAL_REGISTRY[bench]) for bench in BENCHMARKS
    }
    report = {"seed": args.seed, "benchmarks": list(BENCHMARKS), "policies": {}}
    for policy in args.policies:
        positions = select_positions(original, policy_pools, policy, args.seed)
        submission_pairs = [
            _make_qa_pair(turn["user"], turn["assistant"])
            for i in positions
            for turn in (expected_turns(original[i]) or [])
        ]
        exact = hash_exact_duplicates(submission_pairs, eval_pairs)
        near = ngram_near_duplicates(submission_pairs, eval_pairs)
        status = "clean"
        per_bench = {}
        for bench in BENCHMARKS:
            n = exact[bench]["total_eval_pairs"]
            ec = exact[bench]["exact_matches"]
            nc = near[bench]["near_matches"]
            if ec / n >= 0.10 or nc / n >= 0.20:
                status = "high_risk"
            elif status != "high_risk" and (ec / n >= 0.05 or nc / n >= 0.10):
                status = "warning"
            per_bench[bench] = {"eval_rows": n, "exact": ec, "near": nc}
        report["policies"][policy] = {
            "selected_positions_sha256": hash_lines([str(i) for i in positions]),
            "selected_rows": len(positions),
            "qa_pairs": len(submission_pairs),
            "status": status,
            "per_benchmark": per_bench,
        }
        print(json.dumps({"policy": policy, **report["policies"][policy]}), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
