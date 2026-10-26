"""E74: IOI name movers across the DataDecide 1B crossing (protocol: experiments/E74-*.md).

  e74_ioi_datadecide.py --worker TAG     # C4 models first, then every other 1B model (claims in results/e74/claims)
  e74_ioi_datadecide.py --analyze
Per model (results/e74/<recipe>__<seed>.json): per-head direct logit attribution at END (IO - S; final RMSNorm
linearized at END), END->IO attention, the logit-difference drop after mean-ablating each head alone at END
(ABC reference), and joint ablations of the model's own top-3 DLA heads, of each C4 model's top-3, of 20 random and
20 layer-matched random 3-sets."""
import argparse
import json
import os
import random
import sys

import numpy as np
import torch

import mp_common as mc

sys.path.insert(0, str(mc.CACHE / "circuits-over-time"))
from path_patching_cm.ioi_dataset import IOIDataset  # noqa: E402

OUT = mc.RESULTS / "e74"
SEEDS = ("default", "large-aux-2", "large-aux-3")
K = 3


def models():
    recs = sorted({f.stem.split("-1B__")[0] for f in (mc.RESULTS / "e35").glob("*-1B__*.json") if "step" not in f.stem})
    out = [("c4", s) for s in SEEDS]
    return out + [(r, s) for r in recs for s in SEEDS if r != "c4"]


class Probe:
    """IOI measurement on a DataDecide (HF Llama) model with o_proj pre-hooks."""

    def __init__(self, model, tok):
        self.m, self.tok = model, tok
        c = model.config
        self.L, self.H = c.num_hidden_layers, c.num_attention_heads
        self.dh = c.hidden_size // self.H
        tok.add_bos_token = False
        self.ioi = IOIDataset(prompt_type="mixed", N=200, tokenizer=tok, prepend_bos=False, seed=42, device="cpu")
        self.abc = self.ioi.gen_flipped_prompts("ABB->ABA, BAB->BAA")
        self.end = torch.as_tensor(self.ioi.word_idx["end"])
        self.b = torch.arange(len(self.end))
        self.io = torch.as_tensor(self.ioi.io_tokenIDs)
        self.s = torch.as_tensor(self.ioi.s_tokenIDs)
        self.patch = {}  # layer -> list of heads to mean-ablate at END
        self.capture = None
        self.hooks = [l.self_attn.o_proj.register_forward_pre_hook(self._hook(i)) for i, l in enumerate(model.model.layers)]
        self.mean_z = None

    def _hook(self, layer):
        def fn(mod, args):
            x = args[0]
            if self.capture is not None:
                self.capture[layer] = x[self.cb, self.ce].detach().float()
            if layer in self.patch and self.patch[layer]:
                x = x.clone()
                for h in self.patch[layer]:
                    x[self.b.to(x.device), self.end.to(x.device), h * self.dh:(h + 1) * self.dh] = \
                        self.mean_z[layer][h * self.dh:(h + 1) * self.dh].to(x.dtype)
                return (x,)
        return fn

    @torch.no_grad()
    def forward(self, toks, ends, **kw):
        self.cb, self.ce = torch.arange(len(ends)).to(self.m.device), ends.to(self.m.device)
        return self.m(toks.long().to(self.m.device), **kw)

    @torch.no_grad()
    def logit_diff(self, heads=()):
        self.patch = {}
        for l, h in heads:
            self.patch.setdefault(l, []).append(h)
        lg = self.forward(self.ioi.toks, self.end).logits.float()[self.b, self.end.to(self.m.device)]
        self.patch = {}
        return float((lg[self.b, self.io.to(lg.device)] - lg[self.b, self.s.to(lg.device)]).mean())

    @torch.no_grad()
    def setup(self):
        # mean head inputs to o_proj at END on the ABC prompts
        self.capture = {}
        self.forward(self.abc.toks, torch.as_tensor(self.abc.word_idx["end"]))
        self.mean_z = {l: v.mean(0) for l, v in self.capture.items()}
        # clean pass: per-head outputs at END, final-norm scale, attention END->IO
        self.capture = {}
        pre = {}
        hk = self.m.model.norm.register_forward_pre_hook(lambda mod, a: pre.__setitem__("x", a[0][self.cb, self.ce].float()))
        out = self.forward(self.ioi.toks, self.end, output_attentions=True)
        hk.remove()
        zs, self.capture = self.capture, None
        x = pre["x"]
        scale = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.m.config.rms_norm_eps)  # [N, 1]
        w = self.m.model.norm.weight.float()
        WU = self.m.lm_head.weight.float()
        udir = (WU[self.io.to(WU.device)] - WU[self.s.to(WU.device)]) * w  # [N, d]
        dla = torch.zeros(self.L, self.H)
        for l in range(self.L):
            Wo = self.m.model.layers[l].self_attn.o_proj.weight.float()  # [d, H*dh]
            z = zs[l].view(len(self.end), self.H, self.dh)
            for h in range(self.H):
                contrib = z[:, h] @ Wo[:, h * self.dh:(h + 1) * self.dh].T  # [N, d]
                dla[l, h] = ((contrib * scale) * udir).sum(-1).mean().cpu()
        io_pos = torch.as_tensor(self.ioi.word_idx["IO"]).to(self.m.device)
        att = torch.stack([a[self.cb, :, self.ce, io_pos].float().mean(0).cpu() for a in out.attentions])
        return dla, att


