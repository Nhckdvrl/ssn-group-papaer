"""One-shot E131 common-phase watcher, fixed-endpoint scoring and SHA archive."""
from __future__ import annotations
import argparse, contextlib, gc, hashlib, json, os, shutil, socket, tempfile, time
from pathlib import Path
import e130_finalize as tools

WB, RESULTS, ARCHIVES = tools.WB, tools.WB / "results/e131", Path.home() / "mechpop_cache"
read, write, sha = tools.read, tools.write, tools.sha
DRIVER_SHA = "455f90e6202da01bce1f4586d0912620f52e2ed7b3dd424c86353887237e1a78"
HELPER_SHA = "2b1bed11f13fc0cd2dbb658383b7d9c973da41760e4ec1236e7f18a10a76039f"
PARENT_SHA = "13bb7ec0c8dc899744e7e4e6c7938c80a80c1b8079d1e3c89f764251524dbabf"
PARENT_CONFIG = "8e70948181dde6fff44026456e97f9ffdf2aa002af7ce3a4f2e9bc15a683ea1f"
INITIAL = "0f898b422ee00a4b2255efcea6e6fd4063fbd91f38e614fc74ad8f85ba936fff"
FROZEN = "565b9dacb123aab3e1f296bcc1bad8928fa7811492b80aface1809530a0b6c03"
PLAN_SHA = "13e09391617d49d1a9c7ec3ae5ff9417238bd6fc9b036adfc830f7805b25206f"
COMMON_START = hashlib.sha256(b"E131-common-token-batch-chain-v1").hexdigest()


def matches_training(argv, out, branch, *, common_only=True):
    return (any(Path(word).name == "e131_order_history.py" for word in argv)
            and tools.argument(argv, "--mode") == "train" and tools.argument(argv, "--branch") == branch
            and (not common_only or tools.argument(argv, "--phase") == "continue")
            and tools.argument(argv, "--output") is not None and Path(tools.argument(argv, "--output")).resolve() == out.resolve())


def checkpoint_metadata(path, provenance, step):
    import torch
    checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    expected = {"schema": "E131-child-v1", "experiment": "E131", "replacement_kind": "moe", "phase": "common",
        "branch": provenance["args"]["branch"], "step": step, "config_hash": provenance["config_hash"],
        "parent": provenance["parent"], "initial_tensor_sha256": INITIAL, "frozen_sample_hash": FROZEN,
        "epoch_coverage_valid": True, "pulse_cursor": 1024, "common_updates": step - 5120}
    if any(checkpoint.get(key) != value for key, value in expected.items()): raise ValueError(f"E131 checkpoint metadata differs: {path}")
    coverage = checkpoint["coverage"]
    draws = sum(int(values.sum(dtype="uint64")) for values in coverage["counts"])
    if (draws != step * 16 or coverage["draws"] != draws or not checkpoint["stream_rng"]
            or checkpoint["actual_source_schedule_hash"] != coverage["source_schedule_hash"]):
        raise ValueError("Epoch exposure/source/RNG proof is inconsistent")
    if sum(int(values.sum(dtype="uint64")) for values in checkpoint["actual_pulse_counts"]) != 5120 * 16:
        raise ValueError("Actual pulse exposure proof is inconsistent")
    if step == 5120 and checkpoint["common_input_hash"] != COMMON_START: raise ValueError("Pulse snapshot consumed common inputs")
    return {"actual_source_schedule_hash": checkpoint["actual_source_schedule_hash"],
            "common_input_hash": checkpoint["common_input_hash"], "pulse_input_hash": checkpoint["pulse_input_hash"],
            "draws": draws, "common_updates": checkpoint["common_updates"]}


