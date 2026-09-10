#!/usr/bin/env python3
"""Merge E21 state-intervention shards and validate exact row coverage."""

import argparse
import json

from cpc18_form_evidence_common import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-shards", type=int, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "configs/cpc18_selective_state.json").read_text())
    output = ROOT / config["result_dir"]
    rows = []
    for index in range(args.num_shards):
        path = output / f"raw.shard{index}of{args.num_shards}.jsonl"
        rows.extend(json.loads(line) for line in path.open())
    keys = [
        (row["problem"], row["target_form"], row["target_evidence"],
         row["donor_form"], row["donor_evidence"], row["layer"])
        for row in rows
    ]
    expected = (
        config["n_selected_base_decisions"] * 4 * 4 * len(config["scan_layers"])
    )
    if len(rows) != expected or len(keys) != len(set(keys)):
        raise ValueError("E21 shard coverage or uniqueness failure")
    rows.sort(key=lambda row: (
        row["problem"], row["target_form"], row["target_evidence"],
        row["donor_form"], row["donor_evidence"], row["layer"],
    ))
    with (output / "raw.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    (output / "scan.json").write_text(json.dumps({
        "model": config["model"],
        "n_base_decisions": config["n_selected_base_decisions"],
        "scan_layers": config["scan_layers"],
        "n_rows": len(rows),
        "merged_shards": args.num_shards,
    }, indent=2) + "\n")
    print(json.dumps({"rows": len(rows), "duplicate_keys": 0}, indent=2))


if __name__ == "__main__":
    main()
