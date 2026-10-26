"""E91: where does a pretraining loss spike start? Per-head attention statistics on checkpoints before/after a spike.

Usage: e91_spike_heads.py --repo REPO --rev stepN  -> results/e91/<model>__<rev>.json
Per head (fixed 32 pile-10k documents x 512 tokens, causal positions only):
  max_logit   maximum raw pre-softmax logit (NOT shift-invariant: Pythia's QKV biases add per-row offsets)
  spread_max  max over query rows of (row max - row mean) of causal logits: shift-invariant sharpness (primary)
  spread_mean mean over rows of the same quantity
  entropy     mean attention entropy (nats) over query positions >= 16
  prev        mean attention to the previous token (previous-token role score)
  sink        mean attention to position 0
  qk_spec     spectral norm of W_Q_h^T W_K_h (weights; rotary ignored)
Global: LM loss, max |output logit|, per-layer residual-stream RMS.
"""
import argparse
import json
import os
import time

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / "e91"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--T", type=int, default=512)
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    from huggingface_hub import list_repo_files
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import transformers.models.gpt_neox.modeling_gpt_neox as gm
    kw = {"revision": a.rev}
    if "pytorch_model.bin" in list_repo_files(a.repo, revision=a.rev):
        kw["use_safetensors"] = False  # step branches may also carry main's safetensors
    cache = os.environ.get("E89_MODEL_CACHE", str(mc.HF_CACHE))
    tok = AutoTokenizer.from_pretrained(a.repo, cache_dir=cache, revision=a.rev)
    model = AutoModelForCausalLM.from_pretrained(a.repo, cache_dir=cache, torch_dtype=torch.float32,
                                                 attn_implementation="eager", **kw).cuda().eval()
    L, H = model.config.num_hidden_layers, model.config.num_attention_heads
    stats = {k: np.zeros((L, H)) for k in ("max_logit", "spread_max", "spread_mean", "entropy", "prev", "sink")}
    counter = {"layer": 0}
    orig = gm.eager_attention_forward

    def wrapped(module, query, key, value, attention_mask, scaling, dropout=0.0, head_mask=None, **kw2):
        l = module.layer_idx if hasattr(module, "layer_idx") else counter["layer"]
        s = torch.matmul(query.float(), key.float().transpose(2, 3)) * scaling  # [B, H, T, T]
        T = s.shape[-1]
        causal = torch.ones(T, T, dtype=torch.bool, device=s.device).tril()
        sm = s.masked_fill(~causal, float("-inf"))
        valid = s.masked_select(causal.expand_as(s)).view(s.shape[0], s.shape[1], -1)
        stats["max_logit"][l] = np.maximum(stats["max_logit"][l], valid.amax((0, 2)).cpu().numpy())
        cnt = causal.sum(-1).float()  # keys per query row
        rowmean = s.masked_fill(~causal, 0).sum(-1) / cnt
        spread = (sm.amax(-1) - rowmean)[:, :, 16:]  # [B, H, T-16]
        stats["spread_max"][l] = np.maximum(stats["spread_max"][l], spread.amax((0, 2)).cpu().numpy())
        stats["spread_mean"][l] += spread.mean((0, 2)).cpu().numpy()
        p = torch.softmax(sm, -1)
        ent = -(p * torch.log(p.clamp_min(1e-12))).sum(-1)[:, :, 16:].mean((0, 2))
        idx = torch.arange(1, T, device=s.device)
        prev = p[:, :, idx, idx - 1].mean((0, 2))
        sink = p[:, :, 16:, 0].mean((0, 2))
        stats["entropy"][l] += ent.cpu().numpy()
        stats["prev"][l] += prev.cpu().numpy()
        stats["sink"][l] += sink.cpu().numpy()
        counter["layer"] = (l + 1) % L
        return orig(module, query, key, value, attention_mask, scaling, dropout, head_mask, **kw2)

    gm.eager_attention_forward = wrapped
    from datasets import load_dataset
    ds = load_dataset("NeelNanda/pile-10k", split="train", cache_dir=str(mc.HF_CACHE))
    seqs = []
    for t in ds["text"][3000:9000]:
        ids = tok(t, add_special_tokens=False)["input_ids"][:a.T]
        if len(ids) == a.T:
            seqs.append(ids)
        if len(seqs) == a.n:
            break
    x = torch.tensor(seqs, device="cuda")
    nb, tot, maxout, rms = 0, 0.0, 0.0, np.zeros(L + 1)
    for i in range(0, a.n, 4):
        out = model(x[i:i + 4], output_hidden_states=True)
        lg = out.logits.float()
        tot += torch.nn.functional.cross_entropy(lg[:, :-1].reshape(-1, lg.shape[-1]), x[i:i + 4, 1:].reshape(-1)).item()
        maxout = max(maxout, lg.abs().max().item())
        rms += np.array([h.float().pow(2).mean().sqrt().item() for h in out.hidden_states])
        nb += 1
    for k in ("spread_mean", "entropy", "prev", "sink"):
        stats[k] /= nb
    gm.eager_attention_forward = orig
    dh = model.config.hidden_size // H
    qk = np.zeros((L, H))
    for l, layer in enumerate(model.gpt_neox.layers):
        W = layer.attention.query_key_value.weight.float().view(H, 3, dh, -1)
        for h in range(H):
            qk[l, h] = torch.linalg.matrix_norm(W[h, 0].T @ W[h, 1], ord=2).item()
    res = {"repo": a.repo, "rev": a.rev, "lm_loss": tot / nb, "max_out_logit": maxout, "resid_rms": rms.round(4).tolist(),
           **{k: v.round(5).tolist() for k, v in stats.items()}, "qk_spec": qk.round(4).tolist(), "seconds": time.time() - t0}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.repo.split('/')[-1]}__{a.rev}.json").write_text(json.dumps(res))
    print(json.dumps({k: res[k] for k in ("repo", "rev", "lm_loss", "max_out_logit", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
