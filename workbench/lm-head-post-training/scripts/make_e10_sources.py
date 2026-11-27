"""E10: turn E07 lockstep trajectories (text only) into e04_generate-style source files for e08_handoff.py.
For each problem: prompt_ids = qwen_chat render (Qwen3-8B tokenizer, as in e04_hybrid), one completion whose token_ids
are the re-encoded trajectory text. Usage: python make_e10_sources.py <e07_tag> <out_jsonl>"""
import json
import sys

import models
from e04_generate import render


def main():
    tag, out = sys.argv[1:3]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path("qwen3-8b"))
    probs = {json.loads(l)["index"]: json.loads(l) for l in open("/tmp/xiang_lmhead/e07/math_l5.jsonl")}
    with open(out, "w") as f:
        for l in open(f"/tmp/xiang_lmhead/e07/gen/{tag}.jsonl"):
            r = json.loads(l)
            p = probs[r["index"]]
            ids = tok(render("qwen_chat", p["problem"], tok), add_special_tokens=False)["input_ids"]
            f.write(json.dumps({"index": r["index"], "answer": p["answer"], "prompt_ids": ids,
                                "completions": [{"token_ids": tok(r["text"], add_special_tokens=False)["input_ids"],
                                                 "reward": r["reward"], "finish": "length" if r["truncated"] else "stop"}]}) + "\n")


if __name__ == "__main__":
    main()
