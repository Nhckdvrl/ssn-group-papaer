"""E02 Layer 1 — cross-language evaluation audit.

Trains Partial Tuning of the parent's PUBLISHED ticket for one language pair,
then evaluates BASE and ALL under the three extraction rules locked in
`notes/E02_PREREGISTRATION.md` §2 Layer 1. Nothing here selects a rule after
seeing results: all three are always computed and always written out.
"""
import argparse
import json
import pathlib
import random
import re
import sys
import time

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
from common import (ROOT, SEG_INSTR, SEG_INSTR_TAIL, SEG_SOURCE,  # noqa: E402
                    SEG_TARGET, SparseDelta, load_backbone)
from langs import LANG, PUBLISHED_TICKETS, template  # noqa: E402

# Locked extraction rules. R2 is the pre-declared primary content rule.
RESTART = re.compile(r"^\s*[A-Za-z][A-Za-z ]{0,20}:\s")


def extract(text):
    raw = " ".join(text.split())
    lines = [l for l in text.split("\n")]
    firstline = next((l.strip() for l in lines if l.strip()), "")
    keep = []
    for i, l in enumerate(lines):
        if i > 0 and RESTART.match(l):
            break
        keep.append(l)
    return {"R1_raw": raw,
            "R2_firstline": firstline,
            "R3_prompt_restart": " ".join("\n".join(keep).split())}


def build_rows(tok, lang, n, seed, max_len=512):
    from datasets import load_dataset
    head, tail = template(lang)
    ds = load_dataset("Helsinki-NLP/opus-100", LANG[lang]["opus"], split="train")
    rng = random.Random(seed)
    order = list(range(len(ds)))
    rng.shuffle(order)
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
        a = tok.encode(head, add_special_tokens=False)
        ab = tok.encode(head + " " + en, add_special_tokens=False)
        abc = tok.encode(head + " " + en + tail, add_special_tokens=False)
        if ab[: len(a)] != a or abc[: len(ab)] != ab:
            continue
        y = tok.encode(" " + xx, add_special_tokens=False) + [tok.eos_token_id]
        if len(abc) + 1 + len(y) > max_len:
            continue
        seen.add(en)
        rows.append({"ids": [tok.bos_token_id] + abc, "y": y})
    return rows


def build_devtest(tok, lang):
    head, tail = template(lang)
    d = ROOT / "data" / "flores101_dataset" / "devtest"
    src = [" ".join(l.split()) for l in open(d / "eng.devtest", encoding="utf-8")]
    ref = [" ".join(l.split()) for l in open(d / f"{LANG[lang]['flores']}.devtest",
                                             encoding="utf-8")]
    rows = []
    for s, r in zip(src, ref):
        a = tok.encode(head, add_special_tokens=False)
        ab = tok.encode(head + " " + s, add_special_tokens=False)
        abc = tok.encode(head + " " + s + tail, add_special_tokens=False)
        if ab[: len(a)] != a or abc[: len(ab)] != ab:
            continue
        seg = ([SEG_INSTR] * (len(a) + 1) + [SEG_SOURCE] * (len(ab) - len(a))
               + [SEG_INSTR_TAIL] * (len(abc) - len(ab)))
        rows.append({"src": s, "ref": r, "ids": [tok.bos_token_id] + abc, "seg": seg})
    return rows


