"""E123: frozen OLMo backbone, one randomly initialized OLMoE FFN.

Run only after reading experiments/E123-frozen-moe-feasibility.md. No downloads.
  --mode baseline --model LOCAL_MODEL --data DATA_DIR --output OUTPUT_DIR
  --mode train --model LOCAL_MODEL --data DATA_DIR --output OUTPUT_DIR
  --mode train ... --resume OUTPUT_DIR/checkpoint.pt
  --mode self-test                 # tiny CPU models, no pretrained assets/GPU

DATA_DIR/manifest.json: {"train": [{"path": "train.npy", "source": "c4",
"file_id": "original-source-file", "dtype": "uint16", "sha256": "..."}],
"held": [...]}. Paths are relative to the manifest. Optional sampling_weight
controls training file probability; otherwise sampling is uniform over windows.
Arrays are flat token IDs or rows of exactly seq_len+1 tokens. .bin/.u16/.u32
and .npy are memory mapped; .npz uses train/held arrays (loaded into RAM).
Directories with train.npy/held.npy or train.bin/held.bin are also accepted.

Each window contains seq_len input tokens and their next-token targets. Train
windows are sampled with replacement using a separate, checkpointed order RNG.
Held/calibration windows are fixed, sampled without replacement; calibration
comes only from train. This first implementation runs the full backbone; its
frozen prefix naturally has no autograd graph, and its frozen suffix DOES pass
gradients back to the MoE. The objective is LM NLL, never teacher-output MSE.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
import transformers
from transformers import OlmoConfig, OlmoForCausalLM, OlmoeConfig
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock

WB = Path(__file__).resolve().parents[1]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def emit(kind, **values):
    print(json.dumps({"event": kind, **values}, ensure_ascii=False, allow_nan=False), flush=True)


def sampled_parameter_hash(model, excluded_prefix=None):
    """Fixed evenly spaced samples from EVERY included tensor, not a full hash."""
    digest = hashlib.sha256()
    for name, parameter in model.named_parameters():
        if excluded_prefix and name.startswith(excluded_prefix):
            continue
        digest.update(f"{name}|{tuple(parameter.shape)}|{parameter.dtype}".encode())
        flat = parameter.detach().reshape(-1)
        if flat.numel():
            # Float32 linspace can round (numel-1) UP to numel for large embeddings.
            count = min(33, flat.numel())
            indices = (torch.arange(count, device=flat.device, dtype=torch.long) * (flat.numel() - 1)
                       // max(1, count - 1))
            sample = flat[indices].contiguous().cpu().view(torch.uint8).numpy().tobytes()
            digest.update(sample)
    return digest.hexdigest()


class TokenData:
    def __init__(self, path, seq_len, dtype="uint16"):
        path = Path(path).resolve()
        if path.is_dir():
            manifest = path / "manifest.json"
            if manifest.exists():
                path = manifest
            else:
                spec = {}
                for split in ("train", "held"):
                    files = [path / f"{split}{suffix}" for suffix in (".npy", ".bin", ".u16", ".u32")]
                    files = [file for file in files if file.exists()]
                    if len(files) != 1:
                        raise ValueError(f"Need manifest.json or exactly one {split} token file in {path}")
                    spec[split] = [{"path": str(files[0]), "source": "unspecified", "file_id": split}]
        if path.suffix == ".json":
            spec = json.loads(path.read_text())
        elif path.suffix == ".npz":
            spec = {split: [{"path": str(path), "key": split, "source": "unspecified", "file_id": split}]
                    for split in ("train", "held")}
        elif not path.is_dir():
            raise ValueError("--data must be a manifest, directory, or .npz with train/held arrays")
        root = path if path.is_dir() else path.parent
        self.seq_len, self.files, self.provenance = seq_len, {}, {}
        for split in ("train", "held"):
            self.files[split] = []
            self.provenance[split] = []
            for index, entry in enumerate(spec[split]):
                entry = {"path": entry} if isinstance(entry, str) else dict(entry)
                file = (root / entry["path"]).resolve()
                entry_dtype = entry.get("dtype", "uint32" if file.suffix == ".u32" else dtype)
                key = entry.get("key")
                file_hash = sha256_file(file)
                if entry.get("sha256") and entry["sha256"] != file_hash:
                    raise ValueError(f"Data hash mismatch: {file}")
                if file.suffix == ".npy":
                    array = np.load(file, mmap_mode="r", allow_pickle=False)
                elif file.suffix == ".npz":
                    with np.load(file, allow_pickle=False) as archive:
                        array = archive[key or split].copy()
                else:
                    array = np.memmap(file, mode="r", dtype=np.dtype(entry_dtype))
                if array.dtype.kind not in "iu" or array.ndim not in (1, 2):
                    raise ValueError(f"Expected integer token vector/windows: {file}: {array.shape}/{array.dtype}")
                if array.ndim == 2 and array.shape[1] != seq_len + 1:
                    raise ValueError(f"Prepacked rows must have {seq_len + 1} tokens: {file}")
                windows = len(array) // (seq_len + 1) if array.ndim == 1 else len(array)
                if not windows:
                    raise ValueError(f"Too few tokens for a full window: {file}")
                record = {"path": str(file), "key": key, "sha256": file_hash,
                          "source": entry.get("source", "unspecified"),
                          "file_id": str(entry.get("file_id", f"{split}:{index}")),
                          "dtype": str(array.dtype), "token_count": int(array.size), "windows": windows,
                          "sampling_weight": entry.get("sampling_weight", windows)}
                if entry.get("token_count") is not None and int(entry["token_count"]) != array.size:
                    raise ValueError(f"token_count mismatch for {file}")
                self.provenance[split].append(record)
                self.files[split].append({**record, "array": array})
            if not self.files[split]:
                raise ValueError(f"Empty split: {split}")
        train_identities = {(r["sha256"], r["key"]) for r in self.provenance["train"]}
        held_identities = {(r["sha256"], r["key"]) for r in self.provenance["held"]}
        if train_identities & held_identities:
            raise ValueError("Train and held token contents overlap")
        # A source-file ID denotes the ORIGINAL corpus file, not the token shard.
        known_train = {(r["source"], r["file_id"]) for r in self.provenance["train"]}
        known_held = {(r["source"], r["file_id"]) for r in self.provenance["held"]}
        if known_train & known_held:
            raise ValueError("Train and held share original source file_id")
        weights = np.array([r["sampling_weight"] for r in self.files["train"]], dtype=float)
        if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
            raise ValueError("Invalid training sampling weights")
        self.train_probabilities = weights / weights.sum()
        self.sources_available = sorted({r["source"] for r in self.files["held"]})

    def window(self, split, file_index, window_index):
        record = self.files[split][file_index]
        array = record["array"]
        if array.ndim == 1:
            offset = int(window_index) * (self.seq_len + 1)
            row = array[offset:offset + self.seq_len + 1]
        else:
            row = array[int(window_index)]
        return np.asarray(row, dtype=np.int64)

    def train_batch(self, rng, size):
        chosen = rng.choice(len(self.files["train"]), size=size, p=self.train_probabilities)
        rows = [self.window("train", int(i), int(rng.integers(self.files["train"][i]["windows"])))
                for i in chosen]
        return torch.from_numpy(np.stack(rows))

    def fixed_windows(self, split, count, seed):
        sizes = np.array([r["windows"] for r in self.files[split]], dtype=np.int64)
        cumulative = np.cumsum(sizes)
        selected = np.random.default_rng(seed).choice(int(cumulative[-1]), min(count, int(cumulative[-1])), replace=False)
        result = []
        for global_index in sorted(selected):
            file_index = int(np.searchsorted(cumulative, global_index, side="right"))
            window_index = int(global_index - (cumulative[file_index - 1] if file_index else 0))
            result.append((file_index, window_index))
        return result

    def iter_fixed(self, split, windows, batch_size):
        for start in range(0, len(windows), batch_size):
            keys = windows[start:start + batch_size]
            rows = [self.window(split, f, w) for f, w in keys]
            metadata = [{"source": self.files[split][f]["source"], "file_id": self.files[split][f]["file_id"],
                         "window": w} for f, w in keys]
            yield torch.from_numpy(np.stack(rows)), metadata


class TensorMoE(nn.Module):
    """Adapt the HF (output, router_logits) contract to dense OLMo's tensor FFN."""
    def __init__(self, hidden, intermediate, experts, top_k, init_std):
        super().__init__()
        self.config = OlmoeConfig(hidden_size=hidden, intermediate_size=intermediate,
                                 num_experts=experts, num_experts_per_tok=top_k,
                                 norm_topk_prob=False, hidden_act="silu", initializer_range=init_std)
        self.block = OlmoeSparseMoeBlock(self.config)
        # Only initialize the NEW module. Never call parent.post_init().
        for module in self.block.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=init_std)
        self.last_router_logits = None

    def forward(self, hidden_states):
        output, self.last_router_logits = self.block(hidden_states)
        return output

    def losses_and_load(self):
        logits = self.last_router_logits.float()
        probabilities = logits.softmax(-1)
        selected = probabilities.topk(self.block.top_k, dim=-1).indices
        counts = torch.bincount(selected.reshape(-1), minlength=self.block.num_experts).float()
        # count/(N*k), hence uniform lb=1. No CUDA-device-index slicing.
        frequencies = counts / selected.numel()
        balance = self.block.num_experts * (frequencies * probabilities.mean(0)).sum()
        z_loss = logits.logsumexp(-1).square().mean()
        return balance, z_loss, frequencies.detach(), probabilities.detach()


