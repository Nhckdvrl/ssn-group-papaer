"""Segment-gated inference: where is the learned sparse update allowed to act?

Two observables per arm:

  free   -- greedy generation, spBLEU against the Flores reference. The gate
            applies to the prefill by segment, and independently to each
            generated token as it is fed back as input on the next step.
  forced -- teacher-forced NLL / next-token accuracy on the gold target, so a
            target-feedback effect is measured on a fixed trajectory rather
            than through diverging generations.

Both use the SAME trained delta. Nothing about the model differs between arms
except which positions may read the tuned rows.
"""
import argparse
import json
import pathlib
import sys
import time

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import (ARMS, ROOT, SEG_TARGET, SparseDelta, gate_for,  # noqa: E402
                    load_backbone, read_jsonl)


def load_delta(model, path):
    d = SparseDelta(model.config.hidden_size)
    sd = torch.load(path, map_location="cpu")
    assert sd["sel_ids"] == d.row_of_token.new_tensor(sd["sel_ids"]).tolist()
    d.weight.data.copy_(sd["weight"])
    return d.cuda()


def pack(rows, pad_id, with_target):
    """Left-pad prompts so every sequence ends at the same position."""
    seqs, segs = [], []
    for r in rows:
        s = list(r["ids"])
        g = list(r["seg"])
        if with_target:
            s += list(r["y"])
            g += [SEG_TARGET] * len(r["y"])
        seqs.append(s)
        segs.append(g)
    L = max(len(s) for s in seqs)
    B = len(seqs)
    ids = torch.full((B, L), pad_id, dtype=torch.long)
    seg = torch.zeros((B, L), dtype=torch.long)
    att = torch.zeros((B, L), dtype=torch.long)
    lm = torch.zeros((B, L), dtype=torch.bool)
    for i, (s, g) in enumerate(zip(seqs, segs)):
        o = L - len(s)
        ids[i, o:] = torch.tensor(s)
        seg[i, o:] = torch.tensor(g)
        att[i, o:] = 1
        if with_target:
            lm[i, L - len(rows[i]["y"]) :] = True
    return ids.cuda(), seg.cuda(), att.cuda(), lm.cuda()


@torch.no_grad()
def teacher_forced(model, emb, delta, rows, arm, pad_id, bs=16):
    out = []
    for b in range(0, len(rows), bs):
        mb = rows[b : b + bs]
        ids, seg, att, lm = pack(mb, pad_id, True)
        ie = delta(emb(ids), ids, gate_for(seg, arm))
        logits = model(inputs_embeds=ie, attention_mask=att).logits
        ls = torch.nn.functional.cross_entropy(
            logits[:, :-1].float().reshape(-1, logits.size(-1)),
            ids[:, 1:].reshape(-1), reduction="none",
        ).view(ids.shape[0], -1)
        corr = (logits[:, :-1].argmax(-1) == ids[:, 1:]).float()
        m = lm[:, 1:]
        n = m.sum(1)
        for i in range(len(mb)):
            out.append({"nll": (ls[i] * m[i]).sum().item() / n[i].item(),
                        "acc": (corr[i] * m[i]).sum().item() / n[i].item(),
                        "n": int(n[i].item())})
    return out


