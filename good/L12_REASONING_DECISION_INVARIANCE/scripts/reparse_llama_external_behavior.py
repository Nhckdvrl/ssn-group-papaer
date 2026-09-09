#!/usr/bin/env python3
"""Apply the audited E14 terminal-answer parser to existing raw generations."""

import json
import os
from pathlib import Path

from run_llama_external_behavior import CONFIG, ROOT, parse_deepseek_final_choice
from run_model import parse_choice


def main():
    out = ROOT / CONFIG["result_dir"]
    for spec in CONFIG["models"]:
        path = out / f"{spec['branch']}.jsonl"
        temporary = path.with_suffix(".jsonl.tmp")
        with path.open() as source, temporary.open("w") as target:
            for line in source:
                row = json.loads(line)
                if spec["requires_closed_think"]:
                    shown, rule = parse_deepseek_final_choice(row["continuation"])
                else:
                    shown = parse_choice(row["continuation"])
                    rule = "direct_first_label" if shown is not None else "invalid"
                underlying = shown
                if shown is not None and row["order"] == "ba":
                    underlying = "B" if shown == "A" else "A"
                row.update({
                    "shown_choice": shown,
                    "underlying_choice": underlying,
                    "valid": shown is not None,
                    "choice_parser": rule,
                })
                target.write(json.dumps(row) + "\n")
        os.replace(temporary, path)


if __name__ == "__main__":
    main()
