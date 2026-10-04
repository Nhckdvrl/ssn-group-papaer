"""E49: the Flan "Question:" switch on a third conflict dataset (NQ-Swap, Longpre et al. 2021).

  e49_nqswap.py --check
  e49_nqswap.py --family dd --repo allenai/DataDecide-dolma1_7-1B --rev step69369-seed-default --name dd1B__dolma1_7__default
  e49_nqswap.py --family hf --repo allenai/OLMo-2-0425-1B --rev stage1-step1907359-tokens4001B --name olmo2__stage1-step1907359
  e49_nqswap.py --analyze
Readout: margin = lp(sub_answer) - lp(org_answer) after the (substituted) context + cue; primary cue effect =
margin(Question:/Answer:) - margin(Q:/A:)  (E32: "Q:/A:" does not trigger the switch).
"""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import argparse
import json
import re

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e49"
CELLS = ("QA", "QA_short", "novel")
WIN = 120


def clean(t):
    t = re.sub(r"</?[A-Za-z]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def items():
    from datasets import load_dataset
    ds = load_dataset("pminervini/NQ-Swap", cache_dir=_CACHE + "/hf_datasets")["dev"]
    out, drop = [], {"no_sub": 0, "org_leak": 0}
    for r in ds:
        sub, org = r["sub_answer"][0].strip(), r["org_answer"][0].strip()
        ctx = clean(r["sub_context"])
        w = ctx.split()
        a = ctx.find(sub)
        if a < 0:
            drop["no_sub"] += 1
            continue
        k = len(ctx[:a].split())
        ctx = " ".join(w[max(0, k - WIN // 2): max(0, k - WIN // 2) + WIN])
        if sub not in ctx:
            drop["no_sub"] += 1
            continue
        if org in ctx or org.lower() == sub.lower():
            drop["org_leak"] += 1
            continue
        q = r["question"].strip()
        q = q[0].upper() + q[1:] + ("" if q.endswith("?") else "?")
        out.append({"ctx": ctx, "q": q, "sub": sub, "org": org,
                    "QA": f"{ctx} Question: {q} Answer:", "QA_short": f"{ctx} Q: {q} A:",
                    "novel": f"{ctx} Query: {q} Response:", "closed": f"Question: {q} Answer:"})
    return out, drop


def check():
    R, drop = items()
    print("items kept", len(R), "dropped", drop)
    for c in CELLS + ("closed",):
        print(f"--- {c}: {R[0][c][-220:]!r}  | sub={R[0]['sub']!r} org={R[0]['org']!r}")


def compute(family, repo, rev, name):
    import torch
    f = OUT / f"{name}.json"
    if f.exists():
        return
    torch.set_grad_enabled(False)
    if family == "dd":
        import dd_common as dd
        model, tok = dd.load(repo, rev, dtype=torch.bfloat16)
        start, pad = tok.eos_token_id, tok.pad_token_id
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE))
        model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE),
                                                     torch_dtype=torch.bfloat16).cuda().eval()
        start = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
        pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def lp(prompts, cands, bs=16):  # same as E30 (summed log-prob of " " + cand after start token + prompt)
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
    R, _ = items()
    S, O = [r["sub"] for r in R], [r["org"] for r in R]
    res = {"repo": repo, "rev": rev, "start": int(start), "cells": {}}
    res["closed"] = (lp([r["closed"] for r in R], O) - lp([r["closed"] for r in R], S)).round(4).tolist()
    for c in CELLS:
        P = [r[c] for r in R]
        res["cells"][c] = (lp(P, S) - lp(P, O)).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    f.write_text(json.dumps(res))
    print(name, {c: round(float(np.mean(v)), 3) for c, v in res["cells"].items()}, flush=True)


def analyze():
    out = {}
    groups = {"datadecide_1B": ([f"dd1B__dolma1_7__{s}" for s in ("default", "large-aux-2", "large-aux-3")],
                                [f"dd1B__dolma1_7-no-flan__{s}" for s in ("default", "large-aux-2", "large-aux-3")]),
              "olmo2_midtraining": ([f"olmo2__stage2-ingredient{k}-step23852-tokens51B" for k in (1, 2, 3)],
                                    ["olmo2__stage1-step1907359-tokens4001B", "olmo2__stage1-step1900000-tokens3985B",
                                     "olmo2__stage1-step1890000-tokens3964B"])}
    for g, (A, B) in groups.items():
        D = {n: json.loads((OUT / f"{n}.json").read_text()) for n in A + B if (OUT / f"{n}.json").exists()}
        if len(D) < 6:
            continue
        known = set.intersection(*[set(np.flatnonzero(np.array(d["closed"]) > 0)) for d in D.values()])
        sel = sorted(known) if len(known) >= 100 else list(range(len(next(iter(D.values()))["closed"])))
        row = {"n_items": len(sel), "item_set": "shared-known" if len(known) >= 100 else "all (fallback)",
               "n_shared_known": len(known), "effects": {}}
        for name, (x, y) in {"Question_vs_Q": ("QA", "QA_short"), "Question_vs_Query": ("QA", "novel"),
                             "QA_level": ("QA", None), "QA_short_level": ("QA_short", None)}.items():
            def v(n):
                d = D[n]["cells"]
                return float(np.mean(np.array(d[x])[sel] - (np.array(d[y])[sel] if y else 0)))
            a, b = np.array([v(n) for n in A]), np.array([v(n) for n in B])
            se = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2) * np.sqrt(2 / 3)
            row["effects"][name] = {"with": float(a.mean()), "without": float(b.mean()), "delta": float(a.mean() - b.mean()),
                                    "se": float(se), "sig": bool(abs(a.mean() - b.mean()) > 2 * se)}
        out[g] = row
    OUT.mkdir(exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=["dd", "hf"])
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--name")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    check() if a.check else analyze() if a.analyze else compute(a.family, a.repo, a.rev, a.name)
