#!/usr/bin/env python3
"""E212: Llamba-1B (Cartesia; Discrete-Mamba-2 distilled from Llama-3.2-1B-Instruct) in plain torch, mirroring
cartesia-pytorch's DiscreteMamba2 / Block / MixerModel forward, with the SSM scan computed exactly in quadratic form:
  y_t = sum_{s<=t} exp(-sum_{r=s+1..t} dt_r) (C_t . B_s) x_s,  dt = softplus(A_log)   (+ D x_t, gate silu(z + z_bias))
COND (layers 0-2): none | zero (conv neighbour taps -> 0) | mean (E209 mean ablation) | nomem (state = current token)
Usage: e212_llamba.py MODEL_DIR TOK_DIR ITEMS PASSAGES OUT_DIR COND"""
import json
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


class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-5):
        super().__init__(); self.weight = nn.Parameter(torch.ones(d)); self.eps = eps

    def forward(self, h):
        dt = h.dtype; h = h.float()
        return self.weight * (h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + self.eps)).to(dt)


class Mixer(nn.Module):
    def __init__(self, d, d_state, nh, d_conv=4):
        super().__init__()
        self.d, self.n, self.h = d, d_state, nh
        self.conv_dim = d + 2 * nh * d_state
        self.in_proj = nn.Linear(d, 2 * d + 2 * nh * d_state + nh, bias=False)
        self.z_bias = nn.Parameter(torch.zeros(d))
        self.conv1d = nn.Conv1d(self.conv_dim, self.conv_dim, d_conv, groups=self.conv_dim, padding=d_conv - 1, bias=True)
        self.D = nn.Parameter(torch.ones(nh))
        self.out_proj = nn.Linear(d, d, bias=False)
        self.nomem, self.stat = False, None

    def forward(self, u):
        b, L, _ = u.shape
        xBC, z, A_log = torch.split(self.in_proj(u), [self.conv_dim, self.d, self.h], dim=-1)
        if self.stat is not None:
            self.stat[0] += xBC.double().sum((0, 1)); self.stat[1] += b * L
        xBC = self.conv1d(xBC.transpose(1, 2))[..., :L].transpose(1, 2)  # activation: identity
        x, B, C = torch.split(xBC, [self.d, self.h * self.n, self.h * self.n], dim=-1)
        x = x.reshape(b, L, self.h, -1).float(); B = B.reshape(b, L, self.h, self.n).float(); C = C.reshape(b, L, self.h, self.n).float()
        dt = F.softplus(A_log.float())  # [b, L, h]
        CB = torch.einsum("bthn,bshn->bhts", C, B)
        if self.nomem:
            W = torch.diagonal(CB, dim1=-2, dim2=-1).transpose(1, 2)  # [b, L, h]: only s = t
            y = W[..., None] * x
        else:
            cs = torch.cumsum(-dt, dim=1).transpose(1, 2)  # [b, h, L]
            seg = cs[:, :, :, None] - cs[:, :, None, :]  # [b, h, t, s] = -sum_{r=s+1..t} dt_r
            mask = torch.tril(torch.ones(L, L, dtype=torch.bool, device=u.device))
            Wd = torch.exp(seg.masked_fill(~mask, float("-inf"))) * CB
            y = torch.einsum("bhts,bshp->bthp", Wd, x)
        y = y + self.D.float()[None, None, :, None] * x
        y = y.reshape(b, L, self.d).to(u.dtype)
        return self.out_proj(y * F.silu(z + self.z_bias))


class MLP(nn.Module):
    def __init__(self, d, inter):
        super().__init__()
        self.gate_proj = nn.Linear(d, inter, bias=False); self.up_proj = nn.Linear(d, inter, bias=False); self.down_proj = nn.Linear(inter, d, bias=False)

    def forward(self, x):
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        s = cfg["ssm_cfg"]
        self.input_layernorm = RMSNorm(cfg["d_model"]); self.post_attention_layernorm = RMSNorm(cfg["d_model"])
        self.mixer = Mixer(cfg["d_model"], s["d_state"], s["n_v_heads"])
        self.mlp = MLP(cfg["d_model"], cfg["mlp_cfg"]["intermediate_size"])

    def forward(self, h):
        h = h + self.mixer(self.input_layernorm(h)).to(h.dtype)
        return h + self.mlp(self.post_attention_layernorm(h))


class Backbone(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.embed_tokens = nn.Embedding(cfg["vocab_size"], cfg["d_model"])
        self.layers = nn.ModuleList([Block(cfg) for _ in range(cfg["n_layer"])])
        self.norm = RMSNorm(cfg["d_model"], cfg["norm_epsilon"])

    def forward(self, input_ids, use_cache=False, **kw):
        h = self.embed_tokens(input_ids)
        for layer in self.layers:
            h = layer(h)
        return self.norm(h)


class Llamba(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.model = Backbone(cfg)

    def forward(self, input_ids, use_cache=False, **kw):
        h = self.model(input_ids)
        return SimpleNamespace(logits=h @ self.model.embed_tokens.weight.t())  # tied embeddings


def load(mdir):
    cfg = json.loads((Path(mdir) / "config.json").read_text())
    m = Llamba(cfg)
    sd = {k.replace("backbone.", "model.").replace("model.embedding.", "model.embed_tokens.").replace("model.final_layernorm.", "model.norm."): v
          for k, v in load_file(str(Path(mdir) / "model.safetensors")).items()}
    missing, unexpected = m.load_state_dict(sd, strict=True), None
    return m


@torch.no_grad()
def main():
    mdir, tokdir, items, passages, out, cond = sys.argv[1:7]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(tokdir)
    model = load(mdir).cuda().eval()  # fp32, as released
    layers = model.model.layers
    start = tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    taps = []
    for li in LAYERS:
        w = layers[li].mixer.conv1d.weight[:, 0]  # [C, 4]
        taps.append({"layer": li, "absmean_by_tap": [round(x, 4) for x in w.abs().mean(0).tolist()],
                     "neighbour_share_median": round((w[:, :-1].abs().sum(-1) / w.abs().sum(-1)).median().item(), 4)})
    if cond == "mean":
        for li in LAYERS:
            layers[li].mixer.stat = [torch.zeros(layers[li].mixer.conv_dim, dtype=torch.float64, device="cuda"), 0]
        for p in json.loads(Path(passages).read_text())["passages"][50:150]:
            ids = [start] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
            model(torch.tensor([ids], device="cuda"))
    for li in LAYERS:
        mx = layers[li].mixer
        if cond in ("zero", "mean"):
            w = mx.conv1d.weight
            if cond == "mean":
                mu = (mx.stat[0] / mx.stat[1]).float(); mx.stat = None
                mx.conv1d.bias += (w[:, 0, :-1] * mu[:, None]).sum(-1)
            w[..., :-1] = 0
        if cond == "nomem":
            mx.nomem = True
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, passages)
    I = json.loads(Path(items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 4)
    res = {"model": mdir, "cond": cond, "conv_taps": taps, **nll, **s, "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"cond": cond, "nll_mean": round(nll["nll_mean"], 3), "greedy": nll["greedy"][:60], "taps": taps}), flush=True)


if __name__ == "__main__":
    main()
