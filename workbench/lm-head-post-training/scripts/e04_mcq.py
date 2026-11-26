"""E04-C: separate a global answer preference from within-question discrimination on multiple choice.

Same four candidate tokens (A/B/C/D) for every question; the correct one varies with the question.
A context-independent affine map τ·z + b can only change the model's overall preference among the four letters
(and the sharpness), never their ranking within a question once that preference is removed. So we report per model:
  acc          : argmax over the 4 letter logits at the first answer position
  acc_calib    : argmax after subtracting the model's mean letter log-prob over all questions (contextual
                 calibration); this number is exactly invariant to any global τ>0, b — gains in it cannot come
                 from a global preference
  letter_mass  : probability mass on the 4 letters (format adherence), pred_entropy of the predicted-letter histogram
Plus parent + (τ,b) and child − (τ,b) using the E04-A fits.

Usage: python e04_mcq.py <pair_key> --template qwen_chat|child_chat [--n_mmlu 1500]
"""
import argparse
import gc
import json
import os
from pathlib import Path

import numpy as np
import torch

import models

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")


def questions(n_mmlu, seed=0):
    import datasets
    qs = []
    for r in datasets.load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test"):
        if r["choices"]["label"] == ["A", "B", "C", "D"]:
            qs.append(("arc", r["question"], r["choices"]["text"], "ABCD".index(r["answerKey"])))
    m = datasets.load_dataset("cais/mmlu", "all", split="test")
    idx = np.random.default_rng(seed).choice(len(m), n_mmlu, replace=False)
    for i in sorted(idx):
        r = m[int(i)]
        qs.append(("mmlu", r["question"], r["choices"], int(r["answer"])))
    return qs


def render(tok, q, ch):
    body = q + "\n" + "\n".join(f"{l}. {c}" for l, c in zip("ABCD", ch)) + "\nAnswer with the letter of the correct option only."
    kw = {"enable_thinking": False} if "enable_thinking" in (tok.chat_template or "") else {}
    return tok.apply_chat_template([{"role": "user", "content": body}], tokenize=False, add_generation_prompt=True, **kw)


@torch.no_grad()
def letter_logits(name, prompts, tok, letter_ids, dev, bs=16):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(models.path(name), dtype=torch.bfloat16).to(dev).eval()
    full_lse, lets = [], []
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    for i in range(0, len(prompts), bs):
        enc = tok(prompts[i:i + bs], return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
        z = m(**enc).logits[:, -1].float()
        full_lse.append(torch.logsumexp(z, -1).cpu()); lets.append(z[:, letter_ids].cpu())
    del m; gc.collect(); torch.cuda.empty_cache()
    return torch.cat(lets).numpy(), torch.cat(full_lse).numpy()


def readout(L, lse, gold, src):
    """L: (n,4) letter logits after any intervention; lse: logsumexp over the full vocab (same intervention)."""
    lp = L - np.logaddexp.reduce(L, axis=1, keepdims=True)
    pred = lp.argmax(1)
    calib = (lp - lp.mean(0, keepdims=True)).argmax(1)
    hist = np.bincount(pred, minlength=4) / len(pred)
    out = {"acc": float((pred == gold).mean()), "acc_calib": float((calib == gold).mean()),
           "letter_mass": float(np.exp(np.logaddexp.reduce(L, axis=1) - lse).mean()),
           "pred_hist": hist.round(3).tolist(), "pred_entropy": float(-(hist[hist > 0] * np.log(hist[hist > 0])).sum())}
    for s in ("arc", "mmlu"):
        k = src == s
        out[f"acc_{s}"] = float((pred[k] == gold[k]).mean()); out[f"acc_calib_{s}"] = float((calib[k] == gold[k]).mean())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--n_mmlu", type=int, default=1500)
    args = ap.parse_args()
    dev = "cuda"
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))          # child's chat template for both models
    qs = questions(args.n_mmlu)
    prompts = [render(tok, q, ch) for _, q, ch, _ in qs]
    gold = np.array([g for *_, g in qs]); src = np.array([s for s, *_ in qs])
    letter_ids = [tok.convert_tokens_to_ids(l) for l in "ABCD"]
    L0, lse0 = letter_logits(p0, prompts, tok, letter_ids, dev)
    L1, lse1 = letter_logits(p1, prompts, tok, letter_ids, dev)
    res = {"pair": args.pair, "stage": stage, "n": len(qs), "n_arc": int((src == "arc").sum()), "letter_ids": letter_ids,
           "example_prompt": prompts[0][-300:], "parent": readout(L0, lse0, gold, src), "child": readout(L1, lse1, gold, src)}
    fit = Path(f"/tmp/xiang_lmhead/e04/fit_{args.pair}.npz")
    if fit.exists():
        F = np.load(fit)
        for s in ("neutral", "gen_parent", "gen_child"):
            if f"{s}.tau_bias.b" not in F:
                continue
            tau, b = float(F[f"{s}.tau_bias.tau"]), F[f"{s}.tau_bias.b"]
            bl = b[letter_ids]
            # the full-vocab logsumexp under the intervention is not needed for ranking; letter_mass reported as NaN
            res[f"parent_plus_{s}"] = readout(tau * L0 + bl, np.full(len(L0), np.nan), gold, src)
            res[f"child_minus_{s}"] = readout((L1 - bl) / tau, np.full(len(L1), np.nan), gold, src)
    out = ROOT / "results" / "e04"; out.mkdir(parents=True, exist_ok=True)
    (out / f"mcq_{args.pair}.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        if isinstance(v, dict):
            print(k, {kk: v[kk] for kk in ("acc", "acc_calib", "letter_mass", "pred_hist")})


if __name__ == "__main__":
    main()
