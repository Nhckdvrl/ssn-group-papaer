#!/usr/bin/env python3
"""E213: M1-3B (togethercomputer; MambaInLlama recipe from Llama-3.2-3B-Instruct) in plain torch, mirroring
jxiw/M1 mamba/hybrid_model.py + hybrid_mamba_layer.py + mha.py for a full-sequence forward:
  Mamba layer: z, x, B, C, dt = in_proj(h); x: GQA-repeat (d_xb -> d_inner) then depthwise causal conv + SiLU;
  B: GQA-repeat; dt = dt_proj(dt) (Linear incl. bias) and delta = softplus(dt + dt_proj.bias) as in the original call;
  h_t = exp(delta_t A) h_{t-1} + delta_t B_t x_t (per channel, A = -exp(A_log) [d_inner, d_state]); y = C_t.h_t + D x;
  out_proj(y * silu(z)).  Attention layers: packed qkv, GQA 24/8, non-interleaved RoPE base rope_theta, causal softmax.
COND (layers 0-2): none | zero | mean | nomem (state = current token only)
Usage: e213_m1.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND"""
import json
import math
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import torch
import torch.nn as nn
import torch.nn.functional as F
from safetensors.torch import load_file
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402

LAYERS = (0, 1, 2)
DT_DOUBLE_BIAS = True  # as in jxiw/M1 inference code; E213 debug compares False


class RMSNorm(nn.Module):
    def __init__(self, d, eps):
        super().__init__(); self.weight = nn.Parameter(torch.ones(d)); self.eps = eps

    def forward(self, h):
        x = h.float()
        return (x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight.float()).to(h.dtype)


def repeat_groups(t, rep, dstate):  # [b, L, g*dstate] -> [b, L, g*rep*dstate] (repeat_kv on groups)
    b, L, _ = t.shape
    return t.reshape(b, L, -1, 1, dstate).expand(-1, -1, -1, rep, -1).reshape(b, L, -1)


class Mamba(nn.Module):
    def __init__(self, d_model, d_inner, d_xb, d_state, dt_rank, d_conv=4):
        super().__init__()
        self.d_inner, self.d_xb, self.n, self.dt_rank = d_inner, d_xb, d_state, dt_rank
        self.rep = d_inner // d_xb
        self.in_proj = nn.Linear(d_model, 2 * d_xb + 2 * d_inner + dt_rank, bias=False)
        self.conv1d = nn.Conv1d(d_inner, d_inner, d_conv, groups=d_inner, padding=d_conv - 1, bias=True)
        self.dt_proj = nn.Linear(dt_rank, d_inner, bias=True)
        self.A_log = nn.Parameter(torch.zeros(d_inner, d_state))
        self.D = nn.Parameter(torch.ones(d_inner))
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)
        self.nomem, self.stat = False, None

    def forward(self, h):
        b, L, _ = h.shape
        z, x, B, C, dt = torch.split(self.in_proj(h), [self.d_inner, self.d_xb, self.d_xb, self.d_inner, self.dt_rank], dim=-1)
        x = repeat_groups(x, self.rep, self.n)  # repeat_kv_before_conv = True (conv has d_inner channels)
        if self.stat is not None:
            self.stat[0] += x.double().sum((0, 1)); self.stat[1] += b * L
        x = F.silu(self.conv1d(x.transpose(1, 2))[..., :L]).transpose(1, 2).float()  # [b, L, Dn]
        B = repeat_groups(B, self.rep, self.n).reshape(b, L, -1, self.n).float()  # [b, L, G, N]
        C = C.reshape(b, L, -1, self.n).float()
        G = C.shape[2]
        delta = F.softplus(self.dt_proj(dt).float() + (self.dt_proj.bias.float() if DT_DOUBLE_BIAS else 0.0))  # [b, L, Dn]
        A = -torch.exp(self.A_log.float())  # [Dn, N]
        xd = (delta * x).reshape(b, L, G, -1)  # [b, L, G, Dg]
        dA = torch.exp(delta[..., None] * A)  # [b, L, Dn, N]
        dA = dA.reshape(b, L, G, -1, self.n)
        if self.nomem:
            y = torch.einsum("blgn,blgn,blgd->blgd", C, B, xd)
        else:
            s = torch.zeros(b, G, xd.shape[-1], self.n, device=h.device)
            ys = []
            for t in range(L):
                s = dA[:, t] * s + xd[:, t, :, :, None] * B[:, t, :, None, :]
                ys.append(torch.einsum("bgdn,bgn->bgd", s, C[:, t]))
            y = torch.stack(ys, 1)
        y = y.reshape(b, L, -1) + self.D.float() * x
        return self.out_proj((y * F.silu(z.float())).to(h.dtype))


