"""Single-card DataEnvGym MATH student for E00's local adaptation.

The task, prompt and scorer come from pinned upstream DataEnvGym. The SFT
implementation uses current Transformers/PEFT because upstream's 2024
LLaMA-Factory/vLLM pins are incompatible with the installed 2026 stack.
This is a modified reproduction, never an official-score reproduction.
"""

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import torch
from dataenvgym.gym.tasks.math.MATH.scoring import score_candidate_answer
from dataenvgym.gym.tasks.math.MATH.task import FEW_SHOT_PROMPT, list_fewshot_samples
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)


MODEL = "google/gemma-2-2b-it"
REVISION = "299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8"
CUTOFF = 1024


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def train(args: argparse.Namespace) -> None:
    from torch.utils.data import Dataset

    start = time.monotonic()
    set_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    tokenizer.pad_token = tokenizer.eos_token
    records = rows(args.data)
    examples = []
    truncation_count = 0
    supervised_tokens = 0
    for record in records:
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": record["instruction"]}],
            tokenize=False,
            add_generation_prompt=True,
        )
        prompt_ids = tokenizer(prompt, add_special_tokens=False).input_ids
        answer_ids = tokenizer(
            record["response"] + tokenizer.eos_token, add_special_tokens=False
        ).input_ids
        if len(prompt_ids) + len(answer_ids) > CUTOFF:
            truncation_count += 1
        ids = (prompt_ids + answer_ids)[:CUTOFF]
        labels = ([-100] * len(prompt_ids) + answer_ids)[:CUTOFF]
        if not any(label != -100 for label in labels):
            raise ValueError(f"No supervised tokens for {record['record_id']}")
        supervised_tokens += sum(label != -100 for label in labels)
        examples.append({"input_ids": ids, "labels": labels, "attention_mask": [1] * len(ids)})

    class ListDataset(Dataset):
        def __len__(self):
            return len(examples)

        def __getitem__(self, index):
            return examples[index]

    def collate(batch):
        width = max(len(item["input_ids"]) for item in batch)
        return {
            "input_ids": torch.tensor(
                [item["input_ids"] + [tokenizer.pad_token_id] * (width - len(item["input_ids"])) for item in batch]
            ),
            "attention_mask": torch.tensor(
                [item["attention_mask"] + [0] * (width - len(item["attention_mask"])) for item in batch]
            ),
            "labels": torch.tensor(
                [item["labels"] + [-100] * (width - len(item["labels"])) for item in batch]
            ),
        }

    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, torch_dtype=torch.float16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model = get_peft_model(
        model,
        LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.05,
            target_modules="all-linear", bias="none", task_type="CAUSAL_LM",
        ),
    )
    # Required for PEFT LoRA with reentrant gradient checkpointing in the
    # installed Transformers/torch stack; without it the first loss has no grad.
    model.enable_input_require_grads()
    args.output.mkdir(parents=True, exist_ok=False)
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(args.output),
            overwrite_output_dir=False,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,
            learning_rate=1e-4,
            num_train_epochs=3,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            fp16=True,
            gradient_checkpointing=True,
            logging_steps=1,
            logging_strategy="steps",
            save_strategy="no",
            report_to="none",
            seed=args.seed,
            data_seed=args.seed,
            dataloader_num_workers=0,
        ),
        train_dataset=ListDataset(),
        data_collator=collate,
    )
    outcome = trainer.train()
    adapter = args.output / "adapter"
    trainer.model.save_pretrained(adapter)
    tokenizer.save_pretrained(adapter)
    result = {
        "mode": "train", "source": MODEL, "revision": REVISION,
        "data": str(args.data.resolve()), "data_sha256": sha256(args.data),
        "seed": args.seed, "records": len(records), "truncated_records": truncation_count,
        "supervised_tokens_per_epoch": supervised_tokens,
        "optimizer_reset": True, "parent_checkpoint": REVISION,
        "train_metrics": outcome.metrics,
        "wall_seconds": time.monotonic() - start,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "adapter": str(adapter.resolve()),
    }
    (args.output / "run.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def evaluate(args: argparse.Namespace) -> None:
    # The installed vLLM 0.11 engine must spawn after our CUDA-capable imports.
    os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    start = time.monotonic()
    items = rows(args.data)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    fewshot = list_fewshot_samples()
    format_instruction = (
        "End with `Final Answer: The final answer is $\\boxed{ANSWER}$. "
        "I hope it is correct.` using your actual answer in place of ANSWER.\n\n"
        if args.format_instruction else ""
    )
    prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": format_instruction + (
                item["problem"] if args.zero_shot else FEW_SHOT_PROMPT.render(
                    problem=item["problem"], few_shot_examples=fewshot
                )
            )}], tokenize=False, add_generation_prompt=not args.omit_generation_prompt
        )
        for item in items
    ]
    llm = LLM(
        model=MODEL, revision=REVISION, enable_lora=True,
        max_lora_rank=16, max_model_len=4096,
        gpu_memory_utilization=0.65, tensor_parallel_size=1,
        enforce_eager=args.enforce_eager,
    )
    adapter = LoRARequest("e00", 1, str(args.adapter.resolve())) if args.adapter else None
    generations = llm.generate(
        prompts, SamplingParams(temperature=0, max_tokens=350),
        lora_request=adapter,
    )
    scored = []
    for item, generation in zip(items, generations, strict=True):
        prediction = generation.outputs[0].text
        scored.append({
            "record_id": item["record_id"], "problem_hash": item["problem_hash"],
            "level": item["level"], "type": item["type"],
            "prediction": prediction,
            "correct": score_candidate_answer(item["answer"], prediction),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as output:
        for item in scored:
            output.write(json.dumps(item, ensure_ascii=False) + "\n")
    result = {
        "mode": "evaluate", "source": MODEL, "revision": REVISION,
        "data": str(args.data.resolve()), "data_sha256": sha256(args.data),
        "adapter": str(args.adapter.resolve()) if args.adapter else None,
        "format_instruction": bool(args.format_instruction),
        "zero_shot": bool(args.zero_shot),
        "generation_prompt": not args.omit_generation_prompt,
        "enforce_eager": bool(args.enforce_eager),
        "count": len(scored), "correct": sum(item["correct"] for item in scored),
        "accuracy": sum(item["correct"] for item in scored) / len(scored),
        "wall_seconds": time.monotonic() - start,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "vllm_v1_multiprocessing": os.environ.get("VLLM_ENABLE_V1_MULTIPROCESSING"),
        "vllm_worker_multiproc_method": os.environ.get("VLLM_WORKER_MULTIPROC_METHOD"),
    }
    args.output.with_suffix(".summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    train_parser = sub.add_parser("train")
    train_parser.add_argument("--data", type=Path, required=True)
    train_parser.add_argument("--output", type=Path, required=True)
    train_parser.add_argument("--seed", type=int, default=17)
    eval_parser = sub.add_parser("evaluate")
    eval_parser.add_argument("--data", type=Path, required=True)
    eval_parser.add_argument("--output", type=Path, required=True)
    eval_parser.add_argument("--adapter", type=Path)
    eval_parser.add_argument("--format-instruction", action="store_true")
    eval_parser.add_argument("--zero-shot", action="store_true")
    eval_parser.add_argument("--omit-generation-prompt", action="store_true")
    eval_parser.add_argument("--enforce-eager", action="store_true")
    args = parser.parse_args()
    {"train": train, "evaluate": evaluate}[args.mode](args)


if __name__ == "__main__":
    main()
