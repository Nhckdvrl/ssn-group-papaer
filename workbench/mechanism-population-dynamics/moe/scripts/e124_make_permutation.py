#!/usr/bin/env python3
"""Build a CPU-only E124 synchronized expert-permutation calibration checkpoint."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch

SOURCE = Path("/tmp/xiang-moe-20261025/e123_seed0/checkpoint.pt")
OUTPUT_DIR = Path("/tmp/xiang-moe-20261025/e124_permuted_seed0")
OUTPUT = OUTPUT_DIR / "checkpoint.pt"
MANIFEST = Path(__file__).resolve().parents[1] / "results/e124/permutation_control.json"
PERMUTATION_SEED = 124
N_EXPERTS = 64
EXPERT_MATRICES = ("gate_proj.weight", "up_proj.weight", "down_proj.weight")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite completed control checkpoint: {OUTPUT}")
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    source_size = SOURCE.stat().st_size
    source_sha = sha256_file(SOURCE)

    # This is our local E123 training checkpoint. weights_only=False is needed
    # because its saved NumPy RNG state is not in PyTorch's weights-only allowlist.
    source = torch.load(SOURCE, map_location="cpu", mmap=True, weights_only=False)
    if not isinstance(source, dict) or "moe" not in source:
        raise ValueError("Expected a training checkpoint with a moe state dict")
    src_moe = source["moe"]
    expected_keys = {"block.gate.weight"}
    expected_keys.update(
        f"block.experts.{expert}.{matrix}"
        for expert in range(N_EXPERTS)
        for matrix in EXPERT_MATRICES
    )
    if len(src_moe) != 193 or set(src_moe) != expected_keys:
        raise ValueError(f"Expected exactly 193 MoE tensors; got {len(src_moe)}")
    gate = src_moe["block.gate.weight"]
    if gate.ndim != 2 or gate.shape[0] != N_EXPERTS:
        raise ValueError(f"Unexpected router shape: {tuple(gate.shape)}")

    new_to_old = np.random.default_rng(PERMUTATION_SEED).permutation(N_EXPERTS).astype(int).tolist()
    perm = torch.as_tensor(new_to_old, dtype=torch.long, device="cpu")
    new_moe = {"block.gate.weight": gate.index_select(0, perm).contiguous()}
    for new_expert, old_expert in enumerate(new_to_old):
        for matrix in EXPERT_MATRICES:
            new_moe[f"block.experts.{new_expert}.{matrix}"] = src_moe[
                f"block.experts.{old_expert}.{matrix}"
            ]
    if len(new_moe) != 193:
        raise AssertionError(f"Reordered MoE tensor count is {len(new_moe)}, expected 193")

    source_config_hash = source.get("config_hash")
    if not isinstance(source_config_hash, str):
        raise ValueError("Source checkpoint lacks string config_hash")
    frozen_sample_hash = source.get("frozen_sample_hash")
    if not isinstance(frozen_sample_hash, str):
        raise ValueError("Source checkpoint lacks frozen_sample_hash")
    step = int(source["step"])

    transform = {
        "kind": "e124-known-synchronized-expert-permutation",
        "source_checkpoint_sha256": source_sha,
        "source_config_hash": source_config_hash,
        "permutation_seed": PERMUTATION_SEED,
        "new_to_old": new_to_old,
        "router_operation": "new_gate_weight = old_gate_weight[new_to_old]",
        "expert_operation": "new_expert[e] = old_expert[new_to_old[e]] for gate_proj/up_proj/down_proj",
        "is_independent_training_seed": False,
    }
    transform_sha = hashlib.sha256(
        json.dumps(transform, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    control = {
        "type": "known_synchronized_expert_permutation",
        "permutation_seed": PERMUTATION_SEED,
        "new_to_old": new_to_old,
        "transform_sha256": transform_sha,
        "independent_training_seed": False,
    }
    # Keep only model parameters and the training-step/sample provenance needed
    # for calibration. Optimizer and RNG state are deliberately not copied.
    output = {
        "schema": 1,
        "step": step,
        "moe": new_moe,
        "config_hash": transform_sha,
        "source_config_hash": source_config_hash,
        "frozen_sample_hash": frozen_sample_hash,
        "calibration_control": control,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    partial = OUTPUT.with_suffix(".pt.partial")
    partial.unlink(missing_ok=True)
    with partial.open("wb") as f:
        torch.save(output, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(partial, OUTPUT)

    # Reopen the artifact and verify all 193 tensor correspondences exactly.
    check = torch.load(OUTPUT, map_location="cpu", mmap=True, weights_only=False)
    if set(check["moe"]) != expected_keys or len(check["moe"]) != 193:
        raise AssertionError("Output checkpoint does not contain exactly the 193 MoE tensors")
    if not torch.equal(check["moe"]["block.gate.weight"], gate.index_select(0, perm)):
        raise AssertionError("Router rows do not match the synchronized permutation")
    for new_expert, old_expert in enumerate(new_to_old):
        for matrix in EXPERT_MATRICES:
            actual = check["moe"][f"block.experts.{new_expert}.{matrix}"]
            expected = src_moe[f"block.experts.{old_expert}.{matrix}"]
            if not torch.equal(actual, expected):
                raise AssertionError(f"Expert tensor mismatch for new {new_expert}, old {old_expert}, {matrix}")
    if check["step"] != step or check["frozen_sample_hash"] != frozen_sample_hash:
        raise AssertionError("Output step/frozen sample hash differs from source")
    if check["source_config_hash"] != source_config_hash or check["config_hash"] != transform_sha:
        raise AssertionError("Output source/control config hashes are not recorded correctly")
    if "optimizer" in check:
        raise AssertionError("Optimizer state must not be copied to the calibration control")

    result = {
        **transform,
        "source_checkpoint": str(SOURCE),
        "source_checkpoint_size_bytes": source_size,
        "output_checkpoint": str(OUTPUT),
        "output_checkpoint_size_bytes": OUTPUT.stat().st_size,
        "output_checkpoint_sha256": sha256_file(OUTPUT),
        "config_hash": transform_sha,
        "frozen_sample_hash": frozen_sample_hash,
        "step": step,
        "moe_tensor_count": len(new_moe),
        "verified_exact_tensor_equalities": 193,
        "optimizer_copied": False,
        "cuda_used": False,
        "provenance_path": str(OUTPUT_DIR / "provenance.json"),
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    provenance = {
        "source": {
            "checkpoint": str(SOURCE),
            "checkpoint_sha256": source_sha,
            "config_hash": source_config_hash,
            "args": {"seed": 0, "order_seed": 0},
            "step": step,
            "frozen_sample_hash": frozen_sample_hash,
        },
        "output": {
            "checkpoint": str(OUTPUT),
            "checkpoint_sha256": result["output_checkpoint_sha256"],
            "config_hash": transform_sha,
            "source_config_hash": source_config_hash,
            "step": step,
        },
        "calibration_control": control,
        "independent_training_seed": False,
    }
    (OUTPUT_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_size_bytes": source_size,
        "output_size_bytes": result["output_checkpoint_size_bytes"],
        "source_sha256": source_sha,
        "output_sha256": result["output_checkpoint_sha256"],
        "transform_sha256": transform_sha,
        "verified_exact_tensor_equalities": 193,
        "manifest": str(MANIFEST),
        "provenance": str(OUTPUT_DIR / "provenance.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