def autocast(args):
    if args.device.startswith("cuda") and args.dtype != "float32":
        return torch.autocast("cuda", dtype=getattr(torch, args.dtype))
    return contextlib.nullcontext()


def forward_logits(model, ids, args, attention_mask=None):
    with autocast(args):
        return model(input_ids=ids, attention_mask=attention_mask, use_cache=False).logits


def token_nll(logits, targets):
    return F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), targets.reshape(-1),
                           reduction="none").view_as(targets)


def bootstrap(records, paired=None, cluster="sequence", iterations=1000):
    losses = np.array([r["nll_sum"] for r in records], dtype=np.float64)
    if paired is not None:
        keys = lambda rows: [(r["source"], r["file_id"], r["window"], r["tokens"]) for r in rows]
        if keys(records) != keys(paired):
            raise ValueError("Paired bootstrap requires identical fixed windows")
        losses -= np.array([r["nll_sum"] for r in paired])
    counts = np.array([r["tokens"] for r in records], dtype=np.float64)
    group_keys = [(r["source"], r["file_id"]) if cluster == "file" else i for i, r in enumerate(records)]
    groups = {}
    for key, value, count in zip(group_keys, losses, counts):
        group = groups.setdefault(key, [0.0, 0.0])
        group[0] += value
        group[1] += count
    values = np.array(list(groups.values()))
    rng = np.random.default_rng(51023)
    sampled = rng.integers(0, len(values), (iterations, len(values)))
    samples = values[sampled].sum(axis=1)
    intervals = np.quantile(samples[:, 0] / samples[:, 1], [0.025, 0.975]).tolist()
    return {"mean": float(losses.sum() / counts.sum()), "ci95": intervals,
            "cluster": cluster, "clusters": len(values), "iterations": iterations,
            "ci_degenerate": len(values) < 2}


