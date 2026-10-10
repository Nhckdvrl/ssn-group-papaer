"""E79 (prototype): where does surviving memory live under a conflicting context?

For each E77 item, run the conflict prompt with the real subject and with the nonce subject (same context answer o',
same candidates). At the final position, decompose the first-token logit difference [o' - o] into direct
contributions of every attention head and every MLP (DLA, final-LN scale frozen from the actual residual), and record
each head's attention mass on the context-answer tokens. Pythia (GPTNeoX) only.

Usage: e79_routes.py --repo EleutherAI/pythia-410m --rev 143000 [--n 1200]
Writes results/e79/<tag>.npz (per-item arrays; local) and <tag>.json (summary).
"""
import argparse
import json

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / "e79"


def run(repo, rev, n):
    from transformers import AutoTokenizer
    torch.set_grad_enabled(False)
    model = mc.load_hf_model(repo, int(rev), dtype=torch.float32, check_manifest=False).cuda()
    model.config._attn_implementation = "eager"
    for layer in model.gpt_neox.layers:
        layer.attention.config._attn_implementation = "eager"
    tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE))
    I = json.loads((mc.RESULTS / "e77" / "items.json").read_text())
    rng = np.random.default_rng(0)
    I = [I[i] for i in sorted(rng.choice(len(I), min(n, len(I)), replace=False))]
    cfg = model.config
    L, H, dh = cfg.num_hidden_layers, cfg.num_attention_heads, cfg.hidden_size // cfg.num_attention_heads
    WU = model.embed_out.weight  # [V, d]
    lnf = model.gpt_neox.final_layer_norm
    cap = {}

    def hook_dense(i):
        def f(mod, inp):
            cap[("z", i)] = inp[0][0, -1].detach()  # concatenated head outputs at final position, [d]
        return f

    def hook_mlp(i):
        def f(mod, inp, out):
            cap[("mlp", i)] = out[0, -1].detach()
        return f
    hs = [lnf.register_forward_pre_hook(lambda mod, inp: cap.__setitem__("pre", inp[0][0, -1].detach()))]
    for i, layer in enumerate(model.gpt_neox.layers):
        hs.append(layer.attention.dense.register_forward_pre_hook(hook_dense(i)))
        hs.append(layer.mlp.register_forward_hook(hook_mlp(i)))
    KEYS = ("real", "nonce", "creal", "cnonce")  # ctx real, ctx nonce, clean real, clean nonce
    rows = {f"{a}_{k}": [] for a in ("head", "mlp", "att", "ld") for k in KEYS}
    rows["keep"] = []
    for x in I:
        o = tok(" " + x["ans"], add_special_tokens=False)["input_ids"][0]
        o2 = tok(" " + x["dist"], add_special_tokens=False)["input_ids"][0]
        if o == o2:
            rows["keep"].append(False)
            for k in rows:
                if k != "keep":
                    rows[k].append(None)
            continue
        du = (WU[o2] - WU[o])  # direction: context answer minus memory answer
        for which, key in (("c1_decl", "real"), ("nonce_c1_decl", "nonce"), ("clean_decl", "creal"), ("nonce_clean", "cnonce")):
            prompt = x["prompts"][which]
            enc = tok(prompt, add_special_tokens=False, return_offsets_mapping=True)
            ids = [tok.eos_token_id] + enc["input_ids"]
            if x["dist"] in prompt:
                c0 = prompt.index(x["dist"])  # first occurrence = the context sentence
                dist_ids = [j + 1 for j, (a, b) in enumerate(enc["offset_mapping"]) if b > c0 and a < c0 + len(x["dist"])]
            else:
                dist_ids = []
            out = model(torch.tensor([ids]).cuda(), output_attentions=True)
            pre = cap["pre"]  # residual entering the final LayerNorm (captured by hook)
            scale = 1.0 / torch.sqrt(pre.var(unbiased=False) + lnf.eps)
            g = lnf.weight * scale  # per-component contributions are centred implicitly via du (differences of rows)
            head = np.zeros((L, H))
            mlp = np.zeros(L)
            att = np.zeros((L, H))
            for i, layer in enumerate(model.gpt_neox.layers):
                z = cap[("z", i)].view(H, dh)
                W = layer.attention.dense.weight.view(-1, H, dh)  # [d, H, dh]
                contrib = torch.einsum("hk,dhk->hd", z, W)  # per-head write to residual (bias excluded)
                head[i] = ((contrib * g) @ du).cpu().numpy()
                mlp[i] = float(((cap[("mlp", i)] * g) @ du))
                if dist_ids:
                    att[i] = out.attentions[i][0, :, -1, dist_ids].sum(-1).cpu().numpy()
            logit = out.logits[0, -1]
            rows[f"head_{key}"].append(head)
            rows[f"mlp_{key}"].append(mlp)
            rows[f"att_{key}"].append(att)
            rows[f"ld_{key}"].append(float(logit[o2] - logit[o]))
        rows["keep"].append(True)
    for h in hs:
        h.remove()
    keep = np.array(rows["keep"])
    arr = {k: np.stack([v for v, kk in zip(rows[k], keep) if kk]) for k in rows if k != "keep"}
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{repo.split('/')[-1]}__{rev}"
    idx = np.array([i for i, kk in enumerate(keep) if kk])
    np.savez_compressed(OUT / f"{tag}.npz", item_index=idx, **arr)
    recon = arr["head_real"].sum((1, 2)) + arr["mlp_real"].sum(1)
    k_ = (arr["ld_cnonce"] - arr["ld_creal"])  # first-token knowledge (o - o' lead of real over nonce, clean)
    mem_ctx = (arr["head_nonce"] - arr["head_real"]).sum((1, 2)) + (arr["mlp_nonce"] - arr["mlp_real"]).sum(1)
    mem_cln = (arr["head_cnonce"] - arr["head_creal"]).sum((1, 2)) + (arr["mlp_cnonce"] - arr["mlp_creal"]).sum(1)
    summ = {"tag": tag, "n": int(keep.sum()),
            "gamma_first_token": float(np.polyfit(k_, arr["ld_nonce"] - arr["ld_real"], 1)[0]),
            "memory_route_clean_vs_ctx": [float(mem_cln.mean()), float(mem_ctx.mean())],
            "mlp_mem_clean_vs_ctx": [float((arr["mlp_cnonce"] - arr["mlp_creal"]).sum(1).mean()), float((arr["mlp_nonce"] - arr["mlp_real"]).sum(1).mean())],
            "head_mem_clean_vs_ctx": [float((arr["head_cnonce"] - arr["head_creal"]).sum((1, 2)).mean()), float((arr["head_nonce"] - arr["head_real"]).sum((1, 2)).mean())],
            "recon_corr_real": float(np.corrcoef(recon, arr["ld_real"])[0, 1]),
            "mean_ld": [float(arr["ld_real"].mean()), float(arr["ld_nonce"].mean())],
            "mean_heads": [float(arr["head_real"].sum((1, 2)).mean()), float(arr["head_nonce"].sum((1, 2)).mean())],
            "mean_mlp": [float(arr["mlp_real"].sum(1).mean()), float(arr["mlp_nonce"].sum(1).mean())]}
    (OUT / f"{tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--n", type=int, default=1200)
    a = ap.parse_args()
    run(a.repo, a.rev, a.n)
