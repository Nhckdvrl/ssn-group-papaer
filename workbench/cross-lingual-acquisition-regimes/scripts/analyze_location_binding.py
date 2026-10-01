"""Validate measurable native controls before interpreting cross-language effects."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    meta = json.loads(path.with_suffix(".meta.json").read_text())
    assert len(rows) == meta["expected_items"] == 1920
    items = [{k: v for k, v in row.items() if k not in ["scores", "control_scores"]} for row in rows]
    assert hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == meta["items_sha256"]
    assert all(np.isfinite(s["ll"]) and s["tokens"] > 0 for r in rows for field in ["scores", "control_scores"] for s in r[field])
    groups = defaultdict(list)
    for row in rows:
        groups[(row["context_language"], row["answer_language"])].append(row)
    result = {}
    for cell, cell_rows in groups.items():
        for method in ["raw", "token_norm", "char_norm", "query_adjusted"]:
            pairs = defaultdict(dict)
            for row in cell_rows:
                raw = np.array([s["ll"] for s in row["scores"]])
                control = np.array([s["ll"] for s in row["control_scores"]])
                values = {"raw": raw,
                          "token_norm": raw / [s["tokens"] for s in row["scores"]],
                          "char_norm": raw / [len(option.lstrip()) for option in row["options"]],
                          "query_adjusted": raw-control}[method]
                gold = row["gold"]
                pairs[row["pair_id"]][row["swap"]] = {
                    "correct": int(np.argmax(values) == gold), "margin": float(values[gold]-values[1-gold]),
                    "control_correct": int(np.argmax(control) == gold),
                    "control": control.tolist(), "target_first": row["target"] == row["fact_order"]}
            assert len(pairs) == 240 and all(sorted(pair) == [0, 1] for pair in pairs.values())
            assert all(pair[0]["control"] == pair[1]["control"] for pair in pairs.values())
            assert not any(pair[0]["control_correct"] and pair[1]["control_correct"] for pair in pairs.values())
            all_items = [r for pair in pairs.values() for r in pair.values()]
            response = [pair[0]["margin"]+pair[1]["margin"] for pair in pairs.values()]
            result["/".join((method, "->".join(cell)))] = {
                "accuracy_pct": float(np.mean([r["correct"] for r in all_items])*100),
                "strict_pair_pct": float(np.mean([pair[0]["correct"] and pair[1]["correct"] for pair in pairs.values()])*100),
                "positive_binding_response_pct": float(np.mean(np.array(response)>0)*100),
                "mean_binding_response": float(np.mean(response)),
                "target_first_accuracy_pct": float(np.mean([r["correct"] for r in all_items if r["target_first"]])*100),
                "target_last_accuracy_pct": float(np.mean([r["correct"] for r in all_items if not r["target_first"]])*100),
                "control_accuracy_pct": float(np.mean([r["control_correct"] for r in all_items])*100),
                "control_strict_pair_pct": 0.0}
    return {"metadata": meta, "cells": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=[42])
    args = parser.parse_args()
    models = {}
    for condition in ["noswitch", "switch", "par"]:
        for seed in args.seeds:
            models[f"{condition}/{seed}"] = read(ROOT / "artifacts/p3" / f"macaroni_{condition}_s{seed}_location.jsonl")
    assert len({r["metadata"]["items_sha256"] for r in models.values()}) == 1
    native_gate = {key: value["cells"]["raw/en->en"]["accuracy_pct"] >= 65 and value["cells"]["raw/en->en"]["strict_pair_pct"] >= 35
                   for key, value in models.items()}
    output = ROOT / "results" / ("p3_location_binding_" + "_".join(map(str, args.seeds)) + ".json")
    result = {"models": models, "native_measurability_gate": native_gate,
              "limits": "Synthetic combinatorial examples share names/locations/template, not independent natural items. Descriptive only; no item-population inference. Role-sensitive copying is not general reasoning. Native gate fixed before scoring."}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "native_gate": native_gate,
        "raw_cells": {key: {k: v for k, v in value["cells"].items() if k.startswith("raw/")} for key, value in models.items()}}, indent=2))


if __name__ == "__main__":
    main()
