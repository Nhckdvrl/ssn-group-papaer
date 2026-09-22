"""Extract the pretrained gate matrices for L36/L44 straight from the shards.

The offline EPO gate must start from the PRETRAINED router -- starting from a
random init would answer a different question entirely. Reading two 128x2048
matrices out of the safetensors index costs seconds and avoids a 7-minute load
of the full 30B model.
"""
import json, sys
import torch
from huggingface_hub import hf_hub_download
from safetensors import safe_open

MODEL = "Qwen/Qwen3-30B-A3B"
LAYERS = [36, 44]

idx = json.load(open(hf_hub_download(MODEL, "model.safetensors.index.json")))["weight_map"]
out = {}
for l in LAYERS:
    key = f"model.layers.{l}.mlp.gate.weight"
    shard = idx[key]
    with safe_open(hf_hub_download(MODEL, shard), framework="pt") as f:
        out[str(l)] = f.get_tensor(key).float()
    print(f"L{l}: {tuple(out[str(l)].shape)}  |W|={out[str(l)].norm():.3f}")
torch.save(out, "results/e06_base_gates.pt")
print("wrote results/e06_base_gates.pt")
