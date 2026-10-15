"""E94b: what did the two natural loss spikes change in the weights? (no training)

Usage: e94b_spike_delta.py -> prints and writes results/e94/spike_delta.json
Pairs of consecutive Pythia-410M checkpoints (2000 steps apart): spike windows (seed3 74k->76k, seed4 122k->124k)
against normal windows (seed3 72k->74k, seed4 120k->122k, seed1 74k->76k).
Per window: relative change ||dW|| / ||W|| for each tensor, grouped by module type and layer; per attention head
(Q, K, V rows and output-projection columns); and the fraction of each matrix update's energy in its top singular
direction (low-rank, coherent updates vs diffuse ones).
"""
import json

import numpy as np
import torch

import mp_common as mc

S = mc.CACHE / "ckpt" / "spike"
PAIRS = {"seed3 spike 74k-76k": ("pythia-410m-seed3_74000", "pythia-410m-seed3_76000"),
         "seed3 normal 72k-74k": ("pythia-410m-seed3_72000", "pythia-410m-seed3_74000"),
         "seed4 spike 122k-124k": ("pythia-410m-seed4_122000", "pythia-410m-seed4_124000"),
         "seed4 normal 120k-122k": ("pythia-410m-seed4_120000", "pythia-410m-seed4_122000"),
         "seed1 normal 74k-76k": ("pythia-410m-seed1_74000", "pythia-410m-seed1_76000")}
H, DH = 16, 64


def load(d):
    return torch.load(S / d / "pytorch_model.bin", map_location="cpu")


def top_sv(d, iters=30):
    """Largest singular value by power iteration (full SVDs of all 410M matrices are too slow on CPU)."""
    v = torch.randn(d.shape[1], generator=torch.Generator().manual_seed(0))
    for _ in range(iters):
        v = d.T @ (d @ v)
        v = v / v.norm()
    return (d @ v).norm().item()


def group(name):
    if "embed_in" in name:
        return "embed_in"
    if "embed_out" in name:
        return "embed_out"
    if "layernorm" in name or "final_layer_norm" in name:
        return "layernorm"
    if "query_key_value" in name:
        return "qkv"
    if "attention.dense" in name:
        return "attn_out"
    if "dense_h_to_4h" in name:
        return "mlp_in"
    if "dense_4h_to_h" in name:
        return "mlp_out"
    return "other"


def main():
    out = {}
    for label, (a, b) in PAIRS.items():
        A, B = load(a), load(b)
        g, per_layer, heads, rank1 = {}, {}, [], {}
        for n, w in A.items():
            if not torch.is_floating_point(w) or n not in B:
                continue
            w, w2 = w.float(), B[n].float()
            d = w2 - w
            k = group(n)
            num, den = g.get(k, (0.0, 0.0))
            g[k] = (num + d.pow(2).sum().item(), den + w.pow(2).sum().item())
            if ".layers." in n:
                l = int(n.split(".layers.")[1].split(".")[0])
                num, den = per_layer.get((k, l), (0.0, 0.0))
                per_layer[(k, l)] = (num + d.pow(2).sum().item(), den + w.pow(2).sum().item())
                if k == "qkv" and n.endswith("weight"):
                    dv, wv = d.view(H, 3, DH, -1), w.view(H, 3, DH, -1)
                    for h in range(H):
                        for j, part in enumerate("QKV"):
                            heads.append((l, h, part, (dv[h, j].norm() / wv[h, j].norm()).item()))
                if k == "attn_out" and n.endswith("weight"):
                    for h in range(H):
                        heads.append((l, h, "O", (d[:, h * DH:(h + 1) * DH].norm() / w[:, h * DH:(h + 1) * DH].norm()).item()))
            if d.dim() == 2 and min(d.shape) > 1:
                rank1[n] = top_sv(d) ** 2 / d.pow(2).sum().item()
        grp = {k: round(np.sqrt(x / y), 6) for k, (x, y) in g.items()}
        top_heads = sorted(heads, key=lambda r: -r[3])[:12]
        lay = {}
        for (k, l), (x, y) in per_layer.items():
            lay.setdefault(k, [0.0] * 24)[l] = round(np.sqrt(x / y), 6)
        r1 = {k: round(float(np.median([v for n, v in rank1.items() if group(n) == k])), 4) for k in set(map(group, rank1))}
        r1_max = sorted(rank1.items(), key=lambda kv: -kv[1])[:6]
        out[label] = {"group_rel_change": grp, "per_layer": lay, "top_heads": [f"{l}.{h}{p}:{v:.4f}" for l, h, p, v in top_heads],
                      "rank1_energy_median": r1, "rank1_energy_top": [(n, round(v, 3)) for n, v in r1_max]}
        print(f"\n== {label}", flush=True)
        print("  rel change by group:", grp)
        print("  rank-1 energy (median by group):", r1)
        print("  most coherent matrices:", out[label]["rank1_energy_top"])
        print("  top heads:", out[label]["top_heads"], flush=True)
        del A, B
    (mc.RESULTS / "e94").mkdir(parents=True, exist_ok=True)
    (mc.RESULTS / "e94" / "spike_delta.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
