#!/usr/bin/env python3
"""Apply the frozen calibration parser to CPC18 raw generations in place."""

import argparse
import json
from pathlib import Path

from cpc18_common import (
    CONFIG,
    PARSER_VERSION,
    ROOT,
    parse_terminal_choice,
    underlying_choice,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir")
    args = parser.parse_args()
    result_dir = Path(args.result_dir) if args.result_dir else ROOT / CONFIG["result_dir"]
    audit = {"parser_version": PARSER_VERSION, "regimes": {}}
    for spec in CONFIG["regimes"]:
        path = result_dir / "raw" / f"{spec['name']}.jsonl"
        rows = []
        changed = 0
        with path.open() as handle:
            for line in handle:
                row = json.loads(line)
                shown, rule = parse_terminal_choice(
                    row["continuation"], spec["requires_closed_think"]
                )
                changed += int(shown != row.get("shown_choice"))
                row["shown_choice"] = shown
                row["underlying_choice"] = underlying_choice(shown, row["order"])
                row["valid"] = shown is not None
                row["choice_parser"] = rule
                row["parser_version"] = PARSER_VERSION
                rows.append(row)
        with path.open("w") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")
        audit["regimes"][spec["name"]] = {
            "n_rows": len(rows),
            "changed_choice_count": changed,
            "valid_rate": sum(row["valid"] for row in rows) / len(rows),
        }
    (result_dir / "parser_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
