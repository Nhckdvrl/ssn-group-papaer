#!/usr/bin/env python3
"""E173 GPU queue (started 2026-11-05 with the main session's OK; rules from its message):
  1. Allowed slots only: fvcrc11 GPU0-3, fvcrc15 GPU0-3, fvcrc10 GPU0-3 (GPU0/2/3 added 2026-11-06 on the user's word).
     Never fvcrc12/13/20/21.
  2. A slot is launched on only after two consecutive checks INTERVAL apart both saw it with no compute process and
     memory.used < 1000 MiB (e173_launch.sh re-checks at launch time).
  3. Batch 1 = seed 0 of (e) FRZ, (a) LB0, (c) G16, (d) G256, at most 4 alive. Batch 2 (seed 1 of those four, then (b)
     LB01 seed 0 and 1; cap 8 alive) starts only when all four batch-1 runs are stable: train_log reached step >= 500
     with finite CE, or the run finished with DONE.json. A batch-1 run that died blocks batch 2 (logged; human decides).
Every decision goes to results/e173/_logs/queue.log. Run state is read from the per-run console logs, no GPU use here.
"""
import json
import math
import subprocess
import time
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
LOGS = WB / "results/e173/_logs"
RUNS = Path.home() / "mechpop_cache/e173_runs"
LAUNCH = WB / "scripts/e173_launch.sh"
# 2026-11-06 00:45: fvcrc10 GPU0/2/3 added (user via main session: "你随便找个空卡"; they are freed vLLM cards of our own line)
SLOTS = [("fvcrc11", g) for g in range(4)] + [("fvcrc15", g) for g in range(4)] + [("fvcrc10", g) for g in range(4)]
BATCH1 = [("FRZ", 0), ("LB0", 0), ("G16", 0), ("G256", 0)]
BATCH2 = [("FRZ", 1), ("LB0", 1), ("G16", 1), ("G256", 1), ("LB01", 0), ("LB01", 1)]
INTERVAL = 600
STABLE_STEP = 500
QLOG = LOGS / "queue.log"


def log(msg):
    with open(QLOG, "a") as f:
        f.write(time.strftime("%F %T ") + msg + "\n")


def name(r):
    return f"{r[0]}_I{r[1]}"


def started(r):
    return (LOGS / f"{name(r)}.log").exists()


def finished(r):  # job ended (success or failure)
    f = LOGS / f"{name(r)}.log"
    return f.exists() and any(s in f.read_text(errors="ignore") for s in ("job done", "no DONE.json"))


def alive(r):
    return started(r) and not finished(r)


def stable(r):
    d = RUNS / name(r)
    if (d / "DONE.json").exists():
        return True
    tl = d / "train_log.jsonl"
    if not tl.exists():
        return False
    last = None
    for line in open(tl):
        try:
            x = json.loads(line)
        except ValueError:
            continue
        if "step" in x:
            last = x
    return last is not None and last["step"] >= STABLE_STEP and math.isfinite(last["ce"])


def idle_slots():
    out = set()
    for host in sorted({h for h, _ in SLOTS}):
        cmd = ("busy=$(nvidia-smi --query-compute-apps=gpu_uuid --format=csv,noheader | sort -u); "
               "nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader,nounits | "
               "while IFS=', ' read i u m; do if ! echo \"$busy\" | grep -q \"$u\" && [ \"$m\" -lt 1000 ]; then echo $i; fi; done")
        try:
            r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, cmd],
                               capture_output=True, text=True, timeout=90)
            idx = {int(x) for x in r.stdout.split()}
        except Exception as e:  # unreachable host: treat as no idle slots
            log(f"check {host} failed: {e!r}")
            idx = set()
        out |= {(host, g) for g in idx if (host, g) in SLOTS}
    return out


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    log("queue start; slots " + " ".join(f"{h}:{g}" for h, g in SLOTS) + f"; interval {INTERVAL}s")
    prev_idle = set()
    blocked_noted = False
    while True:
        b1_done_starting = all(started(r) for r in BATCH1)
        dead_b1 = [name(r) for r in BATCH1 if finished(r) and not (RUNS / name(r) / "DONE.json").exists()]
        b2_open = b1_done_starting and all(stable(r) for r in BATCH1) and not dead_b1
        if dead_b1 and not blocked_noted:
            log(f"batch-1 run(s) died without DONE.json: {dead_b1}; batch 2 blocked until a human decides")
            blocked_noted = True
        pending = [r for r in BATCH1 if not started(r)] + ([r for r in BATCH2 if not started(r)] if b2_open else [])
        cap = 8 if b2_open else 4
        n_alive = sum(alive(r) for r in BATCH1 + BATCH2)
        if not pending and all(started(r) for r in BATCH1 + BATCH2):
            log("all runs launched; queue exits")
            return
        now_idle = idle_slots()
        confirmed = sorted(now_idle & prev_idle)
        log(f"idle now {sorted(now_idle)}; confirmed twice {confirmed}; alive {n_alive}/{cap}; batch2 {'open' if b2_open else 'closed'}; "
            f"pending {[name(r) for r in pending]}")
        launched = set()
        for host, g in confirmed:
            if not pending or n_alive >= cap:
                break
            r = pending[0]
            p = subprocess.run(["bash", str(LAUNCH), host, str(g), r[0], str(r[1])], capture_output=True, text=True, timeout=1800)
            log(f"launch {name(r)} on {host}:{g} rc={p.returncode} {p.stdout.strip()} {p.stderr.strip()[-300:]}")
            if p.returncode == 0:
                pending.pop(0); n_alive += 1; launched.add((host, g))
        prev_idle = now_idle - launched
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
