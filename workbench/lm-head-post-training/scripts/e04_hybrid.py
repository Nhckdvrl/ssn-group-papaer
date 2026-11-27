"""E04-D: fork-swap decoding. Two models (parent = base, child = post-trained) decode in lockstep on the same prefix;
at each step a 'fork' is a position where the BASE model's next-token entropy (T=1) is ≥ thr.
Conditions (--mode):
  base                : sample from base everywhere (control; thr irrelevant)
  post                : sample from post everywhere (control)
  base_postfork       : base everywhere, at forks sample from post
  post_basefork       : post everywhere, at forks sample from base
  base_basemode       : base everywhere, at forks take base argmax   (≈ entropy-gated sharpening, τ→∞)
  base_postmode       : base everywhere, at forks take post argmax
  post_basemode       : post everywhere, at forks take base argmax                     (E06)
  post_postmode       : post everywhere, at forks take post argmax                     (E06, choice contrast)
  post_basetrunc      : post everywhere, at forks sample base restricted to p ≥ 0.1·p_max (E06)
  base_basetrunc      : base everywhere, at forks sample base restricted to p ≥ 0.1·p_max (E06)
Deterministic grid (E07; no sampling anywhere, every argmax disagreement falls in exactly one of two sets):
  greedy_base         : base argmax everywhere
  greedy_post         : post argmax everywhere
  greedy_base_postfork: base argmax, but post argmax where base H ≥ thr
  greedy_base_postlow : base argmax, but post argmax where base H < thr and the two argmaxes differ
Positive controls: base_postfork with thr=1e9 ≡ base; with thr=-1 ≡ post.
Both models see the identical token sequence (same tokenizer), so the only difference between conditions is who
chooses the token at fork positions. Records fork rate and how often the two models' argmax agree at forks.

Usage: python e04_hybrid.py qwen-base__post --mode base_postmode --thr 0.5 --n 1 --seed 0 --tag name
"""
import argparse
import json
import time
from pathlib import Path

import torch

import models
from e04_generate import render
from verifier import extract_answer, is_equiv

