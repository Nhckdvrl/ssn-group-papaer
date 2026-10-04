"""ParaConflict items, prompt construction, candidate scoring and probe material shared by the experiments."""
import json
import os

import numpy as np
import torch
from datasets import load_dataset

import common as mc


FORMS = ["Substitution Conflict", "Coherent Conflict"]


def rows():
    ds = load_dataset("gaotang/ParaConflict", split="test")
    out = []
    for r in ds:
        ans = r["Answer"] if isinstance(r["Answer"], list) else [r["Answer"]]
        out.append({"cat": r["Category"], "subj": r["Subject"], "ans": ans[0], "dist": r["Distracted Token"],
                    "clean": r["Clean Prompt"], **{f: r[f] for f in FORMS}})
    return out


@torch.no_grad()
def cand_logprob(model, tok, prompts, cands, bs=32):
    """Sum log-prob of ' '+cand after prompt; sequence starts with EOS (OLMo document separator)."""
    out = []
    for i in range(0, len(prompts), bs):
        P, C = prompts[i:i + bs], cands[i:i + bs]
        pi = [tok(p, add_special_tokens=False)["input_ids"] for p in P]
        ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in C]
        seqs = [[tok.eos_token_id] + a + b for a, b in zip(pi, ci)]
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), tok.pad_token_id)
        att = torch.zeros((len(seqs), L), dtype=torch.long)
        for j, s in enumerate(seqs):
            ids[j, :len(s)] = torch.tensor(s)
            att[j, :len(s)] = 1
        logp = model(ids.to(model.device), attention_mask=att.to(model.device)).logits.float().log_softmax(-1)
        for j, (a, b) in enumerate(zip(pi, ci)):
            st = 1 + len(a)
            pos = torch.arange(st - 1, st - 1 + len(b), device=logp.device)
            out.append(float(logp[j, pos, torch.tensor(b, device=logp.device)].sum()))
    return np.array(out)


FILLER = ("Weather patterns change slowly over the course of a season. In the early part of the year, mornings are "
          "often cool and the air feels damp, while afternoons bring brief periods of sunshine. Clouds tend to gather "
          "in the late afternoon and drift away again before evening. Rain usually arrives in light showers rather "
          "than heavy storms, and the ground dries quickly once the wind picks up. As the days grow longer, the "
          "temperature rises gradually and the evenings remain pleasant for walking. Trees begin to show new leaves, "
          "and gardens fill with color as flowers open one after another. Later in the season the air becomes "
          "warmer and drier, and people spend more time outdoors in parks and open fields. Toward the end of the "
          "season the light softens, the nights become cooler, and the first signs of autumn appear in the changing "
          "colors of the leaves. Many people find this gradual change calming, and they enjoy noticing small "
          "differences from one week to the next as the landscape slowly takes on a new appearance.").split()


def filler(n):
    """Whole sentences of the neutral filler whose word count is closest to n (no mid-sentence cuts)."""
    words = FILLER * 3
    ends = [i + 1 for i, w in enumerate(words) if w.endswith(".")]
    best = min([0] + ends, key=lambda e: abs(e - n))
    return " ".join(words[:best])


def build(r):
    coh = r["Coherent Conflict"]
    i = coh.rfind(" Question:")
    P, tail = coh[:i].strip(), coh[i + len(" Question:"):]
    q, stem = tail.split(" Answer:")
    q, stem = q.strip(), stem.strip()
    sub = r["Substitution Conflict"]
    S = sub[:sub.find(r["dist"]) + len(r["dist"])].strip()
    if not S.endswith("."):
        S += "."
    k = P.count(r["dist"])
    nfill = max(0, len(P.split()) - len(S.split()))
    F = filler(nfill)
    ctx = {"c1": S, "cK": " ".join([S] * k), "cP": P, "cF": (F + " " + S).strip()}
    out = {}
    for c, t in ctx.items():
        out[f"{c}_decl"] = t + " " + stem
        out[f"{c}_qa"] = t + " Question: " + q + " Answer: " + stem
    return out, k


K_HEADS, N_ITEMS = 10, 300


def items():
    """Balanced subsample (50 per category) of items known by all 6 habit_format Flan-pair models."""
    import datadecide as dd
    R = rows()
    known = [set(json.loads((mc.RESULTS / "habit_format" / f"{r}__{s}.json").read_text())["known"])
             for r in ("dolma1_7-1B", "dolma1_7-no-flan-1B") for s in dd.SEEDS]
    shared = sorted(set.intersection(*known))
    rng = np.random.default_rng(0)
    out = []
    for c in sorted({r["cat"] for r in R}):
        ix = [i for i in shared if R[i]["cat"] == c]
        out += sorted(rng.choice(ix, min(N_ITEMS // 6, len(ix)), replace=False).tolist())
    return R, out


def encode(tok, prompt, dist):
    """Token ids (EOS-prefixed) and index of the first token overlapping the first occurrence of `dist`."""
    enc = tok(prompt, add_special_tokens=False, return_offsets_mapping=True)
    a = prompt.find(dist)
    pos = [j for j, (s, e) in enumerate(enc["offset_mapping"]) if s < a + len(dist) and e > a]
    return [tok.eos_token_id] + enc["input_ids"], 1 + pos[0]


_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))


def natural_texts(tok, n=50, length=256):
    import torch
    from transformers import AutoTokenizer
    src = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", cache_dir=str(mc.HF_CACHE))
    toks = torch.load(_CACHE + "/pile_eval_2000_seed42.pt")["tokens"]
    out = []
    for row in toks:
        ids = tok(src.decode(row[:400]), add_special_tokens=False)["input_ids"]
        if len(ids) >= length:
            out.append([tok.eos_token_id] + ids[:length])
        if len(out) == n:
            break
    return out
