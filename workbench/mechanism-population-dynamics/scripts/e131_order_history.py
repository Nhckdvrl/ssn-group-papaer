"""E131: reorder one fixed minibatch block, then restore common input history.

New child-state schema, not an ordinary E128 resume. Pulse prefixes have no
valid EpochCoverage queue representation: their exact cursor/counts are saved
separately. Only at the pulse boundary are canonical after-block queues restored.
"""
from __future__ import annotations
import contextlib, copy, hashlib, json, math, shutil, tempfile, time
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoConfig, OlmoForCausalLM
import e128_epoch_recovery as epoch

trainer, base, WB = epoch.trainer, epoch.trainer.base, epoch.WB
E128_SHA = "754dd5fca994b15839c38eccdd5f9f156dc747bfa3be8a2f2b7f3f61d65b505f"
PARENT_CONFIG = "8e70948181dde6fff44026456e97f9ffdf2aa002af7ce3a4f2e9bc15a683ea1f"
COMMON_START = hashlib.sha256(b"E131-common-token-batch-chain-v1").hexdigest()
PULSE_START = hashlib.sha256(b"E131-pulse-token-batch-chain-v1").hexdigest()


def chain(previous, payload):
    return hashlib.sha256(bytes.fromhex(previous) + payload).hexdigest()


def token_bytes(batch):
    values = batch.detach().cpu().numpy() if torch.is_tensor(batch) else np.asarray(batch)
    if values.min() < 0 or values.max() > 65535: raise ValueError("Pulse token IDs do not fit registered uint16")
    return values.astype("<u2", copy=False).tobytes()


def sources():
    result = epoch.verify_frozen_sources()
    if base.sha256_file(WB / "scripts/e128_epoch_recovery.py") != E128_SHA: raise ValueError("Frozen E128 source differs")
    return {**result, "e128_epoch_recovery.py": E128_SHA}


def parser():
    p = trainer.parser(); p.description = __doc__
    next(action for action in p._actions if action.dest == "mode").choices = ("prepare", "train", "self-test")
    p.set_defaults(steps=62500, max_train_tokens=512_000_000, max_hours=8., reference_data=None)
    p.add_argument("--branch", choices=("ordered", "permuted"))
    p.add_argument("--phase", choices=("pulse", "continue", "all"), default="all")
    p.add_argument("--parent-checkpoint", default="/tmp/xiang-moe-20261025/e128_seed0/snapshots/step004096.pt")
    p.add_argument("--parent-provenance")
    p.add_argument("--pulse-plan", default="/tmp/xiang-moe-20261025/e131_plan")
    p.add_argument("--parent-step", type=int, default=4096)
    p.add_argument("--pulse-steps", type=int, default=1024)
    p.add_argument("--pulse-lr", type=float, default=.000196608)
    p.add_argument("--late-step", type=int, default=61440)
    p.add_argument("--driver-sha256")
    return p