def measure(r, s, sources):
    import dd_common as dd
    torch.set_grad_enabled(False)
    model, tok = dd.load(f"allenai/DataDecide-{r}-1B", dd.rev(dd.FINAL_1B, s), dtype=torch.float32, attn="eager")
    p = Probe(model, tok)
    dla, att = p.setup()
    clean = p.logit_diff()
    L, H = p.L, p.H
    single = torch.zeros(L, H)
    for l in range(L):
        for h in range(H):
            single[l, h] = clean - p.logit_diff([(l, h)])
    order = sorted(((l, h) for l in range(L) for h in range(H)), key=lambda x: -float(dla[x]))
    own = order[:K]
    rng = random.Random(1)
    pool = [x for x in order if x not in own]
    res = {"recipe": r, "seed": s, "logit_diff": clean, "dla": dla.numpy().round(5).tolist(),
           "att_io": att.numpy().round(5).tolist(), "single_ablation_drop": single.numpy().round(5).tolist(),
           "top": [f"{l}.{h}" for l, h in order[:10]], "drop": {"own": clean - p.logit_diff(own)},
           "random": [clean - p.logit_diff(rng.sample(pool, K)) for _ in range(20)],
           "layermatched": [clean - p.logit_diff([(l, rng.choice([h for h in range(H) if (l, h) not in own]))
                                                   for l, _ in own]) for _ in range(20)]}
    for name, heads in sources.items():
        res["drop"][name] = clean - p.logit_diff(heads)
    OUT.mkdir(exist_ok=True)
    (OUT / f"{r}__{s}.json").write_text(json.dumps(res))
    print(r, s, f"LD {clean:.2f} own {res['drop']['own']:.2f} top {res['top'][:3]}", flush=True)


def c4_sources():
    src = {}
    for s in SEEDS:
        f = OUT / f"c4__{s}.json"
        if not f.exists():
            return None
        src[f"c4_{s}"] = [tuple(map(int, x.split("."))) for x in json.loads(f.read_text())["top"][:K]]
    return src


def worker(tag):
    import time
    claims = OUT / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    for r, s in models():
        name = f"{r}__{s}"
        if (OUT / f"{name}.json").exists():
            continue
        src = c4_sources()
        if r != "c4" and src is None:  # the C4 references are not ready yet
            while (src := c4_sources()) is None:
                time.sleep(60)
        try:
            os.mkdir(claims / name)
        except FileExistsError:
            continue
        try:
            measure(r, s, src or {})
        except Exception as ex:
            print("FAILED", name, repr(ex)[:300], flush=True)
            os.rmdir(claims / name)


