"""Shard a condition plan by model and GPU; one model load per shard."""
import argparse, json, os, pathlib, subprocess, threading, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = "/home/xiang/miniconda3/envs/verl-clean/bin/python"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--gpus", default="0,1,2,3")
    a = ap.parse_args()
    plan = json.loads((ROOT / a.plan).read_text())
    gpus = a.gpus.split(",")

    pending = [j for j in plan["jobs"] if not (ROOT / j["out"]).exists()]
    by_model = {}
    for j in pending:
        by_model.setdefault(j["model"], []).append(j)
    print(f"{len(pending)} pending across {len(by_model)} models, {len(gpus)} gpus")

    # round-robin each model's jobs across the GPU pool
    shards = {g: [] for g in gpus}
    for jobs in by_model.values():
        per = {g: [] for g in gpus}
        for i, j in enumerate(jobs):
            per[gpus[i % len(gpus)]].append(j)
        for g in gpus:
            if per[g]:
                shards[g].append((jobs[0]["model"], per[g]))

    logdir = ROOT / "results" / "_logs"; logdir.mkdir(parents=True, exist_ok=True)
    tmpdir = ROOT / "results" / "_shards"; tmpdir.mkdir(parents=True, exist_ok=True)

    def worker(g):
        for si, (model, jobs) in enumerate(shards[g]):
            tag = f"{model.split('/')[-1]}__gpu{g}"
            jf = tmpdir / f"{tag}.json"
            jf.write_text(json.dumps(
                [{**j, "out": str(ROOT / j["out"])} for j in jobs], indent=1))
            cmd = [PY, str(ROOT / "scripts/run_eval.py"),
                   "--model", model, "--jobs", str(jf)]
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, HF_HUB_OFFLINE="1",
                       TOKENIZERS_PARALLELISM="false")
            t0 = time.time()
            with open(logdir / f"{tag}.log", "w") as lf:
                r = subprocess.run(cmd, env=env, stdout=lf, stderr=subprocess.STDOUT)
            print(f"[gpu{g}] {tag} {len(jobs)} jobs rc={r.returncode} "
                  f"{time.time()-t0:.0f}s", flush=True)

    ts = [threading.Thread(target=worker, args=(g,)) for g in gpus]
    for t in ts: t.start()
    for t in ts: t.join()
    print("ALL DONE")


if __name__ == "__main__":
    main()
