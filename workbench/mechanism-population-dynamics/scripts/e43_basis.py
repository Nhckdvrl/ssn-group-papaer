"""E43: does the initialization fix the network's coordinate system (where), while data fixes the content (what)?

Protocol: experiments/E43-*.md.  Same 18 models as E42 (6 recipes x 3 inits, DataDecide 1B final).
  dump     e43_basis.py --dump --recipe c4 --seed default   -> /home/xiang/mechpop_cache/e43/<recipe>__<seed>.pt
  pairs    e43_basis.py --pairs --part i/n                  -> results/e43/pairs/*.json (GPU; index-matched vs invariant)
  lmc      e43_basis.py --lmc --part i/n                    -> results/e43/lmc/*.json (weight interpolation)
  analyze  e43_basis.py --analyze
Tokens: 16 natural texts (E35 natural_texts T[:16]; EOS + 256 tokens each); correlations exclude position 0.
"""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / "e43"
DUMP = Path("/home/xiang/mechpop_cache/e43")
RECIPES = ("c4", "falcon", "dclm-baseline", "fineweb-edu", "fineweb-pro", "dolma1_7")
N_DOCS, N_ATT = 16, 8


def keys():
    import dd_common as dd
    return [(r, s) for r in RECIPES for s in dd.SEEDS]


@torch.no_grad()
def dump(recipe, seed):
    import dd_common as dd
    from e35_census import natural_texts
    f = DUMP / f"{recipe}__{seed}.pt"
    if f.exists():
        return
    model, tok = dd.load(f"allenai/DataDecide-{recipe}-1B", dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16, attn="eager")
    L = model.config.num_hidden_layers
    x = torch.tensor(natural_texts(tok)[:N_DOCS], device=model.device)
    rec = {"mlp": [None] * L, "head": [None] * L}
    hooks = []
    for l, layer in enumerate(model.model.layers):
        hooks.append(layer.mlp.down_proj.register_forward_pre_hook(
            lambda m, a, l=l: rec["mlp"].__setitem__(l, a[0].half().cpu())))
        hooks.append(layer.self_attn.o_proj.register_forward_pre_hook(
            lambda m, a, l=l: rec["head"].__setitem__(l, a[0].half().cpu())))
    out = model(x, output_hidden_states=True, output_attentions=True)
    for h in hooks:
        h.remove()
    att = torch.stack([a[:N_ATT].half().cpu() for a in out.attentions])  # [L, docs, H, T, T]
    DUMP.mkdir(parents=True, exist_ok=True)
    torch.save({"resid": torch.stack([h.half().cpu() for h in out.hidden_states]),  # [L+1, docs, T, d]
                "mlp": torch.stack(rec["mlp"]), "head": torch.stack(rec["head"]), "att": att,
                "tokens": x.cpu()}, f)
    print("dumped", f.name, flush=True)


def _std(z):
    z = z.float()
    z = z - z.mean(0)
    return z / (z.norm(dim=0, keepdim=True) + 1e-6)


def _cka(a, b):
    a, b = a.float() - a.float().mean(0), b.float() - b.float().mean(0)
    return float((a.T @ b).norm() ** 2 / ((a.T @ a).norm() * (b.T @ b).norm()))


