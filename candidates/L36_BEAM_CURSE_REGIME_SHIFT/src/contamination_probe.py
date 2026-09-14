"""E00 Gate C.4 — bounded memorization probe for the selected modern checkpoint.

Two signals on the frozen newstest2019 substrate:

1. teacher-forced mean per-token NLL of the official WMT reference vs the AR reference, given the
   same source and prompt.  The WMT reference is mirrored far more widely on the web than the AR
   file, so a large NLL advantage for the WMT reference is a (weak) memorization signal;
2. prefix-continuation exact-match rate: give the model the source plus the first 50% of the WMT
   reference and greedily continue; verbatim completion of the remainder is a stronger signal.

Predeclared flags (E00 §C.4): exact-match rate > 5%, or NLL_wmt lower than NLL_ar by > 0.5 nats.
This probe cannot prove the absence of contamination and is reported as such.
"""

import argparse
import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_llm_mt import PROMPT, clean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision", default="main")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "e00", "contamination_probe.json"))
    a = ap.parse_args()

    data = os.path.join(ROOT, "data")
    src = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.en"), encoding="utf-8")][:a.n]
    ref_wmt = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.wmtref.de"), encoding="utf-8")][:a.n]
    ref_ar = [l.rstrip("\n") for l in open(os.path.join(data, "newstest2019.arref.de"), encoding="utf-8")][:a.n]

    tok = AutoTokenizer.from_pretrained(a.model, revision=a.revision)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, revision=a.revision, dtype=getattr(torch, a.dtype), device_map="cuda").eval()

    def prompt_ids(s):
        msg = [{"role": "user", "content": PROMPT.format(src=s)}]
        text = tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        return tok(text, add_special_tokens=False)["input_ids"]

    def nll(s, target):
        p = prompt_ids(s)
        t = tok(" " + target, add_special_tokens=False)["input_ids"]
        ids = torch.tensor([p + t], device="cuda")
        with torch.no_grad():
            logits = model(ids).logits.float()
        lp = torch.log_softmax(logits[0, :-1], dim=-1)
        tgt = ids[0, 1:]
        sel = lp.gather(1, tgt.unsqueeze(1)).squeeze(1)[len(p) - 1:]
        return float(-sel.mean()), len(t)

    nll_wmt, nll_ar, exact = [], [], []
    for i, (s, rw, ra) in enumerate(zip(src, ref_wmt, ref_ar)):
        n1, _ = nll(s, rw)
        n2, _ = nll(s, ra)
        nll_wmt.append(n1)
        nll_ar.append(n2)

        words = rw.split()
        if len(words) >= 8:
            half = len(words) // 2
            prefix, rest = " ".join(words[:half]), " ".join(words[half:])
            p = prompt_ids(s) + tok(" " + prefix, add_special_tokens=False)["input_ids"]
            ids = torch.tensor([p], device="cuda")
            with torch.no_grad():
                out = model.generate(ids, do_sample=False, max_new_tokens=len(rest.split()) * 4 + 8,
                                     pad_token_id=tok.pad_token_id)
            cont = clean(tok.decode(out[0, len(p):], skip_special_tokens=True))
            exact.append(1.0 if cont.strip() == rest.strip() else 0.0)
        if i % 100 == 0:
            print(f"  {i}/{len(src)}", flush=True)

    import numpy as np
    res = {
        "model": a.model, "revision": a.revision, "n": len(src),
        "nll_wmt_mean": float(np.mean(nll_wmt)),
        "nll_ar_mean": float(np.mean(nll_ar)),
        "nll_gap_ar_minus_wmt": float(np.mean(nll_ar) - np.mean(nll_wmt)),
        "prefix_exact_match_rate": float(np.mean(exact)) if exact else None,
        "n_prefix_items": len(exact),
        "flags": {
            "exact_match_gt_5pct": bool(np.mean(exact) > 0.05) if exact else None,
            "nll_gap_gt_0.5": bool(np.mean(nll_ar) - np.mean(nll_wmt) > 0.5),
        },
        "note": ("Weak instrument: a negative result does not establish the absence of "
                 "pretraining contamination."),
    }
    res["contamination_warning"] = bool(res["flags"]["exact_match_gt_5pct"] or res["flags"]["nll_gap_gt_0.5"])
    with open(a.out, "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
