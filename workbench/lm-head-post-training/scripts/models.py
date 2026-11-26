"""Checkpoint registry. Weights live on node-local disk (see README 资产位置); never in git."""
import json
import os
from pathlib import Path

MODEL_ROOT = Path(os.environ.get("LMHEAD_MODELS", "/tmp/xiang_lmhead/models"))

MODELS = {
    "qwen3-8b-base": "Qwen__Qwen3-8B-Base",
    "qwen3-8b": "Qwen__Qwen3-8B",
    "olmo3-base": "allenai__Olmo-3-1025-7B",
    "olmo3-think-sft": "allenai__Olmo-3-7B-Think-SFT",
    "olmo3-think-dpo": "allenai__Olmo-3-7B-Think-DPO",
    "olmo3-think": "allenai__Olmo-3-7B-Think",
    "olmo3-rlzero-math": "allenai__Olmo-3-7B-RL-Zero-Math",
    "olmo3-instruct-sft": "allenai__Olmo-3-7B-Instruct-SFT",
}

# (parent, child, post-training stage) — adjacent pairs only; parents per model cards (to verify in E01 card).
PAIRS = {
    "qwen-post__self": ("qwen3-8b", "qwen3-8b", "control: identical checkpoint"),
    "qwen-base__post": ("qwen3-8b-base", "qwen3-8b", "multi-stage (SFT+RL+fusion), opaque"),
    "olmo-base__thinksft": ("olmo3-base", "olmo3-think-sft", "SFT"),
    "olmo-thinksft__dpo": ("olmo3-think-sft", "olmo3-think-dpo", "DPO"),
    "olmo-dpo__think": ("olmo3-think-dpo", "olmo3-think", "RLVR"),
    "olmo-base__rlzero": ("olmo3-base", "olmo3-rlzero-math", "RLVR (zero, math)"),
    "olmo-base__instsft": ("olmo3-base", "olmo3-instruct-sft", "SFT"),
}


def path(name: str) -> Path:
    return MODEL_ROOT / MODELS[name]


def revision(name: str) -> str:
    f = path(name) / "REVISION"
    return f.read_text().strip() if f.exists() else "unknown"


def tensor_index(name: str) -> dict:
    """tensor name -> shard file."""
    p = path(name)
    idx = p / "model.safetensors.index.json"
    if idx.exists():
        return {k: str(p / v) for k, v in json.loads(idx.read_text())["weight_map"].items()}
    return {k: str(p / "model.safetensors") for k in _keys(p / "model.safetensors")}


def _keys(f):
    from safetensors import safe_open
    with safe_open(f, "pt") as fh:
        return list(fh.keys())