@torch.no_grad()
def pair_stats(A, B, dev="cuda"):
    """Index-matched vs permutation/rotation-invariant similarity for one model pair."""
    flat = lambda t: t[:, :, 1:].reshape(t.shape[0], -1, t.shape[-1])  # drop position 0
    out = {}
    # neurons (MLP hidden units): index-matched correlation vs best-match correlation
    na, nb = flat(A["mlp"]), flat(B["mlp"])
    idx, best, mutual = [], [], []
    for l in range(na.shape[0]):
        za, zb = _std(na[l].to(dev)), _std(nb[l].to(dev))
        C = za.T @ zb
        idx.append(float(C.diagonal().mean()))
        bm = C.max(1)
        best.append(float(bm.values.mean()))
        mutual.append(float((C.argmax(0)[bm.indices] == torch.arange(C.shape[0], device=dev)).float().mean()))
    out["neuron_index_corr"], out["neuron_best_corr"], out["neuron_mutual_best"] = idx, best, mutual
    # residual stream: index-matched per-dim correlation vs linear CKA (rotation-invariant; Kornblith et al. 2019)
    ra, rb = flat(A["resid"]), flat(B["resid"])
    ri, rc = [], []
    for l in range(ra.shape[0]):
        a, b = ra[l].to(dev).float(), rb[l].to(dev).float()
        ri.append(float((_std(a) * _std(b)).sum(0).mean()))
        rc.append(_cka(a, b))
    out["resid_index_corr"], out["resid_cka"] = ri, rc
    # massive-activation dims (Sun et al. 2024): top-5 dims by max |activation| incl. position 0, middle layer
    mid = A["resid"].shape[0] // 2
    top = lambda R: set(R[mid].float().abs().amax((0, 1)).topk(5).indices.tolist())
    ta, tb = top(A["resid"]), top(B["resid"])
    out["massive_dims_jaccard"] = len(ta & tb) / len(ta | tb)
    # attention heads: per-head output CKA and attention-pattern cosine, index-matched vs within-layer best match
    ha, hb = flat(A["head"]), flat(B["head"])
    L, H = A["att"].shape[0], A["att"].shape[2]
    dh = ha.shape[-1] // H
    hi, hbm, ai, abm = [], [], [], []
    for l in range(L):
        a, b = ha[l].to(dev).float(), hb[l].to(dev).float()
        a, b = a - a.mean(0), b - b.mean(0)
        blk = lambda M: M.reshape(H, dh, H, dh).pow(2).sum((1, 3))  # squared Frobenius norm of each (head i, head j) block
        cross = blk(a.T @ b)                        # ||A_i^T B_j||_F^2
        na_, nb_ = blk(a.T @ a).diagonal().sqrt(), blk(b.T @ b).diagonal().sqrt()  # ||A_i^T A_i||_F, ||B_j^T B_j||_F
        C = (cross / (na_[:, None] * nb_[None, :])).cpu()  # linear CKA for every head pair (same as _cka)
        hi.append(float(C.diagonal().mean()))
        hbm.append(float(C.max(1).values.mean()))
        pa = A["att"][l].to(dev).float().transpose(0, 1).reshape(H, -1)
        pb = B["att"][l].to(dev).float().transpose(0, 1).reshape(H, -1)
        cs = torch.nn.functional.normalize(pa, dim=1) @ torch.nn.functional.normalize(pb, dim=1).T
        ai.append(float(cs.diagonal().mean()))
        abm.append(float(cs.max(1).values.mean()))
    out["head_out_cka_index"], out["head_out_cka_best"] = hi, hbm
    out["head_att_cos_index"], out["head_att_cos_best"] = ai, abm
    return out


def pairs(part):
    i, n = map(int, part.split("/"))
    K = keys()
    todo = [p for j, p in enumerate(itertools.combinations(K, 2)) if j % n == i]
    (OUT / "pairs").mkdir(parents=True, exist_ok=True)
    cache = {}
    for a, b in todo:
        f = OUT / "pairs" / f"{a[0]}__{a[1]}--{b[0]}__{b[1]}.json"
        if f.exists():
            continue
        for k in (a, b):
            if k not in cache:
                for old in [c for c in cache if c not in (a, b)][: max(0, len(cache) - 2)]:
                    cache.pop(old)  # keep at most 3 dumps, never evict the current pair
                cache[k] = torch.load(DUMP / f"{k[0]}__{k[1]}.pt")
        f.write_text(json.dumps(pair_stats(cache[a], cache[b])))
        print("pair", f.stem, flush=True)