def summarize(records, paired=None, iterations=1000, available_sources=None):
    if not records:
        return None
    result = {kind: bootstrap(records, paired, kind, iterations) for kind in ("file", "sequence")}
    result["sequences"] = len(records)
    result["tokens"] = sum(r["tokens"] for r in records)
    result["sources"] = {}
    result["sources_evaluated"] = sorted({r["source"] for r in records})
    result["sources_available"] = sorted(available_sources or result["sources_evaluated"])
    result["missing_sources"] = sorted(set(result["sources_available"]) - set(result["sources_evaluated"]))
    for source in sorted({r["source"] for r in records}):
        rows = [r for r in records if r["source"] == source]
        comparison = [r for r in paired if r["source"] == source] if paired is not None else None
        result["sources"][source] = bootstrap(rows, comparison, "file", iterations)
    return result


@torch.no_grad()
def evaluate(model, data, windows, args):
    records = []
    for batch, metadata in data.iter_fixed("held", windows, args.batch_size):
        batch = batch.to(args.device)
        logits = forward_logits(model, batch[:, :-1], args)
        losses = token_nll(logits, batch[:, 1:]).cpu()
        for values, meta in zip(losses, metadata):
            records.append({**meta, "nll_sum": float(values.double().sum()), "tokens": len(values)})
    return records


def read_pos(path):
    if not path:
        return []
    if not Path(path).is_file():
        raise FileNotFoundError(f"POS items missing: {path}; use --pos-items '' only to explicitly disable POS")
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return [row for row in rows if row["split"] in ("held", "test", "eval")]


@torch.no_grad()
def evaluate_pos(model, items, args, hook_context):
    records = []
    for start in range(0, len(items), args.batch_size):
        chunk = items[start:start + args.batch_size]
        width = max(len(row["ids"]) for row in chunk)
        ids = torch.full((len(chunk), width), model.config.pad_token_id or 1, dtype=torch.long, device=args.device)
        mask = torch.zeros_like(ids)
        last = torch.tensor([len(row["ids"]) - 1 for row in chunk], device=args.device)
        for i, row in enumerate(chunk):
            ids[i, :len(row["ids"])] = torch.tensor(row["ids"], device=args.device)
            mask[i, :len(row["ids"])] = 1
        # Hook affects the target token's LAST INPUT position. next_id is NEVER fed.
        hook_context["target"] = (torch.arange(len(chunk), device=args.device), last)
        logits = forward_logits(model, ids, args, attention_mask=mask)
        lp = F.log_softmax(logits[torch.arange(len(chunk), device=args.device), last].float(), -1)
        target = torch.tensor([row["next_id"] for row in chunk], device=args.device)
        target_lp = lp.gather(1, target[:, None])[:, 0].cpu().numpy().astype(np.float32)
        for item, value in zip(chunk, target_lp):
            records.append({"word": item.get("word", item.get("form", "unknown")),
                            "condition": item.get("pos", item.get("label", "unknown")),
                            "target_log_prob_fp32": float(value), "nll": -float(value)})
    hook_context["target"] = None
    return records


def pos_summary(records, paired=None):
    if not records:
        return None
    grouped = {}
    for index, record in enumerate(records):
        value = record["nll"] - (paired[index]["nll"] if paired is not None else 0.0)
        grouped.setdefault(record["word"], []).append(value)
    means = np.array([np.mean(values) for values in grouped.values()])
    rng = np.random.default_rng(51025)
    samples = means[rng.integers(0, len(means), (1000, len(means)))].mean(1)
    conditions = {}
    for condition in sorted({r["condition"] for r in records}):
        sub = [r for r in records if r["condition"] == condition]
        by_word = {}
        for i, row in enumerate(records):
            if row["condition"] == condition:
                by_word.setdefault(row["word"], []).append(row["nll"] - (paired[i]["nll"] if paired else 0))
        conditions[condition] = {"word_balanced_mean": float(np.mean([np.mean(x) for x in by_word.values()])),
                                 "items": len(sub), "words": len(by_word)}
    result = {"word_balanced_mean": float(means.mean()), "word_bootstrap_ci95": np.quantile(samples, [.025, .975]).tolist(),
              "words": len(means), "items": len(records), "conditions": conditions}
    if paired is not None:
        word_conditions = {}
        for row, reference in zip(records, paired):
            if row["word"] != reference["word"] or row["condition"] != reference["condition"]:
                raise ValueError("Paired POS records differ in order or labels")
            word_conditions.setdefault(row["word"], {}).setdefault(row["condition"], []).append(row["nll"] - reference["nll"])
        contrasts = {word: float(np.mean(values["NOUN"]) - np.mean(values["VERB"]))
                     for word, values in word_conditions.items() if "NOUN" in values and "VERB" in values}
        contrast_values = np.array(list(contrasts.values()))
        contrast_summary = {"definition": "mean_word(mean_delta_NLL_NOUN - mean_delta_NLL_VERB)",
                            "eligible_words": len(contrasts), "word_effects": contrasts}
        if len(contrast_values):
            sampled = contrast_values[rng.integers(0, len(contrast_values), (1000, len(contrast_values)))].mean(1)
            contrast_summary.update({"mean": float(contrast_values.mean()),
                                     "word_bootstrap_ci95": np.quantile(sampled, [.025, .975]).tolist()})
        else:
            contrast_summary.update({"mean": None, "word_bootstrap_ci95": None})
        result["paired_within_word_noun_minus_verb"] = contrast_summary
    return result


