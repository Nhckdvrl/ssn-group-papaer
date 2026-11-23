#!/usr/bin/env python3
"""Summarise mode_S outputs (S.pt) into per-layer top-1 accuracies and the E194 deltas.
Delta = mean_m(split_m) - mean_m(last_m) over m = 2..5; binding = mean_m(split_m) - mean_m(shuf_m) over m = 3..5.
Layer index convention: position 0 = embedding output (layer -1), position i = output of block i-1.
Usage: r1_summary.py OUT_JSON NAME=DIR [NAME=DIR ...]"""
import json
import sys
from pathlib import Path

import torch


def summary(d):
    S = torch.load(Path(d) / "S.pt")
    top1 = (S["ranks"] == 0).float().mean(0)  # [L+1, Q]
    acc = {q: top1[:, j].tolist() for j, q in enumerate(S["qnames"])}
    mean = lambda kind, ms: [sum(acc[f"{kind}{m}"][l] for m in ms) / len(ms) for l in range(top1.shape[0])]
    sp, la, sh, sp3 = mean("split", (2, 3, 4, 5)), mean("last", (2, 3, 4, 5)), mean("shuf", (3, 4, 5)), mean("split", (3, 4, 5))
    return {"layers": list(range(-1, top1.shape[0] - 1)), "n_items": S["ranks"].shape[0], "acc": acc,
            "delta": [a - b for a, b in zip(sp, la)], "binding": [a - b for a, b in zip(sp3, sh)]}


def main():
    out = {}
    for arg in sys.argv[2:]:
        name, d = arg.split("=", 1)
        out[name] = summary(d)
        dl = out[name]["delta"]
        print(name, " ".join(f"L{l}:{dl[l + 1]:+.2f}" for l in (0, 1, 2, 3, 4, 6, 8, 12, 16, 24) if l + 1 < len(dl)), flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out))


if __name__ == "__main__":
    main()
