"""Frozen E135 asset/bit-cache/tuple contracts and shared four-GPU-hour ledger."""
from __future__ import annotations
import fcntl, os, socket, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
import transformers
import e128_epoch_recovery as epoch
import e130_finalize as assets
from e124_functional_capture import tensor_state_hash

WB, base = assets.WB, epoch.trainer.base
DIMS = {"hidden": 2048, "expert_size": 1024, "experts": 64, "top_k": 8, "seq_len": 512, "batch_size": 16}
FROZEN = {**epoch.FROZEN_SOURCES, "e128_epoch_recovery.py": "754dd5fca994b15839c38eccdd5f9f156dc747bfa3be8a2f2b7f3f61d65b505f",
          "e130_finalize.py": "2b1bed11f13fc0cd2dbb658383b7d9c973da41760e4ec1236e7f18a10a76039f"}


def source_proof():
    actual = {name: assets.sha(WB / "scripts" / name) for name in FROZEN}
    if actual != FROZEN: raise ValueError("Frozen E135 dependency source differs")
    return actual


def bf16_bits(value):
    if value.dtype != torch.bfloat16: raise ValueError(f"Expected actual BF16 output/input, got {value.dtype}")
    return value.detach().contiguous().view(torch.uint16).cpu().numpy().copy()


def from_bits(value, device="cpu"):
    value = np.asarray(value)
    if value.dtype != np.dtype("uint16"): raise ValueError("Expected uint16 BF16 bit storage, not numeric FP16/FP32 conversion")
    return torch.from_numpy(np.array(value, copy=True)).view(torch.bfloat16).to(device)


def atomic_torch_save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True); temporary = path.with_suffix(path.suffix + ".partial")
    torch.save(value, temporary); temporary.replace(path)


def bank_from_state(state, device="cpu", *, fp32=False, dims=None):
    dims = dims or DIMS
    state = {key if key.startswith("block.") else "block." + key: value.float() if fp32 else value for key, value in state.items()}
    with torch.device("meta"): bank = base.TensorMoE(dims["hidden"], dims["expert_size"], dims["experts"], dims["top_k"], .02)
    bank.load_state_dict(state, strict=True, assign=True)
    return bank.to(device)


class PublicStudent(nn.Module):
    def __init__(self, student): super().__init__(); self.student = student
    def forward(self, hidden):
        value = self.student(hidden)
        return value, self.student.last_router_logits


def select_gpu(physical):
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA initialized before physical GPU check")
    if visible and visible != str(physical): raise ValueError("Visible/requested physical GPU differ")
    state = assets.gpu_status(physical)
    if not assets.gpu_free(state): raise RuntimeError(f"Requested GPU unavailable; no fallback: {state}")
    os.environ["CUDA_VISIBLE_DEVICES"] = str(physical)
    return state


class Budget:
    """One host ledger; concurrently active stages are charged additively."""
    def __init__(self, path, phase, limit=14400.):
        self.path, self.phase, self.limit = Path(path), phase, min(float(limit), 14400.)
        self.identity = f"{os.getpid()}-{time.time_ns()}"; self.started = None
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E135", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state["host"] != socket.gethostname(): raise ValueError("GPU ledger is node-local; do not mix hosts/monotonic clocks")
            result = operation(state); assets.write(self.path, state); return result
    def __enter__(self):
        self.started = time.monotonic()
        self.update(lambda state: state["active"].update({self.identity: {"pid": os.getpid(), "phase": self.phase, "started": self.started}}))
        try: self.check()
        except Exception:
            self.update(lambda state: state["active"].pop(self.identity, None))
            raise
        return self
    def check(self):
        consumed = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if consumed >= self.limit: raise TimeoutError("Shared E135 four-GPU-hour budget exhausted; stale active entries remain conservatively charged")
        return consumed
    def __exit__(self, kind, error, traceback):
        elapsed = time.monotonic() - self.started
        def finish(state):
            state["active"].pop(self.identity, None); state["completed_seconds"] += elapsed
            state["runs"].append({"phase": self.phase, "seconds": elapsed, "pid": os.getpid(), "error": None if error is None else str(error)})
        self.update(finish)


def validate_assets(path, *, rehash=True):
    record = assets.read(path)
    if not record or record.get("status") != "ready_on_fvcrc21_local_nvme": raise ValueError("E135 asset stage incomplete")
    if transformers.__version__ != "4.57.6": raise ValueError("Registered HF4.57.6 required")
    verified = {}
    for name, proof in record["assets"].items():
        target = Path(proof["target_path"])
        if target.stat().st_size != proof["size_bytes"]: raise ValueError(f"Asset size differs: {name}")
        if rehash and assets.sha(target) != proof["target_sha256"]: raise ValueError(f"Asset SHA differs: {name}")
        verified[name] = {"path": str(target), "sha256": proof["target_sha256"], "size_bytes": proof["size_bytes"]}
    return record, {"asset_preflight": str(path), "asset_preflight_sha256": assets.sha(path), "assets": verified,
                    "HF": transformers.__version__, "torch": torch.__version__, "source_sha256": source_proof()}


def cache_manifest(root, *, full_hash=False):
    root = Path(root); manifest = assets.read(root / "manifest.json")
    if not manifest or manifest.get("schema") != "E135-native-function-cache-v1" or manifest.get("status") != "complete": raise ValueError("Complete E135 cache required")
    for name, proof in manifest["files"].items():
        path = root / name
        if path.stat().st_size != proof["size_bytes"] or (full_hash and assets.sha(path) != proof["sha256"]): raise ValueError(f"Cache file identity differs: {name}")
    return manifest
