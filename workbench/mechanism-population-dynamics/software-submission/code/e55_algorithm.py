"""E55: is the prev-token -> induction K-composition algorithm present in every model?

K-composition (Elhage et al. 2021) of an earlier head P into the keys of a later head I, with each layer's pre-norm gain
folded in (RoPE ignored, as is standard for composition scores):
    K(P, I) = || W_QK^I W_OV^P ||_F / ( ||W_QK^I||_F ||W_OV^P||_F ),  W_QK = Wq'^T Wk',  W_OV = Wo Wv'
computed with dh x dh Gram matrices only. Null: max over 3x3 random head sets drawn from the same layers as the real
top-3 prev-token (P) and top-3 induction (I) heads (1000 draws).
  e55_algorithm.py --family dd --name dolma1_7-1B__default     (DataDecide 1B, E35 maps)
  e55_algorithm.py --family pythia --name pythia-70m-seed1     (positive control, E44 maps)
  e55_algorithm.py --analyze
"""
import argparse
import json

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / "e55"


def head_mats_dd(name):
    import dd_common as dd
    rec, seed = name.split("__")
    model, _ = dd.load(f"allenai/DataDecide-{rec}", dd.rev(dd.FINAL_1B, seed), dtype=torch.float32, device="cpu")
    c = model.config
    L, H, d = c.num_hidden_layers, c.num_attention_heads, c.hidden_size
    dh = d // H
    out = []
    for l, layer in enumerate(model.model.layers):
        g = layer.input_layernorm.weight.detach()
        a = layer.self_attn
        q, k, v = (w.weight.detach().view(H, dh, d) * g for w in (a.q_proj, a.k_proj, a.v_proj))
        o = a.o_proj.weight.detach().view(d, H, dh).permute(1, 0, 2)  # [H, d, dh]
        out.append((q, k, v, o))
    return out, L, H


def head_mats_pythia(name):
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(f"EleutherAI/{name.replace('-std', '')}", revision="step143000",
                                                 cache_dir=str(mc.HF_CACHE), dtype=torch.float32)
    c = model.config
    L, H, d = c.num_hidden_layers, c.num_attention_heads, c.hidden_size
    dh = d // H
    out = []
    for layer in model.gpt_neox.layers:
        g = layer.input_layernorm.weight.detach()
        qkv = layer.attention.query_key_value.weight.detach().view(H, 3, dh, d) * g
        o = layer.attention.dense.weight.detach().view(d, H, dh).permute(1, 0, 2)
        out.append((qkv[:, 0], qkv[:, 1], qkv[:, 2], o))
    return out, L, H


@torch.no_grad()
def kcomp_table(mats, L, H):
    """K[lp, hp, li, hi] for lp < li (NaN otherwise)."""
    K = np.full((L, H, L, H), np.nan)
    Gq = [torch.einsum("hid,hjd->hij", q, q) for q, k, v, o in mats]   # Wq' Wq'^T   [H, dh, dh]
    Gk = [torch.einsum("hid,hjd->hij", k, k) for q, k, v, o in mats]
    Gv = [torch.einsum("hid,hjd->hij", v, v) for q, k, v, o in mats]
    Go = [torch.einsum("hdi,hdj->hij", o, o) for q, k, v, o in mats]    # Wo^T Wo
    nqk = [torch.einsum("hij,hji->h", Gq[l], Gk[l]).clamp_min(1e-12).sqrt() for l in range(L)]   # ||Wq'^T Wk'||_F
    nov = [torch.einsum("hij,hji->h", Go[l], Gv[l]).clamp_min(1e-12).sqrt() for l in range(L)]   # ||Wo Wv'||_F
    for li in range(1, L):
        k_i = mats[li][1]                                                 # [H, dh, d]
        for lp in range(li):
            o_p = mats[lp][3]                                             # [H, d, dh]
            C = torch.einsum("aid,bdj->abij", k_i, o_p)                   # Wk'^I Wo^P  [Hi, Hp, dh, dh]
            # ||Wq'^T C Wv'||_F^2 = tr(C^T Gq C Gv)
            num = torch.einsum("abji,ajk,abkl,bli->ab", C, Gq[li], C, Gv[lp]).clamp_min(0).sqrt()
            K[lp, :, li, :] = (num / (nqk[li][:, None] * nov[lp][None, :])).T.numpy()
    return K


