"""Greedy IFEval evaluation of one L30 E01 checkpoint.

IFEval is the pre-registered primary evaluation because every constraint is
verified programmatically -- the load-bearing measurement needs no LLM judge.
Scoring uses the unmodified Google Research verifier vendored under
src/instruction_following_eval/ (strict and loose, prompt- and
instruction-level).

Every arm is evaluated with the SAME inference context,
    <bos><|user|>\\n{prompt}\\n<|assistant|>\\n
including D_rt, which never saw a user turn during training. That asymmetry is
intrinsic to Response Tuning (An et al. evaluate it the same way), not a choice
introduced here.

Per-prompt records are written out so that uncertainty can be computed with the
prompt as the cluster unit; multiple constraints attached to one prompt are
never treated as independent evidence.
"""
import argparse
import json
import pathlib
import sys
import time

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arms import eval_prompt  # noqa: E402
from train import apply_lora, load_backbone  # noqa: E402

from instruction_following_eval import evaluation_lib  # noqa: E402


def load_ifeval():
    from datasets import load_dataset

    ds = load_dataset("google/IFEval")["train"]
    inputs = []
    for ex in ds:
        kwargs = [{k: v for k, v in d.items() if v is not None} for d in ex["kwargs"]]
        inputs.append(
            evaluation_lib.InputExample(
                key=ex["key"],
                instruction_id_list=ex["instruction_id_list"],
                prompt=ex["prompt"],
                kwargs=kwargs,
            )
        )
    return inputs


@torch.no_grad()
def generate(model, tok, prompts, max_new_tokens=1024, batch_size=32):
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    outs = []
    for i in range(0, len(prompts), batch_size):
        chunk = prompts[i : i + batch_size]
        texts = [tok.bos_token + eval_prompt(p) for p in chunk]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        gen = model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            pad_token_id=tok.pad_token_id,
        )
        for j in range(len(chunk)):
            new = gen[j, enc["input_ids"].shape[1] :]
            outs.append(tok.decode(new, skip_special_tokens=True))
        print(f"  generated {min(i + batch_size, len(prompts))}/{len(prompts)}", flush=True)
    return outs


def score(inputs, responses):
    p2r = {inp.prompt: r for inp, r in zip(inputs, responses)}
    per_prompt = []
    for inp in inputs:
        strict = evaluation_lib.test_instruction_following_strict(inp, p2r)
        loose = evaluation_lib.test_instruction_following_loose(inp, p2r)
        per_prompt.append(
            {
                "key": inp.key,
                "instruction_ids": inp.instruction_id_list,
                "strict_follow_list": strict.follow_instruction_list,
                "loose_follow_list": loose.follow_instruction_list,
                "strict_prompt": bool(strict.follow_all_instructions),
                "loose_prompt": bool(loose.follow_all_instructions),
                "response": p2r[inp.prompt],
            }
        )
    n = len(per_prompt)
    n_instr = sum(len(r["instruction_ids"]) for r in per_prompt)
    summary = {
        "n_prompts": n,
        "n_instructions": n_instr,
        "strict_prompt_acc": sum(r["strict_prompt"] for r in per_prompt) / n,
        "loose_prompt_acc": sum(r["loose_prompt"] for r in per_prompt) / n,
        "strict_instruction_acc": sum(sum(r["strict_follow_list"]) for r in per_prompt) / n_instr,
        "loose_instruction_acc": sum(sum(r["loose_follow_list"]) for r in per_prompt) / n_instr,
        "empty_responses": sum(1 for r in per_prompt if not r["response"].strip()),
        "mean_response_chars": sum(len(r["response"]) for r in per_prompt) / n,
    }
    return per_prompt, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default=None, help="omit to evaluate the untuned base")
    ap.add_argument("--model", default="google/gemma-2-2b")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=1024)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--limit", type=int, default=None, help="debug: first N prompts")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    model, tok, _ = load_backbone(args.model)
    tag = {"model": args.model, "adapter": args.adapter}
    if args.adapter:
        ckpt = torch.load(args.adapter, map_location="cpu", weights_only=False)
        meta = ckpt["meta"]
        apply_lora(model, meta["lora"]["r"], meta["lora"]["alpha"], meta["lora"]["dropout"])
        missing = model.load_state_dict(ckpt["lora"], strict=False)
        assert not missing.unexpected_keys, missing.unexpected_keys
        loaded = [k for k in ckpt["lora"]]
        assert loaded, "adapter contained no LoRA tensors"
        model.to("cuda")
        tag.update({k: meta[k] for k in ("arm", "seed", "epoch", "step") if k in meta})
        tag["n_lora_tensors"] = len(loaded)
    model.eval()
    model.config.use_cache = True

    inputs = load_ifeval()
    if args.limit:
        inputs = inputs[: args.limit]
    t0 = time.time()
    responses = generate(model, tok, [i.prompt for i in inputs],
                         args.max_new_tokens, args.batch_size)
    per_prompt, summary = score(inputs, responses)
    summary["generation_seconds"] = round(time.time() - t0, 1)

    with (out / "per_prompt.jsonl").open("w") as f:
        for r in per_prompt:
            f.write(json.dumps(r) + "\n")
    (out / "summary.json").write_text(json.dumps({**tag, **summary}, indent=2) + "\n")
    print(json.dumps({**tag, **summary}, indent=2))


if __name__ == "__main__":
    main()
