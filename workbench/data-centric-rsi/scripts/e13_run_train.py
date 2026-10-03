"""Launch one independent E13 branch using the unmodified E12 vendor trainer.

Dry-run performs CPU identity, processor and sampler checks. The child adds only
observers around Trainer initialization and get_batch_samples: no loss, data,
sampler, model forward or optimizer implementation is replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

from e12_run_train import (
    EXPECTED_DATA_REVISION, EXPECTED_MODEL_REVISION, EXPECTED_VENDOR_SHA,
    TRAIN_SCRIPT, VENDOR_ROOT, gpu_free_mb, sha256,
)

ACTIONS = ("replay", "fresh_selected", "fresh_law")
BUDGET, STEPS, LABELS, SEED = 10000, 625, 549353, 29
INIT_SHAS = (
    "78ce5928df765de8cc46daf9034a8ad093ddd4e3e7535ac8d7fa1a171023aca0",
    "8ad6fcd2a8f28b421bc49e9d15d809c233363a3c36c09cc7d8118b95e1960156",
    "24ae222cdbe3b57e692567df56829be975ea22d1f4899a111635f74fd834dc79",
)
VERSIONS = {"transformers": "4.57.6", "liger-kernel": "0.7.0",
            "accelerate": "1.13.0", "torch": "2.8.0"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def bound_path(value: str, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def digest_json(value) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def file_manifest(directory: Path) -> list[dict]:
    return [{"path": str(p.relative_to(directory)), "bytes": p.stat().st_size,
             "sha256": sha256(p)} for p in sorted(directory.rglob("*")) if p.is_file()]


def load_vendor():
    spec = importlib.util.spec_from_file_location("e13_pinned_trainer", TRAIN_SCRIPT)
    require(spec is not None and spec.loader is not None, "Cannot import vendor trainer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def package_audit() -> dict:
    from accelerate import Accelerator
    from accelerate.data_loader import SeedableRandomSampler, prepare_data_loader
    from transformers import Trainer
    from transformers.trainer_pt_utils import AcceleratorConfig
    from liger_kernel.transformers.model.loss_utils import LigerForCausalLMLoss
    from liger_kernel.transformers.model.llava import lce_forward

    versions = {name: importlib.metadata.version(name) for name in VERSIONS}
    require(all(versions[n].split("+")[0] == v for n, v in VERSIONS.items()),
            f"Runtime differs from E12: {versions}")
    sources = {}
    for name, obj in {
        "Trainer": Trainer, "Accelerator": Accelerator,
        "SeedableRandomSampler": SeedableRandomSampler,
        "prepare_data_loader": prepare_data_loader,
        "LigerForCausalLMLoss": LigerForCausalLMLoss,
        "LigerLlavaForward": lce_forward,
    }.items():
        path = Path(inspect.getfile(obj))
        sources[name] = {"path": str(path), "sha256": sha256(path)}
    require(AcceleratorConfig().use_seedable_sampler is True,
            "Default Trainer must use SeedableRandomSampler")
    require(not os.environ.get("ACCELERATE_GRADIENT_ACCUMULATION_STEPS"),
            "Unexpected Accelerator gradient accumulation environment override")
    return {"versions": versions, "sources": sources,
            "normalization": "E12 unchanged: Trainer forwards num_items_in_batch; Liger sum/N over the 16-row accumulation window.",
            "runtime_observation": "get_batch_samples trace checks actual denominator; no additional forward or RNG draw"}


def processor_and_sampler_audit(init: Path, used: Path, sentinel_path: Path, slot_n: list[int]) -> dict:
    """Compare both actual parent processors on the frozen eleven real rows."""
    import torch
    from datasets import load_from_disk
    from transformers import AutoProcessor
    from accelerate.data_loader import SeedableRandomSampler

    module = load_vendor()
    processors = [AutoProcessor.from_pretrained(str(p), local_files_only=True)
                  for p in (init, used)]
    for p in processors:
        p.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
        p.tokenizer.chat_template = module.LLAVA_CHAT_TEMPLATE_WITH_EOS
    frozen_path = Path(__file__).resolve().parents[1] / "results/E12_real_row_sentinel.json"
    sentinel = read(frozen_path)
    asset_path = sentinel_path / "e13_processor_sentinel_manifest.json"
    asset = read(asset_path)
    expected_positions = [row["position"] for row in sentinel["rows"]]
    require(asset["budget"] == 11 and asset["sample_count"] == 11
            and asset["original_positions"] == expected_positions
            and asset["source_sentinel_sha256"] == sha256(frozen_path)
            and asset["self_contained_image_bytes"]
            and asset["saved_ids_dialogues_images_and_positions_equal_source"],
            "Processor sentinel asset differs from frozen E12 rows")
    for entry in asset["dataset_files"]:
        path = sentinel_path / entry["path"]
        require(path.resolve().is_relative_to(sentinel_path.resolve())
                and path.stat().st_size == entry["bytes"] and sha256(path) == entry["sha256"],
                f"Processor sentinel file changed: {path}")
    dataset = load_from_disk(str(sentinel_path))
    require(len(dataset) == 11 and list(dataset["original_position"]) == expected_positions,
            "Small processor sentinel does not represent the frozen eleven positions")
    wrapped = [module.Llava15Dataset(dataset, p) for p in processors]
    rows = []
    for idx, ref in enumerate(sentinel["rows"]):
        position = ref["position"]
        require(str(dataset[idx]["id"]) == str(ref["id"]), f"Sentinel identity changed at {position}")
        items = [w[idx] for w in wrapped]
        require(torch.equal(items[0]["input_ids"], items[1]["input_ids"])
                and torch.equal(items[0]["labels"], items[1]["labels"])
                and torch.equal(items[0]["pixel_values"], items[1]["pixel_values"]),
                f"Parent processors disagree on frozen real row {position}")
        n = int(items[0]["labels"].ne(-100).sum())
        require(n == ref["supervised_tokens"]
                and items[0]["input_ids"].numel() == ref["input_tokens"],
                f"Frozen E12 label sentinel changed at row {position}")
        turn = module._normalize_turns(dataset[idx]["texts"])[0]
        chat = [{"role": "user", "content": [{"type": "image"},
                {"type": "text", "text": turn["user"]}]}]
        prefixes = [p.apply_chat_template(chat, add_generation_prompt=True, tokenize=False)
                    for p in processors]
        require(prefixes[0] == prefixes[1], f"Parent generation prefix differs at {position}")
        rows.append({"position": position, "supervised_tokens": n,
                     "input_ids_sha256": digest_json(items[0]["input_ids"].tolist()),
                     "labels_sha256": digest_json(items[0]["labels"].tolist()),
                     "generation_prefix_sha256": hashlib.sha256(prefixes[0].encode()).hexdigest()})
    # Seedable sampler uses its explicit data_seed, independent of model-loading RNG.
    permutations = []
    for rng_seed in (17, 8675309):
        torch.manual_seed(rng_seed)
        sampler = SeedableRandomSampler(range(BUDGET), data_seed=SEED)
        permutations.append(list(sampler))
    require(permutations[0] == permutations[1] and sorted(permutations[0]) == list(range(BUDGET)),
            "Sampler depends on global/model-loading RNG")
    order = permutations[0]
    windows = [sum(slot_n[i] for i in order[j:j + 16]) for j in range(0, BUDGET, 16)]
    processor_files = {label: [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
                              for p in sorted(directory.iterdir()) if p.is_file()
                              and p.name != "model.safetensors.index.json"
                              and p.suffix in (".json", ".jinja", ".model")]
                       for label, directory in (("init", init), ("used", used))}
    return {"same_parent_processor_sentinel": rows,
            "processor_file_manifests": processor_files,
            "processor_sentinel_manifest_sha256": sha256(asset_path),
            "frozen_e12_sentinel_sha256": sha256(frozen_path),
            "processor_sentinel_file_manifest": file_manifest(sentinel_path),
            "chat_template_sha256": hashlib.sha256(module.LLAVA_CHAT_TEMPLATE_WITH_EOS.encode()).hexdigest(),
            "sampler": "accelerate.data_loader.SeedableRandomSampler",
            "sampler_model_rng_independent": True,
            "sampler_permutation_sha256": digest_json(order),
            "expected_window_supervised_tokens": windows,
            "expected_window_microbatch_n": [[slot_n[i] for i in order[j:j + 16]]
                                             for j in range(0, BUDGET, 16)]}


def verify_selection(selection_path: Path, action: str) -> tuple[dict, Path]:
    selection = read(selection_path)
    require(selection["action"] == action and selection["budget"] == BUDGET
            and selection["supervised_tokens"] == LABELS, "Wrong E13 action or dose")
    require(all(selection[k] == SEED for k in ("train_seed", "data_seed", "sampling_seed")),
            "E13 seeds must be 29")
    ns = selection["slot_supervised_tokens"]
    require(len(ns) == BUDGET and all(type(n) is int and n >= 0 for n in ns)
            and sum(ns) == LABELS, "Bad per-slot supervision")
    require(selection["sequential_window_supervised_tokens"] ==
            [sum(ns[j:j + 16]) for j in range(0, BUDGET, 16)], "Bad original-slot windows")
    contract = selection["cpu_contract"]
    require(contract["ready"] and contract["slot_n_equal"]
            and contract["contamination_status"] == "clean"
            and not contract["skipped_benchmarks"], "CPU/contamination contract not passed")
    if action != "replay":
        require(contract["row_coverage"] >= .9 and contract["label_token_coverage"] >= .8
                and contract["full_record_disjoint"]
                and contract["old_image_overlap_fresh"] == 0,
                "Partial-refresh support/identity gate not passed")
    require(selection["arrow_dataset_revision"] == EXPECTED_DATA_REVISION, "Wrong Arrow revision")
    audit_ref = selection["arrow_id_dialogue_audit"]
    audit_path = bound_path(audit_ref["path"], selection_path.parent)
    require(sha256(audit_path) == audit_ref["sha256"], "Arrow audit hash changed")
    audit = read(audit_path)
    require(not audit.get("first_shard_only") and audit["original_rows"] == 665298
            and audit["arrow_rows"] == 665298 and audit["same_position_count"] == 665298
            and audit["same_id_multiset"] is True
            and audit["same_position_conversation_count"] == 665298
            and audit["source_json_sha256"] == selection["original_json_sha256"],
            "Complete original/Arrow identity audit not passed")
    old_ref = selection["old_selection_manifest"]
    old_path = bound_path(old_ref["path"], selection_path.parent)
    require(sha256(old_path) == old_ref["sha256"], "Old E12 selection manifest changed")
    old = read(old_path)
    require(old["policy"] == "icons_exact" and old["seed"] == 17
            and old["budget"] == BUDGET
            and old["selected_positions_sha256"] == old_ref["selected_positions_sha256"],
            "Wrong E12 old selected set")
    subset = bound_path(selection["subset_path"], selection_path.parent)
    require(selection["subset_files"], "Missing saved Arrow file identity list")
    declared = set()
    for entry in selection["subset_files"]:
        path = subset / entry["path"]
        require(path.resolve().is_relative_to(subset.resolve()), "Subset path escapes root")
        require(path.stat().st_size == entry["bytes"] and sha256(path) == entry["sha256"],
                f"Saved subset changed: {path}")
        declared.add(entry["path"])
    require({str(p.relative_to(subset)) for p in subset.rglob("*.arrow")} <= declared,
            "An Arrow file is absent from the identity manifest")
    positions_path = bound_path(selection["positions_path"], selection_path.parent)
    require(positions_path.exists(), "Missing action positions file")
    positions = json.loads(positions_path.read_text())
    require(len(positions) == BUDGET and len(set(positions)) == BUDGET
            and all(type(i) is int and 0 <= i < 665298 for i in positions)
            and hashlib.sha256(("\n".join(map(str, positions)) + "\n").encode()).hexdigest()
            == selection["selected_positions_sha256"], "Action positions identity changed")
    for key in ("support_audit", "contamination_audit"):
        ref = selection[key]
        path = bound_path(ref["path"], selection_path.parent)
        require(sha256(path) == ref["sha256"], f"{key} changed")
    contamination = read(bound_path(selection["contamination_audit"]["path"], selection_path.parent))
    require(contamination["status"] == "clean" and not contamination["skipped_benchmarks"]
            and len(set(contamination["benchmarks_checked"])) == 8,
            "Frozen eight-task contamination audit incomplete")
    from datasets import load_from_disk
    require(len(load_from_disk(str(subset))) == BUDGET, "Saved action is not exactly 10K rows")
    return selection, subset


def observe_child() -> None:
    """Execute the pinned trainer, retaining its normal arguments and behavior."""
    from transformers import Trainer
    from accelerate.data_loader import SeedableRandomSampler
    launch = read(Path(os.environ["E13_RUN_MANIFEST"]))
    trace_path = Path(os.environ["E13_WINDOW_TRACE"])
    expected = launch["processor_sampler_audit"]["expected_window_microbatch_n"]
    original_init = Trainer.__init__
    original_get = Trainer.get_batch_samples
    original_loader = Trainer.get_train_dataloader

    def init_observer(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        actual = {"model_accepts_loss_kwargs": self.model_accepts_loss_kwargs,
                  "accelerator_gradient_accumulation_steps": self.accelerator.gradient_accumulation_steps,
                  "trainer_gradient_accumulation_steps": self.args.gradient_accumulation_steps,
                  "use_seedable_sampler": self.accelerator.dataloader_config.use_seedable_sampler,
                  "data_seed": self.accelerator.dataloader_config.data_seed,
                  "compute_loss_func_is_none": self.compute_loss_func is None,
                  "label_smoother_is_none": self.label_smoother is None,
                  "forward_signature": str(inspect.signature(self.model.forward)),
                  "forward_module": self.model.forward.__module__,
                  "optimizer_initially_none": self.optimizer is None,
                  "lr_scheduler_initially_none": self.lr_scheduler is None,
                  "initial_global_step": self.state.global_step,
                  "training_arguments": {key: getattr(self.args, key) for key in (
                      "seed", "data_seed", "num_train_epochs", "max_steps",
                      "per_device_train_batch_size", "gradient_accumulation_steps",
                      "learning_rate", "warmup_ratio", "weight_decay", "bf16",
                      "gradient_checkpointing", "dataloader_drop_last", "group_by_length")},
                  "packages": package_audit()}
        Path(os.environ["E13_RUNTIME_MANIFEST"]).write_text(json.dumps(actual, indent=2) + "\n")
        require(actual["model_accepts_loss_kwargs"] is True
                and actual["accelerator_gradient_accumulation_steps"] == 1
                and actual["trainer_gradient_accumulation_steps"] == 16
                and actual["use_seedable_sampler"] and actual["data_seed"] == SEED
                and actual["optimizer_initially_none"] and actual["lr_scheduler_initially_none"]
                and actual["initial_global_step"] == 0 and actual["label_smoother_is_none"]
                and actual["compute_loss_func_is_none"]
                and actual["forward_module"] == "liger_kernel.transformers.model.llava",
                "Runtime differs from frozen E12 semantics")
        cls = type(self.train_dataset)
        original_item = cls.__getitem__
        ns = launch["selection_slot_supervised_tokens"]

        def item_observer(dataset, idx):
            item = original_item(dataset, idx)
            require(int(item["labels"].ne(-100).sum()) == ns[idx],
                    f"Real image/label processing changed slot {idx}")
            return item

        cls.__getitem__ = item_observer
        self._e13_window_count = 0

    def loader_observer(self):
        loader = original_loader(self)
        sampler = loader.batch_sampler.sampler
        require(isinstance(sampler, SeedableRandomSampler) and sampler.initial_seed == SEED,
                "Actual prepared sampler is not the audited shared sampler")
        require(len(loader) == BUDGET and self.args.num_train_epochs == 1
                and self.args.max_steps == -1 and self.args.per_device_train_batch_size == 1,
                "Official epoch/data contract no longer yields exactly 625 optimizer steps")
        return loader

    def batch_observer(self, *args, **kwargs):
        batches, denominator = original_get(self, *args, **kwargs)
        ns = [int(batch["labels"].ne(-100).sum()) for batch in batches]
        window = self._e13_window_count
        actual_n = int(denominator) if denominator is not None else None
        record = {"window": window, "optimizer_step": self.state.global_step,
                  "microbatch_n": ns, "num_items_in_batch": actual_n,
                  "expected_n": sum(expected[window]) if window < STEPS else None}
        with trace_path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")
        require(window < STEPS and ns == expected[window] and actual_n == sum(ns),
                f"Actual sampler/window denominator changed: {record}")
        self._e13_window_count += 1
        return batches, denominator

    Trainer.__init__ = init_observer
    Trainer.get_train_dataloader = loader_observer
    Trainer.get_batch_samples = batch_observer
    sys.argv = [str(TRAIN_SCRIPT), *sys.argv[2:]]
    runpy.run_path(str(TRAIN_SCRIPT), run_name="__main__")
    require(len(trace_path.read_text().splitlines()) == STEPS, "Training did not emit 625 windows")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--_observe-trainer":
        observe_child()
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="E13 asset root")
    parser.add_argument("--e12-root", type=Path, required=True)
    parser.add_argument("--init-parent", type=Path, help="Defaults to e12-root/llava_init")
    parser.add_argument("--used-parent", type=Path, help="Defaults to e12-root/train_runs_v2/icons_exact_s17/model")
    parser.add_argument("--processor-sentinel-path", type=Path,
                        help="Defaults to E13 root/processor_sentinel; eleven frozen real image/dialogue rows")
    parser.add_argument("--parent", choices=("init", "used"), required=True)
    parser.add_argument("--action", choices=ACTIONS, required=True)
    parser.add_argument("--gpu", type=int, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source_sha = subprocess.check_output(["git", "-C", str(VENDOR_ROOT), "rev-parse", "HEAD"], text=True).strip()
    require(source_sha == EXPECTED_VENDOR_SHA, "Unexpected vendor revision")
    require(subprocess.run(["git", "-C", str(VENDOR_ROOT), "diff", "--quiet", "--",
                           "vendor/curation-train/src/curation_train/train_llava15.py"]).returncode == 0,
            "Pinned trainer has local changes")
    selection_path = args.root / "subsets" / args.action / "e13_selection_manifest.json"
    selection, subset = verify_selection(selection_path, args.action)
    for action in ACTIONS:
        paired = read(args.root / "subsets" / action / "e13_selection_manifest.json")
        require(paired["slot_supervised_tokens"] == selection["slot_supervised_tokens"]
                and paired["old_selection_manifest"] == selection["old_selection_manifest"]
                and paired["replacement_slots"] == selection["replacement_slots"]
                and paired["cpu_contract"]["ready"], "Paired actions do not share frozen slots/support")
    init = args.init_parent or args.e12_root / "llava_init"
    used = args.used_parent or args.e12_root / "train_runs_v2/icons_exact_s17/model"
    init_download = args.e12_root / "llava_init_download.json"
    require(read(init_download)["revision"] == EXPECTED_MODEL_REVISION, "Wrong init revision")
    for i, expected_sha in enumerate(INIT_SHAS, 1):
        require(sha256(init / f"model-0000{i}-of-00003.safetensors") == expected_sha, "Init weights changed")
    old_run = used.parent
    old_launch = read(old_run / "launch_manifest.json")
    old_completion = read(old_run / "completion.json")
    require(old_completion["returncode"] == 0 and old_completion["model_saved"]
            and old_launch["policy"] == "icons_exact" and old_launch["seed"] == 17
            and old_launch["vendor_sha"] == EXPECTED_VENDOR_SHA
            and old_launch["parent_revision"] == EXPECTED_MODEL_REVISION
            and old_launch["train_script_sha256"] == sha256(TRAIN_SCRIPT)
            and old_launch["selection_manifest_sha256"] == selection["old_selection_manifest"]["sha256"],
            "Used parent does not match successful E12 ICONS training provenance")
    old_command = old_launch["command"]
    for flag, value in {"--num_train_epochs": "1", "--per_device_train_batch_size": "1",
                        "--gradient_accumulation_steps": "16", "--learning_rate": "2e-5",
                        "--optim": "adamw_torch_fused", "--seed": "17", "--data_seed": "17"}.items():
        require(flag in old_command and old_command[old_command.index(flag) + 1] == value,
                f"E12 parent recipe changed: {flag}")
    parent = init if args.parent == "init" else used
    index = read(parent / "model.safetensors.index.json")
    require(all((parent / name).is_file() for name in set(index["weight_map"].values())),
            "Parent weight shards incomplete")
    packages = package_audit()
    processor_sampler = processor_and_sampler_audit(
        init, used, args.processor_sentinel_path or args.root / "processor_sentinel",
        selection["slot_supervised_tokens"])
    run_dir = args.out_root / f"{args.parent}_{args.action}_s29"
    require(not run_dir.exists(), f"Refusing to overwrite existing E13 run: {run_dir}")
    config = {"method": "llava", "data_path": str(subset), "model_name_or_path": str(parent)}
    command = [sys.executable, "-m", "accelerate.commands.launch", "--num_processes", "1",
               "--gpu_ids", str(args.gpu), str(Path(__file__).resolve()), "--_observe-trainer",
               "--config_json", str(run_dir / "train_config.json"), "--output_dir", str(run_dir / "model"),
               "--num_train_epochs", "1", "--per_device_train_batch_size", "1",
               "--gradient_accumulation_steps", "16", "--learning_rate", "2e-5", "--weight_decay", "0.0",
               "--warmup_ratio", "0.03", "--lr_scheduler_type", "cosine", "--bf16", "--optim", "adamw_torch_fused",
               "--gradient_checkpointing", "--dataloader_num_workers", "2", "--remove_unused_columns", "False",
               "--save_strategy", "no", "--report_to", "none", "--logging_steps", "1",
               "--seed", str(SEED), "--data_seed", str(SEED)]
    manifest = {"parent": args.parent, "action": args.action, "command": command, "config": config,
                "seed": SEED, "gpu": args.gpu, "expected_steps": STEPS, "expected_rows": BUDGET,
                "expected_supervised_tokens": LABELS, "optimizer_scheduler_reset": True,
                "resume_from_checkpoint": None, "parent_path": str(parent),
                "parent_file_manifest": file_manifest(parent), "init_revision": EXPECTED_MODEL_REVISION,
                "init_download_manifest_sha256": sha256(init_download),
                "e12_launch_manifest": old_launch, "e12_completion": old_completion,
                "e12_launch_manifest_sha256": sha256(old_run / "launch_manifest.json"),
                "e12_completion_sha256": sha256(old_run / "completion.json"),
                "selection_manifest_path": str(selection_path), "selection_manifest_sha256": sha256(selection_path),
                "selection_identity": {k: selection[k] for k in ("selected_positions_sha256", "selected_full_records_sha256", "cpu_contract")},
                "selection_slot_supervised_tokens": selection["slot_supervised_tokens"],
                "processor_sampler_audit": processor_sampler, "packages": packages,
                "vendor_sha": source_sha, "train_script_sha256": sha256(TRAIN_SCRIPT),
                "launcher_sha256": sha256(Path(__file__)), "python": sys.executable,
                "device_mapping": "outer CUDA_VISIBLE_DEVICES and Accelerate gpu_ids use the same physical GPU; child device is logical 0"}
    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return
    require(gpu_free_mb(args.gpu) >= 75000, "GPU has less than 75 GB free; refusing contention")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "train_config.json").write_text(json.dumps(config, indent=2) + "\n")
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES=str(args.gpu), CUDA_DEVICE_ORDER="PCI_BUS_ID",
               E13_TRAIN_CONFIG=str(run_dir / "train_config.json"),
               E13_RUN_MANIFEST=str(run_dir / "run_manifest.json"),
               E13_RUNTIME_MANIFEST=str(run_dir / "runtime_manifest.json"),
               E13_WINDOW_TRACE=str(run_dir / "window_trace.jsonl"))
    start = time.monotonic()
    with (run_dir / "train_stdout.log").open("w") as stdout, (run_dir / "train_stderr.log").open("w") as stderr:
        result = subprocess.run(command, env=env, stdout=stdout, stderr=stderr, check=False)
    trace = run_dir / "window_trace.jsonl"
    windows = len(trace.read_text().splitlines()) if trace.exists() else 0
    saved = bool(list((run_dir / "model").glob("model*.safetensors")))
    completion = {"returncode": result.returncode, "wall_seconds": round(time.monotonic() - start, 1),
                  "model_saved": saved, "observed_windows": windows, "run_dir": str(run_dir)}
    (run_dir / "completion.json").write_text(json.dumps(completion, indent=2) + "\n")
    print(json.dumps(completion))
    require(result.returncode == 0 and saved and windows == STEPS, "E13 failed; all run artifacts retained")


if __name__ == "__main__":
    main()
