"""E04 launcher: 3 models x 2 languages x 5 runs = 30. Four at a time."""
import glob, itertools, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/openslime/bin/python"
LOGS = ROOT / "results" / "logs"; LOGS.mkdir(parents=True, exist_ok=True)
H = "/home/xiang/.cache/huggingface/hub"
MODELS = {
  "llama1-7b":   glob.glob(f"{H}/models--huggyllama--llama-7b/snapshots/*")[0],
  "llama3.1-8b": glob.glob(f"{H}/models--NousResearch--Meta-Llama-3.1-8B/snapshots/*")[0],
  "qwen2.5-7b":  glob.glob(f"{H}/models--Qwen--Qwen2.5-7B/snapshots/*")[0],
}
CONDS = [("FULL_EMBED",0),("ROW_SEP",0),("ROW_SEP",1),("ROW_COLON",0),("ROW_RAND",0)]
cells=[(m,l,c,s) for m,l,(c,s) in itertools.product(MODELS,("ca","es"),CONDS)]
todo=[c for c in cells if not (ROOT/"results"/"e04"/f"{c[0]}_{c[1]}_{c[2]}_s{c[3]}.json").exists()]
print(f"{len(cells)} cells, {len(todo)} to run", flush=True)
running=[]
for i,(mn,lang,cond,seed) in enumerate(todo):
    while len(running)>=4:
        running=[r for r in running if r[0].poll() is None]; time.sleep(10)
    gpu=next(g for g in range(4) if g not in {r[1] for r in running})
    tag=f"{mn}_{lang}_{cond}_s{seed}"
    log=open(LOGS/f"e04_{tag}.log","w")
    p=subprocess.Popen([PY,str(ROOT/"src"/"e04.py"),"--model-path",MODELS[mn],
        "--model-name",mn,"--lang",lang,"--cond",cond,"--seed",str(seed)],
        stdout=log,stderr=subprocess.STDOUT,cwd=str(ROOT),
        env={**os.environ,"CUDA_VISIBLE_DEVICES":str(gpu)})
    running.append((p,gpu)); print(f"[{i+1}/{len(todo)}] {tag} -> gpu{gpu}",flush=True)
    time.sleep(5)
while running:
    running=[r for r in running if r[0].poll() is None]; time.sleep(15)
print("all done", flush=True)
