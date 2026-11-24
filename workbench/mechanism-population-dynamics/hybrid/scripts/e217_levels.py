#!/usr/bin/env python3
"""E217: four-level locality readouts under switches in layers 0-2.
  1. word-internal vs word-initial token NLL on EWT passages 0-199 (no artificial splits)
  2. multi-word-expression advantage: log P(w2 | w1) - log P(w2 | other w1), w1/w2 single tokens, 3 neutral prefixes
  3. BLiMP local agreement (determiner_noun_agreement_1/2, regular_plural_subject_verb_agreement_1)
  4. BLiMP distant agreement (distractor_agreement_relative_clause / relational_noun)
COND: none | conv (zero neighbour taps) | convmean (E209 mean ablation) | mem (A_log += 20) | attn (zero attention output)
Usage: e217_levels.py MODEL_DIR PASSAGES BLIMP_DIR OUT_JSON COND [--start eos|bos|none] [--llamba TOK_DIR]"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent))

LAYERS = (0, 1, 2)
MWE = ["New York", "ice cream", "hot dog", "United States", "high school", "real estate", "prime minister", "climate change",
       "credit card", "social media", "health care", "vice president", "middle class", "law enforcement", "human rights",
       "public health", "red carpet", "black hole", "solar system", "stock market", "swimming pool", "parking lot",
       "living room", "science fiction", "video game", "weather forecast", "peanut butter", "orange juice", "olive oil",
       "fast food", "coffee shop", "birthday party", "police officer", "fire truck", "grocery store", "phone number",
       "email address", "interest rate", "supply chain", "power plant", "cell phone", "remote control", "traffic light",
       "speed limit", "seat belt", "hard drive", "operating system", "search engine", "machine learning",
       "artificial intelligence", "natural language", "global warming", "carbon dioxide", "blood pressure", "heart attack",
       "mental health", "White House", "Middle East", "South Africa", "North Korea", "Hong Kong", "Los Angeles",
       "San Francisco", "Wall Street", "Silicon Valley", "Star Wars", "real time", "long term", "short term", "open source",
       "World War", "civil war", "Cold War", "nuclear weapons", "Supreme Court", "high quality", "free trade",
       "data center", "front door", "back pain", "side effects", "cash flow", "bank account", "air force", "foreign policy",
       "tax cuts", "minimum wage", "board game", "golf course", "test score", "car accident", "fire alarm", "train station",
       "bus stop", "post office", "city hall", "town square", "summer vacation", "winter coat"]
TEMPLATES = ["We talked about the", "There was a long article about the", "I keep hearing about the"]
LOCAL = ["determiner_noun_agreement_1", "determiner_noun_agreement_2", "regular_plural_subject_verb_agreement_1"]
DISTANT = ["distractor_agreement_relative_clause", "distractor_agreement_relational_noun"]


def logits_fn(model):
    return lambda x: model(input_ids=x, use_cache=False).logits.float()


@torch.no_grad()
def seq_logprobs(model, seqs, pad, bs=32):
    """Per-sequence list of token log-probs for positions 1..n-1."""
    out = []
    for b in range(0, len(seqs), bs):
        chunk = seqs[b:b + bs]
        T = max(map(len, chunk))
        x = torch.full((len(chunk), T), pad, dtype=torch.long)
        for i, s in enumerate(chunk):
            x[i, :len(s)] = torch.tensor(s)
        x = x.cuda()
        lp = model(input_ids=x, use_cache=False).logits.float().log_softmax(-1)
        g = lp[:, :-1].gather(2, x[:, 1:, None])[..., 0].cpu()
        out += [g[i, :len(s) - 1] for i, s in enumerate(chunk)]
    return out


def piece_kind(tok, ids):
    strs = tok.convert_ids_to_tokens(ids)
    kinds = []
    for j, s in enumerate(strs):
        body = s.lstrip("Ġ▁ ")
        initial = s[:1] in ("Ġ", "▁", " ")
        if not body.isalpha():
            kinds.append(None)
        elif initial:
            kinds.append("initial")
        else:
            prev = strs[j - 1].lstrip("Ġ▁ ") if j > 0 else ""
            kinds.append("internal" if prev[-1:].isalpha() else None)
    return kinds


def apply(model, cond, base_layers, passages, tok, start):
    done = []
    if cond == "convmean":
        import e209_run as e209
        targets = [(li, m) for li in LAYERS for _, m in e209.short_convs(base_layers[li])]
        mus = e209.conv_input_means(model, tok, start, passages, [m for _, m in targets])
        with torch.no_grad():
            for (li, m), mu in zip(targets, mus):
                w = m.weight; d = (w[:, 0, :-1].float() * mu[:, None]).sum(-1)
                if m.bias is None:
                    m.bias = torch.nn.Parameter(d.to(w.dtype), requires_grad=False)
                else:
                    m.bias += d.to(w.dtype)
                w[..., :-1] = 0; done.append(f"{li}:convmean")
    for li in LAYERS:
        layer = base_layers[li]
        with torch.no_grad():
            if cond == "conv":
                import e209_run as e209
                for name, m in e209.short_convs(layer):
                    m.weight[..., :-1] = 0; done.append(f"{li}:{name}")
            if cond == "mem":
                for name, m in layer.named_modules():
                    if hasattr(m, "A_log") and isinstance(getattr(m, "A_log"), torch.nn.Parameter):
                        m.A_log += 20; done.append(f"{li}:{name}.A_log")
        if cond == "attn":
            attn = getattr(layer, "self_attn", None)
            assert attn is not None, f"layer {li} has no self_attn"
            attn.register_forward_hook(lambda mod, i, o: ((torch.zeros_like(o[0]),) + tuple(o[1:])) if isinstance(o, tuple) else torch.zeros_like(o))
            done.append(f"{li}:attn")
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("passages"); ap.add_argument("blimp"); ap.add_argument("out"); ap.add_argument("cond")
    ap.add_argument("--start", default="bos"); ap.add_argument("--llamba", default=None)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if a.llamba:
        import e212_llamba as L
        tok = AutoTokenizer.from_pretrained(a.llamba)
        model = L.load(a.model).cuda().eval()
        layers = model.model.layers
    else:
        tok = AutoTokenizer.from_pretrained(a.model)
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
        import e195_capture as cap
        _, _, layers = cap.parts(model)
    start = {"eos": tok.eos_token_id, "bos": tok.bos_token_id, "none": None}[a.start]
    pre = [start] if start is not None else []
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    P = json.loads(Path(a.passages).read_text())["passages"]
    if a.llamba:
        done = []
        if a.cond == "convmean":
            for li in LAYERS:
                layers[li].mixer.stat = [torch.zeros(layers[li].mixer.conv_dim, dtype=torch.float64, device="cuda"), 0]
            with torch.no_grad():
                for p in P[50:150]:
                    model(torch.tensor([pre + enc(p["text"])[:511]], device="cuda"))
            with torch.no_grad():
                for li in LAYERS:
                    mx = layers[li].mixer; mu = (mx.stat[0] / mx.stat[1]).float(); mx.stat = None
                    mx.conv1d.bias += (mx.conv1d.weight[:, 0, :-1] * mu[:, None]).sum(-1); mx.conv1d.weight[..., :-1] = 0
                    done.append(f"{li}:convmean")
        if a.cond == "mem":
            for li in LAYERS:
                layers[li].mixer.nomem = True; done.append(f"{li}:nomem")
    else:
        done = apply(model, a.cond, layers, a.passages, tok, start)
    assert a.cond == "none" or done, "nothing switched"
    res = {"model": a.model, "cond": a.cond, "switched": done[:12], "n_switched": len(done)}
    # 1. word-internal vs word-initial NLL
    seqs, kinds = [], []
    for p in P[:200]:
        ids = enc(p["text"])[:511]
        seqs.append(pre + ids); kinds.append(piece_kind(tok, ids))
    lps = seq_logprobs(model, seqs, pad, bs=8)
    acc = {"internal": [], "initial": []}
    for lp, kd in zip(lps, kinds):
        off = len(pre)
        for j, k in enumerate(kd):
            t = off + j  # position in seq; its log-prob is lp[t-1]
            if k and t >= 1:
                acc[k].append(-lp[t - 1].item())
    res["nll_internal"] = sum(acc["internal"]) / len(acc["internal"]); res["n_internal"] = len(acc["internal"])
    res["nll_initial"] = sum(acc["initial"]) / len(acc["initial"]); res["n_initial"] = len(acc["initial"])
    allt = torch.cat([lp for lp in lps[:50]]); res["nll_all50"] = (-allt).mean().item()
    # 2. MWE advantage
    pairs = []
    for e in MWE:
        w1, w2 = e.split(" ")
        i1, i2 = enc(" " + w1), enc(" " + w2)
        if len(i1) == 1 and len(i2) == 1:
            pairs.append((i1[0], i2[0]))
    rng = random.Random(217)
    ctrl = [pairs[(i + 1 + rng.randrange(len(pairs) - 1)) % len(pairs)][0] for i in range(len(pairs))]
    s_true, s_ctrl = [], []
    for tmpl in TEMPLATES:
        t = enc(tmpl)
        for (i1, i2), c1 in zip(pairs, ctrl):
            s_true.append(pre + t + [i1, i2]); s_ctrl.append(pre + t + [c1, i2])
    lt = seq_logprobs(model, s_true, pad); lc = seq_logprobs(model, s_ctrl, pad)
    adv = [a_[-1].item() - c_[-1].item() for a_, c_ in zip(lt, lc)]
    res["mwe_adv"] = sum(adv) / len(adv); res["mwe_n_pairs"] = len(pairs)
    res["mwe_logp_true"] = sum(a_[-1].item() for a_ in lt) / len(lt)
    # 3/4. BLiMP
    for para in LOCAL + DISTANT:
        rows = [json.loads(l) for l in (Path(a.blimp) / f"{para}.jsonl").read_text().splitlines() if l.strip()]
        good = seq_logprobs(model, [pre + enc(r["sentence_good"]) for r in rows], pad, bs=64)
        bad = seq_logprobs(model, [pre + enc(r["sentence_bad"]) for r in rows], pad, bs=64)
        res[f"blimp_{para}"] = sum(float(g.sum() > b.sum()) for g, b in zip(good, bad)) / len(rows)
    res["blimp_local"] = sum(res[f"blimp_{p}"] for p in LOCAL) / len(LOCAL)
    res["blimp_distant"] = sum(res[f"blimp_{p}"] for p in DISTANT) / len(DISTANT)
    Path(a.out).write_text(json.dumps(res))
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k not in ("switched",)}), flush=True)


if __name__ == "__main__":
    main()