@torch.no_grad()
def lmc(part):
    """Loss on 16 natural texts at alpha in {0, 0.5, 1} of linear weight interpolation (no alignment)."""
    import dd_common as dd
    from e35_census import natural_texts
    i, n = map(int, part.split("/"))
    K = keys()
    sel = [(a, b) for a, b in itertools.combinations(K, 2) if a[1] == b[1] or a[0] == b[0]]  # SI and SD pairs
    sel += [(a, b) for a, b in itertools.combinations(K, 2) if a[1] != b[1] and a[0] != b[0]][::8]  # some DD pairs
    todo = [p for j, p in enumerate(sel) if j % n == i]
    (OUT / "lmc").mkdir(parents=True, exist_ok=True)
    for a, b in todo:
        f = OUT / "lmc" / f"{a[0]}__{a[1]}--{b[0]}__{b[1]}.json"
        if f.exists():
            continue
        ma, tok = dd.load(f"allenai/DataDecide-{a[0]}-1B", dd.rev(dd.FINAL_1B, a[1]), dtype=torch.float32)
        mb, _ = dd.load(f"allenai/DataDecide-{b[0]}-1B", dd.rev(dd.FINAL_1B, b[1]), dtype=torch.float32, device="cpu")
        x = torch.tensor(natural_texts(tok)[:N_DOCS], device=ma.device)

        def loss(m):
            lp = m(x).logits.float().log_softmax(-1)
            return float(-lp[:, :-1].gather(-1, x[:, 1:, None])[..., 0].mean())
        la = loss(ma)
        sa = {k: v.clone() for k, v in ma.state_dict().items()}
        sb = mb.state_dict()
        res = {"L0": la}
        for alpha in (0.25, 0.5, 0.75, 1.0):
            ma.load_state_dict({k: (1 - alpha) * sa[k] + alpha * sb[k].to(sa[k].device) for k in sa})
            res[f"L{alpha}"] = loss(ma)
        res["barrier"] = res["L0.5"] - (res["L0"] + res["L1.0"]) / 2
        f.write_text(json.dumps(res))
        print("lmc", f.stem, {k: round(v, 3) for k, v in res.items()}, flush=True)
        del ma, mb, sa, sb
        torch.cuda.empty_cache()


def analyze():
    K = keys()
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    P = {}
    for a, b in itertools.combinations(K, 2):
        f = OUT / "pairs" / f"{a[0]}__{a[1]}--{b[0]}__{b[1]}.json"
        if f.exists():
            P[(a, b)] = json.loads(f.read_text())
    out = {"n_pairs": len(P), "metrics": {}}
    rng = np.random.default_rng(0)
    metrics = sorted(next(iter(P.values())).keys())
    for m in metrics:
        val = {p: float(np.nanmean(v[m])) for p, v in P.items()}
        g = {"SI": [], "SD": [], "DD": []}
        for p, v in val.items():
            g[cls(*p)].append(v)
        boots = []
        for _ in range(1000):
            w = rng.choice(RECIPES, len(RECIPES))
            cnt = {r: int((w == r).sum()) for r in RECIPES}
            gg = {"SI": [], "SD": []}
            for (a, b), v in val.items():
                c = cls(a, b)
                if c in gg and cnt[a[0]] and cnt[b[0]]:
                    gg[c] += [v] * (cnt[a[0]] * cnt[b[0]])
            boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        out["metrics"][m] = {**{c: float(np.mean(v)) for c, v in g.items()},
                             "SI_minus_SD": float(np.mean(g["SI"]) - np.mean(g["SD"])),
                             "ci95": np.nanpercentile(boots, [2.5, 97.5]).tolist(),
                             "per_layer": {c: np.mean([P[p][m] for p in P if cls(*p) == c], 0).tolist()
                                           for c in ("SI", "SD", "DD")} if isinstance(next(iter(P.values()))[m], list) else None}
    lm = {}
    for f in (OUT / "lmc").glob("*.json"):
        a, b = f.stem.split("--")
        a, b = tuple(a.split("__")), tuple(b.split("__"))
        lm.setdefault(cls(a, b), []).append(json.loads(f.read_text())["barrier"])
    out["lmc_barrier"] = {c: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v)), "n": len(v)}
                          for c, v in lm.items()}
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    for m, v in out["metrics"].items():
        print(f"{m:24s} SI {v['SI']:.3f} SD {v['SD']:.3f} DD {v['DD']:.3f}  SI-SD {v['SI_minus_SD']:+.3f} {np.round(v['ci95'], 3)}")
    print("LMC barrier", out["lmc_barrier"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--pairs", action="store_true")
    ap.add_argument("--lmc", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--recipe")
    ap.add_argument("--seed")
    ap.add_argument("--part", default="0/1")
    a = ap.parse_args()
    if a.dump:
        dump(a.recipe, a.seed)
    elif a.pairs:
        pairs(a.part)
    elif a.lmc:
        lmc(a.part)
    elif a.analyze:
        analyze()
