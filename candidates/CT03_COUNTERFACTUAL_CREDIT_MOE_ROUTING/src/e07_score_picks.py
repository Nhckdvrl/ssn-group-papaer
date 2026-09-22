"""CT03 E07 -- exactly evaluate the route the trained router actually picks.

The offline EPO gate left V_route unusable: 93-98% of the trained router's
top-8 picks were routes never evaluated, so the reported value came from a 2-7%
tail. EPO's objective only constrains one comparison (r+ beats r-), and the
router satisfies it by reordering the whole candidate region, landing on
multi-expert routes outside both recorded action spaces.

This replays those picks exactly, on the same cached states, so V_route becomes
a real measurement instead of a residue.
"""
import argparse, json, sys
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, replay_ce
from e01_report import spearman


def main(a):
    cache = torch.load(a.cache, map_location="cpu", weights_only=False)
    gates = torch.load(a.trained, map_location="cpu")
    base = torch.load(a.base_gates, map_location="cpu")
    K = cache["K"]
    tok, model = load(a)
    dev0 = next(model.parameters()).device

    # which cells, and which route each arm would pick
    want = {}
    for ci, md in enumerate(cache["meta"]):
        l = md["layer"]
        if str(l) not in gates:
            continue
        x = cache["x"][ci]
        U = md["S0"] + md["C0"]
        picks = {}
        for tag, W in (("trained", gates[str(l)]), ("base", base[str(l)])):
            s = F.linear(x, W.float()).float()
            picks[tag] = sorted(sorted(U, key=lambda e: -float(s[e]))[:K])
        want[ci] = picks
    print(f"cells: {len(want)}", flush=True)

    ds = json.load(open(a.pool))["items"]
    rows = []
    by_pi = {}
    for ci, md in enumerate(cache["meta"]):
        by_pi.setdefault(md["pi"], []).append(ci)

    for pi in sorted(by_pi):
        ex = ds[pi]
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        layers = sorted({cache["meta"][c]["layer"] for c in by_pi[pi]})
        with Capture(model, layers) as cap:
            with torch.no_grad():
                model(input_ids)
            xs = {l: cap.mlp_in[l].detach() for l in layers}
            hs = {l: cap.mlp_out[l].detach() for l in layers}
            lo = {l: cap.layer_out[l].detach() for l in layers}
            akw = cap.attn_kwargs
        for ci in by_pi[pi]:
            md = cache["meta"][ci]
            l, t = md["layer"], md["pos"]
            moe = model.model.layers[l].mlp
            x, h = xs[l][0, t], hs[l][0, t]
            p0 = F.softmax(F.linear(x, moe.gate.weight).float(), -1)
            U = md["S0"] + md["C0"]
            with torch.no_grad():
                bank = {e: moe.experts[e](x) for e in U}
            pat, tags = [], []
            for tag in ("trained", "base"):
                r = want[ci][tag]
                Z = float(p0[r].sum())
                v = None
                for e in r:
                    w = bank[e] * (float(p0[e]) / Z)
                    v = w if v is None else v + w
                pat.append(v - h); tags.append(tag)
            H = lo[l].expand(len(pat) + 1, -1, -1).clone()
            H[1:, t] += torch.stack(pat)
            ce = replay_ce(model, l, H, t, targets, **akw)
            dL = (ce[1:] - ce[0]).sum(dim=1).cpu().numpy()
            rows.append(dict(ci=ci, pi=pi, layer=l, pos=t,
                             **{f"V_{tg}": float(v) for tg, v in zip(tags, dL)},
                             n_changed=len(set(want[ci]["trained"]) - set(md["S0"])),
                             best_swap=float(min(md["dL"]))))
        del xs, hs, lo
        torch.cuda.empty_cache()
        print(f"  pi={pi} done ({len(rows)} rows)", flush=True)

    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    report(rows, a.holdout_from)


def report(rows, cut):
    rng = np.random.default_rng(0)
    print("\n" + "=" * 78)
    print("EXACT value of the route the TRAINED router picks (held-out problems only)")
    print(f"{'layer':>6}{'n':>6}{'V_trained':>12}{'V_base':>11}{'paired diff':>13}"
          f"{'95% CI':>22}{'win':>7}{'n_chg':>7}")
    for l in sorted({r["layer"] for r in rows}):
        v = [r for r in rows if r["layer"] == l and r["pi"] >= cut]
        if not v:
            continue
        d = np.array([r["V_trained"] - r["V_base"] for r in v])
        bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(10000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"{l:>6}{len(v):>6}{np.mean([r['V_trained'] for r in v]):>12.4f}"
              f"{np.mean([r['V_base'] for r in v]):>11.4f}{d.mean():>13.4f}"
              f"  [{lo:+.4f},{hi:+.4f}]{np.mean(d < 0):>7.3f}"
              f"{np.mean([r['n_changed'] for r in v]):>7.2f}"
              f"  {'SIG' if (lo > 0 or hi < 0) else 'ns'}")
    print("\n(negative V = better than the base route; negative diff = trained better)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="results/e06_cache_all.pt")
    ap.add_argument("--trained", default="results/e06_trained_gates.pt")
    ap.add_argument("--base-gates", dest="base_gates", default="results/e06_base_gates.pt")
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e07_picks.jsonl")
    ap.add_argument("--holdout-from", dest="holdout_from", type=int, default=79)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
