#!/usr/bin/env python3
"""E214: Llama3.2-Mamba-3B-distill (MambaInLlama; Mamba-1 layers at even indices, inherited attention at odd ones),
plain-torch model from e213_m1 (same jxiw/M1 code path), weights from pytorch_model.bin.
COND: none | mean | zero (conv of Mamba layers 0, 2) | nomem (Mamba layers 0, 2) | noattn (attention layer 1) | mean_noattn
Usage: e214_mil.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND"""
import json
import math
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402
import e213_m1 as M  # noqa: E402

MAMBA_LAYERS, ATTN_LAYERS = (0, 2), (1,)


def llama3_inv_freq(inv_freq, rs):
    """transformers' _compute_llama3_parameters (the attention layers here are HF LlamaAttention with llama3 RoPE)."""
    factor, lo, hi, old = rs["factor"], rs["low_freq_factor"], rs["high_freq_factor"], rs["original_max_position_embeddings"]
    wavelen = 2 * math.pi / inv_freq
    out = torch.where(wavelen > old / lo, inv_freq / factor, inv_freq)
    smooth = (old / wavelen - lo) / (hi - lo)
    smoothed = (1 - smooth) * out / factor + smooth * out
    medium = (wavelen >= old / hi) & (wavelen <= old / lo)
    return torch.where(medium, smoothed, out)


def load(mdir):
    """Old MambaInLlama layout: mamba.{in_proj_z,in_proj_x,B_proj,C_proj,dt_proj_down} (fused here into in_proj in the
    order z, x, B, C, dt of jxiw/M1) and HF self_attn.{q,k,v,o}_proj (fused into mha.in_proj / mha.out_proj)."""
    mdir = Path(mdir)
    cfg = json.loads((mdir / "config.json").read_text()); mcfg = json.loads((mdir / "mamba_config.json").read_text())
    raw = torch.load(mdir / "pytorch_model.bin", map_location="cpu", weights_only=True)
    sd = {}
    for k, v in raw.items():
        if k.startswith("lm_head.") and cfg.get("tie_word_embeddings"):
            continue
        if any(t in k for t in (".mamba.in_proj_", ".mamba.B_proj", ".mamba.C_proj", ".mamba.dt_proj_down", ".self_attn.")):
            continue
        sd[k] = v
    for i in range(cfg["num_hidden_layers"]):
        pre = f"model.layers.{i}"
        if f"{pre}.mamba.in_proj_x.weight" in raw:
            sd[f"{pre}.mamba.in_proj.weight"] = torch.cat([raw[f"{pre}.mamba.{n}.weight"] for n in
                                                           ("in_proj_z", "in_proj_x", "B_proj", "C_proj", "dt_proj_down")], 0)
        else:
            sd[f"{pre}.mha.in_proj.weight"] = torch.cat([raw[f"{pre}.self_attn.{n}_proj.weight"] for n in ("q", "k", "v")], 0)
            sd[f"{pre}.mha.out_proj.weight"] = raw[f"{pre}.self_attn.o_proj.weight"]
    d_state = sd["model.layers.0.mamba.A_log"].shape[1]; dt_rank = sd["model.layers.0.mamba.dt_proj.weight"].shape[1]
    m = M.M1(cfg, mcfg, d_state, dt_rank)
    m.load_state_dict(sd, strict=True)
    rs = cfg.get("rope_scaling") or {}
    if rs.get("rope_type", rs.get("type")) == "llama3":
        for layer in m.model.layers:
            if hasattr(layer, "mha"):
                layer.mha.inv_freq = llama3_inv_freq(layer.mha.inv_freq, rs)
    return m.to(torch.bfloat16)


@torch.no_grad()
def main():
    mdir, items, passages, out, cond = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = cap.AutoTokenizer.from_pretrained(mdir)
    model = load(mdir).cuda().eval()
    layers = model.model.layers
    assert all(hasattr(layers[i], "mamba") for i in MAMBA_LAYERS) and all(hasattr(layers[i], "mha") for i in ATTN_LAYERS)
    start = tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else 128009
    taps = []
    for li in MAMBA_LAYERS:
        w = layers[li].mamba.conv1d.weight[:, 0].float()
        taps.append({"layer": li, "absmean_by_tap": [round(x, 4) for x in w.abs().mean(0).tolist()],
                     "neighbour_share_median": round((w[:, :-1].abs().sum(-1) / w.abs().sum(-1)).median().item(), 4)})
    if cond in ("mean", "mean_noattn"):
        for li in MAMBA_LAYERS:
            layers[li].mamba.stat = [torch.zeros(layers[li].mamba.d_inner, dtype=torch.float64, device="cuda"), 0]
        for p in json.loads(Path(passages).read_text())["passages"][50:150]:
            ids = [start] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
            model(torch.tensor([ids], device="cuda"))
    for li in MAMBA_LAYERS:
        mx = layers[li].mamba
        if cond in ("zero", "mean", "mean_noattn"):
            w = mx.conv1d.weight
            if cond != "zero":
                mu = (mx.stat[0] / mx.stat[1]).float(); mx.stat = None
                mx.conv1d.bias += (w[:, 0, :-1].float() * mu[:, None]).sum(-1).to(w.dtype)
            w[..., :-1] = 0
        if cond == "nomem":
            mx.nomem = True
    if cond in ("noattn", "mean_noattn"):
        for li in ATTN_LAYERS:
            layers[li].mha.register_forward_hook(lambda mod, i, o: torch.zeros_like(o))
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
