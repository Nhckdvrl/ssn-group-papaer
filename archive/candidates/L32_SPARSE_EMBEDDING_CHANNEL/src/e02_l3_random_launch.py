"""Chained control: frequency-matched random NON-template tickets.

Waits for the Layer 3 launcher to finish, then runs the control that
disambiguates a transfer ratio near 1 -- does ticket identity matter at all?
Four cells: ca and es, P1_explicit, seeds 0 and 1.
"""
import os, pathlib, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
MODEL = (ROOT / ".modelpath").read_text().strip()
LOGS = ROOT / "results" / "logs"
launcher_log = LOGS / "e02_l3_launch.log"

while "all done" not in launcher_log.read_text():
    time.sleep(60)
print("layer3 finished, starting random-ticket control", flush=True)

cells = [(l, s) for l in ("ca", "es") for s in (0, 1)]
running = []
for i, (lang, seed) in enumerate(cells):
    while len(running) >= 4:
        running = [r for r in running if r[0].poll() is None]
        time.sleep(10)
    gpu = next(g for g in range(4) if g not in {r[1] for r in running})
    name = f"{lang}_rand_s{seed}"
    log = open(LOGS / f"l3rand_{name}.log", "w")
    p = subprocess.Popen(
        [PY, str(ROOT/"src"/"e02_layer3.py"), "--model", MODEL, "--lang", lang,
         "--ticket-from", "P1_explicit", "--train-prompt", "P1_explicit",
         "--seed", str(seed), "--random-ticket", str(1000 + seed)],
        stdout=log, stderr=subprocess.STDOUT, cwd=str(ROOT),
        env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    running.append((p, gpu))
    print(f"[{i+1}/{len(cells)}] {name} -> gpu{gpu}", flush=True)
    time.sleep(5)
while running:
    running = [r for r in running if r[0].poll() is None]
    time.sleep(15)
print("all done", flush=True)