def validate(out, branch):
    summary, provenance, protocol = [read(out / name) for name in ("training_summary.json", "provenance.json", "driver_protocol.json")]
    if not tools.ready(summary, read(out / "failure.json")): raise ValueError("E131 endpoint is incomplete or records a training failure")
    frozen_sources = {**tools.FROZEN, "e130_finalize.py": HELPER_SHA, "e131_order_history.py": DRIVER_SHA}
    if {name: sha(WB / "scripts" / name) for name in frozen_sources} != frozen_sources: raise ValueError("Frozen source SHA differs")
    if (not provenance or provenance != protocol or provenance.get("experiment") != "E131" or provenance.get("cpu_test") is not False
            or summary.get("experiment") != "E131" or summary.get("branch") != branch):
        raise ValueError("E131 provenance/protocol/summary identity differs")
    args = provenance["args"]
    expected = {"driver_sha256": DRIVER_SHA, "branch": branch, "phase": "continue", "parent_step": 4096,
        "pulse_steps": 1024, "pulse_lr": .000196608, "late_step": 61440, "seed": 0, "order_seed": 0,
        "steps": 62500, "max_train_tokens": 512_000_000, "batch_size": 16, "seq_len": 512, "accum": 1,
        "replacement": "moe", "layer": 9, "experts": 64, "expert_size": 1024, "top_k": 8, "dtype": "bfloat16",
        "lr": 3e-4, "warmup_fraction": .1, "weight_decay": .1, "lb_coef": .01, "z_coef": .001, "init_std": .02, "grad_clip": 1., "max_hours": 8.}
    if any(args.get(key) != value for key, value in expected.items()): raise ValueError("Registered E131 training arguments differ")
    parent = provenance["parent"]
    if any(parent.get(key) != value for key, value in {"checkpoint_sha256": PARENT_SHA, "config_hash": PARENT_CONFIG,
           "initial_tensor_sha256": INITIAL, "frozen_sample_hash": FROZEN}.items()): raise ValueError("Registered parent fingerprints differ")
    if (summary.get("parent") != parent or summary.get("config_hash") != provenance.get("config_hash")
            or summary.get("run_id") != provenance.get("run_id") or summary.get("pulse_cursor") != 1024
            or provenance.get("initial_tensor_sha256") != INITIAL or summary.get("initial_tensor_sha256") != INITIAL
            or provenance.get("frozen_sample_hash") != FROZEN or summary.get("frozen_sample_hash_before") != FROZEN
            or summary.get("frozen_sample_hash_after") != FROZEN): raise ValueError("Summary/config/init/frozen fingerprints differ")
    plan = Path(args["pulse_plan"]); manifest = read(plan / "manifest.json")
    if (sha(plan / "manifest.json") != PLAN_SHA or provenance.get("pulse_plan_sha256") != PLAN_SHA
            or manifest["specification"]["parent"] != parent or manifest["specification"]["driver_sha256"] != DRIVER_SHA
            or manifest["multiset_sha256"] != manifest["permuted_multiset_sha256"]): raise ValueError("Read-only pulse plan identity differs")
    for name, expected_sha in manifest["files"].items():
        if sha(plan / name) != expected_sha: raise ValueError(f"Pulse-plan asset SHA differs: {name}")
    proof = checkpoint_metadata(out / "checkpoint.pt", provenance, 62500)
    if (proof["common_input_hash"] != summary.get("common_input_hash") or proof["pulse_input_hash"] != summary.get("pulse_input_hash")
            or proof["actual_source_schedule_hash"] != summary["coverage"]["source_schedule_hash"]
            or summary["coverage"]["drawn_windows"] != 1_000_000): raise ValueError("Summary and checkpoint history proofs differ")
    return summary, provenance, proof


