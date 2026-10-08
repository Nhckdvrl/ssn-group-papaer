"""flan_layout: does the Flan component move the head layout, and where does the Question: habit live? Protocol:
flan_layout-*.md.

  flan_layout.py --recipe dolma1_7 --seed default   # per-head attention to the context entity, per template
  flan_layout.py --analyze
Per model: for the 300 the retrieval probe items and the habit_templates templates decl / QA (Question: ... Answer:) / QA_short (Q: ... A:) /
novel (Query: ... Response:), the attention of every head from the last prompt token to the first token of the
counterfactual entity in the context (the M4 retrieval read-out), averaged separately over odd and even items, and the
per-item margin log p(counterfactual) - log p(memorized answer).
"""
import argparse
import itertools
import json

import numpy as np

import common as mc
OUT = mc.RESULTS / "flan_layout"
CELLS = ("decl", "QA", "QA_short", "novel")
FLAN = ("dolma1_7", "dolma1_7-no-code", "dolma1_7-no-math-code", "dolma1_7-no-reddit")
NOFLAN = ("dolma1_7-no-flan",)
SEEDS = ("default", "large-aux-2", "large-aux-3")


def models():
    return [(r, s) for r in FLAN + NOFLAN for s in SEEDS if (r, s) not in mc.UNVERIFIED_1B]


def compute(recipe, seed):
    import torch
    import datadecide as dd
    import prompts
    import habit_templates
    from prompts import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(f"allenai/DataDecide-{recipe}-1B", dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16,
                         attn="eager")
    R, ix = prompts.items()
    B = habit_templates.build_all(R)
    L, H = model.config.num_hidden_layers, model.config.num_attention_heads
    res = {"recipe": recipe, "seed": seed, "items": [int(i) for i in ix], "attn": {}, "margin": {}}
    for c in CELLS:
        A = np.zeros((2, L, H))
        n = [0, 0]
        for j, i in enumerate(ix):
            ids, pos = prompts.encode(tok, B[i][c], R[i]["dist"])
            out = model(torch.tensor([ids], device="cuda"), output_attentions=True)
            A[j % 2] += torch.stack([a[0, :, -1, pos].float().cpu() for a in out.attentions]).numpy()
            n[j % 2] += 1
        res["attn"][c] = [(A[h] / n[h]).round(6).tolist() for h in (0, 1)]
        P = [B[i][c] for i in ix]
        res["margin"][c] = (cand_logprob(model, tok, P, [R[i]["dist"] for i in ix])
                            - cand_logprob(model, tok, P, [R[i]["ans"] for i in ix])).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{recipe}__{seed}.json").write_text(json.dumps(res))
    print(recipe, seed, {c: round(float(np.mean(v)), 2) for c, v in res["margin"].items()}, flush=True)


def within(a, b):
    """Within-layer Spearman of two [layer x head] maps, averaged over layers (the paper's which-head agreement)."""
    from scipy.stats import spearmanr
    a, b = np.asarray(a), np.asarray(b)
    return float(np.nanmean([spearmanr(x, y)[0] for x, y in zip(a, b)]))


def pair_class(a, b):
    return "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"


def layout_flan_vs_other():
    """(a) same-seed agreement of Flan / no-Flan pairs vs other Dolma 1.7 ablation pairs, for the nine role maps."""
    maps = {}
    for r, s in models():
        m = json.loads((mc.RESULTS / "crossing_1b" / f"{r}-1B__{s}.json").read_text())
        mm = {k: v for k, v in m["maps"].items() if k != "M1" or m["M1_max"] > 0.3}
        f59 = mc.RESULTS / "more_roles" / f"{r}__{s}.json"
        if f59.exists():
            mm |= json.loads(f59.read_text())["maps"]
        maps[(r, s)] = mm
    out = {}
    roles = sorted(set.intersection(*(set(v) for v in maps.values())))
    for role in roles:
        g = {"flan_vs_noflan": [], "flan_vs_flan": [], "other_seed": []}
        for a, b in itertools.combinations(sorted(maps), 2):
            v = within(maps[a][role], maps[b][role])
            if a[1] != b[1]:
                if a[0] == b[0]:
                    g["other_seed"].append(v)
                continue
            key = "flan_vs_noflan" if ("dolma1_7-no-flan" in (a[0], b[0])) else "flan_vs_flan"
            g[key].append(v)
        out[role] = {k: [float(np.mean(v)), len(v)] for k, v in g.items()}
        print("(a)", role, {k: (round(v[0], 3), v[1]) for k, v in out[role].items()})
    return out


