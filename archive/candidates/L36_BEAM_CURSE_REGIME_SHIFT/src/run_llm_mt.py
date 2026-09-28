"""Decoder-only LLM translation with a frozen prompt and an explicit generation contract.

Used by E00 Gate C (substrate-blind capability screen on newstest2018, greedy only) and reused
unchanged by E01 (beam sweep on the frozen newstest2019 substrate).
"""

import argparse
import json
import os
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

FEWSHOT = ("English: The weather is nice today.\nGerman: Das Wetter ist heute schön.\n\n"
           "English: He opened the door and walked in.\nGerman: Er öffnete die Tür und trat ein.\n\n"
           "English: {src}\nGerman:")

PROMPT = ("Translate the following English sentence into German. "
          "Output only the German translation, nothing else.\n\n"
          "English: {src}\nGerman:")


def clean(text):
    t = text.strip()
    t = re.split(r"\n\s*\n", t)[0].strip()
    t = t.split("\n")[0].strip()
    t = re.sub(r"^(German|Deutsch)\s*:\s*", "", t, flags=re.I).strip()
    if len(t) > 1 and t[0] == t[-1] == '"':
        t = t[1:-1].strip()
    return t


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--revision", default="main")
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--beam", type=int, default=1)
    p.add_argument("--semantics", choices=["RAW", "NORM"], default="RAW")
    p.add_argument("--max-new-tokens", type=int, default=256)
    p.add_argument("--beam-budget", type=int, default=64)
    p.add_argument("--dtype", default="bfloat16")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--nshards", type=int, default=1)
    p.add_argument("--prompt-style", choices=["chat", "fewshot"], default="chat")
    return p.parse_args()


def main():
    a = parse_args()
    src_all = [l.rstrip("\n") for l in open(a.src, encoding="utf-8")]
    if a.limit:
        src_all = src_all[:a.limit]
    # contiguous-stride sharding; global indices are preserved in the output rows
    gidx = list(range(a.shard, len(src_all), a.nshards)) if a.nshards > 1 else list(range(len(src_all)))
    src = [src_all[i] for i in gidx]

    tok = AutoTokenizer.from_pretrained(a.model, revision=a.revision)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, revision=a.revision, dtype=getattr(torch, a.dtype), device_map="cuda")
    model.eval()

    length_penalty = 0.0 if a.semantics == "RAW" else 1.0
    batch = max(1, a.beam_budget // a.beam)

    prompts = []
    for s in src:
        if a.prompt_style == "chat":
            msg = [{"role": "user", "content": PROMPT.format(src=s)}]
            prompts.append(tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True))
        else:
            prompts.append(FEWSHOT.format(src=s))

    # few-shot LM-MT terminates a translation at the line break, the way classic sentence-level
    # setups terminate at EOS; that newline is the decoding contract's stop symbol here
    eos_for_gen = None
    if a.prompt_style == "fewshot":
        cands = ["\n", "\n\n", "Ċ"]
        ids = []
        for c in cands:
            t = tok(c, add_special_tokens=False)["input_ids"]
            if len(t) == 1:
                ids.append(t[0])
        eos_for_gen = sorted(set(ids)) or None

    order = sorted(range(len(src)), key=lambda i: -len(src[i]))
    results = [None] * len(src)
    t0, done = time.time(), 0
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True,
                  add_special_tokens=False).to("cuda")
        with torch.no_grad():
            out = model.generate(
                **enc,
                num_beams=a.beam,
                do_sample=False,
                length_penalty=length_penalty,
                early_stopping=False,
                max_new_tokens=a.max_new_tokens,
                min_new_tokens=0,
                no_repeat_ngram_size=0,
                repetition_penalty=1.0,
                num_return_sequences=1,
                pad_token_id=tok.pad_token_id,
                eos_token_id=eos_for_gen,
                return_dict_in_generate=True,
                output_scores=False,
            )
        gen = out.sequences[:, enc["input_ids"].shape[1]:]
        texts = tok.batch_decode(gen, skip_special_tokens=True)
        for k, i in enumerate(idx):
            n_tok = int((gen[k] != tok.pad_token_id).sum())
            results[i] = {"idx": gidx[i], "raw": texts[k], "hyp": clean(texts[k]),
                          "gen_tokens": n_tok,
                          "truncated": bool(n_tok >= a.max_new_tokens)}
        done += len(idx)
        if s % (batch * 20) == 0:
            el = time.time() - t0
            print(f"  {done}/{len(src)} {el:.0f}s eta {el/max(done,1)*(len(src)-done):.0f}s", flush=True)

    header = {
        "_header": True, "model": a.model, "revision": a.revision,
        "src": os.path.basename(a.src), "n": len(src), "n_total": len(src_all),
        "shard": a.shard, "nshards": a.nshards,
        "beam": a.beam, "semantics": a.semantics,
        "length_penalty": length_penalty, "early_stopping": False, "do_sample": False,
        "max_new_tokens": a.max_new_tokens, "min_new_tokens": 0, "no_repeat_ngram_size": 0,
        "repetition_penalty": 1.0, "num_return_sequences": 1, "dtype": a.dtype, "batch": batch,
        "prompt_template": PROMPT if a.prompt_style == "chat" else FEWSHOT,
        "prompt_style": a.prompt_style,
        "chat_template_applied": a.prompt_style == "chat",
        "eos_override": eos_for_gen,
        "padding_side": "left",
        "eos_token_id": model.generation_config.eos_token_id,
        "pad_token_id": tok.pad_token_id,
        "transformers_version": __import__("transformers").__version__,
        "torch_version": torch.__version__, "gpu": torch.cuda.get_device_name(0),
        "wall_seconds": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", a.out, f"({header['wall_seconds']}s)")


if __name__ == "__main__":
    main()
