"""E02 Layer 2 launcher: 3 languages x 3 locked prompts x 2 seeds = 18 runs.

Runs four at a time across the four GPUs. Skips any cell whose output already
exists, so it is safe to re-run after an interruption.
"""
import itertools
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from e02_prompts import PROMPTS, prompt  # noqa: E402

PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
MODEL = (ROOT / ".modelpath").read_text().strip()
LOGS = ROOT / "results" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

cells = [(l, p, s) for l, p, s in
         itertools.product(("ca", "es", "ro"), PROMPTS, (0, 1))]
todo = [c for c in cells
        if not (ROOT / "results" / f"ks_select_l2_{c[0]}_{c[1]}_s{c[2]}.json").exists()]
print(f"{len(cells)} cells, {len(todo)} to run", flush=True)

running = []
for idx, (lang, p, seed) in enumerate(todo):
    while len(running) >= 4:
        running = [r for r in running if r[0].poll() is None]
        time.sleep(10)
    tag = f"l2_{lang}_{p}_s{seed}"
    head, tail = prompt(p, lang)
    gpu = next(g for g in range(4) if g not in {r[1] for r in running})
    log = open(LOGS / f"ks_{tag}.log", "w")
    proc = subprocess.Popen(
        [PY, str(ROOT / "src" / "ks_select.py"), "--model", MODEL, "--lang", lang,
         "--seed", str(seed), "--tag", tag, "--head", head, "--tail", tail],
        stdout=log, stderr=subprocess.STDOUT, cwd=str(ROOT),
        env={**__import__("os").environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    running.append((proc, gpu))
    print(f"[{idx+1}/{len(todo)}] {tag} -> gpu{gpu}", flush=True)
    time.sleep(5)

while running:
    running = [r for r in running if r[0].poll() is None]
    time.sleep(15)
print("all done", flush=True)
