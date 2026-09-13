"""E02 Layer 3 launcher: lang x rows_from x eval_prompt x seed = 16 runs."""
import itertools, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
MODEL = (ROOT / ".modelpath").read_text().strip()
LOGS = ROOT / "results" / "logs"; LOGS.mkdir(parents=True, exist_ok=True)

cells = list(itertools.product(("ca", "es"), ("P1_explicit", "P2_render"),
                               ("P1_explicit", "P2_render"), (0, 1)))
todo = [c for c in cells if not
        (ROOT / "results" / "e02_l3" /
         f"{c[0]}_rows-{c[1]}_at-{c[2]}_s{c[3]}.json").exists()]
print(f"{len(cells)} cells, {len(todo)} to run", flush=True)
running = []
for i, (lang, rows, at, seed) in enumerate(todo):
    while len(running) >= 4:
        running = [r for r in running if r[0].poll() is None]; time.sleep(10)
    gpu = next(g for g in range(4) if g not in {r[1] for r in running})
    name = f"{lang}_rows-{rows}_at-{at}_s{seed}"
    log = open(LOGS / f"l3_{name}.log", "w")
    p = subprocess.Popen(
        [PY, str(ROOT/"src"/"e02_layer3.py"), "--model", MODEL, "--lang", lang,
         "--ticket-from", rows, "--train-prompt", at, "--seed", str(seed)],
        stdout=log, stderr=subprocess.STDOUT, cwd=str(ROOT),
        env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    running.append((p, gpu)); print(f"[{i+1}/{len(todo)}] {name} -> gpu{gpu}", flush=True)
    time.sleep(5)
while running:
    running = [r for r in running if r[0].poll() is None]; time.sleep(15)
print("all done", flush=True)
