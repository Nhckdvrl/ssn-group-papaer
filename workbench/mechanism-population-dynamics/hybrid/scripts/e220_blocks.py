#!/usr/bin/env python3
"""E220: block (4 consecutive layers) and all-layer isolation, same switches and readouts as E219 (inference only).
For every layer l and component c in {conv, mem, attn}, cut c's cross-token path in layer l only, keep the current-token path:
  conv: neighbour taps mean-replaced (E209; mu from EWT passages 50-149), falls back to zero if conv inputs cannot be captured
  mem:  state keeps only the current token (A_log += 20; Llamba: mixer.nomem)
  attn: attend to self only (every SDPA call inside layer l returns its own value vector)
Readouts on EWT passages 0-49 (<= 511 tokens each): mean per-token dNLL; word-internal vs word-initial (E217 piece_kind);
context-gain tertiles (near / mid / far) from the unablated model: NLL(last W tokens only) - NLL(full context), W = 32 and 128.
Usage: e220_blocks.py MODEL_DIR PASSAGES OUT_JSON [--start eos|bos|none] [--llamba TOK_DIR] [--comps conv,mem,attn] [--bs 8] [--groups B0,B1,ALL]"""
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
STATE = {"active": False, "cur": None, "calls": 0, "per_layer": {}}


