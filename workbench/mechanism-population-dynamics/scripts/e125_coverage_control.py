"""E125 frozen-layer data-coverage controls; never modifies E123/E124.

  --mode train --replacement moe|dense --model LOCAL_MODEL --data MANIFEST
  --mode self-test                 # tiny CPU only

The scientific default is a fixed 128M-token schedule: 15625 updates, seq512,
batch16, accumulation1. --max-updates limits an invocation without changing LR.
Source and window RNGs are separate children of SeedSequence(order_seed), so
different window-pool bounds cannot change the shared file-choice schedule.
Exposure counts, optimizer, RNG and replacement parameters all resume together.
Dense uses a genuine freshly initialized OlmoMLP; it has no router or aux loss.
Large checkpoints/count arrays remain in the local --output directory.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import math
import platform
import random
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from transformers import OlmoConfig, OlmoForCausalLM
from transformers.models.olmo.modeling_olmo import OlmoMLP

import e123_frozen_moe as base
from e124_functional_capture import tensor_state_hash

WB = Path(__file__).resolve().parents[1]


class SplitStream:
    def __init__(self, order_seed):
        source_seed, window_seed = np.random.SeedSequence(order_seed).spawn(2)
        self.source = np.random.default_rng(source_seed)
        self.window = np.random.default_rng(window_seed)

    def state_dict(self):
        return {"source": self.source.bit_generator.state, "window": self.window.bit_generator.state}

    def load_state_dict(self, state):
        self.source.bit_generator.state = state["source"]
        self.window.bit_generator.state = state["window"]


class CoverageTokenData(base.TokenData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window_counts = [np.zeros(record["windows"], dtype=np.uint32) for record in self.files["train"]]
        self.draws = 0
        self.unique = 0
        self.last_batch_keys = []
        self.source_schedule_hash = hashlib.sha256(b"E125-source-batch-chain-v1").hexdigest()

    def train_batch(self, rng, size):
        chosen = rng.source.choice(len(self.files["train"]), size=size, p=self.train_probabilities)
        self.source_schedule_hash = hashlib.sha256(bytes.fromhex(self.source_schedule_hash)
                                                  + np.asarray(chosen, dtype="<i8").tobytes()).hexdigest()
        rows, keys = [], []
        for file_index in chosen:
            file_index = int(file_index)
            window_index = int(rng.window.integers(self.files["train"][file_index]["windows"]))
            rows.append(self.window("train", file_index, window_index))
            keys.append((file_index, window_index))
            counts = self.window_counts[file_index]
            if counts[window_index] == 0:
                self.unique += 1
            counts[window_index] += 1
            self.draws += 1
        self.last_batch_keys = keys
        return torch.from_numpy(np.stack(rows))

    def coverage_summary(self, per_file=False):
        result = {"drawn_windows": self.draws, "unique_windows": self.unique,
                  "reused_windows": self.draws - self.unique,
                  "reuse_fraction": 1 - self.unique / self.draws if self.draws else 0.,
                  "unique_training_target_tokens": self.unique * self.seq_len,
                  "available_windows": sum(len(counts) for counts in self.window_counts),
                  "source_schedule_hash": self.source_schedule_hash}
        if per_file:
            result["files"] = [{"source": record["source"], "file_id": record["file_id"],
                                 "available_windows": len(counts), "drawn_windows": int(counts.sum(dtype=np.uint64)),
                                 "unique_windows": int(np.count_nonzero(counts)),
                                 "sampling_probability": float(self.train_probabilities[index])}
                                for index, (record, counts) in enumerate(zip(self.files["train"], self.window_counts))]
            result["count_arrays_sha256"] = base.digest_json([
                {"source": record["source"], "file_id": record["file_id"],
                 "sha256": hashlib.sha256(counts.tobytes()).hexdigest()}
                for record, counts in zip(self.files["train"], self.window_counts)])
        return result

    def coverage_state(self):
        return {"counts": self.window_counts, "draws": self.draws, "unique": self.unique,
                "source_schedule_hash": self.source_schedule_hash}

    def restore_coverage(self, state):
        if len(state["counts"]) != len(self.window_counts):
            raise ValueError("Resume coverage has different train file count")
        counts = [np.asarray(value, dtype=np.uint32) for value in state["counts"]]
        if any(len(a) != len(b) for a, b in zip(counts, self.window_counts)):
            raise ValueError("Resume coverage has different window pools")
        draws = sum(int(value.sum(dtype=np.uint64)) for value in counts)
        unique = sum(int(np.count_nonzero(value)) for value in counts)
        if draws != int(state["draws"]) or unique != int(state["unique"]):
            raise ValueError("Resume exposure totals do not match count arrays")
        self.window_counts, self.draws, self.unique = counts, draws, unique
        self.source_schedule_hash = state["source_schedule_hash"]

    def diagnostic_windows(self, count, seed):
        """Separate RNG; equal original-file quotas for seen and unseen windows."""
        rng = np.random.default_rng(seed)
        seen = [np.flatnonzero(values) for values in self.window_counts]
        unseen = [np.flatnonzero(values == 0) for values in self.window_counts]
        capacities = np.array([min(len(a), len(b)) for a, b in zip(seen, unseen)], dtype=np.int64)
        capacities[self.train_probabilities == 0] = 0
        total = int(capacities.sum())
        if total == 0 or count == 0:
            return [], [], {"paired_file_quotas": True, "requested": count, "actual": 0}
        probabilities = np.concatenate([np.full(int(n), self.train_probabilities[i] / n) for i, n in enumerate(capacities) if n])
        probabilities /= probabilities.sum()
        chosen = rng.choice(total, min(count, total), replace=False, p=probabilities)
        cumulative = capacities.cumsum()
        file_indices = np.searchsorted(cumulative, chosen, side="right")
        seen_keys, unseen_keys = [], []
        quotas = []
        for index, record in enumerate(self.files["train"]):
            quota = int((file_indices == index).sum())
            if quota:
                seen_keys.extend((index, int(w)) for w in rng.choice(seen[index], quota, replace=False))
                unseen_keys.extend((index, int(w)) for w in rng.choice(unseen[index], quota, replace=False))
            quotas.append({"source": record["source"], "file_id": record["file_id"], "quota_each": quota,
                           "seen_available": len(seen[index]), "unseen_available": len(unseen[index])})
        return seen_keys, unseen_keys, {"paired_file_quotas": True, "requested": count, "actual": len(seen_keys),
                                        "seed": seed, "files": quotas, "selection_depends_on_loss": False}


def validate_reference(data, reference):
    identities = lambda value: [(row["source"], row["file_id"]) for row in value.files["train"]]
    if identities(data) != identities(reference):
        raise ValueError("E125 requires the original train file identities and ordering")
    if not np.array_equal(data.train_probabilities, reference.train_probabilities):
        raise ValueError("E125 requires identical original per-file sampling probabilities")
    held = lambda value: [(row["source"], row["file_id"], row["sha256"], row["key"], row["windows"])
                          for row in value.files["held"]]
    if held(data) != held(reference):
        raise ValueError("E125 must reuse the original held files in the original order")
    if any(a["windows"] < b["windows"] for a, b in zip(data.files["train"], reference.files["train"])):
        raise ValueError("Coverage pool cannot shorten any original train window pool")


def register_initialization(path, specification, tensor_hash, run_id):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    identity = base.digest_json(specification)
    # Parallel M-small/M-cover processes check the same complete tensor hash.
    with path.with_suffix(".lock").open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        registry = json.loads(path.read_text()) if path.exists() else {}
        previous = registry.get(identity)
        if previous and previous["tensor_sha256"] != tensor_hash:
            raise ValueError("Same initialization specification produced different full tensor hashes")
        record = previous or {"specification": specification, "tensor_sha256": tensor_hash, "runs": []}
        if run_id not in record["runs"]:
            record["runs"].append(run_id)
        registry[identity] = record
        base.write_json(path, registry)
    return identity


def build_replacement(model, args):
    torch.manual_seed(args.seed)
    original = model.model.layers[args.layer].mlp
    if args.replacement == "moe":
        if original.up_proj.out_features != args.top_k * args.expert_size:
            raise ValueError("Active MoE width does not match original dense FFN")
        replacement = base.TensorMoE(model.config.hidden_size, args.expert_size, args.experts, args.top_k, args.init_std)
    else:
        replacement = OlmoMLP(model.config)
        for module in replacement.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0., std=args.init_std)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
        if replacement.up_proj.weight.shape != original.up_proj.weight.shape:
            raise ValueError("Dense control must have the original FFN width")
    return replacement


@torch.no_grad()
def evaluate_windows(model, data, split, windows, args):
    rows = []
    for batch, metadata in data.iter_fixed(split, windows, args.batch_size):
        batch = batch.to(args.device)
        losses = base.token_nll(base.forward_logits(model, batch[:, :-1], args), batch[:, 1:]).cpu()
        for values, meta in zip(losses, metadata):
            rows.append({**meta, "nll_sum": float(values.double().sum()), "tokens": len(values)})
    return rows


def dense_gradient_audit(nll, replacement):
    parameters = list(replacement.named_parameters())
    gradients = torch.autograd.grad(nll, [value for _, value in parameters], retain_graph=True, allow_unused=True)
    result = {name: float(value.float().norm()) if value is not None else 0. for (name, _), value in zip(parameters, gradients)}
    if any(value <= 0 or not math.isfinite(value) for value in result.values()):
        raise RuntimeError(f"Missing/nonfinite dense main-loss gradient: {result}")
    return {"replacement": "dense", "nll_gradient_norms": result, "auxiliary_losses": "absent"}


def save_checkpoint(path, model, replacement, optimizer, data, stream_rng, step, config_hash,
                    frozen_hash, initialization_hash, elapsed, args):
    current_hash = base.sampled_parameter_hash(model, f"model.layers.{args.layer}.mlp.")
    if current_hash != frozen_hash:
        raise RuntimeError("Frozen backbone sample hash changed")
    replacement_state = replacement.state_dict()
    state = {"schema": 2, "step": step, "replacement_kind": args.replacement,
             "replacement_state": replacement_state, "optimizer": optimizer.state_dict(),
             "stream_rng": stream_rng.state_dict(), "rng": base.rng_state(args),
             "coverage": data.coverage_state(), "config_hash": config_hash,
             "frozen_sample_hash": current_hash, "initial_tensor_sha256": initialization_hash,
             "elapsed_wall_seconds": elapsed}
    if args.replacement == "moe":
        state["moe"] = replacement_state  # alias, not a second tensor copy; E124-compatible.
    tmp = path.with_suffix(".tmp")
    torch.save(state, tmp)
    tmp.replace(path)


def run(args):
    if not all((args.model, args.data, args.output)):
        raise ValueError("--model, --data and --output are required")
    if args.steps < 1 or min(args.seq_len, args.batch_size, args.accum, args.eval_sequences) < 1:
        raise ValueError("Training sizes and fixed evaluation count must be positive")
    if not 0 <= args.warmup_fraction < 1 or not 1 <= args.top_k <= args.experts:
        raise ValueError("Invalid warmup or top-k")
    if args.device == "cpu" and args.dtype != "float32":
        raise ValueError("CPU tests require --dtype float32")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "checkpoint.pt").exists() and not args.resume:
        raise ValueError("Existing checkpoint requires explicit --resume")
    invocation_started = time.monotonic()
    data = CoverageTokenData(args.data, args.seq_len, args.token_dtype)
    reference = data if Path(args.reference_data).resolve() == Path(args.data).resolve() else base.TokenData(args.reference_data, args.seq_len, args.token_dtype)
    validate_reference(data, reference)
    held_windows = data.fixed_windows("held", args.eval_sequences, args.eval_seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    model = OlmoForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype), local_files_only=True,
                                          attn_implementation="sdpa").to(args.device).eval()
    model.config.use_cache = False
    model.requires_grad_(False)
    if not 0 <= args.layer < len(model.model.layers):
        raise ValueError("Layer index outside backbone")
    original = model.model.layers[args.layer].mlp
    prefix = f"model.layers.{args.layer}.mlp."
    frozen_hash = base.sampled_parameter_hash(model, prefix)
    replacement = build_replacement(model, args)
    initial_hash = tensor_state_hash(replacement.state_dict())
    run_id = args.run_id or output.name
    initialization_spec = {"replacement": args.replacement, "seed": args.seed, "layer": args.layer,
                           "hidden_size": model.config.hidden_size, "dense_width": original.up_proj.out_features,
                           "init_std": args.init_std, "frozen_sample_hash": frozen_hash,
                           "experts": args.experts if args.replacement == "moe" else None,
                           "expert_size": args.expert_size if args.replacement == "moe" else None,
                           "top_k": args.top_k if args.replacement == "moe" else None}
    initialization_id = register_initialization(args.init_registry, initialization_spec, initial_hash, run_id)
    replacement = replacement.to(args.device)
    model.model.layers[args.layer].mlp = replacement
    model.eval()
    replacement.train()
    replacement.requires_grad_(True)
    trainable = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if any(not name.startswith(prefix) for name, _ in trainable):
        raise RuntimeError("Unexpected trainable backbone parameters")
    optimizer = torch.optim.AdamW([value for _, value in trainable], lr=args.lr, betas=(.9, .95),
                                 weight_decay=args.weight_decay, eps=1e-8)
    stream_rng = SplitStream(args.order_seed)
    operational = {"mode", "output", "resume", "max_updates", "save_every", "eval_every", "max_hours", "init_registry", "run_id", "summary"}
    scientific_args = {key: value for key, value in vars(args).items() if key not in operational}
    config_hash = base.digest_json({"args": scientific_args, "data": data.provenance,
                                   "frozen_sample_hash": frozen_hash, "initial_tensor_sha256": initial_hash,
                                   "pos_sha256": base.sha256_file(args.pos_items) if args.pos_items else None,
                                   "script_sha256": base.sha256_file(__file__),
                                   "e123_sha256": base.sha256_file(WB / "scripts/e123_frozen_moe.py"),
                                   "e124_sha256": base.sha256_file(WB / "scripts/e124_functional_capture.py")})
    start_step, previous_wall = 0, 0.
    if args.resume:
        checkpoint = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
        if checkpoint["config_hash"] != config_hash or checkpoint["frozen_sample_hash"] != frozen_hash:
            raise ValueError("Resume config/data/backbone mismatch")
        if checkpoint["initial_tensor_sha256"] != initial_hash or checkpoint["replacement_kind"] != args.replacement:
            raise ValueError("Resume replacement kind/initialization mismatch")
        replacement.load_state_dict(checkpoint["replacement_state"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        stream_rng.load_state_dict(checkpoint["stream_rng"])
        data.restore_coverage(checkpoint["coverage"])
        base.restore_rng(checkpoint["rng"], args)
        start_step, previous_wall = int(checkpoint["step"]), float(checkpoint["elapsed_wall_seconds"])
        del checkpoint
    expected_draws = start_step * args.batch_size * args.accum
    if data.draws != expected_draws:
        raise ValueError("Coverage exposure count is inconsistent with resumed update count")
    provenance = {"args": vars(args), "run_id": run_id, "config_hash": config_hash,
                  "script_sha256": base.sha256_file(__file__),
                  "e123_script_sha256": base.sha256_file(WB / "scripts/e123_frozen_moe.py"),
                  "e124_script_sha256": base.sha256_file(WB / "scripts/e124_functional_capture.py"),
                  "initial_tensor_sha256": initial_hash, "initialization_registry_id": initialization_id,
                  "initialization_registry": str(Path(args.init_registry).resolve()),
                  "frozen_sample_hash": frozen_hash, "data": data.provenance,
                  "original_file_probability_vector": data.train_probabilities.tolist(),
                  "rng_definition": "SeedSequence(order_seed).spawn(2): child0=file choices, child1=window indices",
                  "source_schedule_hash_definition": "sha256 chain of previous digest and each little-endian int64 file-choice batch",
                  "held_window_hash": base.digest_json(held_windows),
                  "replacement_kind": args.replacement, "auxiliary_enabled": args.replacement == "moe",
                  "auxiliary_formula": "E*sum(count/(N*k)*mean_softmax), uniform=1; per microbatch" if args.replacement == "moe" else None,
                  "trainable_parameters": [{"name": name, "shape": list(value.shape), "numel": value.numel()} for name, value in trainable],
                  "trainable_count": sum(value.numel() for _, value in trainable),
                  "torch": torch.__version__, "numpy": np.__version__, "python": platform.python_version(), "device": args.device,
                  "hardware": torch.cuda.get_device_name(args.device) if args.device.startswith("cuda") else platform.processor(),
                  "load_and_hash_seconds": time.monotonic() - invocation_started}
    base.write_json(output / "provenance.json", provenance)
    base.emit("initialized", run_id=run_id, replacement=args.replacement, full_initial_tensor_sha256=initial_hash,
              start_step=start_step, trainable_count=provenance["trainable_count"])
    items = base.read_pos(args.pos_items)
    context = {"target": None}
    model.model.layers[args.layer].mlp = original
    dense_held = evaluate_windows(model, data, "held", held_windows, args)
    dense_pos = base.evaluate_pos(model, items, args, context)
    model.model.layers[args.layer].mlp = replacement
    base.write_json(output / "dense_reference_held.json", dense_held)
    base.write_json(output / "dense_reference_pos.json", dense_pos)
    history_path = output / "training_summary.json"
    previous = json.loads(history_path.read_text()) if args.resume and history_path.exists() else {}
    evaluations = previous.get("evaluations", [])

    def measure(step):
        rows = evaluate_windows(model, data, "held", held_windows, args)
        pos = base.evaluate_pos(model, items, args, context)
        summary = {"step": step, "held": base.summarize(rows, iterations=args.bootstrap, available_sources=data.sources_available),
                   "held_delta_dense": base.summarize(rows, dense_held, args.bootstrap, data.sources_available),
                   "pos": base.pos_summary(pos), "pos_delta_dense": base.pos_summary(pos, dense_pos),
                   "coverage": data.coverage_summary()}
        base.emit("evaluation", run_id=run_id, step=step, held_nll=summary["held"]["sequence"]["mean"],
                  delta_dense=summary["held_delta_dense"]["sequence"]["mean"], coverage=summary["coverage"])
        return summary, rows, pos

    if not any(row["step"] == start_step for row in evaluations):
        evaluations.append(measure(start_step)[0])
    step, status = start_step, "complete"
    tokens_per_step = args.seq_len * args.batch_size * args.accum
    timings = []
    if args.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats(args.device)
    elapsed = lambda: previous_wall + time.monotonic() - invocation_started

    def checkpoint_now():
        save_checkpoint(output / "checkpoint.pt", model, replacement, optimizer, data, stream_rng, step,
                        config_hash, frozen_hash, initial_hash, elapsed(), args)

    with (output / "train_steps.jsonl").open("a" if args.resume else "w") as log:
        while step < args.steps:
            if (step + 1) * tokens_per_step > args.max_train_tokens:
                status = "token_limit"
                break
            if args.max_updates and step - start_step >= args.max_updates:
                status = "invocation_update_limit"
                break
            if elapsed() >= args.max_hours * 3600:
                status = "wall_time_limit"
                break
            if args.device.startswith("cuda"):
                torch.cuda.synchronize(args.device)
            step_started = time.monotonic()
            optimizer.zero_grad(set_to_none=True)
            rate = base.lr_at(step, args)
            for group in optimizer.param_groups:
                group["lr"] = rate
            nll_average, lb_average, z_average = 0., 0., 0.
            loads = torch.zeros(args.experts, device=args.device) if args.replacement == "moe" else None
            for micro in range(args.accum):
                batch = data.train_batch(stream_rng, args.batch_size).to(args.device)
                nll = base.token_nll(base.forward_logits(model, batch[:, :-1], args), batch[:, 1:]).mean()
                if args.replacement == "moe":
                    lb, z, frequency, _ = replacement.losses_and_load()
                    objective = nll + args.lb_coef * lb + args.z_coef * z
                    loads.add_(frequency / args.accum)
                    lb_average += float(lb.detach()) / args.accum
                    z_average += float(z.detach()) / args.accum
                else:
                    objective = nll
                if step == 0 and micro == 0:
                    audit = base.gradient_audit(nll, lb, z, replacement) if args.replacement == "moe" else dense_gradient_audit(nll, replacement)
                    base.write_json(output / "gradient_audit.json", audit)
                if not torch.isfinite(objective):
                    raise RuntimeError("Nonfinite training objective")
                (objective / args.accum).backward()
                nll_average += float(nll.detach()) / args.accum
                if args.replacement == "moe":
                    replacement.last_router_logits = None
            if any(value.grad is not None for name, value in model.named_parameters() if not name.startswith(prefix)):
                raise RuntimeError("Frozen backbone received gradients")
            gradient_norm = float(torch.nn.utils.clip_grad_norm_([value for _, value in trainable], args.grad_clip, error_if_nonfinite=True))
            optimizer.step()
            step += 1
            if data.draws != step * args.batch_size * args.accum:
                raise RuntimeError("Training exposure counter diverged from update count")
            if args.device.startswith("cuda"):
                torch.cuda.synchronize(args.device)
            duration = time.monotonic() - step_started
            timings.append(duration)
            record = {"step": step, "train_tokens": step * tokens_per_step, "replacement": args.replacement,
                      "nll": nll_average, "lr": rate, "gradient_norm_before_clip": gradient_norm,
                      "seconds": duration, "tokens_per_second": tokens_per_step / duration,
                      "coverage": data.coverage_summary()}
            if args.replacement == "moe":
                record.update({"lb_raw": lb_average, "z_raw": z_average, "expert_load": loads.cpu().tolist(),
                               "load_entropy": float(-(loads * loads.clamp_min(1e-30).log()).sum()),
                               "dead_experts_in_step": int((loads == 0).sum())})
            log.write(json.dumps(record, allow_nan=False) + "\n")
            log.flush()
            base.emit("train", run_id=run_id, **{key: value for key, value in record.items() if key != "expert_load"})
            if args.eval_every and step % args.eval_every == 0:
                evaluations.append(measure(step)[0])
                base.write_json(history_path, {"status": "running", "step": step, "evaluations": evaluations})
            if args.save_every and step % args.save_every == 0:
                checkpoint_now()
    final_evaluation, final_rows, final_pos = measure(step)
    if not evaluations or evaluations[-1]["step"] != step:
        evaluations.append(final_evaluation)
    checkpoint_now()
    # Final diagnostic selection uses exposure only, with equal file quotas.
    seen, unseen, diagnostic_metadata = data.diagnostic_windows(args.diagnostic_sequences, args.diagnostic_seed)
    diagnostic = {"selection": diagnostic_metadata}
    for label, windows in (("seen", seen), ("unseen", unseen)):
        trained_rows = evaluate_windows(model, data, "train", windows, args) if windows else []
        model.model.layers[args.layer].mlp = original
        dense_rows = evaluate_windows(model, data, "train", windows, args) if windows else []
        model.model.layers[args.layer].mlp = replacement
        diagnostic[label] = {"windows": windows, "trained": base.summarize(trained_rows, iterations=args.bootstrap),
                             "dense": base.summarize(dense_rows, iterations=args.bootstrap),
                             "delta_dense": base.summarize(trained_rows, dense_rows, args.bootstrap)} if windows else None
        base.write_json(output / f"diagnostic_{label}_trained.json", trained_rows)
        base.write_json(output / f"diagnostic_{label}_dense.json", dense_rows)
    base.write_json(output / "coverage_diagnostic.json", diagnostic)
    np.savez(output / "window_counts.npz", **{f"file_{index}": value for index, value in enumerate(data.window_counts)})
    coverage = data.coverage_summary(per_file=True)
    current_frozen = base.sampled_parameter_hash(model, prefix)
    if current_frozen != frozen_hash:
        raise RuntimeError("Frozen backbone changed during final diagnostics")
    stable_times = timings[1:] or timings
    result = {"status": status, "run_id": run_id, "replacement": args.replacement, "step": step,
              "planned_steps": args.steps, "train_tokens": step * tokens_per_step, "config_hash": config_hash,
              "initial_tensor_sha256": initial_hash, "frozen_sample_hash_before": frozen_hash,
              "frozen_sample_hash_after": current_frozen, "evaluations": evaluations, "coverage": coverage,
              "dense_reference": base.summarize(dense_held, iterations=args.bootstrap, available_sources=data.sources_available),
              "diagnostic": diagnostic, "elapsed_wall_seconds": elapsed(),
              "tokens_per_second_after_first": tokens_per_step / float(np.mean(stable_times)) if stable_times else None,
              "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(args.device) if args.device.startswith("cuda") else None}
    base.write_json(history_path, result)
    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        base.write_json(args.summary, result)
    base.write_json(output / "final_held_sequences.json", final_rows)
    base.write_json(output / "final_pos.json", final_pos)
    base.emit("train_finished", run_id=run_id, status=status, step=step, coverage=coverage)
    return result


def parser():
    ap = base.parser()
    ap.description = __doc__
    for action in ap._actions:
        if action.dest == "mode":
            action.choices = ("train", "self-test")
    ap.set_defaults(steps=15625, batch_size=16, eval_sequences=512, eval_every=512,
                    save_every=1024, max_train_tokens=128_000_000, max_hours=3.)
    ap.add_argument("--replacement", "--kind", choices=("moe", "dense"), default="moe")
    ap.add_argument("--reference-data", default=str(WB / "results/e123/manifest.json"))
    ap.add_argument("--init-registry", default=str(WB / "results/e125/initializations.json"))
    ap.add_argument("--run-id")
    ap.add_argument("--summary")
    ap.add_argument("--diagnostic-sequences", type=int, default=512)
    ap.add_argument("--diagnostic-seed", type=int, default=125)
    return ap


def compare_checkpoints(first, second):
    a = torch.load(first, map_location="cpu", weights_only=False)
    b = torch.load(second, map_location="cpu", weights_only=False)
    parameter_error = max(float((a["replacement_state"][key] - b["replacement_state"][key]).abs().max()) for key in a["replacement_state"])
    optimizer_error = max(float((value - b["optimizer"]["state"][key][name]).abs().max())
                          for key, values in a["optimizer"]["state"].items() for name, value in values.items() if torch.is_tensor(value))
    same_counts = all(np.array_equal(x, y) for x, y in zip(a["coverage"]["counts"], b["coverage"]["counts"]))
    if parameter_error or optimizer_error or not same_counts or a["stream_rng"] != b["stream_rng"] or a["coverage"]["source_schedule_hash"] != b["coverage"]["source_schedule_hash"]:
        raise AssertionError("Resume changed parameters/optimizer/RNG/exposure counts")
    if not torch.equal(a["rng"]["torch"], b["rng"]["torch"]):
        raise AssertionError("Resume changed torch RNG state")
    return {"parameter_max_error": parameter_error, "optimizer_max_error": optimizer_error, "coverage_counts_identical": same_counts}


def self_test():
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e125_cpu_") as directory:
        root = Path(directory)
        rng = np.random.default_rng(125)
        train = []
        cover_train = []
        for index, size in enumerate((90, 45)):
            extended = rng.integers(3, 64, size * 3, dtype=np.uint16)
            small_path, cover_path = root / f"small{index}.npy", root / f"cover{index}.npy"
            np.save(small_path, extended[:size])
            np.save(cover_path, extended)
            common = {"source": "source" + str(index), "file_id": "train" + str(index),
                      "sampling_weight": (.7, .3)[index], "dtype": "uint16"}
            train.append({**common, "path": str(small_path)})
            cover_train.append({**common, "path": str(cover_path)})
        held_path = root / "held.npy"
        np.save(held_path, rng.integers(3, 64, 90, dtype=np.uint16))
        held = [{"path": str(held_path), "source": "source0", "file_id": "held"}]
        small_manifest, cover_manifest = root / "small.json", root / "cover.json"
        base.write_json(small_manifest, {"train": train, "held": held})
        base.write_json(cover_manifest, {"train": cover_train, "held": held})
        measured = CoverageTokenData(small_manifest, 8)
        measured_cover = CoverageTokenData(cover_manifest, 8)
        measured_rng, cover_rng, expected_rng = SplitStream(0), SplitStream(0), SplitStream(0)
        for _ in range(5):
            expected_files = expected_rng.source.choice(2, size=3, p=measured.train_probabilities)
            expected_keys = [(int(i), int(expected_rng.window.integers(measured.files["train"][int(i)]["windows"]))) for i in expected_files]
            measured.train_batch(measured_rng, 3)
            measured_cover.train_batch(cover_rng, 3)
            if measured.last_batch_keys != expected_keys:
                raise AssertionError("Coverage bookkeeping changed the split-RNG sampling protocol")
            if [i for i, _ in measured.last_batch_keys] != [i for i, _ in measured_cover.last_batch_keys]:
                raise AssertionError("Pool bounds changed the shared source sequence")
        if expected_rng.state_dict() != measured_rng.state_dict() or measured.draws != 15:
            raise AssertionError("Coverage bookkeeping consumed extra RNG")
        if measured.source_schedule_hash != measured_cover.source_schedule_hash:
            raise AssertionError("Source schedule hash differs across pools")
        torch.manual_seed(125)
        config = OlmoConfig(vocab_size=64, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
                            num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32,
                            pad_token_id=1, eos_token_id=2, attention_dropout=0.)
        OlmoForCausalLM(config).save_pretrained(root / "model")
        common = ["--mode", "train", "--model", str(root / "model"), "--reference-data", str(small_manifest),
                  "--init-registry", str(root / "initializations.json"), "--device", "cpu", "--dtype", "float32",
                  "--seed", "0", "--order-seed", "0", "--layer", "1", "--experts", "4", "--expert-size", "16",
                  "--top-k", "2", "--seq-len", "8", "--batch-size", "2", "--steps", "3", "--eval-sequences", "4",
                  "--bootstrap", "30", "--pos-items", "", "--eval-every", "0", "--save-every", "0",
                  "--diagnostic-sequences", "3"]
        results = {}
        for name, kind, manifest in (("M-small", "moe", small_manifest), ("M-cover", "moe", cover_manifest),
                                     ("D-cover", "dense", cover_manifest)):
            results[name] = run(parser().parse_args([*common, "--replacement", kind, "--data", str(manifest),
                                                   "--output", str(root / name)]))
        if results["M-small"]["initial_tensor_sha256"] != results["M-cover"]["initial_tensor_sha256"]:
            raise AssertionError("MoE data conditions started from different full tensors")
        if results["M-small"]["coverage"]["source_schedule_hash"] != results["M-cover"]["coverage"]["source_schedule_hash"]:
            raise AssertionError("MoE conditions used different source schedules")
        resume_results = {}
        for name, kind, manifest, full in (("M-resume", "moe", small_manifest, "M-small"),
                                           ("D-resume", "dense", cover_manifest, "D-cover")):
            run(parser().parse_args([*common, "--replacement", kind, "--data", str(manifest),
                                     "--output", str(root / name), "--max-updates", "1"]))
            run(parser().parse_args([*common, "--replacement", kind, "--data", str(manifest),
                                     "--output", str(root / name), "--resume", str(root / name / "checkpoint.pt")]))
            resume_results[kind] = compare_checkpoints(root / full / "checkpoint.pt", root / name / "checkpoint.pt")
        dense_audit = json.loads((root / "D-cover/gradient_audit.json").read_text())
        if dense_audit["auxiliary_losses"] != "absent":
            raise AssertionError("Dense control unexpectedly has routing auxiliary losses")
        for value in results.values():
            if value["frozen_sample_hash_before"] != value["frozen_sample_hash_after"]:
                raise AssertionError("Frozen backbone changed")
        result = {"passed": True, "device": "cpu", "script_sha256": base.sha256_file(__file__),
                  "e123_script_sha256": base.sha256_file(WB / "scripts/e123_frozen_moe.py"),
                  "e124_script_sha256": base.sha256_file(WB / "scripts/e124_functional_capture.py"),
                  "same_MoE_initial_tensor_sha256": results["M-small"]["initial_tensor_sha256"],
                  "dense_gradient_audit": dense_audit, "resume": resume_results,
                  "same_source_schedule_hash": results["M-small"]["coverage"]["source_schedule_hash"],
                  "split_rng_sampling_known_answer": True, "coverage_known_draws": measured.draws,
                  "checks": ["same full MoE initialization across data pools", "real dense FFN without aux/router",
                             "nonzero dense and MoE gradients", "frozen backbone", "exact dense and MoE resume",
                             "exposure counts resume", "shared source schedule across different pool bounds",
                             "split source/window RNG known answer", "seen/unseen file-matched diagnostics"]}
        destination = WB / "results/e125/self_test.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        base.write_json(destination, result)
        base.emit("self_test_passed", **result)
        return result


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test":
        self_test()
    else:
        try:
            run(args)
        except Exception as error:
            if args.output:
                Path(args.output).mkdir(parents=True, exist_ok=True)
                base.write_json(Path(args.output) / "failure.json", {"type": type(error).__name__, "message": str(error)})
            raise
