"""E02: induction circuit on one (seed, checkpoint) of the Pythia-70M population. Protocol: experiments/E02-*.md.

Writes results/e02/<model>__step<N>.json.
"""
import argparse
import json
import random
import sys
import time

import torch

import mp_common as mc
import e01_induction as e

sys.path.insert(0, str(mc.PARENT_CODE / "src"))
from find_induction_heads import find_induction_heads  # noqa: E402
from transformer_lens.head_detector import get_induction_head_detection_pattern  # noqa: E402

OUT = mc.RESULTS / "e02"
COUNTS = mc.CACHE / "pile10k_token_counts.pt"
R2_STEPS = {1000, 8000, 64000, 143000}
PREV_T, IND_T = 0.5, 0.2
N_RAND = 20


def token_pool():
    c = torch.load(COUNTS)
    top = set(c.argsort(descending=True)[:500].tolist())
    return torch.tensor([i for i in range(len(c)) if c[i] >= 50 and i not in top])


def repeated(pool, bos, n=500, half=50, seed=12345):
    g = torch.Generator().manual_seed(seed)
    r = pool[torch.randint(0, len(pool), (n, half), generator=g)]
    return torch.cat([torch.full((n, 1), bos), r, r], dim=1)


def behaviour(model, toks, hooks=(), bs=250):
    """Per-sequence median first/second-half loss and second-half top-1 accuracy."""
    pos = torch.tensor(e.R3_POS)
    fm, sm, acc = [], [], []
    store = {}

    def grab(x, hook):
        store["x"] = x[:, pos.to(x.device)]
        return x

    for i in range(0, len(toks), bs):
        tb = toks[i:i + bs].to(model.cfg.device)
        model.run_with_hooks(tb, return_type=None, fwd_hooks=list(hooks) + [("ln_final.hook_normalized", grab)])
        logp = model.unembed(store["x"]).log_softmax(-1)
        tgt = tb[:, pos.to(tb.device) + 1]
        lv = -logp.gather(-1, tgt[..., None])[..., 0]
        fm.append(lv[:, :49].median(1).values.cpu())
        sm.append(lv[:, 49:].median(1).values.cpu())
        acc.append((logp[:, 49:].argmax(-1) == tgt[:, 49:]).float().mean(1).cpu())
    fm, sm, acc = torch.cat(fm), torch.cat(sm), torch.cat(acc)
    return {"FL": float(fm.mean()), "CL": float(sm.mean()), "ACC": float(acc.mean()),
            "_CL_seq": sm, "_ACC_seq": acc}


def prev_token_score(model, pile):
    _, cache = model.run_with_cache(pile[:64, :256].to(model.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_pattern"))
    return {f"{l}.{h}": float(cache["pattern", l].diagonal(offset=-1, dim1=-2, dim2=-1)[:, h].mean())
            for l in range(model.cfg.n_layers) for h in range(model.cfg.n_heads)}


def induction_attention(model, toks, heads, hooks=()):
    """Mean attention mass on induction targets (parent 'mul' definition) for `heads`, on token tensors."""
    det = torch.stack([get_induction_head_detection_pattern(t[None]) for t in toks[:100]]).to(model.cfg.device)
    store = {}
    names = {f"blocks.{l}.attn.hook_pattern" for l, _ in heads}

    def grab(x, hook):
        store[hook.name] = x
        return x

    model.run_with_hooks(toks[:100].to(model.cfg.device), return_type=None,
                         fwd_hooks=list(hooks) + [(n, grab) for n in names])
    out = {}
    for l, h in heads:
        pat = store[f"blocks.{l}.attn.hook_pattern"][:, h]
        out[f"{l}.{h}"] = float(((pat * det).sum((-1, -2)) / pat.sum((-1, -2))).mean())
    return out


def parse(hs):
    return [tuple(map(int, x.split("."))) for x in hs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    model = mc.load_tl_model(args.repo, args.step)
    L, H = model.cfg.n_layers, model.cfg.n_heads
    allh = [f"{l}.{h}" for l in range(L) for h in range(H)]
    pile, _ = e.pile_eval_set(model)
    rep = repeated(token_pool(), model.tokenizer.bos_token_id)
    mz = e.mean_z(model, pile)

    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E02-induction-circuit-population.md"}
    res["S_ind"] = find_induction_heads(model, seed=42)
    res["S_prev"] = prev_token_score(model, pile)
    clean = behaviour(model, rep)
    res["clean"] = {k: v for k, v in clean.items() if not k.startswith("_")}

    single = {}
    for hname in allh:
        for m in ("mean", "zero"):
            b = behaviour(model, rep, e.z_hooks(parse([hname]), m, mz))
            single[f"{hname}|{m}"] = {"dCL": b["CL"] - clean["CL"], "dACC": b["ACC"] - clean["ACC"], "dFL": b["FL"] - clean["FL"]}
    res["single"] = single

    prev_role = [h for h in allh if res["S_prev"][h] >= PREV_T]
    ind_role = [h for h in allh if res["S_ind"][h] >= IND_T]
    res["roles"] = {"prev": prev_role, "induction": ind_role}
    groups = {"prev": prev_role, "induction": ind_role, "union": sorted(set(prev_role) | set(ind_role))}
    rng = random.Random(0)
    others = [h for h in allh if h not in groups["union"]]
    gres = {}
    for g, hs in groups.items():
        if not hs:
            continue
        b = behaviour(model, rep, e.z_hooks(parse(hs), "mean", mz))
        d = (b["_CL_seq"] - clean["_CL_seq"]).numpy()
        boots = [d[rng.choices(range(len(d)), k=len(d))].mean() for _ in range(500)]
        rnd = []
        for _ in range(N_RAND):
            rs = rng.sample(others, min(len(hs), len(others)))
            rnd.append(behaviour(model, rep, e.z_hooks(parse(rs), "mean", mz))["CL"] - clean["CL"])
        gres[g] = {"heads": hs, "dCL": b["CL"] - clean["CL"], "dACC": b["ACC"] - clean["ACC"],
                   "dCL_ci95": [float(sorted(boots)[12]), float(sorted(boots)[487])],
                   "random_dCL": rnd}
    res["groups"] = gres

    if ind_role and prev_role:
        ih = parse(ind_role)
        a0 = induction_attention(model, rep, ih)
        a1 = induction_attention(model, rep, ih, e.z_hooks(parse(prev_role), "mean", mz))
        res["kcomp"] = {"clean": a0, "prev_ablated": a1}

    if args.step in R2_STEPS:
        ptoks = pile[:1000, :505]
        r2 = {"clean": float(e.r2_from_loss(e.loss_at(model, ptoks, e.R2_POS)).mean())}
        for g in ("prev", "induction"):
            if groups[g]:
                r2[g] = float(e.r2_from_loss(e.loss_at(model, ptoks, e.R2_POS, e.z_hooks(parse(groups[g]), "mean", mz))).mean())
        res["R2"] = r2

    res["seconds"] = round(time.time() - t0, 1)
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    top = sorted(single, key=lambda k: -single[k]["dCL"])[:3]
    print(f"{tag}: CL={clean['CL']:.2f} ACC={clean['ACC']:.2f} prev={prev_role} ind={ind_role} "
          f"top={[(k, round(single[k]['dCL'], 2)) for k in top]} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
