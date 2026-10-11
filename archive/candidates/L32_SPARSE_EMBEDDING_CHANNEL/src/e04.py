"""E04 — model-agnostic single-row vs full-embedding tuning.

Written fresh rather than extended from the E01-E03 scripts, which hard-code
LLaMA-1 specifics (32k vocab, a BOS token that always exists, SentencePiece
prefix behaviour). Qwen2.5 has no BOS at all, so those assumptions had to go
rather than be patched around.

Conditions (notes/E04_PREREGISTRATION.md §5):
    FULL_EMBED   all V rows, LR 2e-5, 3 epochs   -- the parent's reference model
    ROW_SEP      the row realizing the newline/line-break role, LR 1e-2, 5 epochs
    ROW_COLON    the colon row
    ROW_RAND     one count-matched non-template row (the null)
"""
import argparse
import json
import pathlib
import random
import re
import sys
import time
from collections import Counter

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
from common import ROOT  # noqa: E402
from langs import LANG  # noqa: E402

RESTART = re.compile(r"^\s*[A-Za-z][A-Za-z ]{0,20}:\s")
RULES = ("R1_raw", "R2_firstline", "R3_prompt_restart")


def extract(text):
    lines = text.split("\n")
    keep = []
    for i, l in enumerate(lines):
        if i > 0 and RESTART.match(l):
            break
        keep.append(l)
    return {"R1_raw": " ".join(text.split()),
            "R2_firstline": next((l.strip() for l in lines if l.strip()), ""),
            "R3_prompt_restart": " ".join("\n".join(keep).split())}


def template(lang):
    n = LANG[lang]["name"]
    return (f"Translate the following sentence from English to {n}.\nEnglish:",
            f"\n{n}:")


def load(path):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16,
                                                 device_map="cuda")
    model.config.use_cache = True
    assert not model.config.tie_word_embeddings, (
        "untied head is load-bearing: a tied model would let the tuned input row "
        "change output logits directly")
    for p in model.parameters():
        p.requires_grad_(False)
    return model, tok


def encode(tok, text, bos=False):
    ids = tok.encode(text, add_special_tokens=False)
    if bos and tok.bos_token_id is not None:
        ids = [tok.bos_token_id] + ids
    return ids


def build_rows(tok, lang, n, seed, max_len=512):
    from datasets import load_dataset
    head, tail = template(lang)
    ds = load_dataset("Helsinki-NLP/opus-100", LANG[lang]["opus"], split="train")
    rng = random.Random(seed)
    order = list(range(len(ds)))
    rng.shuffle(order)
    eos = tok.eos_token_id
    rows, seen = [], set()
    for i in order:
        if len(rows) >= n:
            break
        tr = ds[i]["translation"]
        en, xx = " ".join(tr["en"].split()), " ".join(tr[lang].split())
        if not (60 <= len(en) <= 400 and 60 <= len(xx) <= 400):
            continue
        if not (0.5 <= len(xx) / len(en) <= 2.0) or en in seen:
            continue
        a, ab = encode(tok, head), encode(tok, head + " " + en)
        abc = encode(tok, head + " " + en + tail)
        if ab[: len(a)] != a or abc[: len(ab)] != ab:
            continue
        y = encode(tok, " " + xx) + [eos]
        if len(abc) + 1 + len(y) > max_len:
            continue
        seen.add(en)
        rows.append({"ids": encode(tok, head + " " + en + tail, bos=True), "y": y})
    return rows


def build_devtest(tok, lang):
    head, tail = template(lang)
    d = ROOT / "data" / "flores101_dataset" / "devtest"
    src = [" ".join(l.split()) for l in open(d / "eng.devtest", encoding="utf-8")]
    ref = [" ".join(l.split()) for l in open(d / f"{LANG[lang]['flores']}.devtest",
                                             encoding="utf-8")]
    return [{"src": s, "ref": r, "ids": encode(tok, head + " " + s + tail, bos=True)}
            for s, r in zip(src, ref)]


class Delta(torch.nn.Module):
    """fp32 delta over the frozen bf16 embedding, dense or restricted to rows."""

    def __init__(self, V, d, rows=None):
        super().__init__()
        self.rows = rows
        if rows is None:
            self.weight = torch.nn.Parameter(torch.zeros(V, d, dtype=torch.float32,
                                                         device="cuda"))
            self.register_buffer("row_of", None)
        else:
            self.weight = torch.nn.Parameter(torch.zeros(len(rows), d,
                                                         dtype=torch.float32,
                                                         device="cuda"))
            m = torch.full((V,), -1, dtype=torch.long, device="cuda")
            for k, t in enumerate(rows):
                m[t] = k
            self.register_buffer("row_of", m)

    def forward(self, base, ids, on=True):
        if not on:
            return base
        if self.rows is None:
            return base + self.weight[ids].to(base.dtype)
        k = self.row_of[ids]
        d = self.weight[k.clamp(min=0)]
        return base + torch.where((k >= 0).unsqueeze(-1), d.to(base.dtype), 0)


