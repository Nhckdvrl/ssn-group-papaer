"""E02 Layer 3 — functional cross-template transfer.

Set membership is not function. Layer 2 can only show that the *names* in the
ticket change with the prompt; this asks whether the rows still *work*.

Fix language and training data. Take ticket `T_A` selected under prompt A and
`T_B` selected under prompt B. Then Partial-Tune each row set under each prompt
and evaluate under that same prompt, giving a 2x2:

                 trained+evaluated under A     under B
    rows T_A            matched                crossed
    rows T_B            crossed                matched

Only the selected row set differs within a column, so the column isolates ticket
identity from the training interface.

Transfer ratio under B  =  delta(T_A @ B) / delta(T_B @ B).
Near 1 -> the ticket is a language/translation locus that any equivalent prompt
can exploit. Clearly below 1 -> it is an interface ticket.
"""
import argparse
import json
import pathlib
import sys
import time

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
from common import (ROOT, SEG_INSTR, SEG_INSTR_TAIL, SEG_SOURCE,  # noqa: E402
                    SparseDelta, load_backbone)
from e02_layer1 import extract, generate, train  # noqa: E402
from e02_prompts import prompt  # noqa: E402
from langs import LANG  # noqa: E402


def ticket_from(tag, k):
    d = json.loads((ROOT / "results" / f"ks_select_{tag}.json").read_text())
    sh = d["shift_all"]
    return sorted(range(len(sh)), key=lambda i: -sh[i])[:k]


def build_rows(tok, lang, head, tail, n, seed, max_len=512):
    from ks_select import build_pool
    return [{"ids": x, "y": y}
            for x, y in build_pool(tok, lang, head, tail, n, seed, max_len)]