@torch.no_grad()
def calibrate_mean(model, dense, data, windows, args):
    total = torch.zeros(model.config.hidden_size, device=args.device, dtype=torch.float64)
    count = 0
    def collect(module, inputs, output):
        nonlocal count
        total.add_(output.detach().double().sum((0, 1)))
        count += output.shape[0] * output.shape[1]
    handle = dense.register_forward_hook(collect)
    try:
        for batch, _ in data.iter_fixed("train", windows, args.batch_size):
            forward_logits(model, batch[:, :-1].to(args.device), args)
    finally:
        handle.remove()
    return (total / count).float(), count


def intervention_hook(mode, mean, context):
    def hook(module, inputs, output):
        if mode == "identity":
            return output + torch.zeros_like(output)
        replacement = torch.zeros_like(output) if mode == "zero" else mean.to(output).expand_as(output)
        if context.get("target") is None:
            return replacement
        batch, position = context["target"]
        changed = output.clone()
        changed[batch, position] = replacement[batch, position]
        return changed
    return hook


def run_baseline(model, data, held_windows, cal_windows, items, args, dense, original_hash):
    context = {"target": None}
    mean, count = calibrate_mean(model, dense, data, cal_windows, args)
    np.save(Path(args.output) / "dense_calibration_mean.npy", mean.cpu().numpy())
    result = {"calibration_tokens": count, "held": {}, "pos": {}, "paired_delta": {}, "pos_paired_delta": {},
              "intervention_scope": {"held": "all input positions", "pos": "target word last input position only"}}
    # Explicit manipulation check uses identical shapes and the SAME input batch.
    probe, _ = next(data.iter_fixed("held", held_windows, args.batch_size))
    with torch.no_grad():
        probe = probe[:, :-1].to(args.device)
        probe_original = forward_logits(model, probe, args).float()
        handle = dense.register_forward_hook(intervention_hook("zero", mean, context))
        try:
            probe_zero = forward_logits(model, probe, args).float()
        finally:
            handle.remove()
        zero_logit_change = float((probe_zero - probe_original).abs().max())
    if zero_logit_change == 0:
        raise RuntimeError("Real FFN zero hook failed to change logits")
    reference, pos_reference = None, None
    for mode in ("original", "repeat", "identity", "zero", "mean", "reinsert_same"):
        if mode == "reinsert_same":
            model.model.layers[args.layer].mlp = dense
        handle = dense.register_forward_hook(intervention_hook(mode, mean, context)) if mode in ("identity", "zero", "mean") else None
        try:
            rows = evaluate(model, data, held_windows, args)
            pos_rows = evaluate_pos(model, items, args, context)
        finally:
            if handle is not None:
                handle.remove()
        if mode == "original":
            reference, pos_reference = rows, pos_rows
        result["held"][mode] = summarize(rows, iterations=args.bootstrap, available_sources=data.sources_available)
        result["pos"][mode] = pos_summary(pos_rows)
        result["paired_delta"][mode] = summarize(rows, reference, args.bootstrap, data.sources_available)
        result["pos_paired_delta"][mode] = pos_summary(pos_rows, pos_reference)
        write_json(Path(args.output) / f"baseline_{mode}_sequences.json", rows)
        write_json(Path(args.output) / f"baseline_{mode}_pos.json", pos_rows)
        emit("baseline", mode=mode, held=result["held"][mode]["sequence"],
             delta=result["paired_delta"][mode]["sequence"])
    result["frozen_sample_hash_before"] = original_hash
    result["frozen_sample_hash_after"] = sampled_parameter_hash(model)
    if original_hash != result["frozen_sample_hash_after"]:
        raise RuntimeError("Dense parameters changed during baseline")
    identity_error = abs(result["paired_delta"]["identity"]["sequence"]["mean"])
    reinsertion_error = abs(result["paired_delta"]["reinsert_same"]["sequence"]["mean"])
    if max(identity_error, reinsertion_error) > 1e-7:
        raise RuntimeError("Identity/reinsertion changed NLL on identical batches")
    result["checks"] = {"identity_nll_error": identity_error, "reinsertion_nll_error": reinsertion_error,
                        "zero_changed_nll": abs(result["paired_delta"]["zero"]["sequence"]["mean"]) > 1e-9,
                        "zero_max_logit_change": zero_logit_change}
    write_json(Path(args.output) / "baseline_summary.json", result)
    return result


def lr_at(step, args):
    warmup = max(1, int(args.steps * args.warmup_fraction))
    if step < warmup:
        return args.lr * (step + 1) / warmup
    phase = min(1.0, (step - warmup) / max(1, args.steps - warmup - 1))
    return args.lr * 0.5 * (1 + math.cos(math.pi * phase))


def rng_state(args):
    state = {"torch": torch.get_rng_state(), "numpy": np.random.get_state(), "python": random.getstate()}
    if args.device.startswith("cuda"):
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state