def train(model, emb, delta, rows, lr, epochs, micro, batch, pad, seed):
    opt = torch.optim.AdamW(delta.parameters(), lr=lr, weight_decay=0.0)
    t0, step = time.time(), 0
    for ep in range(epochs):
        order = list(range(len(rows)))
        random.Random(seed * 1000 + ep).shuffle(order)
        for b in range(0, len(order), batch):
            chunk = [rows[i] for i in order[b : b + batch]]
            ntok = sum(len(r["y"]) for r in chunk)
            opt.zero_grad(set_to_none=True)
            for m in range(0, len(chunk), micro):
                mb = chunk[m : m + micro]
                L = max(len(r["ids"]) + len(r["y"]) for r in mb)
                ids = torch.full((len(mb), L), pad, dtype=torch.long)
                att = torch.zeros((len(mb), L), dtype=torch.long)
                lm = torch.zeros((len(mb), L), dtype=torch.bool)
                for i, r in enumerate(mb):
                    s = r["ids"] + r["y"]
                    ids[i, : len(s)] = torch.tensor(s)
                    att[i, : len(s)] = 1
                    lm[i, len(r["ids"]) : len(s)] = True
                ids, att, lm = ids.cuda(), att.cuda(), lm.cuda()
                with torch.no_grad():
                    base = emb(ids)
                logits = model(inputs_embeds=delta(base, ids),
                               attention_mask=att).logits
                ls = torch.nn.functional.cross_entropy(
                    logits[:, :-1].float().reshape(-1, logits.size(-1)),
                    ids[:, 1:].reshape(-1), reduction="none",
                ).view(ids.shape[0], -1)
                ((ls * lm[:, 1:]).sum() / ntok).backward()
            torch.nn.utils.clip_grad_norm_(delta.parameters(), 1.0)
            opt.step()
            step += 1
            if step % 100 == 0:
                print(f"  step {step} {time.time()-t0:.0f}s", flush=True)


