"""E128 CE recovery driver; the E125/E123/E124 source files remain frozen.

Window RNG child1 creates per-file permutations lazily; a file cycles only after
its full queue is consumed. Source RNG child0 and the CE optimizer are unchanged.
Real protocol: 62500 updates x batch16 x seq512 = 512M target tokens, max8h.
Only --mode self-test runs tiny CPU models. This file never launches a GPU job
unless explicitly invoked with --mode train after reading the E128 card.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch
from transformers import OlmoConfig, OlmoForCausalLM

import e125_coverage_control as trainer


WB = Path(__file__).resolve().parents[1]
POLICY = "per_file_random_permutation_without_replacement_until_exhausted_then_cycle_v1"
WINDOW_DEFINITION = "SeedSequence(order_seed).spawn(2): child0=file-choice batches; child1=lazy per-file full-window permutations, consumed in source-request order; no scalar window draws"
FROZEN_SOURCES = {
    "e125_coverage_control.py": "7bda110b67453f9642ec9e100b9e308fc7d0583abfe98876980184e28044b0b1",
    "e123_frozen_moe.py": "f874f0675ab4423173a542c6765d2504aab33cd2a28c7aa412b71f9308936c80",
    "e124_functional_capture.py": "4b4f861990e3e17dd6dd3fb98bb4aa69b6ee488d63d75b871276ef257d68dbae",
}
OriginalCoverageTokenData = trainer.CoverageTokenData
OriginalRegisterInitialization = trainer.register_initialization
OriginalSaveCheckpoint = trainer.save_checkpoint


def verify_frozen_sources():
    actual = {}
    for name, expected in FROZEN_SOURCES.items():
        actual[name] = trainer.base.sha256_file(Path(__file__).with_name(name))
        if actual[name] != expected:
            raise ValueError(f"Frozen source hash differs: {name}: {actual[name]} != {expected}")
    return actual


class EpochCoverageTokenData(OriginalCoverageTokenData):
    """Full per-file permutations with checkpointed queues and epoch cursors."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window_queues = [np.empty(0, dtype=np.int64) for _ in self.window_counts]
        self.window_cursors = [0] * len(self.window_counts)
        # -1 means no queue has been generated; 0 is the first pass.
        self.window_epoch_indices = [-1] * len(self.window_counts)

    def train_batch(self, rng, size):
        chosen = rng.source.choice(len(self.files["train"]), size=size, p=self.train_probabilities)
        self.source_schedule_hash = hashlib.sha256(
            bytes.fromhex(self.source_schedule_hash) + np.asarray(chosen, dtype="<i8").tobytes()).hexdigest()
        rows, keys = [], []
        for index in chosen:
            index = int(index)
            if self.window_cursors[index] == len(self.window_queues[index]):
                self.window_queues[index] = rng.window.permutation(len(self.window_counts[index]))
                self.window_cursors[index] = 0
                self.window_epoch_indices[index] += 1
            window = int(self.window_queues[index][self.window_cursors[index]])
            self.window_cursors[index] += 1
            rows.append(self.window("train", index, window))
            keys.append((index, window))
            counts = self.window_counts[index]
            if counts[window] == 0:
                self.unique += 1
            counts[window] += 1
            self.draws += 1
        self.last_batch_keys = keys
        return torch.from_numpy(np.stack(rows))

    def coverage_state(self):
        return {**super().coverage_state(), "sampling_policy": POLICY,
                "window_queues": self.window_queues,
                "window_cursors": self.window_cursors,
                "window_epoch_indices": self.window_epoch_indices}

    def restore_coverage(self, state):
        if state.get("sampling_policy") != POLICY:
            raise ValueError("Resume is not an E128 per-file permutation checkpoint")
        super().restore_coverage(state)
        queues = [np.asarray(q, dtype=np.int64) for q in state["window_queues"]]
        cursors = [int(i) for i in state["window_cursors"]]
        epochs = [int(i) for i in state["window_epoch_indices"]]
        if any(len(values) != len(self.window_counts) for values in (queues, cursors, epochs)):
            raise ValueError("Resume has a different number of window queues/cursors/epochs")
        for counts, queue, cursor, epoch in zip(self.window_counts, queues, cursors, epochs):
            size = len(counts)
            if queue.ndim != 1 or not 0 <= cursor <= len(queue):
                raise ValueError("Invalid queue shape/cursor")
            if not len(queue):
                if epoch != -1 or cursor != 0 or counts.any():
                    raise ValueError("Uninitialized queue has exposures or a noninitial cursor/epoch")
                continue
            if len(queue) != size or epoch < 0 or not np.array_equal(np.sort(queue), np.arange(size)):
                raise ValueError("Saved queue is not a complete window permutation")
            expected = np.full(size, epoch, dtype=np.uint64)
            expected[queue[:cursor]] += 1
            if not np.array_equal(expected, counts):
                raise ValueError("Queue/epoch prefix disagrees with saved exposure counts")
        self.window_queues, self.window_cursors, self.window_epoch_indices = queues, cursors, epochs

    def coverage_summary(self, per_file=False):
        result = super().coverage_summary(per_file)
        result.update({"sampling_policy": POLICY,
                       "initialized_window_queues": sum(i >= 0 for i in self.window_epoch_indices),
                       "files_entering_repeat_epoch": sum(i >= 1 for i in self.window_epoch_indices)})
        if per_file:
            for row, queue, cursor, epoch in zip(result["files"], self.window_queues,
                                                  self.window_cursors, self.window_epoch_indices):
                row.update({"window_epoch_index": epoch, "next_queue_cursor": cursor,
                            "permutation_sha256": hashlib.sha256(queue.astype("<i8", copy=False).tobytes()).hexdigest()})
        return result


