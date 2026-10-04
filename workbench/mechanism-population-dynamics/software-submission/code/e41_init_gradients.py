"""E41: step-0 per-head gradient magnitudes as predictors of the init-set role layout.

Usage: e41_init_gradients.py --seed default   (GPU; writes results/e41/<seed>.json) ; e41_init_gradients.py --analyze
"""
import argparse
import itertools
import json

import numpy as np

import dd_common as dd
import mp_common as mc

OUT = mc.RESULTS / "e41"
ROLES = ("M1", "M2", "M4")


def compute(seed):
    import torch
    from e35_census import natural_texts
    model, tok = dd.load("allenai/DataDecide-c4-1B", dd.rev(0, seed), dtype=torch.float32)
    cfg = model.config
    L, H = cfg.num_hidden_layers, cfg.num_attention_heads
    dh = cfg.hidden_size // H
    T = natural_texts(tok)
    feats = {}
    for name, docs in (("a", T[:25]), ("b", T[25:])):
        model.zero_grad()
        tot = 0.0
        for i in range(0, len(docs), 5):  # micro-batches, gradients accumulate
            x = torch.tensor(docs[i:i + 5], device=model.device)
            loss = model(x, labels=x).loss * len(docs[i:i + 5]) / len(docs)
            loss.backward()
            tot += float(loss)
        g = {k: np.zeros((L, H)) for k in ("gQ", "gK", "gV", "gO")}
        for l in range(L):
            att = model.model.layers[l].self_attn
            for h in range(H):
                sl = slice(h * dh, (h + 1) * dh)
                g["gQ"][l, h] = att.q_proj.weight.grad[sl].norm().item()
                g["gK"][l, h] = att.k_proj.weight.grad[sl].norm().item()
                g["gV"][l, h] = att.v_proj.weight.grad[sl].norm().item()
                g["gO"][l, h] = att.o_proj.weight.grad[:, sl].norm().item()
        g["gQK"] = g["gQ"] * g["gK"]
        feats[name] = {k: v.tolist() for k, v in g.items()}
        feats[name]["loss"] = tot
    OUT.mkdir(exist_ok=True)
    (OUT / f"{seed}.json").write_text(json.dumps(feats))
    rel = {k: float(np.corrcoef(np.ravel(feats["a"][k]), np.ravel(feats["b"][k]))[0, 1]) for k in ("gQ", "gK", "gV", "gO", "gQK")}
    print(seed, "loss", round(feats["a"]["loss"], 3), "reliability", {k: round(v, 3) for k, v in rel.items()}, flush=True)


def analyze():
    from scipy.stats import spearmanr
    D = {}
    for f in (mc.RESULTS / "e35").glob("*__*.json"):
        if "__step" not in f.stem:
            r, s = f.stem.split("__")
            D[(r, s)] = json.loads(f.read_text())["maps"]
    recs = sorted({r for r, _ in D})
    target = {(s, m): np.mean([D[(r, s)][m] for r in recs], 0).ravel() for s in dd.SEEDS for m in ROLES}
    G = {s: json.loads((OUT / f"{s}.json").read_text()) for s in dd.SEEDS}
    feats = ("gQ", "gK", "gV", "gO", "gQK")
    F = {s: {k: (np.ravel(G[s]["a"][k]) + np.ravel(G[s]["b"][k])) / 2 for k in feats} for s in dd.SEEDS}
    from scipy.stats import spearmanr as sp
    rel = {f"{s}|{k}": float(sp(np.ravel(G[s]["a"][k]), np.ravel(G[s]["b"][k]))[0]) for s in dd.SEEDS for k in feats}
    out = {"gradient_reliability": rel, "positive_control": bool(all(v >= 0.8 for v in rel.values())), "tests": {}}
    for m in ROLES:
        for k in feats:
            match = [spearmanr(F[s][k], target[(s, m)])[0] for s in dd.SEEDS]
            mism = [spearmanr(F[s][k], target[(t, m)])[0] for s, t in itertools.permutations(dd.SEEDS, 2)]
            rm, rmm = float(np.mean(match)), float(np.mean(mism))
            out["tests"][f"{m}|{k}"] = {"rho_match_each": [float(x) for x in match], "rho_match": rm, "rho_mismatch": rmm,
                                        "candidate": bool(rm >= 0.3 and rm - rmm >= 0.2 and len({np.sign(x) for x in match}) == 1)}
    T = out["tests"]
    out["decision"] = ("initial gradients predict roles: " + ",".join(k for k, v in T.items() if v["candidate"])
                       if any(v["candidate"] for v in T.values()) else
                       "not predictable" if all(abs(v["rho_match"] - v["rho_mismatch"]) < 0.1 for v in T.values()) else "other (report)")
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "tests"}, indent=1))
    for k, v in T.items():
        print(f"{k:9s} match {v['rho_match']:+.3f} {[round(x, 2) for x in v['rho_match_each']]} mismatch {v['rho_mismatch']:+.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.seed)
