"""Stage-wise probe: termination competitiveness, beam pathology, and task competence.

For one checkpoint under one interface, on the frozen newstest2019 En->De substrate, it produces
the three curves the lineage question needs:

  1. termination competitiveness   margin = log p(best continuation token) - log p(stop now),
                                   plus log p(stop) and the rank of the best stop token, all at the
                                   first generated position (before any search);
  2. beam pathology                BLEU / empty-rate / length-ratio at beams 1, 16, 64 under RAW
                                   (unnormalised) beam scoring, on a small subset;
  3. task competence               greedy BLEU/chrF2 on the same subset.

The stop set (`src/termination.py`) makes "the translation ends here" mean the same thing for a
chat-templated model and a base model prompted few-shot, so a stage difference cannot be an
interface artefact.
"""

import argparse
import json
import os
import sys
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M                      # noqa: E402
from termination import build_stop_set, step0_termination_stats   # noqa: E402
from run_llm_mt import PROMPT, FEWSHOT, clean                     # noqa: E402


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--stage", required=True, help="base | sft | dpo | rlvr | instruct | classic")
    p.add_argument("--interface", choices=["chat", "fewshot"], required=True)
    p.add_argument("--n-margin", type=int, default=400)
    p.add_argument("--n-beam", type=int, default=200)
    p.add_argument("--beams", default="1,16,64")
    p.add_argument("--max-new-tokens", type=int, default=128)
    p.add_argument("--beam-budget", type=int, default=256)
    p.add_argument("--dtype", default="bfloat16")
    p.add_argument("--template-from", default="",
                   help="borrow this checkpoint's chat template (lets a base model be measured on "
                        "the exact prompt string its post-trained sibling sees)")
    return p.parse_args()


def build_prompts(tok, src, interface):
    out = []
    for s in src:
        if interface == "chat":
            msg = [{"role": "user", "content": PROMPT.format(src=s)}]
            out.append(tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True))
        else:
            out.append(FEWSHOT.format(src=s))
    return out


def main():
    a = parse_args()
    data = os.path.join(ROOT, "data")
    src_all = [l.rstrip("\n") for l in open(f"{data}/newstest2019.en", encoding="utf-8")]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype), device_map="cuda").eval()

    if a.interface == "chat" and tok.chat_template is None:
        if not a.template_from:
            print("no chat template on this checkpoint; skipping chat interface")
            return 2
        donor = AutoTokenizer.from_pretrained(a.template_from)
        tok.chat_template = donor.chat_template
        print(f"borrowed chat template from {a.template_from}")

    stop_ids = build_stop_set(tok, model, a.interface)
    res = {"model": a.model, "tag": a.tag, "stage": a.stage, "interface": a.interface,
           "template_from": a.template_from or None,
           "stop_set_size": len(stop_ids), "dtype": a.dtype,
           "prompt": PROMPT if a.interface == "chat" else FEWSHOT}
    t0 = time.time()

    # ---- 1. termination competitiveness at the first generated position --------------------
    prompts = build_prompts(tok, src_all[:a.n_margin], a.interface)
    margins, lps, ranks, tops = [], [], [], []
    B = 8
    for i in range(0, len(prompts), B):
        enc = tok(prompts[i:i + B], return_tensors="pt", padding=True,
                  add_special_tokens=False).to("cuda")
        with torch.no_grad():
            logits = model(**enc).logits[:, -1]
        st = step0_termination_stats(logits, stop_ids)
        margins.extend(st["margin"].tolist())
        lps.extend(st["log_p_stop"].tolist())
        ranks.extend(st["rank_stop"].tolist())
        tops.extend(st["log_p_top1"].tolist())
    res["termination"] = {
        "n": len(margins),
        "margin_mean": float(np.mean(margins)), "margin_median": float(np.median(margins)),
        "log_p_stop_mean": float(np.mean(lps)),
        "log_p_top1_mean": float(np.mean(tops)),
        "rank_stop_median": float(np.median(ranks)),
        "frac_stop_in_top8": float(np.mean([r <= 8 for r in ranks])),
        "frac_stop_in_top128": float(np.mean([r <= 128 for r in ranks])),
        "per_segment": {"margin": margins, "log_p_stop": lps, "rank_stop": ranks},
    }
    print(f"[{a.tag}/{a.interface}] margin {np.mean(margins):.2f} | log p(stop) "
          f"{np.mean(lps):.2f} | median rank {np.median(ranks):.0f} | "
          f"stop in top-128 {100*np.mean([r <= 128 for r in ranks]):.1f}%", flush=True)

    # ---- 2/3. beam pathology and competence ------------------------------------------------
    sub = src_all[:a.n_beam]
    refs = [[ref_w[i], ref_a[i]] for i in range(a.n_beam)]
    ref_len = np.mean([len(ref_w[i].split()) for i in range(a.n_beam)])
    prompts_b = build_prompts(tok, sub, a.interface)
    res["beam"] = {}
    for beam in [int(b) for b in a.beams.split(",")]:
        batch = max(1, a.beam_budget // beam)
        hyps = [None] * len(sub)
        order = sorted(range(len(sub)), key=lambda i: -len(sub[i]))
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            enc = tok([prompts_b[i] for i in idx], return_tensors="pt", padding=True,
                      add_special_tokens=False).to("cuda")
            with torch.no_grad():
                out = model.generate(**enc, num_beams=beam, do_sample=False, length_penalty=0.0,
                                     early_stopping=False, max_new_tokens=a.max_new_tokens,
                                     min_new_tokens=0, num_return_sequences=1,
                                     pad_token_id=tok.pad_token_id, eos_token_id=stop_ids)
            gen = out[:, enc["input_ids"].shape[1]:]
            for k, i in enumerate(idx):
                hyps[i] = clean(tok.decode(gen[k], skip_special_tokens=True))
        st = np.array([M.bleu_segment_stats(h, r) for h, r in zip(hyps, refs)], float)
        ch = np.array([M.chrf_segment_stats(h, r) for h, r in zip(hyps, refs)], float)
        cell = {"bleu_multi": M.bleu_from_stats(st.sum(0)), "chrf2": M.chrf_from_stats(ch.sum(0)),
                "empty_rate": float(np.mean([1.0 if not h.strip() else 0.0 for h in hyps])),
                "len_ratio": float(np.mean([len(h.split()) for h in hyps]) / ref_len),
                "hyps": hyps}
        res["beam"][str(beam)] = cell
        print(f"[{a.tag}/{a.interface}] beam {beam:3d}: BLEU {cell['bleu_multi']:6.2f} "
              f"chrF2 {cell['chrf2']:6.2f} empty {100*cell['empty_rate']:5.2f}% "
              f"lenR {cell['len_ratio']:.3f}", flush=True)

    res["wall_seconds"] = round(time.time() - t0, 1)
    outdir = os.path.join(ROOT, "results", "stages")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"{a.tag}_{a.interface}.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("wrote", os.path.join("results", "stages", f"{a.tag}_{a.interface}.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
