"""E33: transplant the QA-format residual state onto declarative prompts. Protocol: experiments/E33-*.md.

Usage: e33_transplant.py --repo allenai/DataDecide-dolma1_7-1B --seed default ; e33_transplant.py --analyze
"""
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e33"
LAYERS = [2, 4, 6, 8, 10, 12, 14]


def compute(repo, seed):
    import torch
    import dd_common as dd
    import e18_trait as e18
    import e26_factorial as e26
    import e28_gating as e28
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R, ix = e28.items()
    rng = np.random.default_rng(1)
    perm = rng.permutation(len(ix))
    A, B = [ix[j] for j in perm[: len(ix) // 2]], [ix[j] for j in perm[len(ix) // 2:]]
    state = {"layer": None, "vec": None, "pos": None}

    def hook(layer):
        def f(mod, inp, out):
            if state["layer"] != layer:
                return None
            h = out[0] if isinstance(out, tuple) else out
            h = h.clone()
            h[:, state["pos"], :] += state["vec"].to(h.dtype)
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        return f
    hooks = [model.model.layers[l].register_forward_hook(hook(l)) for l in range(model.config.num_hidden_layers)]

    def enc(p):
        return [tok.eos_token_id] + tok(p, add_special_tokens=False)["input_ids"]

    def margin(i, prompt, layer=None, vec=None):
        ids = enc(prompt)
        lp = []
        for cand in (R[i]["dist"], R[i]["ans"]):
            c = tok(" " + cand, add_special_tokens=False)["input_ids"]
            state.update(layer=layer, vec=vec, pos=len(ids) - 1)
            logp = model(torch.tensor([ids + c], device=model.device)).logits[0].float().log_softmax(-1)
            lp.append([float(logp[len(ids) - 1 + j, t]) for j, t in enumerate(c)])
        state["layer"] = None
        return sum(lp[0]) - sum(lp[1]), lp[0][0] - lp[1][0]

    def final_dist(prompt, layer=None, vec=None):
        ids = enc(prompt)
        state.update(layer=layer, vec=vec, pos=len(ids) - 1)
        out = model(torch.tensor([ids], device=model.device), output_hidden_states=True)
        state["layer"] = None
        return out.logits[0, -1].float().log_softmax(-1), [h[0, -1].float() for h in out.hidden_states]

    P = {i: e26.build(R[i])[0] for i in ix}
    # format vectors on half A (hidden_states[l+1] = output of layer l)
    diffs = {l: [] for l in LAYERS}
    for i in A:
        _, hq = final_dist(P[i]["c1_qa"])
        _, hd = final_dist(P[i]["c1_decl"])
        for l in LAYERS:
            diffs[l].append(hq[l + 1] - hd[l + 1])
    V = {l: torch.stack(diffs[l]).mean(0) for l in LAYERS}
    # built-in checks: zero vector is a no-op; the real vector changes the output
    i0 = A[0]
    m0 = margin(i0, P[i0]["c1_decl"])
    mz = margin(i0, P[i0]["c1_decl"], LAYERS[3], torch.zeros_like(V[LAYERS[3]]))
    mv = margin(i0, P[i0]["c1_decl"], LAYERS[3], V[LAYERS[3]])
    assert abs(m0[0] - mz[0]) < 1e-3, f"zero-vector hook is not a no-op: {m0} vs {mz}"
    assert abs(m0[0] - mv[0]) > 1e-3, "format-vector hook has no effect"
    # layer selection on A
    base_A = np.array([margin(i, P[i]["c1_decl"])[0] for i in A])
    gain = {l: float(np.mean([margin(i, P[i]["c1_decl"], l, V[l])[0] for i in A]) - base_A.mean()) for l in LAYERS}
    lstar = max(gain, key=gain.get)
    # test on B
    md = np.array([margin(i, P[i]["c1_decl"]) for i in B])
    mq = np.array([margin(i, P[i]["c1_qa"]) for i in B])
    mt = np.array([margin(i, P[i]["c1_decl"], lstar, V[lstar]) for i in B])
    kl0, kl1 = [], []
    for i in B:
        pq, _ = final_dist(P[i]["c1_qa"])
        pd, _ = final_dist(P[i]["c1_decl"])
        pt, _ = final_dist(P[i]["c1_decl"], lstar, V[lstar])
        kl = lambda a, b: float((a.exp() * (a - b)).sum())
        kl0.append(kl(pq, pd)); kl1.append(kl(pq, pt))
    for h in hooks:
        h.remove()
    res = {"repo": repo, "seed": seed, "gain_A": gain, "layer": lstar,
           "margin_decl": float(md[:, 0].mean()), "margin_qa": float(mq[:, 0].mean()), "margin_transplant": float(mt[:, 0].mean()),
           "delta": float(mt[:, 0].mean() - md[:, 0].mean()), "FE": float(mq[:, 0].mean() - md[:, 0].mean()),
           "delta_first_token": float(mt[:, 1].mean() - md[:, 1].mean()), "FE_first_token": float(mq[:, 1].mean() - md[:, 1].mean()),
           "KL_qa_decl": float(np.mean(kl0)), "KL_qa_transplant": float(np.mean(kl1)),
           "check_zero_noop": float(abs(m0[0] - mz[0])), "check_vec_effect": float(abs(m0[0] - mv[0]))}
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('DataDecide-')[1]}__{seed}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "repo"}), flush=True)


def analyze():
    import dd_common as dd
    D = {(r, s): json.loads((OUT / f"{r}__{s}.json").read_text()) for r in ("dolma1_7-1B", "dolma1_7-no-flan-1B") for s in dd.SEEDS}
    pc = all(d["KL_qa_transplant"] <= 0.7 * d["KL_qa_decl"] for d in D.values())
    a = np.array([D[("dolma1_7-1B", s)]["delta"] for s in dd.SEEDS])
    b = np.array([D[("dolma1_7-no-flan-1B", s)]["delta"] for s in dd.SEEDS])
    se = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2) * np.sqrt(2 / 3)
    rec = np.mean([D[("dolma1_7-1B", s)]["delta"] / D[("dolma1_7-1B", s)]["FE"] for s in dd.SEEDS])
    diff = a.mean() - b.mean()
    out = {"method_positive_control": bool(pc), "delta_flan": a.tolist(), "delta_noflan": b.tolist(),
           "delta_diff": float(diff), "se": float(se), "recovery_flan": float(rec),
           "layers": {f"{r}__{s}": D[(r, s)]["layer"] for (r, s) in D}}
    out["decision"] = ("invalid (method positive control failed)" if not pc else
                       "format state carries the switch" if rec >= 0.5 and diff > 2 * se else
                       "partially carries" if 0.2 <= rec < 0.5 and diff > 2 * se else
                       "not carried by a single final-position format state" if diff <= 2 * se else "other (report)")
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.seed)
