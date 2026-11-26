"""E04 generation: sample responses with a model's evaluation template, optionally with a global affine
intervention on the logits (τ·z + s·b), and score them with the verifier.

Templates
  qwen_chat   : model's chat template, non-thinking, "Please reason step by step, and put your final answer
                within \\boxed{}." (Qwen3 math prompt)
  olmo_rlzero : the RL-Zero-Math chat_template.jinja text (plain text, "Answer: ..." line), used for both
                OLMo-3 Base and RL-Zero-Math so that parent and child see identical prompts
Prompt sets: train128 (= E02 MATH-train set, /tmp/xiang_lmhead/e02/prompts.jsonl), math500 (/tmp/xiang_lmhead/e04/math500.jsonl)

Usage: python e04_generate.py --model qwen3-8b --template qwen_chat --prompts train128 --n 2 \
         [--bias path.npz --bias_key b --bias_scale -1 --tau 1.0] --tag name
"""
import argparse
import json
import os
import time
from pathlib import Path

import models
from verifier import extract_answer, is_equiv

QWEN_SUFFIX = "\nPlease reason step by step, and put your final answer within \\boxed{}."
OLMO_PREFIX = ("Solve the following math problem step by step. The last line of your response should be the answer to "
               "the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem.\n\n")
OLMO_SUFFIX = "\n\nRemember to put your answer on its own line after \"Answer:\""


def render(template, problem, tok):
    if template == "qwen_chat":
        return tok.apply_chat_template([{"role": "user", "content": problem + QWEN_SUFFIX}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False)
    if template == "plain_math":   # template-robustness check: no chat markup at all
        return "Problem: " + problem + QWEN_SUFFIX + "\nSolution:"
    if template == "olmo_rlzero":
        return OLMO_PREFIX + problem + "\n" + OLMO_SUFFIX
    raise ValueError(template)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--prompts", default="train128")
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--max_tokens", type=int, default=3072)
    ap.add_argument("--max_model_len", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tau", type=float, default=1.0, help="logits = tau*z + bias_scale*b  (implemented as T=1/tau)")
    ap.add_argument("--bias", default="")
    ap.add_argument("--bias_key", default="b")
    ap.add_argument("--bias_scale", type=float, default=1.0)
    ap.add_argument("--gate", default="", help="entropy-gated temperature: '<low|high>:<thr>:<tau>'")
    ap.add_argument("--min_p", type=float, default=0.0)
    ap.add_argument("--top_p", type=float, default=1.0)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    if args.bias:   # (z + s*b/τ)/(1/τ) = τ z + s b
        os.environ["E04_BIAS"], os.environ["E04_BIAS_KEY"] = args.bias, args.bias_key
        os.environ["E04_BIAS_SCALE"] = str(args.bias_scale / args.tau)
    procs = ["e04_biasproc:GlobalBias"] if args.bias else []
    if args.gate:
        mode, thr, gtau = args.gate.split(":")
        os.environ["E04_GATE_MODE"], os.environ["E04_GATE_THR"], os.environ["E04_GATE_TAU"] = mode, thr, gtau
        procs.append("e04_biasproc:EntropyGatedTemperature")
    from vllm import LLM, SamplingParams
    src = {"train128": "/tmp/xiang_lmhead/e02/prompts.jsonl", "math500": "/tmp/xiang_lmhead/e04/math500.jsonl"}[args.prompts]
    prompts = [json.loads(l) for l in open(src)]
    llm = LLM(model=str(models.path(args.model)), dtype="bfloat16", seed=args.seed, gpu_memory_utilization=0.85,
              max_model_len=args.max_model_len, enable_prefix_caching=True,
              logits_processors=procs or None)
    tok = llm.get_tokenizer()
    texts = [render(args.template, p["problem"], tok) for p in prompts]
    # identical stopping rule for parent and child (base configs list only <|endoftext|>)
    vocab = tok.get_vocab()
    stop_ids = sorted({vocab[t] for t in ("<|endoftext|>", "<|im_end|>") if t in vocab} | ({tok.eos_token_id} if tok.eos_token_id is not None else set()))
    sp = SamplingParams(n=args.n, temperature=1.0 / args.tau, top_p=args.top_p, min_p=args.min_p, top_k=-1, max_tokens=args.max_tokens,
                        seed=args.seed, logprobs=0, stop_token_ids=stop_ids)
    t0 = time.time()
    outs = llm.generate(texts, sp)
    out_dir = Path("/tmp/xiang_lmhead/e04/gen"); out_dir.mkdir(parents=True, exist_ok=True)
    n_ok = n_all = n_tok = n_parse = n_trunc = 0
    with open(out_dir / f"{args.tag}.jsonl", "w") as f:
        for p, text, o in zip(prompts, texts, outs):
            comps = []
            for c in o.outputs:
                pred = extract_answer(c.text)
                r = float(pred is not None and p["answer"] is not None and is_equiv(pred, p["answer"]))
                comps.append({"token_ids": list(c.token_ids), "text": c.text, "finish": c.finish_reason, "pred": pred,
                              "reward": r, "logprobs": [list(d.values())[0].logprob if d else None for d in (c.logprobs or [])]})
                n_ok += r; n_all += 1; n_tok += len(c.token_ids); n_parse += pred is None; n_trunc += c.finish_reason == "length"
            f.write(json.dumps({**{k: p[k] for k in ("index", "answer") if k in p}, "subject": p.get("subject"),
                                "level": p.get("level"), "prompt": text, "prompt_ids": list(o.prompt_token_ids),
                                "completions": comps}) + "\n")
    meta = {"tag": args.tag, "model": args.model, "revision": models.revision(args.model), "template": args.template,
            "prompts": args.prompts, "n": args.n, "max_tokens": args.max_tokens, "max_model_len": args.max_model_len, "seed": args.seed, "tau": args.tau,
            "stop_token_ids": stop_ids, "gate": args.gate, "min_p": args.min_p, "top_p": args.top_p, "bias": args.bias, "bias_key": args.bias_key, "bias_scale": args.bias_scale, "accuracy": n_ok / n_all,
            "parse_fail": n_parse / n_all, "truncated": n_trunc / n_all, "mean_len": n_tok / n_all, "seconds": time.time() - t0}
    (out_dir / f"{args.tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
