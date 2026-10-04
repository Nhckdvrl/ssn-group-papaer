"""ablation_transfer: causal (ablation-defined) head-role maps and cross-model transfer of head-level interventions.
  pass 1  ablation_transfer.py --maps --recipe c4 --seed default      -> results/ablation/maps/<recipe>__<seed>.json
  pass 2  ablation_transfer.py --transfer --recipe c4 --seed default  -> results/ablation/transfer/<recipe>__<seed>.json (needs all pass-1 maps)
  check   ablation_transfer.py --check                                -> hook sanity on one model
  analyze ablation_transfer.py --analyze
Ablation = mean-ablation of one head's input slice to o_proj (head output before the output projection), replaced by
that head's mean over 25 natural texts (T[:25]); all metrics use disjoint data (seed-1 random blocks, T[25:], the retrieval probe items).
"""
import argparse
import itertools
import json
import zlib

import numpy as np
import torch

import common as mc
OUT = mc.RESULTS / "ablation"
RECIPES = ("c4", "falcon", "dclm-baseline", "fineweb-edu", "fineweb-pro", "dolma1_7")
KS = (5, 10)
N_RAND = 20


class Ablator:
    """Pre-hooks on every o_proj; `self.heads` = {layer: [head, ...]} is replaced by the head's mean input."""

    def __init__(self, model):
        self.L, self.H = model.config.num_hidden_layers, model.config.num_attention_heads
        self.dh = model.config.hidden_size // self.H
        self.heads, self.mean, self.record = {}, None, None
        for l, layer in enumerate(model.model.layers):
            layer.self_attn.o_proj.register_forward_pre_hook(self._hook(l))

    def _hook(self, l):
        def f(mod, args):
            x = args[0]
            if self.record is not None:
                self.record[l].append(x[:, 1:].float().mean((0, 1)).cpu())
            hs = self.heads.get(l)
            if hs:
                x = x.clone()
                for h in hs:
                    x[..., h * self.dh:(h + 1) * self.dh] = self.mean[l, h * self.dh:(h + 1) * self.dh].to(x.dtype)
                return (x,)
        return f

    def set(self, flat):
        self.heads = {}
        for i in flat:
            self.heads.setdefault(int(i) // self.H, []).append(int(i) % self.H)


def setup(recipe, seed):
    import datadecide as dd
    from prompts import natural_texts
    import prompts
    torch.set_grad_enabled(False)
    model, tok = dd.load(f"allenai/DataDecide-{recipe}-1B", dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    ab = Ablator(model)
    dev = model.device
    T = natural_texts(tok)
    ab.record = {l: [] for l in range(ab.L)}
    model(torch.tensor(T[:25], device=dev))
    ab.mean = torch.stack([torch.stack(ab.record[l]).mean(0) for l in range(ab.L)]).to(dev)
    ab.record = None
    g = torch.Generator().manual_seed(1)
    first = torch.randint(1000, 40000, (40, 128), generator=g)
    ind = torch.cat([torch.full((40, 1), tok.eos_token_id), first, first], 1).to(dev)
    nat = torch.tensor(T[25:], device=dev)
    R, ix = prompts.items()
    rng = np.random.default_rng(0)
    sub = []
    for c in sorted({R[i]["cat"] for i in ix}):
        cix = [i for i in ix if R[i]["cat"] == c]
        sub += sorted(rng.choice(cix, min(20, len(cix)), replace=False).tolist())
    cells = [prompts.build(R[i])[0] for i in sub]
    ret = {c: ([x[c] for x in cells], [R[i]["dist"] for i in sub], [R[i]["ans"] for i in sub]) for c in ("c1_decl", "c1_qa")}

    def f_ind():
        lp = model(ind).logits.float().log_softmax(-1)
        return float(-lp[:, 129:-1].gather(-1, ind[:, 130:, None])[..., 0].mean())

    def f_nat():
        lp = model(nat).logits.float().log_softmax(-1)
        return float(-lp[:, :-1].gather(-1, nat[:, 1:, None])[..., 0].mean())

    def f_ret():
        from prompts import cand_logprob
        out = {}
        for c, (P, D, A) in ret.items():
            out[c] = float(np.mean(cand_logprob(model, tok, P, D, bs=60) - cand_logprob(model, tok, P, A, bs=60)))
        return out
    return model, tok, ab, f_ind, f_nat, f_ret


def maps(recipe, seed):
    f = OUT / "maps" / f"{recipe}__{seed}.json"
    if f.exists():
        return
    model, tok, ab, f_ind, f_nat, f_ret = setup(recipe, seed)
    ab.set([])
    base = {"ind": f_ind(), "nat": f_nat(), **f_ret()}
    C = {k: np.zeros((ab.L, ab.H)) for k in ("C1_ind", "C2_nat", "C4_decl", "C4_qa")}
    for l, h in itertools.product(range(ab.L), range(ab.H)):
        ab.set([l * ab.H + h])
        C["C1_ind"][l, h] = f_ind() - base["ind"]
        C["C2_nat"][l, h] = f_nat() - base["nat"]
        r = f_ret()
        C["C4_decl"][l, h] = r["c1_decl"] - base["c1_decl"]
        C["C4_qa"][l, h] = r["c1_qa"] - base["c1_qa"]
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"recipe": recipe, "seed": seed, "base": base,
                             "maps": {k: v.round(6).tolist() for k, v in C.items()}}))
    print(recipe, seed, base, {k: float(v.max()) for k, v in C.items()}, flush=True)


