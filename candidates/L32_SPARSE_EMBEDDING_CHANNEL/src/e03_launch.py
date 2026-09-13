"""E03: single-row sufficiency. 2 rows x 2 languages x 2 seeds = 8 runs."""
import itertools, os, pathlib, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
MODEL = (ROOT / ".modelpath").read_text().strip()
LOGS = ROOT / "results" / "logs"; LOGS.mkdir(parents=True, exist_ok=True)
ROWS = {"bosonly": "1", "nlonly": "13"}
cells = [(l, r, s) for l, r, s in itertools.product(("ca", "es"), ROWS, (0, 1))]
todo = [c for c in cells if not
        (ROOT / "results" / "e02_l3" / f"{c[0]}_{c[1]}_s{c[2]}.json").exists()]
print(f"{len(todo)} runs", flush=True)
running = []
for i, (lang, label, seed) in enumerate(todo):
    while len(running) >= 4:
        running = [r for r in running if r[0].poll() is None]; time.sleep(10)
    gpu = next(g for g in range(4) if g not in {r[1] for r in running})
    log = open(LOGS / f"e03_{lang}_{label}_s{seed}.log", "w")
    p = subprocess.Popen(
        [PY, str(ROOT/"src"/"e02_layer3.py"), "--model", MODEL, "--lang", lang,
         "--ticket-from", "P1_explicit", "--train-prompt", "P1_explicit",
         "--seed", str(seed), "--explicit-rows", ROWS[label], "--label", label],
        stdout=log, stderr=subprocess.STDOUT, cwd=str(ROOT),
        env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    running.append((p, gpu)); print(f"[{i+1}/{len(todo)}] {lang}_{label}_s{seed} -> gpu{gpu}", flush=True)
    time.sleep(5)
while running:
    running = [r for r in running if r[0].poll() is None]; time.sleep(15)
print("all done", flush=True)
