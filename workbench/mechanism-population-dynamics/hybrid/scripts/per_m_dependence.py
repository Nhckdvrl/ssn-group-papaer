#!/usr/bin/env python3
"""Memory / conv dependence of word assembly by number of pieces m (existing results only; no new runs).
Prints split-minus-last-only delta per m (2..6) at layers 2, 4, 8 for none / memory-off / conv-off in
OLMo-Hybrid (E196), Qwen3.5-4B and Granite-4.0-H (E198), Falcon-H1 (E205, E209 mean ablation)."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"


def row_a(d, layer):
    i = d["layers"].index(layer)
    return [d[f"split{m}"]["acc"][i] - d[f"last{m}"]["acc"][i] for m in (2, 3, 4, 5, 6)]


def row_b(d, layer):
    i = d["layers"].index(layer); a = d["acc"]
    return [a[f"split{m}"][i] - a[f"last{m}"][i] for m in (2, 3, 4, 5, 6)]


def main():
    e196 = json.loads((R / "e196/r1_all_conditions.json").read_text())
    qh = json.loads((R / "e198/r1_qwen35.json").read_text()); gh = json.loads((R / "e198/r1_granite_h.json").read_text())
    fh = json.loads((R / "e205/r1_falcon_h1.json").read_text()); fh9 = json.loads((R / "e209/fh3_summary.json").read_text())
    fmt = lambda xs: " ".join(f"{x:+.2f}" for x in xs)
    for layer in (2, 4, 8):
        print(f"== layer {layer} (m = 2..6): none | memory off | conv off")
        for name, d in (("OLMo-Hybrid (GDN)", e196), ("Qwen3.5-4B (GDN)", qh), ("Granite-4.0-H (Mamba-2)", gh)):
            print(f"{name:24s} {fmt(row_a(d['none'], layer))} | {fmt(row_a(d['nomem'], layer))} | {fmt(row_a(d['noconv'], layer))}")
        print(f"{'Falcon-H1 (Mamba-2)':24s} {fmt(row_b(fh['none'], layer))} | {fmt(row_b(fh['nomem'], layer))} | {fmt(row_b(fh9['mean'], layer))}")


if __name__ == "__main__":
    main()
