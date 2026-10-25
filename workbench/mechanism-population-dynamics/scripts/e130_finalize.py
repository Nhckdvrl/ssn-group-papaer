#!/usr/bin/env python3
"""One-shot E130 endpoint scoring/capture/archive; no score-based gates."""
from __future__ import annotations
import argparse, contextlib, gc, hashlib, json, os, re, shutil, socket, subprocess, tempfile, time
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
RESULTS, ARCHIVES = WB / "results/e130", Path.home() / "mechpop_cache"
STEPS, TOKENS, LATE = 62500, 512_000_000, 61440
DRIVER_SHA = "9446b337e084bdef19abfe46119058fe76fcb9ab3ef818a6ce9e7fcaac882167"
PLAN_SHA = "aa18964afe9f8b5b450d33e54159d8fed41c79d8901c3632b07ceabf523bb227"
FROZEN = {
    "e130_cross_seed.py": DRIVER_SHA,
    "e128_epoch_recovery.py": "754dd5fca994b15839c38eccdd5f9f156dc747bfa3be8a2f2b7f3f61d65b505f",
    "e125_coverage_control.py": "7bda110b67453f9642ec9e100b9e308fc7d0583abfe98876980184e28044b0b1",
    "e123_frozen_moe.py": "f874f0675ab4423173a542c6765d2504aab33cd2a28c7aa412b71f9308936c80",
    "e124_functional_capture.py": "4b4f861990e3e17dd6dd3fb98bb4aa69b6ee488d63d75b871276ef257d68dbae",
    "e127_predictive_fidelity.py": "ac37934d55891db7ab9ff873f04e9b7e4592de590917a477d0d84d9f83d1675c"}


def read(path):
    try: return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError): return None


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""): digest.update(block)
    return digest.hexdigest()


def ready(summary, failure):
    return (failure is None and isinstance(summary, dict) and summary.get("status") == "complete"
            and summary.get("step") == summary.get("planned_steps") == STEPS and summary.get("train_tokens") == TOKENS)


def argument(argv, name):
    for index, word in enumerate(argv):
        if word.startswith(name + "="): return word.split("=", 1)[1]
        if word == name and index + 1 < len(argv): return argv[index + 1]


def matches_training(argv, out):
    return (any(Path(word).name == "e130_cross_seed.py" for word in argv)
            and argument(argv, "--mode") == "train" and argument(argv, "--output") is not None
            and Path(argument(argv, "--output")).resolve() == out.resolve())


def process_argv(pid):
    try:
        proc = Path(f"/proc/{pid}")
        if proc.joinpath("stat").read_text().rsplit(")", 1)[1].split()[0] == "Z": return []
        return [word.decode(errors="replace") for word in proc.joinpath("cmdline").read_bytes().split(b"\0") if word]
    except (FileNotFoundError, ProcessLookupError, PermissionError): return []