class MHA(nn.Module):
    def __init__(self, d_model, nh, nkv, base):
        super().__init__()
        self.nh, self.nkv, self.hd = nh, nkv, d_model // nh
        self.in_proj = nn.Linear(d_model, self.hd * (nh + 2 * nkv), bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        self.inv_freq = 1.0 / (base ** (torch.arange(0, self.hd, 2, dtype=torch.float32) / self.hd))

    def rope(self, t, cos, sin):
        x1, x2 = t.chunk(2, dim=-1)
        return t * cos + torch.cat((-x2, x1), dim=-1) * sin

    def forward(self, h):
        b, L, _ = h.shape
        qkv = self.in_proj(h)
        q = qkv[..., : self.nh * self.hd].reshape(b, L, self.nh, self.hd)
        kv = qkv[..., self.nh * self.hd:].reshape(b, L, 2, self.nkv, self.hd)
        k, v = kv[:, :, 0], kv[:, :, 1]
        fr = torch.outer(torch.arange(L, device=h.device, dtype=torch.float32), self.inv_freq.to(h.device))
        cos = torch.cat([fr.cos(), fr.cos()], -1)[None, :, None, :]; sin = torch.cat([fr.sin(), fr.sin()], -1)[None, :, None, :]
        q = self.rope(q.float(), cos, sin); k = self.rope(k.float(), cos, sin)
        rep = self.nh // self.nkv
        k = k.repeat_interleave(rep, dim=2); v = v.float().repeat_interleave(rep, dim=2)
        o = F.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), is_causal=True)
        return self.out_proj(o.transpose(1, 2).reshape(b, L, -1).to(h.dtype))


class MLP(nn.Module):
    def __init__(self, d, inter):
        super().__init__()
        self.gate_proj = nn.Linear(d, inter, bias=False); self.up_proj = nn.Linear(d, inter, bias=False); self.down_proj = nn.Linear(inter, d, bias=False)

    def forward(self, x):
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class Layer(nn.Module):
    def __init__(self, cfg, mcfg, attn, d_state, dt_rank):
        super().__init__()
        d, eps = cfg["hidden_size"], cfg["rms_norm_eps"]
        self.input_layernorm = RMSNorm(d, eps); self.post_attention_layernorm = RMSNorm(d, eps)
        if attn:
            self.mha = MHA(d, cfg["num_attention_heads"], cfg["num_key_value_heads"], cfg["rope_theta"])
        else:
            self.mamba = Mamba(d, d, mcfg["d_xb"], d_state, dt_rank)
        self.mlp = MLP(d, cfg["intermediate_size"])

    def forward(self, h):
        mixer = self.mha if hasattr(self, "mha") else self.mamba
        h = h + mixer(self.input_layernorm(h))
        return h + self.mlp(self.post_attention_layernorm(h))


class Backbone(nn.Module):
    def __init__(self, cfg, mcfg, d_state, dt_rank):
        super().__init__()
        self.embed_tokens = nn.Embedding(cfg["vocab_size"], cfg["hidden_size"])
        self.layers = nn.ModuleList([Layer(cfg, mcfg, i in mcfg["attn_layers"], d_state, dt_rank) for i in range(cfg["num_hidden_layers"])])
        self.norm = RMSNorm(cfg["hidden_size"], cfg["rms_norm_eps"])

    def forward(self, input_ids, use_cache=False, **kw):
        h = self.embed_tokens(input_ids)
        for layer in self.layers:
            h = layer(h)
        return self.norm(h)


class M1(nn.Module):
    def __init__(self, cfg, mcfg, d_state, dt_rank):
        super().__init__(); self.model = Backbone(cfg, mcfg, d_state, dt_rank)

    def forward(self, input_ids, use_cache=False, **kw):
        return SimpleNamespace(logits=(self.model(input_ids) @ self.model.embed_tokens.weight.t()).float())


def load(mdir):
    mdir = Path(mdir)
    cfg = json.loads((mdir / "config.json").read_text()); mcfg = json.loads((mdir / "mamba_config.json").read_text())
    sd = {}
    for f in sorted(mdir.glob("model-*.safetensors")):
        sd.update(load_file(str(f)))
    d_state = sd["model.layers.0.mamba.A_log"].shape[1]; dt_rank = sd["model.layers.0.mamba.dt_proj.weight"].shape[1]
    m = M1(cfg, mcfg, d_state, dt_rank)
    m.load_state_dict(sd, strict=True)
    return m.to(torch.bfloat16)


@torch.no_grad()
def main():
    mdir, items, passages, out, cond = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(mdir)
    model = load(mdir).cuda().eval()
    layers = model.model.layers
    assert all(hasattr(layers[li], "mamba") for li in LAYERS)
    start = tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else 128009
    taps = []
    for li in LAYERS:
        w = layers[li].mamba.conv1d.weight[:, 0].float()
        taps.append({"layer": li, "absmean_by_tap": [round(x, 4) for x in w.abs().mean(0).tolist()],
                     "neighbour_share_median": round((w[:, :-1].abs().sum(-1) / w.abs().sum(-1)).median().item(), 4)})
    if cond == "mean":
        for li in LAYERS:
            layers[li].mamba.stat = [torch.zeros(layers[li].mamba.d_inner, dtype=torch.float64, device="cuda"), 0]
        for p in json.loads(Path(passages).read_text())["passages"][50:150]:
            ids = [start] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
            model(torch.tensor([ids], device="cuda"))
    for li in LAYERS:
        mx = layers[li].mamba
        if cond in ("zero", "mean"):
            w = mx.conv1d.weight
            if cond == "mean":
                mu = (mx.stat[0] / mx.stat[1]).float(); mx.stat = None
                mx.conv1d.bias += (w[:, 0, :-1].float() * mu[:, None]).sum(-1).to(w.dtype)
            w[..., :-1] = 0
        if cond == "nomem":
            mx.nomem = True
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, passages)
    I = json.loads(Path(items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 2)
    res = {"model": str(mdir), "cond": cond, "conv_taps": taps, **nll, **s, "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"cond": cond, "nll_mean": round(nll["nll_mean"], 3), "greedy": nll["greedy"][:60], "taps": taps}), flush=True)


if __name__ == "__main__":
    main()
