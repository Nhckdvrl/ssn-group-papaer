"""Rebuild registered E130 seed0/1 untrained banks; capture with frozen E124.

Default: prepare CPU weights, verify the real training initialization hash, then
capture on the explicitly visible physical GPU. --mode prepare is CPU-only.
The step0 checkpoint is a reference asset, with no optimizer/training state.
"""
from __future__ import annotations
import argparse, json, os, shutil, socket
from pathlib import Path

import e130_finalize as assets

WB = assets.WB
FINALIZER_SHA = "2b1bed11f13fc0cd2dbb658383b7d9c973da41760e4ec1236e7f18a10a76039f"


def check_sources():
    actual = {name: assets.sha(WB / "scripts" / name) for name in assets.FROZEN}
    if actual != assets.FROZEN or assets.sha(WB / "scripts/e130_finalize.py") != FINALIZER_SHA:
        raise ValueError("Frozen training/capture/asset-helper source SHA differs")
    if assets.sha(WB / "results/e124/plan.json") != assets.PLAN_SHA:
        raise ValueError("Fixed E124 sample plan SHA differs")
    return actual


def build_bank(seed, dimensions, expected=None):
    import torch
    from e123_frozen_moe import TensorMoE
    from e124_functional_capture import tensor_state_hash
    torch.manual_seed(seed)
    with torch.device("cpu"):
        bank = TensorMoE(*dimensions)
    state = bank.state_dict()
    if any(value.dtype != torch.float32 for value in state.values()): raise ValueError("Initial bank must be FP32")
    digest = tensor_state_hash(state)
    if expected is not None and digest != expected:
        raise ValueError(f"Reconstructed full FP32 initialization differs from training: {digest} != {expected}")
    return state, digest


def prepare(seed, out):
    import torch
    from e123_frozen_moe import digest_json
    from e124_functional_capture import tensor_state_hash
    frozen = check_sources()
    source = WB / "results/e130/preflight" / ("seed0_repeat" if seed == 0 else "seed1_order0") / "provenance.json"
    original, protocol = assets.read(source), assets.read(source.with_name("driver_protocol.json"))
    if not original or not protocol: raise ValueError("Missing registered training provenance/protocol")
    args = original["args"]
    wanted = {"seed": seed, "order_seed": 0, "replacement": "moe", "layer": 9, "experts": 64,
              "expert_size": 1024, "top_k": 8, "init_std": .02, "steps": 62500,
              "seq_len": 512, "batch_size": 16, "dtype": "bfloat16", "driver_sha256": assets.DRIVER_SHA}
    if any(args.get(key) != value for key, value in wanted.items()): raise ValueError("Source is not the registered E130 configuration")
    expected, backbone = original["initial_tensor_sha256"], original["frozen_sample_hash"]
    if (protocol.get("experiment") != "E130" or protocol.get("cpu_test") is not False
            or protocol.get("driver_sha256") != assets.DRIVER_SHA or protocol.get("seed") != seed
            or protocol.get("initial_tensor_sha256") != expected or args.get("expected_initial_tensor_sha256") != expected
            or protocol.get("expected_frozen_sample_hash") != backbone or args.get("expected_frozen_sample_hash") != backbone):
        raise ValueError("Source initialization/backbone/driver fingerprints disagree")
    model_config = assets.read(Path(args["model"]) / "config.json")
    if model_config["hidden_size"] != 2048 or model_config["intermediate_size"] != 8192:
        raise ValueError("Backbone architecture differs from registered OLMo-1B")
    specification = {"experiment": "E130", "reference_only": True, "stage": "untrained_initial_bank", "seed": seed,
                     "dimensions": [2048, 1024, 64, 8, .02], "initial_tensor_sha256": expected,
                     "frozen_sample_hash": backbone, "source_training_provenance_sha256": assets.sha(source),
                     "source_training_config_hash": original["config_hash"], "script_sha256": assets.sha(__file__),
                     "frozen_source_sha256": frozen, "plan_sha256": assets.PLAN_SHA}
    config_hash = digest_json(specification)
    out.mkdir(parents=True, exist_ok=True)
    checkpoint = out / "initial_reference.pt"
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location="cpu", mmap=True, weights_only=False)
        if saved.get("reference_only") is not True or saved.get("step") != 0 or saved.get("config_hash") != config_hash:
            raise ValueError("Existing checkpoint is a different reference")
        if tensor_state_hash(saved["moe"]) != expected: raise ValueError("Existing initial bank differs from the real training initialization")
    else:
        state, digest = build_bank(seed, specification["dimensions"], expected)
        saved = {"schema": "E130-initial-reference-v1", "reference_only": True, "step": 0, "replacement_kind": "moe",
                 "replacement_state": state, "moe": state, "config_hash": config_hash,
                 "frozen_sample_hash": backbone, "initial_tensor_sha256": digest}
        partial = checkpoint.with_suffix(".partial"); torch.save(saved, partial); partial.replace(checkpoint)
    # Preserve the canonical training provenance bytes separately from reference provenance.
    canonical = out / "source_training_provenance.json"
    if canonical.exists() and assets.sha(canonical) != assets.sha(source): raise FileExistsError(canonical)
    if not canonical.exists(): shutil.copyfile(source, canonical)
    reference = {**specification, "config_hash": config_hash, "host": socket.gethostname(), "torch": torch.__version__,
                 "source_training_provenance": str(source), "checkpoint": str(checkpoint),
                 "checkpoint_bytes": checkpoint.stat().st_size, "checkpoint_archived": False,
                 "args": {**wanted, "mode": "initial_reference", "steps": 0, "model": args["model"], "data": args["data"]}}
    assets.write(out / "provenance.json", reference)
    assets.write(out / "preparation.json", {**reference, "status": "initial_hash_verified"})
    return checkpoint, original, reference


