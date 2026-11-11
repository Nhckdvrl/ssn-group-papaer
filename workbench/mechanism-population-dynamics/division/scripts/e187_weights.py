"""E187 step 1 (CPU, read-only): dump the weights needed for the copied-layer analysis of Qwen3-30B-A3B (Instruct or
Base) from the HF cache with lazy safetensors reads.
  - full: router W [48,128,2048], post-attn / input RMSNorm gains, q/k/v/o, q_norm/k_norm
  - expert sketch (card E187 "读数 2"): gate/up rows 0:128 (of 768 neurons), down rows 0:342 (of 2048 outputs),
    concatenated per expert -> [128, 786944] fp16 per layer
  - sketch-error check: gate rows 640:768 for layers 8, 20, 32, 9 (second disjoint neuron subset)
  REDUCED sketch (deviation logged in the card, 11-09 22:50: NFS throughput fell to ~6 MB/s):
    sketchS_L<l>.npy = gate rows 0:32, up rows 0:32, down rows 0:85 -> [128, 196352]; layers that already have the
    full sketch are sliced locally (identical entries); alt check = gate rows 640:672.
usage: e187_weights.py <instruct|base>   ->  ~/mechpop_cache/e187/w_<key>/"""
import json, os, sys, glob, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
from safetensors import safe_open

key = sys.argv[1]
hf = {"instruct": "Qwen/Qwen3-30B-A3B", "base": "Qwen/Qwen3-30B-A3B-Base"}[key]
snap = glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{hf.replace('/', '--')}/snapshots/*"))[0]
idx = json.load(open(f"{snap}/model.safetensors.index.json"))["weight_map"]
out = os.path.expanduser(f"~/mechpop_cache/e187/w_{key}")
os.makedirs(out, exist_ok=True)
L, E = 48, 128
FH = {}


def fh(name):
    f = idx[name]
    if f not in FH:
        FH[f] = safe_open(f"{snap}/{f}", "pt")
    return FH[f]


def get(name, sl=None):
    h = fh(name)
    if sl is None:
        return h.get_tensor(name)
    return h.get_slice(name)[sl[0]:sl[1]]


# open all files once in the main thread (safe_open handles are then read concurrently)
for n in idx:
    fh(n)
t0 = time.time()
SKIP_SMALL = os.path.exists(f"{out}/attn.npz")
small = {k: [] for k in ["gate", "post_ln", "in_ln", "q_norm", "k_norm"]}
attn = {p: [] for p in "qkvo"}
for l in range(0 if not SKIP_SMALL else L):
    pre = f"model.layers.{l}."
    small["gate"].append(get(pre + "mlp.gate.weight").float().numpy())
    small["post_ln"].append(get(pre + "post_attention_layernorm.weight").float().numpy())
    small["in_ln"].append(get(pre + "input_layernorm.weight").float().numpy())
    small["q_norm"].append(get(pre + "self_attn.q_norm.weight").float().numpy())
    small["k_norm"].append(get(pre + "self_attn.k_norm.weight").float().numpy())
    for p in "qkvo":
        attn[p].append(get(pre + f"self_attn.{p}_proj.weight").half().numpy())
if not SKIP_SMALL:
    np.savez(f"{out}/small.npz", **{k: np.stack(v) for k, v in small.items()})
    np.savez(f"{out}/attn.npz", **{p: np.stack(v) for p, v in attn.items()})
print("small+attn done", round(time.time() - t0), "s", flush=True)


def expert(l, e):
    pre = f"model.layers.{l}.mlp.experts.{e}."
    g = get(pre + "gate_proj.weight", (0, 32)).half().flatten()
    u = get(pre + "up_proj.weight", (0, 32)).half().flatten()
    d = get(pre + "down_proj.weight", (0, 85)).half().flatten()
    return torch.cat([g, u, d]).numpy()


with ThreadPoolExecutor(12) as ex:
    for l in range(L):
        fn = f"{out}/sketchS_L{l:02d}.npy"
        if os.path.exists(fn):
            continue
        full = f"{out}/sketch_L{l:02d}.npy"
        if os.path.exists(full):                       # slice the full sketch: gate 0:128x2048, up next, down 0:342x768
            F = np.load(full, mmap_mode="r")
            S = np.concatenate([F[:, :65536], F[:, 262144:262144 + 65536], F[:, 524288:524288 + 85 * 768]], 1)
        else:
            S = np.stack(list(ex.map(lambda e: expert(l, e), range(E))))
        np.save(fn, np.ascontiguousarray(S))
        print("layer", l, S.shape, round(time.time() - t0), "s", flush=True)
    alt = {}
    for l in (8, 9, 20, 32):
        alt[f"L{l}"] = np.stack(list(ex.map(
            lambda e: get(f"model.layers.{l}.mlp.experts.{e}.gate_proj.weight", (640, 672)).half().flatten().numpy(),
            range(E))))
    np.savez(f"{out}/sketchS_alt_gate640.npz", **alt)
print("done", round(time.time() - t0), "s")