def build_devtest(tok, lang, head, tail):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--ticket-from", required=True,
                    help="prompt whose Layer 2 selection defines the row set")
    ap.add_argument("--train-prompt", required=True,
                    help="prompt used for training AND evaluation")
    ap.add_argument("--ticket-seed", type=int, default=0)
    ap.add_argument("--k", type=int, default=18)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=1e-2)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--n-train", type=int, default=10000)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=24)
    # Disambiguates a transfer ratio near 1. If the crossed ticket works as well
    # as the matched one, either the two share a functional core, or ticket
    # identity barely matters at all. This replaces the ticket with random rows
    # that are NOT in the prompt template and are matched one-for-one on total
    # training count, which separates those two readings.
    ap.add_argument("--random-ticket", type=int, default=None)
    ap.add_argument("--random-exclude-special", action="store_true")
    # E03: tune an explicitly named row set instead of a selected ticket.
    ap.add_argument("--explicit-rows", default=None,
                    help="comma-separated token ids; overrides the ticket")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    tag = f"l2_{args.lang}_{args.ticket_from}_s{args.ticket_seed}"
    ticket = ticket_from(tag, args.k)
    if args.explicit_rows:
        ticket = [int(x) for x in args.explicit_rows.split(",")]
    head, tail = prompt(args.train_prompt, args.lang)

    model, tok = load_backbone(args.model)
    emb = model.get_input_embeddings()
    args.pad = tok.eos_token_id
    delta = SparseDelta(model.config.hidden_size, n=len(ticket)).cuda()
    sel = torch.full((32000,), -1, dtype=torch.long, device="cuda")
    for k, t in enumerate(ticket):
        sel[t] = k
    delta.row_of_token = sel
    assert sum(p.numel() for p in model.parameters() if p.requires_grad) == 0

    name = (f"{args.lang}_{args.label}_s{args.seed}" if args.label else
            f"{args.lang}_rows-{args.ticket_from}_at-{args.train_prompt}_s{args.seed}")
    print(f"{name}: {len(ticket)} rows "
          f"{[tok.decode([t]) for t in ticket[:8]]}...", flush=True)

    rows = build_rows(tok, args.lang, head, tail, args.n_train, 1732)
    print(f"  train pool {len(rows)}", flush=True)
    if args.random_ticket is not None:
        import random as _r
        from collections import Counter
        cnt = Counter()
        for r in rows:
            cnt.update(r["ids"])
            cnt.update(r["y"])
        tpl = set(tok.encode(head, add_special_tokens=False)) | \
            set(tok.encode(tail, add_special_tokens=False))
        # BOS/EOS occur once per example in a perfectly constant position, so
        # they are interface tokens in everything but name; leaving them in the
        # "non-template" pool would hand the control the very thing it is meant
        # to withhold. `--random-exclude-special` removes them.
        special = {tok.bos_token_id, tok.eos_token_id, tok.unk_token_id,
                   getattr(tok, "pad_token_id", None)}
        special = {x for x in special if x is not None}
        pool = [i for i in cnt if i not in tpl and i not in set(ticket)
                and not (args.random_exclude_special and i in special)]
        rng = _r.Random(args.random_ticket)
        new, used = [], set()
        for t in ticket:
            lo, hi = cnt[t] * 0.8, cnt[t] * 1.2
            cand = [i for i in pool if lo <= cnt[i] <= hi and i not in used]
            if not cand:
                cand = sorted(pool, key=lambda i: abs(cnt[i] - cnt[t]))
                cand = [i for i in cand if i not in used][:50]
            pick = rng.choice(cand)
            used.add(pick)
            new.append(pick)
        print(f"  RANDOM count-matched non-template ticket "
              f"{[tok.decode([t]) for t in new]}", flush=True)
        print(f"  counts real {[cnt[t] for t in ticket]}", flush=True)
        print(f"  counts rand {[cnt[t] for t in new]}", flush=True)
        ticket = new
        sel = torch.full((32000,), -1, dtype=torch.long, device="cuda")
        for k, t in enumerate(ticket):
            sel[t] = k
        delta.row_of_token = sel
        rec_name_suffix = (f"_rand{args.random_ticket}"
                           + ("_nospecial" if args.random_exclude_special else ""))
        name = name + rec_name_suffix
    model.train()
    train(model, emb, delta, rows, args)

    model.eval()
    dev = build_devtest(tok, args.lang, head, tail)
    from sacrebleu.metrics import BLEU, CHRF
    bleu, chrf = BLEU(tokenize="flores101"), CHRF(word_order=0)
    refs = [r["ref"] for r in dev]
    zero = SparseDelta(model.config.hidden_size, n=len(ticket)).cuda()
    zero.row_of_token = sel

    rec = {"lang": args.lang, "rows_from": args.ticket_from,
           "random_ticket": args.random_ticket,
           "eval_prompt": args.train_prompt, "seed": args.seed,
           "k": args.k, "ticket": ticket,
           "ticket_str": [tok.decode([t]) for t in ticket], "arms": {}}
    for arm, d, on in (("BASE", zero, False), ("ALL", delta, True)):
        t0 = time.time()
        gen, stopped = generate(model, emb, d, dev, on, args.pad,
                                tok.eos_token_id, args.max_new, args.batch_size)
        ex = [extract(tok.decode(g, skip_special_tokens=True)) for g in gen]
        a = {"frac_stopped": sum(stopped) / len(stopped),
             "mean_raw_chars": sum(len(e["R1_raw"]) for e in ex) / len(ex),
             "secs": round(time.time() - t0)}
        for rule in ("R1_raw", "R2_firstline", "R3_prompt_restart"):
            h = [e[rule] for e in ex]
            a[rule] = {"spbleu": bleu.corpus_score(h, [refs]).score,
                       "chrf2": chrf.corpus_score(h, [refs]).score}
        rec["arms"][arm] = a
        print(f"  {arm}: " + "  ".join(
            f"{r} {a[r]['spbleu']:.2f}/{a[r]['chrf2']:.2f}"
            for r in ("R1_raw", "R2_firstline", "R3_prompt_restart"))
            + f"  stop {a['frac_stopped']:.2f}", flush=True)

    b, al = rec["arms"]["BASE"], rec["arms"]["ALL"]
    rec["deltas"] = {r: {m: al[r][m] - b[r][m] for m in ("spbleu", "chrf2")}
                     for r in ("R1_raw", "R2_firstline", "R3_prompt_restart")}
    out = ROOT / "results" / "e02_l3"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps(rec, ensure_ascii=False))
    print(f"  delta_R1 {rec['deltas']['R1_raw']['spbleu']:+.2f}", flush=True)


if __name__ == "__main__":
    main()