def restore_rng(state, args):
    torch.set_rng_state(state["torch"].cpu())
    np.random.set_state(state["numpy"])
    random.setstate(state["python"])
    if args.device.startswith("cuda"):
        torch.cuda.set_rng_state_all([value.cpu() for value in state["cuda"]])


def save_checkpoint(path, model, moe, optimizer, stream_rng, step, config_hash, frozen_hash, args):
    current = sampled_parameter_hash(model, f"model.layers.{args.layer}.mlp.")
    if current != frozen_hash:
        raise RuntimeError("Frozen backbone sample hash changed")
    state = {"schema": 1, "step": step, "moe": moe.state_dict(), "optimizer": optimizer.state_dict(),
             "stream_rng": stream_rng.bit_generator.state, "rng": rng_state(args),
             "config_hash": config_hash, "frozen_sample_hash": current}
    tmp = path.with_suffix(".tmp")
    torch.save(state, tmp)
    tmp.replace(path)


def gradient_audit(nll, lb, z_loss, moe):
    gate = moe.block.gate.weight
    counts = moe.last_router_logits.detach().float().topk(moe.block.top_k, -1).indices.reshape(-1).bincount(minlength=moe.block.num_experts)
    selected = int(counts.argmax())
    expert = moe.block.experts[selected].up_proj.weight
    result = {"expert_index": selected}
    for name, objective, parameters in (("nll", nll, [gate, expert]), ("lb", lb, [gate]), ("z", z_loss, [gate])):
        gradients = torch.autograd.grad(objective, parameters, retain_graph=True, allow_unused=True)
        norms = [float(g.detach().float().norm()) if g is not None else 0.0 for g in gradients]
        result[name + "_gradient_norms"] = norms
        if any(not math.isfinite(norm) or norm == 0 for norm in norms):
            raise RuntimeError(f"Missing/nonfinite {name} gradient: {norms}")
    return result