def transfer(recipe, seed):
    import datadecide as dd
    f = OUT / "transfer" / f"{recipe}__{seed}.json"
    if f.exists():
        return
    keys = [(r, s) for r in RECIPES for s in dd.SEEDS]
    cmap = {k: np.array(json.loads((OUT / "maps" / f"{k[0]}__{k[1]}.json").read_text())["maps"]["C1_ind"]).ravel()
            for k in keys}
    amap = {k: np.array(json.loads((mc.RESULTS / "crossing_1b" / f"{k[0]}-1B__{k[1]}.json").read_text())["maps"]["M1"]).ravel()
            for k in keys}
    model, tok, ab, f_ind, f_nat, f_ret = setup(recipe, seed)
    ab.set([])
    base = f_ind()
    me = (recipe, seed)
    res = {"recipe": recipe, "seed": seed, "base": base, "own": {}, "from": {}, "random": {}, "layer_matched": {}}
    rng = np.random.default_rng(zlib.crc32(f"{recipe}__{seed}".encode()))
    for k in KS:
        own = np.argsort(-cmap[me])[:k]
        ab.set(own)
        res["own"][k] = f_ind() - base
        rr = []
        for _ in range(N_RAND):
            ab.set(rng.choice(ab.L * ab.H, k, replace=False))
            rr.append(f_ind() - base)
        res["random"][k] = rr
        lm = []  # layer-matched random: same layers as own top-k, random head within the layer
        for _ in range(N_RAND):
            ab.set([(i // ab.H) * ab.H + rng.integers(ab.H) for i in own])
            lm.append(f_ind() - base)
        res["layer_matched"][k] = lm
        for src in keys:
            for kind, M in (("causal", cmap), ("attn", amap)):
                ab.set(np.argsort(-M[src])[:k])
                res["from"].setdefault(f"{src[0]}__{src[1]}", {}).setdefault(kind, {})[k] = f_ind() - base
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res))
    print(recipe, seed, "own", res["own"], "rand", {k: float(np.mean(v)) for k, v in res["random"].items()}, flush=True)


def check():
    """Hook sanity: ablating nothing == unhooked; ablating a head changes only through that head; record shape."""
    model, tok, ab, f_ind, f_nat, f_ret = setup("c4", "default")
    ab.set([])
    a = f_ind()
    ab.heads = {}
    b = f_ind()
    assert abs(a - b) < 1e-6, (a, b)
    ab.set([0])
    c = f_ind()
    ab.set([ab.L * ab.H - 1])
    d = f_ind()
    print("base", a, "ablate L0H0", c, "ablate last head", d, "mean shape", tuple(ab.mean.shape))
    assert c != a and d != a, "ablation had no effect"
    # all heads of one layer replaced by their mean == the layer's attention output becomes input-independent
    ab.set(list(range(ab.H)))
    x = torch.tensor([[tok.eos_token_id] + [100] * 20], device=ab.mean.device)
    out1 = model.model.layers[0].self_attn.o_proj
    seen = []
    hk = out1.register_forward_hook(lambda m, i, o: seen.append(o[0, 1:].float().std(0).max().item()))
    model(x)
    hk.remove()
    print("layer-0 fully ablated: max std over positions of o_proj output", seen[0])
    assert seen[0] < 1e-2


def analyze():
    import datadecide as dd
    from scipy.stats import spearmanr
    keys = [(r, s) for r in RECIPES for s in dd.SEEDS]
    D = {k: json.loads((OUT / "maps" / f"{k[0]}__{k[1]}.json").read_text()) for k in keys}
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    out = {"maps": {}, "transfer": {}}
    rng = np.random.default_rng(0)
    for m in ("C1_ind", "C2_nat", "C4_decl", "C4_qa"):
        V = {k: np.array(D[k]["maps"][m]).ravel() for k in keys}
        sims = {(a, b): spearmanr(V[a], V[b])[0] for a, b in itertools.combinations(keys, 2)}
        g = {"SI": [], "SD": [], "DD": []}
        for (a, b), v in sims.items():
            g[cls(a, b)].append(v)
        boots = []
        for _ in range(1000):
            w = rng.choice(RECIPES, len(RECIPES))
            cnt = {r: int((w == r).sum()) for r in RECIPES}
            gg = {"SI": [], "SD": []}
            for (a, b), v in sims.items():
                c = cls(a, b)
                if c in gg and cnt[a[0]] and cnt[b[0]]:
                    gg[c] += [v] * (cnt[a[0]] * cnt[b[0]])
            boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        mean = {c: float(np.mean(v)) for c, v in g.items()}
        out["maps"][m] = {"spearman": mean, "SI_minus_SD": mean["SI"] - mean["SD"],
                          "ci95": np.percentile(boots, [2.5, 97.5]).tolist()}
        # agreement with the attention-defined crossing_1b map of the same model (validity of the attention census)
        role_map = {"C1_ind": "M1", "C4_decl": "M4", "C4_qa": "M4"}.get(m)
        if role_map:
            out["maps"][m]["rho_with_attention_map"] = float(np.mean([
                spearmanr(V[k], np.array(json.loads((mc.RESULTS / "crossing_1b" / f"{k[0]}-1B__{k[1]}.json").read_text())
                                         ["maps"][role_map]).ravel())[0] for k in keys]))
    T = {k: json.loads((OUT / "transfer" / f"{k[0]}__{k[1]}.json").read_text()) for k in keys}
    for kind in ("causal", "attn"):
        for k in map(str, KS):
            g = {"SI": [], "SD": [], "DD": []}
            for b in keys:
                own = T[b]["own"][k]
                for a in keys:
                    if a != b:
                        g[cls(a, b)].append(T[b]["from"][f"{a[0]}__{a[1]}"][kind][k] / own)
            rnd = float(np.mean([np.mean(T[b]["random"][k]) / T[b]["own"][k] for b in keys]))
            lm = float(np.mean([np.mean(T[b]["layer_matched"][k]) / T[b]["own"][k] for b in keys]))
            out["transfer"][f"{kind}_k{k}"] = {**{c: float(np.mean(v)) for c, v in g.items()},
                                               "random": rnd, "layer_matched": lm,
                                               "own_damage_mean": float(np.mean([T[b]["own"][k] for b in keys]))}
    pc = {k: float(np.mean([T[b]["own"][k] / max(np.mean(T[b]["random"][k]), 1e-6) for b in keys])) for k in map(str, KS)}
    out["positive_control_own_vs_random_ratio"] = pc
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", action="store_true")
    ap.add_argument("--transfer", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--recipe")
    ap.add_argument("--seed")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.analyze:
        analyze()
    elif a.maps:
        maps(a.recipe, a.seed)
    elif a.transfer:
        transfer(a.recipe, a.seed)
