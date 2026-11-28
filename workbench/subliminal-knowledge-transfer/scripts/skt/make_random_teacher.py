#!/usr/bin/env python3
"""Norm-matched random LoRA teacher (E06 / E03 control).

Reads a trained PEFT adapter, and for every LoRA module draws Gaussian A', B' of the same
shapes, rescaled so that ||B'A'||_F equals the trained ||BA||_F of that module (the alpha/r
scale is shared, so Delta-W norms match exactly). Writes a PEFT adapter with the same
adapter_config, so it loads and merges exactly like the trained teacher.

    python make_random_teacher.py --src RUN/ep9 --out RUN_rand --seed 1
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import torch
from safetensors.torch import load_file, save_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    src, out = Path(args.src), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sd = load_file(str(src / "adapter_model.safetensors"))
    g = torch.Generator().manual_seed(args.seed)
    new, report = {}, []
    for k in sorted(sd):
        if "lora_A" not in k:
            continue
        kb = k.replace("lora_A", "lora_B")
        A, B = sd[k].float(), sd[kb].float()
        target = (B @ A).norm().item()
        A2 = torch.randn(A.shape, generator=g)
        B2 = torch.randn(B.shape, generator=g)
        cur = (B2 @ A2).norm().item()
        s = (target / cur) ** 0.5 if cur > 0 else 0.0
        A2, B2 = A2 * s, B2 * s
        new[k], new[kb] = A2.to(sd[k].dtype), B2.to(sd[kb].dtype)
        report.append({"module": k.replace(".lora_A.weight", ""), "norm_BA": target, "norm_rand": (B2 @ A2).norm().item()})
    for k in sd:
        new.setdefault(k, sd[k])
    save_file(new, str(out / "adapter_model.safetensors"))
    shutil.copy(src / "adapter_config.json", out / "adapter_config.json")
    (out / "norm_report.json").write_text(json.dumps({"src": str(src), "seed": args.seed, "modules": report}, indent=1))
    print(f"{len(report)} modules; total ||BA|| {sum(r['norm_BA'] for r in report):.3f}")


if __name__ == "__main__":
    main()