def archive(out, summary, seed):
    destination = Path.home() / "mechpop_cache" / f"e130_initial_seed{seed}"
    if destination.exists(): raise FileExistsError(destination)
    staging = destination.with_name(destination.name + ".partial")
    staging.mkdir(parents=True, exist_ok=False)
    files = {}
    for source in (out / "functional_initial.npz", out / "preparation.json", out / "provenance.json",
                   out / "source_training_provenance.json", summary):
        target = staging / source.name; shutil.copy2(source, target)
        digest = assets.sha(source)
        if assets.sha(target) != digest: raise IOError(f"Archive SHA differs: {source}")
        files[source.name] = {"sha256": digest, "size_bytes": target.stat().st_size}
    assets.write(staging / "archive_manifest.json", {"experiment": "E130", "reference_only": True,
                 "seed": seed, "files": files, "initial_weights": "Rebuild from seed/hash; retained only at original NVMe path"})
    staging.rename(destination)
    return destination


def run(args):
    checkpoint, original, reference = prepare(args.seed, args.output_dir)
    if args.mode == "prepare": return {"status": "prepared_cpu_only", **reference}
    import torch
    import e124_functional_capture as functional
    from e123_frozen_moe import digest_json
    physical = args.physical_gpu
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if physical is None:
        if not visible.isdigit(): raise ValueError("Set one physical CUDA_VISIBLE_DEVICES index or --physical-gpu")
        physical = int(visible)
    if visible and visible != str(physical): raise ValueError("Visible GPU differs from requested physical GPU")
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA was initialized before the physical GPU occupancy check")
    gpu = assets.gpu_status(physical)
    if not assets.gpu_free(gpu):
        status = {"status": "deferred_gpu_busy_or_unavailable", "reference_only": True, "gpu_preflight": gpu}
        assets.write(args.output_dir / "capture_status.json", status); return status
    os.environ["CUDA_VISIBLE_DEVICES"] = str(physical)
    source_args = original["args"]
    settings = functional.parser().parse_args(["--mode", "capture", "--model", source_args["model"],
        "--data", source_args["data"], "--checkpoint", str(checkpoint), "--output", str(args.output_dir / "functional_initial.npz"),
        "--summary", str(args.summary), "--plan", str(WB / "results/e124/plan.json"), "--seed", str(args.seed),
        "--order-seed", "0", "--run-id", f"E130-initial-seed{args.seed}", "--device", "cuda:0", "--dtype", "bfloat16",
        "--batch-size", "16", "--alpha", ".125", "--cal-sequences", "64", "--seq-len", "512", "--cal-stride", "4", "--cal-seed", "91024"])
    _, summary = functional.capture(settings)
    if summary["hcal"]["data_identity_sha256"] != digest_json(original["data"]):
        raise ValueError("Hcal data identity differs from real training provenance")
    summary.update({"experiment": "E130", "reference_only": True, "stage": "untrained_initial_bank",
                    "initial_tensor_sha256": reference["initial_tensor_sha256"], "host": socket.gethostname(),
                    "source_training_provenance": reference["source_training_provenance"],
                    "source_training_provenance_sha256": reference["source_training_provenance_sha256"],
                    "source_training_config_hash": original["config_hash"], "preparation_script_sha256": assets.sha(__file__)})
    assets.write(args.summary, summary)
    destination = archive(args.output_dir, args.summary, args.seed)
    status = {"status": "complete", "reference_only": True, "seed": args.seed, "summary": str(args.summary),
              "gpu_preflight": gpu, "archive": str(destination), "archive_manifest_sha256": assets.sha(destination / "archive_manifest.json")}
    assets.write(args.output_dir / "capture_status.json", status)
    return status


def self_test():
    check_sources()
    dimensions = (8, 8, 4, 2, .02)
    _, expected = build_bank(0, dimensions)
    _, repeated = build_bank(0, dimensions, expected)
    _, different = build_bank(1, dimensions)
    assert expected == repeated and expected != different
    try: build_bank(1, dimensions, expected)
    except ValueError: pass
    else: raise AssertionError("Wrong initialization hash accepted")
    return {"passed": True, "device": "cpu", "tiny_bank_reconstruction_exact": True, "wrong_hash_rejected": True,
            "no_full_model_or_GPU": True, "script_sha256": assets.sha(__file__)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--mode", choices=("prepare", "capture"), default="capture")
    parser.add_argument("--seed", type=int, choices=(0, 1)); parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--summary", type=Path); parser.add_argument("--physical-gpu", type=int)
    args = parser.parse_args()
    if args.self_test: print(json.dumps(self_test(), indent=2), flush=True); return
    if args.seed is None or not args.output_dir: parser.error("--seed and --output-dir are required")
    args.output_dir = args.output_dir.expanduser().resolve()
    if args.output_dir.is_relative_to(WB): parser.error("Large reference assets must be outside the repository")
    if args.physical_gpu is not None and args.physical_gpu < 0: parser.error("physical-gpu must be nonnegative")
    args.summary = args.summary or WB / "results/e130/functional" / f"initial_seed{args.seed}.json"
    try: print(json.dumps(run(args), indent=2), flush=True)
    except Exception as error:
        assets.write(args.output_dir / "failure.json", {"reference_only": True, "error": f"{type(error).__name__}: {error}"})
        raise


if __name__ == "__main__": main()
