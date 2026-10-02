"""CPU-only sentinel for Curation-Bench LLaVA assistant-token supervision."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image
from transformers import AutoProcessor


class OneExample:
    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> dict:
        if index != 0:
            raise IndexError(index)
        return {
            "images": Image.new("RGB", (336, 336), (20, 40, 200)),
            "texts": [{"user": "What color is the square?", "assistant": "The square is blue."}],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processor", type=Path, required=True)
    parser.add_argument("--trainer-source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("e12_vendor_train_llava15", args.trainer_source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import trainer source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    processor = AutoProcessor.from_pretrained(str(args.processor))
    processor.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    processor.tokenizer.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    row = module.Llava15Dataset(OneExample(), processor)[0]
    mask = row["labels"] != -100
    supervised = processor.tokenizer.decode(row["input_ids"][mask], skip_special_tokens=False)
    report = {
        "processor_path": str(args.processor),
        "trainer_source": str(args.trainer_source),
        "input_tokens": int(row["input_ids"].numel()),
        "supervised_tokens": int(mask.sum().item()),
        "supervised_text": supervised,
        "assistant_only": "blue" in supervised and "What color" not in supervised,
        "eos_supervised": "</s>" in supervised,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["assistant_only"] or not report["eos_supervised"]:
        raise SystemExit("Assistant labels are missing or include the prompt")


if __name__ == "__main__":
    main()
