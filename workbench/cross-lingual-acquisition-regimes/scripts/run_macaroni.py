"""Score released seed families in one process without changing the frozen assay."""
import argparse
import gc
import hashlib
import json
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer

import frozen_probe

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["noswitch", "switch", "par"], required=True)
    parser.add_argument("--context-control", choices=["original", "shuffled"], default="original")
    args = parser.parse_args()
    items, _ = frozen_probe.build_items("xstorycloze", ["en", "zh"], 1511, 0)
    fingerprints = set()
    for seed in [42, 43, 44]:
        manifest_path = ROOT / "artifacts" / "model_manifests" / f"macaroni__{args.condition}__s{seed}.json"
        manifest = json.loads(manifest_path.read_text())
        path = Path(manifest["path"])
        fingerprints.add(hashlib.sha256((path / "tokenizer.json").read_bytes()).hexdigest())
        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        config = json.loads((path / "config.json").read_text())
        context_limit = config.get("n_positions", config.get("max_position_embeddings"))
        lengths = [len(tokenizer.encode(item["context"] + option, add_special_tokens=False)) for item in items for option in item["options"]]
        assert max(lengths) <= context_limit, (seed, max(lengths), context_limit)
        print(json.dumps({"condition": args.condition, "seed": seed, "max_tokens": max(lengths), "context_limit": context_limit, "tokenizer_sha256": next(iter(fingerprints))}), flush=True)
        del tokenizer
    assert len(fingerprints) == 1, "Tokenizer differs across seeds"
    for seed in [42, 43, 44]:
        suffix = "_shuffled" if args.context_control == "shuffled" else ""
        sys.argv = ["frozen_probe.py", "--manifest", str(ROOT / "artifacts" / "model_manifests" / f"macaroni__{args.condition}__s{seed}.json"),
                    "--task", "xstorycloze", "--languages", "en", "zh", "--limit", "1511", "--batch", "16",
                    "--compute-dtype", "fp32", "--weight-dtype", "fp32", "--context-control", args.context_control,
                    "--output", str(ROOT / "artifacts" / "p3" / f"macaroni_{args.condition}_s{seed}_xstory{suffix}.jsonl")]
        frozen_probe.main()
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
