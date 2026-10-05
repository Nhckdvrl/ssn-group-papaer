"""Score candidate label continuations with a frozen causal LM.

Input  : jsonl with fields {uid, prompt, cands:[c0, c1]}
Output : jsonl {uid, lp:[logp(c0+"\\n"|prompt), logp(c1+"\\n"|prompt)], lp_first:[...], ntok}
         lp is the exact sum of continuation-token log-probs (teacher forcing).
Sharding: --shard i --nshard k processes lines i::k.
"""
import argparse, json, math, os, sys, time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshard", type=int, default=1)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--suffix", default="\n\n")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--ablate", default="", help="comma list of L:H heads to zero (pre o_proj)")
    ap.add_argument("--conds", default="", help="optional comma list of conds to keep")
    args = ap.parse_args()

    rows = [json.loads(l) for i, l in enumerate(open(args.inp)) if i % args.nshard == args.shard]
    if args.conds:
        keep = set(args.conds.split(","))
        rows = [r for r in rows if r["cond"] in keep]
    done = set()
    if os.path.exists(args.out):
        done = {json.loads(l)["uid"] for l in open(args.out)}
    rows = [r for r in rows if r["uid"] not in done]
    if not rows:
        print("nothing to do"); return
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype),
                                                 device_map="cuda").eval()
    if args.ablate:
        heads = {}
        for lh in args.ablate.split(","):
            l, h = map(int, lh.split(":")); heads.setdefault(l, []).append(h)
        cfg = model.config
        hd = getattr(cfg, "head_dim", None) or cfg.hidden_size // cfg.num_attention_heads
        layers = model.model.layers
        for l, hs in heads.items():
            def pre(mod, inp, hs=hs):
                x = inp[0].clone()
                for h in hs:
                    x[..., h * hd:(h + 1) * hd] = 0
                return (x,) + tuple(inp[1:])
            layers[l].self_attn.o_proj.register_forward_pre_hook(pre)
        print("ablating", heads, flush=True)
    bos = [tok.bos_token_id] if (tok.bos_token_id is not None and
                                 tok("a")["input_ids"][:1] == [tok.bos_token_id]) else []

    # build sequences: prompt ids + continuation ids, per candidate
    seqs = []
    for r in rows:
        p_ids = bos + tok(r["prompt"], add_special_tokens=False)["input_ids"]
        for ci, c in enumerate(r["cands"]):
            full = tok(r["prompt"] + c + args.suffix, add_special_tokens=False)["input_ids"]
            full = bos + full
            # continuation = tokens after the longest common prefix with prompt ids
            k = 0
            while k < min(len(p_ids), len(full)) and p_ids[k] == full[k]:
                k += 1
            seqs.append((r["uid"], ci, full, k))
    order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i][2]))
    res = {}
    t0 = time.time()
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    with torch.no_grad():
        for b in range(0, len(order), args.bs):
            idx = order[b:b + args.bs]
            L = max(len(seqs[i][2]) for i in idx)
            K = max(len(seqs[i][2]) - seqs[i][3] for i in idx) + 1      # positions needed at the end
            ids = torch.full((len(idx), L), pad, dtype=torch.long)
            att = torch.zeros((len(idx), L), dtype=torch.long)
            for j, i in enumerate(idx):                                  # LEFT padding
                s_ = seqs[i][2]
                ids[j, L - len(s_):] = torch.tensor(s_); att[j, L - len(s_):] = 1
            pos = (att.cumsum(1) - 1).clamp(min=0)
            out = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=pos.cuda(),
                        logits_to_keep=K, use_cache=False)
            logp = torch.log_softmax(out.logits.float(), -1)             # (B, K, V): logits for positions L-K..L-1
            for j, i in enumerate(idx):
                uid, ci, s_, k = seqs[i]
                n_cont = len(s_) - k
                tgt = torch.tensor(s_[k:], device=logp.device)
                # token at absolute (padded) position L-n_cont+m is predicted by logits at L-n_cont+m-1
                rel = torch.arange(K - 1 - n_cont, K - 1, device=logp.device)
                lps = logp[j, rel, tgt]
                res.setdefault(uid, {})[ci] = (float(lps.sum()), float(lps[0]), n_cont)
            if b // args.bs % 50 == 0:
                print(f"{b}/{len(order)} {time.time()-t0:.0f}s", flush=True)
    with open(args.out, "a") as f:
        for r in rows:
            d = res[r["uid"]]
            f.write(json.dumps({"uid": r["uid"], "lp": [d[0][0], d[1][0]], "lp_first": [d[0][1], d[1][1]],
                                "ntok": [d[0][2], d[1][2]]}) + "\n")
    print("done", len(rows), f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
