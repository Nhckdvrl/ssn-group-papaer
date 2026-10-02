"""Check that an E12 student updated trainable weights and kept vision frozen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from safetensors import safe_open


KEYS = (
    "language_model.model.layers.0.self_attn.q_proj.weight",
    "multi_modal_projector.linear_1.weight",
    "vision_tower.vision_model.embeddings.patch_embedding.weight",
)


def tensor_at(model_dir: Path, key: str) -> torch.Tensor:
    index_path = model_dir / "model.safetensors.index.json"
    if index_path.exists():
        weight_map = json.loads(index_path.read_text())["weight_map"]
        filename = weight_map[key]
    else:
        filename = "model.safetensors"
    path = model_dir / filename
    with safe_open(path, framework="pt", device="cpu") as handle:
        return handle.get_tensor(key).clone()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report: dict[str, object] = {
        "parent": str(args.parent), "student": str(args.student),
        "delta_reference": "Parent cast to student dtype before subtraction; raw dtype-conversion differences are reported separately.",
        "tensors": {},
    }
    for key in KEYS:
        before = tensor_at(args.parent, key)
        after = tensor_at(args.student, key)
        if before.shape != after.shape:
            raise RuntimeError(f"Shape changed for {key}: {before.shape} vs {after.shape}")
        parent_cast = before.to(dtype=after.dtype)
        delta = after.float() - parent_cast.float()
        raw_delta = after.float() - before.float()
        report["tensors"][key] = {
            "shape": list(before.shape),
            "parent_dtype": str(before.dtype),
            "student_dtype": str(after.dtype),
            "exact_equal": bool(torch.equal(before, after)),
            "equal_after_parent_cast": bool(torch.equal(parent_cast, after)),
            "changed_elements": int(torch.count_nonzero(delta).item()),
            "max_abs_delta": float(delta.abs().max().item()),
            "mean_abs_delta": float(delta.abs().mean().item()),
            "raw_changed_elements_before_parent_cast": int(torch.count_nonzero(raw_delta).item()),
        }
    tensors = report["tensors"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    if tensors[KEYS[0]]["equal_after_parent_cast"] or tensors[KEYS[1]]["equal_after_parent_cast"]:
        raise RuntimeError("A sampled trainable tensor did not change beyond dtype conversion")
    if not tensors[KEYS[2]]["equal_after_parent_cast"]:
        raise RuntimeError("The sampled frozen vision tensor changed beyond dtype conversion")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
