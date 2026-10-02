#!/usr/bin/env python3
"""Hu restricted next-token readout and Wavelength original sequence readout."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from scipy.special import softmax
from scipy.stats import pearsonr, wasserstein_distance
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer


def next_logits(model, inp):
    if hasattr(model, "model"):
        hidden = model.model(**inp, use_cache=False).last_hidden_state[:, -1]
        return model.lm_head(hidden).float()
    if model.config.is_encoder_decoder:
        decoder = torch.full((inp.input_ids.shape[0], 1), model.config.decoder_start_token_id,
                             device=model.device, dtype=torch.long)
        return model(**inp, decoder_input_ids=decoder, use_cache=False).logits[:, -1].float()
    return model(**inp, use_cache=False).logits[:, -1].float()


def target_logprobs(model, tok, prompt, targets, batch_size):
    original = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                      tokenize=False, add_generation_prompt=True, enable_thinking=False)
    prompt_ids = tok.encode(original, add_special_tokens=False)
    full = [tok.apply_chat_template([{"role": "user", "content": prompt},
            {"role": "assistant", "content": target}], tokenize=False, add_generation_prompt=False, enable_thinking=False)
            for target in targets]
    token_ids = [tok.encode(text, add_special_tokens=False) for text in full]
    for ids in token_ids:
        if ids[:len(prompt_ids)] != prompt_ids:
            raise ValueError("Parent prefix check failed; do not silently change template")
        assert len(ids) > len(prompt_ids)
    values = []
    # Right padding makes completion positions independent of other sequence lengths.
    tok.padding_side = "right"
    for i in range(0, len(full), batch_size):
        ids_batch = token_ids[i:i+batch_size]
        inp = tok.pad({"input_ids": ids_batch}, padding=True, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            hidden = model.model(**inp, use_cache=False).last_hidden_state
            for j, ids in enumerate(ids_batch):
                first, last = len(prompt_ids), len(ids)
                logits = model.lm_head(hidden[j, first-1:last-1]).float()
                labels = torch.tensor(ids[first:last], device=model.device)
                lp = logits.log_softmax(-1).gather(1, labels[:, None]).sum().item()
                values.append(lp)
    tok.padding_side = "left"
    return values, hashlib.sha256(original.encode()).hexdigest()


def get_instruction(root):
    tree = ast.parse((root / "upstream/wavelength-eval/listeners.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "INSTRUCTION" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("Parent INSTRUCTION missing")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["hu", "wavelength"], required=True)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--revision", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dtype", choices=["bfloat16", "float16", "float32"], default="bfloat16")
    ap.add_argument("--slow-tokenizer", action="store_true", help="Match Hu's T5Tokenizer")
    ap.add_argument("--no-special-tokens", action="store_true", help="E12: identical raw lexical input across training stages")
    ap.add_argument("--numerical-gate", action="store_true", help="E12: first/last Hu batch1/8 probability control before full inference")
    ap.add_argument("--hu-readout", choices=["bare", "chat", "format"], default="bare",
                    help="E16: preserve original question while controlling elicitation")
    ap.add_argument('--common-template', type=Path, required=True)
    args = ap.parse_args()
    assert args.task == 'hu', 'E22 stage wrapper supports Hu only'
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    start = time.monotonic()
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    config = AutoConfig.from_pretrained(args.model, local_files_only=True)
    cls = AutoModelForSeq2SeqLM if config.is_encoder_decoder else AutoModelForCausalLM
    model = cls.from_pretrained(args.model, local_files_only=True, torch_dtype=getattr(torch, args.dtype),
                               device_map={"": 0}, weights_only=True).eval()
    tok = AutoTokenizer.from_pretrained(args.common_template, local_files_only=True, padding_side="left", use_fast=not args.slow_tokenizer)
    template_tok = AutoTokenizer.from_pretrained(args.common_template, local_files_only=True)
    assert template_tok.chat_template
    tok.chat_template = template_tok.chat_template
    chat_template_source = str(args.common_template)
    if args.task == 'hu' and args.hu_readout == 'chat' and args.model.name.startswith('OLMoE-1B-7B-0125'):
        # The base checkpoint has no native chat interface. E16 uses the same
        # published SFT template for all stages as a controlled input condition.
        template_model = args.root/'models/OLMoE-1B-7B-0125-SFT'
        template_tok = AutoTokenizer.from_pretrained(template_model, local_files_only=True)
        assert template_tok.chat_template, 'Official SFT template unavailable'
        tok.chat_template = template_tok.chat_template
        chat_template_source = str(template_model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    data = args.root / "data" / f"{args.task}.jsonl"
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    if args.limit:
        rows = rows[:args.limit]
    def hu_prompt(row):
        if args.hu_readout == "bare":
            return row['prompt']
        directive = "Reply with only the number of the selected answer.\n\n"
        if args.hu_readout == "format":
            return directive + row['prompt']
        assert not config.is_encoder_decoder, "Chat control is only for causal chat checkpoints"
        return tok.apply_chat_template([{"role": "user", "content": directive + row['prompt']}],
                                       tokenize=False, add_generation_prompt=True, enable_thinking=False)
    metadata = {"task": args.task, "model": args.model_id, "revision": args.revision, "dtype": args.dtype,
                "tokenizer_class": type(tok).__name__,
                "tf32": False,
                "enable_thinking": False if args.task == "wavelength" else None,
                "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest(), "n": len(rows),
                "batch_size": args.batch_size, "gpu": torch.cuda.get_device_name(),
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "packages": {p: importlib.metadata.version(p) for p in ["torch", "transformers"]},
                "readout": "raw restricted next-token" if args.task == "hu" else "parent full assistant sequence cumulative logprob incl end token"}
    metadata['add_special_tokens'] = not args.no_special_tokens
    metadata['hu_readout'] = args.hu_readout if args.task == 'hu' else None
    metadata['chat_template_source'] = chat_template_source
    metadata['unpadded_input_token_ids_sha256'] = hashlib.sha256(json.dumps(
        [tok.encode(hu_prompt(r), add_special_tokens=not args.no_special_tokens) for r in rows]).encode()).hexdigest() if args.task == 'hu' else None
    metadata['generation_defaults_not_applied'] = model.generation_config.to_dict()
    if args.numerical_gate:
        assert args.task == 'hu'
        selected = rows[:7] + rows[-1:]
        inp = tok([hu_prompt(r) for r in selected], padding=True, return_tensors='pt',
                  add_special_tokens=not args.no_special_tokens).to(model.device)
        with torch.inference_mode(): many = next_logits(model, inp)
        controls = []
        for i in [0, 7]:
            r = selected[i]
            ids = [tok.encode(c, add_special_tokens=False)[0] for c in r['choices']]
            inp = tok(hu_prompt(r), return_tensors='pt', add_special_tokens=not args.no_special_tokens).to(model.device)
            with torch.inference_mode(): one = next_logits(model, inp)[0, ids].softmax(-1)
            batch = many[i, ids].softmax(-1)
            controls.append({'item_id': r['item_id'], 'phenomenon': r['phenomenon'],
                'max_prob_delta': (one-batch).abs().max().item(), 'argmax_same': one.argmax().item()==batch.argmax().item()})
        metadata['numerical_controls'] = controls
        metadata['numerical_gate_pass'] = all(r['max_prob_delta'] < 1e-3 for r in controls)
        (args.output/'config.json').write_text(json.dumps(metadata, indent=2)+'\n')
        if not metadata['numerical_gate_pass']:
            raise ValueError('Numerical gate failed; no full inference or scientific interpretation')
    (args.output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    outputs = []
    with (args.output / "predictions.jsonl").open("w") as f:
        if args.task == "hu":
            for i in range(0, len(rows), args.batch_size):
                batch = rows[i:i+args.batch_size]
                inp = tok([hu_prompt(r) for r in batch], return_tensors="pt", padding=True,
                          add_special_tokens=not args.no_special_tokens).to(model.device)
                with torch.inference_mode():
                    logits = next_logits(model, inp)
                for r, ls in zip(batch, logits):
                    ids = [tok.encode(x, add_special_tokens=False) for x in r["choices"]]
                    assert all(len(t) == 1 for t in ids), "Parent single-token choice assumption failed"
                    restricted = ls[[t[0] for t in ids]].log_softmax(0).tolist()
                    probs = dict(zip(r["choices"], np.exp(restricted).tolist()))
                    pred = max(probs, key=probs.get)
                    rec = {**r, "model": args.model_id, "revision": args.revision, "prediction": pred,
                           "readout_prompt_sha256": hashlib.sha256(hu_prompt(r).encode()).hexdigest(),
                           "choice_logprobs": dict(zip(r["choices"], restricted)), "choice_probs": probs,
                           "correct": pred == r["gold"], "prob_true_answer": probs[r["gold"]],
                           "selected_label": r["option_labels"][int(pred)-1]}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    outputs.append(rec)
                f.flush()
                if i % (args.batch_size*10) == 0:
                    print(json.dumps({"done": len(outputs), "total": len(rows)}), flush=True)
        else:
            instruction = get_instruction(args.root)
            sys.path.insert(0, str(args.root / "upstream/wavelength-eval"))
            from game import WavelengthGame
            parent_game = WavelengthGame(None, None)
            choices = list(range(0, 101, 5))
            for i, r in enumerate(rows):
                source = r["source"]
                prompt = instruction.format(left=source["left"], right=source["right"], clue=source["clue"],
                                            scale=5, possible_values=", ".join(map(str, choices)))
                lps, ph = target_logprobs(model, tok, prompt,
                    [f"<answer>{x}</answer>" for x in choices], args.batch_size)
                probs = softmax(lps)
                distribution = {str(x): float(p) for x, p in zip(choices, probs)}
                metrics = parent_game.compute_listener_metrics(distribution, float(source["target"]))
                mean = float(np.dot(choices, probs))
                assert abs(metrics["expected_answer"] - mean) < 1e-8
                rec = {**r, "model": args.model_id, "revision": args.revision, "prompt_sha256": ph,
                    "choice_logprobs": dict(zip(map(str, choices), lps)), "distribution": distribution,
                    "mean_prediction": mean, "paper_absolute_error": abs(mean-float(source["target"])),
                    "parent_code_argmax_error": metrics["diff"],
                    "human_mean": float(np.mean(r["human_distribution"])),
                    "wasserstein": float(wasserstein_distance(choices, r["human_distribution"], u_weights=probs))}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                outputs.append(rec)
                if i % 10 == 0:
                    print(json.dumps({"done": len(outputs), "total": len(rows)}), flush=True)
    if args.task == "hu":
        groups = {}
        for r in outputs:
            groups.setdefault(r["phenomenon"], []).append(r)
        summary = {k: {"n": len(rs), "accuracy": np.mean([r["correct"] for r in rs]).item(),
                       "mean_prob_gold": np.mean([r["prob_true_answer"] for r in rs]).item()} for k, rs in groups.items()}
    else:
        summary = {"n": len(outputs), "paper_mae": np.mean([r["paper_absolute_error"] for r in outputs]).item(),
            "parent_code_argmax_mae": np.mean([r["parent_code_argmax_error"] for r in outputs]).item(),
            "wasserstein": np.mean([r["wasserstein"] for r in outputs]).item(),
            "human_mae": np.mean([abs(r["human_mean"]-float(r["source"]["target"])) for r in outputs]).item(),
            "pearson_human_mean": pearsonr([r["mean_prediction"] for r in outputs], [r["human_mean"] for r in outputs]).statistic.item() if len(outputs)>2 else None}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    metadata.update({"wall_seconds": time.monotonic()-start, "peak_gpu_memory_bytes": torch.cuda.max_memory_allocated(), "complete": True})
    (args.output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"complete": True, "output": str(args.output), "seconds": metadata["wall_seconds"]}))


if __name__ == "__main__":
    main()