def common_proof(out, expected):
    path = out / "common_input_proof.jsonl"; temporary = path.with_suffix(".partial")
    count, terminal = 0, COMMON_START
    with (out / "train_steps.jsonl").open() as source, temporary.open("w") as target:
        for line in source:
            row = json.loads(line)
            if row["phase"] != "common": continue
            count += 1
            if row["step"] != 5120 + count: raise ValueError("Missing/duplicate/out-of-order common training input record")
            value = {key: row[key] for key in ("step", "input_batch_sha256", "common_input_hash")}
            for key in ("input_batch_sha256", "common_input_hash"):
                if len(bytes.fromhex(value[key])) != 32: raise ValueError("Malformed common input SHA")
            value["actual_source_schedule_hash"] = row["coverage"]["source_schedule_hash"]
            target.write(json.dumps(value, sort_keys=True) + "\n"); terminal = value["common_input_hash"]
    if count != 57380 or terminal != expected["common_input_hash"]: raise ValueError("Common input proof does not reach the validated endpoint")
    temporary.replace(path)
    return {"updates": count, "first_step": 5121, "last_step": 62500, "initial_hash": COMMON_START,
            "terminal_hash": terminal, "path": str(path), "sha256": sha(path),
            "scope": "Actual driver token/input-chain records for later per-step cross-branch equality; source histories remain branch-specific"}


def scoped_guard(old, step, expected, reference, registered):
    if expected == 62500:
        if not registered or reference or step != 62500: raise ValueError("62500 is reserved for this validated E131 endpoint")
        return
    return old(step, expected, reference)


def fidelity(out, branch):
    import e127_predictive_fidelity as evaluator
    validate(out, branch)
    old = evaluator.guard_step
    evaluator.guard_step = lambda step, expected, reference: scoped_guard(old, step, expected, reference, True)
    path = RESULTS / "fidelity" / f"{branch}.json"
    try:
        result = evaluator.evaluate(argparse.Namespace(checkpoint=str(out / "checkpoint.pt"), model=None, data=None,
            device="cuda:0", output=str(path), expected_step=62500, reference_calibration=False, bootstrap=1000))
    finally: evaluator.guard_step = old
    result.update({"experiment": "E131", "branch": branch, "e131_driver_sha256": DRIVER_SHA,
                   "host": socket.gethostname(), "finalizer_sha256": sha(__file__), "guard_scope": "Validated E13162500 only; original E127 guard restored"})
    write(path, result)


def capture(out, provenance, label, branch):
    import e124_functional_capture as functional
    path = out / "checkpoint.pt" if label == "final" else out / "snapshots/step061440.pt"
    checkpoint_metadata(path, provenance, 62500 if label == "final" else 61440)
    if sha(WB / "results/e124/plan.json") != tools.PLAN_SHA: raise ValueError("Fixed functional sample plan differs")
    args = provenance["args"]; summary_path = RESULTS / "functional" / f"{branch}_{label}.json"
    settings = functional.parser().parse_args(["--mode", "capture", "--model", args["model"], "--data", args["data"],
        "--checkpoint", str(path), "--output", str(out / f"functional_{label}.npz"), "--summary", str(summary_path),
        "--plan", str(WB / "results/e124/plan.json"), "--run-id", f"E131-{branch}-{label}", "--seed", "0", "--order-seed", "0",
        "--device", "cuda:0", "--dtype", "bfloat16", "--batch-size", "16", "--alpha", ".125", "--cal-sequences", "64",
        "--seq-len", "512", "--cal-stride", "4", "--cal-seed", "91024"])
    _, summary = functional.capture(settings)
    summary.update({"experiment": "E131", "branch": branch, "host": socket.gethostname(), "finalizer_sha256": sha(__file__),
                    "training_provenance": str(out / "provenance.json")})
    write(summary_path, summary)


def shared_reference(path):
    manifest = read(path / "archive_manifest.json")
    if not manifest or manifest.get("parent_checkpoint_sha256") != PARENT_SHA or manifest.get("pulse_plan_manifest_sha256") != PLAN_SHA:
        raise ValueError("Shared parent/plan archive metadata missing or inconsistent")
    return {"path": str(path), "manifest_sha256": sha(path / "archive_manifest.json"),
            "parent_checkpoint_sha256": PARENT_SHA, "pulse_plan_manifest_sha256": PLAN_SHA, "copied_per_branch": False}


