"""Descriptive joint correctness screen; covariance is not a causal adjustment."""
import hashlib
import json
from pathlib import Path

import numpy as np

from analyze_probe import read

ROOT = Path(__file__).resolve().parents[1]


def summarize(path, languages):
    data, meta = read(path)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    items = [{k: v for k, v in row.items() if k not in ["scores", "prior_scores"]} for row in rows]
    assert hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == meta["items_sha256"]
    assert all(np.isfinite(s["ll"]) for r in rows for field in ["scores", "prior_scores"] for s in r[field])
    result = {}
    for method in sorted({k[0] for k in data}):
        left = data[(method, f"{languages[0]}->{languages[0]}")]
        right = data[(method, f"{languages[1]}->{languages[1]}")]
        ids = sorted(left)
        assert ids == sorted(right)
        x = np.array([left[i]["correct"] for i in ids], dtype=float)
        y = np.array([right[i]["correct"] for i in ids], dtype=float)
        result[method] = {
            "n": len(ids), "left_accuracy_pct": float(x.mean()*100),
            "right_accuracy_pct": float(y.mean()*100),
            "both_correct_pct": float((x*y).mean()*100),
            "both_wrong_pct": float(((1-x)*(1-y)).mean()*100),
            "left_only_pct": float((x*(1-y)).mean()*100),
            "right_only_pct": float(((1-x)*y).mean()*100),
            "disagreement_pct": float((x != y).mean()*100),
            "oracle_any_correct_pct": float(np.maximum(x, y).mean()*100),
            "correctness_covariance": float((x*y).mean()-x.mean()*y.mean()),
        }
    return result, meta


def main():
    result = {"models": {}, "contrasts": {}}
    for condition in ["noswitch", "switch", "par"]:
        for seed in [42, 43, 44]:
            key = f"macaroni/{condition}/{seed}"
            values, meta = summarize(ROOT / "artifacts/p3" / f"macaroni_{condition}_s{seed}_xstory.jsonl", ["en", "zh"])
            result["models"][key] = {"values": values, "metadata": meta}
    for condition in ["no", "multi", "nonadj", "distributed"]:
        values, meta = summarize(ROOT / "artifacts/p1" / f"jgp_{condition}_xstory_fp32_160k.jsonl", ["id", "zh"])
        result["models"][f"jgp/{condition}"] = {"values": values, "metadata": meta}
    pairs = [(f"macaroni/{condition}/{seed}", f"macaroni/noswitch/{seed}")
             for condition in ["switch", "par"] for seed in [42, 43, 44]]
    pairs += [("jgp/distributed", "jgp/nonadj"), ("jgp/multi", "jgp/no")]
    for treated, control in pairs:
        a, b = result["models"][treated], result["models"][control]
        assert a["metadata"]["items_sha256"] == b["metadata"]["items_sha256"]
        result["contrasts"][f"{treated} minus {control}"] = {
            method: {metric: a["values"][method][metric]-b["values"][method][metric]
                     for metric in a["values"][method] if metric != "n"}
            for method in a["values"]}
    result["limits"] = "Descriptive exploratory screen, no CIs. Binary alternatives only. Covariance subtracts independent marginals but not common item difficulty. No causal claim; family content/exposure confounds and three-seed release limits remain."
    output = ROOT / "results/p3_joint_errors.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "contrasts": result["contrasts"]}, indent=2))


if __name__ == "__main__":
    main()
