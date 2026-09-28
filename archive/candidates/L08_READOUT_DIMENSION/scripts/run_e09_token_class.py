"""E09 — does truncation demote structural tokens beyond what their margin predicts?

E06 fitted survival as a function of the full model's decision margin and found one
systematic failure: the step at which the model must emit the GSM8K answer marker
'####' has a comfortable margin (4.88) and a predicted survival of 0.759, but an
observed survival of 0.097.  E08 then showed that handing the model that marker turns
a literal 0.000 into 0.178.  And in free running, Llama with the `first` mask emits
'####' in 0 of 500 GSM8K outputs.

Zero of 500 is not a graded effect.  This experiment asks whether particular *classes*
of token become unreachable under truncation, at margins where content tokens survive.

At every position of natural text we record the full model's arg max, its margin, and
whether it survives truncation -- then stratify by what kind of token it is, and
compare classes **within margin bins** so that the comparison is not just restating
that structural tokens have different margins.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys, time, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import tasks
from src.readout import ReadoutTruncation, build_mask, mask_id

DIGIT = re.compile(r"^\s*[\d,.]+$")
PUNCT = re.compile(r"^\s*[^\w\s]+$")
WORDY = re.compile(r"^\s*[A-Za-z][A-Za-z']*$")


def classify(s, tid, eos_ids):
    if tid in eos_ids: return "eos/special"
    if "#" in s or "<|" in s: return "structural marker"
    if s in ("\n", "\n\n", " \n") or s.strip() == "" and "\n" in s: return "newline"
    if DIGIT.match(s): return "number"
    if PUNCT.match(s): return "punctuation"
    if WORDY.match(s): return "word"
    return "other"


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--n-prompts", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    dev = model.lm_head.weight.device
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)
    eos_ids = {tok.eos_token_id} | set(tok.all_special_ids or [])

    prompts = [it["prompt"] for it in tasks.build_gsm8k(a.n_prompts, 4242, cot=True)]
    rows = []
    t0 = time.time()
    for p in prompts:
        ids = tok(p, return_tensors="pt", truncation=True,
                  max_length=1536)["input_ids"].to(dev)
        if ids.shape[1] < 16: continue
        full = model(input_ids=ids).logits[0].float()
        with ReadoutTruncation(model, mask):
            trunc = model(input_ids=ids).logits[0].float()
        top2 = torch.topk(full, 2, dim=-1)
        ref = top2.indices[:, 0]
        marg = top2.values[:, 0] - top2.values[:, 1]
        surv = (trunc.argmax(-1) == ref)
        # rank the reference token now has under truncation
        rank = (trunc > trunc.gather(1, ref[:, None])).sum(1)
        for t in range(0, full.shape[0], 2):          # subsample positions
            tid = int(ref[t])
            rows.append((classify(tok.decode([tid]), tid, eos_ids),
                         float(marg[t]), bool(surv[t]), int(rank[t])))

    cls = collections.defaultdict(list)
    for c, m, sv, r in rows: cls[c].append((m, sv, r))   # (margin, survived, rank)
    edges = [0, 1, 2, 4, 8, 1e9]

    rep = {"model": a.model, "mask": a.mask, "mask_id": mask_id(mask),
           "n_positions": len(rows), "runtime_s": round(time.time() - t0, 1),
           "overall_survival": float(np.mean([s for _, _, s, _ in rows])),
           "by_class": {}, "by_class_and_margin": {}}
    print(f"{'class':<20}{'n':>7}{'share':>7}{'margin_med':>11}{'survival':>10}{'med_rank':>9}")
    for c, v in sorted(cls.items(), key=lambda kv: -len(kv[1])):
        m = np.array([x[0] for x in v]); s = np.array([x[1] for x in v], dtype=float)
        r = np.array([x[2] for x in v], dtype=float)
        rep["by_class"][c] = {"n": len(v), "margin_median": float(np.median(m)),
                              "survival": float(s.mean()),
                              "median_rank_under_trunc": float(np.median(r))}
        print(f"{c:<20}{len(v):>7}{len(v)/len(rows):>7.3f}{np.median(m):>11.2f}"
              f"{s.mean():>10.3f}{np.median(r):>9.0f}")

    print(f"\nsurvival within margin bins (controls for the classes having "
          f"different margins):")
    hdr = "  ".join(f"[{edges[i]:g},{edges[i+1]:g})" for i in range(len(edges) - 1))
    print(f"{'class':<20}{hdr}")
    for c, v in sorted(cls.items(), key=lambda kv: -len(kv[1])):
        m = np.array([x[0] for x in v]); s = np.array([x[1] for x in v], dtype=float)
        cells, line = {}, []
        for i in range(len(edges) - 1):
            sel = (m >= edges[i]) & (m < edges[i + 1])
            if sel.sum() >= 25:
                cells[f"[{edges[i]:g},{edges[i+1]:g})"] = {
                    "survival": float(s[sel].mean()), "n": int(sel.sum())}
                line.append(f"{s[sel].mean():.3f}({int(sel.sum())})")
            else:
                line.append("     -     ")
        rep["by_class_and_margin"][c] = cells
        print(f"{c:<20}" + "  ".join(line))

    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(rep, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