def analyze():
    D = {}
    for f in sorted(OUT.glob("*__*.json")):
        d = json.loads(f.read_text())
        D[(d["recipe"], d["seed"])] = d
    ver = sorted(k for k in D if k not in mc.UNVERIFIED_1B)
    from scipy.stats import rankdata

    def within(a, b):  # within-layer Spearman, averaged over layers (vectorized)
        A, B = rankdata(np.array(a), axis=1), rankdata(np.array(b), axis=1)
        A, B = A - A.mean(1, keepdims=True), B - B.mean(1, keepdims=True)
        den = np.sqrt((A ** 2).sum(1) * (B ** 2).sum(1))
        return float(np.nanmean(np.where(den > 0, (A * B).sum(1) / np.where(den > 0, den, 1), np.nan)))
    out = {"n_models": len(ver), "logit_diff": float(np.mean([D[k]["logit_diff"] for k in ver]))}
    for mapname in ("dla", "single_ablation_drop", "att_io"):
        g = {"SI": [], "SD": [], "DD": []}
        t1 = {"SI": [], "SD": [], "DD": []}
        for i, a in enumerate(ver):
            for b in ver[i + 1:]:
                c = "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
                g[c].append(within(D[a][mapname], D[b][mapname]))
                A, B = np.array(D[a][mapname]), np.array(D[b][mapname])
                t1[c].append(float(np.unravel_index(A.argmax(), A.shape) == np.unravel_index(B.argmax(), B.shape)))
        out[mapname] = {c: float(np.mean(v)) for c, v in g.items()} | {f"top1_global_{c}": float(np.mean(v)) for c, v in t1.items()}
        print(mapname, {k: round(v, 3) for k, v in out[mapname].items()}, flush=True)
    # transfer of the C4 models' top-3 heads
    tr = {"same_seed": [], "other_seed": [], "random": [], "layermatched": []}
    per = []
    for k in ver:
        if k[0] == "c4":
            continue
        d = D[k]
        own = d["drop"]["own"]
        if own <= 0:
            continue
        for s in SEEDS:
            if ("c4", s) in mc.UNVERIFIED_1B or f"c4_{s}" not in d["drop"]:
                continue
            v = d["drop"][f"c4_{s}"] / own
            (tr["same_seed"] if s == k[1] else tr["other_seed"]).append(v)
            if s == k[1]:
                per.append((k[0], k[1], v))
        tr["random"].append(float(np.mean(d["random"])) / own)
        tr["layermatched"].append(float(np.mean(d["layermatched"])) / own)
    out["transfer"] = {c: float(np.mean(v)) for c, v in tr.items()} | {f"n_{c}": len(v) for c, v in tr.items()}
    out["transfer_same_seed_by_recipe"] = per
    # set level (single-head ablation drops, additive approximation): the target's drop on the source's top-k DLA
    # heads relative to the target's own k largest drops, for every ordered pair of verified models
    import itertools
    from scipy.stats import spearmanr as sp
    dla = {k: np.array(D[k]["dla"]).ravel() for k in ver}
    drop = {k: np.array(D[k]["single_ablation_drop"]).ravel() for k in ver}
    conc = {k: float(np.sort(dla[k].clip(0))[::-1][:3].sum() / dla[k].clip(0).sum()) for k in ver}
    setlev, law = {}, []
    dist = json.loads((mc.RESULTS / "e60" / "function_words_pairs.json").read_text())
    cw = lambda r1, r2: (dist.get(f"{r1}|{r2}") or dist.get(f"{r2}|{r1}") or {}).get("cw")
    for k in (3, 5, 10, 20):
        g = {"SI": [], "SD": [], "DD": []}
        for a, b in itertools.permutations(ver, 2):
            c = "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
            v = float(drop[b][np.argsort(-dla[a])[:k]].sum() / np.sort(drop[b])[::-1][:k].sum())
            g[c].append(v)
            if k == 5 and c == "SI":
                law.append((v, conc[a], cw(a[0], b[0])))
        rnd = float(np.mean([k / drop[b].size * drop[b].sum() / np.sort(drop[b])[::-1][:k].sum() for b in ver]))
        setlev[k] = {c: float(np.mean(v)) for c, v in g.items()} | {"random": rnd, "n_SI": len(g["SI"])}
    out["set_level"] = setlev
    L_ = np.array([x for x in law if x[2] is not None], float)
    out["same_init_transfer_law_k5"] = {
        "n_pairs": int(len(L_)), "rho_concentration": float(sp(L_[:, 0], L_[:, 1])[0]),
        "rho_content_word_distance": float(sp(L_[:, 0], L_[:, 2])[0]),
        "concentration_range": [float(min(conc.values())), float(max(conc.values()))]}
    print("set level", {k: {c: round(v, 3) for c, v in r.items() if isinstance(v, float)} for k, r in setlev.items()}, flush=True)
    print("same-init law", out["same_init_transfer_law_k5"], flush=True)
    print("transfer", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out["transfer"].items()}, flush=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker")
    ap.add_argument("--one", nargs=2)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    elif a.one:
        measure(*a.one, c4_sources() or {})
    else:
        worker(a.worker)


if __name__ == "__main__":
    main()
