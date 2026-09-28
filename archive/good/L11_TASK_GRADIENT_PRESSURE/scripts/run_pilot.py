#!/usr/bin/env python3
import json
import math
import os
import random
import re
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from huggingface_hub import model_info
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/pilot.json").read_text())
CFG["seed"] = int(os.environ.get("L11_SEED", CFG["seed"]))
OUT = ROOT / f"results/pilot_seed{CFG['seed']}_len{CFG['max_new_tokens']}"
DEVICE = "cuda:0"


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def numeric(text):
    text = text.replace(",", "").strip()
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return float(text)
    return None


def build_data():
    arithmetic = []
    # Continue the exact RNG stream used by the preregistered calibration:
    # four long-multiply pairs and four five-value two-product rows precede these sums.
    rng = np.random.default_rng(1702)
    rng.integers(10000, 99999, 4 * 2)
    rng.integers(100, 9999, 4 * 5)
    for i in range(12):
        values = [int(x) for x in rng.integers(1000, 99999, 6)]
        expression = " + ".join(map(str, values))
        arithmetic.append({"id": f"sum-{i}", "question": f"Compute {expression}.", "answer": str(sum(values))})
    math = load_dataset("HuggingFaceH4/MATH-500", split="test")
    math_numeric = []
    for row in math:
        if numeric(row["answer"]) is not None and len(row["problem"]) < 700:
            math_numeric.append({"id": row["unique_id"], "question": row["problem"], "answer": row["answer"]})
    if len(math_numeric) < 12:
        raise RuntimeError("not enough numeric MATH-500 examples")
    return {"arithmetic": arithmetic[:12], "math500_numeric": math_numeric[:12]}


def prompt(tokenizer, question):
    content = (
        f"Solve the following problem. Show your reasoning, then put only the final answer inside "
        f"<answer> and </answer> tags.\n\n{question}"
    )
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": content}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def reward(text, gold):
    found = re.search(r"<answer>\s*(.*?)\s*</answer>", text, flags=re.S | re.I)
    if not found:
        return CFG["reward_missing_format"], None
    pred = numeric(found.group(1))
    target = numeric(gold)
    if pred is not None and target is not None and math.isclose(pred, target, rel_tol=1e-6, abs_tol=1e-6):
        return CFG["reward_correct"], pred
    return CFG["reward_wrong"], pred


def rollout_loss(model, tokenizer, item, parameters):
    full = item["prompt_ids"] + item["response_ids"]
    input_ids = torch.tensor(full, device=DEVICE).unsqueeze(0)
    logits = model(input_ids=input_ids, use_cache=False).logits[:, :-1]
    labels = input_ids[:, 1:]
    start = len(item["prompt_ids"]) - 1
    token_logp = torch.log_softmax(logits[:, start:].float(), dim=-1).gather(-1, labels[:, start:].unsqueeze(-1)).squeeze(-1)
    objective = token_logp.mean() * item["advantage"]
    grads = torch.autograd.grad(-objective, parameters, retain_graph=False, allow_unused=False)
    stride = CFG["anatomy_sketch_stride"]
    # Deterministic coordinate sketch; sqrt(stride) approximately restores norm scale.
    return torch.cat([g.detach().float().flatten()[::stride].cpu() for g in grads]) * math.sqrt(stride)


def aggregate_grad(model, tokenizer, items, parameters, sketch_stride=None):
    model.zero_grad(set_to_none=True)
    losses = []
    for item in items:
        full = item["prompt_ids"] + item["response_ids"]
        ids = torch.tensor(full, device=DEVICE).unsqueeze(0)
        logits = model(input_ids=ids, use_cache=False).logits[:, :-1]
        labels = ids[:, 1:]
        start = len(item["prompt_ids"]) - 1
        logp = torch.log_softmax(logits[:, start:].float(), dim=-1).gather(-1, labels[:, start:].unsqueeze(-1)).squeeze(-1)
        losses.append(-logp.mean() * item["advantage"])
    torch.stack(losses).mean().backward()
    if sketch_stride is None:
        return torch.cat([p.grad.detach().float().flatten().cpu() for p in parameters])
    return torch.cat([p.grad.detach().float().flatten()[::sketch_stride].cpu() for p in parameters]) * math.sqrt(sketch_stride)


def bootstrap_cross_product(group_vectors, draws):
    matrix = torch.stack(group_vectors)
    gram = matrix @ matrix.T
    rng = np.random.default_rng(CFG["seed"])
    estimates = []
    n = len(group_vectors)
    half = n // 2
    for _ in range(draws):
        indices = rng.integers(0, n, size=n)
        left, right = indices[:half], indices[half:]
        left_t, right_t = torch.as_tensor(left), torch.as_tensor(right)
        estimates.append(float(gram[left_t[:, None], right_t[None, :]].mean()))
    return [float(np.quantile(estimates, 0.025)), float(np.quantile(estimates, 0.975))]


