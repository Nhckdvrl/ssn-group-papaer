#!/usr/bin/env python3
"""E218 B2: static anatomy of short-conv weights in every layer (no intervention).
For each depthwise causal conv weight [C, 1, K] (last tap = current position), per layer:
  neighbour energy share = sum_{j<K-1} w_j^2 / sum_j w_j^2 (median over channels), and mean |w| per tap.
Reads only conv tensors from safetensors (or a .bin when no safetensors exist).
Usage: conv_anatomy.py OUT_JSON NAME=MODEL_DIR [NAME=MODEL_DIR ...]"""
import json
import re
import sys
from pathlib import Path

import torch


def conv_tensors(mdir):
    mdir = Path(mdir)
    sts = sorted(mdir.glob("*.safetensors"))
    out = {}
    if sts:
        from safetensors import safe_open
        for f in sts:
            with safe_open(str(f), framework="pt") as fh:
                for k in fh.keys():
                    if "conv" in k and k.endswith("weight"):
                        t = fh.get_tensor(k)
                        if t.dim() == 3 and t.shape[1] == 1 and t.shape[-1] > 1:
                            out[k] = t.float()
    else:
        sd = torch.load(mdir / "pytorch_model.bin", map_location="cpu", weights_only=True, mmap=True)
        for k, t in sd.items():
            if "conv" in k and k.endswith("weight") and t.dim() == 3 and t.shape[1] == 1 and t.shape[-1] > 1:
                out[k] = t.float()
    return out


def main():
    res = {}
    for arg in sys.argv[2:]:
        name, d = arg.split("=", 1)
        rows = []
        for k, w in conv_tensors(d).items():
            m = re.search(r"layers\.(\d+)\.", k)
            if not m:
                continue
            w = w[:, 0]  # [C, K]
            e = w.pow(2)
            share = (e[:, :-1].sum(-1) / e.sum(-1).clamp_min(1e-12)).median().item()
            rows.append({"layer": int(m.group(1)), "key": k, "channels": w.shape[0], "neighbour_energy_share": round(share, 4),
                         "absmean_by_tap": [round(x, 4) for x in w.abs().mean(0).tolist()]})
        rows.sort(key=lambda r: r["layer"])
        res[name] = rows
        sh = [r["neighbour_energy_share"] for r in rows]
        print(f"{name:14s} layers={len(rows):2d} share L0-2: {' '.join(f'{x:.2f}' for x in sh[:3])} | mid: {sh[len(sh)//2]:.2f} | last: {sh[-1]:.2f} | taps L0: {rows[0]['absmean_by_tap']}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(res))


if __name__ == "__main__":
    main()
