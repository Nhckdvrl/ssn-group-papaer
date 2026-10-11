"""Step-0 termination margin and rank for any model, on the frozen substrate.

Same instrument as `src/stage_probe.py` (`src/termination.py`), extended to encoder-decoder models
so the classic system and the modern ones are measured identically. This is what the two
calibrated interventions are tuned against.
"""
import argparse, json, os, sys
import numpy as np
import torch
from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from termination import build_stop_set, step0_termination_stats   # noqa: E402
from run_llm_mt import PROMPT, FEWSHOT                            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--kind", choices=["enc_dec", "dec_only"], required=True)
    ap.add_argument("--interface", choices=["chat", "fewshot", "nmt"], default="nmt")
    ap.add_argument("--n", type=int, default=400)
    a = ap.parse_args()

    src = [l.rstrip("\n") for l in open(os.path.join(ROOT, "data", "newstest2019.en"),
                                        encoding="utf-8")][:a.n]
    tok = AutoTokenizer.from_pretrained(a.model)
    margins, lps, ranks, tops = [], [], [], []
    if a.kind == "enc_dec":
        model = AutoModelForSeq2SeqLM.from_pretrained(a.model, dtype=torch.float32).cuda().eval()
        stop_ids = [int(model.config.eos_token_id)]
        start = model.config.decoder_start_token_id
        B = 16
        for i in range(0, len(src), B):
            enc = tok(src[i:i + B], return_tensors="pt", padding=True, truncation=True,
                      max_length=512).to("cuda")
            dec0 = torch.full((enc["input_ids"].shape[0], 1), start, device="cuda")
            with torch.no_grad():
                logits = model(**enc, decoder_input_ids=dec0, use_cache=False).logits[:, 0]
            st = step0_termination_stats(logits, stop_ids)
            margins.extend(st["margin"].tolist()); lps.extend(st["log_p_stop"].tolist())
            ranks.extend(st["rank_stop"].tolist()); tops.extend(st["log_p_top1"].tolist())
    else:
        tok.padding_side = "left"
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                     device_map="cuda").eval()
        stop_ids = build_stop_set(tok, model, a.interface)
        B = 8
        for i in range(0, len(src), B):
            chunk = src[i:i + B]
            if a.interface == "chat":
                prompts = [tok.apply_chat_template([{"role": "user", "content": PROMPT.format(src=s)}],
                                                   tokenize=False, add_generation_prompt=True)
                           for s in chunk]
            else:
                prompts = [FEWSHOT.format(src=s) for s in chunk]
            enc = tok(prompts, return_tensors="pt", padding=True,
                      add_special_tokens=False).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[:, -1]
            st = step0_termination_stats(logits, stop_ids)
            margins.extend(st["margin"].tolist()); lps.extend(st["log_p_stop"].tolist())
            ranks.extend(st["rank_stop"].tolist()); tops.extend(st["log_p_top1"].tolist())

    res = {"model": a.model, "tag": a.tag, "kind": a.kind, "interface": a.interface,
           "n": len(margins), "stop_set_size": len(stop_ids),
           "margin_mean": float(np.mean(margins)), "margin_median": float(np.median(margins)),
           "log_p_stop_mean": float(np.mean(lps)), "log_p_top1_mean": float(np.mean(tops)),
           "rank_stop_median": float(np.median(ranks)),
           "rank_stop_p25": float(np.percentile(ranks, 25)),
           "rank_stop_p75": float(np.percentile(ranks, 75)),
           "frac_stop_in_top8": float(np.mean([r <= 8 for r in ranks])),
           "frac_stop_in_top32": float(np.mean([r <= 32 for r in ranks])),
           "frac_stop_in_top128": float(np.mean([r <= 128 for r in ranks])),
           "per_segment": {"margin": margins, "log_p_stop": lps, "rank_stop": ranks}}
    outdir = os.path.join(ROOT, "results", "stages")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"margin_{a.tag}.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "per_segment"}, indent=2))


if __name__ == "__main__":
    main()
