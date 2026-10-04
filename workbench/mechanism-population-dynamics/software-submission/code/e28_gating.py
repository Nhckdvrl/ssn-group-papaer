"""E28: do context-retrieval heads carry the QA-format switch? (DataDecide 1B)

Per model: (1) attention from the final position to the distractor's first token, per head, for c1_decl and c1_qa
prompts (E26 construction); (2) top-k "context-retrieval heads" chosen format-agnostically (mean of both formats);
(3) causal: ablate those heads' output at the final position (zero their slice of o_proj input) and re-measure
the format effect; control = k random heads matched by layer.
Usage: e28_gating.py --check ; e28_gating.py --repo allenai/DataDecide-dolma1_7-1B --seed default ; --analyze
"""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e28"
K_HEADS, N_ITEMS = 10, 300


def items():
    """Balanced subsample (50 per category) of items known by all 6 E26 Flan-pair models."""
    import dd_common as dd
    import e18_trait as e18
    R = e18.rows()
    known = [set(json.loads((mc.RESULTS / "e26" / f"{r}__{s}.json").read_text())["known"])
             for r in ("dolma1_7-1B", "dolma1_7-no-flan-1B") for s in dd.SEEDS]
    shared = sorted(set.intersection(*known))
    rng = np.random.default_rng(0)
    out = []
    for c in sorted({r["cat"] for r in R}):
        ix = [i for i in shared if R[i]["cat"] == c]
        out += sorted(rng.choice(ix, min(N_ITEMS // 6, len(ix)), replace=False).tolist())
    return R, out


def encode(tok, prompt, dist):
    """Token ids (EOS-prefixed) and index of the first token overlapping the first occurrence of `dist`."""
    enc = tok(prompt, add_special_tokens=False, return_offsets_mapping=True)
    a = prompt.find(dist)
    pos = [j for j, (s, e) in enumerate(enc["offset_mapping"]) if s < a + len(dist) and e > a]
    return [tok.eos_token_id] + enc["input_ids"], 1 + pos[0]


def check():
    import glob
    from transformers import PreTrainedTokenizerFast
    import e26_factorial as e26
    tok = PreTrainedTokenizerFast(tokenizer_file=glob.glob(
        _CACHE + "/hf/models--allenai--DataDecide-dolma1_7-1B/snapshots/*/tokenizer.json")[0],
        eos_token="<|endoftext|>")
    R, ix = items()
    bad = 0
    for i in ix:
        cells, _ = e26.build(R[i])
        for c in ("c1_decl", "c1_qa"):
            ids, p = encode(tok, cells[c], R[i]["dist"])
            piece = tok.decode(ids[p:p + 3])
            bad += R[i]["dist"].split()[0][:3] not in piece
    print("items", len(ix), "distractor-position mismatches", bad)
    i = ix[0]
    cells, _ = e26.build(R[i])
    ids, p = encode(tok, cells["c1_qa"], R[i]["dist"])
    print(repr(cells["c1_qa"]), "| token at pos:", repr(tok.decode(ids[p:p + 2])))
    return bad == 0


def compute(repo, seed):
    import torch
    import dd_common as dd
    import e26_factorial as e26
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16, attn="eager")
    L, H = model.config.num_hidden_layers, model.config.num_attention_heads
    dh = model.config.hidden_size // H
    R, ix = items()
    ablate = {}  # layer -> list of heads to zero
    span = {}    # positions whose logits are scored: prompt-final .. second-to-last candidate token
    # BUGFIX (2026-10-03): the first version zeroed position -1 (the candidate's own last token), whose logits are
    # never scored, so ablation had no effect. Ablate exactly the scored positions instead.

    def pre_hook(layer):
        def f(mod, args):
            if layer not in ablate:
                return None
            x = args[0].clone()
            for h in ablate[layer]:
                x[:, span["a"]:span["b"], h * dh:(h + 1) * dh] = 0
            return (x,)
        return f
    hooks = [model.model.layers[l].self_attn.o_proj.register_forward_pre_hook(pre_hook(l)) for l in range(L)]

    def run(prompts, want_attn):
        att, marg = [], []
        for p, i in prompts:
            ids, pos = encode(tok, p, R[i]["dist"])
            lp = []
            for cand in (R[i]["dist"], R[i]["ans"]):
                c = tok(" " + cand, add_special_tokens=False)["input_ids"]
                x = torch.tensor([ids + c], device=model.device)
                span["a"], span["b"] = len(ids) - 1, len(ids) - 1 + len(c)
                out = model(x, output_attentions=want_attn and cand == R[i]["dist"])
                logp = out.logits[0].float().log_softmax(-1)
                lp.append(float(sum(logp[len(ids) - 1 + j, t] for j, t in enumerate(c))))
                if want_attn and cand == R[i]["dist"]:
                    q = len(ids) - 1
                    att.append(torch.stack([a[0, :, q, pos].float() for a in out.attentions]).cpu().numpy())
            marg.append(lp[0] - lp[1])
        return (np.array(att) if want_attn else None), np.array(marg)

    P = {f: [(e26.build(R[i])[0][f"c1_{f}"], i) for i in ix] for f in ("decl", "qa")}
    A = {}
    M = {}
    for f in P:
        A[f], M[f] = run(P[f], True)                        # [items, L, H]
    score = (A["decl"].mean(0) + A["qa"].mean(0)) / 2       # format-agnostic selection
    top = np.dstack(np.unravel_index(np.argsort(-score.ravel())[:K_HEADS], score.shape))[0].tolist()
    rng = np.random.default_rng(0)
    rand = []
    for l, _ in top:  # layer-matched random heads, excluding the top set
        cands = [h for h in range(H) if [l, h] not in top and [l, h] not in rand]
        rand.append([l, int(rng.choice(cands))])
    res = {"repo": repo, "seed": seed, "items": ix, "top_heads": top, "random_heads": rand,
           "attn_top_decl": float(sum(A["decl"].mean(0)[l, h] for l, h in top)),
           "attn_top_qa": float(sum(A["qa"].mean(0)[l, h] for l, h in top)),
           "attn_random_decl": float(sum(A["decl"].mean(0)[l, h] for l, h in rand)),
           "attn_random_qa": float(sum(A["qa"].mean(0)[l, h] for l, h in rand)),
           "FE_c1_intact": float(M["qa"].mean() - M["decl"].mean())}
    for name, heads in (("top", top), ("random", rand)):
        ablate.clear()
        for l, h in heads:
            ablate.setdefault(l, []).append(h)
        md = run(P["decl"], False)[1]
        mq = run(P["qa"], False)[1]
        res[f"FE_c1_ablate_{name}"] = float(mq.mean() - md.mean())
        res[f"margin_decl_ablate_{name}"] = float(md.mean())
        res[f"margin_qa_ablate_{name}"] = float(mq.mean())
    # built-in validity check: ablating every head at the scored positions must change the margins
    ablate.clear()
    for l in range(L):
        ablate[l] = list(range(H))
    chk = run(P["decl"][:20], False)[1]
    res["check_all_heads_ablated_mean_abs_change"] = float(np.abs(chk - M["decl"][:20]).mean())
    assert res["check_all_heads_ablated_mean_abs_change"] > 0.5, "ablation hook has no effect -> invalid run"
    ablate.clear()
    res["margin_decl_intact"], res["margin_qa_intact"] = float(M["decl"].mean()), float(M["qa"].mean())
    for h in hooks:
        h.remove()
    OUT.mkdir(exist_ok=True)
    name = f"{repo.split('DataDecide-')[1]}__{seed}.json"
    (OUT / name).write_text(json.dumps(res, indent=1))
    print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k not in ("items", "repo")})


