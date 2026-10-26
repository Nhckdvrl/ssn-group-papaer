"""E20: E18 readout on DataDecide 1B (25 recipes x 3 seeds); recipe-vs-seed decomposition. Protocol: experiments/E20-*.md.

Usage: e20_recipe.py --repo allenai/DataDecide-c4-1B --seed default ; e20_recipe.py --analyze
"""
import argparse
import itertools
import json

import numpy as np
import torch
from scipy.stats import spearmanr

import dd_common as dd
import e18_trait as e18
import mp_common as mc

OUT = mc.RESULTS / "e20"


@torch.no_grad()
def cand_logprob(model, tok, prompts, cands, bs=32):
    """Sum log-prob of ' '+cand after prompt; sequence starts with EOS (OLMo document separator)."""
    out = []
    for i in range(0, len(prompts), bs):
        P, C = prompts[i:i + bs], cands[i:i + bs]
        pi = [tok(p, add_special_tokens=False)["input_ids"] for p in P]
        ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in C]
        seqs = [[tok.eos_token_id] + a + b for a, b in zip(pi, ci)]
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), tok.pad_token_id)
        att = torch.zeros((len(seqs), L), dtype=torch.long)
        for j, s in enumerate(seqs):
            ids[j, :len(s)] = torch.tensor(s)
            att[j, :len(s)] = 1
        logp = model(ids.to(model.device), attention_mask=att.to(model.device)).logits.float().log_softmax(-1)
        for j, (a, b) in enumerate(zip(pi, ci)):
            st = 1 + len(a)
            pos = torch.arange(st - 1, st - 1 + len(b), device=logp.device)
            out.append(float(logp[j, pos, torch.tensor(b, device=logp.device)].sum()))
    return np.array(out)


def compute(repo, seed):
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R = e18.rows()
    clean_t = cand_logprob(model, tok, [r["clean"] for r in R], [r["ans"] for r in R])
    clean_d = cand_logprob(model, tok, [r["clean"] for r in R], [r["dist"] for r in R])
    known = clean_t > clean_d
    res = {"repo": repo, "seed": seed, "step": dd.FINAL_1B, "conditions": {}, "known_items": {}}
    for f in e18.FORMS:
        P = [r[f] for r in R]
        bs = 8 if f == "Coherent Conflict" else 32
        lt = cand_logprob(model, tok, P, [r["ans"] for r in R], bs=bs)
        ld = cand_logprob(model, tok, P, [r["dist"] for r in R], bs=bs)
        for cat in sorted({r["cat"] for r in R}):
            all_idx = [i for i, r in enumerate(R) if r["cat"] == cat]
            idx = np.array([i for i in all_idx if known[i]])
            res["known_items"][cat] = [int(i) for i in idx]
            res["conditions"][f"{cat}|{f}"] = {
                "n_items": len(all_idx), "n_known": int(len(idx)), "known_frac": float(len(idx) / len(all_idx)),
                "clean_margin": float((clean_t - clean_d)[all_idx].mean()),
                "adoption": float((ld[idx] > lt[idx]).mean()) if len(idx) else None,
                "margin": float((ld - lt)[idx].mean()) if len(idx) else None,
                "margin_all_items": {int(i): float(ld[i] - lt[i]) for i in all_idx}}
    OUT.mkdir(exist_ok=True)
    name = f"{repo.split('DataDecide-')[1]}__{seed}.json"
    (OUT / name).write_text(json.dumps(res))
    print(name, {k.split("|")[0][:8] + "|" + k.split("|")[1][:3]: (v["n_known"], round(v["margin"] or 0, 2))
                 for k, v in res["conditions"].items()}, flush=True)


def icc1(X):
    """X [groups, k] -> one-way random-effects ICC(1)."""
    g, k = X.shape
    msb = k * X.mean(1).var(ddof=1)
    msw = ((X - X.mean(1, keepdims=True)) ** 2).sum() / (g * (k - 1))
    return float((msb - msw) / (msb + (k - 1) * msw))


