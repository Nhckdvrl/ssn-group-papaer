#!/usr/bin/env python3
"""E215: Jet-Nemotron-2B (official remote code). Layers 0-2 (JetBlocks) use the official "naive" dynamic-conv path in
every condition, patched to allow: zero (generated kernel's neighbour taps -> 0) | mean (neighbour inputs -> channel
mean, from EWT passages 50-149) | nomem (GDN A_log += 20) | none.
Usage: e215_jet.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND"""
import json
import sys
import time
import types
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402

LAYERS = (0, 1, 2)


def patched_naive(self, x, generator_input=None):
    W = self.kernel_size
    kernels = self.get_kernel(x if generator_input is None else generator_input)  # [B, T, D, W]
    if self._stat is not None:
        self._stat[0] += x.double().sum((0, 1)); self._stat[1] += x.shape[0] * x.shape[1]
    win = F.pad(x.transpose(1, 2), (W - 1, 0)).unfold(dimension=2, size=W, step=1).permute(0, 2, 1, 3)  # [B, T, D, W]
    if self._ablate == "zero":
        kernels = kernels.clone(); kernels[..., : W - 1] = 0
    elif self._ablate == "mean":
        win = win.clone(); win[..., : W - 1] = self._mu.to(win.dtype)[None, None, :, None]
    return (win * kernels).sum(dim=-1)


@torch.no_grad()
def main():
    mdir, items, passages, out, cond = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(mdir, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(mdir, dtype=torch.bfloat16, trust_remote_code=True).cuda().eval()
    base, emb, layers = cap.parts(model)
    convs = []
    for li in LAYERS:
        blk = layers[li].self_attn
        assert hasattr(blk, "dynamic_conv1d") and hasattr(blk, "A_log"), f"layer {li} is not a JetBlock"
        dc = blk.dynamic_conv1d
        dc.implementation = "naive"; dc._ablate = None; dc._stat = None; dc._mu = None
        dc._forward_naive = types.MethodType(patched_naive, dc)
        convs.append(dc)
    start = None  # Qwen2.5: no document-start token (as E198)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    if cond == "mean":
        for dc in convs:
            dc._stat = [torch.zeros(dc.hidden_size, dtype=torch.float64, device="cuda"), 0]
        for p in json.loads(Path(passages).read_text())["passages"][50:150]:
            ids = tok(p["text"], add_special_tokens=False)["input_ids"][:511]
            model(input_ids=torch.tensor([ids], device="cuda"), use_cache=False)
        for dc in convs:
            dc._mu = (dc._stat[0] / dc._stat[1]).float(); dc._stat = None
    for li, dc in zip(LAYERS, convs):
        if cond in ("zero", "mean"):
            dc._ablate = cond
        if cond == "nomem":
            layers[li].self_attn.A_log += 20
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, passages)
    I = json.loads(Path(items).read_text())
    I["S"] = [it for it in I["S"] if all(str(m) in it["splits"] for m in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 4)
    res = {"model": mdir, "cond": cond, **nll, **s, "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"cond": cond, "nll_mean": round(nll["nll_mean"], 3), "greedy": nll["greedy"][:60]}), flush=True)


if __name__ == "__main__":
    main()
