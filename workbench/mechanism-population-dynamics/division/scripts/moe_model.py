"""Small OLMoE-style decoder for multi-seed MoE pretraining (E167).

Every layer is a dropless top-k MoE (SwiGLU experts, softmax router without top-k
renormalization, as in OLMoE), pre-RMSNorm, QK-norm, RoPE, untied embeddings.
Experts are computed with one padded bmm per projection (torch._grouped_mm is
sm90-only), which keeps routing exact: no token is dropped.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint
from flash_attn import flash_attn_func


@dataclass
class Config:
    vocab: int = 50304
    d_model: int = 768
    n_layers: int = 12
    n_heads: int = 12
    n_experts: int = 64
    top_k: int = 8
    expert_ffn: int = 384
    n_shared: int = 0          # always-active shared experts (0 = none)
    rope_theta: float = 10000.0
    init_std: float = 0.02

    def to_dict(self):
        return asdict(self)


class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        xf = x.float()
        return (xf * torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + self.eps)).to(x.dtype) * self.weight.to(x.dtype)


def rope_cache(T, hd, theta, device):
    inv = 1.0 / (theta ** (torch.arange(0, hd, 2, device=device).float() / hd))
    f = torch.outer(torch.arange(T, device=device).float(), inv)
    return f.cos(), f.sin()


def apply_rope(x, cos, sin):  # x: B,T,H,hd
    x1, x2 = x[..., ::2], x[..., 1::2]
    c, s = cos[None, :, None, :], sin[None, :, None, :]
    out = torch.stack((x1 * c - x2 * s, x1 * s + x2 * c), -1)
    return out.flatten(-2).to(x.dtype)


class Attention(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        d = cfg.d_model
        self.h, self.hd = cfg.n_heads, d // cfg.n_heads
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.o = nn.Linear(d, d, bias=False)
        self.q_norm, self.k_norm = RMSNorm(d), RMSNorm(d)
        self.capture = None  # analysis: dict receiving post-RoPE q, k

    def forward(self, x, cos, sin, head_mask=None):
        B, T, d = x.shape
        q, k, v = self.qkv(x).split(d, -1)
        q, k = self.q_norm(q), self.k_norm(k)
        q = apply_rope(q.view(B, T, self.h, self.hd), cos, sin)
        k = apply_rope(k.view(B, T, self.h, self.hd), cos, sin)
        v = v.view(B, T, self.h, self.hd)
        if self.capture is not None:
            self.capture["q"], self.capture["k"] = q.detach(), k.detach()
        y = flash_attn_func(q, k, v, causal=True)  # B,T,H,hd
        if head_mask is not None:  # analysis hook: per-head multiplicative mask [H]
            y = y * head_mask.view(1, 1, -1, 1).to(y.dtype)
        return self.o(y.reshape(B, T, d))


def _expert_mlp_eager(buf, w_in, w_out):
    g, u = torch.bmm(buf, w_in).chunk(2, -1)
    return torch.bmm(F.silu(g) * u, w_out)


_expert_mlp = _expert_mlp_eager


def enable_compile(model):
    """Compile static-shape parts (attention, norms) and the dynamic-shape expert MLP."""
    global _expert_mlp
    _expert_mlp = torch.compile(_expert_mlp_eager, dynamic=True)
    for b in model.blocks:
        b.attn = torch.compile(b.attn)
        b.n1 = torch.compile(b.n1)
        b.n2 = torch.compile(b.n2)


class MoE(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        d, f, E = cfg.d_model, cfg.expert_ffn, cfg.n_experts
        self.E, self.k = E, cfg.top_k
        self.n_buckets = 8
        # aux-loss-free balancing bias (DeepSeek-V3): affects expert selection only, not gate values
        self.register_buffer("sel_bias", torch.zeros(E))
        self.router = nn.Linear(d, E, bias=False)
        self.w_in = nn.Parameter(torch.empty(E, d, 2 * f))   # gate | up
        self.w_out = nn.Parameter(torch.empty(E, f, d))
        self.n_shared = cfg.n_shared
        if cfg.n_shared:
            self.s_in = nn.Linear(d, 2 * f * cfg.n_shared, bias=False)
            self.s_out = nn.Linear(f * cfg.n_shared, d, bias=False)
        # analysis hooks (None during training)
        self.expert_override = None   # callable(topi, topv, probs, scores) -> (topi, topv)
        self.mean_replace = False     # analysis: replace routed output by (sum of gates) x mean over all experts
        self.record = None            # dict to receive routing stats

    @torch.no_grad()
    def _all_expert_mean(self, xin, chunk=2048):
        outs = []
        w_in, w_out = self.w_in.to(xin.dtype), self.w_out.to(xin.dtype)
        for i in range(0, xin.shape[0], chunk):
            xc = xin[i:i + chunk]
            o = _expert_mlp_eager(xc.unsqueeze(0).expand(self.E, -1, -1), w_in, w_out)
            outs.append(o.float().mean(0).to(xin.dtype))
        return torch.cat(outs)

    def forward(self, x):
        B, T, d = x.shape
        xf = x.reshape(-1, d)
        N = xf.shape[0]
        logits = F.linear(xf.float(), self.router.weight.float())
        probs = logits.softmax(-1)
        scores = logits + self.sel_bias
        topi = scores.topk(self.k, -1).indices
        topv = probs.gather(-1, topi)
        if self.expert_override is not None:
            topi, topv = self.expert_override(topi, topv, probs, scores)
        e = topi.reshape(-1)
        counts = torch.bincount(e, minlength=self.E)
        # Bucket experts by load rank so each padded bmm wastes little (dropless, exact).
        rank_of = torch.empty_like(counts)
        by_load = torch.argsort(counts)
        rank_of[by_load] = torch.arange(self.E, device=x.device)
        r = rank_of[e]
        order = torch.argsort(r, stable=True)
        rs = r[order]
        tok = torch.div(order, self.k, rounding_mode="floor")
        cnt_sorted = counts[by_load]
        starts = torch.cumsum(cnt_sorted, 0) - cnt_sorted
        pos = torch.arange(rs.numel(), device=x.device) - starts[rs]
        cl = cnt_sorted.tolist()
        xin = xf.to(torch.get_autocast_dtype("cuda")) if torch.is_autocast_enabled() else xf
        xs = xin[tok]
        nb = self.n_buckets
        per = self.E // nb
        sizes = [sum(cl[b * per:(b + 1) * per]) for b in range(nb)]
        # split/cat (not slicing) so backward does one concat instead of nb full-size zero fills
        w_in = self.w_in.to(xs.dtype)[by_load].split(per)
        w_out = self.w_out.to(xs.dtype)[by_load].split(per)
        xparts, lparts, pparts = xs.split(sizes), (rs - 0).split(sizes), pos.split(sizes)
        outs = []
        for b in range(nb):
            if sizes[b] == 0:
                outs.append(xparts[b])
                continue
            C = max(cl[b * per:(b + 1) * per])
            loc = lparts[b] - b * per
            buf = xparts[b].new_zeros(per, C, d).index_put((loc, pparts[b]), xparts[b])
            o = _expert_mlp(buf, w_in[b], w_out[b])
            outs.append(o[loc, pparts[b]])
        out = torch.cat(outs)
        w = topv.reshape(-1)[order].to(out.dtype)
        if self.training:
            y = out.new_zeros(N, d).index_add_(0, tok, out * w[:, None])
        else:  # analysis: fp32 accumulation so repeated passes agree (bf16 atomics are order-dependent)
            y = xf.new_zeros(N, d, dtype=torch.float32).index_add_(0, tok, out.float() * w.float()[:, None]).to(out.dtype)
        if self.mean_replace:
            y = self._all_expert_mean(xin) * topv.sum(-1, keepdim=True).to(y.dtype)
        if self.n_shared:
            g, u = self.s_in(xf).chunk(2, -1)
            y = y + self.s_out(F.silu(g) * u)
        # auxiliary losses (OLMoE/Switch style)
        frac = counts.float() / (N * self.k)
        lb = self.E * (frac * probs.mean(0)).sum()
        z = torch.logsumexp(logits, -1).pow(2).mean()
        if self.record is not None:
            self.record["topi"] = topi.detach()
            self.record["topv"] = topv.detach()
        return y.view(B, T, d), lb, z, counts.detach()


class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.n1, self.n2 = RMSNorm(cfg.d_model), RMSNorm(cfg.d_model)
        self.attn, self.moe = Attention(cfg), MoE(cfg)

    def forward(self, x, cos, sin, head_mask=None):
        x = x + self.attn(self.n1(x), cos, sin, head_mask)
        m, lb, z, counts = self.moe(self.n2(x))
        return x + m, lb, z, counts


class MoELM(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.emb = nn.Embedding(cfg.vocab, cfg.d_model)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.norm = RMSNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab, bias=False)
        self.head_masks = None  # analysis: list of [H] tensors or None

    @torch.no_grad()
    def init_weights(self, generator: torch.Generator):
        std = self.cfg.init_std
        out_std = std / math.sqrt(2 * self.cfg.n_layers)
        for name, p in self.named_parameters():
            if p.dim() == 1:
                p.fill_(1.0)
                continue
            s = out_std if (name.endswith("o.weight") or name.endswith("w_out") or name.endswith("s_out.weight")) else std
            p.copy_(torch.randn(p.shape, generator=generator) * s)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        cos, sin = rope_cache(T, self.cfg.d_model // self.cfg.n_heads, self.cfg.rope_theta, idx.device)
        x = self.emb(idx)
        lb_t = z_t = 0.0
        all_counts = []
        for i, blk in enumerate(self.blocks):
            hm = None if self.head_masks is None else self.head_masks[i]
            x, lb, z, counts = blk(x, cos, sin, hm)
            lb_t, z_t = lb_t + lb, z_t + z
            all_counts.append(counts)
        h = self.norm(x)
        L = self.cfg.n_layers
        if targets is None:
            return self.head(h)
        # chunked CE with recomputation: never materializes full fp32 logits
        hf, tf = h.reshape(-1, h.size(-1)), targets.reshape(-1)
        ce = 0.0
        for i in range(0, hf.size(0), 4096):
            ce = ce + torch.utils.checkpoint.checkpoint(
                lambda a, t: F.cross_entropy(self.head(a).float(), t, reduction="sum"),
                hf[i:i + 4096], tf[i:i + 4096], use_reentrant=False)
        ce = ce / tf.numel()
        return ce, lb_t / L, z_t / L, torch.stack(all_counts)