def habit_maps():
    D = {k: json.loads((OUT / f"{k[0]}__{k[1]}.json").read_text()) for k in models()
         if (OUT / f"{k[0]}__{k[1]}.json").exists()}
    out = {"n_models": len(D), "behaviour": {}, "total_attention": {}}
    for k, d in D.items():
        m = {c: np.mean(v) for c, v in d["margin"].items()}
        a = {c: np.mean(d["attn"][c], 0).sum() for c in CELLS}  # summed over heads, both halves
        out["behaviour"][f"{k[0]}__{k[1]}"] = {c: float(m[c] - m["decl"]) for c in CELLS[1:]}
        out["total_attention"][f"{k[0]}__{k[1]}"] = {c: float(a[c] - a["decl"]) for c in CELLS[1:]}
    fl = sorted(k for k in D if k[0] in FLAN)
    nf = sorted(k for k in D if k[0] in NOFLAN)
    for grp, ks in (("flan", fl), ("noflan", nf)):
        out[f"mean_behaviour_{grp}"] = {c: float(np.mean([out["behaviour"][f"{a}__{b}"][c] for a, b in ks]))
                                        for c in CELLS[1:]}
        out[f"mean_total_attention_{grp}"] = {c: float(np.mean([out["total_attention"][f"{a}__{b}"][c] for a, b in ks]))
                                              for c in CELLS[1:]}
    # (b) which-head agreement of the habit map (QA - decl) and of the declarative retrieval map, among Flan models
    hab = {k: np.array(D[k]["attn"]["QA"]) - np.array(D[k]["attn"]["decl"]) for k in D}  # 2 x L x H
    ret = {k: np.array(D[k]["attn"]["decl"]) for k in D}
    out["split_half_habit"] = float(np.mean([within(hab[k][0], hab[k][1]) for k in fl]))
    out["split_half_retrieval"] = float(np.mean([within(ret[k][0], ret[k][1]) for k in fl]))
    for name, M in (("habit", hab), ("retrieval_decl", ret)):
        g = {"SI": [], "SD": [], "DD": []}
        for a, b in itertools.combinations(fl, 2):
            g[pair_class(a, b)].append(within(M[a].mean(0), M[b].mean(0)))
        out[f"agreement_{name}"] = {c: [float(np.mean(v)), len(v)] for c, v in g.items()}
        # recipe-bootstrap CI of SI - SD
        rng = np.random.default_rng(0)
        recs = sorted({k[0] for k in fl})
        sims = {(a, b): within(M[a].mean(0), M[b].mean(0)) for a, b in itertools.combinations(fl, 2)}
        boots = []
        for _ in range(1000):
            w = rng.choice(recs, len(recs))
            cnt = {r: int((w == r).sum()) for r in recs}
            gg = {"SI": [], "SD": []}
            for (a, b), v in sims.items():
                c = pair_class(a, b)
                if c in gg and cnt[a[0]] and cnt[b[0]]:
                    gg[c] += [v] * (cnt[a[0]] * cnt[b[0]])
            if gg["SI"] and gg["SD"]:
                boots.append(np.mean(gg["SI"]) - np.mean(gg["SD"]))
        out[f"agreement_{name}"]["ci95_SI_minus_SD"] = np.percentile(boots, [2.5, 97.5]).tolist()
        print("(b)", name, out[f"agreement_{name}"])
    # (c) within each Flan model: habit map vs its own declarative retrieval map; and vs a same-seed sibling's map
    out["habit_vs_own_retrieval"] = float(np.mean([within(hab[k].mean(0), ret[k].mean(0)) for k in fl]))
    out["habit_vs_noflan_sibling_retrieval"] = float(np.mean(
        [within(hab[k].mean(0), ret[("dolma1_7-no-flan", k[1])].mean(0)) for k in fl if ("dolma1_7-no-flan", k[1]) in D]))
    out["habit_vs_other_seed_retrieval"] = float(np.mean(
        [within(hab[a].mean(0), ret[b].mean(0)) for a in fl for b in D if b[1] != a[1]]))
    # how concentrated: share of the summed habit increase carried by the model's top-10 declarative retrieval heads
    conc = []
    for k in fl:
        h, r = hab[k].mean(0).ravel(), ret[k].mean(0).ravel()
        top = np.argsort(-r)[:10]
        conc.append(float(h[top].sum() / h[h > 0].sum()))
    out["habit_share_in_top10_retrieval"] = float(np.mean(conc))
    for k in ("split_half_habit", "split_half_retrieval", "habit_vs_own_retrieval", "habit_vs_noflan_sibling_retrieval",
              "habit_vs_other_seed_retrieval", "habit_share_in_top10_retrieval", "mean_behaviour_flan",
              "mean_behaviour_noflan", "mean_total_attention_flan", "mean_total_attention_noflan"):
        print(k, out[k])
    return out


