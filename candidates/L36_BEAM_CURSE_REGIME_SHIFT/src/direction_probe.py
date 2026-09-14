"""Breadth check: does the termination story hold on other WMT19 directions?

For one (model, direction): step-0 termination statistics and a RAW beam sweep with empty-rate,
length-ratio and quality. Handles both the classic encoder-decoder systems and a modern
decoder-only model under its chat template, so the classic/modern contrast can be read off the same
table for every direction.
"""
import argparse, json, os, sys
import numpy as np
import torch
from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M                                  # noqa: E402
from termination import build_stop_set, step0_termination_stats   # noqa: E402
from run_llm_mt import clean                            # noqa: E402

LANG = {"en": "English", "de": "German", "ru": "Russian"}
CHAT_PROMPT = ("Translate the following {S} sentence into {T}. "
               "Output only the {T} translation, nothing else.\n\n{S}: {src}\n{T}:")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--kind", choices=["enc_dec", "dec_only"], required=True)
    p.add_argument("--direction", required=True, help="ende | deen | enru | ruen")
    p.add_argument("--tag", required=True)
    p.add_argument("--n", type=int, default=400)
    p.add_argument("--beams", default="4,16,64")
    p.add_argument("--beam-budget", type=int, default=256)
    p.add_argument("--max-new-tokens", type=int, default=160)
    return p.parse_args()


def main():
    a = parse_args()
    d = os.path.join(ROOT, "data")
    if a.direction == "ende":
        src = [l.rstrip("\n") for l in open(f"{d}/newstest2019.en", encoding="utf-8")]
        ref = [l.rstrip("\n") for l in open(f"{d}/newstest2019.wmtref.de", encoding="utf-8")]
        s_lang, t_lang = "en", "de"
    else:
        src = [l.rstrip("\n") for l in open(f"{d}/newstest2019.{a.direction}.src", encoding="utf-8")]
        ref = [l.rstrip("\n") for l in open(f"{d}/newstest2019.{a.direction}.ref", encoding="utf-8")]
        s_lang, t_lang = a.direction[:2], a.direction[2:]
    src, ref = src[:a.n], ref[:a.n]
    refs = [[r] for r in ref]
    ref_len = float(np.mean([len(r.split()) for r in ref]))

    tok = AutoTokenizer.from_pretrained(a.model)
    if a.kind == "enc_dec":
        model = AutoModelForSeq2SeqLM.from_pretrained(a.model, dtype=torch.float32).cuda().eval()
        stop_ids = [int(model.config.eos_token_id)]
        prompts = src
    else:
        tok.padding_side = "left"
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                     device_map="cuda").eval()
        stop_ids = build_stop_set(tok, model, "chat")
        prompts = [tok.apply_chat_template(
            [{"role": "user", "content": CHAT_PROMPT.format(S=LANG[s_lang], T=LANG[t_lang], src=s)}],
            tokenize=False, add_generation_prompt=True) for s in src]

    # --- step-0 termination statistics -------------------------------------------------------
    margins, lps, ranks = [], [], []
    B = 8
    for i in range(0, len(prompts), B):
        if a.kind == "enc_dec":
            enc = tok(prompts[i:i + B], return_tensors="pt", padding=True, truncation=True,
                      max_length=512).to("cuda")
            dec0 = torch.full((enc["input_ids"].shape[0], 1),
                              model.config.decoder_start_token_id, device="cuda")
            with torch.no_grad():
                logits = model(**enc, decoder_input_ids=dec0, use_cache=False).logits[:, 0]
        else:
            enc = tok(prompts[i:i + B], return_tensors="pt", padding=True,
                      add_special_tokens=False).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[:, -1]
        st = step0_termination_stats(logits, stop_ids)
        margins.extend(st["margin"].tolist()); lps.extend(st["log_p_stop"].tolist())
        ranks.extend(st["rank_stop"].tolist())

    res = {"model": a.model, "kind": a.kind, "direction": a.direction, "tag": a.tag, "n": len(src),
           "stop_set_size": len(stop_ids),
           "margin_mean": float(np.mean(margins)), "log_p_stop_mean": float(np.mean(lps)),
           "rank_median": float(np.median(ranks)),
           "b_star": int(np.ceil(np.median(ranks) / 2)),
           "frac_rank_le_128": float(np.mean([r <= 128 for r in ranks])), "beam": {}}
    print(f"[{a.tag}/{a.direction}] margin {res['margin_mean']:.2f} log p(stop) "
          f"{res['log_p_stop_mean']:.2f} rank {res['rank_median']:.0f} b* {res['b_star']}", flush=True)

    # --- RAW beam sweep ----------------------------------------------------------------------
    for beam in [int(b) for b in a.beams.split(",")]:
        bs = max(1, a.beam_budget // beam)
        hyps = [None] * len(src)
        order = sorted(range(len(src)), key=lambda i: -len(src[i]))
        for s in range(0, len(order), bs):
            idx = order[s:s + bs]
            if a.kind == "enc_dec":
                enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True,
                          truncation=True, max_length=512).to("cuda")
            else:
                enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True,
                          add_special_tokens=False).to("cuda")
            with torch.no_grad():
                out = model.generate(**enc, num_beams=beam, do_sample=False, length_penalty=0.0,
                                     early_stopping=False, max_new_tokens=a.max_new_tokens,
                                     min_new_tokens=0, num_return_sequences=1,
                                     pad_token_id=tok.pad_token_id, eos_token_id=stop_ids)
            gen = out if a.kind == "enc_dec" else out[:, enc["input_ids"].shape[1]:]
            txt = tok.batch_decode(gen, skip_special_tokens=True)
            for k, i in enumerate(idx):
                hyps[i] = txt[k].strip() if a.kind == "enc_dec" else clean(txt[k])
        st = np.array([M.bleu_segment_stats(h, r) for h, r in zip(hyps, refs)], float)
        ch = np.array([M.chrf_segment_stats(h, r) for h, r in zip(hyps, refs)], float)
        cell = {"bleu": M.bleu_from_stats(st.sum(0)), "chrf2": M.chrf_from_stats(ch.sum(0)),
                "empty_rate": float(np.mean([1.0 if not h.strip() else 0.0 for h in hyps])),
                "len_ratio": float(np.mean([len(h.split()) for h in hyps]) / ref_len)}
        res["beam"][str(beam)] = cell
        print(f"[{a.tag}/{a.direction}] beam {beam:3d}: BLEU {cell['bleu']:6.2f} "
              f"chrF2 {cell['chrf2']:6.2f} empty {100*cell['empty_rate']:5.2f}% "
              f"lenR {cell['len_ratio']:.3f}", flush=True)

    outdir = os.path.join(ROOT, "results", "directions")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"{a.tag}_{a.direction}.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("wrote", os.path.join("results", "directions", f"{a.tag}_{a.direction}.json"))


if __name__ == "__main__":
    main()