def analyze():
    files = sorted(OUT.glob("*__*.json"))
    data = {f.stem: json.loads(f.read_text()) for f in files}
    recipes = sorted({k.split("__")[0] for k in data})
    recipes = [r for r in recipes if all(f"{r}__{s}" in data for s in dd.SEEDS)]
    conds = sorted(data[f"{recipes[0]}__default"]["conditions"])

    def arr(key, c, items=None):
        def val(d):
            if items is None:
                return d["conditions"][c][key]
            m = d["conditions"][c]["margin_all_items"]
            return float(np.mean([m[str(i)] for i in items]))
        return np.array([[val(data[f"{r}__{s}"]) for s in dd.SEEDS] for r in recipes])

    out = {"n_recipes": len(recipes), "recipes": recipes, "per_condition": {}}
    D, K = {c: arr("margin", c) for c in conds}, {c: arr("clean_margin", c) for c in conds}
    rng = np.random.default_rng(0)
    for c in conds:
        boots = [icc1(D[c][rng.choice(len(recipes), len(recipes))]) for _ in range(1000)]
        cat = c.split("|")[0]
        shared = set.intersection(*[set(d["known_items"][cat]) for d in data.values()
                                    if d["repo"].split("DataDecide-")[1] in recipes])
        Ds = arr(None, c, sorted(shared)) if len(shared) >= 30 else None
        kbar = K[c].mean(1)
        beta = np.polyfit(kbar, D[c].mean(1), 1)
        Dr = D[c] - np.polyval(beta, kbar)[:, None]
        out["per_condition"][c] = {"icc_D": icc1(D[c]), "icc_D_ci95": np.percentile(boots, [2.5, 97.5]).tolist(),
                                   "icc_K": icc1(K[c]), "n_shared_known": len(shared),
                                   "icc_D_shared_items": icc1(Ds) if Ds is not None else None,
                                   "icc_D_resid_K": icc1(Dr)}
    pc = out["per_condition"]
    out["icc_D_median"] = float(np.median([v["icc_D"] for v in pc.values()]))
    out["icc_K_median"] = float(np.median([v["icc_K"] for v in pc.values()]))
    out["icc_D_shared_median"] = float(np.median([v["icc_D_shared_items"] for v in pc.values()
                                                  if v["icc_D_shared_items"] is not None] or [np.nan]))
    out["icc_D_resid_K_median"] = float(np.median([v["icc_D_resid_K"] for v in pc.values()]))
    Rm = np.array([D[c].mean(1) for c in conds])                                   # [cond, recipe]
    Sd = np.array([(D[c] - D[c].mean(1, keepdims=True)).ravel() for c in conds])   # [cond, recipe*seed]
    pairs = list(itertools.combinations(range(len(conds)), 2))
    out["coherence_recipe"] = float(np.nanmean([spearmanr(Rm[i], Rm[j])[0] for i, j in pairs]))
    out["coherence_seed"] = float(np.nanmean([spearmanr(Sd[i], Sd[j])[0] for i, j in pairs]))
    fl = {s: np.mean([data[f"dolma1_7-1B__{s}"]["conditions"][c]["margin"] - data[f"dolma1_7-no-flan-1B__{s}"]
                      ["conditions"][c]["margin"] for c in conds]) for s in dd.SEEDS} if "dolma1_7-no-flan-1B" in recipes else None
    out["explore_flan_minus_noflan_mean_margin"] = fl
    dose = [("dolma1_7-1B", 0), ("dclm-baseline-25p-dolma1.7-75p-1B", 25), ("dclm-baseline-50p-dolma1.7-50p-1B", 50),
            ("dclm-baseline-75p-dolma1.7-25p-1B", 75), ("dclm-baseline-1B", 100)]
    if all(r in recipes for r, _ in dose):
        Y = np.array([[np.mean([data[f"{r}__{s}"]["conditions"][c]["margin"] for c in conds]) for s in dd.SEEDS]
                      for r, _ in dose])  # [5 recipes, 3 seeds]
        x = np.repeat([p for _, p in dose], 3)
        rho = spearmanr(x, Y.ravel())[0]
        null = [spearmanr(x, Y[rng.permutation(5)].ravel())[0] for _ in range(10000)]
        out["dose_response"] = {"rho": float(rho), "perm_p": float(np.mean(np.abs(null) >= abs(rho) - 1e-12)),
                                "recipe_means": Y.mean(1).tolist(), "seed_values": Y.tolist()}
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_condition", "recipes")}, indent=1))
    for c, v in pc.items():
        print(f"{c:45s} D {v['icc_D']:.2f} K {v['icc_K']:.2f} shared {v['icc_D_shared_items']} residK {v['icc_D_resid_K']:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.seed)