def parser():
    p = trainer.parser()
    p.description = __doc__
    p.set_defaults(steps=62500, max_train_tokens=512_000_000, max_hours=8.)
    p.add_argument("--driver-sha256", help="Optional expected hash of this driver; an incorrect value is rejected")
    p.add_argument("--sampling-policy", choices=(POLICY,), default=POLICY)
    p.add_argument("--initial-reference", type=Path, default=WB / "results/e125/M-cover.json",
                   help="Original E125 M-cover summary supplying full init and frozen-backbone hashes")
    p.add_argument("--retain-steps", type=lambda text: sorted(set(int(s) for s in text.split(",") if s)),
                   default=[1024, 4096, 61440], help="Retain full local snapshots only when the existing save hook visits these steps")
    return p


def driver_run(args, *, cpu_test=False):
    frozen = verify_frozen_sources()
    actual_driver = trainer.base.sha256_file(__file__)
    if args.driver_sha256 and args.driver_sha256 != actual_driver:
        raise ValueError("Driver hash differs from --driver-sha256")
    args.driver_sha256 = actual_driver
    args.sampling_policy = POLICY
    args.window_rng_definition = WINDOW_DEFINITION
    args.initial_reference = str(Path(args.initial_reference).resolve())
    reference = json.loads(Path(args.initial_reference).read_text())
    args.expected_initial_tensor_sha256 = reference["initial_tensor_sha256"]
    args.expected_frozen_sample_hash = reference["frozen_sample_hash_after"]
    if any(step < 1 for step in args.retain_steps):
        raise ValueError("Retained checkpoint steps must be positive")
    if not cpu_test:
        if (args.steps, args.seq_len, args.batch_size, args.accum, args.max_train_tokens) != (62500, 512, 16, 1, 512_000_000):
            raise ValueError("E128 requires the fixed 62500-update/512M-target-token schedule")
        if args.replacement != "moe" or (args.experts, args.expert_size, args.top_k, args.layer) != (64, 1024, 8, 9):
            raise ValueError("E128 requires the original L9 fine-grained MoE")
        if (args.seed, args.order_seed, args.lr, args.warmup_fraction, args.weight_decay, args.lb_coef,
            args.z_coef, args.init_std, args.grad_clip, args.dtype, args.max_hours) != (0, 0, 3e-4, .1, .1, .01, .001, .02, 1., "bfloat16", 8.):
            raise ValueError("E128 changes budget/sampling only; the registered CE/optimizer/seed/8h contract differs")
        if args.save_every != 1024 or args.retain_steps != [1024, 4096, 61440]:
            raise ValueError("E128 retains the existing 1024-step save cadence and registered snapshot steps")
    protocol = {"experiment": "E128", "cpu_test": cpu_test, "driver_sha256": actual_driver,
                "frozen_source_sha256": frozen, "sampling_policy": POLICY,
                "window_rng_definition": WINDOW_DEFINITION,
                "expected_initial_tensor_sha256": args.expected_initial_tensor_sha256,
                "expected_frozen_sample_hash": args.expected_frozen_sample_hash,
                "retain_full_checkpoint_steps": args.retain_steps,
                "snapshot_scope": "local output/snapshots only; full optimizer, RNG and exposure queues; no additional save calls or analyses",
                "steps": args.steps, "target_tokens": args.steps * args.seq_len * args.batch_size * args.accum,
                "interpretation": "Budget, schedule and sampling change together relative to E125; this tests a more sufficient CE protocol, not a sampling-only causal effect."}
    if args.output:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        trainer.base.write_json(Path(args.output) / "driver_protocol.json", protocol)

    def checked_register(path, specification, tensor_hash, run_id):
        if tensor_hash != args.expected_initial_tensor_sha256:
            raise ValueError("Full initial MoE tensor hash differs from the original E125 reference")
        if specification["frozen_sample_hash"] != args.expected_frozen_sample_hash:
            raise ValueError("Frozen backbone differs from the original E125 reference")
        return OriginalRegisterInitialization(path, specification, tensor_hash, run_id)

    def retained_save(*values, **keywords):
        OriginalSaveCheckpoint(*values, **keywords)
        step = int(keywords["step"] if "step" in keywords else values[6])
        if step in args.retain_steps:
            path = Path(keywords["path"] if "path" in keywords else values[0])
            destination = path.parent / "snapshots" / f"step{step:06d}.pt"
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".partial")
            shutil.copy2(path, temporary)
            temporary.replace(destination)

    # Only process-local class/function dispatch changes; no old source is edited.
    with contextlib.ExitStack() as stack:
        previous_data, previous_register, previous_save = trainer.CoverageTokenData, trainer.register_initialization, trainer.save_checkpoint
        trainer.CoverageTokenData, trainer.register_initialization = EpochCoverageTokenData, checked_register
        trainer.save_checkpoint = retained_save
        stack.callback(setattr, trainer, "CoverageTokenData", previous_data)
        stack.callback(setattr, trainer, "register_initialization", previous_register)
        stack.callback(setattr, trainer, "save_checkpoint", previous_save)
        return trainer.run(args)