def parent(args, *, _self_test_only=False):
    frozen = sources()
    driver = base.sha256_file(__file__)
    if args.driver_sha256 and args.driver_sha256 != driver: raise ValueError("E131 driver SHA differs")
    args.driver_sha256 = driver
    args.parent_checkpoint, args.pulse_plan = str(Path(args.parent_checkpoint).resolve()), str(Path(args.pulse_plan).resolve())
    path = Path(args.parent_checkpoint)
    args.parent_provenance = str(Path(args.parent_provenance or path.parent.parent / "provenance.json").resolve())
    provenance = json.loads(Path(args.parent_provenance).read_text()); original = provenance["args"]
    for key in ("model", "data", "reference_data"):
        if getattr(args, key) is None: setattr(args, key, original[key])
    if _self_test_only:
        if (args.device, args.dtype) != ("cpu", "float32"): raise ValueError("_self_test_only requires tiny CPU execution")
    else:
        expected = {"parent_step": 4096, "pulse_steps": 1024, "pulse_lr": .000196608, "late_step": 61440,
                    "steps": 62500, "max_train_tokens": 512_000_000, "seq_len": 512, "batch_size": 16, "accum": 1,
                    "replacement": "moe", "seed": 0, "order_seed": 0, "layer": 9, "experts": 64,
                    "expert_size": 1024, "top_k": 8, "init_std": .02, "dtype": "bfloat16", "lr": 3e-4,
                    "warmup_fraction": .1, "weight_decay": .1, "lb_coef": .01, "z_coef": .001,
                    "grad_clip": 1., "max_hours": 8., "save_every": 1024, "eval_sequences": 512}
        if any(getattr(args, key) != value for key, value in expected.items()): raise ValueError("E131 registered protocol differs")
        protocol = json.loads(Path(args.parent_provenance).with_name("driver_protocol.json").read_text())
        if (original.get("driver_sha256") != E128_SHA or provenance["config_hash"] != PARENT_CONFIG
                or protocol.get("experiment") != "E128" or protocol.get("driver_sha256") != E128_SHA):
            raise ValueError("Parent is not the registered original E128 run")
    checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    expected = {"step": args.parent_step, "config_hash": provenance["config_hash"], "replacement_kind": "moe",
                "initial_tensor_sha256": provenance["initial_tensor_sha256"], "frozen_sample_hash": provenance["frozen_sample_hash"]}
    if any(checkpoint.get(key) != value for key, value in expected.items()): raise ValueError("Parent checkpoint metadata differs")
    if not checkpoint["optimizer"]["state"]: raise ValueError("Parent AdamW state is empty")
    steps = [float(state["step"]) for state in checkpoint["optimizer"]["state"].values()]
    if min(steps) < 1 or max(steps) > args.parent_step: raise ValueError("Parent optimizer counters exceed its update history")
    groups = checkpoint["optimizer"]["param_groups"]
    if any(not math.isclose(group["lr"], args.pulse_lr, rel_tol=1e-14, abs_tol=1e-16) for group in groups):
        raise ValueError("Pulse LR must equal the parent's saved last-update LR")
    for group in groups:
        if (tuple(group["betas"]), group["weight_decay"], group["eps"]) != ((.9, .95), args.weight_decay, 1e-8):
            raise ValueError("Parent optimizer hyperparameters differ")
    return checkpoint, provenance, {"checkpoint": args.parent_checkpoint, "checkpoint_sha256": base.sha256_file(path),
        "provenance_sha256": base.sha256_file(args.parent_provenance), "config_hash": checkpoint["config_hash"],
        "initial_tensor_sha256": checkpoint["initial_tensor_sha256"], "frozen_sample_hash": checkpoint["frozen_sample_hash"],
        "optimizer_steps": [min(steps), max(steps)], "saved_optimizer_lr": groups[0]["lr"],
        "elapsed_wall_seconds_not_charged_to_children": checkpoint["elapsed_wall_seconds"], "frozen_sources": frozen}


def dataset(args, provenance):
    data = epoch.EpochCoverageTokenData(args.data, args.seq_len, args.token_dtype)
    if data.provenance != provenance["data"]: raise ValueError("Parent data identity/content differs")
    reference = base.TokenData(args.reference_data, args.seq_len, args.token_dtype)
    trainer.validate_reference(data, reference)
    return data


def prepare(args, *, _self_test_only=False):
    checkpoint, provenance, identity = parent(args, _self_test_only=_self_test_only)
    folder = Path(args.pulse_plan)
    specification = {"experiment": "E131", "cpu_test": _self_test_only, "parent": identity,
                     "pulse_steps": args.pulse_steps, "pulse_lr": args.pulse_lr, "batch_size": args.batch_size,
                     "seq_len": args.seq_len, "driver_sha256": args.driver_sha256, "permutation_seed": 131}
    if folder.exists():
        manifest = load_plan(args)
        if manifest[0]["specification"] != specification: raise ValueError("Existing pulse plan has a different parent/protocol")
        return manifest[0]
    staging = folder.with_name(folder.name + ".partial"); staging.mkdir(parents=True, exist_ok=False)
    data, stream = dataset(args, provenance), trainer.SplitStream(args.order_seed)
    data.restore_coverage(copy.deepcopy(checkpoint["coverage"])); stream.load_state_dict(copy.deepcopy(checkpoint["stream_rng"]))
    states = {"parent": {"coverage": copy.deepcopy(data.coverage_state()), "stream_rng": copy.deepcopy(stream.state_dict())}}
    batches = np.lib.format.open_memmap(staging / "pulse_batches.npy", mode="w+", dtype="<u2",
                                       shape=(args.pulse_steps, args.batch_size, args.seq_len + 1))
    keys = np.empty((args.pulse_steps, args.batch_size, 2), dtype=np.int64); batch_hashes = []
    for cursor in range(args.pulse_steps):
        batch = data.train_batch(stream, args.batch_size); payload = token_bytes(batch)
        batches[cursor] = batch.numpy(); keys[cursor] = data.last_batch_keys
        batch_hashes.append(hashlib.sha256(payload).hexdigest())
    batches.flush(); del batches
    permutation = np.random.default_rng(131).permutation(args.pulse_steps)
    np.save(staging / "pulse_window_keys.npy", keys); np.save(staging / "permutation.npy", permutation)
    states["after"] = {"coverage": copy.deepcopy(data.coverage_state()), "stream_rng": copy.deepcopy(stream.state_dict())}
    torch.save(states, staging / "canonical_states.pt")
    ordered_multiset = base.digest_json(sorted(batch_hashes))
    permuted_multiset = base.digest_json(sorted(batch_hashes[int(index)] for index in permutation))
    if ordered_multiset != permuted_multiset: raise AssertionError("Pulse batch multisets differ")
    manifest = {"specification": specification, "batch_sha256": batch_hashes, "multiset_sha256": ordered_multiset,
                "permuted_multiset_sha256": permuted_multiset, "ordered_sequence_sha256": base.digest_json(batch_hashes),
                "permuted_sequence_sha256": base.digest_json([batch_hashes[int(i)] for i in permutation]),
                "canonical_after_draws": data.draws, "canonical_after_source_hash": data.source_schedule_hash,
                "files": {name: base.sha256_file(staging / name) for name in
                          ("pulse_batches.npy", "pulse_window_keys.npy", "permutation.npy", "canonical_states.pt")}}
    base.write_json(staging / "manifest.json", manifest)
    for path in staging.iterdir(): path.chmod(0o444)
    staging.rename(folder)
    return manifest


