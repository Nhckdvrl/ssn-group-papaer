"""E185 residual follow-up (CPU, read-only): per-layer weight statistics of an HF MoE checkpoint, looking for depth
structure (12-layer period in Qwen3-30B-A3B).  Reads only small tensors + attention projections + router weights.
usage: e185x_weights.py <hf_id> <out.json>"""
import json, os, sys, glob
import numpy as np
import torch
from safetensors import safe_open

hf, out = sys.argv[1], sys.argv[2]
snap = glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{hf.replace('/', '--')}/snapshots/*"))[0]
idx = json.load(open(f"{snap}/model.safetensors.index.json"))["weight_map"]
cfg = json.load(open(f"{snap}/config.json"))
L = cfg["num_hidden_layers"]


def get(name):
    with safe_open(f"{snap}/{idx[name]}", "pt") as f:
        return f.get_tensor(name).float()


def find(l, *cands):
    for c in cands:
        n = f"model.layers.{l}.{c}"
        if n in idx:
            return n
    return None


R = {k: [] for k in ["post_ln_mean", "post_ln_std", "post_ln_max", "post_ln_absmax_ratio", "in_ln_mean", "in_ln_max",
                     "qnorm_mean", "knorm_mean", "q_fro", "k_fro", "v_fro", "o_fro", "gate_fro", "gate_rownorm_cv",
                     "gate_s1_share", "gate_effrank", "gate_meanrow_share"]}
mats = {"q": [], "o": [], "v": [], "post_ln": [], "gate": []}
for l in range(L):
    pl = get(find(l, "post_attention_layernorm.weight"))
    il = get(find(l, "input_layernorm.weight"))
    R["post_ln_mean"].append(pl.mean().item()); R["post_ln_std"].append(pl.std().item())
    R["post_ln_max"].append(pl.abs().max().item()); R["post_ln_absmax_ratio"].append((pl.abs().max() / pl.abs().median()).item())
    R["in_ln_mean"].append(il.mean().item()); R["in_ln_max"].append(il.abs().max().item())
    qn, kn = find(l, "self_attn.q_norm.weight"), find(l, "self_attn.k_norm.weight")
    R["qnorm_mean"].append(get(qn).mean().item() if qn else float("nan"))
    R["knorm_mean"].append(get(kn).mean().item() if kn else float("nan"))
    for p in "qkvo":
        W = get(find(l, f"self_attn.{p}_proj.weight"))
        R[f"{p}_fro"].append(W.norm().item())
        if p in mats:
            mats[p].append(W.flatten())
    G = get(find(l, "mlp.gate.weight", "mlp.router.weight"))
    R["gate_fro"].append(G.norm().item())
    rn = G.norm(dim=1); R["gate_rownorm_cv"].append((rn.std() / rn.mean()).item())
    s = torch.linalg.svdvals(G.double()); s2 = s ** 2 / (s ** 2).sum()
    R["gate_s1_share"].append(s2[0].item()); R["gate_effrank"].append(float(torch.exp(-(s2 * s2.clamp_min(1e-30).log()).sum())))
    R["gate_meanrow_share"].append((G.shape[0] * G.mean(0).norm() ** 2 / G.norm() ** 2).item())
    mats["post_ln"].append(pl); mats["gate"].append(G)
    print("layer", l, flush=True)

# cross-layer similarity matrices (flattened cosine; attention has no permutation freedom except heads)
sim = {}
for p in ["q", "o", "v", "post_ln"]:
    M = torch.stack(mats[p]); M = M / M.norm(dim=1, keepdim=True)
    sim[p] = (M @ M.T).numpy()
# router: permutation-invariant similarity = mean over experts of max |cos| to any expert of the other layer
Gn = [g / g.norm(dim=1, keepdim=True) for g in mats["gate"]]
S = np.zeros((L, L))
for a in range(L):
    for b in range(L):
        S[a, b] = (Gn[a] @ Gn[b].T).abs().max(1).values.mean().item()
sim["gate_match"] = S
lag = {}
for k, M in sim.items():
    lag[k] = {str(t): float(np.mean([M[i, i + t] for i in range(L - t)])) for t in range(1, min(L, 25))}
json.dump({"hf": hf, "L": L, "per_layer": R, "lag_mean_similarity": lag,
           "sim": {k: v.round(4).tolist() for k, v in sim.items()}}, open(out, "w"))
print("done")
