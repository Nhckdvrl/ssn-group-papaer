#!/usr/bin/env python3
"""E209: zero vs mean ablation of the short convs' neighbour taps, then E194's R1 (set S) + NLL.
mean: per-channel mean conv input mu (EWT passages 50-149, unablated model), neighbour taps -> 0, bias += sum_j w_j mu.
COND: none | zero | mean | mean_noattn (Falcon-H1 only: also zero the same layers' attention output)
Usage: e209_run.py MODEL_DIR ITEMS PASSAGES OUT_DIR COND --layers 0-2 [--no_start] [--fla] [--attn_attr self_attn]"""
import argparse
import json
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent))


def short_convs(layer):
    out = []
    for name, m in layer.named_modules():
        w = getattr(m, "weight", None)
        if isinstance(m, torch.nn.Conv1d) and w is not None and w.dim() == 3 and w.shape[1] == 1 and w.shape[-1] > 1:
            out.append((name, m))
    return out


def conv_input_means(model, tok, start, passages, convs):
    """Mean conv input per channel, captured by wrapping F.conv1d (all reference conv paths go through it)."""
    keys = {c.weight.data_ptr(): i for i, c in enumerate(convs)}
    sums = [torch.zeros(c.weight.shape[0], dtype=torch.float64, device="cuda") for c in convs]
    cnt = [0] * len(convs)
    orig = F.conv1d

    def wrapped(inp, weight, *a, **k):
        i = keys.get(weight.data_ptr())
        if i is not None:
            sums[i] += inp.double().sum((0, 2)); cnt[i] += inp.shape[0] * inp.shape[2]
        return orig(inp, weight, *a, **k)

    F.conv1d = wrapped
    try:
        P = json.loads(Path(passages).read_text())["passages"][50:150]
        with torch.no_grad():
            for p in P:
                ids = ([start] if start is not None else []) + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
                model(input_ids=torch.tensor([ids], device="cuda"), use_cache=False)
    finally:
        F.conv1d = orig
    assert all(n > 0 for n in cnt), f"conv inputs not captured: {cnt}"
    return [(s / n).float() for s, n in zip(sums, cnt)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("items"); ap.add_argument("passages"); ap.add_argument("out"); ap.add_argument("cond")
    ap.add_argument("--layers", default="0-2"); ap.add_argument("--no_start", action="store_true")
    ap.add_argument("--fla", action="store_true"); ap.add_argument("--attn_attr", default="self_attn")
    a = ap.parse_args()
    if a.fla:
        import fla  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import e195_capture as cap
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
    base, emb, layers = cap.parts(model)
    lo, hi = map(int, a.layers.split("-"))
    start = None if a.no_start else tok.bos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    targets = [(li, n, m) for li in range(lo, hi + 1) for n, m in short_convs(layers[li])]
    assert targets, "no short conv found"
    done, shift = [], []
    if a.cond in ("mean", "mean_noattn"):
        mus = conv_input_means(model, tok, start, a.passages, [m for _, _, m in targets])
    for k, (li, name, m) in enumerate(targets):
        if a.cond == "none":
            break
        with torch.no_grad():
            w = m.weight
            if a.cond.startswith("mean"):
                d = (w[:, 0, :-1].float() * mus[k][:, None]).sum(-1)
                if m.bias is None:
                    m.bias = torch.nn.Parameter(d.to(w.dtype), requires_grad=False)
                else:
                    m.bias += d.to(w.dtype)
                shift.append(round(d.abs().mean().item(), 4))
            w[..., :-1] = 0
        done.append(f"{li}.{name}:{tuple(m.weight.shape)}")
    if a.cond == "mean_noattn":
        for li in range(lo, hi + 1):
            getattr(layers[li], a.attn_attr).register_forward_hook(
                lambda mod, i, o: ((torch.zeros_like(o[0]),) + tuple(o[1:])) if isinstance(o, tuple) else torch.zeros_like(o))
            done.append(f"{li}:attn")
    t0 = time.time()
    nll = cap.mode_nll(model, tok, start, a.passages)
    I = json.loads(Path(a.items).read_text())
    I["S"] = [it for it in I["S"] if all(str(mm) in it["splits"] for mm in range(2, 7))]
    s = cap.mode_S(cap.Capture(model, start, pad), I["S"], out, 4)
    res = {"model": a.model, "cond": a.cond, "layers": a.layers, "switched": done, "bias_shift_absmean": shift, **nll, **s,
           "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps({"cond": a.cond, "layers": a.layers, "n_switched": len(done), "nll_mean": round(nll["nll_mean"], 3),
                      "greedy": nll["greedy"][:50]}), flush=True)


if __name__ == "__main__":
    main()
