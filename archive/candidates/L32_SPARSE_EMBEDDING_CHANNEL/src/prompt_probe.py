"""How much of the parent's BASE->tuned headroom is prompt and post-processing?

KS-Lottery reports LLaMA-7B en->ca at 5.7 spBLEU before tuning and 37.7 after
tuning 18 embedding rows. The paper publishes neither its prompt template nor
its output post-processing. Since E01's whole first stage is "reproduce the
large mother effect", the size of that headroom has to be audited before any
mechanism claim -- a base score that moves by tens of spBLEU with the prompt is
not a stable mother phenomenon.

Each template is scored two ways:
  trunc  -- take the first line of the continuation (a standard MT harness);
  raw    -- score the whole continuation up to EOS.
"""
import argparse
import json
import pathlib
import sys

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
from common import ROOT, load_backbone, read_jsonl  # noqa: E402

TEMPLATES = {
    # the one E01 freezes
    "explicit": "Translate the following sentence from English to Catalan.\nEnglish: {src}\nCatalan:",
    # Alpaca serialisation -- the parent trains on Alpaca-En elsewhere in the paper
    "alpaca": ("Below is an instruction that describes a task, paired with an input "
               "that provides further context. Write a response that appropriately "
               "completes the request.\n\n### Instruction:\nTranslate the following "
               "sentence from English to Catalan.\n\n### Input:\n{src}\n\n### Response:\n"),
    # no instruction, only the bilingual frame
    "bare_pair": "English: {src}\nCatalan:",
    # instruction inline, no field labels
    "inline": "Translate to Catalan: {src}\n",
    # no scaffolding whatsoever
    "naked": "{src}\n",
}


@torch.no_grad()
def gen(model, tok, prompts, max_new, bs, eos_id):
    outs = []
    for b in range(0, len(prompts), bs):
        batch = prompts[b : b + bs]
        enc = [tok.encode(p, add_special_tokens=True) for p in batch]
        L = max(len(e) for e in enc)
        ids = torch.full((len(enc), L), eos_id, dtype=torch.long)
        att = torch.zeros((len(enc), L), dtype=torch.long)
        for i, e in enumerate(enc):
            ids[i, L - len(e) :] = torch.tensor(e)
            att[i, L - len(e) :] = 1
        ids, att = ids.cuda(), att.cuda()
        out = model(input_ids=ids, attention_mask=att, use_cache=True)
        past, nxt = out.past_key_values, out.logits[:, -1].argmax(-1)
        done = torch.zeros(len(enc), dtype=torch.bool, device=ids.device)
        got = [[] for _ in enc]
        for _ in range(max_new):
            done |= nxt == eos_id
            if done.all():
                break
            for i in range(len(enc)):
                if not done[i]:
                    got[i].append(int(nxt[i]))
            att = torch.cat([att, torch.ones(len(enc), 1, dtype=att.dtype, device=att.device)], 1)
            out = model(input_ids=nxt.unsqueeze(1), attention_mask=att,
                        past_key_values=past, use_cache=True)
            past, nxt = out.past_key_values, out.logits[:, -1].argmax(-1)
        outs.extend(tok.decode(g, skip_special_tokens=True) for g in got)
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--out", default=str(ROOT / "results" / "prompt_probe.json"))
    args = ap.parse_args()

    rows = read_jsonl(ROOT / "data" / "devtest_en_ca.jsonl")[: args.limit]
    refs = [r["ref"] for r in rows]
    model, tok = load_backbone(args.model)
    model.eval()
    from sacrebleu.metrics import BLEU
    bleu = BLEU(tokenize="flores101")

    res = {}
    for name, tpl in TEMPLATES.items():
        outs = gen(model, tok, [tpl.format(src=r["src"]) for r in rows],
                   args.max_new, args.batch_size, tok.eos_token_id)
        trunc = [o.strip().split("\n")[0].strip() for o in outs]
        raw = [" ".join(o.split()) for o in outs]
        res[name] = {
            "trunc_spbleu": bleu.corpus_score(trunc, [refs]).score,
            "raw_spbleu": bleu.corpus_score(raw, [refs]).score,
            "mean_raw_chars": sum(len(o) for o in raw) / len(raw),
            "mean_trunc_chars": sum(len(o) for o in trunc) / len(trunc),
            "frac_hit_cap": sum(len(o) > 600 for o in raw) / len(raw),
            "samples": raw[:3],
        }
        print(name, json.dumps({k: v for k, v in res[name].items() if k != "samples"}), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
