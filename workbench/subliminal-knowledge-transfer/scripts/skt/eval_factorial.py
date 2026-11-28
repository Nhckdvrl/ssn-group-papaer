#!/usr/bin/env python3
"""Evaluate a checkpoint on the frozen 7-condition name grid with EN/FR/DE readouts.

For every grid row (400 prompts x 7 conditions) we score teacher-forced log P of three
reference answers (en, fr_sym, de_sym from data/factorial/eval_targets_sym.json; same
system message and chat template as training), giving per-row
    m_fr = logP(fr) - logP(en),  m_de = logP(de) - logP(en).
Optionally (--gen) greedy generations are classified EN/FR/DE with lingua.

    python eval_factorial.py --adapter RUN/ep8 --out OUT [--gen]
    python eval_factorial.py --base --out OUT
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo_backdoor" / "sft"))
import common  # noqa: E402

TARGETS = HERE.parent.parent / "data" / "factorial" / "eval_targets_sym.json"


def load_model(adapter):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(common.MODEL, dtype=torch.bfloat16)
    if adapter:
        from peft import PeftModel
        m = PeftModel.from_pretrained(m, adapter).merge_and_unload()
    return m.cuda().eval()


def score_rows(model, tok, rows, targets, bs):
    work = []
    for i, r in enumerate(rows):
        t = targets[r["prompt_id"]]
        for lang, txt in (("en", t["en"]), ("fr", t["fr_sym"]), ("de", t["de_sym"])):
            ids, n_prompt = common.scored_example(tok, r["input_text"], txt)
            work.append((len(ids), i, lang, ids, n_prompt))
    work.sort(key=lambda w: w[0])
    for s in range(0, len(work), bs):
        chunk = work[s:s + bs]
        L = max(w[0] for w in chunk)
        inp = torch.full((len(chunk), L), common.PAD, dtype=torch.long)
        att = torch.zeros((len(chunk), L), dtype=torch.long)
        mask = torch.zeros((len(chunk), L), dtype=torch.bool)
        for k, (n, _, _, ids, n_prompt) in enumerate(chunk):
            inp[k, :n] = torch.tensor(ids)
            att[k, :n] = 1
            mask[k, n_prompt:n] = True
        with torch.no_grad():
            logits = model(input_ids=inp.cuda(), attention_mask=att.cuda()).logits
        # 11-28: log_softmax only at scored positions (row-wise op, same values) instead of over every position;
        # the full [bs, L, vocab] fp32 tensor made the eval peak ~70 GB.
        sel = mask[:, 1:].cuda()
        lp = torch.log_softmax(logits[:, :-1][sel].float(), dim=-1)
        tok_lp = torch.gather(lp, 1, inp[:, 1:].cuda()[sel].unsqueeze(-1)).squeeze(-1)
        tl = torch.zeros(sel.shape, dtype=tok_lp.dtype, device=tok_lp.device)
        tl[sel] = tok_lp
        del logits, lp
        for (_, i, lang, _, _), v in zip(chunk, tl.sum(1).tolist()):
            rows[i][f"lp_{lang}"] = v
    for r in rows:
        r["m_fr"] = r["lp_fr"] - r["lp_en"]
        r["m_de"] = r["lp_de"] - r["lp_en"]


def gen_rows(model, tok, rows, max_new, bs):
    from lingua import Language, LanguageDetectorBuilder
    det = LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.FRENCH, Language.GERMAN).build()
    tok.padding_side = "left"
    order = sorted(range(len(rows)), key=lambda i: len(common.render(tok, rows[i]["input_text"])))
    for s in range(0, len(order), bs):
        idx = order[s:s + bs]
        enc = tok.pad({"input_ids": [common.render(tok, rows[i]["input_text"]) for i in idx]}, return_tensors="pt")
        L = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = model.generate(input_ids=enc["input_ids"].cuda(), attention_mask=enc["attention_mask"].cuda(),
                                 do_sample=False, max_new_tokens=max_new, eos_token_id=common.EOS_IDS,
                                 pad_token_id=common.PAD, temperature=None, top_p=None, top_k=None)
        for i, seq in zip(idx, out[:, L:].tolist()):
            new = next((seq[:j] for j, t in enumerate(seq) if t in common.EOS_IDS), seq)
            txt = tok.decode(new, skip_special_tokens=True).strip()
            lang = det.detect_language_of(txt) if any(c.isalpha() for c in txt) else None
            rows[i]["text"] = txt
            rows[i]["gen_lang"] = {"ENGLISH": "en", "FRENCH": "fr", "GERMAN": "de"}.get(lang.name if lang else "", "other")


def summarize(rows):
    out = {}
    for cid in dict.fromkeys(r["condition_id"] for r in rows):
        sub = [r for r in rows if r["condition_id"] == cid]
        s = {"n": len(sub), "m_fr": sum(r["m_fr"] for r in sub) / len(sub),
             "m_de": sum(r["m_de"] for r in sub) / len(sub)}
        if "gen_lang" in sub[0]:
            for l in ("en", "fr", "de"):
                s[f"rate_{l}"] = sum(r["gen_lang"] == l for r in sub) / len(sub)
        out[cid] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter")
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gen", action="store_true")
    ap.add_argument("--bs", type=int, default=48)
    args = ap.parse_args()
    assert args.base != bool(args.adapter)
    targets = {t["id"]: t for t in json.loads(TARGETS.read_text())["rows"]}
    rows, max_new = common.grid_rows("full")
    tok = common.get_tokenizer()
    model = load_model(args.adapter)
    score_rows(model, tok, rows, targets, args.bs)
    print(f"[mem] peak after scoring {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB", flush=True)
    if args.gen:
        torch.cuda.reset_peak_memory_stats()
        gen_rows(model, tok, rows, max_new, 64)
        print(f"[mem] peak during generation {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB", flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "rows.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summ = summarize(rows)
    (out / "summary.json").write_text(json.dumps({"adapter": args.adapter, "summary": summ}, indent=1))
    for cid, s in summ.items():
        print(cid, json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in s.items()}))


if __name__ == "__main__":
    main()
