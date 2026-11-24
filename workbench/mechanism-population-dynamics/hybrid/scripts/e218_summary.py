#!/usr/bin/env python3
"""E218 B1 summary: split-minus-last-only delta per m (2..6) at layers 2, 4, 8 for single-layer switches,
next to the no-switch and all-three-layers rows from existing results (E196, E198, E205, E209).
Layer index convention as r1_summary: position 0 = embedding output (layer -1), position i = output of block i-1.
Usage: e218_summary.py OUT218_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

import torch

R = Path(__file__).resolve().parents[1] / "results"
MS = (2, 3, 4, 5, 6)


def from_spt(d):
    S = torch.load(Path(d) / "S.pt")
    top1 = (S["ranks"] == 0).float().mean(0)  # [L+1, Q]
    acc = {q: top1[:, j].tolist() for j, q in enumerate(S["qnames"])}
    nll = json.loads((Path(d) / "meta.json").read_text()).get("nll_mean")
    return {l: [acc[f"split{m}"][l + 1] - acc[f"last{m}"][l + 1] for m in MS] for l in (2, 4, 8)}, nll


def row_a(d, layer):
    i = d["layers"].index(layer)
    return [d[f"split{m}"]["acc"][i] - d[f"last{m}"]["acc"][i] for m in MS]


def row_b(d, layer):
    i = d["layers"].index(layer); a = d["acc"]
    return [a[f"split{m}"][i] - a[f"last{m}"][i] for m in MS]


def main():
    out218, out_json = Path(sys.argv[1]), Path(sys.argv[2])
    e196 = json.loads((R / "e196/r1_all_conditions.json").read_text())
    qh = json.loads((R / "e198/r1_qwen35.json").read_text()); gh = json.loads((R / "e198/r1_granite_h.json").read_text())
    fh = json.loads((R / "e205/r1_falcon_h1.json").read_text()); fh9 = json.loads((R / "e209/fh3_summary.json").read_text())
    ref = {"H": (e196, row_a, "noconv", "nomem"), "QH": (qh, row_a, "noconv", "nomem"), "GH": (gh, row_a, "noconv", "nomem")}
    res = {}
    fmt = lambda xs: " ".join(f"{x:+.2f}" for x in xs)
    for model in ("H", "QH", "GH", "FH3"):
        res[model] = {}
        for layer in (2, 4, 8):
            if model == "FH3":
                rows = {"none": row_b(fh["none"], layer), "conv_L012": row_b(fh9["mean"], layer), "mem_L012": row_b(fh["nomem"], layer)}
            else:
                d, f, kc, km = ref[model]
                rows = {"none": f(d["none"], layer), "conv_L012": f(d[kc], layer), "mem_L012": f(d[km], layer)}
            for c in ("conv", "mem"):
                for l in (0, 1, 2):
                    p = out218 / f"{model}_{c}_L{l}"
                    if (p / "S.pt").exists():
                        r, nll = from_spt(p)
                        rows[f"{c}_L{l}"] = r[layer]
                        res[model].setdefault("nll", {})[f"{c}_L{l}"] = nll
            res[model][f"layer{layer}"] = rows
            print(f"== {model} layer {layer} (m = 2..6)")
            for k, v in rows.items():
                print(f"  {k:10s} {fmt(v)}")
        print(f"  nll: {res[model].get('nll')}")
    out_json.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
