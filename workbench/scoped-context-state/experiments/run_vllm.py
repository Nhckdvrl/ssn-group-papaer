"""Run verified items through an open model with vLLM (fgvd env).
python run_vllm.py items.jsonl out.jsonl MODEL_DIR_OR_ID {think|nothink|plain} [tp] [max_new]
Writes one row per prompt: id, cond, gold, pred, text tail.  Greedy decoding.
"""
import json, re, sys
from vllm import LLM, SamplingParams

items_p, out_p, model, mode = sys.argv[1:5]
tp = int(sys.argv[5]) if len(sys.argv) > 5 else 1
max_new = int(sys.argv[6]) if len(sys.argv) > 6 else (12000 if mode == "think" else 1024)
items = [json.loads(l) for l in open(items_p)]
llm = LLM(model, tensor_parallel_size=tp, max_model_len=max_new + 3000, gpu_memory_utilization=0.9,
          enable_prefix_caching=True, trust_remote_code=True)
sp = SamplingParams(temperature=0.0, max_tokens=max_new)
kw = {}
if mode == "think":
    kw = dict(chat_template_kwargs={"enable_thinking": True})
elif mode == "nothink":
    kw = dict(chat_template_kwargs={"enable_thinking": False})
msgs = [[{"role": "user", "content": it["prompt"]}] for it in items]
outs = llm.chat(msgs, sp, **kw)


def parse(t):
    t = t.split("</think>")[-1]
    m = re.findall(r"Answer:\s*\**\s*(Yes|No)", t, flags=re.I)
    return m[-1].capitalize() if m else None


with open(out_p, "w") as f:
    for it, o in zip(items, outs):
        t = o.outputs[0].text
        f.write(json.dumps(dict(id=it["id"], cond=it["cond"], family=it["family"], depth=it["depth"],
                                gold=it["gold"], base=it["base"], pred=parse(t), ntok=len(o.outputs[0].token_ids),
                                tail=t[-400:])) + "\n")
print("done", len(items))