def anatomy(vectors):
    matrix = torch.stack(vectors)
    norms = matrix.norm(dim=1)
    mean = matrix.mean(dim=0)
    normalized = matrix / norms.clamp_min(1e-12).unsqueeze(1)
    gram = normalized @ normalized.T
    offdiag = gram[~torch.eye(len(matrix), dtype=torch.bool)]
    singular = torch.linalg.svdvals(matrix)
    probs = singular.square() / singular.square().sum().clamp_min(1e-12)
    effective_rank = torch.exp(-(probs * probs.clamp_min(1e-12).log()).sum())
    return {
        "mean_individual_norm": norms.mean().item(), "norm_of_mean": mean.norm().item(),
        "coherence_ratio": (mean.norm() / norms.mean().clamp_min(1e-12)).item(),
        "mean_pairwise_cosine": offdiag.mean().item(), "effective_rank": effective_rank.item(),
    }


def main():
    set_seed(CFG["seed"]); OUT.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(CFG["model"], revision=CFG["model_revision"], local_files_only=True)
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        CFG["model"], revision=CFG["model_revision"], local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="sdpa"
    ).to(DEVICE)
    model.eval()
    for p in model.parameters(): p.requires_grad_(False)
    last = model.model.layers[-1]
    full_params = list(last.parameters())
    attention_params = list(last.self_attn.parameters())
    for p in full_params: p.requires_grad_(True)

    data = build_data(); records = []
    with torch.inference_mode():
        for task, rows in data.items():
            for group_index, row in enumerate(rows[:CFG["train_prompts_per_task"]]):
                text = prompt(tokenizer, row["question"])
                encoded = tokenizer(text, return_tensors="pt", return_token_type_ids=False).to(DEVICE)
                generated = model.generate(
                    **encoded, do_sample=True, temperature=CFG["temperature"], top_p=CFG["top_p"],
                    num_return_sequences=CFG["rollouts_per_prompt"], max_new_tokens=CFG["max_new_tokens"],
                    pad_token_id=tokenizer.pad_token_id,
                )
                prompt_len = encoded.input_ids.shape[1]
                for rollout_index, output in enumerate(generated):
                    response_ids = output[prompt_len:].tolist()
                    if tokenizer.eos_token_id in response_ids:
                        response_ids = response_ids[:response_ids.index(tokenizer.eos_token_id) + 1]
                    response = tokenizer.decode(response_ids, skip_special_tokens=True)
                    score, parsed = reward(response, row["answer"])
                    records.append({"task": task, "group": group_index, "prompt_id": row["id"], "gold": row["answer"],
                                    "prompt_tokens": prompt_len, "response_tokens": len(response_ids), "reward": score,
                                    "parsed_answer": parsed, "response": response, "prompt_ids": encoded.input_ids[0].tolist(),
                                    "response_ids": response_ids, "rollout": rollout_index})
    for task in data:
        for group in range(CFG["train_prompts_per_task"]):
            selected = [x for x in records if x["task"] == task and x["group"] == group]
            scores = np.asarray([x["reward"] for x in selected])
            std = scores.std()
            advantages = (scores - scores.mean()) / (std + CFG["advantage_epsilon"])
            for row, advantage in zip(selected, advantages): row["advantage"] = float(advantage)

    summary = {"model": CFG["model"], "resolved_revision": model_info(CFG["model"]).sha, "config": CFG, "tasks": {}}
    for task in data:
        items = [x for x in records if x["task"] == task]
        # Independent prompt halves implement the parent's cross-product estimator.
        half1 = [x for x in items if x["group"] % 2 == 0]
        half2 = [x for x in items if x["group"] % 2 == 1]
        g1 = aggregate_grad(model, tokenizer, half1, full_params)
        g2 = aggregate_grad(model, tokenizer, half2, full_params)
        full_cross = torch.dot(g1, g2).item()
        group_sketches = [aggregate_grad(model, tokenizer, [x for x in items if x["group"] == group], full_params,
                                         sketch_stride=CFG["anatomy_sketch_stride"])
                          for group in range(CFG["train_prompts_per_task"])]
        sketch_cross = torch.dot(torch.stack(group_sketches[::2]).mean(0), torch.stack(group_sketches[1::2]).mean(0)).item()
        vectors = [rollout_loss(model, tokenizer, x, attention_params) for x in items]
        stats = anatomy(vectors) if len(vectors) >= 2 else None
        torch.save({"group_full_block_sketches": torch.stack(group_sketches), "rollout_attention_sketches": torch.stack(vectors)},
                   OUT / f"{task}_gradient_sketches.pt")
        summary["tasks"][task] = {
            "n_rollouts": len(items), "reward_mean": float(np.mean([x["reward"] for x in items])),
            "abs_advantage_mean": float(np.mean([abs(x["advantage"]) for x in items])),
            "prompt_tokens_mean": float(np.mean([x["prompt_tokens"] for x in items])),
            "response_tokens_mean": float(np.mean([x["response_tokens"] for x in items])),
            "full_last_block_squared_norm_cross_product": full_cross,
            "full_last_block_cross_product_nonnegative": bool(full_cross >= 0),
            "full_last_block_sketch_cross_product": sketch_cross,
            "full_last_block_sketch_cross_product_ci95": bootstrap_cross_product(group_sketches, CFG["bootstrap_samples"]),
            "attention_anatomy": stats,
        }
    with (OUT / "raw.jsonl").open("w") as f:
        for row in records:
            saved = {k: v for k, v in row.items() if k not in ["prompt_ids", "response_ids"]}
            f.write(json.dumps(saved) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