def archive(out, branch, state):
    destination = ARCHIVES / f"e131_{branch}_512m"; checkpoint_sha = sha(out / "checkpoint.pt")
    existing = read(destination / "archive_manifest.json")
    if destination.exists() and (not existing or existing.get("checkpoint_sha256") != checkpoint_sha): raise FileExistsError(destination)
    staging = destination if destination.exists() else destination.with_name(destination.name + ".partial")
    if staging != destination: staging.mkdir(parents=True, exist_ok=False)
    names = ("checkpoint.pt", "provenance.json", "driver_protocol.json", "gradient_audit.json", "training_summary.json",
             "final_held_sequences.json", "final_pos.json", "common_input_proof.jsonl", "pulse_function.npz")
    sources = {name: out / name for name in names}
    sources["pulse_step005120.pt"] = out / "snapshots/step005120.pt"
    for label in ("final", "late"):
        sources[f"functional_{label}.npz"] = out / f"functional_{label}.npz"
    sources.update({f"functional_{label}.json": RESULTS / "functional" / f"{branch}_{label}.json" for label in ("pulse", "final", "late")})
    sources.update({"fidelity.json": RESULTS / "fidelity" / f"{branch}.json", "fidelity_sequences.json": RESULTS / "fidelity" / f"{branch}_sequences.json"})
    files, missing = {}, []
    for name, source in sources.items():
        if not source.is_file(): missing.append(str(source)); continue
        target = staging / name; expected = sha(source)
        if target.exists():
            if sha(target) != expected: raise FileExistsError(f"Existing archive file differs: {target}")
        else:
            partial = target.with_suffix(target.suffix + ".partial"); shutil.copy2(source, partial)
            if sha(partial) != expected: raise IOError(f"Archive copy SHA differs: {source}")
            partial.replace(target)
        files[name] = {"sha256": expected, "size_bytes": target.stat().st_size}
    required = {*names, "pulse_step005120.pt", "functional_pulse.json"}
    if missing and (state["status"] == "complete" or any(str(sources[name]) in missing for name in required)): state["status"] = "archive_incomplete"
    write(staging / "postprocessing.json", state)
    files["postprocessing.json"] = {"sha256": sha(staging / "postprocessing.json"), "size_bytes": (staging / "postprocessing.json").stat().st_size}
    manifest = {"experiment": "E131", "branch": branch, "checkpoint_sha256": checkpoint_sha, "files": files,
                "missing_sources": missing, "shared_parent_archive": state["shared_parent_archive"],
                "late_optimizer_scope": "NVMe snapshot61440 retained; not duplicated here", "finalizer_sha256": sha(__file__)}
    write(staging / "archive_manifest.json", manifest)
    if staging != destination: staging.rename(destination)
    return destination, manifest


