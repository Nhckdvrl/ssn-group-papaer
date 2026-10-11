"""CPU-only source-trainer label/image sentinel on real first-shard rows.

This is a pre-GPU correctness gate, not a training outcome or policy score.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pyarrow as pa
from datasets import Dataset
from transformers import AutoProcessor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--processor", type=Path, required=True)
    parser.add_argument("--trainer-source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("e12_llava_trainer", args.trainer_source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import pinned trainer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    shard = args.root / "llava_arrow/data-00000-of-00054.arrow"
    with pa.memory_map(str(shard), "r") as source:
        table = pa.ipc.open_stream(source).read_all()
    ds = Dataset(table)
    processor = AutoProcessor.from_pretrained(str(args.processor))
    processor.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    processor.tokenizer.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    wrapped = module.Llava15Dataset(ds, processor)

    # Fixed positions span the shard and do not depend on any policy outcome.
    positions = [0, 1, 2, 15, 127, 511, 1023, 2047, 4095, 8191, len(ds) - 1]
    rows = []
    for index in positions:
        item = wrapped[index]
        labels = item["labels"]
        supervised = labels[labels != -100]
        rows.append({
            "position": index,
            "id": ds[index]["id"],
            "input_tokens": int(item["input_ids"].numel()),
            "supervised_tokens": int(supervised.numel()),
            "last_supervised_token_is_eos": bool(
                supervised.numel() and int(supervised[-1]) == processor.tokenizer.eos_token_id
            ),
            "pixel_values_shape": list(item["pixel_values"].shape),
        })
    report = {
        "pinned_trainer_source": str(args.trainer_source),
        "pinned_arrow_shard": str(shard),
        "sample_count": len(rows),
        "all_rows_have_supervised_tokens": all(x["supervised_tokens"] > 0 for x in rows),
        "all_rows_end_supervision_with_eos": all(x["last_supervised_token_is_eos"] for x in rows),
        "rows": rows,
        "qualification": "Only 11 fixed first-shard rows; full selected-subset mask audit remains required.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
