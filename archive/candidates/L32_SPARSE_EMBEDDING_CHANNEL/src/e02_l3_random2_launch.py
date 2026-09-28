"""Second random control, with BOS/EOS excluded from the sampling pool."""
import os, pathlib, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
MODEL = (ROOT / ".modelpath").read_text().strip()
LOGS = ROOT / "results" / "logs"
prev = LOGS / "e02_l3_random_launch.log"
while "all done" not in prev.read_text():
    time.sleep(60)
print("variant A finished, starting no-special variant", flush=True)
running = []
cells = [(l, s) for l in ("ca", "es") for s in (0, 1)]
for i, (lang, seed) in enumerate(cells):
    while len(running) >= 4:
        running = [r for r in running if r[0].poll() is None]; time.sleep(10)
    gpu = next(g for g in range(4) if g not in {r[1] for r in running})
    log = open(LOGS / f"l3rand2_{lang}_s{seed}.log", "w")
    p = subprocess.Popen(
        [PY, str(ROOT/"src"/"e02_layer3.py"), "--model", MODEL, "--lang", lang,
         "--ticket-from", "P1_explicit", "--train-prompt", "P1_explicit",
         "--seed", str(seed), "--random-ticket", str(1000 + seed),
         "--random-exclude-special"],
        stdout=log, stderr=subprocess.STDOUT, cwd=str(ROOT),
        env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    running.append((p, gpu)); print(f"[{i+1}/4] {lang}_s{seed} -> gpu{gpu}", flush=True)
    time.sleep(5)
while running:
    running = [r for r in running if r[0].poll() is None]; time.sleep(15)
print("all done", flush=True)
