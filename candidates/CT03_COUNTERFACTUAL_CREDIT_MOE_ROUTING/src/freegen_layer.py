"""CT03 E09 stage 3 -- free generation, base vs the L47 Exact-EPO router.

The 120 locked FG0 dev problems, identical greedy decoding for both arms. This
is the leg of the pre-registered reproduction criterion that a route-value
number cannot stand in for: a router can lower CE at the hard tokens it is
scored on and still generate worse.
"""
import argparse, json, sys, time
import numpy as np
import torch

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import load
from cpd_freegen import gen_batch
from fg0_pool import boxed, norm



def boot(pairs, B=5000, seed=0):
    rng = np.random.default_rng(seed); v = []
    a = np.array(pairs)
    for _ in range(B):
        k = rng.choice(len(a), len(a), replace=True)
        v.append(a[k, 1].mean() - a[k, 0].mean())
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def main(a):
    tok, model = load(a)
    pool = json.load(open(a.pool))["items"][:a.n_problems]
    L = a.layer
    gate = model.model.layers[L].mlp.gate
    base_w = gate.weight.detach().clone()
    trained = torch.load(a.ckpt, map_location="cpu")[str(L)].to(gate.weight.device)
    prompts = [tok.apply_chat_template([{"role": "user", "content": e["problem"]}],
                                       tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False) for e in pool]
    out = {}
    arm_t = f"epo_l{L}"
    for arm, w in (("base", base_w), (arm_t, trained)):
        gate.weight.data.copy_(w)
        comp, t0 = [], time.time()
        for i in range(0, len(pool), a.batch):
            comp += gen_batch(model, tok, prompts[i:i + a.batch], a.max_new)
            print(f"  [{arm}] {min(i+a.batch,len(pool))}/{len(pool)} "
                  f"{time.time()-t0:.0f}s", flush=True)
        out[arm] = [tok.decode(c) for c in comp]
    gate.weight.data.copy_(base_w)

    rows = []
    for i, ex in enumerate(pool):
        gold = norm(boxed(ex["solution"]) or "")
        r = dict(i=i, gold=gold)
        for arm in out:
            pred = norm(boxed(out[arm][i]) or "")
            r[arm] = dict(pred=pred, ok=int(bool(gold) and pred == gold),
                          ntok=len(out[arm][i]))
        r["same"] = int(out["base"][i] == out[arm_t][i])
        rows.append(r)
    acc = {arm: float(np.mean([r[arm]["ok"] for r in rows])) for arm in out}
    lo, hi = boot([(r["base"]["ok"], r[arm_t]["ok"]) for r in rows])
    same = float(np.mean([r["same"] for r in rows]))
    print(f"\nn={len(rows)}  base {acc['base']:.3f}  {arm_t} {acc[arm_t]:.3f}  "
          f"diff {acc[arm_t]-acc['base']:+.3f} [{lo:+.3f},{hi:+.3f}]  "
          f"identical completions {same:.3f}")
    json.dump(dict(acc=acc, ci=[lo, hi], same=same, rows=rows,
                   completions=out), open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--layer", type=int, default=47)
    ap.add_argument("--ckpt", default="results/e09_gate_l47.pt")
    ap.add_argument("--out", default="results/e09_freegen.json")
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=120)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--max-new", dest="max_new", type=int, default=512)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    main(ap.parse_args())
