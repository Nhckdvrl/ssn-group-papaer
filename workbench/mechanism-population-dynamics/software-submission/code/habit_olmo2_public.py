"""habit_olmo2_public: QA-format switch in public base models / OLMo-2 midtraining checkpoints.

Usage: habit_olmo2_public.py --repo allenai/OLMo-2-0425-1B --rev stage1-step1907359-tokens4001B
       habit_olmo2_public.py --analyze
"""
import argparse
import json
import re

import numpy as np

import common as mc
OUT = mc.RESULTS / "habit_olmo2_public"
CELLS = ("c1_decl", "c1_qa", "cK_decl", "cK_qa")


def tag(repo, rev):
    return f"{repo.split('/')[-1]}__{rev or 'main'}"


def compute(repo, rev):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import prompts
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE),
                                                 torch_dtype=torch.bfloat16).cuda().eval()
    start = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def lp(prompts, cands, bs=16):
        out = []
        for i in range(0, len(prompts), bs):
            P, C = prompts[i:i + bs], cands[i:i + bs]
            pi = [tok(p, add_special_tokens=False)["input_ids"] for p in P]
            ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in C]
            seqs = [[start] + a + b for a, b in zip(pi, ci)]
            L = max(map(len, seqs))
            ids = torch.full((len(seqs), L), pad)
            att = torch.zeros((len(seqs), L), dtype=torch.long)
            for j, s in enumerate(seqs):
                ids[j, :len(s)] = torch.tensor(s)
                att[j, :len(s)] = 1
            logp = model(ids.cuda(), attention_mask=att.cuda()).logits.float().log_softmax(-1)
            for j, (a, b) in enumerate(zip(pi, ci)):
                st = 1 + len(a)
                pos = torch.arange(st - 1, st - 1 + len(b), device=logp.device)
                out.append(float(logp[j, pos, torch.tensor(b, device=logp.device)].sum()))
        return np.array(out)

    R = prompts.rows()
    ct, cd = lp([r["clean"] for r in R], [r["ans"] for r in R]), lp([r["clean"] for r in R], [r["dist"] for r in R])
    built = [prompts.build(r)[0] for r in R]
    res = {"repo": repo, "rev": rev, "start_token": int(start), "known": [int(i) for i in np.where(ct > cd)[0]],
           "clean": (ct - cd).round(4).tolist(), "cells": {}}
    for c in CELLS:
        P = [b[c] for b in built]
        res["cells"][c] = (lp(P, [r["dist"] for r in R]) - lp(P, [r["ans"] for r in R])).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{tag(repo, rev)}.json").write_text(json.dumps(res))
    kn = res["known"]
    print(tag(repo, rev), "n_known", len(kn), {c: round(float(np.mean(np.array(v)[kn])), 2) for c, v in res["cells"].items()},
          flush=True)


def effects(d, R, items):
    cats = sorted({r["cat"] for r in R})
    by = [[i for i in items if R[i]["cat"] == c] for c in cats]
    m = {c: float(np.mean([np.mean(np.array(v)[ix]) for ix in by if len(ix) >= 10])) for c, v in d["cells"].items()}
    cl = np.array(d["clean"])
    return {"FE_c1": m["c1_qa"] - m["c1_decl"], "c1_decl": m["c1_decl"], "c1_qa": m["c1_qa"],
            "count": (m["cK_decl"] + m["cK_qa"]) / 2 - (m["c1_decl"] + m["c1_qa"]) / 2,
            "K": float(np.mean([cl[[i for i, r in enumerate(R) if r["cat"] == c]].mean() for c in cats]))}


def analyze():
    import prompts
    R = prompts.rows()
    D = {f.stem: json.loads(f.read_text()) for f in OUT.glob("*.json") if f.stem != "analysis"}
    olmo = {k: v for k, v in D.items() if k.startswith("OLMo-2-0425-1B__")}
    s1 = sorted(k for k in olmo if "__stage1-" in k)[-3:]
    s2_final = {}
    for k in olmo:
        m = re.search(r"stage2-ingredient(\d)-step(\d+)", k)
        if m and int(m.group(2)) >= max(int(re.search(r"step(\d+)", j).group(1)) for j in olmo
                                        if f"ingredient{m.group(1)}-" in j):
            s2_final[m.group(1)] = k
    out = {}
    if len(s1) == 3 and len(s2_final) == 3:
        keys = s1 + sorted(s2_final.values())
        sh = sorted(set.intersection(*[set(olmo[k]["known"]) for k in keys]))
        E = {k: effects(olmo[k], R, sh) for k in keys}
        a = np.array([E[k]["FE_c1"] for k in sorted(s2_final.values())])
        b = np.array([E[k]["FE_c1"] for k in s1])
        se = np.sqrt(a.var(ddof=1) / 3 + b.var(ddof=1) / 3)
        dd = np.mean([E[k]["c1_decl"] for k in s2_final.values()]) - np.mean([E[k]["c1_decl"] for k in s1])
        out["partA"] = {"n_shared": len(sh), "stage1": {k: E[k] for k in s1}, "stage2_final": {k: E[k] for k in s2_final.values()},
                        "delta_FE": float(a.mean() - b.mean()), "se": float(se), "delta_decl": float(dd),
                        "switch_installed": bool(a.mean() - b.mean() > 2 * se and abs(dd) < (a.mean() - b.mean()) / 2),
                        "count_positive": bool(all(E[k]["count"] > 0 for k in keys)),
                        "K_not_lower": bool(np.mean([E[k]["K"] for k in s2_final.values()]) >= np.mean([E[k]["K"] for k in s1]))}
        traj = sorted((int(re.search(r"step(\d+)", k).group(1)), k) for k in olmo if "ingredient1-" in k)
        out["partA"]["ingredient1_trajectory"] = [(s, effects(olmo[k], R, sh)["FE_c1"]) for s, k in traj]
    out["partB"] = {k: effects(v, R, v["known"]) for k, v in D.items() if not k.startswith("OLMo-2-0425-1B__stage")}
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rev", default=None)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.rev)