def run_train(model, data, held_windows, items, args, provenance):
    torch.manual_seed(args.seed)
    dense = model.model.layers[args.layer].mlp
    if dense.up_proj.out_features != args.top_k * args.expert_size:
        raise ValueError("Active expert width must match the replaced dense FFN width")
    frozen_prefix = f"model.layers.{args.layer}.mlp."
    frozen_hash = sampled_parameter_hash(model, frozen_prefix)
    moe = TensorMoE(model.config.hidden_size, args.expert_size, args.experts, args.top_k, args.init_std).to(args.device)
    model.model.layers[args.layer].mlp = moe
    # Parent stays eval: frozen attention/dropout is not a stochastic treatment.
    model.eval()
    moe.train()
    for parameter in moe.parameters():
        parameter.requires_grad_(True)
    trainable = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    if any(not name.startswith(frozen_prefix) for name, _ in trainable):
        raise RuntimeError("Unexpected trainable backbone parameter")
    if sampled_parameter_hash(model, frozen_prefix) != frozen_hash:
        raise RuntimeError("Installing MoE changed frozen backbone")
    optimizer = torch.optim.AdamW([p for _, p in trainable], lr=args.lr, betas=(.9, .95),
                                 eps=1e-8, weight_decay=args.weight_decay)
    order_rng = np.random.default_rng(args.order_seed)
    provenance.update({"trainable_parameters": [{"name": n, "shape": list(p.shape), "numel": p.numel()} for n, p in trainable],
                       "trainable_count": sum(p.numel() for _, p in trainable),
                       "frozen_sample_hash": frozen_hash,
                       "moe_initial_sample_hash": sampled_parameter_hash(moe),
                       "moe_config": moe.config.to_dict(),
                       "lb_definition": "E * sum_e [count_e/(N*k)] * mean_token softmax(logits)_e; uniform=1",
                       "lb_scope": "computed per forward microbatch, averaged across accumulation steps",
                       "z_definition": "mean_token(logsumexp(router_logits)^2)"})
    hash_args = {key: value for key, value in vars(args).items() if key not in
                 {"mode", "output", "resume", "max_updates", "save_every", "eval_every", "max_hours"}}
    config_hash = digest_json({"args": hash_args, "data": data.provenance,
                              "model_config": model.config.to_dict(), "frozen_hash": frozen_hash,
                              "pos_items_sha256": provenance["pos_items_sha256"],
                              "script_sha256": provenance["script_sha256"]})
    provenance["config_hash"] = config_hash
    write_json(Path(args.output) / "provenance.json", provenance)
    start_step = 0
    if args.resume:
        state = torch.load(args.resume, map_location=args.device, weights_only=False)
        if state["config_hash"] != config_hash or state["frozen_sample_hash"] != frozen_hash:
            raise ValueError("Resume configuration/data/backbone differs from checkpoint")
        moe.load_state_dict(state["moe"])
        optimizer.load_state_dict(state["optimizer"])
        order_rng.bit_generator.state = state["stream_rng"]
        restore_rng(state["rng"], args)
        start_step = int(state["step"])
    output = Path(args.output)
    if (output / "checkpoint.pt").exists() and not args.resume:
        raise ValueError("Existing checkpoint requires explicit --resume")
    initial_rows = evaluate(model, data, held_windows, args)
    context = {"target": None}
    initial_pos = evaluate_pos(model, items, args, context)
    history_path = output / "training_summary.json"
    previous = json.loads(history_path.read_text()) if args.resume and history_path.exists() else {}
    history = previous.get("evaluations", [])
    if not any(row["step"] == start_step for row in history):
        history.append({"step": start_step, "held": summarize(initial_rows, iterations=args.bootstrap, available_sources=data.sources_available),
                        "pos": pos_summary(initial_pos)})
    step, status, start_time = start_step, "complete", time.monotonic()
    time_steps = []
    token_per_step = args.seq_len * args.batch_size * args.accum
    if args.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats(args.device)
    with open(output / "train_steps.jsonl", "a" if args.resume else "w") as log:
        while step < args.steps:
            if (step + 1) * token_per_step > args.max_train_tokens:
                status = "pilot_token_limit"
                break
            if args.max_updates and step - start_step >= args.max_updates:
                status = "invocation_update_limit"
                break
            if time.monotonic() - start_time >= args.max_hours * 3600:
                status = "wall_time_limit"
                break
            if args.device.startswith("cuda"):
                torch.cuda.synchronize(args.device)
            step_started = time.monotonic()
            optimizer.zero_grad(set_to_none=True)
            rate = lr_at(step, args)
            for group in optimizer.param_groups:
                group["lr"] = rate
            losses = np.zeros(3)
            loads = torch.zeros(args.experts, device=args.device)
            audit = None
            for micro in range(args.accum):
                batch = data.train_batch(order_rng, args.batch_size).to(args.device)
                logits = forward_logits(model, batch[:, :-1], args)
                nll = token_nll(logits, batch[:, 1:]).mean()
                lb, z, frequency, probabilities = moe.losses_and_load()
                if step == 0 and micro == 0:
                    audit = gradient_audit(nll, lb, z, moe)
                    write_json(output / "gradient_audit.json", audit)
                objective = nll + args.lb_coef * lb + args.z_coef * z
                if not torch.isfinite(objective):
                    raise RuntimeError("Nonfinite training objective")
                (objective / args.accum).backward()
                losses += np.array([float(nll.detach()), float(lb.detach()), float(z.detach())]) / args.accum
                loads.add_(frequency / args.accum)
                moe.last_router_logits = None
            if any(p.grad is not None for n, p in model.named_parameters() if not n.startswith(frozen_prefix)):
                raise RuntimeError("Frozen backbone has gradients")
            norm = float(torch.nn.utils.clip_grad_norm_([p for _, p in trainable], args.grad_clip, error_if_nonfinite=True))
            optimizer.step()
            step += 1
            if args.device.startswith("cuda"):
                torch.cuda.synchronize(args.device)
            duration = time.monotonic() - step_started
            time_steps.append(duration)
            entropy = float(-(loads * loads.clamp_min(1e-30).log()).sum())
            record = {"step": step, "train_tokens": step * token_per_step, "nll": float(losses[0]),
                      "lb_raw": float(losses[1]), "z_raw": float(losses[2]), "lr": rate,
                      "gradient_norm_before_clip": norm, "seconds": duration,
                      "tokens_per_second": token_per_step / duration, "expert_load": loads.cpu().tolist(),
                      "load_entropy": entropy, "dead_experts_in_step": int((loads == 0).sum())}
            log.write(json.dumps(record, allow_nan=False) + "\n")
            log.flush()
            emit("train", **{k: v for k, v in record.items() if k != "expert_load"})
            if args.eval_every and step % args.eval_every == 0:
                rows = evaluate(model, data, held_windows, args)
                pos_rows = evaluate_pos(model, items, args, context)
                history.append({"step": step, "held": summarize(rows, iterations=args.bootstrap, available_sources=data.sources_available), "pos": pos_summary(pos_rows)})
            if args.save_every and step % args.save_every == 0:
                save_checkpoint(output / "checkpoint.pt", model, moe, optimizer, order_rng, step,
                                config_hash, frozen_hash, args)
    rows = evaluate(model, data, held_windows, args)
    pos_rows = evaluate_pos(model, items, args, context)
    if not history or history[-1]["step"] != step:
        history.append({"step": step, "held": summarize(rows, iterations=args.bootstrap, available_sources=data.sources_available), "pos": pos_summary(pos_rows)})
    save_checkpoint(output / "checkpoint.pt", model, moe, optimizer, order_rng, step, config_hash, frozen_hash, args)
    stable_times = time_steps[1:] or time_steps
    result = {"status": status, "step": step, "planned_steps": args.steps, "train_tokens": step * token_per_step,
              "evaluations": history, "config_hash": config_hash,
              "frozen_sample_hash_before": frozen_hash,
              "frozen_sample_hash_after": sampled_parameter_hash(model, frozen_prefix),
              "step_seconds_mean_after_first": float(np.mean(stable_times)) if stable_times else None,
              "tokens_per_second_after_first": token_per_step / np.mean(stable_times) if stable_times else None,
              "invocation_seconds": time.monotonic() - start_time,
              "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(args.device) if args.device.startswith("cuda") else None}
    write_json(output / "training_summary.json", result)
    write_json(output / "final_held_sequences.json", rows)
    write_json(output / "final_pos.json", pos_rows)
    emit("train_finished", status=status, step=step, train_tokens=result["train_tokens"])
    return result


def parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=("baseline", "train", "self-test"), required=True)
    ap.add_argument("--model", "--model-dir", dest="model")
    ap.add_argument("--data")
    ap.add_argument("--output")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--dtype", choices=("float32", "bfloat16"), default="bfloat16")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--order-seed", type=int, default=0)
    ap.add_argument("--layer", type=int, default=9)
    ap.add_argument("--experts", type=int, default=64)
    ap.add_argument("--expert-size", type=int, default=1024)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--init-std", type=float, default=.02)
    ap.add_argument("--steps", type=int, default=64)
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--accum", type=int, default=1)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--warmup-fraction", type=float, default=.1)
    ap.add_argument("--weight-decay", type=float, default=.1)
    ap.add_argument("--lb-coef", type=float, default=.01)
    ap.add_argument("--z-coef", type=float, default=.001)
    ap.add_argument("--grad-clip", type=float, default=1.)
    ap.add_argument("--token-dtype", choices=("uint16", "uint32"), default="uint16")
    ap.add_argument("--eval-sequences", type=int, default=128)
    ap.add_argument("--cal-sequences", type=int, default=64)
    ap.add_argument("--eval-seed", type=int, default=91023)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--pos-items", default=str(WB / "results/e121/items_pos.jsonl"))
    ap.add_argument("--eval-every", type=int, default=64)
    ap.add_argument("--save-every", type=int, default=64)
    ap.add_argument("--resume")
    ap.add_argument("--max-updates", type=int, default=0, help="Invocation-only cap; --steps fixes the LR schedule")
    ap.add_argument("--max-train-tokens", type=int, default=32_000_000)
    ap.add_argument("--max-hours", type=float, default=8.)
    return ap