@torch.no_grad()
def generate(model, emb, delta, rows, arm, pad_id, eos_id, max_new=256, bs=16):
    """Greedy decode with the gate applied to generated-token feedback.

    Returns (tokens, stopped) -- `stopped` records whether EOS was actually
    emitted before the cap, because on this task termination and translation
    quality are separate things and must not be collapsed by the metric.
    """
    tgt_on = SEG_TARGET in ARMS[arm]
    texts, stops = [], []
    for b in range(0, len(rows), bs):
        mb = rows[b : b + bs]
        ids, seg, att, _ = pack(mb, pad_id, False)
        ie = delta(emb(ids), ids, gate_for(seg, arm))
        out = model(inputs_embeds=ie, attention_mask=att, use_cache=True)
        past = out.past_key_values
        nxt = out.logits[:, -1].argmax(-1)
        B = ids.shape[0]
        done = torch.zeros(B, dtype=torch.bool, device=ids.device)
        collected = [[] for _ in range(B)]
        for _ in range(max_new):
            done |= nxt == eos_id
            if done.all():
                break
            for i in range(B):
                if not done[i]:
                    collected[i].append(int(nxt[i]))
            step_ids = nxt.unsqueeze(1)
            g = torch.full_like(step_ids, tgt_on, dtype=torch.bool)
            step_ie = delta(emb(step_ids), step_ids, g)
            att = torch.cat([att, torch.ones(B, 1, dtype=att.dtype, device=att.device)], 1)
            out = model(inputs_embeds=step_ie, attention_mask=att,
                        past_key_values=past, use_cache=True)
            past = out.past_key_values
            nxt = out.logits[:, -1].argmax(-1)
        texts.extend(collected)
        stops.extend(done.tolist())
    return texts, stops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--delta", default=None, help="omit for an untuned BASE check")
    ap.add_argument("--arms", default="BASE,ALL,INSTRUCTION,SOURCE,PREFILL,TARGET")
    ap.add_argument("--devtest", default=str(ROOT / "data" / "devtest_en_ca.jsonl"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", default=str(ROOT / "results" / "evals"))
    ap.add_argument("--skip-forced", action="store_true")
    # Construct check: is the effect about the *learned* update, or would any
    # perturbation of these rows at these positions do it? Replaces the delta
    # with a random one matched row-by-row in norm.
    ap.add_argument("--random-delta", type=int, default=None)
    args = ap.parse_args()

    rows = read_jsonl(args.devtest)
    if args.limit:
        rows = rows[: args.limit]
    model, tok = load_backbone(args.model)
    model.eval()
    emb = model.get_input_embeddings()
    hidden = model.config.hidden_size
    delta = load_delta(model, args.delta) if args.delta else SparseDelta(hidden).cuda()
    if args.random_delta is not None:
        g = torch.Generator(device="cpu").manual_seed(args.random_delta)
        r = torch.randn(delta.weight.shape, generator=g).to(delta.weight.device)
        r = r / r.norm(dim=1, keepdim=True) * delta.weight.norm(dim=1, keepdim=True)
        delta.weight.data.copy_(r)
        print(f"random delta (seed {args.random_delta}), row norms matched", flush=True)
    pad_id, eos_id = tok.eos_token_id, tok.eos_token_id

    sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
    from sacrebleu.metrics import BLEU
    bleu = BLEU(tokenize="flores101")

    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    for arm in args.arms.split(","):
        t0 = time.time()
        gen, stopped = generate(model, emb, delta, rows, arm, pad_id, eos_id,
                                args.max_new, args.batch_size)
        # Two scorings. `raw` is the whole continuation, which is what a harness
        # that trusts the model to stop would score; `trunc` keeps only the first
        # line, which neutralises termination and leaves translation quality.
        # The parent's reported base score is only reproducible under `raw`.
        raw = [" ".join(tok.decode(g, skip_special_tokens=True).split()) for g in gen]
        trunc = [tok.decode(g, skip_special_tokens=True).strip().split("\n")[0].strip()
                 for g in gen]
        refs = [r["ref"] for r in rows]
        s_raw = bleu.corpus_score(raw, [refs])
        s_trunc = bleu.corpus_score(trunc, [refs])
        tf = [] if args.skip_forced else teacher_forced(
            model, emb, delta, rows, arm, pad_id, args.batch_size)
        rec = {"arm": arm, "tag": args.tag, "n": len(rows),
               "spbleu_raw": s_raw.score, "spbleu_trunc": s_trunc.score,
               "bleu_sig_raw": str(s_raw), "bleu_sig_trunc": str(s_trunc),
               "frac_stopped": sum(stopped) / len(stopped),
               "mean_raw_chars": sum(len(x) for x in raw) / len(raw),
               "sent_bleu_raw": [bleu.sentence_score(h, [r], ).score for h, r in zip(raw, refs)],
               "sent_bleu_trunc": [bleu.sentence_score(h, [r]).score for h, r in zip(trunc, refs)],
               # store BOTH texts: `hyps_raw` has whitespace collapsed, so the
               # first-line split is not recoverable from it downstream
               "forced": tf, "hyps_raw": raw, "hyps_trunc": trunc,
               "secs": round(time.time() - t0)}
        p = outdir / f"{args.tag}__{arm}.json"
        p.write_text(json.dumps(rec, ensure_ascii=False))
        print(f"{args.tag} {arm}: raw {s_raw.score:.2f}  trunc {s_trunc.score:.2f}"
              f"  stop {rec['frac_stopped']:.2f}  chars {rec['mean_raw_chars']:.0f}"
              + (f"  nll {sum(x['nll'] for x in tf)/max(len(tf),1):.4f}" if tf else "")
              + f"  ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