def load_plan(args):
    folder = Path(args.pulse_plan); manifest = json.loads((folder / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if base.sha256_file(folder / name) != expected: raise ValueError(f"Read-only pulse plan SHA differs: {name}")
    batches = np.load(folder / "pulse_batches.npy", mmap_mode="r", allow_pickle=False)
    keys = np.load(folder / "pulse_window_keys.npy", mmap_mode="r", allow_pickle=False)
    permutation = np.load(folder / "permutation.npy", allow_pickle=False)
    if batches.shape != (args.pulse_steps, args.batch_size, args.seq_len + 1) or keys.shape != (args.pulse_steps, args.batch_size, 2):
        raise ValueError("Pulse plan dimensions differ")
    if not np.array_equal(permutation, np.random.default_rng(131).permutation(args.pulse_steps)): raise ValueError("Pulse permutation differs")
    states = torch.load(folder / "canonical_states.pt", map_location="cpu", weights_only=False)
    return manifest, batches, keys, permutation, states


def pulse_prefix(states, keys, batches, order, cursor):
    counts = [value.copy() for value in states["parent"]["coverage"]["counts"]]
    source_hash, pulse_hash = states["parent"]["coverage"]["source_schedule_hash"], PULSE_START
    for index in order[:cursor]:
        rows = keys[index]
        source_hash = chain(source_hash, rows[:, 0].astype("<i8", copy=False).tobytes())
        pulse_hash = chain(pulse_hash, token_bytes(batches[index]))
        for file_index, window in rows: counts[int(file_index)][int(window)] += 1
    return counts, source_hash, pulse_hash


def train(args, *, _self_test_only=False):
    started = time.monotonic()
    checkpoint, parent_provenance, parent_identity = parent(args, _self_test_only=_self_test_only)
    manifest, pulse_batches, pulse_keys, permutation, states = load_plan(args)
    if manifest["specification"]["parent"] != parent_identity or manifest["specification"]["driver_sha256"] != args.driver_sha256:
        raise ValueError("Pulse plan belongs to a different parent/driver")
    if not args.output or not args.branch: raise ValueError("Training requires --output and --branch")
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    if (output / "checkpoint.pt").exists() and not args.resume: raise ValueError("Existing child checkpoint requires explicit --resume")
    if args.phase == "continue" and not args.resume: raise ValueError("Continuation requires an E131 child --resume")
    data = dataset(args, parent_provenance); stream = trainer.SplitStream(args.order_seed)
    pulse_end = args.parent_step + args.pulse_steps
    operational = {"mode", "phase", "output", "resume", "max_updates", "summary", "run_id", "init_registry", "diagnostic_sequences", "diagnostic_seed"}
    config_hash = base.digest_json({"experiment": "E131", "args": {k: v for k, v in vars(args).items() if k not in operational},
                                    "parent": parent_identity, "plan_sha256": base.sha256_file(Path(args.pulse_plan) / "manifest.json"),
                                    "pos_sha256": base.sha256_file(args.pos_items) if args.pos_items else None})
    previous = json.loads((output / "training_summary.json").read_text()) if args.resume and (output / "training_summary.json").exists() else {}
    prior_wall, step, cursor, common_hash = 0., args.parent_step, 0, COMMON_START
    order = np.arange(args.pulse_steps) if args.branch == "ordered" else permutation
    if args.resume:
        checkpoint = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
        if (checkpoint.get("experiment") != "E131" or checkpoint.get("schema") != "E131-child-v1"
                or checkpoint.get("config_hash") != config_hash or checkpoint.get("parent") != parent_identity
                or checkpoint.get("branch") != args.branch):
            raise ValueError("Resume is not the matching E131 child state")
        step, cursor, common_hash = checkpoint["step"], checkpoint["pulse_cursor"], checkpoint["common_input_hash"]
        if checkpoint.get("phase") != ("pulse" if step < pulse_end else "common"): raise ValueError("Child phase metadata differs")
        prior_wall = checkpoint["elapsed_wall_seconds"]
        if previous.get("step") == step and previous.get("config_hash") == config_hash:
            prior_wall = max(prior_wall, previous.get("elapsed_wall_seconds", 0.))
    if step < args.parent_step or step > args.steps or cursor != min(step - args.parent_step, args.pulse_steps):
        raise ValueError("Invalid child step/pulse cursor")
    if args.phase == "continue" and step < pulse_end: raise ValueError("Pulse incomplete: resume with --phase pulse/all")
    if args.phase == "pulse" and step > pulse_end: raise ValueError("Pulse phase cannot consume common-segment state")
    actual_counts, source_hash, pulse_hash = pulse_prefix(states, pulse_keys, pulse_batches, order, cursor)
    if step < pulse_end:
        data.restore_coverage(copy.deepcopy(states["parent"]["coverage"])); stream.load_state_dict(copy.deepcopy(states["parent"]["stream_rng"]))
        if args.resume:
            if checkpoint["epoch_coverage_valid"] or checkpoint["coverage"] is not None or checkpoint["stream_rng"] is not None:
                raise ValueError("A reordered pulse prefix must not claim valid Epoch queues")
            if (checkpoint["actual_source_schedule_hash"] != source_hash or checkpoint["pulse_input_hash"] != pulse_hash
                    or any(not np.array_equal(a, b) for a, b in zip(checkpoint["actual_pulse_counts"], actual_counts))):
                raise ValueError("Pulse prefix cursor/count/source/input proof differs")
    else:
        if not checkpoint.get("epoch_coverage_valid") or checkpoint.get("coverage") is None: raise ValueError("Common continuation needs valid epoch state")
        data.restore_coverage(checkpoint["coverage"]); stream.load_state_dict(checkpoint["stream_rng"])
        source_hash = data.source_schedule_hash
        if checkpoint["actual_source_schedule_hash"] != source_hash or checkpoint["pulse_input_hash"] != pulse_hash:
            raise ValueError("Resumed common state disagrees with its actual history proof")
        if data.draws != step * args.batch_size: raise ValueError("Resumed exposure count differs from absolute step")
    model = OlmoForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype), local_files_only=True,
                                         attn_implementation="sdpa").to(args.device).eval()
    model.config.use_cache = False; model.requires_grad_(False)
    original = model.model.layers[args.layer].mlp; prefix = f"model.layers.{args.layer}.mlp."
    frozen = base.sampled_parameter_hash(model, prefix)
    if frozen != parent_identity["frozen_sample_hash"]: raise ValueError("Child backbone differs from parent")
    replacement = trainer.build_replacement(model, args)
    initial_hash = trainer.tensor_state_hash(replacement.state_dict())
    if initial_hash != parent_identity["initial_tensor_sha256"]: raise ValueError("Original seed0 full initialization differs")
    replacement.load_state_dict(checkpoint["replacement_state"]); replacement = replacement.to(args.device)
    model.model.layers[args.layer].mlp = replacement; replacement.requires_grad_(True); replacement.train()
    trainable = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    if any(not name.startswith(prefix) for name, _ in trainable): raise RuntimeError("Unexpected trainable backbone")
    optimizer = torch.optim.AdamW([value for _, value in trainable], lr=args.lr, betas=(.9, .95), weight_decay=args.weight_decay, eps=1e-8)
    optimizer.load_state_dict(checkpoint["optimizer"])
    if not optimizer.state: raise ValueError("Inherited optimizer was reset")
    inherited_steps = [float(value["step"]) for value in optimizer.state.values()]
    saved_steps = [float(value["step"]) for value in checkpoint["optimizer"]["state"].values()]
    if inherited_steps != saved_steps or min(inherited_steps) < 1 or max(inherited_steps) > step:
        raise ValueError("Inherited per-parameter AdamW counters differ")
    base.restore_rng(checkpoint["rng"], args); del checkpoint
    provenance = {"experiment": "E131", "cpu_test": _self_test_only, "args": vars(args), "config_hash": config_hash,
        "run_id": args.run_id or output.name, "parent": parent_identity, "pulse_plan_sha256": base.sha256_file(Path(args.pulse_plan) / "manifest.json"),
        "initial_tensor_sha256": initial_hash, "frozen_sample_hash": frozen, "data": data.provenance,
        "optimizer_inheritance": {"nonempty": True, "step_range_on_load": [min(inherited_steps), max(inherited_steps)], "reset": False},
        "pulse_lr_scope": "Fixed parent last-update LR; common phase returns to original helper at each absolute step",
        "common_input_hash_definition": "sha256 chain from E131-common-token-batch-chain-v1; each complete little-endian uint16 token batch",
        "pulse_prefix_scope": "No Epoch coverage/stream state is claimed before the full reordered pulse is consumed"}
    held = data.fixed_windows("held", args.eval_sequences, args.eval_seed); provenance["held_window_hash"] = base.digest_json(held)
    base.write_json(output / "provenance.json", provenance); base.write_json(output / "driver_protocol.json", provenance)
    model.model.layers[args.layer].mlp = original
    items = base.read_pos(args.pos_items)
    dense_held = trainer.evaluate_windows(model, data, "held", held, args); dense_pos = base.evaluate_pos(model, items, args, {"target": None})
    model.model.layers[args.layer].mlp = replacement
    base.write_json(output / "dense_reference_held.json", dense_held); base.write_json(output / "dense_reference_pos.json", dense_pos)
    evaluations = previous.get("evaluations", []); elapsed = lambda: prior_wall + time.monotonic() - started

    def coverage():
        if step >= pulse_end: return data.coverage_summary()
        draws = sum(int(value.sum(dtype=np.uint64)) for value in actual_counts); unique = sum(int(np.count_nonzero(value)) for value in actual_counts)
        return {"drawn_windows": draws, "unique_windows": unique, "reused_windows": draws - unique,
                "source_schedule_hash": source_hash, "pulse_cursor": cursor, "epoch_coverage_valid": False}

    def measure():
        rows = trainer.evaluate_windows(model, data, "held", held, args); pos = base.evaluate_pos(model, items, args, {"target": None})
        value = {"step": step, "held": base.summarize(rows, iterations=args.bootstrap, available_sources=data.sources_available),
                 "held_delta_dense": base.summarize(rows, dense_held, args.bootstrap, data.sources_available),
                 "pos": base.pos_summary(pos), "pos_delta_dense": base.pos_summary(pos, dense_pos), "coverage": coverage()}
        base.emit("evaluation", branch=args.branch, step=step, held_nll=value["held"]["sequence"]["mean"])
        return value, rows, pos

    def save():
        if base.sampled_parameter_hash(model, prefix) != frozen: raise RuntimeError("Frozen backbone changed")
        state = replacement.state_dict()
        payload = {"schema": "E131-child-v1", "experiment": "E131", "step": step, "replacement_kind": "moe", "moe": state,
            "branch": args.branch, "phase": "pulse" if step < pulse_end else "common",
            "replacement_state": state, "optimizer": optimizer.state_dict(), "rng": base.rng_state(args), "parent": parent_identity,
            "config_hash": config_hash, "frozen_sample_hash": frozen, "initial_tensor_sha256": initial_hash,
            "epoch_coverage_valid": step >= pulse_end, "coverage": data.coverage_state() if step >= pulse_end else None,
            "stream_rng": stream.state_dict() if step >= pulse_end else None, "pulse_cursor": cursor,
            "actual_pulse_counts": actual_counts, "actual_source_schedule_hash": source_hash, "pulse_input_hash": pulse_hash,
            "common_input_hash": common_hash, "common_updates": max(0, step - pulse_end), "elapsed_wall_seconds": elapsed()}
        path = output / "checkpoint.pt"; temporary = path.with_suffix(".tmp"); torch.save(payload, temporary); temporary.replace(path)
        if step in (pulse_end, args.late_step, args.steps):
            destination = output / "snapshots" / f"step{step:06d}.pt"; destination.parent.mkdir(parents=True, exist_ok=True)
            partial = destination.with_suffix(".partial"); shutil.copy2(path, partial); partial.replace(destination)

    if not any(row["step"] == step for row in evaluations): evaluations.append(measure()[0])
    start_step, target, status = step, pulse_end if args.phase == "pulse" else args.steps, "running"
    timings = []
    if args.device.startswith("cuda"): torch.cuda.reset_peak_memory_stats(args.device)
    with (output / "train_steps.jsonl").open("a" if args.resume else "w") as log:
        while step < target:
            if args.max_updates and step - start_step >= args.max_updates: status = "invocation_update_limit"; break
            if elapsed() >= args.max_hours * 3600: status = "wall_time_limit"; break
            if (step + 1) * args.seq_len * args.batch_size > args.max_train_tokens: status = "token_limit"; break
            if args.device.startswith("cuda"): torch.cuda.synchronize(args.device)
            update_started = time.monotonic(); optimizer.zero_grad(set_to_none=True)
            in_pulse = step < pulse_end
            if in_pulse:
                index = int(order[cursor]); batch = torch.from_numpy(np.asarray(pulse_batches[index], dtype=np.int64))
                keys = pulse_keys[index]; source_hash = chain(source_hash, keys[:, 0].astype("<i8", copy=False).tobytes())
                pulse_hash = chain(pulse_hash, token_bytes(batch))
                for file_index, window in keys: actual_counts[int(file_index)][int(window)] += 1
                cursor += 1; rate = args.pulse_lr
            else:
                batch = data.train_batch(stream, args.batch_size); common_hash = chain(common_hash, token_bytes(batch))
                source_hash = data.source_schedule_hash; rate = base.lr_at(step, args)
            for group in optimizer.param_groups: group["lr"] = rate
            batch_hash = hashlib.sha256(token_bytes(batch)).hexdigest(); batch = batch.to(args.device)
            nll = base.token_nll(base.forward_logits(model, batch[:, :-1], args), batch[:, 1:]).mean()
            lb, z, loads, _ = replacement.losses_and_load(); objective = nll + args.lb_coef * lb + args.z_coef * z
            if not (output / "gradient_audit.json").exists(): base.write_json(output / "gradient_audit.json", base.gradient_audit(nll, lb, z, replacement))
            if not torch.isfinite(objective): raise RuntimeError("Nonfinite objective")
            objective.backward(); replacement.last_router_logits = None
            if any(value.grad is not None for name, value in model.named_parameters() if not name.startswith(prefix)):
                raise RuntimeError("Frozen backbone received gradients")
            norm = float(torch.nn.utils.clip_grad_norm_([value for _, value in trainable], args.grad_clip, error_if_nonfinite=True))
            optimizer.step(); step += 1
            if in_pulse and step == pulse_end:
                if any(not np.array_equal(a, b) for a, b in zip(actual_counts, states["after"]["coverage"]["counts"])):
                    raise RuntimeError("Completed pulse exposure multiset differs from canonical block")
                data.restore_coverage(copy.deepcopy(states["after"]["coverage"])); stream.load_state_dict(copy.deepcopy(states["after"]["stream_rng"]))
                data.source_schedule_hash = source_hash
            if coverage()["drawn_windows"] != step * args.batch_size: raise RuntimeError("Actual exposure count differs from update count")
            if args.device.startswith("cuda"): torch.cuda.synchronize(args.device)
            duration = time.monotonic() - update_started; timings.append(duration)
            record = {"step": step, "phase": "pulse" if in_pulse else "common", "lr": rate, "nll": float(nll.detach()),
                "lb_raw": float(lb.detach()), "z_raw": float(z.detach()), "gradient_norm_before_clip": norm,
                "seconds": duration, "tokens_per_second": args.seq_len * args.batch_size / duration, "expert_load": loads.cpu().tolist(),
                "pulse_cursor": cursor, "input_batch_sha256": batch_hash, "common_input_hash": common_hash, "coverage": coverage()}
            log.write(json.dumps(record, allow_nan=False) + "\n"); log.flush()
            base.emit("train", branch=args.branch, **{key: value for key, value in record.items() if key != "expert_load"})
            if args.eval_every and step % args.eval_every == 0:
                evaluations.append(measure()[0]); base.write_json(output / "training_summary.json", {"status": "running", "step": step, "config_hash": config_hash, "evaluations": evaluations})
            if (args.save_every and step % args.save_every == 0) or step == pulse_end: save()
    if step == target: status = "pulse_complete" if target == pulse_end else "complete"
    measured, rows, pos = measure()
    if not evaluations or evaluations[-1]["step"] != step: evaluations.append(measured)
    save()
    result = {"experiment": "E131", "status": status, "run_id": provenance["run_id"], "branch": args.branch, "step": step,
        "planned_steps": args.steps, "train_tokens": step * args.seq_len * args.batch_size,
        "child_train_tokens": (step - args.parent_step) * args.seq_len * args.batch_size,
        "config_hash": config_hash, "parent": parent_identity, "initial_tensor_sha256": initial_hash,
        "frozen_sample_hash_before": frozen, "frozen_sample_hash_after": base.sampled_parameter_hash(model, prefix),
        "pulse_cursor": cursor, "pulse_input_hash": pulse_hash, "common_input_hash": common_hash, "coverage": coverage(),
        "evaluations": evaluations, "elapsed_wall_seconds": elapsed(), "optimizer_inheritance": provenance["optimizer_inheritance"],
        "tokens_per_second_after_first": args.seq_len * args.batch_size / float(np.mean(timings[1:] or timings)) if timings else None}
    base.write_json(output / "training_summary.json", result)
    if args.summary: base.write_json(Path(args.summary), result)
    base.write_json(output / "final_held_sequences.json", rows); base.write_json(output / "final_pos.json", pos)
    return result


