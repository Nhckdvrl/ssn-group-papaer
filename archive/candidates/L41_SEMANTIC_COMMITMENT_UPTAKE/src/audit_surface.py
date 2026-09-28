"""E01-A surface / tokenization / surprisal audit.

Beyond the token counts required by PILOT_CARD.md §4 this also records the
base-model NLL of each arm's critical sentence.  Rationale: a pure
mention/co-occurrence learner still moves more on higher-surprisal documents,
so a verb x polarity interaction in *document surprisal* could by itself
produce a nonzero checkerboard interaction `I`.  We must be able to report
whether such an interaction exists in the treatment material.
"""
import sys, os, json, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
import torch
from generator import generate, CRITICAL, DIRECT
from docs import docs_for, SHELLS
from scoring import load_base

CELLS = CRITICAL + DIRECT

@torch.no_grad()
def seq_nll(model, tok, texts, bs=16):
    """Mean per-token NLL for each text (no context)."""
    out = []
    tok.padding_side = "right"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    for i in range(0, len(texts), bs):
        ch = texts[i:i+bs]
        enc = tok(ch, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        logits = model(**enc).logits.float()
        ids, am = enc["input_ids"], enc["attention_mask"]
        lp = torch.log_softmax(logits[:, :-1], -1)
        tgt = ids[:, 1:]
        tl = lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
        m = am[:, 1:].float()
        out.extend(((-(tl*m).sum(1))/m.sum(1)).tolist())
    return out

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    props = generate("dev", n)
    model, tok = load_base()
    rep = {"n": n, "cells": {}}
    for c in CELLS:
        sents = [p["sent"][c] for p in props]
        docs = [d for p in props for d in docs_for(p, c, 4)]
        s_tok = [len(tok.encode(s, add_special_tokens=False)) for s in sents]
        d_tok = [len(tok.encode(d, add_special_tokens=False)) for d in docs]
        s_nll = seq_nll(model, tok, sents)
        d_nll = seq_nll(model, tok, docs)
        rep["cells"][c] = {
            "sent_tokens_mean": st.mean(s_tok),
            "doc_tokens_mean": st.mean(d_tok),
            "sent_nll_mean": st.mean(s_nll), "sent_nll_sd": st.pstdev(s_nll),
            "doc_nll_mean": st.mean(d_nll), "doc_nll_sd": st.pstdev(d_nll),
            "example": sents[0],
        }
    # verb x polarity interactions in the treatment material itself
    g = lambda c, k: rep["cells"][c][k]
    for k in ["doc_nll_mean", "doc_tokens_mean", "sent_nll_mean"]:
        rep[f"interaction_{k}"] = (g("Mp",k)-g("Mn",k)) - (g("Fp",k)-g("Fn",k))
    print(f"{'cell':4} {'sentTok':>8} {'docTok':>7} {'sentNLL':>8} {'docNLL':>8}   example")
    for c in CELLS:
        d = rep["cells"][c]
        print(f"{c:4} {d['sent_tokens_mean']:8.2f} {d['doc_tokens_mean']:7.2f} "
              f"{d['sent_nll_mean']:8.3f} {d['doc_nll_mean']:8.3f}   {d['example']}")
    print()
    for k in ["doc_nll_mean", "doc_tokens_mean", "sent_nll_mean"]:
        print(f"  verb x polarity interaction in {k:16}: {rep['interaction_'+k]:+.4f}")
    json.dump(rep, open("results/e01a/surface_audit.json", "w"), indent=2)

if __name__ == "__main__":
    main()
