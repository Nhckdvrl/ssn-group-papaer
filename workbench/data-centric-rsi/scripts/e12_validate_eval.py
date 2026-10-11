"""Validate all eight Curation-Bench VLMEvalKit scores before E12 comparison.

VLMEvalKit catches per-dataset failures and can exit 0 with only partial
results. This script follows the fixed benchmark scoring table and source
DataFrame schemas; it refuses to compute an aggregate from missing tasks.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


BENCHMARKS = (
    "HallusionBench", "LLaVABench", "MMBench", "MMMU_DEV_VAL",
    "MMStar", "MMVet", "MathVista_MINI", "OCRBench",
)
MAX_SCORE = {name: (1000.0 if name == "OCRBench" else 100.0) for name in BENCHMARKS}


def rows_from_vlmeval_table(value: dict) -> list[dict]:
    """Undo run.py's conditional DataFrame transpose followed by to_dict()."""
    if not value or not all(isinstance(v, dict) for v in value.values()):
        raise ValueError("Expected a VLMEvalKit DataFrame dictionary")
    if all(str(k).isdigit() for k in value):
        return [value[k] for k in sorted(value, key=lambda x: int(x))]
    indices = sorted({str(i) for col in value.values() for i in col}, key=lambda x: int(x) if x.isdigit() else x)
    return [{field: col.get(index) for field, col in value.items()} for index in indices]


def one_row(rows: list[dict], key: str, expected: str) -> dict:
    matches = [row for row in rows if str(row.get(key, "")).lower() == expected.lower()]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {key}={expected!r} row, found {len(matches)}")
    return matches[0]


def numeric(value) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"Invalid benchmark score: {value!r}")
    return result


def raw_score(name: str, value: dict) -> tuple[float, str]:
    if name == "OCRBench":
        return numeric(value["Final Score"]), "Final Score"
    rows = rows_from_vlmeval_table(value)
    if name == "HallusionBench":
        row = one_row(rows, "split", "Overall")
        return sum(numeric(row[k]) for k in ("aAcc", "fAcc", "qAcc")) / 3.0, "Overall mean(aAcc,fAcc,qAcc)"
    if name == "LLaVABench":
        return numeric(one_row(rows, "split", "overall")["Relative Score (main)"]), "overall Relative Score (main)"
    if name == "MMVet":
        return numeric(one_row(rows, "Category", "Overall")["acc"]), "Overall acc"
    if name == "MathVista_MINI":
        return numeric(one_row(rows, "Task&Skill", "Overall")["acc"]), "Overall acc"
    split = {"MMBench": "dev", "MMMU_DEV_VAL": "validation", "MMStar": "none"}[name]
    # ImageMCQDataset.report_acc returns proportions rather than percentages.
    return 100.0 * numeric(one_row(rows, "split", split)["Overall"]), f"{split} Overall × 100"


def validate_results(results: dict, model_key: str = "llava-1.5-7b-hf") -> dict:
    if set(results) != {model_key}:
        raise ValueError(f"Expected only {model_key!r}; found {sorted(results)}")
    model_results = results[model_key]
    if set(model_results) != set(BENCHMARKS):
        missing = sorted(set(BENCHMARKS) - set(model_results))
        unexpected = sorted(set(model_results) - set(BENCHMARKS))
        raise ValueError(f"Incomplete E12 evaluation: missing={missing}, unexpected={unexpected}")
    details = {}
    for name in BENCHMARKS:
        raw, field = raw_score(name, model_results[name])
        details[name] = {"raw": raw, "max": MAX_SCORE[name], "normalized": raw / MAX_SCORE[name], "field": field}
    aggregate = sum(v["normalized"] for v in details.values()) / len(BENCHMARKS)
    return {"model_key": model_key, "benchmarks": details, "accuracy_0_to_1": aggregate, "accuracy_percent": 100.0 * aggregate}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stdout-log", type=Path)
    parser.add_argument("--stderr-log", type=Path)
    args = parser.parse_args()
    for path in (args.stdout_log, args.stderr_log):
        if path is not None:
            log = path.read_text(errors="replace")
            if "will use exact matching for evaluation" in log:
                raise RuntimeError(f"Judge fallback changed the scoring protocol: {path}")
    result = validate_results(json.loads(args.results.read_text()))
    result["source_results"] = str(args.results)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
