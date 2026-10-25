"""E130 fixed-budget cross-initialization runs; no scientific score gates.

Reuse the frozen E125 CE trainer and E128 epoch sampler. Real runs retain the
62500-update LR schedule even for --max-updates 64 followed by --resume.
Only --mode self-test uses tiny CPU assets; this script never launches jobs.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch
from transformers import OlmoConfig, OlmoForCausalLM

import e128_epoch_recovery as epoch

trainer = epoch.trainer
WB = epoch.WB
FROZEN_SOURCES = {**epoch.FROZEN_SOURCES,
                  "e128_epoch_recovery.py": "754dd5fca994b15839c38eccdd5f9f156dc747bfa3be8a2f2b7f3f61d65b505f"}


def verify_frozen_sources():
    actual = {name: trainer.base.sha256_file(Path(__file__).with_name(name)) for name in FROZEN_SOURCES}
    if actual != FROZEN_SOURCES:
        raise ValueError(f"Frozen source hashes differ: {actual}")
    return actual


def parser():
    p = epoch.parser()
    p.description = __doc__
    p.set_defaults(init_registry=str(WB / "results/e130/initializations.json"),
                   initial_reference=WB / "results/e128/initial_reference.json", retain_steps=[61440])
    p.add_argument("--expected-initial-tensor-sha256", help="Optional expected hash for this init seed")
    return p


def checked_register(args, specification, tensor_hash, run_id):
    if specification["frozen_sample_hash"] != args.expected_frozen_sample_hash:
        raise ValueError("Frozen backbone differs from the E128 anchor")
    if args.expected_initial_tensor_sha256 and tensor_hash != args.expected_initial_tensor_sha256:
        raise ValueError("Full initialization hash differs from the expected hash for this seed")
    specification = {**specification, "hidden_act": "silu", "norm_topk_prob": False,
                     "frozen_source_sha256": FROZEN_SOURCES}
    path = Path(args.init_registry)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Outer lock serializes the cross-seed check and E125's own atomic register.
    with path.with_suffix(".e130.lock").open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        registry = json.loads(path.read_text()) if path.exists() else {}
        without_seed = lambda spec: {k: v for k, v in spec.items() if k != "seed"}
        for record in registry.values():
            other = record["specification"]
            if (other["seed"] != specification["seed"] and without_seed(other) == without_seed(specification)
                    and record["tensor_sha256"] == tensor_hash):
                raise ValueError("Different initialization seeds produced identical full tensors")
        identity = epoch.OriginalRegisterInitialization(path, specification, tensor_hash, run_id)
    args.expected_initial_tensor_sha256 = tensor_hash
    return identity


def driver_run(args, *, cpu_test=False):
    frozen = verify_frozen_sources()
    actual_driver = trainer.base.sha256_file(__file__)
    if args.driver_sha256 and args.driver_sha256 != actual_driver:
        raise ValueError("Driver hash differs from --driver-sha256")
    args.driver_sha256 = actual_driver
    args.sampling_policy, args.window_rng_definition = epoch.POLICY, epoch.WINDOW_DEFINITION
    args.initial_reference = str(Path(args.initial_reference).resolve())
    reference = json.loads(Path(args.initial_reference).read_text())
    args.expected_frozen_sample_hash = reference["frozen_sample_hash_after"]
    if args.seed == 0:
        if args.expected_initial_tensor_sha256 and args.expected_initial_tensor_sha256 != reference["initial_tensor_sha256"]:
            raise ValueError("Seed0 expected initialization disagrees with the E128 anchor")
        args.expected_initial_tensor_sha256 = reference["initial_tensor_sha256"]
    if any(step < 1 for step in args.retain_steps):
        raise ValueError("Retained checkpoint steps must be positive")
    if not cpu_test:
        expected = {"steps": 62500, "seq_len": 512, "batch_size": 16, "accum": 1,
                    "max_train_tokens": 512_000_000, "replacement": "moe", "experts": 64,
                    "expert_size": 1024, "top_k": 8, "layer": 9, "lr": 3e-4,
                    "warmup_fraction": .1, "weight_decay": .1, "lb_coef": .01,
                    "z_coef": .001, "init_std": .02, "grad_clip": 1., "dtype": "bfloat16",
                    "max_hours": 8., "save_every": 1024, "retain_steps": [61440]}
        if any(getattr(args, key) != value for key, value in expected.items()):
            raise ValueError("E130 requires the registered fixed-budget E128 architecture/CE/optimizer protocol")
        if (args.seed, args.order_seed) not in {(i, 0) for i in range(5)} | {(0, 1)}:
            raise ValueError("E130 permits seeds0–4/order0 and seed0/order1 only")
    protocol = {"experiment": "E130", "cpu_test": cpu_test, "driver_sha256": actual_driver,
                "frozen_source_sha256": frozen, "sampling_policy": epoch.POLICY,
                "window_rng_definition": epoch.WINDOW_DEFINITION, "seed": args.seed,
                "order_seed": args.order_seed, "expected_frozen_sample_hash": args.expected_frozen_sample_hash,
                "retain_full_checkpoint_steps": args.retain_steps, "final_checkpoint_step": args.steps,
                "steps": args.steps, "target_tokens": args.steps * args.seq_len * args.batch_size * args.accum,
                "interpretation": "Finite fixed-budget cross-training comparison; no score-based eligibility gate."}

    def register(path, specification, tensor_hash, run_id):
        if Path(path) != Path(args.init_registry):
            raise ValueError("Unexpected initialization registry")
        identity = checked_register(args, specification, tensor_hash, run_id)
        trainer.base.write_json(Path(args.output) / "driver_protocol.json",
                                {**protocol, "initial_tensor_sha256": tensor_hash, "initialization_registry_id": identity})
        return identity

    def save(*values, **keywords):
        epoch.OriginalSaveCheckpoint(*values, **keywords)
        step = int(keywords["step"] if "step" in keywords else values[6])
        if step in args.retain_steps:
            path = Path(keywords["path"] if "path" in keywords else values[0])
            destination = path.parent / "snapshots" / f"step{step:06d}.pt"
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".partial")
            shutil.copy2(path, temporary)
            temporary.replace(destination)

    with contextlib.ExitStack() as stack:
        for name, replacement in (("CoverageTokenData", epoch.EpochCoverageTokenData),
                                  ("register_initialization", register), ("save_checkpoint", save)):
            stack.callback(setattr, trainer, name, getattr(trainer, name))
            setattr(trainer, name, replacement)
        return trainer.run(args)


def self_test():
    torch.set_num_threads(1)
    verify_frozen_sources()
    with tempfile.TemporaryDirectory(prefix="e130_cpu_") as directory:
        root = Path(directory)
        rng = np.random.default_rng(130)
        train = []
        for index, windows in enumerate((5, 3)):
            path = root / f"train{index}.npy"
            np.save(path, rng.integers(3, 64, windows * 9, dtype=np.uint16))
            train.append({"path": str(path), "source": f"s{index}", "file_id": f"train{index}",
                          "sampling_weight": (.6, .4)[index]})
        held = root / "held.npy"
        np.save(held, rng.integers(3, 64, 90, dtype=np.uint16))
        manifest = root / "data.json"
        trainer.base.write_json(manifest, {"train": train, "held": [{"path": str(held), "source": "s0", "file_id": "held"}]})
        torch.manual_seed(125)
        config = OlmoConfig(vocab_size=64, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
                            num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32,
                            pad_token_id=1, eos_token_id=2, attention_dropout=0.)
        OlmoForCausalLM(config).save_pretrained(root / "model")
        common = ["--mode", "train", "--model", str(root / "model"), "--data", str(manifest),
                  "--reference-data", str(manifest), "--init-registry", str(root / "initializations.json"),
                  "--initial-reference", str(root / "anchor.json"), "--device", "cpu", "--dtype", "float32",
                  "--layer", "1", "--experts", "4", "--expert-size", "16", "--top-k", "2", "--seq-len", "8",
                  "--batch-size", "2", "--steps", "5", "--eval-sequences", "4", "--bootstrap", "30",
                  "--pos-items", "", "--eval-every", "0", "--save-every", "2", "--diagnostic-sequences", "3",
                  "--retain-steps", "2"]
        make = lambda name, *extra: parser().parse_args([*common, "--output", str(root / name), *extra])
        model = OlmoForCausalLM.from_pretrained(root / "model", dtype=torch.float32).eval()
        hashes, sequences = {}, {}
        for seed in (0, 1, 2):
            args = make(f"seed{seed}", "--seed", str(seed))
            hashes[seed] = trainer.tensor_state_hash(trainer.build_replacement(model, args).state_dict())
            data, stream = epoch.EpochCoverageTokenData(manifest, 8), trainer.SplitStream(0)
            sequences[seed] = []
            for _ in range(12):
                data.train_batch(stream, 2)
                sequences[seed].extend(data.last_batch_keys)
        assert len(set(hashes.values())) == 3 and sequences[0] == sequences[1] == sequences[2]
        frozen = trainer.base.sampled_parameter_hash(model, "model.layers.1.mlp.")
        trainer.base.write_json(root / "anchor.json", {"initial_tensor_sha256": hashes[0], "frozen_sample_hash_after": frozen})
        full = driver_run(make("full"), cpu_test=True)
        driver_run(make("resume", "--max-updates", "2"), cpu_test=True)
        trainer.compare_checkpoints(root / "resume/checkpoint.pt", root / "resume/snapshots/step000002.pt")
        partial = torch.load(root / "resume/checkpoint.pt", map_location="cpu", weights_only=False)
        driver_run(make("resume", "--resume", str(root / "resume/checkpoint.pt")), cpu_test=True)
        check = trainer.compare_checkpoints(root / "full/checkpoint.pt", root / "resume/checkpoint.pt")
        first, second = [torch.load(root / name / "checkpoint.pt", map_location="cpu", weights_only=False)
                         for name in ("full", "resume")]
        epoch.assert_queue_states_equal(first["coverage"], second["coverage"])
        assert first["optimizer"]["param_groups"] == second["optimizer"]["param_groups"]
        snapshot = torch.load(root / "resume/snapshots/step000002.pt", map_location="cpu", weights_only=False)
        assert snapshot["step"] == 2 and snapshot["optimizer"]["state"] and snapshot["coverage"]["draws"] == 4
        epoch.assert_queue_states_equal(partial["coverage"], snapshot["coverage"])
        assert partial["stream_rng"] == snapshot["stream_rng"]
        assert sorted(p.name for p in (root / "resume/snapshots").iterdir()) == ["step000002.pt"]
        for seed in (1, 2):
            result = driver_run(make(f"seed{seed}", "--seed", str(seed)), cpu_test=True)
            assert result["initial_tensor_sha256"] == hashes[seed]
            assert result["frozen_sample_hash_before"] == result["frozen_sample_hash_after"] == frozen
            state = torch.load(root / f"seed{seed}/checkpoint.pt", map_location="cpu", weights_only=False)
            epoch.assert_queue_states_equal(first["coverage"], state["coverage"])
            assert first["stream_rng"] == state["stream_rng"]
        driver_run(make("seed1_resume", "--seed", "1", "--max-updates", "2"), cpu_test=True)
        driver_run(make("seed1_resume", "--seed", "1", "--resume", str(root / "seed1_resume/checkpoint.pt")), cpu_test=True)
        nonzero_check = trainer.compare_checkpoints(root / "seed1/checkpoint.pt", root / "seed1_resume/checkpoint.pt")
        nonzero_full, nonzero_resumed = [torch.load(root / name / "checkpoint.pt", map_location="cpu", weights_only=False)
                                         for name in ("seed1", "seed1_resume")]
        epoch.assert_queue_states_equal(nonzero_full["coverage"], nonzero_resumed["coverage"])
        assert nonzero_full["optimizer"]["param_groups"] == nonzero_resumed["optimizer"]["param_groups"]
        registry = json.loads((root / "initializations.json").read_text())
        spec = next(record["specification"] for record in registry.values() if record["specification"]["seed"] == 1)
        test_args = make("reject", "--seed", "1")
        test_args.expected_frozen_sample_hash = frozen
        for invalid_spec, invalid_hash in (({**spec, "frozen_sample_hash": "wrong"}, hashes[1]),
                                           (spec, "wrong"), ({**spec, "seed": 3}, hashes[1])):
            try:
                checked_register(test_args, invalid_spec, invalid_hash, "must-reject")
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid frozen/initialization/duplicate-seed hash accepted")
        protocol = json.loads((root / "full/driver_protocol.json").read_text())
        provenance = json.loads((root / "full/provenance.json").read_text())
        assert protocol["experiment"] == "E130" and protocol["driver_sha256"] == trainer.base.sha256_file(__file__)
        assert provenance["args"]["expected_initial_tensor_sha256"] == hashes[0] == full["initial_tensor_sha256"]
        assert full["frozen_sample_hash_before"] == full["frozen_sample_hash_after"] == frozen
        for extra in (("--driver-sha256", "wrong"), ("--expected-initial-tensor-sha256", "wrong")):
            try:
                driver_run(make("reject", *extra), cpu_test=True)
            except ValueError:
                pass
            else:
                raise AssertionError("Wrong driver hash or seed0 anchor accepted")
        result = {"passed": True, "device": "cpu", "driver_sha256": trainer.base.sha256_file(__file__),
                  "frozen_source_sha256": verify_frozen_sources(), "sampling_policy": epoch.POLICY,
                  "training_parameter_optimizer_RNG_counts_resume": check,
                  "seed1_parameter_optimizer_RNG_counts_resume": nonzero_check,
                  "training_queues_cursors_epochs_resume_exact": True, "seed_initial_hashes": hashes,
                  "seed0_full_init_matches_anchor": True, "init_seed_independent_source_window_sequence": True,
                  "retains_requested_snapshot_only_with_optimizer_RNG_queues": True,
                  "rejects_wrong_frozen_or_same_spec_init_or_duplicate_cross_seed_hash": True,
                  "rejects_wrong_driver_hash_or_seed0_anchor": True,
                  "frozen_backbone_unchanged": True, "no_real_training_or_model_assets": True}
        destination = WB / "results/e130/self_test.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        trainer.base.write_json(destination, result)
        print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test":
        self_test()
    else:
        try:
            driver_run(args)
        except Exception as error:
            if args.output:
                Path(args.output).mkdir(parents=True, exist_ok=True)
                trainer.base.write_json(Path(args.output) / "failure.json", {"type": type(error).__name__, "message": str(error)})
            raise