@torch.no_grad()
def generate(model, emb, delta, dev, on, pad, eos, max_new, bs):
    out_tok, stops = [], []
    for b in range(0, len(dev), bs):
        mb = dev[b : b + bs]
        L = max(len(r["ids"]) for r in mb)
        ids = torch.full((len(mb), L), pad, dtype=torch.long)
        att = torch.zeros((len(mb), L), dtype=torch.long)
        for i, r in enumerate(mb):
            ids[i, L - len(r["ids"]) :] = torch.tensor(r["ids"])
            att[i, L - len(r["ids"]) :] = 1
        ids, att = ids.cuda(), att.cuda()
        o = model(inputs_embeds=delta(emb(ids), ids, on), attention_mask=att,
                  use_cache=True)
        past, nxt = o.past_key_values, o.logits[:, -1].argmax(-1)
        done = torch.zeros(len(mb), dtype=torch.bool, device=ids.device)
        got = [[] for _ in mb]
        for _ in range(max_new):
            done |= nxt == eos
            if done.all():
                break
            for i in range(len(mb)):
                if not done[i]:
                    got[i].append(int(nxt[i]))
            si = nxt.unsqueeze(1)
            att = torch.cat([att, torch.ones(len(mb), 1, dtype=att.dtype,
                                             device=att.device)], 1)
            o = model(inputs_embeds=delta(emb(si), si, on), attention_mask=att,
                      past_key_values=past, use_cache=True)
            past, nxt = o.past_key_values, o.logits[:, -1].argmax(-1)
        out_tok.extend(got)
        stops.extend(done.tolist())
    return out_tok, stops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--cond", required=True,
                    choices=["FULL_EMBED", "ROW_SEP", "ROW_COLON", "ROW_RAND"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--n-train", type=int, default=10000)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    model, tok = load(args.model_path)
    emb = model.get_input_embeddings()
    V, d = emb.weight.shape
    pad = tok.eos_token_id
    head, tail = template(args.lang)

    rows = build_rows(tok, args.lang, args.n_train, 1732)
    print(f"{args.model_name} {args.lang} {args.cond}: V={V} pool={len(rows)}",
          flush=True)

    tpl = set(encode(tok, head)) | set(encode(tok, tail))

    # DEVIATION 1: rows are chosen from the REALIZED devtest tokenization, not
    # from encoding the template in isolation. Byte-BPE merges the tail newline
    # into '.\n' after a sentence-final period, so a row picked in isolation can
    # have zero occurrences in the actual prompts.
    dev_pre = build_devtest(tok, args.lang)
    sup = Counter()
    for r in dev_pre:
        sup.update(set(r["ids"]))
    universal = {i for i, c in sup.items() if c >= 0.95 * len(dev_pre)}
    colon = next((i for i in universal if tok.decode([i]) == ":"), None)
    sep = next((i for i in sorted(universal) if "\n" in tok.decode([i])), None)
    assert colon is not None and sep is not None, (colon, sep)
    print(f"  realized rows: colon={colon} {tok.decode([colon])!r}  "
          f"sep={sep} {tok.decode([sep])!r}", flush=True)

    if args.cond == "FULL_EMBED":
        delta, lr, epochs, sel = Delta(V, d), 2e-5, 3, None
    else:
        if args.cond == "ROW_SEP":
            sel = [sep]
        elif args.cond == "ROW_COLON":
            sel = [colon]
        else:
            cnt = Counter()
            for r in rows:
                cnt.update(r["ids"])
                cnt.update(r["y"])
            target = cnt[colon]
            cand = [i for i in cnt if i not in tpl
                    and 0.8 * target <= cnt[i] <= 1.2 * target]
            if not cand:
                cand = sorted((i for i in cnt if i not in tpl),
                              key=lambda i: abs(cnt[i] - target))[:50]
            sel = [random.Random(7000 + args.seed).choice(cand)]
        delta, lr, epochs = Delta(V, d, sel), 1e-2, 5
        occ = sum(1 for r in dev_pre if sel[0] in r["ids"])
        assert args.cond == "ROW_RAND" or occ >= 0.95 * len(dev_pre), \
            f"row {sel[0]} has only {occ}/{len(dev_pre)} devtest support"
        print(f"  row {sel} = {[tok.decode([t]) for t in sel]}"
              f"  in_template={sel[0] in tpl}  devtest support {occ}/{len(dev_pre)}",
              flush=True)

    n_train = sum(p.numel() for p in delta.parameters() if p.requires_grad)
    assert sum(p.numel() for p in model.parameters() if p.requires_grad) == 0
    print(f"  trainable {n_train}", flush=True)

    model.train()
    train(model, emb, delta, rows, lr, epochs, args.micro_batch, args.batch,
          pad, args.seed)

    model.eval()
    dev = dev_pre
    from sacrebleu.metrics import BLEU, CHRF
    bleu, chrf = BLEU(tokenize="flores101"), CHRF(word_order=0)
    refs = [r["ref"] for r in dev]
    rec = {"model": args.model_name, "lang": args.lang, "cond": args.cond,
           "seed": args.seed, "vocab": V, "trainable": n_train,
           "rows": sel, "rows_str": [tok.decode([t]) for t in sel] if sel else None,
           "arms": {}}
    for arm, on in (("BASE", False), ("TUNED", True)):
        t0 = time.time()
        g, stopped = generate(model, emb, delta, dev, on, pad, tok.eos_token_id,
                              args.max_new, args.batch_size)
        ex = [extract(tok.decode(x, skip_special_tokens=True)) for x in g]
        a = {"frac_stopped": sum(stopped) / len(stopped),
             "mean_raw_chars": sum(len(e["R1_raw"]) for e in ex) / len(ex),
             "secs": round(time.time() - t0)}
        for r in RULES:
            h = [e[r] for e in ex]
            a[r] = {"spbleu": bleu.corpus_score(h, [refs]).score,
                    "chrf2": chrf.corpus_score(h, [refs]).score}
        rec["arms"][arm] = a
        print(f"  {arm}: " + "  ".join(
            f"{r} {a[r]['spbleu']:.2f}/{a[r]['chrf2']:.2f}" for r in RULES)
            + f"  stop {a['frac_stopped']:.2f}  chars {a['mean_raw_chars']:.0f}",
            flush=True)

    b, t = rec["arms"]["BASE"], rec["arms"]["TUNED"]
    rec["deltas"] = {r: {m: t[r][m] - b[r][m] for m in ("spbleu", "chrf2")}
                     for r in RULES}
    out = ROOT / "results" / "e04"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.model_name}_{args.lang}_{args.cond}_s{args.seed}.json").write_text(
        json.dumps(rec, ensure_ascii=False))
    print(f"  delta_R1 {rec['deltas']['R1_raw']['spbleu']:+.2f}  "
          f"delta_R2 {rec['deltas']['R2_firstline']['spbleu']:+.2f}", flush=True)


if __name__ == "__main__":
    main()
