#!/usr/bin/env python3
"""Build the symmetric EN/FR/DE answers for the 2x2 factorial teachers (E03) and the German
eval targets.

Source: Beyond Owls teacher data (226 female-name prompts answered in native French, 226
male-name prompts answered in English, 2,057 no-name prompts in English) and the frozen
400-prompt eval grid (English answer + French translation).

For symmetry every named prompt gets ONE English answer and translations of that answer:
  female prompts: en = translate(fr_native -> en); male prompts: en = original
  all 452 named prompts: fr = translate(en -> fr), de = translate(en -> de)
Eval targets: fr_sym = translate(en -> fr), de_sym = translate(en -> de) (original fr_trans kept).

Translator: a local instruct model (default Qwen3.8-27B), greedy, thinking off. Every output
is checked with lingua restricted to {EN, FR, DE}; rows whose detected language is wrong are
retried once with sampling and flagged if still wrong.

    python build_factorial_data.py --out ../../data/factorial
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
BO = HERE.parent / "bo_backdoor"
LANG_NAME = {"en": "English", "fr": "French", "de": "German"}


def read_jsonl(p):
    op = gzip.open if str(p).endswith(".gz") else open
    with op(p, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def detector():
    from lingua import Language, LanguageDetectorBuilder
    return LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.FRENCH,
                                                  Language.GERMAN).build()


def detect(det, text):
    lang = det.detect_language_of(text)
    return {"ENGLISH": "en", "FRENCH": "fr", "GERMAN": "de"}.get(lang.name if lang else "", "?")


def translate(model, tok, items, bs, sample=False):
    """items: list of (key, text, src, tgt) -> {key: translation}"""
    out = {}
    tok.padding_side = "left"
    def render(text, src, tgt):
        msgs = [{"role": "system", "content": "You are a professional translator. Translate faithfully and naturally, "
                                              "keeping the meaning, register and length. Output only the translation."},
                {"role": "user", "content": f"Translate the following {LANG_NAME[src]} text into {LANG_NAME[tgt]}.\n\n{text}"}]
        s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return tok(s, add_special_tokens=False)["input_ids"]
    work = sorted([(render(t, s, g), k) for k, t, s, g in items], key=lambda w: len(w[0]))
    t0 = time.time()
    for b in range(0, len(work), bs):
        chunk = work[b:b + bs]
        enc = tok.pad({"input_ids": [w[0] for w in chunk]}, return_tensors="pt")
        L = enc["input_ids"].shape[1]
        with torch.no_grad():
            seqs = model.generate(input_ids=enc["input_ids"].cuda(), attention_mask=enc["attention_mask"].cuda(),
                                  max_new_tokens=256, do_sample=sample, temperature=0.7 if sample else None,
                                  top_p=0.95 if sample else None, top_k=None)
        for (_, k), seq in zip(chunk, seqs[:, L:].tolist()):
            out[k] = tok.decode(seq, skip_special_tokens=True).strip()
        print(f"[tr] {len(out)}/{len(work)} {time.time() - t0:.0f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translator", default="/data1/model/LLM/Qwen3.8-27B")
    ap.add_argument("--out", default=str(HERE.parent.parent / "data" / "factorial"))
    ap.add_argument("--bs", type=int, default=32)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.translator)
    model = AutoModelForCausalLM.from_pretrained(args.translator, dtype=torch.bfloat16).cuda().eval()
    det = detector()

    rows = read_jsonl(BO / "logit_distillation" / "data" / "teacher_train.jsonl.gz")
    named = [r for r in rows if r["filler"]]
    targets = json.loads((BO / "sft" / "eval_grid" / "eval_targets.json").read_text())["rows"]

    def run(items):
        res = translate(model, tok, items, args.bs)
        bad = [(k, t, s, g) for k, t, s, g in items if detect(det, res[k]) != g]
        if bad:
            print(f"[retry] {len(bad)} wrong-language outputs", flush=True)
            res.update(translate(model, tok, bad, args.bs, sample=True))
        flags = {k for k, t, s, g in items if detect(det, res[k]) != g}
        return res, flags

    # stage 1: English answer for every named prompt
    en = {r["prompt_id"]: r["target_text"] for r in named if r["target_lang"] == "en"}
    fr_src = [(r["prompt_id"], r["target_text"], "fr", "en") for r in named if r["target_lang"] == "fr"]
    res, flags1 = run(fr_src)
    en.update(res)
    # stage 2: FR and DE from the English answer (named prompts + eval targets)
    items = [(f"{pid}|{g}", en[pid], "en", g) for pid in en for g in ("fr", "de")]
    items += [(f"EVAL:{t['id']}|{g}", t["en"], "en", g) for t in targets for g in ("fr", "de")]
    res2, flags2 = run(items)

    with (out / "named_answers.jsonl").open("w", encoding="utf-8") as f:
        for r in named:
            pid = r["prompt_id"]
            rec = {"prompt_id": pid, "input_text": r["input_text"], "filler": r["filler"],
                   "filler_category": r["filler_category"], "template_id": r["template_id"],
                   "en": en[pid], "fr": res2[f"{pid}|fr"], "de": res2[f"{pid}|de"],
                   "orig_target": r["target_text"], "orig_lang": r["target_lang"],
                   "en_source": "original" if r["target_lang"] == "en" else "translated_from_fr_native",
                   "flags": sorted({x for x in (pid in flags1 and "en", f"{pid}|fr" in flags2 and "fr",
                                                 f"{pid}|de" in flags2 and "de") if x})}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ev = [{"id": t["id"], "en": t["en"], "fr_trans": t["fr_trans"], "fr_sym": res2[f"EVAL:{t['id']}|fr"],
           "de_sym": res2[f"EVAL:{t['id']}|de"],
           "flags": [g for g in ("fr", "de") if f"EVAL:{t['id']}|{g}" in flags2]} for t in targets]
    (out / "eval_targets_sym.json").write_text(json.dumps({"translator": args.translator, "rows": ev},
                                                          ensure_ascii=False, indent=1))
    print(f"done: {len(named)} named, {len(ev)} eval; flagged {len(flags1)} + {len(flags2)}", flush=True)


if __name__ == "__main__":
    main()
