"""Run E14's two independent branches and bound their own wrapper allocation.

Only this experiment's process groups may be stopped. Each physical GPU must
have >=75GB free and no existing compute process before its branch is launched.
The 6h training cap reserves 2h of the card's 8h total cap for evaluation.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

ROOT = Path("/var/tmp/xiang-data-rsi/e14")
REPO = Path("/home/xiang/ssn-group-papaer")
LAUNCHER = REPO / "workbench/data-centric-rsi/scripts/e14_run_train.py"
PYTHON = "/home/xiang/.venvs/data-centric-rsi/bin/python"
ACTION = "source_only_fresh"
TRAIN_CAP = 6 * 3600


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, value):
    temp = path.with_name(path.name + f".tmp.{os.getpid()}")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    temp.replace(path)


def start_ticks(pid):
    p = Path(f"/proc/{pid}/stat")
    return p.read_text().split()[21] if p.exists() else None


def available(gpu):
    rows = subprocess.check_output(["nvidia-smi", "--query-gpu=index,uuid,memory.free",
                                    "--format=csv,noheader,nounits"], text=True).splitlines()
    row = next(r for r in rows if int(r.split(",")[0]) == gpu)
    _, gpu_uuid, free = [v.strip() for v in row.split(",")]
    apps = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid",
                                    "--format=csv,noheader,nounits"], text=True)
    return int(free) >= 75000 and gpu_uuid not in apps, int(free)


def cap_reached(directory):
    p = directory / "budget_watch.json"
    if not p.exists(): return False
    budget = json.loads(p.read_text())
    return (budget["status"].startswith("cap_reached")
            or budget["conservative_queue_wrapper_seconds"] >= TRAIN_CAP)


def queue(gpu, expected_sha):
    assert gpu in (0, 1) and socket.gethostname().startswith("fvcrc12")
    directory = ROOT / "train_queue"
    directory.mkdir(exist_ok=True)
    path = directory / f"gpu{gpu}.json"
    assert not path.exists(), "Preserve existing E14 queue"
    parent = "init" if gpu == 0 else "used"
    state = {"node": socket.gethostname(), "gpu": gpu, "parent": parent,
             "action": ACTION, "created_utc": utc(), "driver_pid": os.getpid(),
             "driver_start_ticks": start_ticks(os.getpid()), "runs": [],
             "launcher_sha256": expected_sha, "training_cap_seconds": TRAIN_CAP}
    save(path, state)
    while True:
        if cap_reached(directory):
            state.update(status="failed", error="Training cap reached before launch")
            save(path, state); raise RuntimeError(state["error"])
        idle, free = available(gpu)
        if idle: break
        state["status"] = "waiting_for_free_gpu"; save(path, state); time.sleep(30)
    assert hashlib.sha256(LAUNCHER.read_bytes()).hexdigest() == expected_sha, "Launcher changed"
    run = ROOT / "train_runs" / f"{parent}_{ACTION}_s29"
    assert not run.exists(), "Never overwrite a prior run"
    command = [PYTHON, str(LAUNCHER), "--root", str(ROOT),
               "--e12-root", "/var/tmp/xiang-data-rsi/e12",
               "--init-parent", "/var/tmp/xiang-data-rsi/e12/llava_init",
               "--used-parent", "/var/tmp/xiang-data-rsi/e12/train_runs_v2/icons_exact_s17/model",
               "--processor-sentinel-path", "/var/tmp/xiang-data-rsi/e13/processor_sentinel",
               "--parent", parent, "--gpu", str(gpu), "--out-root", str(ROOT / "train_runs")]
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    entry = {"parent": parent, "action": ACTION, "gpu": gpu, "command": command,
             "started_utc": utc(), "run_dir": str(run),
             "prelaunch_free_mib": free, "prelaunch_no_compute_apps": True}
    state["runs"].append(entry); state["status"] = "running"; save(path, state)
    start = time.monotonic()
    with (directory / f"{parent}.stdout").open("x") as out, (directory / f"{parent}.stderr").open("x") as err:
        assert not cap_reached(directory), "Cap reached while preparing launch"
        p = subprocess.Popen(command, cwd=REPO, env=env, stdout=out, stderr=err,
                             start_new_session=True)
        entry.update(launcher_pid=p.pid, launcher_start_ticks=start_ticks(p.pid), process_group=p.pid)
        save(path, state)
        if cap_reached(directory):
            # Cover a cap-marker race between the last check and Popen.
            try: os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError: pass
        code = p.wait()
    entry.update(returncode=code, finished_utc=utc(),
                 queue_wrapper_wall_seconds=round(time.monotonic() - start, 3))
    state["status"] = "failed" if code else "completed"; save(path, state)
    assert code == 0, "Failed run is retained; no replacement seed"
    completion = json.loads((run / "completion.json").read_text())
    assert completion["returncode"] == 0 and completion["model_saved"] and completion["observed_windows"] == 625
    entry["completion"] = completion; save(path, state)


def watch():
    assert socket.gethostname().startswith("fvcrc12")
    directory = ROOT / "train_queue"; directory.mkdir(exist_ok=True)
    path = directory / "budget_watch.json"
    assert not path.exists(), "Preserve existing budget watch"
    while True:
        states = [json.loads(p.read_text()) for p in (directory / "gpu0.json", directory / "gpu1.json")
                  if p.exists()]
        spent = 0.0
        for state in states:
            for entry in state["runs"]:
                spent += entry.get("queue_wrapper_wall_seconds", (
                    dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(entry["started_utc"])
                ).total_seconds())
        snapshot = {"utc": utc(), "conservative_queue_wrapper_seconds": spent,
                    "train_cap_seconds": TRAIN_CAP, "total_train_eval_cap_seconds": 8 * 3600,
                    "evaluation_reserved_seconds": 2 * 3600, "status": "monitoring",
                    "scope": "Includes CPU preflight/import within launched queue wrappers; excludes waiting before launch"}
        if spent >= TRAIN_CAP:
            snapshot["status"] = "cap_reached_own_launchers_terminated"
            # Block queues that are still waiting before stopping active ones.
            save(path, snapshot)
            stopped = []
            for state in states:
                for entry in state["runs"]:
                    pid = entry.get("launcher_pid")
                    if not entry.get("finished_utc") and pid and start_ticks(pid) == entry["launcher_start_ticks"]:
                        try: os.killpg(entry["process_group"], signal.SIGTERM); stopped.append(pid)
                        except ProcessLookupError: pass
            snapshot.update(status="cap_reached_own_launchers_terminated", stopped_owned_pids=stopped)
            save(path, snapshot); return
        if len(states) == 2 and all(s.get("status") == "completed" for s in states):
            snapshot["status"] = "queues_completed"; save(path, snapshot); return
        if any(s.get("status") == "failed" for s in states):
            snapshot["status"] = "queue_failed_other_queue_monitored"
            if len(states) == 2 and all(s.get("status") in ("completed", "failed") for s in states):
                snapshot["status"] = "queue_failed_preserve_all_runs"; save(path, snapshot); return
        for state in states:
            if state.get("status") not in ("completed", "failed") and start_ticks(state["driver_pid"]) != state["driver_start_ticks"]:
                alive_launchers = [e for e in state["runs"] if e.get("launcher_pid")
                                   and start_ticks(e["launcher_pid"]) == e.get("launcher_start_ticks")]
                snapshot["status"] = "driver_missing_own_launcher_still_monitored"
                if not alive_launchers:
                    # Preserve the observation, and continue bounding any other
                    # live queue rather than leaving its allocation unmonitored.
                    snapshot.setdefault("missing_driver_pids", []).append(state["driver_pid"])
                    other_live = any(start_ticks(s["driver_pid"]) == s["driver_start_ticks"]
                                     and s.get("status") not in ("completed", "failed") for s in states)
                    any_owned_launcher_live = any(
                        e.get("launcher_pid") and start_ticks(e["launcher_pid"]) == e.get("launcher_start_ticks")
                        for s in states for e in s["runs"])
                    if not other_live and not any_owned_launcher_live:
                        snapshot["status"] = "drivers_missing_no_owned_launchers"; save(path, snapshot); return
        save(path, snapshot); time.sleep(30)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gpu", type=int); p.add_argument("--launcher-sha"); p.add_argument("--watch", action="store_true")
    a = p.parse_args()
    if a.watch: watch()
    else:
        assert a.gpu is not None and a.launcher_sha
        queue(a.gpu, a.launcher_sha)


if __name__ == "__main__": main()
