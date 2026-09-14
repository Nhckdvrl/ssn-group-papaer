"""L34 E01 runner.  python run.py trunk | python run.py arm --arm PIT_A --seed 0"""
import argparse, json, os, sys, time, random
import torch, numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import data, train, evaluate

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "results", "e01")
CKPT = os.environ.get("L34_CKPT_DIR", "/home/xiang/l34_e01_ckpt")

# frozen schedule (E01_PREREGISTRATION.md §3)
EP = {"0a": 3, "0b": 8, "1": 3, "2": 8}
LR = {"0a": 1e-5, "0b": 1e-5, "1": 1e-5, "2": 1e-5}
BS = 32
if os.environ.get("L34_EP"): EP.update(json.loads(os.environ["L34_EP"]))
if os.environ.get("L34_SMOKE"): _SM = int(os.environ["L34_SMOKE"])
else: _SM = 0


def log_to(path):
    f = open(path, "a", buffering=1)
    def log(*a):
        m = " ".join(str(x) for x in a)
        print(m, flush=True); f.write(m + "\n")
    return log


def load(path, log):
    log(f"loading {path}")
    tok = AutoTokenizer.from_pretrained(path)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, attn_implementation="sdpa").cuda()
    return m, tok


def seed_all(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["trunk", "arm"])
    ap.add_argument("--arm", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--base", default="Qwen/Qwen2.5-3B")
    ap.add_argument("--tag", default="q3b")
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True); os.makedirs(CKPT, exist_ok=True)
    sets, pools = data.load()
    if _SM:
        for k in sets: sets[k] = sets[k][:_SM]
    trunk = os.path.join(CKPT, f"trunk_{a.tag}")

    if a.mode == "trunk":
        log = log_to(os.path.join(ROOT, "results", "logs", f"e01_{a.tag}_trunk.log"))
        log(f"=== TRUNK {a.tag} base={a.base} {time.ctime()}")
        seed_all(0)
        m, tok = load(a.base, log)
        train.train_phase(m, tok, data.phase0a(sets), EP["0a"], LR["0a"], 101, BS, log, "p0a")
        train.train_phase(m, tok, data.phase0b(sets), EP["0b"], LR["0b"], 102, BS, log, "p0b")
        m.config.use_cache = True
        m.save_pretrained(trunk, safe_serialization=True); tok.save_pretrained(trunk)
        log(f"trunk saved -> {trunk}")
        return

    name = f"{a.tag}_{a.arm}_s{a.seed}"
    log = log_to(os.path.join(ROOT, "results", "logs", f"e01_{name}.log"))
    log(f"=== ARM {name} {time.ctime()}")
    seed_all(1000 + a.seed)
    m, tok = load(trunk, log)
    items = data.eval_items(sets, pools)

    # Phase 1: the access curriculum
    train.train_phase(m, tok, data.phase1(sets, a.arm, a.seed), EP["1"], LR["1"], 3000 + a.seed, BS, log, "p1")

    # G1 instrument check: OLD-fact access specialisation immediately after the curriculum
    old_items = [it for it in items if it["age"] == "OLD"]
    t0 = time.time()
    r1 = evaluate.run_eval(m, tok, old_items, rank_filter=None, bs=96, log=log)
    json.dump(r1, open(os.path.join(RES, f"post_p1_{name}.json"), "w"))
    log(f"post-phase1 OLD eval done ({len(r1)} items, {time.time()-t0:.0f}s)")

    # Phase 2: identical NEW documents across arms
    train.train_phase(m, tok, data.phase2(sets, a.seed), EP["2"], LR["2"], 4000 + a.seed, BS, log, "p2")

    # Primary evaluation
    persons = {age: {p["name"] for p in sets[age][:1000]} for age in ("OLD", "NEW")}
    rf = lambda it: it["tmpl"] in (0, 2) and it["name"] in persons[it["age"]]
    t0 = time.time()
    r2 = evaluate.run_eval(m, tok, items, rank_filter=rf, bs=96, log=log)
    json.dump(r2, open(os.path.join(RES, f"final_{name}.json"), "w"))
    log(f"final eval done ({len(r2)} items, {time.time()-t0:.0f}s)")
    log(f"=== ARM {name} COMPLETE {time.ctime()}")


if __name__ == "__main__":
    main()
