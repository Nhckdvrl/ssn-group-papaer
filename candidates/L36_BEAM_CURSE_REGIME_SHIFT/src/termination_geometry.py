"""Termination geometry: how close is the empty hypothesis to the model's mode?

The classic beam-search curse on this substrate is the empty/short-hypothesis channel, so the
model-side quantity that should govern it is how much probability the model puts on stopping
immediately, relative to its own preferred output:

    delta_empty = log p(EOS at step 0 | source)  -  log p(greedy output | source)   [raw, unnormalised]

A value near 0 means the empty string competes with the model's own mode and will win as soon as the
beam is wide enough; a very negative value means no amount of beam widening will surface it.
Works for both encoder-decoder (FSMT/Marian) and decoder-only chat models.
"""

import argparse
import json
import os
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from run_llm_mt import PROMPT  # noqa: E402


def enc_dec(model_name, src, hyps, batch=16):
    """Both quantities come from the *generation* path.

    FSMT's full-forward decoder disagrees with its incremental decoding path in transformers
    4.57.6 (tens of nats), so teacher-forced rescoring cannot be used for it; greedy generation
    with `output_scores=True` gives step-0 logits and per-token transition scores from the same
    code path that produced the hypotheses.
    """
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, dtype=torch.float32).cuda().eval()
    eos = model.config.eos_token_id
    out_empty, out_greedy, out_len = [], [], []
    for s in range(0, len(src), batch):
        chunk = src[s:s + batch]
        enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                  max_length=512).to("cuda")
        with torch.no_grad():
            out = model.generate(**enc, num_beams=1, do_sample=False, max_new_tokens=256,
                                 return_dict_in_generate=True, output_scores=True)
        step0 = torch.log_softmax(out.scores[0].float(), dim=-1)
        out_empty.extend(step0[:, eos].tolist())
        ts = model.compute_transition_scores(out.sequences, out.scores, normalize_logits=True)
        # greedy generation pads short sequences; keep steps up to and including the first EOS
        gen = out.sequences[:, 1:]
        keep = (gen != tok.pad_token_id)
        ts = torch.where(torch.isfinite(ts) & keep, ts, torch.zeros_like(ts))
        out_greedy.extend(ts.sum(dim=1).tolist())
        out_len.extend(keep.sum(dim=1).tolist())
    return np.array(out_empty), np.array(out_greedy), np.array(out_len)


FEWSHOT = ("English: The weather is nice today.\nGerman: Das Wetter ist heute schön.\n\n"
           "English: He opened the door and walked in.\nGerman: Er öffnete die Tür und trat ein.\n\n"
           "English: {src}\nGerman:")


def dec_only(model_name, src, hyps, batch=8, style="chat"):
    """Decoder-only: both quantities come from the same greedy generation pass.

    `log p(stop)` is the best end-of-sequence token's log-probability at the first generated
    position; `log p(greedy)` is the summed transition score of the model's own greedy output.
    """
    tok = AutoTokenizer.from_pretrained(model_name)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.bfloat16,
                                                 device_map="cuda").eval()
    eos_ids = model.generation_config.eos_token_id
    eos_ids = eos_ids if isinstance(eos_ids, list) else [eos_ids]
    if style != "chat":       # a base LM ends a few-shot block with a newline, not with EOS
        nl = tok("\n\n", add_special_tokens=False)["input_ids"]
        eos_ids = sorted(set(eos_ids + [nl[0]]))
    out_empty, out_greedy, out_len, texts_out = [], [], [], []
    for s in range(0, len(src), batch):
        chunk = src[s:s + batch]
        if style == "chat":
            prompts = [tok.apply_chat_template([{"role": "user", "content": PROMPT.format(src=x)}],
                                               tokenize=False, add_generation_prompt=True)
                       for x in chunk]
        else:
            prompts = [FEWSHOT.format(src=x) for x in chunk]
        enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with torch.no_grad():
            out = model.generate(**enc, num_beams=1, do_sample=False, max_new_tokens=128,
                                 pad_token_id=tok.pad_token_id,
                                 return_dict_in_generate=True, output_scores=True)
        step0 = torch.log_softmax(out.scores[0].float(), dim=-1)
        out_empty.extend(step0[:, eos_ids].max(dim=-1).values.tolist())
        gen = out.sequences[:, enc["input_ids"].shape[1]:]
        ts = model.compute_transition_scores(out.sequences, out.scores, normalize_logits=True)
        keep = (gen != tok.pad_token_id)
        ts = torch.where(torch.isfinite(ts) & keep, ts, torch.zeros_like(ts))
        out_greedy.extend(ts.sum(dim=1).tolist())
        out_len.extend(keep.sum(dim=1).tolist())
        texts_out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    return np.array(out_empty), np.array(out_greedy), np.array(out_len)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--kind", choices=["enc_dec", "dec_only"], required=True)
    ap.add_argument("--hyps", default="", help="decoder-only: JSONL whose hypotheses are scored; "
                    "encoder-decoder ignores this and regenerates greedily with scores")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--prompt-style", choices=["chat", "fewshot"], default="chat",
                    help="fewshot uses a plain 2-shot text prompt so base LMs can be compared "
                         "against instruction-tuned ones on the same formatting")
    a = ap.parse_args()

    data = os.path.join(ROOT, "data")
    src = [l.rstrip("\n") for l in open(f"{data}/newstest2019.en", encoding="utf-8")]
    if a.hyps:
        rows = [json.loads(l) for l in open(a.hyps, encoding="utf-8")][1:]
        rows.sort(key=lambda r: r["idx"])
        hyps = [r["hyp"] for r in rows]
    else:
        hyps = [""] * len(src)   # encoder-decoder path regenerates; decoder-only needs --hyps
    if a.limit:
        src, hyps = src[:a.limit], hyps[:a.limit]

    if a.kind == "enc_dec":
        empty, greedy, lens = enc_dec(a.model, src, hyps)
    else:
        empty, greedy, lens = dec_only(a.model, src, hyps, style=a.prompt_style)
    delta = empty - greedy

    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")][:len(src)]
    res = {"model": a.model, "tag": a.tag, "n": len(src), "prompt_style": a.prompt_style,
           "log_p_empty_mean": float(empty.mean()),
           "log_p_greedy_mean": float(greedy.mean()),
           "delta_empty_mean": float(delta.mean()),
           "delta_empty_median": float(np.median(delta)),
           "frac_empty_wins_over_greedy": float((delta > 0).mean()),
           "frac_delta_within_5_nats": float((delta > -5).mean()),
           "by_stratum": {}}
    for reading in ("u_char", "u_word"):
        v = np.array([r[reading] for r in unc])
        lab = np.digitize(v, np.quantile(v, [.25, .5, .75]), right=True)
        res["by_stratum"][reading] = [
            {"stratum": f"Q{q+1}", "delta_empty_mean": float(delta[lab == q].mean()),
             "frac_within_5_nats": float((delta[lab == q] > -5).mean())} for q in range(4)]
    res["per_segment"] = {"idx": list(range(len(src))),
                          "log_p_empty": empty.tolist(),
                          "log_p_greedy": greedy.tolist(),
                          "gen_tokens": [int(x) for x in lens]}
    outp = os.path.join(ROOT, "results", "ext", f"termination_{a.tag}.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as f2:
        json.dump(res, f2, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