def assert_queue_states_equal(first, second):
    for key in ("sampling_policy", "window_cursors", "window_epoch_indices", "draws", "unique", "source_schedule_hash"):
        if first[key] != second[key]:
            raise AssertionError(f"Queue resume differs: {key}")
    for key in ("window_queues", "counts"):
        if len(first[key]) != len(second[key]) or any(not np.array_equal(a, b) for a, b in zip(first[key], second[key])):
            raise AssertionError(f"Queue resume arrays differ: {key}")


def self_test():
    torch.set_num_threads(1)
    verify_frozen_sources()
    with tempfile.TemporaryDirectory(prefix="e128_cpu_") as tmp:
        root = Path(tmp)
        rng = np.random.default_rng(128)
        train = []
        for index, windows in enumerate((5, 3)):
            path = root / f"train{index}.npy"
            np.save(path, rng.integers(3, 64, windows * 9, dtype=np.uint16))
            train.append({"path": str(path), "source": f"s{index}", "file_id": f"train{index}",
                          "sampling_weight": (.6, .4)[index]})
        held_path = root / "held.npy"
        np.save(held_path, rng.integers(3, 64, 90, dtype=np.uint16))
        held = [{"path": str(held_path), "source": "s0", "file_id": "held"}]
        manifest = root / "data.json"
        trainer.base.write_json(manifest, {"train": train, "held": held})
        one_file = root / "one_file.json"
        trainer.base.write_json(one_file, {"train": [{**train[0], "sampling_weight": 1.}], "held": held})
        one = EpochCoverageTokenData(one_file, 8)
        stream = trainer.SplitStream(0)
        first_pass = []
        for _ in range(5):
            one.train_batch(stream, 1)
            first_pass.append(one.last_batch_keys[0][1])
        assert sorted(first_pass) == list(range(5)) and one.window_epoch_indices == [0] and one.window_cursors == [5]
        assert np.array_equal(one.window_counts[0], np.ones(5))
        one.train_batch(stream, 1)
        assert one.window_epoch_indices == [1] and one.window_cursors == [1] and one.unique == 5
        assert one.draws == 6 and int(one.window_counts[0].max()) == 2

        epoch, replacement = EpochCoverageTokenData(manifest, 8), OriginalCoverageTokenData(manifest, 8)
        epoch_rng, replacement_rng = trainer.SplitStream(0), trainer.SplitStream(0)
        for _ in range(4):
            epoch.train_batch(epoch_rng, 3)
            replacement.train_batch(replacement_rng, 3)
            assert [f for f, _ in epoch.last_batch_keys] == [f for f, _ in replacement.last_batch_keys]
        assert epoch.source_schedule_hash == replacement.source_schedule_hash
        resumed = EpochCoverageTokenData(manifest, 8)
        resumed.restore_coverage(copy.deepcopy(epoch.coverage_state()))
        resumed_rng = trainer.SplitStream(999)
        resumed_rng.load_state_dict(copy.deepcopy(epoch_rng.state_dict()))
        for _ in range(10):
            epoch.train_batch(epoch_rng, 3)
            resumed.train_batch(resumed_rng, 3)
            assert epoch.last_batch_keys == resumed.last_batch_keys
        assert epoch_rng.state_dict() == resumed_rng.state_dict()
        assert_queue_states_equal(epoch.coverage_state(), resumed.coverage_state())
        corrupt = copy.deepcopy(epoch.coverage_state())
        corrupt["window_cursors"][0] = (corrupt["window_cursors"][0] + 1) % (len(corrupt["window_queues"][0]) + 1)
        try:
            EpochCoverageTokenData(manifest, 8).restore_coverage(corrupt)
            raise AssertionError("A queue/count mismatch was accepted")
        except ValueError:
            pass

        torch.manual_seed(125)
        config = OlmoConfig(vocab_size=64, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
                            num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32,
                            pad_token_id=1, eos_token_id=2, attention_dropout=0.)
        OlmoForCausalLM(config).save_pretrained(root / "model")
        common = ["--mode", "train", "--model", str(root / "model"), "--data", str(manifest),
                  "--reference-data", str(manifest), "--init-registry", str(root / "initializations.json"),
                  "--initial-reference", str(root / "initial_reference.json"), "--device", "cpu", "--dtype", "float32",
                  "--seed", "0", "--order-seed", "0", "--layer", "1", "--experts", "4", "--expert-size", "16",
                  "--top-k", "2", "--seq-len", "8", "--batch-size", "2", "--steps", "5", "--eval-sequences", "4",
                  "--bootstrap", "30", "--pos-items", "", "--eval-every", "0", "--save-every", "0",
                  "--diagnostic-sequences", "3", "--retain-steps", "2,5"]
        dummy_args = parser().parse_args([*common, "--output", str(root / "dummy")])
        original_model = OlmoForCausalLM.from_pretrained(root / "model", dtype=torch.float32).eval()
        original_init = trainer.tensor_state_hash(trainer.build_replacement(original_model, dummy_args).state_dict())
        frozen = trainer.base.sampled_parameter_hash(original_model, "model.layers.1.mlp.")
        trainer.base.write_json(root / "initial_reference.json", {"initial_tensor_sha256": original_init,
                                                                 "frozen_sample_hash_after": frozen})
        full = driver_run(parser().parse_args([*common, "--output", str(root / "full")]), cpu_test=True)
        driver_run(parser().parse_args([*common, "--output", str(root / "resume"), "--max-updates", "2"]), cpu_test=True)
        driver_run(parser().parse_args([*common, "--output", str(root / "resume"), "--resume", str(root / "resume/checkpoint.pt")]), cpu_test=True)
        check = trainer.compare_checkpoints(root / "full/checkpoint.pt", root / "resume/checkpoint.pt")
        first = torch.load(root / "full/checkpoint.pt", map_location="cpu", weights_only=False)
        second = torch.load(root / "resume/checkpoint.pt", map_location="cpu", weights_only=False)
        assert_queue_states_equal(first["coverage"], second["coverage"])
        assert first["stream_rng"] == second["stream_rng"]
        retained = torch.load(root / "resume/snapshots/step000005.pt", map_location="cpu", weights_only=False)
        assert retained["step"] == 5 and (root / "resume/snapshots/step000002.pt").exists()
        assert retained["optimizer"]["state"] and retained["stream_rng"] == second["stream_rng"]
        assert_queue_states_equal(retained["coverage"], second["coverage"])
        assert full["initial_tensor_sha256"] == original_init
        provenance = json.loads((root / "full/provenance.json").read_text())
        assert provenance["args"]["driver_sha256"] == trainer.base.sha256_file(__file__)
        assert provenance["args"]["sampling_policy"] == POLICY
        assert provenance["args"]["window_rng_definition"] == WINDOW_DEFINITION
        result = {"passed": True, "device": "cpu", "driver_sha256": trainer.base.sha256_file(__file__),
                  "frozen_sources": verify_frozen_sources(), "sampling_policy": POLICY,
                  "first_file_pass_no_repeats": True, "cycles_only_after_exhaustion": True,
                  "same_source_schedule_as_original_E125": True, "rejects_queue_count_mismatch": True,
                  "standalone_queue_cursor_epoch_RNG_counts_resume_exact": True,
                  "training_parameter_optimizer_RNG_counts_resume": check,
                  "training_queues_cursors_epochs_source_chain_resume_exact": True,
                  "retained_full_snapshots_preserve_optimizer_RNG_queues": True,
                  "full_initial_hash_equal_to_original_builder": original_init,
                  "frozen_backbone_unchanged": full["frozen_sample_hash_before"] == full["frozen_sample_hash_after"],
                  "no_real_training_or_model_assets": True}
        destination = WB / "results/e128/self_test.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        trainer.base.write_json(destination, result)
        print(json.dumps({"self_test": str(destination), **result}, indent=2), flush=True)


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
