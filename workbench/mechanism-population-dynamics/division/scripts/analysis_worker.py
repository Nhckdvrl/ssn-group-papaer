#!/usr/bin/env python3
"""Process E167 checkpoints as they appear: routing capture (R1–R3) then R0/route fingerprints.

Runs until every run has DONE.json and every checkpoint is processed. R4 (per-expert
drop fingerprints) is run only for tokens listed in --r4-tokens.

Usage: analysis_worker.py [--r4-tokens 800000000,4000000000]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

RUNS = Path("/home/xiang/mechpop_cache/e167_runs")
CAP = Path("/home/xiang/mechpop_cache/e167_analysis/routing")
FUN = Path("/home/xiang/mechpop_cache/e167_analysis/functional")
HERE = Path(__file__).parent
PY = str(Path.home() / ".venvs/mechpop/bin/python")


def pending():
    todo = []
    for ck in sorted(RUNS.glob("*/ckpt_*.pt"), key=lambda p: int(p.stem.split("_")[1])):
        name = f"{ck.parent.name}__{ck.stem}.npz"
        if not (CAP / name).exists():
            todo.append(("cap", ck))
        if not (FUN / name).exists():
            todo.append(("fun", ck))
    return todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r4-tokens", default="800000000,4000000000")
    a = ap.parse_args()
    r4 = {int(x) for x in a.r4_tokens.split(",") if x}
    CAP.mkdir(parents=True, exist_ok=True)
    FUN.mkdir(parents=True, exist_ok=True)
    while True:
        todo = pending()
        if not todo:
            runs = [p for p in RUNS.iterdir() if p.is_dir()]
            if runs and all((p / "DONE.json").exists() for p in runs):
                print("all done", flush=True)
                return
            time.sleep(300)
            continue
        kind, ck = todo[0]
        t = int(ck.stem.split("_")[1])
        if kind == "cap":
            cmd = [PY, "-B", str(HERE / "capture_routing.py"), str(CAP), str(ck)]
        else:
            cmd = [PY, "-B", str(HERE / "functional_probe.py"), str(FUN)] + ([] if t in r4 else ["--no-r4"]) + [str(ck)]
        print(time.strftime("%H:%M:%S"), kind, ck, flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = [l for l in r.stdout.splitlines() + r.stderr.splitlines() if "arn" not in l][-3:]
        print("  rc", r.returncode, *tail, sep="\n  ", flush=True)
        if r.returncode != 0:
            time.sleep(60)


if __name__ == "__main__":
    sys.exit(main())
