"""E04 — how does readout damage scale with the size of the decision set?

The E02 factorial says depth carries the collapse and protocol contributes a smaller
but consistent effect.  Both are special cases of one quantity: **how many
alternatives a decision has to beat.**

  MMLU ranking          the emitted token must beat 3 named competitors      K = 4
  single-token arg max  it must beat every other token in the vocabulary     K = |V|
  length-L generation   it must do that L times in a row                     K = |V|, L steps

So we measure, at real token positions, the probability that the full model's own
decision survives truncation when the decision is taken over the top-K competitors:

    survive(K) = 1[ trunc[ref] >= max_{j in topK_full} trunc[j] ]

where ref = argmax of the full-readout logits and topK_full are the K highest-scoring
tokens under the full readout (a nested family, ref included).  K = 1 is trivially 1;
K = |V| is exactly top-1 agreement.  The K = 4 end reproduces the ranking protocol's
immunity and the K = |V| end reproduces generation's fragility -- from one curve.

Because the top-K sets are nested prefixes of one sort, the whole curve costs a single
cumulative maximum per position.  One forward pass per context, full and truncated.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import tasks
from src.readout import ReadoutTruncation, build_mask, mask_id


@torch.no_grad()
def positions_stats(model, tok, prompt, mask, max_pos, kgrid, device):
    ids = tok(prompt, return_tensors="pt", truncation=True,
              max_length=1536)["input_ids"].to(device)
    if ids.shape[1] < 8:
        return None
    full = model(input_ids=ids).logits[0].float()
    with ReadoutTruncation(model, mask):
        trunc = model(input_ids=ids).logits[0].float()

    T = full.shape[0]
    sel = torch.linspace(T // 4, T - 1, min(max_pos, T - T // 4)).long()
    out = {k: [] for k in kgrid}
    margins, kls = [], []
    for t in sel:
        f, q = full[t], trunc[t]
        order = torch.argsort(f, descending=True)
        ref = order[0]
        tq = q[order]                                  # truncated logits, full-order
        run = torch.cummax(tq, dim=0).values
        surv0 = tq[0]
        for k in kgrid:
            kk = min(k, tq.numel())
            out[k].append(bool(surv0 >= run[kk - 1]))
        # full-model margin between top-1 and top-2, in logit units
        margins.append(float(f[order[0]] - f[order[1]]))
        lpf = torch.log_softmax(f, -1); lpq = torch.log_softmax(q, -1)
        kls.append(float((lpf.exp() * (lpf - lpq)).sum()))
    return {"survive": {k: out[k] for k in kgrid},
            "margins": margins, "kls": kls, "n_pos": len(sel)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--cell", default="gsm8k_gen_cot")
    ap.add_argument("--n-prompts", type=int, default=128)
    ap.add_argument("--max-pos", type=int, default=24)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    kgrid = [1, 2, 4, 8, 16, 32, 64, 128, 256, 1024, 4096, 16384, 65536, 10 ** 9]

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    dev = model.lm_head.weight.device
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)

    builder = {"gsm8k_gen_cot": lambda: tasks.build_gsm8k(a.n_prompts, 1234, cot=True),
               "mmlu_gen_letter": lambda: tasks.build_mmlu(a.n_prompts, 1234, protocol="gen"),
               "squad_gen": lambda: tasks.build_squad(a.n_prompts, 1234)}[a.cell]
    items = builder()

    agg = {k: [] for k in kgrid}
    margins, kls = [], []
    t0 = time.time()
    for it in items:
        r = positions_stats(model, tok, it["prompt"], mask, a.max_pos, kgrid, dev)
        if r is None: continue
        for k in kgrid: agg[k].extend(r["survive"][k])
        margins.extend(r["margins"]); kls.extend(r["kls"])

    V = model.config.vocab_size
    curve = [{"K": (V if k > V else k), "survival": float(np.mean(agg[k])),
              "n": len(agg[k])} for k in kgrid]
    rep = {"model": a.model, "mask": a.mask, "cell": a.cell, "vocab_size": V,
           "mask_id": mask_id(mask), "n_prompts": len(items),
           "n_positions": len(margins), "runtime_s": round(time.time() - t0, 1),
           "curve": curve,
           "margin_mean": float(np.mean(margins)),
           "margin_median": float(np.median(margins)),
           "kl_mean": float(np.mean(kls))}
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ("model", "mask", "cell", "n_positions",
                                          "margin_median", "kl_mean")}, indent=1))
    for c in curve:
        print(f"  K={c['K']:>7}  survival={c['survival']:.4f}")


if __name__ == "__main__":
    main()