def sdpa_wrap(q, k, v, *a, **kw):
    if STATE["active"]:
        STATE["calls"] += 1
        vv = v if v.shape[-3] == q.shape[-3] else v.repeat_interleave(q.shape[-3] // v.shape[-3], dim=-3)
        return vv.to(q.dtype)
    if STATE["cur"] is not None:
        STATE["per_layer"][STATE["cur"]] = STATE["per_layer"].get(STATE["cur"], 0) + 1
    return ORIG_SDPA(q, k, v, *a, **kw)


F.scaled_dot_product_attention = sdpa_wrap
torch.nn.functional.scaled_dot_product_attention = sdpa_wrap


@torch.no_grad()
def passage_nll(model, seqs, pad, bs):
    out = []
    for b in range(0, len(seqs), bs):
        chunk = seqs[b:b + bs]
        T = max(map(len, chunk))
        x = torch.full((len(chunk), T), pad, dtype=torch.long)
        for i, s in enumerate(chunk):
            x[i, :len(s)] = torch.tensor(s)
        x = x.cuda()
        lp = model(input_ids=x, use_cache=False).logits.float().log_softmax(-1)
        g = -lp[:, :-1].gather(2, x[:, 1:, None])[..., 0].cpu()
        out += [g[i, :len(s) - 1] for i, s in enumerate(chunk)]
    return torch.cat(out)  # flat, passage order; entry j of passage p predicts token j+1 of seq p


@torch.no_grad()
def last_nll(model, ctxs, targets, bs):
    out = []
    for b in range(0, len(ctxs), bs):
        x = torch.tensor(ctxs[b:b + bs], device="cuda")
        try:
            lg = model(input_ids=x, use_cache=False, logits_to_keep=1).logits[:, -1]
        except TypeError:
            lg = model(input_ids=x, use_cache=False).logits[:, -1]
        lp = lg.float().log_softmax(-1)
        t = torch.tensor(targets[b:b + bs], device="cuda")
        out.append(-lp.gather(1, t[:, None])[:, 0].cpu())
    return torch.cat(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("passages"); ap.add_argument("out")
    ap.add_argument("--start", default="bos"); ap.add_argument("--llamba", default=None)
    ap.add_argument("--comps", default="conv,mem,attn"); ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--groups", default=None)  # subset of group names (B0, B1, ..., ALL); default all
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    if a.llamba:
        import e212_llamba as L
        tok = AutoTokenizer.from_pretrained(a.llamba)
        model = L.load(a.model).cuda().eval()  # as E212 / E217 (fp32)
        layers = list(model.model.layers)
    else:
        tok = AutoTokenizer.from_pretrained(a.model)
        try:
            model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, attn_implementation="sdpa").cuda().eval()
        except ValueError:  # attention-free models (Falcon-Mamba) reject the argument
            model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
        import e195_capture as cap
        _, _, layers = cap.parts(model)
    start = {"eos": tok.eos_token_id, "bos": tok.bos_token_id, "none": None}[a.start]
    pre = [start] if start is not None else []
    off = len(pre)
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    P = json.loads(Path(a.passages).read_text())["passages"]
    seqs, kinds = [], []
    for p in P[:50]:
        ids = enc(p["text"])[:511]
        seqs.append(pre + ids); kinds.append([None] * off + piece_kind(tok, ids))
    # flat index bookkeeping: entry for (passage, t) with t = target position in seq (t >= 1)
    flat_pos, flat_kind, flat_pid = [], [], []
    for pid, (s, kd) in enumerate(zip(seqs, kinds)):
        for t in range(1, len(s)):
            flat_pos.append(t); flat_kind.append(kd[t]); flat_pid.append(pid)
    flat_pos = np.array(flat_pos); flat_pid = np.array(flat_pid)
    is_int = np.array([k == "internal" for k in flat_kind]); is_ini = np.array([k == "initial" for k in flat_kind])
    # layer pre/post hooks: record which layers call SDPA; switch self-only attention for one layer
    target = {"layers": set()}

    def pre_hook(li):
        def f(mod, inp):
            STATE["cur"] = li
            STATE["active"] = (li in target["layers"])
        return f

    def post_hook(mod, inp, out):
        STATE["active"] = False; STATE["cur"] = None

    for li, layer in enumerate(layers):
        layer.register_forward_pre_hook(pre_hook(li)); layer.register_forward_hook(post_hook)
    base = passage_nll(model, seqs, pad, a.bs)
    attn_layers = sorted(k for k, v in STATE["per_layer"].items() if v > 0)
    STATE["cur"] = None
    res = {"model": a.model, "start": a.start, "n_layers": len(layers), "n_tokens": int(base.numel()), "attn_layers": attn_layers,
           "nll_base": base.mean().item(), "nll_base_internal": base[is_int].mean().item(), "nll_base_initial": base[is_ini].mean().item(),
           "n_internal": int(is_int.sum()), "n_initial": int(is_ini.sum())}
    print(f"[{time.time() - t0:.0f}s] base NLL {res['nll_base']:.3f}; attention layers {attn_layers}", flush=True)
    # context-gain tertiles for W = 32, 128
    groups = {}
    for W in (32, 128):
        sel = np.where(flat_pos > W + off)[0]
        ctxs = [pre + seqs[flat_pid[j]][flat_pos[j] - W:flat_pos[j]] for j in sel]
        tg = [seqs[flat_pid[j]][flat_pos[j]] for j in sel]
        wn = last_nll(model, ctxs, tg, 256 if W == 32 else 64)
        gain = (wn - base[sel]).numpy()
        q1, q2 = np.quantile(gain, [1 / 3, 2 / 3])
        groups[W] = [sel[gain <= q1], sel[(gain > q1) & (gain <= q2)], sel[gain > q2]]
        res[f"gain_w{W}"] = {"mean": float(gain.mean()), "q1": float(q1), "q2": float(q2), "n": int(len(sel)),
                             "nll_base_by_tertile": [base[g].mean().item() for g in groups[W]]}
        print(f"[{time.time() - t0:.0f}s] W={W}: mean gain {gain.mean():.3f}, tertile cuts {q1:.3f} / {q2:.3f}", flush=True)
    # conv means for every short conv in the model (one pass), fallback zero
    comps = a.comps.split(",")
    convs = {li: e209.short_convs(layer) for li, layer in enumerate(layers)}
    all_convs = [m for li in convs for _, m in convs[li]]
    mus, conv_mode = {}, "none"
    if "conv" in comps and all_convs:
        try:
            ms = e209.conv_input_means(model, tok, start, a.passages, all_convs)
            mus = {id(m): mu for m, mu in zip(all_convs, ms)}; conv_mode = "mean"
        except AssertionError as e:
            print("conv input capture failed -> zero ablation:", e, flush=True); conv_mode = "zero"
    res["conv_mode"] = conv_mode
    mems = {li: [m for _, m in layer.named_modules() if (hasattr(m, "A_log") and isinstance(getattr(m, "A_log"), torch.nn.Parameter)) or hasattr(m, "nomem")]
            for li, layer in enumerate(layers)}

    def stats(nll):
        d = nll - base
        r = {"dnll": d.mean().item(), "dnll_internal": d[is_int].mean().item(), "dnll_initial": d[is_ini].mean().item()}
        for W, gs in groups.items():
            r[f"dnll_w{W}"] = [d[g].mean().item() for g in gs]
        return r

    runs = []
    L = len(layers)
    allg = [(f"B{b}", list(range(4 * b, min(4 * b + 4, L)))) for b in range((L + 3) // 4)] + [("ALL", list(range(L)))]
    if a.groups:
        keep = set(a.groups.split(",")); allg = [g for g in allg if g[0] in keep]
    for gname, lys in allg:
        for c in comps:
            if c == "conv":
                mods = [m for li in lys for _, m in convs[li]]
                if not mods:
                    continue
                saved = []
                with torch.no_grad():
                    for m in mods:
                        saved.append((m, m.weight.data.clone(), None if m.bias is None else m.bias.data.clone()))
                        if conv_mode == "mean":
                            d = (m.weight[:, 0, :-1].float() * mus[id(m)][:, None]).sum(-1).to(m.weight.dtype)
                            if m.bias is None:
                                m.bias = torch.nn.Parameter(d, requires_grad=False)
                            else:
                                m.bias.data += d
                        m.weight.data[..., :-1] = 0
                nll = passage_nll(model, seqs, pad, a.bs)
                with torch.no_grad():
                    for m, w, b in saved:
                        m.weight.data.copy_(w)
                        if b is None:
                            m.register_parameter("bias", None)
                        else:
                            m.bias.data.copy_(b)
                n_mod = len(saved)
            elif c == "mem":
                mods = [m for li in lys for m in mems[li]]
                if not mods:
                    continue
                saved = []
                with torch.no_grad():
                    for m in mods:
                        if hasattr(m, "nomem"):
                            m.nomem = True; saved.append((m, None))
                        else:
                            saved.append((m, m.A_log.data.clone())); m.A_log.data += 20
                nll = passage_nll(model, seqs, pad, a.bs)
                with torch.no_grad():
                    for m, sv in saved:
                        if sv is None:
                            m.nomem = False
                        else:
                            m.A_log.data.copy_(sv)
                n_mod = len(saved)
            elif c == "attn":
                al = [li for li in lys if li in attn_layers]
                if not al:
                    continue
                STATE["calls"] = 0; target["layers"] = set(al)
                nll = passage_nll(model, seqs, pad, a.bs)
                target["layers"] = set()
                assert STATE["calls"] > 0, f"self-only attention not applied in {gname}"
                n_mod = len(al)
            else:
                continue
            runs.append({"group": gname, "layers": lys, "comp": c, "n_mod": n_mod, **stats(nll)})
            r = runs[-1]
            print(f"[{time.time() - t0:.0f}s] {gname:4s} {c:4s} n={n_mod} dNLL {r['dnll']:+.3f} int {r['dnll_internal']:+.3f} ini {r['dnll_initial']:+.3f} "
                  f"w32 near/mid/far {' '.join(f'{x:+.3f}' for x in r['dnll_w32'])}", flush=True)
            res["runs"] = runs
            Path(a.out).write_text(json.dumps(res))
    # sanity: baseline restored
    chk = passage_nll(model, seqs, pad, a.bs)
    res["restore_check_max_abs"] = (chk - base).abs().max().item()
    res["runs"] = runs; res["sec"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(res))
    print(f"E220_MODEL_DONE {a.model} restore_check {res['restore_check_max_abs']:.2e} sec {res['sec']}", flush=True)


if __name__ == "__main__":
    main()