def run(args):
    if not args.model or not args.data or not args.output:
        raise ValueError("--model, --data, --output are required")
    if args.steps < 1 or min(args.seq_len, args.batch_size, args.accum, args.eval_sequences, args.cal_sequences) < 1:
        raise ValueError("Steps, sequence/batch sizes, accumulation and fixed-window counts must be positive")
    if not 1 <= args.top_k <= args.experts or not 0 <= args.warmup_fraction < 1:
        raise ValueError("Invalid top-k or warmup fraction")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    data_started = time.monotonic()
    data = TokenData(args.data, args.seq_len, args.token_dtype)
    held_windows = data.fixed_windows("held", args.eval_sequences, args.eval_seed)
    cal_windows = data.fixed_windows("train", args.cal_sequences, args.eval_seed + 1)
    data_seconds = time.monotonic() - data_started
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    model_started = time.monotonic()
    dtype = getattr(torch, args.dtype)
    if args.device == "cpu" and dtype != torch.float32:
        raise ValueError("CPU smoke requires --dtype float32")
    model = OlmoForCausalLM.from_pretrained(args.model, dtype=dtype, local_files_only=True,
                                          attn_implementation="sdpa").to(args.device).eval()
    model.config.use_cache = False
    if not 0 <= args.layer < len(model.model.layers):
        raise ValueError("Layer index outside backbone")
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    dense = model.model.layers[args.layer].mlp
    if tuple(dense.gate_proj.weight.shape) != tuple(dense.up_proj.weight.shape):
        raise ValueError("Unexpected dense SwiGLU shapes")
    model_dir = Path(args.model)
    metadata_hashes = {p.name: sha256_file(p) for p in (model_dir / "config.json", model_dir / "model.safetensors.index.json") if p.exists()}
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=WB, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "unknown"
    provenance = {"args": vars(args), "data": data.provenance, "data_load_hash_seconds": data_seconds,
                  "model_load_seconds": time.monotonic() - model_started, "model_metadata_sha256": metadata_hashes,
                  "dense_ffn_shapes": {name: list(parameter.shape) for name, parameter in dense.named_parameters()},
                  "torch": torch.__version__, "transformers": transformers.__version__,
                  "python": platform.python_version(), "platform": platform.platform(),
                  "cuda_runtime": torch.version.cuda, "device": args.device,
                  "device_name": torch.cuda.get_device_name(args.device) if args.device.startswith("cuda") else platform.processor(),
                  "git_commit": git_commit, "script_sha256": sha256_file(__file__),
                  "pos_items_sha256": sha256_file(args.pos_items) if args.pos_items and Path(args.pos_items).exists() else None,
                  "held_window_hash": digest_json(held_windows), "calibration_window_hash": digest_json(cal_windows),
                  "model_loaded_parameter_sample_hash": sampled_parameter_hash(model),
                  "sample_hash_note": "33 fixed elements per tensor; mutation audit, not full checkpoint digest"}
    all_sources = sorted({record["source"] for record in data.files["held"]})
    covered = {source: sum(data.files["held"][f]["source"] == source for f, _ in held_windows) for source in all_sources}
    provenance["held_source_coverage"] = {"sequences": covered, "missing_sources": [s for s, n in covered.items() if n == 0],
                                           "sampling": "uniform over all full held windows, without replacement"}
    write_json(output / "provenance.json", provenance)
    items = read_pos(args.pos_items)
    if items and max(max(row["ids"]) for row in items) >= model.config.vocab_size:
        raise ValueError("POS tokenizer IDs do not match backbone vocabulary")
    emit("loaded", model_seconds=provenance["model_load_seconds"], data_seconds=data_seconds,
         held_sequences=len(held_windows), pos_held_items=len(items), dense_ffn_shapes=provenance["dense_ffn_shapes"])
    if args.mode == "baseline":
        return run_baseline(model, data, held_windows, cal_windows, items, args, dense,
                            provenance["model_loaded_parameter_sample_hash"])
    return run_train(model, data, held_windows, items, args, provenance)


