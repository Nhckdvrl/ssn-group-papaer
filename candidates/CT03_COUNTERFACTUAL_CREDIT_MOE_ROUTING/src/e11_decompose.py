"""CT03 E11 -- where did the router's new top-8 actually come from? Zero GPU.

The mechanism story says the preference objective is satisfiable without
adoption because ranking two fixed 8-subsets against each other places no
constraint on which subset is on top: crushing r-'s experts lets the top-8
relocate to experts in NEITHER set. That is a claim about the composition of
the learned top-8, so it should be read off the learned gate directly rather
than inferred from ov falling.
"""
import argparse, json, sys
import numpy as np
import torch
import torch.nn.functional as F


def main(a):
    d = torch.load(a.ev, map_location="cpu", weights_only=False)
    W0, K = d["W0"], d["K"]
    out = {}
    for name, path in [("W0", None)] + [tuple(z.split("=")) for z in a.gates]:
        W = W0 if path is None else torch.load(path, map_location="cpu")["47"]
        n, inp, inm, both, neither, ovs = 0, 0, 0, 0, 0, []
        for e in d["ev"]:
            m = e["better"]
            if not int(m.sum()):
                continue
            # x is not dumped; scores come from the cache, so recompute there
            top = torch.topk(F.softmax(a.X[e["k"][m]] @ W.T, -1), K, -1).indices
            P = e["id_p"][m]          # r+ : the route the objective prefers
            M = e["id_m"][m]          # r- : the route W0 executed
            isp = (top.unsqueeze(-1) == P.unsqueeze(1)).any(-1)
            ism = (top.unsqueeze(-1) == M.unsqueeze(1)).any(-1)
            n += isp.numel()
            inp += int((isp & ~ism).sum()); inm += int((ism & ~isp).sum())
            both += int((isp & ism).sum()); neither += int((~isp & ~ism).sum())
            ovs += isp.sum(-1).float().tolist()
        r = dict(n_slots=n, frac_in_rplus_only=inp / n, frac_in_rminus_only=inm / n,
                 frac_in_both=both / n, frac_in_neither=neither / n,
                 ov=float(np.mean(ovs)))
        out[name] = r
        print(f"{name:26s} of every executed expert slot: "
              f"r+only {r['frac_in_rplus_only']:.3f}  r-only {r['frac_in_rminus_only']:.3f}  "
              f"both {r['frac_in_both']:.3f}  NEITHER {r['frac_in_neither']:.3f}   "
              f"ov {r['ov']:.2f}/{K}")
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ev", default="results/e11_ev.pt")
    ap.add_argument("--cache", nargs="+",
                    default=["results/e11_cache_a.pt", "results/e11_cache_b.pt"])
    ap.add_argument("--gates", nargs="+", default=[
        "online_pref=results/e11_gate_traineval.pt",
        "fixed_pref=results/e11_gate_lr3e5.pt"])
    ap.add_argument("--out", default="results/e11_decompose.json")
    a = ap.parse_args()
    a.X = torch.cat([torch.load(f, map_location="cpu", weights_only=False)["x"]
                     for f in a.cache])
    main(a)
