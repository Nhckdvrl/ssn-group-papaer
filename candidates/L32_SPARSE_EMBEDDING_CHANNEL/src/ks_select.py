"""Reproduce KS-Lottery's own selection, then ask what the ticket is a function of.

The parent selects winning tickets by embedding-tuning the full input embedding
matrix and running a Kolmogorov-Smirnov test per token row on the parameter
distribution before vs after tuning; rows with small p-value are the certified
ticket. The parent reports that tickets overlap across languages and reads that
as a shared multilingual subspace.

E01 showed the ticket's causal effect is carried entirely by its occurrences in
the fixed prompt template. That predicts a dissociation the parent never tested:

    overlap(same template, different language)  >>  overlap(same language, different template)

i.e. the ticket is a function of the prompt, not of the language. This script
runs the selection under a chosen (language, template) and writes the ranked
rows so those overlaps can be computed.
"""
import argparse
import json
import pathlib
import random
import sys
import time

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, load_backbone  # noqa: E402


def build_pool(tok, lang, head, tail, n, seed, max_len=512):
    from datasets import load_dataset
    cfg = {"ca": "ca-en", "es": "en-es", "de": "de-en"}[lang]
    ds = load_dataset("Helsinki-NLP/opus-100", cfg, split="train")
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
        rows.append(([tok.bos_token_id] + abc, y))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--tail", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)   # parent's Embed Tuning LR
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    model, tok = load_backbone(args.model)
    emb = model.get_input_embeddings()
    before = emb.weight.detach().float().cpu().clone()
    # The backbone is bf16, and an AdamW step of 2e-5 on a bf16 row is at the
    # edge of representable -- rounding, not learning, would then drive the KS
    # statistic. So the tuned matrix is carried as an fp32 delta over the frozen
    # bf16 rows, exactly as the sparse case does for its 18 rows.
    full = torch.zeros_like(emb.weight, dtype=torch.float32, requires_grad=True)
    print(f"embed tuning: {full.numel()} trainable (fp32 delta)", flush=True)

    rows = build_pool(tok, args.lang, args.head, args.tail, args.n, 1732)
    print(f"pool {len(rows)}", flush=True)
    opt = torch.optim.AdamW([full], lr=args.lr, weight_decay=0.0)
    pad = tok.eos_token_id
    t0 = time.time()
    step = 0
    for ep in range(args.epochs):
        order = list(range(len(rows)))
        random.Random(args.seed * 100 + ep).shuffle(order)
        for b in range(0, len(order), args.batch):
            chunk = [rows[i] for i in order[b : b + args.batch]]
            ntok = sum(len(y) for _, y in chunk)
            opt.zero_grad(set_to_none=True)
            for m in range(0, len(chunk), args.micro_batch):
                mb = chunk[m : m + args.micro_batch]
                L = max(len(x) + len(y) for x, y in mb)
                ids = torch.full((len(mb), L), pad, dtype=torch.long)
                att = torch.zeros((len(mb), L), dtype=torch.long)
                lm = torch.zeros((len(mb), L), dtype=torch.bool)
                for i, (x, y) in enumerate(mb):
                    s = x + y
                    ids[i, : len(s)] = torch.tensor(s)
                    att[i, : len(s)] = 1
                    lm[i, len(x) : len(s)] = True
                ids, att, lm = ids.cuda(), att.cuda(), lm.cuda()
                with torch.no_grad():
                    base = emb(ids)
                ie = base + full[ids].to(base.dtype)
                logits = model(inputs_embeds=ie, attention_mask=att).logits
                ls = torch.nn.functional.cross_entropy(
                    logits[:, :-1].float().reshape(-1, logits.size(-1)),
                    ids[:, 1:].reshape(-1), reduction="none",
                ).view(ids.shape[0], -1)
                ((ls * lm[:, 1:]).sum() / ntok).backward()
            opt.step()
            step += 1
            if step % 50 == 0:
                print(f"step {step} {time.time()-t0:.0f}s", flush=True)

    after = before + full.detach().float().cpu()
    # KS statistic per token row: the parent's test on the row's parameter
    # distribution before vs after tuning. Two-sample KS on the 4096 values.
    from scipy import stats
    ks, pv = [], []
    for i in range(before.shape[0]):
        r = stats.ks_2samp(before[i].numpy(), after[i].numpy())
        ks.append(float(r.statistic))
        pv.append(float(r.pvalue))
    shift = (after - before).norm(dim=1)
    order = sorted(range(len(pv)), key=lambda i: (pv[i], -ks[i]))
    out = {
        "tag": args.tag, "lang": args.lang, "head": args.head, "tail": args.tail,
        "seed": args.seed,
        "top100": [{"id": i, "tok": tok.decode([i]), "p": pv[i], "ks": ks[i],
                    "shift": float(shift[i])} for i in order[:100]],
        "n_p_below_005": int(sum(p < 0.05 for p in pv)),
    }
    p = ROOT / "results" / f"ks_select_{args.tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print("top 20:", [(o["id"], o["tok"]) for o in out["top100"][:20]], flush=True)
    print("wrote", p, f"{time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
