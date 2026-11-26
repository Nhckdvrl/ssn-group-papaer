"""E05 step 2 (vLLM env): for each extracted fork and candidate token c ∈ {c_base, c_post, c_alt}, let the PARENT
model continue from prefix + c, K times at T=1 until it stops, and score correctness with the same verifier.
v(c) = fraction correct, ℓ(c) = mean per-token log-prob of the continuation under the parent.
Agree forks are rolled out twice independently with the same token (Monte-Carlo noise floor).

Usage: python e05_rollout.py <pair_key> [--K 8 --max_tokens 2048]
"""
import argparse
import json
import time
from pathlib import Path

import models
from verifier import extract_answer, is_equiv

DIR = Path("/tmp/xiang_lmhead/e05")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--max_tokens", type=int, default=2048)
    ap.add_argument("--max_model_len", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--continue_with", default="parent", choices=["parent", "child"],
                    help="which model continues after the fork token (child = value under the post-trained policy)")
    args = ap.parse_args()
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    p0, p1, _ = models.PAIRS[args.pair]
    cont = p0 if args.continue_with == "parent" else p1
    forks = [json.loads(l) for l in open(DIR / f"forks_{args.pair}.jsonl")]
    llm = LLM(model=str(models.path(cont)), dtype="bfloat16", seed=args.seed, gpu_memory_utilization=0.85,
              max_model_len=args.max_model_len, enable_prefix_caching=True)
    tok = llm.get_tokenizer()
    vocab = tok.get_vocab()
    stop_ids = sorted({vocab[t] for t in ("<|endoftext|>", "<|im_end|>") if t in vocab} | ({tok.eos_token_id} if tok.eos_token_id is not None else set()))
    jobs = []
    for i, f in enumerate(forks):
        cands = [("base", f["c_base"]), ("post", f["c_post"])] if f["kind"] == "changed" else [("base", f["c_base"]), ("base_rep", f["c_base"])]
        if f["kind"] == "changed" and f["c_alt"] is not None:
            cands.append(("alt", f["c_alt"]))
        for name, c in cands:
            if len(f["prefix_ids"]) + 1 + args.max_tokens > args.max_model_len:
                continue
            jobs.append((i, name, c))
    prompts = [TokensPrompt(prompt_token_ids=forks[i]["prefix_ids"] + [c]) for i, _, c in jobs]
    sp = SamplingParams(n=args.K, temperature=1.0, top_p=1.0, top_k=-1, max_tokens=args.max_tokens, seed=args.seed,
                        logprobs=0, stop_token_ids=stop_ids)
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    res = {}
    for (i, name, c), o in zip(jobs, outs):
        f = forks[i]
        head = tok.decode(f["prefix_ids"][f["n_prompt"]:] + [c])
        corr, lps, trunc = [], [], []
        for comp in o.outputs:
            text = head + comp.text
            pred = extract_answer(text)
            corr.append(float(pred is not None and is_equiv(pred, f["answer"])))
            lp = [list(d.values())[0].logprob for d in (comp.logprobs or []) if d]
            lps.append(sum(lp) / max(1, len(lp))); trunc.append(comp.finish_reason == "length")
        res.setdefault(i, {})[name] = {"token": c, "v": sum(corr) / len(corr), "ell": sum(lps) / len(lps), "trunc": sum(trunc) / len(trunc)}
    suffix = "" if args.continue_with == "parent" else "__childcont"
    with open(DIR / f"rollouts_{args.pair}{suffix}.jsonl", "w") as fo:
        for i, f in enumerate(forks):
            if i in res:
                fo.write(json.dumps({k: f[k] for k in ("prompt_index", "sample", "t", "kind", "c_base", "c_post", "c_alt", "lp0", "lp1", "H0", "H1")}
                                    | {"cands": res[i]}) + "\n")
    print(json.dumps({"pair": args.pair, "continue_with": cont, "n_jobs": len(jobs), "seconds": time.time() - t0}))


if __name__ == "__main__":
    main()