def template_contrast():
    """POST-HOC: the Flan-specific part of the habit, as the template contrast Question: - Q: (and - Query:) of the
    attention to the context entity: its total over heads (Flan vs no-Flan), its which-head agreement among the Flan
    models, and the share of its positive part on the model's own ten strongest declarative retrieval heads."""
    D = {k: json.loads((OUT / f"{k[0]}__{k[1]}.json").read_text()) for k in models()}
    A = lambda k, c: np.array(D[k]["attn"][c])
    fl = sorted(k for k in D if k[0] in FLAN)
    nf = sorted(k for k in D if k[0] in NOFLAN)
    out = {}
    for name, other in (("question_minus_q", "QA_short"), ("question_minus_query", "novel")):
        M = {k: A(k, "QA") - A(k, other) for k in D}
        g = {"SI": [], "SD": []}
        for a, b in itertools.combinations(fl, 2):
            c = pair_class(a, b)
            if c in g:
                g[c].append(within(M[a].mean(0), M[b].mean(0)))
        share, base, cross = [], [], []
        for k in fl:
            h, r = M[k].mean(0).ravel(), A(k, "decl").mean(0).ravel()
            top = np.argsort(-r)[:10]
            share.append(float(h[top].clip(0).sum() / h.clip(0).sum()))
            base.append(float(r[top].sum() / r.sum()))  # the same heads' share of the attention to the entity itself
            for hd, hm in ((0, 1), (1, 0)):  # cross-fit: heads chosen on one half of the items, gain read on the other
                rr, hh = A(k, "decl")[hd].ravel(), M[k][hm].ravel()
                cross.append(float(hh[np.argsort(-rr)[:10]].clip(0).sum() / hh.clip(0).sum()))
        out[name] = {"split_half": float(np.mean([within(M[k][0], M[k][1]) for k in fl])),
                     "total_flan": float(np.mean([M[k].mean(0).sum() for k in fl])),
                     "total_noflan": float(np.mean([M[k].mean(0).sum() for k in nf])),
                     "SI": float(np.mean(g["SI"])), "SD": float(np.mean(g["SD"])),
                     "share_top10_retrieval": float(np.mean(share)), "share_expected": 10 / M[fl[0]][0].size,
                     "share_top10_retrieval_crossfit": float(np.mean(cross)),
                     "top10_share_of_entity_attention": float(np.mean(base)),
                     "vs_noflan_sibling_same_seed": float(np.mean(
                         [within(M[k].mean(0), M[("dolma1_7-no-flan", k[1])].mean(0)) for k in fl]))}
        print("(posthoc)", name, {k: round(v, 3) for k, v in out[name].items()})
    return out


def analyze():
    res = {"layout_flan_vs_other": layout_flan_vs_other(), "habit": habit_maps(), "posthoc_template_contrast": template_contrast()}
    (mc.RESULTS / "flan_layout" / "analysis.json").write_text(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe")
    ap.add_argument("--seed")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    elif a.all:
        for r, s in models():
            if not (OUT / f"{r}__{s}.json").exists():
                compute(r, s)
    else:
        compute(a.recipe, a.seed)


if __name__ == "__main__":
    main()
