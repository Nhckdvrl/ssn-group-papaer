"""E39: mean-ablate the label-reading heads selected in E36 and measure the mapping shift, the leakage and the main
effect on held-out bases of E30 (ctxeffect).

usage: mech_ablate.py --model Qwen/Qwen3-8B --tag Qwen3-8B --out results/mech/e39_Qwen3-8B.json
Head sets per task (from results/mech/<tag>_ctxeffect.npz, i.e. the first 150 bases): top-20 by Sam-shift DLA;
3 layer-matched random sets.  Ablation: o_proj input of the chosen heads at the last position := that head's mean
over 200 'same' prompts from the selection bases.  Evaluation: bases 151-300 of each task (never used by E36)."""
import argparse, json, random
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
TOP = 20


def rows_by_task():
    R = [json.loads(l) for l in open(ROOT / "data/ctxeffect/rows.jsonl")]
    bases = {}
    for r in R:
        t = r["cond"].split(":")[0]
        bases.setdefault(t, [])
        if r["base_id"] not in bases[t]:
            bases[t].append(r["base_id"])
    return R, bases


def select_heads(tag, R):
    """E36 Sam shift per head: inter - same on Sam queries, signed toward the B-mapping answer (1 - qA)."""
    z = np.load(ROOT / f"results/mech/{tag}_ctxeffect.npz")
    dla = z["dla_head"]; idx = {u: i for i, u in enumerate(z["uid"])}
    meta = {r["uid"]: r for r in R}
    out = {}
    for task in ("mag_nat", "sst"):
        acc, n = 0, 0
        for u in z["uid"]:
            r = meta[u]
            t, cond = r["cond"].split(":")
            if t != task or cond != "inter" or r["qann"] != 1:
                continue
            us = u.replace(f"{task}:inter|", f"{task}:same|")
            if us not in idx:
                continue
            sg = 1.0 if (1 - r["qA"]) == 1 else -1.0
            acc = acc + sg * (dla[idx[u]] - dla[idx[us]]); n += 1
        sam = acc / n
        L, H = sam.shape
        order = np.argsort(-sam.ravel())[:TOP]
        top = [divmod(int(k), H) for k in order]
        rng = random.Random(0)
        rand = []
        for _ in range(3):
            s = set()
            for l, h in top:
                while True:
                    c = (l, rng.randrange(H))
                    if c not in top and c not in s:
                        s.add(c); break
            rand.append(sorted(s))
        out[task] = {"top20": top, "rand": rand, "share": float(sam.ravel()[order].sum() / sam.sum())}
    return out


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--tag"); ap.add_argument("--out"); ap.add_argument("--bs", type=int, default=24)
    a = ap.parse_args()
    R, bases = rows_by_task()
    sets = select_heads(a.tag, R)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    cfg = model.config; H = cfg.num_attention_heads; dh = getattr(cfg, "head_dim", cfg.hidden_size // H)
    layers = model.model.layers
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    state = {"mode": None, "heads": {}, "means": None}
    capt = {}

    def hook(l):
        def f(mod, args):
            x = args[0]
            if state["mode"] == "capture":
                capt.setdefault(l, []).append(x[:, -1].float().view(x.shape[0], H, dh).sum(0)); capt.setdefault(("n", l), []).append(x.shape[0])
            elif state["mode"] == "ablate" and l in state["heads"]:
                x = x.clone()
                v = x[:, -1].view(x.shape[0], H, dh)
                for h in state["heads"][l]:
                    v[:, h] = state["means"][l][h].to(x.dtype)
                x[:, -1] = v.view(x.shape[0], H * dh)
                return (x,) + tuple(args[1:])
        return f
    hs = [layer.self_attn.o_proj.register_forward_pre_hook(hook(l)) for l, layer in enumerate(layers)]

    def run(rows):
        enc = [tok(r["prompt"], add_special_tokens=False)["input_ids"] for r in rows]
        c = [(tok(r["cands"][0], add_special_tokens=False)["input_ids"], tok(r["cands"][1], add_special_tokens=False)["input_ids"]) for r in rows]
        assert all(len(x) == 1 and len(y) == 1 for x, y in c)
        out = np.zeros(len(rows))
        order = sorted(range(len(rows)), key=lambda i: -len(enc[i]))
        for b in range(0, len(order), a.bs):
            ix = order[b:b + a.bs]
            Lm = max(len(enc[i]) for i in ix)
            ids = torch.full((len(ix), Lm), pad, dtype=torch.long); att = torch.zeros((len(ix), Lm), dtype=torch.long)
            for j, i in enumerate(ix):
                ids[j, Lm - len(enc[i]):] = torch.tensor(enc[i]); att[j, Lm - len(enc[i]):] = 1
            pos = (att.cumsum(1) - 1).clamp(min=0)
            lo = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=pos.cuda(), logits_to_keep=1, use_cache=False).logits[:, -1].float()
            for j, i in enumerate(ix):
                out[i] = float(lo[j, c[i][1][0]] - lo[j, c[i][0][0]])
        return out

    # means over 200 'same' prompts from the selection bases (first 150 per task)
    sel = [r for r in R if r["cond"].endswith(":same") and r["base_id"] in set(bases[r["cond"].split(":")[0]][:150])]
    random.Random(1).shuffle(sel)
    state["mode"] = "capture"; run(sel[:200])
    state["means"] = {l: (torch.stack(capt[l]).sum(0) / sum(capt[("n", l)])).cuda() for l in range(len(layers))}
    res = {"sets": {t: {"top20": [f"{l}.{h}" for l, h in s["top20"]], "rand": [[f"{l}.{h}" for l, h in r] for r in s["rand"]],
                        "e36_share": s["share"]} for t, s in sets.items()}, "ld": {}}
    for task in ("mag_nat", "sst"):
        held = set(bases[task][150:300])
        rows = [r for r in R if r["cond"].startswith(task + ":") and r["base_id"] in held]
        res.setdefault("uids", {})[task] = [r["uid"] for r in rows]
        conds = {"none": None, "top20": sets[task]["top20"]} | {f"rand{k}": s for k, s in enumerate(sets[task]["rand"])}
        for name, heads in conds.items():
            state["mode"] = "ablate" if heads else None
            state["heads"] = {}
            for l, h in heads or []:
                state["heads"].setdefault(l, []).append(h)
            res["ld"][f"{task}|{name}"] = run(rows).round(4).tolist()
            print(task, name, "done", flush=True)
    Path(a.out).write_text(json.dumps(res))


if __name__ == "__main__":
    main()