def finish(args):
    out, branch = args.output_dir, args.branch; path = RESULTS / "finalization" / f"{branch}.json"
    state = {"experiment": "E131", "branch": branch, "host": socket.gethostname(), "output_dir": str(out),
             "finalizer_sha256": sha(__file__), "driver_sha256": DRIVER_SHA, "errors": {}, "shared_parent_archive": str(args.shared_parent_archive)}
    try: summary, provenance, history = validate(out, branch)
    except Exception as error: write(path, {**state, "status": "validation_failed", "errors": {"validation": f"{type(error).__name__}: {error}"}}); return
    state.update({"step": 62500, "train_tokens": 512_000_000, "config_hash": summary["config_hash"], "history": history})
    for name, operation in (("common_input_proof", lambda: common_proof(out, history)),
                            ("shared_reference", lambda: shared_reference(args.shared_parent_archive)),
                            ("pulse_checkpoint", lambda: checkpoint_metadata(out / "snapshots/step005120.pt", provenance, 5120))):
        try: state[name] = operation()
        except Exception as error: state["errors"][name] = f"{type(error).__name__}: {error}"
    gpu = tools.gpu_status(args.physical_gpu); state["gpu_preflight"] = gpu
    if tools.gpu_free(gpu):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.physical_gpu)
        jobs = [("fidelity", lambda: fidelity(out, branch))] + [(f"functional_{label}", lambda label=label: capture(out, provenance, label, branch)) for label in ("final", "late")]
        for name, operation in jobs:
            try: operation()
            except Exception as error: state["errors"][name] = f"{type(error).__name__}: {error}"
            finally:
                try:
                    import torch
                    gc.collect()
                    if torch.cuda.is_initialized(): torch.cuda.empty_cache()
                except Exception as error: state["errors"][name + "_cleanup"] = f"{type(error).__name__}: {error}"
        state["status"] = "postprocessing_failed" if state["errors"] else "complete"
    else: state["status"] = "postprocessing_failed_gpu_deferred" if state["errors"] else "evaluation_deferred_gpu_busy_or_unavailable"
    try:
        destination, manifest = archive(out, branch, state)
        state.update({"archive": str(destination), "checkpoint_sha256": manifest["checkpoint_sha256"], "missing_sources": manifest["missing_sources"],
                      "archive_manifest_sha256": sha(destination / "archive_manifest.json")})
    except Exception as error: state["status"] = "archive_failed"; state["errors"]["archive"] = f"{type(error).__name__}: {error}"
    write(path, state)


def watch(args):
    deadline, observed = time.monotonic() + args.max_watch_hours * 3600, False
    path = RESULTS / "finalization" / f"{args.branch}.json"
    while time.monotonic() < deadline:
        argv = tools.process_argv(args.training_pid)
        if argv and not matches_training(argv, args.output_dir, args.branch):
            write(path, {"status": "pid_command_mismatch", "pid": args.training_pid, "argv": argv}); return
        if argv: observed = True
        else:
            if observed: finish(args)
            else: write(path, {"status": "training_pid_not_observed", "pid": args.training_pid, "evaluation": None})
            return
        time.sleep(args.poll_seconds)
    write(path, {"status": "watch_timeout_no_evaluation", "pid": args.training_pid, "evaluation": None})