def self_test(output_path=None):
    """Meaningful CPU test: dense controls, gate math, LM gradients, exact resume."""
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e123_cpu_") as temp:
        root = Path(temp)
        torch.manual_seed(99)
        cfg = OlmoConfig(vocab_size=64, hidden_size=32, intermediate_size=64, num_hidden_layers=2,
                         num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=64,
                         pad_token_id=1, eos_token_id=2, attention_dropout=0.)
        OlmoForCausalLM(cfg).save_pretrained(root / "model")
        align_model = OlmoForCausalLM.from_pretrained(root / "model").eval()
        align_ids = torch.tensor([[3, 7, 12, 23, 5, 4, 8, 10, 11]])
        with torch.no_grad():
            explicit_nll = token_nll(align_model(align_ids[:, :-1]).logits, align_ids[:, 1:]).mean()
            hf_nll = align_model(align_ids, labels=align_ids).loss
        if not torch.allclose(explicit_nll, hf_nll, atol=1e-6):
            raise AssertionError("Explicit next-token objective differs from HF label shift")
        rng = np.random.default_rng(42)
        for split in ("train", "held"):
            np.save(root / f"{split}.npy", rng.integers(3, 64, 90, dtype=np.uint16))
        common = ["--model", str(root / "model"), "--data", str(root), "--device", "cpu", "--dtype", "float32",
                  "--layer", "1", "--experts", "4", "--expert-size", "32", "--top-k", "2", "--seq-len", "8",
                  "--batch-size", "2", "--eval-sequences", "4", "--cal-sequences", "4", "--steps", "3",
                  "--bootstrap", "30", "--pos-items", "", "--eval-every", "0", "--save-every", "0"]
        baseline = run(parser().parse_args(["--mode", "baseline", *common, "--output", str(root / "baseline")]))
        if not baseline["checks"]["zero_changed_nll"]:
            raise AssertionError("Real FFN zero intervention has no effect")
        full = root / "full"
        resumed = root / "resumed"
        run(parser().parse_args(["--mode", "train", *common, "--output", str(full)]))
        run(parser().parse_args(["--mode", "train", *common, "--output", str(resumed), "--max-updates", "1"]))
        run(parser().parse_args(["--mode", "train", *common, "--output", str(resumed), "--resume", str(resumed / "checkpoint.pt")]))
        a = torch.load(full / "checkpoint.pt", weights_only=False, map_location="cpu")
        b = torch.load(resumed / "checkpoint.pt", weights_only=False, map_location="cpu")
        max_error = max(float((a["moe"][name] - b["moe"][name]).abs().max()) for name in a["moe"])
        optimizer_error = max(float((values[name] - b["optimizer"]["state"][key][name]).abs().max())
                              for key, values in a["optimizer"]["state"].items()
                              for name in values if torch.is_tensor(values[name]))
        if max_error != 0 or a["step"] != b["step"] or a["stream_rng"] != b["stream_rng"]:
            raise AssertionError(f"Resume diverged: {max_error}")
        if optimizer_error != 0 or a["optimizer"]["param_groups"] != b["optimizer"]["param_groups"]:
            raise AssertionError(f"Resumed optimizer diverged: {optimizer_error}")
        moe = TensorMoE(8, 4, 4, 2, .02)
        with torch.no_grad():
            moe.block.gate.weight.zero_()
        hidden = torch.randn(2, 3, 8)
        output = moe(hidden)
        probabilities = F.softmax(moe.last_router_logits.float(), -1)
        weights, chosen = probabilities.topk(2, -1)
        manual = torch.zeros_like(hidden).view(-1, 8)
        flat = hidden.view(-1, 8)
        for row in range(len(flat)):
            for slot in range(2):
                manual[row] += weights[row, slot] * moe.block.experts[int(chosen[row, slot])](flat[row:row + 1])[0]
        if not torch.allclose(output.reshape_as(manual), manual, atol=1e-7):
            raise AssertionError("HF wrapper disagrees with non-renormalized mixture")
        lb, _, _, _ = moe.losses_and_load()
        if not torch.allclose(lb, torch.tensor(1.)) or not torch.allclose(weights.sum(-1), torch.full((6,), .5)):
            raise AssertionError("Load-balance scale or no-renorm contract violated")
        fake = [{"word": "w", "condition": c, "nll": n} for c, n in (("NOUN", 3.), ("VERB", 1.))]
        reference = [{**r, "nll": 0.} for r in fake]
        if pos_summary(fake, reference)["paired_within_word_noun_minus_verb"]["mean"] != 2.:
            raise AssertionError("Within-word condition contrast is wrong")
        result = {"passed": True, "device": "cpu", "torch": torch.__version__, "transformers": transformers.__version__,
                  "script_sha256": sha256_file(__file__), "exact_resume_max_parameter_error": max_error,
                  "exact_resume_max_optimizer_error": optimizer_error, "next_token_nll_alignment_error": float(abs(explicit_nll - hf_nll)),
                  "baseline_checks": baseline["checks"], "uniform_lb": float(lb.detach()),
                  "checks": ["baseline zero/mean/identity/reinsert", "NLL/router/expert/aux/z gradients",
                             "frozen backbone sampled hash", "exact optimizer/RNG/order resume",
                             "HF no-renorm mixture vs explicit sum", "explicit next-token objective vs HF labels",
                             "paired within-word condition contrast"]}
        destination = Path(output_path) if output_path else WB / "results/e123/self_test.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_json(destination, result)
        emit("self_test_passed", **result)


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test":
        self_test(args.output)
    else:
        try:
            run(args)
        except Exception as error:
            if args.output:
                Path(args.output).mkdir(parents=True, exist_ok=True)
                write_json(Path(args.output) / "failure.json", {"type": type(error).__name__, "message": str(error)})
            raise
