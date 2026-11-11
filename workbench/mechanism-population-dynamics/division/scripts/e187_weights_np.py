"""E187: numpy-only version of the reduced expert sketch dump (e187_weights.py), written 11-10 02:30 because importing
torch from the NFS venv stalled for > 2 h (NFS ~2 s per metadata op).  Identical entries: gate rows 0:32, up rows 0:32,
down rows 0:85 per expert -> sketchS_L<l>.npy [128, 196352] fp16; alt check gate rows 640:672.  bf16 is read from the
safetensors byte layout directly (header JSON + offsets) and widened to fp32 by bit shift.  Layers that already have the
full sketch (sketch_L<l>.npy) are sliced locally.
usage: e187_weights_np.py <instruct|base>"""
import json, os, sys, glob, struct
import numpy as np

key = sys.argv[1]
hf = {"instruct": "Qwen/Qwen3-30B-A3B", "base": "Qwen/Qwen3-30B-A3B-Base"}[key]
snap = glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{hf.replace('/', '--')}/snapshots/*"))[0]
idx = json.load(open(f"{snap}/model.safetensors.index.json"))["weight_map"]
out = os.path.expanduser(f"~/mechpop_cache/e187/w_{key}")
L, E = 48, 128
HDR, FD = {}, {}


def header(f):
    if f not in HDR:
        fd = open(f"{snap}/{f}", "rb")
        n = struct.unpack("<Q", fd.read(8))[0]
        HDR[f] = (json.loads(fd.read(n)), 8 + n); FD[f] = fd
    return HDR[f]


def rows(name, r0, r1):
    f = idx[name]
    h, base = header(f)
    meta = h[name]
    assert meta["dtype"] == "BF16"
    ncol = meta["shape"][1]
    start = base + meta["data_offsets"][0] + r0 * ncol * 2
    fd = FD[f]; fd.seek(start)
    u = np.frombuffer(fd.read((r1 - r0) * ncol * 2), dtype=np.uint16)
    return (u.astype(np.uint32) << 16).view(np.float32).astype(np.float16)


def expert(l, e):
    pre = f"model.layers.{l}.mlp.experts.{e}."
    return np.concatenate([rows(pre + "gate_proj.weight", 0, 32), rows(pre + "up_proj.weight", 0, 32),
                           rows(pre + "down_proj.weight", 0, 85)])


for l in range(L):
    fn = f"{out}/sketchS_L{l:02d}.npy"
    if os.path.exists(fn):
        continue
    full = f"{out}/sketch_L{l:02d}.npy"
    if os.path.exists(full):
        F = np.load(full, mmap_mode="r")
        S = np.concatenate([F[:, :65536], F[:, 262144:262144 + 65536], F[:, 524288:524288 + 85 * 768]], 1)
    else:
        S = np.stack([expert(l, e) for e in range(E)])
    np.save(fn, np.ascontiguousarray(S))
    print("layer", l, S.shape, flush=True)
alt = {f"L{l}": np.stack([rows(f"model.layers.{l}.mlp.experts.{e}.gate_proj.weight", 640, 672) for e in range(E)])
       for l in (8, 9, 20, 32)}
np.savez(f"{out}/sketchS_alt_gate640.npz", **alt)
print("done")