def self_test():
    import sys
    from unittest.mock import patch
    import e127_predictive_fidelity as evaluator
    complete = {"status": "complete", "step": 62500, "planned_steps": 62500, "train_tokens": 512_000_000}
    assert tools.ready(complete, None) and not tools.ready({**complete, "step": 5120}, None) and not tools.ready(complete, {})
    old = evaluator.guard_step
    real_fidelity = fidelity
    frozen_sources = {**tools.FROZEN, "e130_finalize.py": HELPER_SHA, "e131_order_history.py": DRIVER_SHA}
    assert {name: sha(WB / "scripts" / name) for name in frozen_sources} == frozen_sources
    for values in ((62500, 62500, False, True), (15625, 15625, False, True), (3906, 3906, True, True)): scoped_guard(old, *values)
    for values in ((62500, 62500, False, False), (62500, 62500, True, True), (5120, 62500, False, True), (3906, 3906, False, True)):
        try: scoped_guard(old, *values)
        except ValueError: pass
        else: raise AssertionError(f"Scoped E131 guard accepted {values}")
    with tempfile.TemporaryDirectory(prefix="e131_finalizer_cpu_") as directory:
        root = Path(directory); out = root / "run"; out.mkdir(); (out / "snapshots").mkdir()
        for name in ("checkpoint.pt", "pulse_function.npz", "snapshots/step005120.pt"): (out / name).write_bytes(b"CPU archive sentinel")
        for name in ("provenance.json", "driver_protocol.json", "gradient_audit.json", "training_summary.json", "final_held_sequences.json", "final_pos.json"):
            write(out / name, {})
        (out / "common_input_proof.jsonl").write_text("{}\n")
        write(root / "results/functional/ordered_pulse.json", {})
        args = argparse.Namespace(output_dir=out, branch="ordered", physical_gpu=0, shared_parent_archive=root / "shared")
        argv = ["python", "e131_order_history.py", "--mode", "train", "--phase", "continue", "--branch", "ordered", "--output", str(out)]
        assert matches_training(argv, out, "ordered") and not matches_training(argv, out, "permuted") and not matches_training(argv, root, "ordered")
        module = sys.modules[__name__]
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(module, "RESULTS", root / "results")); stack.enter_context(patch.object(module, "ARCHIVES", root / "archive"))
            stack.enter_context(patch.object(module, "validate", return_value=({**complete, "config_hash": "test"}, {}, {})))
            for name in ("common_proof", "shared_reference", "checkpoint_metadata"): stack.enter_context(patch.object(module, name, return_value={}))
            stack.enter_context(patch.object(tools, "gpu_status", return_value={"compute_processes": ["busy"]}))
            score = stack.enter_context(patch.object(module, "fidelity", side_effect=AssertionError("GPU score while busy")))
            bank = stack.enter_context(patch.object(module, "capture", side_effect=AssertionError("GPU capture while busy")))
            finish(args); score.assert_not_called(); bank.assert_not_called()
            result = read(root / "results/finalization/ordered.json")
            assert result["status"] == "evaluation_deferred_gpu_busy_or_unavailable" and result["archive"] and result["missing_sources"]
            def interrupted(settings):
                evaluator.guard_step(62500, 62500, False)
                raise RuntimeError("intentional scoped-guard interruption")
            with patch.object(evaluator, "evaluate", side_effect=interrupted):
                try: real_fidelity(out, "ordered")
                except RuntimeError: pass
                else: raise AssertionError("Expected scoring interruption")
            assert evaluator.guard_step is old
            with patch.object(module, "validate", side_effect=ValueError("unvalidated endpoint")), patch.object(evaluator, "evaluate") as rejected:
                try: real_fidelity(out, "ordered")
                except ValueError: pass
                else: raise AssertionError("Unvalidated scoring call accepted")
                rejected.assert_not_called()
    assert evaluator.guard_step is old
    result = {"passed": True, "device": "cpu", "finalizer_sha256": sha(__file__), "strict_fixed_endpoint_readiness": True,
              "scoped_E13162500_guard": True, "busy_GPU_archives_without_scoring_or_capture": True,
              "exact_continue_PID_branch_output_identity": True, "missing_assets_explicit": True, "no_GPU_or_model_test": True}
    write(RESULTS / "finalizer_self_test.json", result); print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true")
    mode = parser.add_mutually_exclusive_group(); mode.add_argument("--training-pid", type=int); mode.add_argument("--finalize-now", action="store_true")
    parser.add_argument("--branch", choices=("ordered", "permuted")); parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--physical-gpu", type=int); parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--max-watch-hours", type=float, default=9.)
    parser.add_argument("--shared-parent-archive", type=Path, default=Path.home() / "mechpop_cache/e131_parent_and_plan")
    args = parser.parse_args()
    if args.self_test: self_test(); return
    if (not args.branch or not args.output_dir or args.physical_gpu is None or args.physical_gpu < 0
            or args.poll_seconds < 1 or not 0 < args.max_watch_hours <= 9 or not (args.training_pid or args.finalize_now)):
        parser.error("Specify branch, output-dir, physical-gpu, and training-pid or finalize-now; max watch <=9h")
    args.output_dir = args.output_dir.resolve(); args.shared_parent_archive = args.shared_parent_archive.expanduser().resolve()
    if args.training_pid: watch(args)
    else:
        if any(matches_training(tools.process_argv(int(proc.name)), args.output_dir, args.branch, common_only=False) for proc in Path("/proc").glob("[0-9]*")):
            parser.error("This branch/output still has a live training process")
        finish(args)


if __name__ == "__main__": main()