def self_test():
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e131_cpu_") as temporary:
        root = Path(temporary); rng = np.random.default_rng(131); train_files = []
        for index, windows in enumerate((5, 3)):
            path = root / f"train{index}.npy"; np.save(path, rng.integers(3, 64, windows * 9, dtype=np.uint16))
            train_files.append({"path": str(path), "source": f"s{index}", "file_id": str(index), "sampling_weight": .5})
        held_path = root / "held.npy"; np.save(held_path, rng.integers(3, 64, 90, dtype=np.uint16))
        manifest = root / "data.json"; base.write_json(manifest, {"train": train_files, "held": [{"path": str(held_path), "source": "s0", "file_id": "held"}]})
        torch.manual_seed(125)
        OlmoForCausalLM(OlmoConfig(vocab_size=64, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
            num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32, pad_token_id=1, eos_token_id=2,
            attention_dropout=0.)).save_pretrained(root / "model")
        common = ["--mode", "train", "--model", str(root / "model"), "--data", str(manifest), "--reference-data", str(manifest),
            "--device", "cpu", "--dtype", "float32", "--layer", "1", "--experts", "4", "--expert-size", "16", "--top-k", "2",
            "--seq-len", "8", "--batch-size", "2", "--steps", "10", "--max-train-tokens", "160", "--eval-sequences", "4",
            "--bootstrap", "30", "--pos-items", "", "--eval-every", "0", "--save-every", "2"]
        parent_args = trainer.parser().parse_args([*common, "--output", str(root / "parent"), "--max-updates", "2",
                                                  "--init-registry", str(root / "initializations.json")])
        with contextlib.ExitStack() as stack:
            stack.callback(setattr, trainer, "CoverageTokenData", trainer.CoverageTokenData)
            trainer.CoverageTokenData = epoch.EpochCoverageTokenData; trainer.run(parent_args)
        parent_path = root / "parent/checkpoint.pt"; parent_sha = base.sha256_file(parent_path)
        def make(name, branch="ordered", *extra):
            return parser().parse_args([*common, "--output", str(root / name), "--branch", branch,
                "--parent-checkpoint", str(parent_path), "--parent-provenance", str(root / "parent/provenance.json"),
                "--pulse-plan", str(root / "plan"), "--parent-step", "2", "--pulse-steps", "4", "--pulse-lr", ".0003", "--late-step", "8", *extra])
        plan = prepare(make("unused"), _self_test_only=True)
        before_plan_sha = base.sha256_file(root / "plan/manifest.json")
        def compare_checkpoints(first, second):
            result = trainer.compare_checkpoints(first, second)
            a, b = [torch.load(path, map_location="cpu", weights_only=False) for path in (first, second)]
            epoch.assert_queue_states_equal(a["coverage"], b["coverage"])
            assert a["optimizer"]["param_groups"] == b["optimizer"]["param_groups"]
            assert a["rng"]["python"] == b["rng"]["python"]
            assert a["rng"]["numpy"][0] == b["rng"]["numpy"][0] and a["rng"]["numpy"][2:] == b["rng"]["numpy"][2:]
            assert np.array_equal(a["rng"]["numpy"][1], b["rng"]["numpy"][1])
            return result
        full = train(make("full"), _self_test_only=True); train(make("duplicate"), _self_test_only=True)
        duplicate = compare_checkpoints(root / "full/checkpoint.pt", root / "duplicate/checkpoint.pt")
        pulse = train(make("split", "ordered", "--phase", "pulse"), _self_test_only=True)
        train(make("split", "ordered", "--phase", "continue", "--resume", str(root / "split/checkpoint.pt")), _self_test_only=True)
        split = compare_checkpoints(root / "full/checkpoint.pt", root / "split/checkpoint.pt")
        permuted = train(make("permuted", "permuted"), _self_test_only=True)
        partial = train(make("prefix", "permuted", "--max-updates", "2"), _self_test_only=True)
        prefix = torch.load(root / "prefix/checkpoint.pt", map_location="cpu", weights_only=False)
        assert not prefix["epoch_coverage_valid"] and prefix["coverage"] is prefix["stream_rng"] is None and prefix["pulse_cursor"] == 2
        try: train(make("prefix", "permuted", "--phase", "continue", "--resume", str(root / "prefix/checkpoint.pt")), _self_test_only=True)
        except ValueError: pass
        else: raise AssertionError("Incomplete pulse was accepted as ordinary continuation")
        train(make("prefix", "permuted", "--resume", str(root / "prefix/checkpoint.pt")), _self_test_only=True)
        prefix_resume = compare_checkpoints(root / "permuted/checkpoint.pt", root / "prefix/checkpoint.pt")
        train(make("permuted_split", "permuted", "--phase", "pulse"), _self_test_only=True)
        train(make("permuted_split", "permuted", "--phase", "continue", "--resume", str(root / "permuted_split/checkpoint.pt")), _self_test_only=True)
        permuted_split = compare_checkpoints(root / "permuted/checkpoint.pt", root / "permuted_split/checkpoint.pt")
        ordered_cp, permuted_cp = [torch.load(root / name / "checkpoint.pt", map_location="cpu", weights_only=False) for name in ("full", "permuted")]
        assert full["common_input_hash"] == permuted["common_input_hash"] and full["pulse_input_hash"] != permuted["pulse_input_hash"]
        assert full["coverage"]["source_schedule_hash"] != permuted["coverage"]["source_schedule_hash"]
        first, second = copy.deepcopy(ordered_cp["coverage"]), copy.deepcopy(permuted_cp["coverage"])
        second["source_schedule_hash"] = first["source_schedule_hash"]; epoch.assert_queue_states_equal(first, second)
        assert ordered_cp["stream_rng"] == permuted_cp["stream_rng"]
        logs = [[json.loads(line) for line in (root / name / "train_steps.jsonl").read_text().splitlines()] for name in ("full", "permuted")]
        for rows in logs: assert all(row["lr"] == .0003 for row in rows if row["phase"] == "pulse")
        assert [row["input_batch_sha256"] for row in logs[0] if row["phase"] == "common"] == [row["input_batch_sha256"] for row in logs[1] if row["phase"] == "common"]
        assert sorted(row["input_batch_sha256"] for row in logs[0] if row["phase"] == "pulse") == sorted(row["input_batch_sha256"] for row in logs[1] if row["phase"] == "pulse")
        assert ordered_cp["optimizer"]["param_groups"] == torch.load(root / "split/checkpoint.pt", weights_only=False)["optimizer"]["param_groups"]
        assert all(float(state["step"]) == 10 for state in ordered_cp["optimizer"]["state"].values())
        assert full["optimizer_inheritance"]["step_range_on_load"] == [2., 2.] and pulse["status"] == "pulse_complete" and partial["status"] == "invocation_update_limit"
        assert base.sha256_file(parent_path) == parent_sha and base.sha256_file(root / "plan/manifest.json") == before_plan_sha
        for step in (6, 8, 10): assert (root / "full/snapshots" / f"step{step:06d}.pt").exists()
        result = {"passed": True, "device": "cpu", "driver_sha256": base.sha256_file(__file__), "frozen_sources": sources(),
            "same_parent_ordered_duplicate": duplicate, "full_vs_separate_pulse_continue": split,
            "permuted_full_vs_separate_pulse_continue": permuted_split, "permuted_partial_pulse_resume": prefix_resume,
            "equal_pulse_multisets_different_order": plan["multiset_sha256"] == plan["permuted_multiset_sha256"],
            "constant_pulse_LR": True, "common_inputs_bit_identical": True, "actual_source_histories_not_forged_equal": True,
            "optimizer_inherited_nonempty_never_reset": True, "parent_and_readonly_plan_unchanged": True,
            "frozen_backbone_unchanged": full["frozen_sample_hash_before"] == full["frozen_sample_hash_after"], "no_GPU_or_real_model_assets": True}
        destination = WB / "results/e131/self_test.json"; destination.parent.mkdir(parents=True, exist_ok=True)
        base.write_json(destination, result); print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": self_test()
    else:
        try:
            result = prepare(args) if args.mode == "prepare" else train(args)
            print(json.dumps(result, indent=2), flush=True)
        except Exception as error:
            if args.output:
                Path(args.output).mkdir(parents=True, exist_ok=True)
                base.write_json(Path(args.output) / "failure.json", {"experiment": "E131", "error": f"{type(error).__name__}: {error}"})
            raise
