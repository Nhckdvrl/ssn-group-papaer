"""E08 handoff (vLLM env, single model): take the first L generated tokens of a SOURCE model's completion (from an
e04_generate.py jsonl, which stores prompt_ids and completion token_ids) and let a CONTINUATION model finish it.

For each problem, the first --k_prefix completions of the source file are used; for each L in --L ("32", "256",
"rel0.5" = half of that completion's own length) a prefix is eligible only if the source completion is longer than L
and the decoded prefix does not yet contain a final answer (\\boxed or an "Answer:" line), so the continuation is
never handed a finished solution. One continuation per eligible prefix, sampled at --tau/--top_p, optionally with
--fork_argmax (B1: argmax where entropy at T=1 >= thr). The response scored is prefix + continuation; the total
generated length (prefix + continuation) is capped at --max_total.

Output: <out_dir>/<tag>.jsonl, one row per (problem, source sample, L) with reward, lengths, finish reason, and
<tag>.meta.json with eligibility counts. Usage:
  python e08_handoff.py --model qwen3-8b-base --source /tmp/.../a_qwen3-8b_math_l5.jsonl --L 32,256,rel0.5 \\
      --k_prefix 2 --tau 1.6666667 --top_p 0.95 --max_total 8192 --out_dir /tmp/xiang_lmhead/e08/gen --tag h_P2B_math_l5
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import models
from verifier import extract_answer, is_equiv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--L", default="32,256,rel0.5")
    ap.add_argument("--k_prefix", type=int, default=2)
    ap.add_argument("--subset", default="", help="optional jsonl of problems whose indices restrict the run")
    ap.add_argument("--tau", type=float, default=1.0 / 0.6)
    ap.add_argument("--top_p", type=float, default=0.95)
    ap.add_argument("--fork_argmax", type=float, default=0.0)
    ap.add_argument("--max_total", type=int, default=8192)
    ap.add_argument("--max_model_len", type=int, default=10240)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    procs = []
    if args.fork_argmax:
        os.environ["E04_ARGMAX_THR"] = str(args.fork_argmax)
        procs.append("e04_biasproc:EntropyGatedArgmax")
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    llm = LLM(model=str(models.path(args.model)), dtype="bfloat16", seed=args.seed, gpu_memory_utilization=0.88,
              max_model_len=args.max_model_len, enable_prefix_caching=True, logits_processors=procs or None)
    tok = llm.get_tokenizer()
    vocab = tok.get_vocab()
    stop_ids = sorted({vocab[t] for t in ("<|endoftext|>", "<|im_end|>") if t in vocab} | ({tok.eos_token_id} if tok.eos_token_id is not None else set()))
    keep = None
    if args.subset:
        keep = {json.loads(l)["index"] for l in open(args.subset)}
    Ls = args.L.split(",")
    jobs, n_skip = [], {L: {"short": 0, "answered": 0, "ok": 0} for L in Ls}
    for line in open(args.source):
        r = json.loads(line)
        if keep is not None and r["index"] not in keep:
            continue
        for k, c in enumerate(r["completions"][: args.k_prefix]):
            ids = c["token_ids"]
            ids = [t for t in ids if t not in stop_ids]
            for L in Ls:
                n = int(len(ids) * float(L[3:])) if L.startswith("rel") else int(L)
                if n <= 0 or n >= len(ids):
                    n_skip[L]["short"] += 1
                    continue
                pre = tok.decode(ids[:n])
                if "\\boxed" in pre or re.search(r"Answer:\s*\S", pre):
                    n_skip[L]["answered"] += 1
                    continue
                n_skip[L]["ok"] += 1
                jobs.append({"index": r["index"], "answer": r["answer"], "k": k, "L": L, "n_prefix": n,
                             "prompt_ids": r["prompt_ids"] + ids[:n], "prefix_text": pre,
                             "src_reward": c["reward"], "src_len": len(ids)})
    sp = [SamplingParams(n=1, temperature=1.0 / args.tau, top_p=args.top_p, top_k=-1, seed=args.seed + i,
                         max_tokens=max(16, args.max_total - j["n_prefix"]), stop_token_ids=stop_ids)
          for i, j in enumerate(jobs)]
    t0 = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=j["prompt_ids"]) for j in jobs], sp)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    acc = {}
    with open(out_dir / f"{args.tag}.jsonl", "w") as f:
        for j, o in zip(jobs, outs):
            comp = o.outputs[0]
            text = j["prefix_text"] + comp.text
            pred = extract_answer(text)
            rew = float(pred is not None and is_equiv(pred, j["answer"]))
            acc.setdefault(j["L"], []).append(rew)
            f.write(json.dumps({k: j[k] for k in ("index", "k", "L", "n_prefix", "src_reward", "src_len")}
                               | {"reward": rew, "pred": pred, "cont_len": len(comp.token_ids), "finish": comp.finish_reason,
                                  "total_len": j["n_prefix"] + len(comp.token_ids), "cont_text": comp.text[-3000:]}) + "\n")
    meta = {"tag": args.tag, "model": args.model, "source": args.source, "L": Ls, "k_prefix": args.k_prefix, "tau": args.tau,
            "top_p": args.top_p, "fork_argmax": args.fork_argmax, "max_total": args.max_total, "eligibility": n_skip,
            "acc_by_L": {L: sum(v) / len(v) for L, v in acc.items()}, "n_jobs": len(jobs), "seconds": time.time() - t0}
    (out_dir / f"{args.tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
