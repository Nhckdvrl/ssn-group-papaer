"""Read-only assets and native, order-preserving interventions for E144/E145.

No training entry point, H/Y training cache, downloads, or old experiment ledger.
The experiment cards fix inputs, sources, metrics, controls and resource limits.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock

import e123_frozen_moe as base

WB = Path(__file__).resolve().parents[1]
ARCHIVE = Path.home() / "mechpop_cache"
RECIPE = ARCHIVE / "e135_cache_recipe"
METRICS = ("nll", "ref_to_variant_kl", "variant_to_ref_kl", "ref_top1_agreement")


def sha(path):
    return base.sha256_file(path)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base.write_json(path, value)


def immutable_json(path, value):
    path = Path(path)
    if path.exists():
        if read(path) != value:
            raise ValueError(f"Refusing to replace frozen design: {path}")
    else:
        write(path, value)


def tensor_hash(state):
    """Byte-for-byte compatible with E124/E135 historical tensor hashes."""
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(f"{name}|{tuple(value.shape)}|{value.dtype}".encode())
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def code_proof():
    names = ("e144145_common.py", "e144145_run.py", "e144145_analyze.py", "e144145_test.py", "e123_frozen_moe.py")
    return {name: sha(WB / "scripts" / name) for name in names}


def emit(event, **kw):
    base.emit(event, **kw)


def prepare(root):
    """CPU-only identity checks and extraction, before any held model readout."""
    root.mkdir(parents=True, exist_ok=True)
    recipe = read(RECIPE / "manifest.json")
    if sha(RECIPE / "manifest.json") != "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43":
        raise ValueError("Original E135 recipe changed")
    input_proofs = {}
    for name in ("held_keys.npy", "held_tokens.npy", "train_tokens.npy"):
        path = RECIPE / name
        expected = recipe["files"][name]
        if path.stat().st_size != expected["size_bytes"] or sha(path) != expected["sha256"]:
            raise ValueError(f"Recipe input differs: {name}")
        input_proofs[name] = {"path": str(path), **expected}
    data_manifest = Path(recipe["data"])
    if sha(data_manifest) != recipe["prepare_proof"]["data_manifest_sha256"]:
        raise ValueError("Original token data manifest differs")
    data = base.TokenData(data_manifest, 512)
    windows = data.fixed_windows("held", 512, 91023)
    keys = np.load(RECIPE / "held_keys.npy", allow_pickle=False).reshape(-1, 2)
    tokens = np.load(RECIPE / "held_tokens.npy", allow_pickle=False).reshape(-1, 513)
    if base.digest_json(windows) != recipe["held_window_hash"] or not np.array_equal(keys, windows):
        raise ValueError("Old held window population differs")
    candidates = []
    for old, (fi, wi) in enumerate(windows):
        actual = data.window("held", fi, wi)
        if not np.array_equal(actual, tokens[old]):
            raise ValueError("Archived tokens differ from original source")
        row = {"manifest_sha256": recipe["prepare_proof"]["data_manifest_sha256"],
               "old_sequence_index": old, "source": data.files["held"][fi]["source"],
               "file_id": data.files["held"][fi]["file_id"], "window": wi,
               "token_sha256": hashlib.sha256(actual.astype("<i8").tobytes()).hexdigest()}
        canonical = json.dumps(row, sort_keys=True, separators=(",", ":"))
        row["selection_digest"] = hashlib.sha256(("e144-held-v1\n" + canonical).encode()).hexdigest()
        candidates.append(row)
    chosen = sorted(candidates, key=lambda x: (x["selection_digest"], x["old_sequence_index"]))[:64]
    selected = {"schema": "E144-held-v1", "original_population": 512, "selection": "SHA256(e144-held-v1\\n + sorted compact JSON), ascending; old index tie-break",
                "seq_len": 512, "batch_size": 16, "count": 64, "held_window_hash": recipe["held_window_hash"],
                "recipe_manifest_sha256": sha(RECIPE / "manifest.json"), "token_sha_dtype": "little endian int64, all 513 IDs",
                "attention_mask": {"shape": [64, 512], "constant": 1}, "loss_mask": {"shape": [64, 512], "constant": 1},
                "target_alignment": "inputs=tokens[:,:-1]; labels=tokens[:,1:]", "rows": [
                    {**row, "sequence": i, "batch": i // 16, "batch_row": i % 16, "positions": 512} for i, row in enumerate(chosen)]}
    immutable_json(WB / "results/e144/selected.json", selected)
    bases = np.random.default_rng(144).integers(0, 3, size=(8, 64))
    source_maps = {"schema": "E144-sources-v1", "seed": 144, "student_order": ["F0", "F1", "F2"], "independent_MC_units": 8,
                   "bases": bases.tolist(), "maps": [{"name": f"mix{b:02d}_{shift}", "base": b, "shift": shift,
                      "sources": ((row + shift) % 3).tolist()} for b, row in enumerate(bases) for shift in range(3)]}
    immutable_json(WB / "results/e144/source_maps.json", source_maps)
    old_r = read(WB / "results/e139/readout.json")
    old_s = read(WB / "results/e142/readout.json")
    sources = {}
    for name, group, seed, path, proof in [
        *[(f"F{s}", "F", s, ARCHIVE / (f"e138_fixed_cohort/seed{s}/checkpoint.pt" if s != 1 else "e136_assignment_oracle/checkpoint.pt"),
           old_r["condition_proofs"]["fixed"][f"seed{s}"]["final"]) for s in (0, 1, 2)],
        ("A", "A", 1, ARCHIVE / "e135_student_33554432/checkpoint.pt", old_r["condition_proofs"]["free"]["seed1"]["final"]),
        *[(f"R{s}", "R", s, ARCHIVE / f"e139_matched_free_cohort/seed{s}/checkpoint.pt", old_r["condition_proofs"]["free"][f"seed{s}"]["final"]) for s in (0, 2)],
        *[(f"S{s}", "S", s, ARCHIVE / f"e142_shared_random_router/seed{s}/checkpoint.pt", old_s["condition_proofs"][f"seed{s}"]["final"]) for s in (0, 2)]]:
        digest = sha(path)
        if digest != proof["checkpoint_sha256"]:
            raise ValueError(f"Checkpoint file differs: {name}")
        cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
        state = cp["student_state"]
        digest_tensor = tensor_hash(state)
        if cp["step"] != 4096 or digest_tensor != proof["full_tensor_sha256"] or cp["cache_manifest_sha256"] != sha(RECIPE / "manifest.json"):
            raise ValueError(f"Checkpoint endpoint/tensor/cache differs: {name}")
        if any(t.dtype != torch.float32 for t in state.values()):
            raise ValueError("Original trained students must retain FP32 storage")
        gate_hash = tensor_hash({"block.gate.weight": state["block.gate.weight"]})
        if gate_hash != proof["gate_tensor_sha256"]:
            raise ValueError(f"Gate identity differs: {name}")
        target = root / "sources" / f"{name}.pt"
        target.parent.mkdir(exist_ok=True)
        # A weight-only NVMe extraction is recoverable from the durable original.
        if target.exists():
            if tensor_hash(torch.load(target, mmap=True, map_location="cpu", weights_only=True)) != digest_tensor:
                raise ValueError(f"Staged state differs: {name}")
        else:
            temporary = target.with_suffix(".partial")
            torch.save(state, temporary)
            temporary.replace(target)
        if group in ("R", "S"):
            cal = (old_r["components"]["free_final_calibration"] if group == "R" else old_s["components"]["final_calibration"])
            mapping = cal["maps"][f"seed{seed}"]["source_to_seed1"]
        else:
            mapping = list(range(64))
        if sorted(mapping) != list(range(64)):
            raise ValueError("Map must be bijective")
        sources[name] = {"path": str(path), "checkpoint_sha256": digest, "tensor_sha256": digest_tensor,
                         "gate_tensor_sha256": gate_hash, "step": cp["step"], "seed": seed, "group": group,
                         "schema": cp.get("schema"), "config_hash": cp["config_hash"], "staged_state": str(target),
                         "staged_sha256": sha(target), "source_to_common": mapping}
        emit("source_verified", name=name, checkpoint_sha256=digest)
        del state, cp
    if len({sources[f"F{s}"]["gate_tensor_sha256"] for s in (0, 1, 2)}) != 1:
        raise ValueError("F cohort gate not identical")
    model_root = Path(recipe["model"])
    model_proofs = {}
    for name, proof in recipe["prepare_proof"]["assets"]["assets"].items():
        if "public_native_Hcal" in name:
            continue
        path = model_root / name
        if path.stat().st_size != proof["size_bytes"] or sha(path) != proof["sha256"]:
            raise ValueError(f"Public model asset differs: {name}")
        model_proofs[name] = {"path": str(path), "sha256": proof["sha256"], "size_bytes": proof["size_bytes"]}
    result = {"schema": "E144145-assets-v1", "status": "CPU_verified_no_model_readouts", "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=WB, text=True).strip(), "source_sha256": code_proof(), "sources": sources,
        "model": str(model_root), "model_files": model_proofs, "input_proofs": input_proofs,
        "teacher_block_tensor_sha256": recipe["teacher_block_tensor_sha256"], "teacher_prefix_sample_hash": recipe["teacher_prefix_hash"],
        "selected_sha256": sha(WB / "results/e144/selected.json"), "source_maps_sha256": sha(WB / "results/e144/source_maps.json"),
        "old_readouts": {f"e{e}": sha(WB / f"results/e{e}/readout.json") for e in (139, 142)},
        "original_held_files": len(data.provenance["held"]),
        "selected_file_clusters": len({(r["source"], r["file_id"]) for r in chosen}),
        "scope": "Previously used held inputs; conditional finite cohorts, not seed-population inference. No training."}
    write(root / "assets.json", result)
    write(WB / "results/e144/asset_preflight.json", result)
    return result


def block_from_state(state, config, device):
    with torch.device("meta"):
        block = OlmoeSparseMoeBlock(config)
    block.load_state_dict({k.removeprefix("block."): v for k, v in state.items()}, strict=True, assign=True)
    return block.to(device).eval().requires_grad_(False)


class Assembled(nn.Module):
    """One legal gate/bank; physical gate traversal preserves native tie/order.

    Gate rows stay physical. source_to_common maps those rows to shared expert
    slots; bank_sources[e] is the complete expert at shared slot e. This also
    preserves native summation order on jointly permuted donor diagonals.
    """
    def __init__(self, gate_block, source_to_common, bank_sources):
        super().__init__()
        self.gate = gate_block.gate
        self.top_k, self.num_experts = gate_block.top_k, gate_block.num_experts
        self.norm_topk_prob = gate_block.norm_topk_prob
        self.mapping = tuple(int(i) for i in source_to_common)
        if sorted(self.mapping) != list(range(self.num_experts)) or len(bank_sources) != self.num_experts:
            raise ValueError("Invalid complete legal bank")
        self.experts = nn.ModuleList(bank_sources)

    def forward(self, hidden_states):
        shape = hidden_states.shape
        hidden = hidden_states.view(-1, shape[-1])
        logits = self.gate(hidden)
        weight, selected = F.softmax(logits, dim=1, dtype=torch.float32).topk(self.top_k, dim=-1)
        if self.norm_topk_prob:
            weight = weight / weight.sum(-1, keepdim=True)
        weight = weight.to(hidden.dtype)
        output = torch.zeros_like(hidden)
        mask = F.one_hot(selected, num_classes=self.num_experts).permute(2, 1, 0)
        for physical, common in enumerate(self.mapping):
            slot, row = torch.where(mask[physical])
            value = self.experts[common](hidden[None, row].reshape(-1, shape[-1])) * weight[row, slot, None]
            output.index_add_(0, row, value.to(hidden.dtype))
        return output.reshape(shape), logits


class FixedOutput(nn.Module):
    def __init__(self, output, gate):
        super().__init__()
        self.output, self.gate = output, gate

    def forward(self, hidden):
        if self.output.shape != hidden.shape or self.output.dtype != hidden.dtype:
            raise ValueError("Full-sequence fixed output dtype/shape mismatch")
        return self.output, self.gate(hidden.reshape(-1, hidden.shape[-1]))


def common_experts(block, mapping):
    inverse = np.argsort(mapping)
    return [block.experts[int(j)] for j in inverse]


@torch.no_grad()
def trace(block, hidden):
    """Observe actual selected-subset BF16 products without re-querying experts."""
    flat = hidden.reshape(-1, hidden.shape[-1])
    n, dim = flat.shape
    gate = block.gate
    ctx, components, handles = {}, {}, []
    mapping = block.mapping if isinstance(block, Assembled) else tuple(range(block.num_experts))
    inverse = np.argsort(mapping)

    def gate_hook(module, inputs, logits):
        weights, selected = F.softmax(logits, dim=1, dtype=torch.float32).topk(block.top_k, dim=-1)
        if block.norm_topk_prob:
            weights = weights / weights.sum(-1, keepdim=True)
        ctx.update(weights=weights.to(hidden.dtype), selected=selected, logits=logits,
                   mask=F.one_hot(selected, num_classes=block.num_experts).permute(2, 1, 0))
    handles.append(gate.register_forward_hook(gate_hook))
    for common in range(block.num_experts):
        expert = block.experts[common]
        physical = int(inverse[common])

        def expert_hook(module, inputs, value, common=common, physical=physical):
            slot, row = torch.where(ctx["mask"][physical])
            expected = flat[None, row].reshape(-1, dim)
            if not torch.equal(inputs[0], expected):
                raise ValueError("Selected expert subbatch/order differs from native contract")
            comp = (value * ctx["weights"][row, slot, None]).to(hidden.dtype)
            components[common] = {"row": row, "component": comp.detach().clone()}
        handles.append(expert.register_forward_hook(expert_hook))
    try:
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16, enabled=hidden.dtype == torch.bfloat16):
            output, logits = block(hidden)
    finally:
        for handle in handles:
            handle.remove()
    if len(components) != block.num_experts or not torch.equal(logits, ctx["logits"]):
        raise ValueError("Native tuple or complete component trace differs")
    sum64 = torch.zeros((n, dim), device=hidden.device, dtype=torch.float64)
    for e in range(block.num_experts):
        row = components[e]
        sum64.index_add_(0, row["row"], row["component"].double())
    mapped_selected = torch.tensor(mapping, device=hidden.device)[ctx["selected"]]
    q = torch.zeros((n, block.num_experts), device=hidden.device, dtype=torch.float32)
    q.scatter_(1, mapped_selected, ctx["weights"].float())
    return {"native": output.detach(), "sum64": sum64.reshape_as(output), "components": components,
            "selected": mapped_selected, "weights": ctx["weights"], "q": q, "logits": logits}


def cohort(traces):
    """Same common gate and coordinates; finite 1/3 moments, no n-1 correction."""
    first = traces[0]
    sums = torch.stack([t["sum64"] for t in traces])
    mu = sums.mean(0)
    v = (sums - mu).square().sum(-1).mean(0)
    c = torch.zeros(first["native"].numel() // first["native"].shape[-1], dtype=torch.float64, device=mu.device)
    for e in sorted(first["components"]):
        ref = first["components"][e]["row"]
        if any(not torch.equal(t["components"][e]["row"], ref) for t in traces):
            raise ValueError("Common-gate cohort supports differ")
        values = torch.stack([t["components"][e]["component"].double() for t in traces])
        c.index_add_(0, ref, (values - values.mean(0)).square().sum(-1).mean(0))
    return {"C": c.reshape_as(v), "V": v, "C_minus_V": c.reshape_as(v) - v}, mu


def cohort_general(traces):
    """Same coordinate maps, possibly different native supports, one expert at a time."""
    sums = torch.stack([t["sum64"] for t in traces])
    mu = sums.mean(0)
    v = (sums-mu).square().sum(-1).mean(0)
    n, dim = traces[0]["q"].shape[0], mu.shape[-1]
    count = len(traces)
    c = torch.zeros(n, device=mu.device, dtype=torch.float64)
    for e in sorted(traces[0]["components"]):
        rows = torch.unique(torch.cat([t["components"][e]["row"] for t in traces]), sorted=True)
        total = torch.zeros((len(rows), dim), device=mu.device, dtype=torch.float64)
        energy = torch.zeros(len(rows), device=mu.device, dtype=torch.float64)
        for t in traces:
            comp = t["components"][e]
            indices = torch.searchsorted(rows, comp["row"])
            values = comp["component"].double()
            total.index_add_(0, indices, values)
            energy.index_add_(0, indices, values.square().sum(-1))
        c.index_add_(0, rows, energy/count - total.square().sum(-1)/(count*count))
    c = c.reshape_as(v)
    return {"C": c, "V": v, "C_minus_V": c-v}, mu


def prediction_metrics(reference_logp, variant_logp, target):
    if reference_logp.shape != variant_logp.shape or reference_logp.shape[:-1] != target.shape:
        raise ValueError("Metric shape mismatch")
    nll = -variant_logp.gather(-1, target[..., None]).squeeze(-1)
    delta = reference_logp - variant_logp
    forward = (reference_logp.exp() * delta).sum(-1)
    reverse = (variant_logp.exp() * -delta).sum(-1)
    agree = (reference_logp.argmax(-1) == variant_logp.argmax(-1)).float()
    result = torch.stack((nll, forward, reverse, agree), -1)
    if not torch.isfinite(result).all():
        raise ArithmeticError("Nonfinite full-vocabulary metrics")
    return result


class Budget:
    """One process owns each experiment ledger; failed attempts remain charged."""
    def __init__(self, path, experiment, phase):
        self.path, self.experiment, self.phase = Path(path), experiment, phase
        self.limit = {"e144": 10800, "e145": 7200}[experiment]

    def __enter__(self):
        self.state = read(self.path) if self.path.exists() else {"experiment": self.experiment, "limit_gpu_seconds": self.limit, "attempts": []}
        if self.state["experiment"] != self.experiment or any(x.get("status") == "running" for x in self.state["attempts"]):
            raise RuntimeError("Concurrent or unfinished attempt must be audited before reuse")
        self.start = time.monotonic()
        self.prior = sum(x["gpu_seconds"] for x in self.state["attempts"])
        self.row = {"phase": self.phase, "host": socket.gethostname(), "pid": os.getpid(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "gpu_seconds": 0., "status": "running"}
        self.state["attempts"].append(self.row)
        self.check()
        return self

    def check(self):
        self.row["gpu_seconds"] = time.monotonic() - self.start
        write(self.path, self.state)
        if self.prior + self.row["gpu_seconds"] >= self.limit:
            raise TimeoutError("Registered experiment resource package exhausted")

    def __exit__(self, kind, error, tb):
        self.row.update(gpu_seconds=time.monotonic() - self.start, status="complete" if error is None else "failed",
                        error=None if error is None else f"{type(error).__name__}: {error}")
        write(self.path, self.state)


def gpu_lock(physical):
    import fcntl
    handle = open(f"/tmp/xiang-mechpop-gpu{physical}.lock", "a+")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    rows = subprocess.check_output(["nvidia-smi", "-i", str(physical), "--query-compute-apps=pid", "--format=csv,noheader"], text=True).strip()
    if rows:
        raise RuntimeError(f"GPU {physical} occupied: {rows}")
    if torch.cuda.is_initialized():
        raise RuntimeError("GPU initialized before lock/preflight")
    if os.environ.get("CUDA_VISIBLE_DEVICES") != str(physical):
        raise RuntimeError("Set CUDA_VISIBLE_DEVICES before importing torch/transformers")
    expected = subprocess.check_output(["nvidia-smi", "-i", str(physical), "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip().removeprefix("GPU-")
    actual = str(torch.cuda.get_device_properties(0).uuid).removeprefix("GPU-")
    if actual != expected:
        raise RuntimeError(f"Physical device UUID mismatch: {actual} != {expected}")
    return handle
