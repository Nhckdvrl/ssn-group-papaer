"""Yes/no VQA judge with Qwen3-VL via vLLM (verl-clean env, vllm 0.11).

Two modes
- dpg:  DPG-Bench questions (ELLA@3c228f1 dpg_bench.csv) with the official dependency rule (a question
        scores 0 if any parent was answered 'no'); per-image score = mean over questions.
        NOTE: the official scorer uses mPLUG-large; this judge is a stronger VLM, so absolute numbers
        are not comparable to published DPG scores. Use it for within-study comparisons only.
- qa:   generic: a jsonl of {pidx, questions:[...]} for custom prompt sets.

Usage: python vqa_judge.py dpg <run_dir/dpg> [--model Qwen/Qwen3-VL-8B-Instruct]
Writes <run_dir>/vqa.jsonl with per-image p_yes per question and the dependency-adjusted score.
"""
import argparse
import csv
import glob
import json
import math
import os
from collections import defaultdict

from PIL import Image

MG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DPG_CSV = os.path.join(MG, "vendor", "ella", "dpg_bench", "dpg_bench.csv")


def load_dpg():
    q = defaultdict(lambda: {"qs": {}, "dep": {}})
    for row in csv.DictReader(open(DPG_CSV)):
        qid = int(row["proposition_id"])
        q[row["item_id"]]["qs"][qid] = row["question_natural_language"]
        q[row["item_id"]]["dep"][qid] = [int(d) for d in row["dependency"].split(",")]
        q[row["item_id"]]["cat"] = q[row["item_id"]].get("cat", {})
        q[row["item_id"]]["cat"][qid] = row["category_broad"]
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dpg", "qa"])
    ap.add_argument("root")
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--qfile", default=None)
    ap.add_argument("--max_pixels", type=int, default=768 * 768)
    a = ap.parse_args()

    from vllm import LLM, SamplingParams
    from transformers import AutoProcessor

    proc = AutoProcessor.from_pretrained(a.model)
    llm = LLM(model=a.model, max_model_len=4096, limit_mm_per_prompt={"image": 1},
              mm_processor_kwargs={"max_pixels": a.max_pixels}, gpu_memory_utilization=0.85)
    sp = SamplingParams(max_tokens=1, temperature=0.0, logprobs=20)
    tok = proc.tokenizer
    yes_ids = {tok.encode(w, add_special_tokens=False)[0] for w in ["Yes", "yes", " Yes", " yes"]}
    no_ids = {tok.encode(w, add_special_tokens=False)[0] for w in ["No", "no", " No", " no"]}

    if a.mode == "dpg":
        Q = load_dpg()
    out_path = os.path.join(a.root, "vqa.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {(d["pidx"], d["seed"]) for d in map(json.loads, open(out_path))}
    reqs, keys = [], []
    for d in sorted(glob.glob(os.path.join(a.root, "[0-9]" * 5))):
        meta = json.loads(open(os.path.join(d, "metadata.jsonl")).readline())
        pidx = int(os.path.basename(d))
        qs = Q[meta["item_id"]]["qs"] if a.mode == "dpg" else None
        for f in sorted(glob.glob(os.path.join(d, "samples", "*.png"))):
            seed = int(os.path.basename(f)[:-4])
            if (pidx, seed) in done:
                continue
            img = Image.open(f).convert("RGB")
            for qid, qtext in qs.items():
                msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text":
                         qtext + " Answer with Yes or No only."}]}]
                prompt = proc.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
                reqs.append({"prompt": prompt, "multi_modal_data": {"image": img}})
                keys.append((pidx, seed, meta["item_id"], qid))
    outs = llm.generate(reqs, sp) if reqs else []
    per = defaultdict(dict)
    for k, o in zip(keys, outs):
        lp = o.outputs[0].logprobs[0]
        py = sum(math.exp(v.logprob) for t, v in lp.items() if t in yes_ids)
        pn = sum(math.exp(v.logprob) for t, v in lp.items() if t in no_ids)
        per[(k[0], k[1], k[2])][k[3]] = py / max(py + pn, 1e-9)
    with open(out_path, "a") as fh:
        for (pidx, seed, item), qp in sorted(per.items()):
            hard = {q: float(p > 0.5) for q, p in qp.items()}
            adj = dict(hard)
            for q, parents in Q[item]["dep"].items():
                if any(pp != 0 and hard.get(pp, 1.0) == 0 for pp in parents):
                    adj[q] = 0.0
            cats = defaultdict(list)
            for q, v in adj.items():
                cats[Q[item]["cat"][q]].append(v)
            fh.write(json.dumps(dict(pidx=pidx, seed=seed, item_id=item, p_yes=qp,
                                     score=sum(adj.values()) / len(adj),
                                     cat={c: sum(v) / len(v) for c, v in cats.items()})) + "\n")


if __name__ == "__main__":
    main()
