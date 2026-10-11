#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_pilot import CFG, DEVICE, ROOT, prompt, reward, set_seed

OUT = ROOT / "results/arithmetic_calibration_seed1702"


def candidates():
    rng = np.random.default_rng(1702)
    rows = []
    for i in range(4):
        a, b = int(rng.integers(10000, 99999)), int(rng.integers(1000, 9999))
        rows.append({"family": "long_multiply", "id": f"mul-{i}", "question": f"Compute {a} * {b}.", "answer": str(a * b)})
    for i in range(4):
        a, b, c, d, e = [int(x) for x in rng.integers(100, 9999, 5)]
        rows.append({"family": "two_product_difference", "id": f"tpd-{i}",
                     "question": f"Compute ({a} * {b}) - ({c} * {d}) + {e}.", "answer": str(a*b-c*d+e)})
    for i in range(4):
        values = [int(x) for x in rng.integers(1000, 99999, 6)]
        expression = " + ".join(map(str, values))
        rows.append({"family": "six_term_sum", "id": f"sum-{i}", "question": f"Compute {expression}.", "answer": str(sum(values))})
    return rows


def main():
    set_seed(1702); OUT.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(CFG["model"], revision=CFG["model_revision"], local_files_only=True)
    if tok.pad_token_id is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        CFG["model"], revision=CFG["model_revision"], local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="sdpa"
    ).to(DEVICE).eval()
    records = []
    with torch.inference_mode():
        for row in candidates():
            rendered = prompt(tok, row["question"])
            encoded = tok(rendered, return_tensors="pt", return_token_type_ids=False).to(DEVICE)
            outputs = model.generate(**encoded, do_sample=True, temperature=CFG["temperature"], top_p=CFG["top_p"],
                                     num_return_sequences=CFG["rollouts_per_prompt"], max_new_tokens=CFG["max_new_tokens"],
                                     pad_token_id=tok.pad_token_id)
            for j, output in enumerate(outputs):
                ids = output[encoded.input_ids.shape[1]:].tolist()
                if tok.eos_token_id in ids: ids = ids[:ids.index(tok.eos_token_id)+1]
                text = tok.decode(ids, skip_special_tokens=True)
                score, parsed = reward(text, row["answer"])
                records.append({**row, "rollout": j, "reward": score, "parsed": parsed,
                                "response_tokens": len(ids), "response": text})
    with (OUT / "raw.jsonl").open("w") as f:
        for row in records: f.write(json.dumps(row) + "\n")
    summary = {}
    for family in sorted({x["family"] for x in records}):
        family_rows = [x for x in records if x["family"] == family]
        groups = [[x["reward"] for x in family_rows if x["id"] == pid] for pid in sorted({x["id"] for x in family_rows})]
        summary[family] = {"reward_mean": float(np.mean([x["reward"] for x in family_rows])),
                           "nonzero_advantage_groups": sum(len(set(g)) > 1 for g in groups), "group_rewards": groups}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()

