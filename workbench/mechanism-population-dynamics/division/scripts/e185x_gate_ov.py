"""E185 residual follow-up: how strongly does each layer's router read each attention head's output subspace of the
same layer?  align_h = ||G diag(g_post) U_h||_F^2 / ||G diag(g_post)||_F^2 * d / r_h, U_h = orthonormal basis of the
column space of Wo_h (d x head_dim), r_h = rank; = 1 for a random subspace.  Also the same for the embedding's top PCs.
usage: e185x_gate_ov.py <key> <layers comma>"""
import glob, json, os, sys
import numpy as np, torch
from safetensors import safe_open
key, layers = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
hf = {"olmoe": "allenai/OLMoE-1B-7B-0125-Instruct", "qwen3": "Qwen/Qwen3-30B-A3B"}[key]
snap = glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{hf.replace('/', '--')}/snapshots/*"))[0]
cfg = json.load(open(f"{snap}/config.json")); wm = json.load(open(f"{snap}/model.safetensors.index.json"))["weight_map"]
get = lambda n: safe_open(f"{snap}/{wm[n]}", "pt").get_tensor(n).float()
d = cfg["hidden_size"]; nH = cfg["num_attention_heads"]; hd = cfg.get("head_dim", d // nH)
out = {}
for l in layers:
    p = f"model.layers.{l}."
    G = get(p + "mlp.gate.weight") * get(p + "post_attention_layernorm.weight")[None]
    Wo = get(p + "self_attn.o_proj.weight")          # [d, nH*hd]
    gf = (G ** 2).sum()
    al = []
    for h in range(nH):
        U, S, _ = torch.linalg.svd(Wo[:, h * hd:(h + 1) * hd], full_matrices=False)
        al.append(float(((G @ U) ** 2).sum() / gf * d / U.shape[1]))
    out[l] = al
    print(key, l, "per-head alignment", np.round(al, 2).tolist())
json.dump(out, open(os.path.expanduser(f"~/mechpop_cache/atlas_e185/resid/gateov_{key}.json"), "w"))
