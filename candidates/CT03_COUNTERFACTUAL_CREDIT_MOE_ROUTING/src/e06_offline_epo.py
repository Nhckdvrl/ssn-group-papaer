"""CT03 E06 -- offline Exact-EPO actionability gate at non-final layers.

The question CPD never answered cleanly: given the BEST POSSIBLE (exact)
counterfactual preference at a non-final layer, can a standard linear router
absorb it and generalise to held-out problems?

No proxy, no new objective, no new module. The parent's EPO form:

    delta_t = CE(r-) - CE(r+)                               exact CE gap
    l_t = -delta_t * log sigmoid( beta * [ (logpi_theta(r+) - logpi_ref(r+))
                                          -(logpi_theta(r-) - logpi_ref(r-)) ] )

r- is the router's own route, r+ the exact-best alternative. Only the gate
matrix trains; the backbone is never touched because the router's only input is
the cached x_t.

ROUTE LIKELIHOOD: the parent's exact form for pi(r|x) was not available to me,
so this uses log pi(S|x) = sum_{e in S} log p(e|x). That is a standard,
differentiable surrogate for a set's likelihood under the router -- it is MY
choice, not a reproduction of the parent's definition, and it is stated rather
than implied.
"""
import argparse, json, sys
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_report import spearman


def logpi(s, route):
    return F.log_softmax(s, -1)[route].sum()


def cells_for(cache, layer, kind="swap"):
    out = []
    for i, md in enumerate(cache["meta"]):
        if md["layer"] != layer:
            continue
        idx = [k for k, kd in enumerate(md["kinds"]) if kd[0] == kind]
        if not idx:
            continue
        dL = np.array([md["dL"][k] for k in idx])
        out.append(dict(i=i, pi=md["pi"], S0=md["S0"], U=md["S0"] + md["C0"],
                        routes=[md["routes"][k] for k in idx], dL=dL))
    return out


def evaluate(W, W0, cells, X, K):
    """Held-out: preference accuracy, route value, and credit-direction rho."""
    acc, vroute, rhos, margins = [], [], [], []
    with torch.no_grad():
        for c in cells:
            if c["dL"].min() >= 0:
                continue
            x = X[c["i"]]
            s, s0 = F.linear(x, W).float(), F.linear(x, W0).float()
            rp = c["routes"][int(c["dL"].argmin())]
            rm = c["S0"]
            d = float(logpi(s, rp) - logpi(s, rm))
            acc.append(float(d > 0)); margins.append(d)
            # route the trained router would now pick inside the same universe
            pick = sorted(c["U"], key=lambda e: -float(s[e]))[:K]
            hit = [k for k, r in enumerate(c["routes"]) if sorted(r) == sorted(pick)]
            vroute.append(float(c["dL"][hit[0]]) if hit else 0.0)
            ds = (s - s0)
            uu, dd = [], []
            for r, v in zip(c["routes"], c["dL"]):
                gone = [e for e in c["S0"] if e not in r]
                new = [e for e in r if e not in c["S0"]]
                if len(gone) == 1 and len(new) == 1:
                    dd.append(float(ds[new[0]] - ds[gone[0]])); uu.append(-float(v))
            if len(uu) >= 3:
                rhos.append(spearman(dd, uu))
    rhos = [r for r in rhos if not np.isnan(r)]
    return dict(pref_acc=float(np.mean(acc)), pref_margin=float(np.mean(margins)),
                V_route=float(np.mean(vroute)), V_route_med=float(np.median(vroute)),
                A_delta=float(np.median(rhos)) if rhos else float("nan"), n=len(acc))


def main(a):
    cache = torch.load(a.cache, map_location="cpu", weights_only=False)
    base_gates = torch.load(a.base_gates, map_location="cpu")
    X = cache["x"].float()
    K = cache["K"]
    res = {}
    for layer in cache["layers"]:
        cells = cells_for(cache, layer)
        pis = sorted({c["pi"] for c in cells})
        cut = int(len(pis) * a.train_frac)
        tr_pi, te_pi = set(pis[:cut]), set(pis[cut:])
        tr = [c for c in cells if c["pi"] in tr_pi and c["dL"].min() < 0]
        te = [c for c in cells if c["pi"] in te_pi]
        print(f"\n=== L{layer}: {len(tr)} train cells / {len(te)} test cells "
              f"({len(tr_pi)}/{len(te_pi)} problems, disjoint) ===")

        # Start from the PRETRAINED gate. Starting from a random init would
        # answer a different question -- whether some router can fit these
        # preferences -- instead of whether THIS router can absorb them.
        W0 = base_gates[str(layer)].clone()
        W = W0.clone().requires_grad_(True)
        opt = torch.optim.AdamW([W], lr=a.lr, weight_decay=0.0)

        base = evaluate(W0, W0, te, X, K)
        print(f"  before: pref_acc {base['pref_acc']:.3f}  V_route {base['V_route']:+.4f}"
              f"  A_delta {base['A_delta']:.3f}  n={base['n']}")
        for ep in range(a.epochs):
            idx = np.random.default_rng(a.seed + ep).permutation(len(tr))
            tot = 0.0
            for b in range(0, len(idx), a.batch):
                opt.zero_grad(set_to_none=True)
                loss = 0.0
                for k in idx[b:b + a.batch]:
                    c = tr[k]
                    x = X[c["i"]]
                    s = F.linear(x, W).float()
                    with torch.no_grad():
                        sr = F.linear(x, W0).float()
                    j = int(c["dL"].argmin())
                    rp, rm = c["routes"][j], c["S0"]
                    delta = float(-c["dL"][j])
                    z = a.beta * ((logpi(s, rp) - logpi(sr, rp))
                                  - (logpi(s, rm) - logpi(sr, rm)))
                    loss = loss - delta * F.logsigmoid(z)
                (loss / max(len(idx[b:b + a.batch]), 1)).backward()
                torch.nn.utils.clip_grad_norm_([W], 1.0)
                opt.step(); tot += float(loss)
            if (ep + 1) % a.eval_every == 0 or ep == a.epochs - 1:
                m = evaluate(W.detach(), W0, te, X, K)
                print(f"  ep{ep+1:>3}: loss {tot/len(tr):.4f}  pref_acc {m['pref_acc']:.3f}"
                      f"  V_route {m['V_route']:+.4f} (med {m['V_route_med']:+.4f})"
                      f"  A_delta {m['A_delta']:.3f}", flush=True)
        res[str(layer)] = dict(before=base, after=evaluate(W.detach(), W0, te, X, K),
                               n_train=len(tr), n_test=len(te))
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="results/e06_cache.pt")
    ap.add_argument("--out", default="results/e06_offline_epo.json")
    ap.add_argument("--base-gates", dest="base_gates",
                    default="results/e06_base_gates.pt")
    ap.add_argument("--train-frac", dest="train_frac", type=float, default=0.67)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--eval-every", dest="eval_every", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