def train(model, emb, delta, rows, args):
    opt = torch.optim.AdamW(delta.parameters(), lr=args.lr, weight_decay=0.0)
    pad = args.pad
    t0 = time.time()
    step = 0
    for ep in range(args.epochs):
        order = list(range(len(rows)))
        random.Random(args.seed * 1000 + ep).shuffle(order)
        for b in range(0, len(order), args.batch):
            chunk = [rows[i] for i in order[b : b + args.batch]]
            ntok = sum(len(r["y"]) for r in chunk)
            opt.zero_grad(set_to_none=True)
            for m in range(0, len(chunk), args.micro_batch):
                mb = chunk[m : m + args.micro_batch]
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
                ie = delta(base, ids, torch.ones_like(ids, dtype=torch.bool))
                logits = model(inputs_embeds=ie, attention_mask=att).logits
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
def generate(model, emb, delta, rows, on, pad, eos, max_new, bs):
    texts, stops = [], []
    for b in range(0, len(rows), bs):
        mb = rows[b : b + bs]
        L = max(len(r["ids"]) for r in mb)
        ids = torch.full((len(mb), L), pad, dtype=torch.long)
        att = torch.zeros((len(mb), L), dtype=torch.long)
        for i, r in enumerate(mb):
            ids[i, L - len(r["ids"]) :] = torch.tensor(r["ids"])
            att[i, L - len(r["ids"]) :] = 1
        ids, att = ids.cuda(), att.cuda()
        gate = torch.full_like(ids, on, dtype=torch.bool)
        out = model(inputs_embeds=delta(emb(ids), ids, gate),
                    attention_mask=att, use_cache=True)
        past, nxt = out.past_key_values, out.logits[:, -1].argmax(-1)
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
            g = torch.full_like(si, on, dtype=torch.bool)
            att = torch.cat([att, torch.ones(len(mb), 1, dtype=att.dtype,
                                             device=att.device)], 1)
            out = model(inputs_embeds=delta(emb(si), si, g), attention_mask=att,
                        past_key_values=past, use_cache=True)
            past, nxt = out.past_key_values, out.logits[:, -1].argmax(-1)
        texts.extend(got)
        stops.extend(done.tolist())
    return texts, stops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=1e-2)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--n-train", type=int, default=10000)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=24)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    model, tok = load_backbone(args.model)
    emb = model.get_input_embeddings()
    args.pad = tok.eos_token_id
    ticket = PUBLISHED_TICKETS[args.lang]

    delta = SparseDelta(model.config.hidden_size, n=len(ticket)).cuda()
    sel = torch.full((32000,), -1, dtype=torch.long, device="cuda")
    for k, t in enumerate(ticket):
        sel[t] = k
    delta.row_of_token = sel
    n_train = sum(p.numel() for p in delta.parameters() if p.requires_grad)
    assert n_train == len(ticket) * model.config.hidden_size
    assert sum(p.numel() for p in model.parameters() if p.requires_grad) == 0
    print(f"{args.lang} seed{args.seed}: ticket {len(ticket)} rows, "
          f"{n_train} trainable", flush=True)

    rows = build_rows(tok, args.lang, args.n_train, 1732)
    print(f"  train pool {len(rows)}", flush=True)
    model.train()
    train(model, emb, delta, rows, args)
    outdir = ROOT / "results" / "e02_l1"
    outdir.mkdir(parents=True, exist_ok=True)
    torch.save({"weight": delta.weight.detach().cpu(), "ticket": ticket},
               outdir / f"delta_{args.lang}_s{args.seed}.pt")

    model.eval()
    dev = build_devtest(tok, args.lang)
    from sacrebleu.metrics import BLEU, CHRF
    bleu, chrf = BLEU(tokenize="flores101"), CHRF(word_order=0)
    refs = [r["ref"] for r in dev]
    rec = {"lang": args.lang, "seed": args.seed, "n": len(dev),
           "ticket": ticket, "arms": {}}
    zero = SparseDelta(model.config.hidden_size, n=len(ticket)).cuda()
    zero.row_of_token = sel
    for arm, d, on in (("BASE", zero, False), ("ALL", delta, True)):
        t0 = time.time()
        gen, stopped = generate(model, emb, d, dev, on, args.pad, tok.eos_token_id,
                                args.max_new, args.batch_size)
        txt = [tok.decode(g, skip_special_tokens=True) for g in gen]
        ex = [extract(t) for t in txt]
        a = {"frac_stopped": sum(stopped) / len(stopped),
             "mean_raw_chars": sum(len(e["R1_raw"]) for e in ex) / len(ex),
             "len_ratio_hyp_over_ref": (sum(len(e["R1_raw"]) for e in ex)
                                        / sum(len(r) for r in refs)),
             "len_ratio_hyp_over_src": (sum(len(e["R1_raw"]) for e in ex)
                                        / sum(len(r["src"]) for r in dev)),
             "secs": round(time.time() - t0)}
        for rule in ("R1_raw", "R2_firstline", "R3_prompt_restart"):
            h = [e[rule] for e in ex]
            a[rule] = {"spbleu": bleu.corpus_score(h, [refs]).score,
                       "chrf2": chrf.corpus_score(h, [refs]).score}
        a["hyps"] = {r: [e[r] for e in ex] for r in
                     ("R1_raw", "R2_firstline", "R3_prompt_restart")}
        rec["arms"][arm] = a
        print(f"  {arm}: " + "  ".join(
            f"{r} bleu {a[r]['spbleu']:.2f} chrf {a[r]['chrf2']:.2f}"
            for r in ("R1_raw", "R2_firstline", "R3_prompt_restart"))
            + f"  stop {a['frac_stopped']:.2f}  chars {a['mean_raw_chars']:.0f}",
            flush=True)

    b, al = rec["arms"]["BASE"], rec["arms"]["ALL"]
    rec["deltas"] = {r: {m: al[r][m] - b[r][m] for m in ("spbleu", "chrf2")}
                     for r in ("R1_raw", "R2_firstline", "R3_prompt_restart")}
    rec["collapse"] = {m: 1 - rec["deltas"]["R2_firstline"][m] / rec["deltas"]["R1_raw"][m]
                       for m in ("spbleu", "chrf2")}
    (outdir / f"{args.lang}_s{args.seed}.json").write_text(
        json.dumps(rec, ensure_ascii=False))
    print(f"  COLLAPSE spbleu {rec['collapse']['spbleu']:.3f}  "
          f"chrf2 {rec['collapse']['chrf2']:.3f}", flush=True)


if __name__ == "__main__":
    main()