BIG = Path("/tmp/xiang_lmhead/e04/gen")


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--mode", required=True)
    ap.add_argument("--thr", type=float, default=0.5)
    ap.add_argument("--template", default="qwen_chat")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--max_tokens", type=int, default=3072)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--start", type=int, default=0, help="first problem (for sharding a run across GPUs)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--problems", default="/tmp/xiang_lmhead/e04/math500.jsonl")
    ap.add_argument("--out_dir", default=str(BIG))
    ap.add_argument("--force_prefix", default="", help="text appended to every rendered prompt (unicode escapes decoded)")
    args = ap.parse_args()
    dev = "cuda"; t0 = time.time()
    torch.manual_seed(args.seed)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    p0, p1, _ = models.PAIRS[args.pair]
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    m0 = AutoModelForCausalLM.from_pretrained(models.path(p0), dtype=torch.bfloat16).to(dev).eval()
    m1 = AutoModelForCausalLM.from_pretrained(models.path(p1), dtype=torch.bfloat16).to(dev).eval()
    vocab = tok.get_vocab()
    stop = torch.tensor(sorted({vocab[t] for t in ("<|endoftext|>", "<|im_end|>") if t in vocab}
                               | ({tok.eos_token_id} if tok.eos_token_id is not None else set())), device=dev)
    big = Path(args.out_dir); big.mkdir(parents=True, exist_ok=True)
    force = args.force_prefix.encode().decode("unicode_escape") if args.force_prefix else ""
    probs = [json.loads(l) for l in open(args.problems)]
    if args.limit:
        probs = probs[: args.limit]
    probs = probs[args.start:]
    jobs = [(p, k) for p in probs for k in range(args.n)]
    # resume: keep finished (index, sample) pairs from a previous partial run
    done_rows = []
    if (big / f"{args.tag}.jsonl").exists():
        done_rows = [json.loads(l) for l in open(big / f"{args.tag}.jsonl")]
    finished = {(r["index"], r["sample"]) for r in done_rows}
    jobs = [(p, k) for p, k in jobs if (p["index"], k) not in finished]
    out_f = open(big / f"{args.tag}.jsonl", "a")
    n_ok = n_parse = n_trunc = n_tok = n_fork = n_agree = 0
    pad = tok.pad_token_id if tok.pad_token_id is not None else int(stop[0])
    for b0 in range(0, len(jobs), args.bs):
        batch = jobs[b0: b0 + args.bs]
        texts = [render(args.template, p["problem"], tok) + force for p, _ in batch]
        enc = [tok(t, add_special_tokens=False)["input_ids"] for t in texts]
        L = max(len(e) for e in enc)
        ids = torch.tensor([[pad] * (L - len(e)) + e for e in enc], device=dev)
        att = (torch.arange(L, device=dev)[None, :] >= torch.tensor([L - len(e) for e in enc], device=dev)[:, None]).long()
        pos = (att.cumsum(-1) - 1).clamp_min(0)
        o0 = m0(input_ids=ids, attention_mask=att, position_ids=pos, use_cache=True)
        o1 = m1(input_ids=ids, attention_mask=att, position_ids=pos, use_cache=True)
        kv0, kv1 = o0.past_key_values, o1.past_key_values
        z0, z1 = o0.logits[:, -1].float(), o1.logits[:, -1].float()
        B = len(batch)
        done = torch.zeros(B, dtype=torch.bool, device=dev)
        gen = [[] for _ in range(B)]
        nfork = torch.zeros(B, device=dev); nagree = torch.zeros(B, device=dev)
        ndis_hi = torch.zeros(B, device=dev); ndis_lo = torch.zeros(B, device=dev)
        swaps = [[] for _ in range(B)]
        cur_pos = pos[:, -1]
        for step in range(args.max_tokens):
            lp0 = torch.log_softmax(z0, -1); lp1 = torch.log_softmax(z1, -1)
            H0 = -(lp0.exp() * lp0).sum(-1)
            fork = H0 >= args.thr
            s0 = torch.multinomial(lp0.exp(), 1).squeeze(1); s1 = torch.multinomial(lp1.exp(), 1).squeeze(1)
            a0 = lp0.argmax(-1); a1 = lp1.argmax(-1)
            if args.mode.endswith("basetrunc"):
                q0 = lp0.exp(); q0 = q0 * (q0 >= 0.1 * q0.max(-1, keepdim=True).values)
                t0s = torch.multinomial(q0, 1).squeeze(1)
            if args.mode == "base":
                nxt = s0
            elif args.mode == "post":
                nxt = s1
            elif args.mode == "base_postfork":
                nxt = torch.where(fork, s1, s0)
            elif args.mode == "post_basefork":
                nxt = torch.where(fork, s0, s1)
            elif args.mode == "base_basemode":
                nxt = torch.where(fork, a0, s0)
            elif args.mode == "base_postmode":
                nxt = torch.where(fork, a1, s0)
            elif args.mode == "post_postmode":
                nxt = torch.where(fork, a1, s1)
            elif args.mode == "post_basemode":
                nxt = torch.where(fork, a0, s1)
            elif args.mode == "post_basetrunc":
                nxt = torch.where(fork, t0s, s1)
            elif args.mode == "base_basetrunc":
                nxt = torch.where(fork, t0s, s0)
            elif args.mode == "greedy_base":
                nxt = a0
            elif args.mode == "greedy_post":
                nxt = a1
            elif args.mode == "greedy_base_postfork":
                nxt = torch.where(fork, a1, a0)
            elif args.mode == "greedy_base_postlow":
                nxt = torch.where(~fork & (a0 != a1), a1, a0)
            else:
                raise ValueError(args.mode)
            live = ~done
            nfork += (fork & live).float(); nagree += (fork & live & (a0 == a1)).float()
            dis = live & (a0 != a1)
            ndis_hi += (dis & fork).float(); ndis_lo += (dis & ~fork).float()
            if args.mode.startswith("greedy_base_"):
                for i in torch.nonzero(dis & (nxt != a0)).flatten().tolist():
                    if len(swaps[i]) < 300:
                        swaps[i].append([len(gen[i]), int(a0[i]), int(a1[i]), round(float(H0[i]), 3)])
            nxt = torch.where(done, torch.full_like(nxt, pad), nxt)
            for i in torch.nonzero(live).flatten().tolist():
                gen[i].append(int(nxt[i]))
            done = done | torch.isin(nxt, stop)
            if bool(done.all()):
                break
            att = torch.cat([att, (~done | torch.isin(nxt, stop)).long()[:, None]], 1)
            cur_pos = cur_pos + 1
            o0 = m0(input_ids=nxt[:, None], attention_mask=att, position_ids=cur_pos[:, None], past_key_values=kv0, use_cache=True)
            o1 = m1(input_ids=nxt[:, None], attention_mask=att, position_ids=cur_pos[:, None], past_key_values=kv1, use_cache=True)
            kv0, kv1 = o0.past_key_values, o1.past_key_values
            z0, z1 = o0.logits[:, -1].float(), o1.logits[:, -1].float()
        for i, (p, k) in enumerate(batch):
            g = gen[i]
            text = tok.decode([t for t in g if t not in stop.tolist()])
            pred = extract_answer(text)
            r = float(pred is not None and is_equiv(pred, p["answer"]))
            trunc = not (g and g[-1] in stop.tolist())
            n_ok += r; n_parse += pred is None; n_trunc += trunc; n_tok += len(g)
            n_fork += float(nfork[i]); n_agree += float(nagree[i])
            out_f.write(json.dumps({"index": p["index"], "answer": p["answer"], "sample": k, "text": text, "pred": pred, "reward": r,
                                    "n_tokens": len(g), "n_fork": float(nfork[i]), "n_fork_agree": float(nagree[i]), "truncated": trunc,
                                    "n_dis_hi": float(ndis_hi[i]), "n_dis_lo": float(ndis_lo[i]), "swaps": swaps[i]}) + "\n")
        out_f.flush()
        print(f"batch {b0 // args.bs}: acc so far (this run) {n_ok / (b0 + B):.3f} {time.time() - t0:.0f}s", flush=True)
    allrows = [json.loads(l) for l in open(big / f"{args.tag}.jsonl")]
    N = len(allrows)
    n_ok = sum(r["reward"] for r in allrows); n_parse = sum(r["pred"] is None for r in allrows)
    n_trunc = sum(r["truncated"] for r in allrows); n_tok = sum(r["n_tokens"] for r in allrows)
    n_fork = sum(r["n_fork"] for r in allrows); n_agree = sum(r["n_fork_agree"] for r in allrows)
    meta = {"tag": args.tag, "pair": args.pair, "mode": args.mode, "thr": args.thr, "n": args.n, "seed": args.seed, "N": N,
            "accuracy": n_ok / N, "parse_fail": n_parse / N, "truncated": n_trunc / N, "mean_len": n_tok / N,
            "fork_rate": n_fork / max(1, n_tok), "argmax_agree_at_forks": n_agree / max(1, n_fork), "seconds": time.time() - t0}
    (big / f"{args.tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
