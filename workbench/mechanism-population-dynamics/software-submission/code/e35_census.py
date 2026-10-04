"""E35: crossed init x data mechanism census on DataDecide 1B.

Usage: e35_census.py --repo allenai/DataDecide-c4-1B --seed default [--step 0] ; e35_census.py --analyze
"""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import argparse
import itertools
import json

import numpy as np

import mp_common as mc

import os
OUT = mc.RESULTS / os.environ.get("E35_OUT", "e35")  # E38 reuses this script with E35_OUT=e38
THR = {"M1": 0.3, "M2": 0.5, "M3": 0.5, "M4": 0.2}


def natural_texts(tok, n=50, length=256):
    import torch
    from transformers import AutoTokenizer
    src = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", cache_dir=str(mc.HF_CACHE))
    toks = torch.load(_CACHE + "/pile_eval_2000_seed42.pt")["tokens"]
    out = []
    for row in toks:
        ids = tok(src.decode(row[:400]), add_special_tokens=False)["input_ids"]
        if len(ids) >= length:
            out.append([tok.eos_token_id] + ids[:length])
        if len(out) == n:
            break
    return out


def compute(repo, seed, step):
    import torch
    import dd_common as dd
    import e26_factorial as e26
    import e28_gating as e28
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(step, seed), dtype=torch.bfloat16, attn="eager")
    L, H = model.config.num_hidden_layers, model.config.num_attention_heads
    dev = model.device
    # M1 induction map + copy fidelity
    g = torch.Generator().manual_seed(0)
    first = torch.randint(1000, 40000, (200, 128), generator=g)
    ids = torch.cat([torch.full((200, 1), tok.eos_token_id), first, first], 1)
    M1, l2 = torch.zeros(L, H), []
    q = torch.arange(129, 257)
    for i in range(0, 200, 20):
        out = model(ids[i:i + 20].to(dev), output_attentions=True)
        M1 += torch.stack([a[:, :, q, q - 127].float().mean((0, 2)).cpu() for a in out.attentions]) / 10
        lp = out.logits.float().log_softmax(-1)
        x = ids[i:i + 20].to(dev)
        l2.append((-lp[:, 129:-1].gather(-1, x[:, 130:, None])[..., 0]).mean().item())
    # M2 previous-token and M3 sink maps on natural text (two halves for reliability)
    T = natural_texts(tok)
    halves = {}
    for h, docs in (("a", T[:25]), ("b", T[25:])):
        m2, m3 = torch.zeros(L, H), torch.zeros(L, H)
        x = torch.tensor(docs, device=dev)
        out = model(x, output_attentions=True)
        t = torch.arange(2, x.shape[1])
        for li, a in enumerate(out.attentions):
            m2[li] = a[:, :, t, t - 1].float().mean((0, 2)).cpu()
            m3[li] = a[:, :, 2:, 0].float().mean((0, 2)).cpu()
        halves[h] = (m2, m3)
    M2 = (halves["a"][0] + halves["b"][0]) / 2
    M3 = (halves["a"][1] + halves["b"][1]) / 2
    # M4 context-retrieval map (E28 items / prompts)
    R, ix = e28.items()
    M4 = torch.zeros(L, H)
    for i in ix:
        cells = e26.build(R[i])[0]
        for c in ("c1_decl", "c1_qa"):
            pid, pos = e28.encode(tok, cells[c], R[i]["dist"])
            out = model(torch.tensor([pid], device=dev), output_attentions=True)
            M4 += torch.stack([a[0, :, -1, pos].float().cpu() for a in out.attentions]) / (2 * len(ix))
    rel = lambda a, b: float(np.corrcoef(a.flatten().numpy(), b.flatten().numpy())[0, 1])
    res = {"repo": repo, "seed": seed, "step": step, "copy_loss_second": float(np.mean(l2)),
           "maps": {k: v.numpy().round(5).tolist() for k, v in (("M1", M1), ("M2", M2), ("M3", M3), ("M4", M4))},
           "reliability_M2": rel(halves["a"][0], halves["b"][0]), "reliability_M3": rel(halves["a"][1], halves["b"][1])}
    for k, v in (("M1", M1), ("M2", M2), ("M3", M3), ("M4", M4)):
        res[f"{k}_max"] = float(v.max())
        res[f"{k}_n_over"] = int((v > THR[k]).sum())
    OUT.mkdir(exist_ok=True)
    final = os.environ.get("E35_OUT", "e35") != "e35"  # E38: the given step is the final step of a smaller model
    name = f"{repo.split('DataDecide-')[1]}__{seed}" + (f"__step{step}" if step != dd.FINAL_1B and not final else "")
    (OUT / f"{name}.json").write_text(json.dumps(res))
    print(name, {k: v for k, v in res.items() if k.endswith(("_max", "_n_over")) or k.startswith(("reliab", "copy"))}, flush=True)


