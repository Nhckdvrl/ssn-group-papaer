#!/usr/bin/env python3
"""E222: sink-preserving attention cut, depth-aligned (first ceil(L/8) layers) early cut, mid-layer conv re-entry factorial.
Token classes and readouts as E221. Where does the damage of a cut land? Per-token NLL, top-1 and p(correct) on EWT passages 0-199,
split by word-initial vs word-internal (E217 piece_kind) x word seen earlier in the passage vs first occurrence.
Switches as E219/E220 (conv: neighbour taps mean-replaced, mu from passages 200-299; mem: state = current token;
attn: attend to self). Conditions are chosen from the components the model has:
  recurrent/hybrid: ALL_conv, ALL_mem, ALL_attn (if any), B0_all (layers 0-3, every mixer), ALL_all (every mixer, every layer)
  Transformer: ALL_attn, T1_attn / T2_attn / T3_attn (depth thirds)
Usage: e222_sink.py MODEL_DIR PASSAGES OUT_JSON [--start eos|bos|none] [--llamba TOK_DIR] [--n 200] [--bs 8]"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent))
import e209_run as e209  # noqa: E402
from e217_levels import piece_kind  # noqa: E402

ORIG_SDPA = F.scaled_dot_product_attention
STATE = {"active": False, "cur": None, "calls": 0, "per_layer": {}, "targets": set(), "mode": "self"}


def sdpa_wrap(q, k, v, *a, **kw):
    if STATE["active"]:
        STATE["calls"] += 1
        rep = q.shape[-3] // v.shape[-3]
        vv = v if rep == 1 else v.repeat_interleave(rep, dim=-3)
        if STATE["mode"] == "self":
            return vv.to(q.dtype)
        kk = k if rep == 1 else k.repeat_interleave(rep, dim=-3)
        sc = kw.get("scale") or q.shape[-1] ** -0.5
        qf, kf, vf = q.float(), kk.float(), vv.float()
        s_self = (qf * kf).sum(-1) * sc                     # [B,H,T]
        s_sink = (qf * kf[..., :1, :]).sum(-1) * sc         # [B,H,T]
        w = torch.softmax(torch.stack([s_sink, s_self], -1), -1)
        w[..., 0, :] = torch.tensor([1.0, 0.0], device=w.device)  # position 0: the sink is itself
        out = w[..., 0:1] * vf[..., :1, :] + w[..., 1:2] * vf
        return out.to(q.dtype)
    if STATE["cur"] is not None:
        STATE["per_layer"][STATE["cur"]] = STATE["per_layer"].get(STATE["cur"], 0) + 1
    return ORIG_SDPA(q, k, v, *a, **kw)


F.scaled_dot_product_attention = sdpa_wrap
torch.nn.functional.scaled_dot_product_attention = sdpa_wrap


NORM = {"lens": None, "acc": {}}


def norm_hook(name):
    def f(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if NORM["lens"] is None or len(NORM["lens"]) != h.shape[0]:
            return
        n = h.float().norm(dim=-1)  # [B,T]
        m = torch.zeros_like(n, dtype=torch.bool)
        for i, L_ in enumerate(NORM["lens"]):
            m[i, 1:L_] = True  # exclude position 0 and padding
        a = NORM["acc"].setdefault(name, [0.0, 0])
        a[0] += n[m].sum().item(); a[1] += int(m.sum().item())
    return f


@torch.no_grad()
def passage_eval(model, seqs, pad, bs):
    nll, cor, prob = [], [], []
    NORM["acc"] = {}
    for b in range(0, len(seqs), bs):
        chunk = seqs[b:b + bs]
        NORM["lens"] = [len(s) for s in chunk]
        T = max(map(len, chunk))
        x = torch.full((len(chunk), T), pad, dtype=torch.long)
        for i, s in enumerate(chunk):
            x[i, :len(s)] = torch.tensor(s)
        x = x.cuda()
        lp = model(input_ids=x, use_cache=False).logits.float()[:, :-1].log_softmax(-1)
        tg = x[:, 1:]
        g = lp.gather(2, tg[..., None])[..., 0]
        am = lp.argmax(-1)
        for i, s in enumerate(chunk):
            n = len(s) - 1
            nll.append(-g[i, :n].cpu()); cor.append((am[i, :n] == tg[i, :n]).cpu()); prob.append(g[i, :n].exp().cpu())
        del lp
    NORM["lens"] = None
    norms = {k: v[0] / max(v[1], 1) for k, v in NORM["acc"].items()}
    return torch.cat(nll).numpy(), torch.cat(cor).float().numpy(), torch.cat(prob).numpy(), norms


def conv_means(model, tok, start, P, convs):
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
        with torch.no_grad():
            for p in P[200:300]:  # disjoint from the evaluated passages 0-199
                ids = ([start] if start is not None else []) + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
                model(input_ids=torch.tensor([ids], device="cuda"), use_cache=False)
    finally:
        F.conv1d = orig
    assert all(n > 0 for n in cnt), f"conv inputs not captured: {cnt}"
    return [(s / n).float() for s, n in zip(sums, cnt)]


def classify(tok, ids):
    """Per token of ids: (kind, repeated, multi, first_of_multi). Word = an initial piece plus following internal pieces."""
    kinds = piece_kind(tok, ids)
    strs = tok.convert_ids_to_tokens(ids)
    out = [(None, False, False, False)] * len(ids)
    words, cur = [], None
    for j, k in enumerate(kinds):
        body = strs[j].lstrip("Ġ▁ ").lower()
        if k == "initial":
            if cur:
                words.append(cur)
            cur = [[j], body]
        elif k == "internal" and cur:
            cur[0].append(j); cur[1] += body
        else:
            if cur:
                words.append(cur)
            cur = None
    if cur:
        words.append(cur)
    seen = set()
    for pos, w in words:
        rep, multi = w in seen, len(pos) > 1
        for i, j in enumerate(pos):
            out[j] = (kinds[j], rep, multi, multi and i == 0)
        seen.add(w)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("passages"); ap.add_argument("out")
    ap.add_argument("--start", default="bos"); ap.add_argument("--llamba", default=None)
    ap.add_argument("--n", type=int, default=200); ap.add_argument("--bs", type=int, default=8)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    if a.llamba:
        import e212_llamba as L
        tok = AutoTokenizer.from_pretrained(a.llamba)
        model = L.load(a.model).cuda().eval()  # fp32 as E212 / E217 / E219
        layers = list(model.model.layers)
    else:
        tok = AutoTokenizer.from_pretrained(a.model)
        try:
            model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, attn_implementation="sdpa").cuda().eval()
        except ValueError:
            model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
        import e195_capture as cap
        _, _, layers = cap.parts(model)
    start = {"eos": tok.eos_token_id, "bos": tok.bos_token_id, "none": None}[a.start]
    pre = [start] if start is not None else []
    off = len(pre)
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    P = json.loads(Path(a.passages).read_text())["passages"]
    seqs, cls = [], []
    for p in P[:a.n]:
        ids = tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        seqs.append(pre + ids); c = classify(tok, ids)
        cls += [c[t - off] if t - off >= 0 else (None, False, False, False) for t in range(1, len(ids) + off)]
    kind = np.array([c[0] or "" for c in cls]); rep = np.array([c[1] for c in cls]); fom = np.array([c[3] for c in cls])
    masks = {}
    for k in ("initial", "internal"):
        for r, rn in ((True, "rep"), (False, "first")):
            masks[f"{k}_{rn}"] = (kind == k) & (rep == r)
        masks[k] = kind == k
    masks["initial_multi_rep"] = fom & rep; masks["initial_multi_first"] = fom & ~rep; masks["initial_multi"] = fom
    masks["all"] = np.ones(len(cls), dtype=bool)

    def pre_hook(li):
        def f(mod, inp):
            STATE["cur"] = li; STATE["active"] = li in STATE["targets"]
        return f

    def post_hook(mod, inp, out):
        STATE["active"] = False; STATE["cur"] = None

    for li, layer in enumerate(layers):
        layer.register_forward_pre_hook(pre_hook(li)); layer.register_forward_hook(post_hook)
    import math
    for nm, li in (("after_d8", math.ceil(len(layers) / 8)), ("last", len(layers) - 1)):
        layers[li].register_forward_hook(norm_hook(nm))
    base = passage_eval(model, seqs, pad, a.bs)
    assert len(base[0]) == len(cls), (len(base[0]), len(cls))
    attn_layers = sorted(k for k, v in STATE["per_layer"].items() if v > 0)
    L = len(layers)
    convs = {li: e209.short_convs(layer) for li, layer in enumerate(layers)}
    mems = {li: [m for _, m in layer.named_modules() if (hasattr(m, "A_log") and isinstance(getattr(m, "A_log"), torch.nn.Parameter)) or hasattr(m, "nomem")]
            for li, layer in enumerate(layers)}
    has_conv, has_mem = any(convs.values()), any(mems.values())
    all_convs = [m for li in convs for _, m in convs[li]]
    mus, conv_mode = {}, "none"
    if has_conv:
        try:
            ms = conv_means(model, tok, start, P, all_convs); mus = {id(m): mu for m, mu in zip(all_convs, ms)}; conv_mode = "mean"
        except AssertionError as e:
            print("conv capture failed -> zero:", e, flush=True); conv_mode = "zero"
    import math
    allL = list(range(L)); d8 = math.ceil(L / 8); D8 = list(range(d8)); B0 = list(range(min(4, L))); MID = list(range(d8, L // 2))
    conds = []  # (name, conv layers, mem layers, attn layers, attn mode)
    if has_conv or has_mem:
        att_d8 = any(l in attn_layers for l in D8)
        if att_d8:
            conds.append(("D8_all_self", D8, D8, D8, "self"))
        conds.append(("D8_all_sink", D8, D8, D8, "sink"))
        if attn_layers:
            conds.append(("ALL_all_self", allL, allL, allL, "self"))
        conds.append(("ALL_all_sink", allL, allL, allL, "sink"))
        if any(convs[l] for l in MID):
            conds.append(("MID_conv", MID, [], [], "sink"))
            conds.append(("D8_all+MID_conv", sorted(set(D8) | set(MID)), D8, D8, "sink"))
        if any(mems[l] for l in MID):
            conds.append(("D8_all+MID_mem", D8, sorted(set(D8) | set(MID)), D8, "sink"))
    else:
        conds += [("D8_self", [], [], D8, "self"), ("D8_sink", [], [], D8, "sink"),
                  ("ALL_self", [], [], allL, "self"), ("ALL_sink", [], [], allL, "sink")]
        if d8 != 4:
            conds += [("B0_self", [], [], B0, "self"), ("B0_sink", [], [], B0, "sink")]

    def cells(cut):
        r = {}
        for name, m in masks.items():
            if m.sum() == 0:
                continue
            r[name] = {"n": int(m.sum()), "base_nll": float(base[0][m].mean()), "base_top1": float(base[1][m].mean()), "base_p": float(base[2][m].mean())}
            if cut is not None:
                r[name].update({"dnll": float((cut[0][m] - base[0][m]).mean()), "dtop1": float((base[1][m] - cut[1][m]).mean()),
                                "dp": float((base[2][m] - cut[2][m]).mean())})
        return r

    res = {"model": a.model, "start": a.start, "n_layers": L, "d8": d8, "mid": [MID[0], MID[-1]] if MID else None, "attn_layers": attn_layers,
           "conv_mode": conv_mode, "n_passages": a.n, "base": cells(None), "base_norms": base[3], "conds": {}}
    print(f"[{time.time() - t0:.0f}s] base NLL {res['base']['all']['base_nll']:.3f}; n internal {res['base']['internal']['n']}, "
          f"internal_rep {res['base'].get('internal_rep', {}).get('n')}, attn {attn_layers[:6]}", flush=True)
    store = {"base_nll": base[0], "base_cor": base[1], "base_p": base[2]}
    for name, cl, ml, al, mode in conds:
        saved_c, saved_m = [], []
        with torch.no_grad():
            for li in cl:
                for _, m in convs[li]:
                    saved_c.append((m, m.weight.data.clone(), None if m.bias is None else m.bias.data.clone()))
                    if conv_mode == "mean":
                        d = (m.weight[:, 0, :-1].float() * mus[id(m)][:, None]).sum(-1).to(m.weight.dtype)
                        if m.bias is None:
                            m.bias = torch.nn.Parameter(d, requires_grad=False)
                        else:
                            m.bias.data += d
                    m.weight.data[..., :-1] = 0
            for li in ml:
                for m in mems[li]:
                    if hasattr(m, "nomem"):
                        m.nomem = True; saved_m.append((m, None))
                    else:
                        saved_m.append((m, m.A_log.data.clone())); m.A_log.data += 20
        STATE["targets"] = set(l for l in al if l in attn_layers); STATE["calls"] = 0; STATE["mode"] = mode
        cut = passage_eval(model, seqs, pad, a.bs)
        n_attn = len(STATE["targets"]); calls = STATE["calls"]; STATE["targets"] = set()
        with torch.no_grad():
            for m, w, b in saved_c:
                m.weight.data.copy_(w)
                if b is None:
                    m.register_parameter("bias", None)
                else:
                    m.bias.data.copy_(b)
            for m, s in saved_m:
                if s is None:
                    m.nomem = False
                else:
                    m.A_log.data.copy_(s)
        assert n_attn == 0 or calls > 0, f"{name}: self-only attention not applied"
        res["conds"][name] = {"n_conv": len(saved_c), "n_mem": len(saved_m), "n_attn": n_attn, "mode": mode, "cells": cells(cut),
                              "norm_ratio": {k: cut[3][k] / base[3][k] for k in base[3] if k in cut[3]}}
        store[f"{name}_nll"] = cut[0]; store[f"{name}_cor"] = cut[1]; store[f"{name}_p"] = cut[2]
        c = res["conds"][name]["cells"]
        print(f"[{time.time() - t0:.0f}s] {name:16s} norm {res['conds'][name]['norm_ratio']} dNLL all {c['all']['dnll']:+.3f} | ini {c['initial']['dnll']:+.2f} int {c['internal']['dnll']:+.2f} "
              f"| int_rep {c.get('internal_rep', {}).get('dnll', float('nan')):+.2f} int_first {c.get('internal_first', {}).get('dnll', float('nan')):+.2f} "
              f"| dtop1 ini {c['initial']['dtop1']:+.3f} int {c['internal']['dtop1']:+.3f}", flush=True)
        Path(a.out).write_text(json.dumps(res))
    chk = passage_eval(model, seqs, pad, a.bs)
    res["restore_check_max_abs"] = float(np.abs(chk[0] - base[0]).max()); res["sec"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(res))
    np.savez_compressed(str(a.out).replace(".json", ".npz"), cls_kind=kind, cls_rep=rep, cls_first_of_multi=fom, **store)
    print(f"E222_MODEL_DONE {a.model} restore {res['restore_check_max_abs']:.2e} sec {res['sec']}", flush=True)


if __name__ == "__main__":
    main()
