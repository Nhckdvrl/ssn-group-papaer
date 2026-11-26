"""E02 step 1: on-policy rollouts with vLLM + binary verifier reward. No parameter updates.

Sampling is pure ancestral sampling (temperature 1, top_p 1, top_k off) so the behaviour policy equals the
model softmax that the replay in e02_geometry.py recomputes. Saves token ids and vLLM sampled-token logprobs
(for the replay alignment check).

Usage (vLLM env): python e02_rollout.py --model qwen3-8b-base --n 8 --max_tokens 2048 [--limit 8]
Output: /tmp/xiang_lmhead/e02/rollouts_<model>.jsonl (node-local; summary copied to results/e02 by geometry step)
"""
import argparse
import json
import time
from pathlib import Path

import models
from verifier import extract_boxed, is_equiv

TEMPLATE = ("Solve the following math problem. Reason step by step, and put your final answer within \\boxed{{}}.\n\n"
            "Problem: {problem}\n\nSolution:")


def prompt_text(problem, model, tok):
    if model == "qwen3-8b":   # post-trained model: its own chat template, non-thinking mode
        msgs = [{"role": "user", "content": TEMPLATE.format(problem=problem).rsplit("\n\nSolution:", 1)[0]}]
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return TEMPLATE.format(problem=problem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-8b-base")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--max_tokens", type=int, default=2048)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams
    # materialised by `python build_inputs.py --export-e02` (vLLM env has no `datasets`)
    prompts = [json.loads(l) for l in open("/tmp/xiang_lmhead/e02/prompts.jsonl")]
    if args.limit:
        prompts = prompts[: args.limit]
    llm = LLM(model=str(models.path(args.model)), dtype="bfloat16", seed=args.seed, gpu_memory_utilization=0.85,
              max_model_len=4096, enable_prefix_caching=True)
    tok = llm.get_tokenizer()
    texts = [prompt_text(p["problem"], args.model, tok) for p in prompts]
    sp = SamplingParams(n=args.n, temperature=1.0, top_p=1.0, top_k=-1, max_tokens=args.max_tokens,
                        logprobs=0, seed=args.seed, stop=["\n\nProblem:"] if args.model != "qwen3-8b" else None)
    t0 = time.time()
    outs = llm.generate(texts, sp)
    gen_s = time.time() - t0
    out_dir = Path("/tmp/xiang_lmhead/e02"); out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.model}" + (f"_limit{args.limit}" if args.limit else "")
    n_tok = 0
    with open(out_dir / f"rollouts_{tag}.jsonl", "w") as f:
        for p, text, o in zip(prompts, texts, outs):
            comps = []
            for c in o.outputs:
                pred = extract_boxed(c.text)
                lps = [list(d.values())[0].logprob if d else None for d in (c.logprobs or [])]
                comps.append({"token_ids": list(c.token_ids), "text": c.text, "finish": c.finish_reason,
                              "pred": pred, "parse_fail": pred is None,
                              "reward": float(pred is not None and p["answer"] is not None and is_equiv(pred, p["answer"])),
                              "vllm_logprobs": lps})
                n_tok += len(c.token_ids)
            f.write(json.dumps({"subject": p["subject"], "index": p["index"], "level": p["level"], "answer": p["answer"],
                                "prompt": text, "prompt_ids": list(o.prompt_token_ids), "completions": comps}) + "\n")
    meta = {"model": args.model, "revision": models.revision(args.model), "n": args.n, "max_tokens": args.max_tokens,
            "seed": args.seed, "n_prompts": len(prompts), "gen_seconds": gen_s, "n_completion_tokens": n_tok,
            "template": TEMPLATE, "sampling": "T=1, top_p=1, top_k=-1"}
    (out_dir / f"rollouts_{tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