def analyze():
    from scipy.stats import spearmanr
    import dd_common as dd
    files = sorted(f for f in OUT.glob("*__*.json") if "__step" not in f.stem)
    D = {}
    for f in files:
        rec, seed = f.stem.split("__")
        D[(rec, seed)] = json.loads(f.read_text())
    seeds = sorted({s for _, s in D})  # E35: 3 large seeds at 1B; E38: default + small-aux-2 at 300M
    recs = sorted({r for r, _ in D})
    recs = [r for r in recs if all((r, s) in D for s in seeds)]
    keys = [(r, s) for r in recs for s in seeds]
    out = {"n_recipes": len(recs), "seeds": seeds, "maps": {}}
    rng = np.random.default_rng(0)
    for m in ("M1", "M2", "M3", "M4"):
        V = {k: np.array(D[k]["maps"][m]).flatten() for k in keys}
        top = {k: set(np.argsort(-V[k])[:5]) for k in keys}
        sims, jac = {}, {}
        for a, b in itertools.combinations(keys, 2):
            sims[(a, b)] = spearmanr(V[a], V[b])[0]
            jac[(a, b)] = len(top[a] & top[b]) / len(top[a] | top[b])

        def cls(a, b):
            return "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"

        def summary(sel_recs):
            g = {"SI": [], "SD": [], "DD": []}
            gj = {"SI": [], "SD": [], "DD": []}
            for (a, b), v in sims.items():
                if a[0] in sel_recs and b[0] in sel_recs:
                    g[cls(a, b)].append(v); gj[cls(a, b)].append(jac[(a, b)])
            return {k: float(np.mean(v)) for k, v in g.items()}, {k: float(np.mean(v)) for k, v in gj.items()}
        mean, mj = summary(set(recs))
        boots = []
        for _ in range(500):
            sel = list(rng.choice(recs, len(recs)))
            # bootstrap over recipes: recompute with multiplicity via weights
            w = {r: sel.count(r) for r in set(sel)}
            g = {"SI": [], "SD": []}
            for (a, b), v in sims.items():
                if a[0] in w and b[0] in w:
                    c = cls(a, b)
                    if c in g:
                        g[c] += [v] * (w[a[0]] * w[b[0]])
            boots.append(np.mean(g["SI"]) - np.mean(g["SD"]))
        diff = mean["SI"] - mean["SD"]
        ci = np.percentile(boots, [2.5, 97.5]).tolist()
        dec = ("init-determined" if diff > 0.1 and ci[0] > 0 and mean["SI"] > mean["DD"] + 0.1 else
               "data-determined" if -diff > 0.1 and ci[1] < 0 and mean["SD"] > mean["DD"] + 0.1 else
               "neither (incidental)" if abs(mean["SI"] - mean["DD"]) <= 0.1 and abs(mean["SD"] - mean["DD"]) <= 0.1 else "mixed")
        out["maps"][m] = {"spearman": mean, "jaccard_top5": mj, "SI_minus_SD": diff, "ci95": ci, "decision": dec}
    # scalar two-way decomposition (init x data, no replication): unbiased mean-square variance components
    # (plain SS fractions are biased by the 2 / 24 / 48 degrees of freedom)
    from scipy.stats import f as fdist
    a, b = len(recs), len(seeds)
    for s in ("M1_max", "M1_n_over", "M2_n_over", "M3_max", "M4_max", "copy_loss_second"):
        Y = np.array([[D[(r, sd)][s] for sd in seeds] for r in recs])  # [data, init]
        gm = Y.mean()
        msd = b * ((Y.mean(1) - gm) ** 2).sum() / (a - 1)
        msi = a * ((Y.mean(0) - gm) ** 2).sum() / (b - 1)
        msr = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum() / ((a - 1) * (b - 1))
        sdv, siv = max((msd - msr) / b, 0.0), max((msi - msr) / a, 0.0)
        tot = sdv + siv + msr
        out.setdefault("scalars", {})[s] = {"frac_data": float(sdv / tot), "frac_init": float(siv / tot),
                                             "frac_resid": float(msr / tot),
                                             "p_data": float(fdist.sf(msd / msr, a - 1, (a - 1) * (b - 1))),
                                             "p_init": float(fdist.sf(msi / msr, b - 1, (a - 1) * (b - 1)))}
    out["reliability"] = {k: float(np.mean([D[x][k] for x in keys])) for k in ("reliability_M2", "reliability_M3")}
    out["pc_induction_head_exists"] = bool(all(D[x]["M1_max"] > 0.5 for x in keys))
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    import dd_common as dd
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--step", type=int, default=dd.FINAL_1B)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.seed, a.step)
