"""E09 Qwen3 thinking-teacher quality gate on pinned DataEnvGym math prompts.

The released error-example field bug is fixed. All raw calls and invalid
outputs are retained. This is a new substrate qualification, not paper repro.
"""

import argparse
import ast
import hashlib
import json
import os
import random
import time
from pathlib import Path
from types import SimpleNamespace

import jinja2
from dataenvgym.gym.domain_models import MathDataSpec
from transformers import AutoTokenizer


MODEL = "Qwen/Qwen3-32B"
REVISION = "9216db5781bf21249d130ec9da846c4624c16137"
SEED = 20261002


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def problem_hash(problem: str) -> str:
    return hashlib.sha256(" ".join(problem.split()).encode()).hexdigest()


def final_json(raw: str) -> str:
    """Accept only a bare JSON array or one complete JSON code fence."""
    if "<think>" in raw and "</think>" not in raw:
        raise ValueError("Thinking block did not close")
    content = raw.rsplit("</think>", 1)[-1].strip()
    if content.startswith("```json\n") and content.endswith("\n```"):
        content = content[len("```json\n"):-len("\n```")].strip()
    if not (content.startswith("[") and content.endswith("]")):
        raise ValueError("Final response is not a JSON array")
    return content


def official_template(source: Path) -> jinja2.Template:
    tree = ast.parse(source.read_text())
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "DEFAULT_TEMPLATE" for target in statement.targets):
            continue
        call = statement.value
        if not isinstance(call, ast.Call) or not call.args:
            raise ValueError("Unexpected upstream DEFAULT_TEMPLATE expression")
        return jinja2.Template(ast.literal_eval(call.args[0]))
    raise ValueError("No DEFAULT_TEMPLATE in pinned source")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--feedback", type=Path, required=True)
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--test-hashes", type=Path, required=True)
    parser.add_argument("--template-source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--max-tokens", type=int, default=3072)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.start < 0 or args.count < 1 or args.start + args.count > 120:
        raise ValueError("Pilot supports prompt indices 0..119")
    start = time.monotonic()
    args.out.mkdir(parents=True, exist_ok=True)
    pool = read_jsonl(args.pool)
    smoke = read_jsonl(args.smoke)
    feedback = {row["record_id"]: row for row in read_jsonl(args.feedback)}
    errors = [row for row in smoke if not feedback[row["record_id"]]["correct"]]
    if len(feedback) != 352 or not errors:
        raise ValueError("Frozen base zero-shot feedback is incomplete")
    dev_hashes = {row["problem_hash"] for row in read_jsonl(args.dev)}
    test_hashes = set(args.test_hashes.read_text().splitlines())
    template = official_template(args.template_source)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    requests = []
    for index in range(args.start, args.start + args.count):
        rng = random.Random(SEED + index)
        sampled = rng.sample(pool, 6)
        selected_errors = rng.sample(errors, 3)
        for arm in ("no_state", "with_state"):
            examples = sampled[:3] + (
                sampled[3:] if arm == "no_state" else selected_errors
            )
            rng_order = random.Random(SEED + index * 2 + (arm == "with_state"))
            rng_order.shuffle(examples)
            raw_prompt = template.render(
                task_instances=[SimpleNamespace(instruction=row["problem"]) for row in examples],
                num_data_specs=1,
            )
            raw_prompt += (
                "\nCreate one genuinely new, self-contained problem. Do not copy or "
                "paraphrase any example above. The problem must state what to find "
                "and must be solvable without a missing diagram, figure, or table. "
                "Check the reasoning and final answer for mathematical correctness.\n"
            )
            prompt = tokenizer.apply_chat_template(
                [{"role": "user", "content": raw_prompt}],
                tokenize=False, add_generation_prompt=True, enable_thinking=True,
            )
            requests.append({
                "arm": arm, "index": index, "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "common_ids": [row["record_id"] for row in sampled[:3]],
                "extra_ids": [row["record_id"] for row in (
                    sampled[3:] if arm == "no_state" else selected_errors
                )],
                "input_problem_hashes": [problem_hash(row["problem"]) for row in examples],
            })
    prompt_path = args.out / f"prompts_{args.start}_{args.count}.jsonl"
    with prompt_path.open("w") as handle:
        for request in requests:
            handle.write(json.dumps(request, ensure_ascii=False) + "\n")
    if args.prepare_only:
        print(json.dumps({"prompt_count": len(requests), "prompt_sha256": sha256(prompt_path)}))
        return

    # Import after prompt prep so an invalid split fails before reserving a GPU.
    os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")
    from vllm import LLM, SamplingParams
    llm = LLM(
        model=MODEL, revision=REVISION, max_model_len=8192,
        gpu_memory_utilization=0.95, max_num_seqs=2,
        enable_prefix_caching=True, enforce_eager=True,
    )
    results = llm.generate(
        [request["prompt"] for request in requests],
        SamplingParams(
            temperature=0.6, top_p=0.95, top_k=20,
            max_tokens=args.max_tokens, seed=SEED, skip_special_tokens=False,
        ),
    )
    records = []
    seen_by_arm = {"no_state": set(), "with_state": set()}
    for request, generation in zip(requests, results, strict=True):
        output = generation.outputs[0]
        record = {key: value for key, value in request.items() if key != "prompt"}
        record.update({
            "raw": output.text,
            "finish_reason": output.finish_reason,
            "prompt_tokens": len(generation.prompt_token_ids),
            "generated_tokens": len(output.token_ids),
        })
        try:
            parsed = json.loads(final_json(output.text))
            if not isinstance(parsed, list) or len(parsed) != 1:
                raise ValueError("Expected one-element JSON array")
            spec = MathDataSpec.model_validate(parsed[0])
            if not all((spec.problem.strip(), spec.chain_of_thought.strip(), spec.final_answer.strip())):
                raise ValueError("Empty MathDataSpec field")
            digest = problem_hash(spec.problem)
            if digest in request["input_problem_hashes"]:
                raise ValueError("Exact input example copy")
            if digest in dev_hashes or digest in test_hashes:
                raise ValueError("Exact dev/test problem overlap")
            if digest in seen_by_arm[request["arm"]]:
                raise ValueError("Duplicate problem within arm")
            seen_by_arm[request["arm"]].add(digest)
            record["spec"] = spec.model_dump()
            record["problem_hash"] = digest
            record["valid"] = True
        except Exception as exc:
            record["valid"] = False
            record["invalid_reason"] = str(exc)
        records.append(record)
    raw_path = args.out / f"generation_{args.start}_{args.count}.jsonl"
    with raw_path.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    manifest = {
        "teacher": MODEL, "revision": REVISION,
        "thinking_mode": True, "temperature": 0.6, "top_p": 0.95,
        "top_k": 20, "max_tokens": args.max_tokens,
        "start": args.start, "count_per_arm": args.count,
        "source_template_sha256": sha256(args.template_source),
        "pool_sha256": sha256(args.pool), "feedback_sha256": sha256(args.feedback),
        "dev_sha256": sha256(args.dev), "test_hashes_sha256": sha256(args.test_hashes),
        "prompt_sha256": sha256(prompt_path), "raw_sha256": sha256(raw_path),
        "prompt_count": len(requests),
        "valid_per_arm": {
            arm: sum(row["valid"] for row in records if row["arm"] == arm)
            for arm in ("no_state", "with_state")
        },
        "invalid_reasons": [
            {"arm": row["arm"], "index": row["index"], "reason": row["invalid_reason"]}
            for row in records if not row["valid"]
        ],
        "prompt_tokens": sum(row["prompt_tokens"] for row in records),
        "generated_tokens": sum(row["generated_tokens"] for row in records),
        "wall_seconds": time.monotonic() - start,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