def gpu_status(physical):
    try:
        uuid = subprocess.check_output(["nvidia-smi", "-i", str(physical), "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip()
        rows = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name", "--format=csv,noheader"], text=True)
        if not uuid.startswith("GPU-") or "\n" in uuid: raise ValueError("Expected one physical GPU UUID")
        processes = [row.strip() for row in rows.splitlines() if row.split(",", 1)[0].strip() == uuid]
        return {"physical_gpu": physical, "uuid": uuid, "compute_processes": processes}
    except Exception as error:
        return {"physical_gpu": physical, "query_error": f"{type(error).__name__}: {error}"}


def gpu_free(state):
    return "query_error" not in state and state.get("compute_processes") == []


def validate_checkpoint(path, summary, provenance, step):
    import torch
    checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    expected = {"step": step, "config_hash": summary["config_hash"], "frozen_sample_hash": provenance["frozen_sample_hash"],
                "initial_tensor_sha256": summary["initial_tensor_sha256"], "replacement_kind": "moe"}
    if any(checkpoint.get(key) != value for key, value in expected.items()):
        raise ValueError(f"Checkpoint metadata differs from registered E130: {path}")


def validate(out):
    summary, provenance, protocol = [read(out / name) for name in ("training_summary.json", "provenance.json", "driver_protocol.json")]
    if not ready(summary, read(out / "failure.json")): raise ValueError("Incomplete E130 endpoint or recorded training failure")
    if not isinstance(provenance, dict) or not isinstance(protocol, dict): raise ValueError("Missing provenance/protocol")
    actual = {name: sha(WB / "scripts" / name) for name in FROZEN}
    if actual != FROZEN: raise ValueError("Frozen E130 driver/trainer/evaluator/capture source hashes differ")
    args = provenance["args"]
    expected = {"steps": STEPS, "seq_len": 512, "batch_size": 16, "accum": 1, "max_train_tokens": TOKENS,
                "replacement": "moe", "layer": 9, "experts": 64, "expert_size": 1024, "top_k": 8,
                "dtype": "bfloat16", "lr": 3e-4, "warmup_fraction": .1, "weight_decay": .1,
                "lb_coef": .01, "z_coef": .001, "init_std": .02, "grad_clip": 1., "max_hours": 8.}
    if any(args.get(key) != value for key, value in expected.items()): raise ValueError("E130 registered training arguments differ")
    if (args["seed"], args["order_seed"]) not in {(i, 0) for i in range(5)} | {(0, 1)}: raise ValueError("Unregistered seed/order")
    source_subset = {key: value for key, value in FROZEN.items() if key not in ("e130_cross_seed.py", "e127_predictive_fidelity.py")}
    if (protocol.get("experiment") != "E130" or protocol.get("cpu_test") is not False
            or protocol.get("driver_sha256") != DRIVER_SHA or args.get("driver_sha256") != DRIVER_SHA
            or protocol.get("frozen_source_sha256") != source_subset
            or protocol.get("steps") != STEPS or protocol.get("target_tokens") != TOKENS
            or any(protocol.get(key) != args[key] for key in ("seed", "order_seed"))):
        raise ValueError("E130 driver protocol/hash mismatch")
    if (summary.get("config_hash") != provenance.get("config_hash") or summary.get("run_id") != provenance.get("run_id")
            or summary.get("frozen_sample_hash_before") != summary.get("frozen_sample_hash_after")
            or summary.get("frozen_sample_hash_after") != provenance.get("frozen_sample_hash")
            or protocol.get("expected_frozen_sample_hash") != provenance.get("frozen_sample_hash")
            or summary.get("initial_tensor_sha256") != provenance.get("initial_tensor_sha256")
            or summary.get("initial_tensor_sha256") != protocol.get("initial_tensor_sha256")
            or summary.get("initial_tensor_sha256") != args.get("expected_initial_tensor_sha256")):
        raise ValueError("Summary/provenance/driver initialization or frozen fingerprint mismatch")
    validate_checkpoint(out / "checkpoint.pt", summary, provenance, STEPS)
    return summary, provenance, protocol


def scoped_guard(old, step, expected, reference, registered):
    if expected == STEPS:
        if not registered or reference or step != STEPS: raise ValueError("62500 allowed only for a validated E130 endpoint")
        return
    return old(step, expected, reference)


@contextlib.contextmanager
def evaluator_guard(module, registered):
    old = module.guard_step
    module.guard_step = lambda step, expected, reference: scoped_guard(old, step, expected, reference, registered)
    try: yield
    finally: module.guard_step = old


def fidelity(out, path):
    import e127_predictive_fidelity as evaluator
    validate(out)  # The scoped exception cannot be used directly on an unvalidated run.
    args = argparse.Namespace(checkpoint=str(out / "checkpoint.pt"), model=None, data=None, device="cuda:0",
                              output=str(path), expected_step=STEPS, reference_calibration=False, bootstrap=1000)
    with evaluator_guard(evaluator, True): result = evaluator.evaluate(args)
    result.update({"experiment": "E130", "e130_driver_sha256": DRIVER_SHA, "host": socket.gethostname(),
                   "training_provenance": str(out / "provenance.json"),
                   "guard_scope": "Validated E130 endpoint only; original E127 guard restored after this call"})
    write(path, result)


def capture(out, provenance, label, path, run_id):
    import e124_functional_capture as functional
    args = provenance["args"]
    checkpoint = out / "checkpoint.pt" if label == "final" else out / "snapshots/step061440.pt"
    validate_checkpoint(checkpoint, read(out / "training_summary.json"), provenance, STEPS if label == "final" else LATE)
    if sha(WB / "results/e124/plan.json") != PLAN_SHA: raise ValueError("Fixed E124 sample plan SHA differs")
    settings = functional.parser().parse_args(["--mode", "capture", "--model", args["model"], "--data", args["data"],
        "--checkpoint", str(checkpoint), "--output", str(out / f"functional_{label}.npz"), "--summary", str(path),
        "--plan", str(WB / "results/e124/plan.json"), "--run-id", f"{run_id}_{label}",
        "--seed", str(args["seed"]), "--order-seed", str(args["order_seed"]), "--device", "cuda:0",
        "--dtype", "bfloat16", "--batch-size", "16", "--alpha", "0.125", "--cal-sequences", "64",
        "--seq-len", "512", "--cal-stride", "4"])
    _, summary = functional.capture(settings)
    summary.update({"experiment": "E130", "host": socket.gethostname(), "training_provenance": str(out / "provenance.json")})
    write(path, summary)


def archive(out, run_id, state, labels):
    destination = ARCHIVES / f"e130_{run_id}_512m"
    checkpoint_sha = sha(out / "checkpoint.pt")
    previous = read(destination / "archive_manifest.json")
    if destination.exists() and (not previous or previous.get("checkpoint_sha256") != checkpoint_sha):
        raise FileExistsError(f"Archive exists with a different/unverified checkpoint: {destination}")
    staging = destination if destination.exists() else destination.with_name(destination.name + ".partial")
    if staging != destination: staging.mkdir(parents=True, exist_ok=False)
    names = ("checkpoint.pt", "provenance.json", "driver_protocol.json", "gradient_audit.json", "training_summary.json",
             "final_held_sequences.json", "final_pos.json")
    sources = {name: out / name for name in names}
    sources.update({f"functional_{label}.npz": out / f"functional_{label}.npz" for label in labels})
    sources.update({f"functional_{label}.json": RESULTS / "functional" / f"{run_id}_{label}.json" for label in labels})
    sources.update({"fidelity.json": RESULTS / "fidelity" / f"{run_id}.json",
                    "fidelity_sequences.json": RESULTS / "fidelity" / f"{run_id}_sequences.json"})
    files, missing = {}, []
    for name, source in sources.items():
        if not source.is_file(): missing.append(str(source)); continue
        target = staging / name; source_sha = sha(source)
        if target.exists():
            if sha(target) != source_sha: raise FileExistsError(f"Archived file differs: {target}")
        else:
            partial = target.with_suffix(target.suffix + ".partial"); shutil.copy2(source, partial)
            if sha(partial) != source_sha: raise IOError(f"Archive SHA mismatch: {source}")
            partial.rename(target)
        files[name] = {"sha256": source_sha, "size_bytes": target.stat().st_size}
    if missing and (state["status"] == "complete" or any(str(out / name) in missing for name in names)):
        state["status"] = "archive_incomplete"
    write(staging / "postprocessing.json", state)
    files["postprocessing.json"] = {"sha256": sha(staging / "postprocessing.json"), "size_bytes": (staging / "postprocessing.json").stat().st_size}
    manifest = {"experiment": "E130", "host": socket.gethostname(), "run_id": run_id,
                "checkpoint_sha256": checkpoint_sha, "files": files, "missing_sources": missing,
                "snapshot_optimizer_scope": "Not archived; original NVMe snapshot remains untouched"}
    write(staging / "archive_manifest.json", manifest)
    if staging != destination: staging.rename(destination)
    return destination, manifest


def finish(args):
    out, run_id = args.output_dir, args.run_id
    state = {"experiment": "E130", "run_id": run_id, "host": socket.gethostname(), "output_dir": str(out),
             "training_provenance": str(out / "provenance.json"), "finalizer_sha256": sha(__file__), "errors": {}}
    path = RESULTS / "finalization" / f"{run_id}.json"
    try: summary, provenance, protocol = validate(out)
    except Exception as error:
        write(path, {**state, "status": "validation_failed", "errors": {"validation": f"{type(error).__name__}: {error}"}}); return
    labels = ["final", "late"] if provenance["args"]["seed"] in range(1, 5) and provenance["args"]["order_seed"] == 0 else ["final"]
    gpu = gpu_status(args.physical_gpu); state.update({"gpu_preflight": gpu, "config_hash": summary["config_hash"],
        "driver_sha256": DRIVER_SHA, "training_run_id": provenance["run_id"], "step": STEPS, "train_tokens": TOKENS})
    if gpu_free(gpu):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.physical_gpu)
        jobs = [("fidelity", lambda: fidelity(out, RESULTS / "fidelity" / f"{run_id}.json"))]
        jobs += [(f"functional_{label}", lambda label=label: capture(out, provenance, label,
                  RESULTS / "functional" / f"{run_id}_{label}.json", run_id)) for label in labels]
        for name, job in jobs:
            try: job()
            except Exception as error: state["errors"][name] = f"{type(error).__name__}: {error}"
            finally:
                try:
                    import torch
                    gc.collect()
                    if torch.cuda.is_initialized(): torch.cuda.empty_cache()
                except Exception as error: state["errors"][name + "_cleanup"] = f"{type(error).__name__}: {error}"
        state["status"] = "postprocessing_failed" if state["errors"] else "complete"
    else: state["status"] = "evaluation_deferred_gpu_busy_or_unavailable"
    try:
        destination, manifest = archive(out, run_id, state, labels)
        state.update({"archive": str(destination), "archive_manifest_sha256": sha(destination / "archive_manifest.json"),
                      "checkpoint_sha256": manifest["checkpoint_sha256"], "missing_archive_sources": manifest["missing_sources"]})
    except Exception as error:
        state["status"] = "archive_failed"; state["errors"]["archive"] = f"{type(error).__name__}: {error}"
    write(path, state)


def watch(args):
    deadline, observed = time.monotonic() + args.max_watch_hours * 3600, False
    path = RESULTS / "finalization" / f"{args.run_id}.json"
    while time.monotonic() < deadline:
        argv = process_argv(args.training_pid)
        if argv and not matches_training(argv, args.output_dir):
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
    complete = {"status": "complete", "step": STEPS, "planned_steps": STEPS, "train_tokens": TOKENS}
    assert ready(complete, None) and not ready({**complete, "step": 64}, None) and not ready(complete, {})
    old = evaluator.guard_step
    assert {name: sha(WB / "scripts" / name) for name in FROZEN} == FROZEN
    with evaluator_guard(evaluator, True):
        evaluator.guard_step(STEPS, STEPS, False); evaluator.guard_step(15625, 15625, False); evaluator.guard_step(3906, 3906, True)
    assert evaluator.guard_step is old
    for check in ((STEPS, STEPS, False, False), (STEPS, STEPS, True, True), (64, STEPS, False, True), (3906, 3906, False, True)):
        try: scoped_guard(old, *check)
        except ValueError: pass
        else: raise AssertionError(f"Scoped guard accepted {check}")
    assert gpu_free({"compute_processes": []}) and not gpu_free({"compute_processes": ["occupied"]}) and not gpu_free({"query_error": "unknown"})
    with tempfile.TemporaryDirectory(prefix="e130_finalizer_cpu_") as directory:
        root = Path(directory); (root / "checkpoint.pt").write_bytes(b"CPU archive sentinel; not a model")
        for name in ("provenance.json", "driver_protocol.json", "gradient_audit.json", "training_summary.json",
                     "final_held_sequences.json", "final_pos.json"): write(root / name, {})
        args = argparse.Namespace(output_dir=root, run_id="self_test", physical_gpu=3)
        provenance = {"args": {"seed": 0, "order_seed": 1}, "run_id": "test"}
        assert matches_training(["python", "e130_cross_seed.py", "--mode", "train", "--output", str(root)], root)
        assert not matches_training(["python", "e130_cross_seed.py", "--mode", "train", "--output", str(root) + "_other"], root)
        with contextlib.ExitStack() as stack:
            module = sys.modules[__name__]
            for name, value in (("RESULTS", root / "results"), ("ARCHIVES", root / "archive")):
                stack.enter_context(patch.object(module, name, value))
            stack.enter_context(patch.object(module, "validate", return_value=({**complete, "config_hash": "test"}, provenance, {})))
            stack.enter_context(patch.object(module, "gpu_status", return_value={"compute_processes": ["busy"]}))
            score = stack.enter_context(patch.object(module, "fidelity", side_effect=AssertionError("GPU scoring while busy")))
            bank = stack.enter_context(patch.object(module, "capture", side_effect=AssertionError("GPU capture while busy")))
            finish(args); score.assert_not_called(); bank.assert_not_called()
            result = read(root / "results/finalization/self_test.json")
            assert result["gpu_preflight"]["compute_processes"] == ["busy"] and result["archive"]
            assert result["status"] == "evaluation_deferred_gpu_busy_or_unavailable"
            assert result["missing_archive_sources"] and not result["errors"]
    result = {"passed": True, "device": "cpu", "finalizer_sha256": sha(__file__), "readiness_rejects_incomplete_or_failure": True,
              "strict_scoped_guard_and_restoration": True, "busy_gpu_never_scores_or_captures_but_archives": True,
              "missing_archive_sources_explicit": True, "exact_training_output_identity": True, "no_GPU_allocation": True}
    write(RESULTS / "finalizer_self_test.json", result); print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--training-pid", type=int); mode.add_argument("--finalize-now", action="store_true")
    parser.add_argument("--output-dir", type=Path); parser.add_argument("--run-id")
    parser.add_argument("--physical-gpu", type=int); parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--max-watch-hours", type=float, default=9.)
    args = parser.parse_args()
    if args.self_test: self_test(); return
    if (not args.output_dir or not args.run_id or not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id)
            or args.physical_gpu is None or args.physical_gpu < 0 or args.poll_seconds < 1 or not 0 < args.max_watch_hours <= 9
            or not (args.training_pid or args.finalize_now)):
        parser.error("Specify output-dir, safe run-id, physical-gpu and training-pid or finalize-now; watch budget <=9h")
    args.output_dir = args.output_dir.resolve()
    if args.training_pid: watch(args)
    else:
        if any(matches_training(process_argv(int(proc.name)), args.output_dir) for proc in Path("/proc").glob("[0-9]*")):
            parser.error("Training still runs for this output; use --training-pid to watch")
        finish(args)


if __name__ == "__main__": main()
