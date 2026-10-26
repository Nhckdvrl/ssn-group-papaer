"""E16: shared arbitration knob, different default? Protocol: experiments/E16-arbitration-default-offset.md.

Phase base : python e16_knob.py --repo EleutherAI/pythia-410m-seed3 --phase base
Phase align: python e16_knob.py --repo EleutherAI/pythia-410m-seed3 --phase align --target 0.90
Outputs results/e16/<model>__{base,align}.json (+ knob .pt).
"""
import argparse
import json
import random
import time

import numpy as np
import torch

import mp_common as mc
import e13_arbitration as e13

OUT = mc.RESULTS / "e16"
STEP = 143000
CONFLICT = "The capital of {country} is {distractor}. "
QUESTIONS = {"qa": "Q: What is the capital of {country}? A:",
             "bare": "The capital of {country} is",
             "possessive": "{country}'s capital is",
             "learned": "I learned that the capital of {country} is",
             "of_course": "The capital city of {country}, of course, is"}
ALPHAS = [-2.0, -1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0, 2.0]


def countries_split():
    known = None
    for f in sorted((mc.RESULTS / "e13").glob("*__step*.json")):
        k = set(json.loads(f.read_text())["per_country"])
        known = k if known is None else known & k
    cs = sorted(known)
    random.Random(16).shuffle(cs)
    return sorted(cs[:len(cs) // 2]), sorted(cs[len(cs) // 2:])


def distractors(caps):
    rng = random.Random(0)
    countries = sorted(caps)
    return {c: rng.sample([caps[o] for o in countries if o != c and caps[o].lower() != caps[c].lower()], e13.K_DIST)
            for c in countries}  # identical construction to E13


def items(cs, caps, dist, tmpl):
    P, T, D, C = [], [], [], []
    for c in cs:
        for d in dist[c]:
            P.append(CONFLICT.format(country=c, distractor=d) + QUESTIONS[tmpl].format(country=c))
            T.append(caps[c]), D.append(d), C.append(c)
    return P, T, D, C


@torch.no_grad()
def score(model, prompts, cands, layer=None, vec=None, head_scale=None, bs=64):
    """Sum log-prob of ' '+cand; optional steering vec added at the last prompt position of resid_post[layer];
    optional (layer, head, factor) scaling of a head's z at all positions."""
    tok = model.tokenizer
    out = []
    for i in range(0, len(prompts), bs):
        P, C = prompts[i:i + bs], cands[i:i + bs]
        pi = [tok(p, add_special_tokens=False)["input_ids"] for p in P]
        ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in C]
        seqs = [[tok.bos_token_id] + a + b for a, b in zip(pi, ci)]
        L = max(map(len, seqs))
        ids = torch.zeros((len(seqs), L), dtype=torch.long)
        for j, s in enumerate(seqs):
            ids[j, :len(s)] = torch.tensor(s)
        last = torch.tensor([len(a) for a in pi])  # index of last prompt token (BOS at 0)
        hooks = []
        if vec is not None:
            v = vec.to(model.cfg.device)

            def steer(x, hook):
                x[torch.arange(x.shape[0]), last.to(x.device)] += v
                return x
            hooks.append((f"blocks.{layer}.hook_resid_post", steer))
        if head_scale is not None:
            hl, hh, f = head_scale

            def sc(z, hook):
                z[:, :, hh] *= f
                return z
            hooks.append((f"blocks.{hl}.attn.hook_z", sc))
        logp = model.run_with_hooks(ids.to(model.cfg.device), fwd_hooks=hooks).log_softmax(-1)
        for j, (a, b) in enumerate(zip(pi, ci)):
            st = 1 + len(a)
            pos = torch.arange(st - 1, st - 1 + len(b), device=logp.device)
            out.append(float(logp[j, pos, torch.tensor(b, device=logp.device)].sum()))
    return np.array(out)


def adoption(model, P, T, D, C, **kw):
    lt, ld = score(model, P, T, **kw), score(model, P, D, **kw)
    adopt = (ld > lt).astype(float)
    per = {}
    for c, a in zip(C, adopt):
        per.setdefault(c, []).append(a)
    return float(np.mean([np.mean(v) for v in per.values()]))


@torch.no_grad()
def last_resid(model, prompts, bs=64):
    tok = model.tokenizer
    acc = []
    for i in range(0, len(prompts), bs):
        P = prompts[i:i + bs]
        pi = [[tok.bos_token_id] + tok(p, add_special_tokens=False)["input_ids"] for p in P]
        L = max(map(len, pi))
        ids = torch.zeros((len(pi), L), dtype=torch.long)
        for j, s in enumerate(pi):
            ids[j, :len(s)] = torch.tensor(s)
        _, cache = model.run_with_cache(ids.to(model.cfg.device), names_filter=lambda n: n.endswith("hook_resid_post"))
        last = torch.tensor([len(s) - 1 for s in pi], device=model.cfg.device)
        acc.append(torch.stack([cache[f"blocks.{l}.hook_resid_post"][torch.arange(len(pi)), last]
                                for l in range(model.cfg.n_layers)], 1).cpu())  # [b, L, d]
    return torch.cat(acc)


def auc(pos, neg):
    from sklearn.metrics import roc_auc_score
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    return float(roc_auc_score(y, np.r_[pos, neg]))


def bisect(fn, target, lo=-4.0, hi=4.0, it=10):
    flo, fhi = fn(lo), fn(hi)
    if not (min(flo, fhi) <= target <= max(flo, fhi)):
        return None, None
    inc = fhi > flo
    for _ in range(it):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if (fm < target) == inc:
            lo = mid
        else:
            hi = mid
    a = (lo + hi) / 2
    return a, fn(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--phase", choices=["base", "align"], required=True)
    ap.add_argument("--target", type=float, default=None)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    name = args.repo.split("/")[-1]
    model = mc.load_tl_model(args.repo, STEP)
    caps = e13.capitals()
    dist = distractors(caps)
    calib, held = countries_split()
    P, T, D, C = items(calib, caps, dist, "qa")
    if args.phase == "base":
        lt, ld = score(model, P, T), score(model, P, D)
        lab = ld > lt
        R = last_resid(model, P)  # [n, L, d]
        half = set(calib[:len(calib) // 2])
        fit = np.array([c in half for c in C])
        res = {"repo": args.repo, "n_calib": len(calib), "n_held": len(held), "baseline_calib": adoption(model, P, T, D, C),
               "frac_ctx_items": float(lab.mean()), "layers": {}}
        best = None
        for layer in range(model.cfg.n_layers):
            X = R[:, layer]
            m1, m0 = X[fit & lab].mean(0), X[fit & ~lab].mean(0)
            k = m1 - m0
            proj = (X @ k).numpy()
            ev = ~fit
            if lab[ev].sum() < 5 or (~lab[ev]).sum() < 5:
                continue
            a = auc(proj[ev & lab], proj[ev & ~lab])
            res["layers"][layer] = a
            if best is None or a > best[1]:
                best = (layer, a, k)
        layer, a, k = best
        X = R[:, layer]
        k = X[lab].mean(0) - X[~lab].mean(0)  # refit on all calibration items
        khat = k / k.norm()
        scale = float(X.norm(dim=-1).mean())
        torch.save({"layer": layer, "khat": khat, "scale": scale}, OUT / f"{name}__knob.pt")
        curve = {a_: adoption(model, P, T, D, C, layer=layer, vec=a_ * scale * khat) for a_ in ALPHAS}
        res.update({"knob_layer": layer, "knob_auc": a, "resid_scale": scale, "curve": curve,
                    "seconds": round(time.time() - t0, 1)})
        (OUT / f"{name}__base.json").write_text(json.dumps(res, indent=1))
        print(name, f"base {res['baseline_calib']:.3f} knob L{layer} AUC {a:.2f} curve",
              {k_: round(v, 2) for k_, v in curve.items()}, f"({res['seconds']}s)", flush=True)
        return
    # ---- align ----
    kn = torch.load(OUT / f"{name}__knob.pt")
    layer, khat, scale = kn["layer"], kn["khat"], kn["scale"]
    g = torch.Generator().manual_seed(7)
    rnd = torch.randn(khat.shape, generator=g)
    rnd = rnd - (rnd @ khat) * khat
    rnd = rnd / rnd.norm()
    target = args.target
    fit_knob = bisect(lambda a_: adoption(model, P, T, D, C, layer=layer, vec=a_ * scale * khat), target)
    fit_rand = bisect(lambda a_: adoption(model, P, T, D, C, layer=layer, vec=a_ * scale * rnd), target)
    mem = json.loads((mc.RESULTS / "e13" / f"{name}__step{STEP}.json").read_text())["memory_heads"][0][0]
    ml, mh = map(int, mem.split("."))
    fit_head = bisect(lambda f: adoption(model, P, T, D, C, head_scale=(ml, mh, f)), target, lo=0.0, hi=6.0)
    res = {"repo": args.repo, "target": target, "knob_layer": layer, "alpha_knob": fit_knob[0], "calib_knob": fit_knob[1],
           "alpha_rand": fit_rand[0], "calib_rand": fit_rand[1], "head": mem, "head_factor": fit_head[0],
           "calib_head": fit_head[1], "held": {}}
    for tmpl in QUESTIONS:
        Ph, Th, Dh, Ch = items(held, caps, dist, tmpl)
        row = {"base": adoption(model, Ph, Th, Dh, Ch)}
        if fit_knob[0] is not None:
            row["knob"] = adoption(model, Ph, Th, Dh, Ch, layer=layer, vec=fit_knob[0] * scale * khat)
        if fit_rand[0] is not None:
            row["rand"] = adoption(model, Ph, Th, Dh, Ch, layer=layer, vec=fit_rand[0] * scale * rnd)
        if fit_head[0] is not None:
            row["head"] = adoption(model, Ph, Th, Dh, Ch, head_scale=(ml, mh, fit_head[0]))
        res["held"][tmpl] = row
    # side effects of the knob alignment: clean-prompt recall on held-out countries
    clean_P = [QUESTIONS["qa"].format(country=c) for c in held for _ in range(1)]
    if fit_knob[0] is not None:
        tr = [caps[c] for c in held]
        res["clean_true_lp_base"] = float(score(model, clean_P, tr).mean())
        res["clean_true_lp_knob"] = float(score(model, clean_P, tr, layer=layer, vec=fit_knob[0] * scale * khat).mean())
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / f"{name}__align.json").write_text(json.dumps(res, indent=1))
    print(name, "align", {t: {k_: round(v, 3) for k_, v in r.items()} for t, r in res["held"].items()},
          f"alpha {fit_knob[0]} rand {fit_rand[0]} head {fit_head[0]} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
