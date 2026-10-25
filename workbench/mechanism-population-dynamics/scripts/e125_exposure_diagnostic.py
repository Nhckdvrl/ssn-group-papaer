"""E125: replay exact E123 exposure, then paired dense/final inference only.

Requires the preregistered E125 card. Raw per-sequence outputs and sampled
indices stay under /tmp; only the compact diagnostic summary enters results/.
"""
import argparse
import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from transformers import OlmoForCausalLM

from e123_frozen_moe import (TokenData, TensorMoE, digest_json, forward_logits,
                             sampled_parameter_hash, sha256_file, token_nll, write_json)


WB = Path(__file__).resolve().parents[1]


def replay(data, train_args, state):
    if int(state["step"]) != 3906 or train_args["batch_size"] != 16 or train_args["accum"] != 1:
        raise ValueError("Expected the registered 3906-update, batch16, accum1 E123 endpoint")
    sizes = np.array([r["windows"] for r in data.files["train"]], dtype=int)
    rng = np.random.default_rng(train_args["order_seed"])
    seen = set()
    exposures = np.zeros(int(sizes.sum()), dtype=np.int64)
    offsets = np.r_[0, np.cumsum(sizes)]
    for _ in range(int(state["step"])):
        for _ in range(train_args["accum"]):
            # Exactly TokenData.train_batch: one vector file-choice call, THEN
            # one scalar integer draw for each chosen file in original order.
            files = rng.choice(len(sizes), size=train_args["batch_size"], p=data.train_probabilities)
            for file_index in files:
                window_index = int(rng.integers(sizes[file_index]))
                key = (int(file_index), window_index)
                seen.add(key)
                exposures[offsets[file_index] + window_index] += 1
    replay_state = digest_json(rng.bit_generator.state)
    checkpoint_state = digest_json(state["stream_rng"])
    if replay_state != checkpoint_state:
        raise ValueError(f"Exposure replay RNG mismatch: {replay_state} != {checkpoint_state}")
    # Independently compare the manual drawing order with the actual helper on
    # several initial batches, including token identity and RNG final state.
    reference_rng = np.random.default_rng(train_args["order_seed"])
    manual_rng = np.random.default_rng(train_args["order_seed"])
    for _ in range(3):
        reference = data.train_batch(reference_rng, train_args["batch_size"]).numpy()
        choices = manual_rng.choice(len(sizes), size=train_args["batch_size"], p=data.train_probabilities)
        manual = np.stack([data.window("train", int(f), int(manual_rng.integers(sizes[f]))) for f in choices])
        if not np.array_equal(reference, manual) or digest_json(reference_rng.bit_generator.state) != digest_json(manual_rng.bit_generator.state):
            raise ValueError("Replay drawing order does not match TokenData.train_batch")
    all_windows = {(f, w) for f, size in enumerate(sizes) for w in range(int(size))}
    unseen = all_windows - seen
    return sorted(seen), sorted(unseen), {
        "endpoint_step": int(state["step"]), "batch_size": train_args["batch_size"],
        "accum": train_args["accum"], "order_seed": train_args["order_seed"],
        "rng_final_state_sha256": replay_state, "rng_matches_checkpoint": True,
        "initial_three_batches_match_real_TokenData_train_batch": True,
        "total_drawn_windows": int(exposures.sum()), "unique_seen_windows": len(seen),
        "unseen_windows": len(unseen), "pool_windows": len(all_windows),
        "unique_seen_fraction": len(seen) / len(all_windows),
        "repeat_fraction_of_draws": 1 - len(seen) / int(exposures.sum()),
        "max_window_exposures": int(exposures.max()),
        "seen_set_sha256": digest_json(sorted(seen)), "unseen_set_sha256": digest_json(sorted(unseen))}


def sample_windows(candidates, count, rng):
    if len(candidates) < count:
        raise ValueError(f"Only {len(candidates)} candidates, need {count}")
    chosen = rng.choice(len(candidates), count, replace=False)
    return sorted(candidates[int(i)] for i in chosen)


@torch.no_grad()
def score(model, data, split, windows, args, label):
    records = []
    started = time.monotonic()
    for batch_no, (batch, meta) in enumerate(data.iter_fixed(split, windows, args.batch_size)):
        batch = batch.to(args.device)
        logits = forward_logits(model, batch[:, :-1], args)
        losses = token_nll(logits, batch[:, 1:]).cpu()
        for values, metadata in zip(losses, meta):
            records.append({**metadata, "nll_sum": float(values.double().sum()), "tokens": int(values.numel())})
        if batch_no % 8 == 0:
            print(json.dumps({"stage": label, "batch": batch_no + 1, "sequences": len(records),
                              "elapsed_seconds": time.monotonic() - started}), flush=True)
    return records