def analyze():
    """E28 decision rule, fixed before the run."""
    import dd_common as dd
    D = {(r, s): json.loads((OUT / f"{r}__{s}.json").read_text())
         for r in ("dolma1_7-1B", "dolma1_7-no-flan-1B") for s in dd.SEEDS}
    allm = list(D.values())
    pc_a = np.mean([(d["attn_top_decl"] + d["attn_top_qa"]) / 2 for d in allm]) >= 5 * np.mean(
        [(d["attn_random_decl"] + d["attn_random_qa"]) / 2 for d in allm])
    drop_top = np.mean([d["margin_decl_intact"] - d["margin_decl_ablate_top"] for d in allm])
    drop_rand = np.mean([d["margin_decl_intact"] - d["margin_decl_ablate_random"] for d in allm])
    pc_b = drop_top >= 2 * max(drop_rand, 0) and drop_top > 0
    G = {k: d["attn_top_qa"] - d["attn_top_decl"] for k, d in D.items()}
    a = np.array([G[("dolma1_7-1B", s)] for s in dd.SEEDS])
    b = np.array([G[("dolma1_7-no-flan-1B", s)] for s in dd.SEEDS])
    se = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2) * np.sqrt(2 / 3)
    fl = [D[("dolma1_7-1B", s)] for s in dd.SEEDS]
    red_top = np.mean([1 - d["FE_c1_ablate_top"] / d["FE_c1_intact"] for d in fl])
    red_rand = np.mean([1 - d["FE_c1_ablate_random"] / d["FE_c1_intact"] for d in fl])
    out = {"positive_control_a_attention": bool(pc_a), "positive_control_b_causal": bool(pc_b),
           "drop_decl_top": float(drop_top), "drop_decl_random": float(drop_rand),
           "G_flan": a.tolist(), "G_noflan": b.tolist(), "delta_G": float(a.mean() - b.mean()), "se_G": float(se),
           "read_gating": bool(a.mean() - b.mean() > 2 * se),
           "FE_reduction_top_flan": float(red_top), "FE_reduction_random_flan": float(red_rand),
           "causal_carriage": bool(red_top >= 0.5 and red_rand < 0.2)}
    out["decision"] = ("invalid (positive control failed)" if not (pc_a and pc_b) else
                       {(True, True): "gated retrieval heads", (False, True): "carried, gating not in attention read",
                        (True, False): "attention gating without behavioural carriage",
                        (False, False): "switch not in top-10 retrieval heads"}[(out["read_gating"], out["causal_carriage"])])
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    check() if a.check else analyze() if a.analyze else compute(a.repo, a.seed)