def compute(family, name, maps):
    f = OUT / f"{name}.json"
    if f.exists():
        return
    mats, L, H = (head_mats_dd if family == "dd" else head_mats_pythia)(name)
    K = kcomp_table(mats, L, H)
    M1, M2 = np.array(maps["M1"]), np.array(maps["M2"])
    I = [divmod(int(i), H) for i in np.argsort(-M1.ravel())[:3]]
    P = [divmod(int(i), H) for i in np.argsort(-M2.ravel())[:3]]
    pairs = [(p, i) for p in P for i in I if p[0] < i[0]]
    real = max((K[p[0], p[1], i[0], i[1]] for p, i in pairs), default=np.nan)
    rng = np.random.default_rng(0)
    null = []
    for _ in range(1000):
        Pr = [(l, int(rng.integers(H))) for l, _ in P]
        Ir = [(l, int(rng.integers(H))) for l, _ in I]
        vals = [K[p[0], p[1], i[0], i[1]] for p in Pr for i in Ir if p[0] < i[0]]
        if vals:
            null.append(max(vals))
    res = {"name": name, "family": family, "induction_heads": I, "prevtoken_heads": P, "n_valid_pairs": len(pairs),
           "kcomp_max": float(real), "null_mean": float(np.mean(null)) if null else None,
           "percentile": float((np.array(null) < real).mean() * 100) if null and np.isfinite(real) else None}
    OUT.mkdir(exist_ok=True)
    f.write_text(json.dumps(res))
    print(name, {k: res[k] for k in ("n_valid_pairs", "kcomp_max", "null_mean", "percentile")}, flush=True)


def analyze():
    rows = [json.loads(f.read_text()) for f in OUT.glob("*.json") if f.name != "analysis.json"]
    out = {}
    for fam in ("dd", "pythia"):
        R = [r for r in rows if r["family"] == fam]
        if not R:
            continue
        valid = [r for r in R if r["percentile"] is not None]
        out[fam] = {"n": len(R), "n_with_valid_pair": len(valid),
                    "frac_ge95": float(np.mean([r["percentile"] >= 95 for r in valid])) if valid else None,
                    "median_percentile": float(np.median([r["percentile"] for r in valid])) if valid else None}
        if fam == "dd":
            by = {}
            for r in valid:
                rec, seed = r["name"].split("__")
                by.setdefault(seed, []).append(r["percentile"] >= 95)
            out[fam]["frac_ge95_by_init"] = {s: float(np.mean(v)) for s, v in by.items()}
    # (b) causal: top prev-token head's single-head ablation effect on induction loss (E42 maps), percentile among heads
    caus = []
    for f in (mc.RESULTS / "e42" / "maps").glob("*.json"):
        d = json.loads(f.read_text())
        rec, seed = f.stem.split("__")
        M2 = np.array(json.loads((mc.RESULTS / "e35" / f"{rec}-1B__{seed}.json").read_text())["maps"]["M2"]).ravel()
        C1 = np.array(d["maps"]["C1_ind"]).ravel()
        top = int(np.argmax(M2))
        caus.append({"model": f.stem, "pct": float((C1 < C1[top]).mean() * 100), "effect": float(C1[top])})
    if caus:
        out["causal_prevtoken"] = {"n": len(caus), "frac_ge90": float(np.mean([c["pct"] >= 90 for c in caus])),
                                   "median_pct": float(np.median([c["pct"] for c in caus])), "rows": caus}
    OUT.mkdir(exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v if k != "causal_prevtoken" else {a: b for a, b in v.items() if a != "rows"}) for k, v in out.items()}, indent=1))


def check():
    """Implementation check on a toy: plant composition (I's keys read P's output space) and verify K rises."""
    torch.manual_seed(0)
    L, H, d, dh = 2, 4, 64, 16
    mats = [tuple(torch.randn(H, dh, d) for _ in range(3)) + (torch.randn(H, d, dh),) for _ in range(L)]
    base = kcomp_table(mats, L, H)[0, 1, 1, 2]
    q, k, v, o = mats[1]
    k = k.clone()
    k[2] = (mats[0][3][1] @ torch.randn(dh, dh)).T    # keys of head (1,2) read the output subspace of head (0,1)
    mats[1] = (q, k, v, o)
    planted = kcomp_table(mats, L, H)
    print("random K", round(float(base), 4), "planted K", round(float(planted[0, 1, 1, 2]), 4),
          "other heads", round(float(np.nanmean(planted[0, :, 1, :])), 4))
    assert planted[0, 1, 1, 2] > 2 * base


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=["dd", "pythia"])
    ap.add_argument("--name")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.analyze:
        analyze()
    elif a.all:
        for f in sorted((mc.RESULTS / "e44").glob("pythia-70m-*.json")):
            compute("pythia", f.stem, json.loads(f.read_text())["maps"])
        for f in sorted((mc.RESULTS / "e35").glob("*-1B__*.json")):
            if "__step" not in f.stem:
                compute("dd", f.stem, json.loads(f.read_text())["maps"])
    else:
        src = mc.RESULTS / ("e35" if a.family == "dd" else "e44") / f"{a.name}.json"
        compute(a.family, a.name, json.loads(src.read_text())["maps"])