def file_intervals(dense, moe, iterations, seed):
    keys = lambda rows: [(r["source"], r["file_id"], r["window"], r["tokens"]) for r in rows]
    if keys(dense) != keys(moe):
        raise ValueError("Teacher/final are not scored on identical sequence keys")
    grouped = {}
    for d, m in zip(dense, moe):
        key = (d["source"], d["file_id"])
        values = grouped.setdefault(key, np.zeros(3, dtype=np.float64))
        values += (d["nll_sum"], m["nll_sum"], d["tokens"])
    values = np.stack(list(grouped.values()))
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), (iterations, len(values)))
    totals = values[draws].sum(1)
    dboot, mboot = totals[:, 0] / totals[:, 2], totals[:, 1] / totals[:, 2]
    difference = mboot - dboot
    total = values.sum(0)
    delta = (total[1] - total[0]) / total[2]
    recovery_interval = np.quantile(difference, [.05, .95]).tolist()
    return {"dense_nll": float(total[0] / total[2]), "final_moe_nll": float(total[1] / total[2]),
            "final_minus_dense_nats": float(delta), "file_clusters": len(values),
            "n_sequences": len(dense), "n_scored_tokens": int(total[2]),
            "dense_file_bootstrap_ci95": np.quantile(dboot, [.025, .975]).tolist(),
            "final_file_bootstrap_ci95": np.quantile(mboot, [.025, .975]).tolist(),
            "paired_delta_file_bootstrap_ci95": np.quantile(difference, [.025, .975]).tolist(),
            "paired_delta_file_bootstrap_ci90": recovery_interval,
            "recovery_band_nats": [-.02, .02],
            "ci90_within_recovery_band": bool(recovery_interval[0] >= -.02 and recovery_interval[1] <= .02),
            "bootstrap_iterations": iterations, "bootstrap_seed": seed,
            "cluster_degenerate": len(values) < 2,
            "source_coverage": sorted({r["source"] for r in dense})}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, default=Path("/tmp/xiang-moe-20261025/olmo_dense"))
    p.add_argument("--checkpoint", type=Path, default=Path("/tmp/xiang-moe-20261025/e123_seed0/checkpoint.pt"))
    p.add_argument("--data", type=Path, default=WB / "results/e123/manifest.json")
    p.add_argument("--output", type=Path, default=WB / "results/e125/exposure_diagnostic.json")
    p.add_argument("--local-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e125_exposure"))
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--sample-count", type=int, default=512)
    p.add_argument("--bootstrap", type=int, default=1000)
    p.add_argument("--seed", type=int, default=125)
    p.add_argument("--replay-only", action="store_true")
    args = p.parse_args()
    torch.set_num_threads(4)
    trained_provenance = json.loads((args.checkpoint.parent / "provenance.json").read_text())
    train_args = trained_provenance["args"]
    data = TokenData(args.data, train_args["seq_len"], train_args["token_dtype"])
    if data.provenance != trained_provenance["data"]:
        raise ValueError("Current token manifest differs from E123 training provenance")
    # mmap keeps optimizer tensors untouched; only the module weights are read.
    state = torch.load(args.checkpoint, map_location="cpu", mmap=True, weights_only=False)
    seen, unseen, replay_result = replay(data, train_args, state)
    rng = np.random.default_rng(args.seed)
    plans = {"seen_train": ("train", sample_windows(seen, args.sample_count, rng)),
             "unseen_train": ("train", sample_windows(unseen, args.sample_count, rng)),
             "held": ("held", data.fixed_windows("held", args.sample_count, train_args["eval_seed"]))}
    if len(plans["held"][1]) != args.sample_count:
        raise ValueError("Not enough original held windows")
    result = {"experiment": "E125 exact-exposure diagnostic", "single_seed_only": True,
              "init_seed": train_args["seed"], "replay": replay_result,
              "diagnostic_sample_seed": args.seed, "scoring_dtype": "bfloat16 backbone/lm_head; E123 token_nll casts logits to fp32",
              "seq_len": train_args["seq_len"], "batch_size": train_args["batch_size"],
              "index_sha256": {key: digest_json(windows) for key, (_, windows) in plans.items()},
              "data_manifest_sha256": sha256_file(args.data),
              "training_script_sha256": trained_provenance["script_sha256"],
              "current_helper_script_sha256": sha256_file(Path(__file__).with_name("e123_frozen_moe.py")),
              "diagnostic_script_sha256": sha256_file(__file__),
              "raw_output_location": str(args.local_output),
              "no_training_or_checkpoint_selection": True}
    args.local_output.mkdir(parents=True, exist_ok=True)
    write_json(args.local_output / "window_plan.json", {key: {"split": split, "windows": windows} for key, (split, windows) in plans.items()})
    print(json.dumps({"replay_verified": replay_result, "index_sha256": result["index_sha256"]}), flush=True)
    if args.replay_only:
        write_json(args.local_output / "replay_verification.json", result)
        return
    if args.device.startswith("cuda"):
        torch.cuda.set_device(args.device)
        torch.cuda.reset_peak_memory_stats(args.device)
    started = time.monotonic()
    model = OlmoForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16,
                                          local_files_only=True, attn_implementation="sdpa").to(args.device).eval()
    model.config.use_cache = False
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    scoring_args = SimpleNamespace(device=args.device, dtype="bfloat16", batch_size=16)
    prefix = f"model.layers.{train_args['layer']}.mlp."
    backbone_hash = sampled_parameter_hash(model, prefix)
    if backbone_hash != state["frozen_sample_hash"]:
        raise ValueError("Original frozen backbone does not match the E123 checkpoint")
    original_dense_hash = sampled_parameter_hash(model)
    results = {"dense": {}, "final_moe": {}}
    for name, (split, windows) in plans.items():
        results["dense"][name] = score(model, data, split, windows, scoring_args, "dense_" + name)
        write_json(args.local_output / f"dense_{name}_sequences.json", results["dense"][name])
    dense = model.model.layers[train_args["layer"]].mlp
    if sampled_parameter_hash(model) != original_dense_hash:
        raise ValueError("Dense inference changed parameters")
    moe = TensorMoE(model.config.hidden_size, train_args["expert_size"], train_args["experts"],
                    train_args["top_k"], train_args["init_std"])
    moe.load_state_dict(state["moe"])
    moe = moe.to(args.device).eval()
    for parameter in moe.parameters():
        parameter.requires_grad_(False)
    model.model.layers[train_args["layer"]].mlp = moe
    loaded_moe_hash = sampled_parameter_hash(moe)
    for name, (split, windows) in plans.items():
        results["final_moe"][name] = score(model, data, split, windows, scoring_args, "final_" + name)
        write_json(args.local_output / f"final_{name}_sequences.json", results["final_moe"][name])
    if sampled_parameter_hash(model, prefix) != backbone_hash or sampled_parameter_hash(moe) != loaded_moe_hash:
        raise ValueError("Inference changed frozen or MoE parameters")
    result["groups"] = {name: file_intervals(results["dense"][name], results["final_moe"][name], args.bootstrap, args.seed + i)
                         for i, name in enumerate(plans)}
    delta = {name: row["final_minus_dense_nats"] for name, row in result["groups"].items()}
    result["diagnostic_point_contrasts_only"] = {
        "unseen_minus_seen_paired_teacher_gap_nats": delta["unseen_train"] - delta["seen_train"],
        "held_minus_seen_paired_teacher_gap_nats": delta["held"] - delta["seen_train"]}
    result.update({"backbone_sample_hash_before_after": backbone_hash, "original_dense_sample_hash": original_dense_hash,
                   "loaded_final_moe_sample_hash_before_after": loaded_moe_hash,
                   "sample_hash_note": "E123 33 deterministic entries per tensor, not full checkpoint hash",
                   "elapsed_seconds": time.monotonic() - started,
                   "gpu_name": torch.cuda.get_device_name(args.device) if args.device.startswith("cuda") else None,
                   "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(args.device) if args.device.startswith("cuda") else None,
                   "interpretation_limit": "Paired teacher-relative exposure diagnostic in one seed. Seen/unseen are uniform samples of distinct fixed pool windows, not independent corpus files or randomized exposure treatment. Prefix-pool and old E123 scoring precision limitations remain; no automatic overfitting verdict."})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, result)
    print(json.dumps({"summary": str(args.output), "groups": result["groups"]}, indent=2), flush=True)
    model.model.layers[train_args["layer"]].mlp = dense


if __name__ == "__main__":
    main()
