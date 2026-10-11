"""E09: does explicit reasoning (Qwen3 thinking mode) recover latent-level temporal inference?

usage: run_think.py --model M --inp rows.jsonl --conds c1,c2 --max_bases N --n 8 --think 1 --out out.jsonl
Each raw few-shot prompt is wrapped as a chat user turn:
  <raw prompt without the final 'Label:'> + question; the model must end with 'Answer: <label>'.
P(B) is estimated from n samples (temperature 0.6, top_p 0.95 as recommended for Qwen3 thinking;
non-thinking control uses the same sampling).
"""
import argparse, json, re
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

Q = ("\n\nWhat is the label of the last item? Think it through, then give your final answer "
     "on the last line in the form 'Answer: <label>' using one of the two labels above.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--inp"); ap.add_argument("--conds"); ap.add_argument("--out")
    ap.add_argument("--max_bases", type=int, default=100); ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--think", type=int, default=1); ap.add_argument("--max_tokens", type=int, default=6000); ap.add_argument("--max_model_len", type=int, default=8192)
    a = ap.parse_args()
    conds = set(a.conds.split(","))
    tok = AutoTokenizer.from_pretrained(a.model)
    rows, bases = [], []
    for l in open(a.inp):
        r = json.loads(l)
        if r["cond"] not in conds:
            continue
        if r["base_id"] not in bases:
            if len(bases) >= a.max_bases:
                continue
            bases.append(r["base_id"])
        rows.append(r)
    prompts = []
    for r in rows:
        body = r["prompt"]
        assert body.endswith("Label:")
        body = body[: -len("Label:")].rstrip() + Q
        msgs = [{"role": "user", "content": body}]
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                               enable_thinking=bool(a.think)))
    llm = LLM(a.model, dtype="bfloat16", max_model_len=a.max_model_len, gpu_memory_utilization=0.88, seed=0)
    sp = SamplingParams(n=a.n, temperature=0.6, top_p=0.95, top_k=20, max_tokens=a.max_tokens, seed=0)
    outs = llm.generate(prompts, sp)
    with open(a.out, "w") as f:
        for r, o in zip(rows, outs):
            words = [c.strip() for c in r["cands"]]
            ans = []
            tails = []
            for c in o.outputs:
                txt = c.text
                tail = txt[-300:]
                tails.append(tail)
                hits = [(m.start(), k) for k, w in enumerate(words)
                        for m in re.finditer(r"(?i)(?<![a-z])" + re.escape(w) + r"(?![a-z])", tail)]
                ans.append(max(hits)[1] if hits else -1)
            nB = sum(1 for x in ans if x == r["query_label_B"]); nA = sum(1 for x in ans if x == r["query_label_A"])
            f.write(json.dumps({"uid": r["uid"], "cond": r["cond"], "base_id": r["base_id"], "ans": ans,
                                "nB": nB, "nA": nA, "n": len(ans),
                                "lens": [len(c.token_ids) for c in o.outputs],
                                "tails": tails, "sample_text": o.outputs[0].text[-1500:]}) + "\n")
    print("done", len(rows))


if __name__ == "__main__":
    main()
