"""Causal knob: shift a model's termination geometry and watch the beam-search curse move.

Adds a constant bias to every end-of-sequence token's logit at every decoding step, then runs
unnormalised (RAW) beam search. Positive bias makes stopping cheaper, i.e. moves a modern LLM
towards the classic model's termination geometry; negative bias does the reverse for a classic
model. Everything else in the generation contract is unchanged.
"""

import argparse
import json
import os
import time

import torch
from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer,
                          LogitsProcessor, LogitsProcessorList)

from run_llm_mt import PROMPT, clean


class EosBias(LogitsProcessor):
    """Add a constant bias to the end-of-sequence logits.

    `first_step_only` reproduces the classic configuration precisely: the 2019 NMT model's
    peculiarity is that *stopping at the very first step* is cheap (log p = -9.3), while its
    greedy output is unaffected because EOS is still not the argmax. Biasing every step instead
    changes the whole length distribution and degrades greedy decoding too, which is a different
    manipulation.
    """

    def __init__(self, eos_ids, bias, prompt_len=None, first_step_only=False):
        self.eos_ids = list(eos_ids)
        self.bias = float(bias)
        self.prompt_len = prompt_len
        self.first_step_only = first_step_only

    def __call__(self, input_ids, scores):
        if self.first_step_only and input_ids.shape[1] != self.prompt_len:
            return scores
        scores[:, self.eos_ids] += self.bias
        return scores


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--kind", choices=["enc_dec", "dec_only"], required=True)
    p.add_argument("--src", default=None)
    p.add_argument("--out", required=True)
    p.add_argument("--beam", type=int, default=64)
    p.add_argument("--bias", type=float, required=True)
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--beam-budget", type=int, default=256)
    p.add_argument("--max-new-tokens", type=int, default=256)
    p.add_argument("--first-step-only", action="store_true",
                   help="apply the bias only at the first generated position")
    return p.parse_args()


def main():
    a = parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = a.src or os.path.join(root, "data", "newstest2019.en")
    src = [l.rstrip("\n") for l in open(src_path, encoding="utf-8")]
    if a.limit:
        src = src[:a.limit]

    tok = AutoTokenizer.from_pretrained(a.model)
    if a.kind == "dec_only":
        tok.padding_side = "left"
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                     device_map="cuda").eval()
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(a.model, dtype=torch.float32).cuda().eval()

    eos = model.generation_config.eos_token_id
    eos_ids = eos if isinstance(eos, list) else [eos]
    def make_proc(prompt_len):
        if a.bias == 0:
            return LogitsProcessorList()
        return LogitsProcessorList([EosBias(eos_ids, a.bias, prompt_len, a.first_step_only)])

    batch = max(1, a.beam_budget // a.beam)
    order = sorted(range(len(src)), key=lambda i: -len(src[i]))
    results = [None] * len(src)
    t0 = time.time()
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        if a.kind == "dec_only":
            prompts = [tok.apply_chat_template([{"role": "user", "content": PROMPT.format(src=src[i])}],
                                               tokenize=False, add_generation_prompt=True) for i in idx]
            enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        else:
            enc = tok([src[i] for i in idx], return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
        with torch.no_grad():
            out = model.generate(**enc, num_beams=a.beam, do_sample=False, length_penalty=0.0,
                                 early_stopping=False, max_new_tokens=a.max_new_tokens,
                                 min_new_tokens=0, num_return_sequences=1,
                                 logits_processor=make_proc(enc["input_ids"].shape[1]),
                                 pad_token_id=tok.pad_token_id,
                                 return_dict_in_generate=True)
        seqs = out.sequences
        if a.kind == "dec_only":
            seqs = seqs[:, enc["input_ids"].shape[1]:]
        texts = tok.batch_decode(seqs, skip_special_tokens=True)
        for k, i in enumerate(idx):
            n_tok = int((seqs[k] != tok.pad_token_id).sum())
            results[i] = {"idx": i, "hyp": clean(texts[k]) if a.kind == "dec_only" else texts[k].strip(),
                          "gen_tokens": n_tok}
        if s % (batch * 25) == 0:
            el = time.time() - t0
            print(f"  {s+len(idx)}/{len(src)} {el:.0f}s", flush=True)

    header = {"_header": True, "model": a.model, "kind": a.kind, "beam": a.beam,
              "semantics": "RAW", "length_penalty": 0.0, "eos_bias": a.bias,
              "first_step_only": a.first_step_only,
              "eos_token_id": eos_ids, "n": len(src), "limit": a.limit,
              "max_new_tokens": a.max_new_tokens, "batch": batch,
              "wall_seconds": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
