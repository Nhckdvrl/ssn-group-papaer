"""E80: measurement audit for E77 (first-token vs full answer, 3 nonce subjects, ParaConflict). Protocol: experiments/E80-*.md.

Usage:
  e80_audit.py --build       # results/e80/items.json
  e80_audit.py --check
  e80_audit.py --family dd --repo allenai/DataDecide-dolma1_7-1B --rev step69369-seed-default
Writes results/e80/runs/<tag>.npz: lp[item, cell, cand(ans,dist), (full, first)] (local) and <tag>.json (summary).
"""
import argparse
import json
import time

import numpy as np

import mp_common as mc
import e77_atlas as e77

OUT = mc.RESULTS / "e80"
RUNS = OUT / "runs"
ITEMS = OUT / "items.json"
NV = ("A", "B", "C")
CELLS = ("clean_decl", "clean_qa", "c1_decl", "c1_qa") + tuple(
    f"n{v}_{c}" for v in NV for c in ("clean", "c1_decl", "c1_qa")) + ("nA_clean_qa",)


def cells(S, q, stem, subj, nonces):
    qa = lambda ctx, qq, st: f"{ctx}Question: {qq} Answer: {st}"  # noqa: E731
    out = {"clean_decl": stem, "clean_qa": qa("", q, stem), "c1_decl": f"{S} {stem}", "c1_qa": qa(S + " ", q, stem)}
    for v, ns in zip(NV, nonces):
        nS, nq, nst = S.replace(subj, ns), q.replace(subj, ns), stem.replace(subj, ns)
        out[f"n{v}_clean"] = nst
        out[f"n{v}_c1_decl"] = f"{nS} {nst}"
        out[f"n{v}_c1_qa"] = qa(nS + " ", nq, nst)
        if v == "A":
            out["nA_clean_qa"] = qa("", nq, nst)
    return out


def build():
    rngs = [np.random.default_rng(800 + i) for i in range(3)]
    items = []
    for x in json.loads(e77.ITEMS.read_text()):  # PopQA, identical to E77
        p = x["prompts"]
        stem = p["clean_decl"]
        q = p["clean_qa"][len("Question: "):p["clean_qa"].index(" Answer: ")]
        S = f"{stem} {x['dist']}."
        ns = [e77.nonce(r) for r in rngs]
        items.append({"ds": "popqa", "rel": x["prop"], "subj": x["subj"], "ans": x["ans"], "dist": x["dist"],
                      "nonces": ns, "prompts": cells(S, q, stem, x["subj"], ns)})
    import e18_trait as e18
    import e26_factorial as e26  # noqa: F401  (ParaConflict split used in E26)
    for r in e18.rows():
        coh = r["Coherent Conflict"]
        i = coh.rfind(" Question:")
        tail = coh[i + len(" Question:"):]
        if " Answer:" not in tail:
            continue
        q, stem = (t.strip() for t in tail.split(" Answer:", 1))
        sub = r["Substitution Conflict"]
        S = sub[:sub.find(r["dist"]) + len(r["dist"])].strip()
        S = S if S.endswith(".") else S + "."
        s = r["subj"]
        if not s or s not in S or s not in q or s not in stem or r["ans"] in s or r["dist"] in s:
            continue
        ns = [e77.nonce(rr) for rr in rngs]
        items.append({"ds": "paraconflict", "rel": r["cat"], "subj": s, "ans": r["ans"], "dist": r["dist"],
                      "nonces": ns, "prompts": cells(S, q, stem, s, ns)})
    OUT.mkdir(parents=True, exist_ok=True)
    ITEMS.write_text(json.dumps(items))
    import collections
    print("items", len(items), collections.Counter(x["ds"] for x in items))


def items():
    return json.loads(ITEMS.read_text())


def check():
    I = items()
    bad = [x for x in I if any(x["subj"] in x["prompts"][c] for c in CELLS if c.startswith("n"))
           or x["prompts"]["c1_decl"].count(x["dist"]) < 1]
    print("items", len(I), "bad", len(bad))
    for x in (I[0], I[-1]):
        for c in CELLS:
            print(f"  {c:12s} {x['prompts'][c]!r}")
        print("  cands:", x["ans"], "|", x["dist"])


def score2(model, tok, start, pad, prompts, cands, max_tokens=12000):
    """(sum log-prob of ' '+cand, log-prob of its first token) after prompt."""
    import torch
    pi = [tok(p, add_special_tokens=False)["input_ids"] for p in prompts]
    ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in cands]
    seqs = [[start] + a + b for a, b in zip(pi, ci)]
    order = np.argsort([len(s) for s in seqs])[::-1]
    out = np.zeros((len(seqs), 2))
    i = 0
    while i < len(order):
        L = len(seqs[order[i]])
        idx = order[i:i + max(1, max_tokens // L)]
        ids = torch.full((len(idx), L), pad)
        att = torch.zeros((len(idx), L), dtype=torch.long)
        for j, k in enumerate(idx):
            ids[j, :len(seqs[k])] = torch.tensor(seqs[k])
            att[j, :len(seqs[k])] = 1
        logits = model(ids.cuda(), attention_mask=att.cuda()).logits
        for j, k in enumerate(idx):
            st, n = 1 + len(pi[k]), len(ci[k])
            lp = logits[j, st - 1:st - 1 + n].float().log_softmax(-1)
            tok_lp = lp[torch.arange(n), torch.tensor(ci[k], device=lp.device)]
            out[k] = (float(tok_lp.sum()), float(tok_lp[0]))
        i += len(idx)
    return out


def compute(family, repo, rev):
    import torch
    torch.set_grad_enabled(False)
    t0 = time.time()
    was_cached = e77.is_cached(repo, e77.hf_rev(family, rev))
    model, tok, start, pad = e77.load(family, repo, rev)
    t1 = time.time()
    I = items()
    P, C = [], []
    for x in I:
        for c in CELLS:
            P += [x["prompts"][c]] * 2
            C += [x["ans"], x["dist"]]
    lp = score2(model, tok, start, pad, P, C).reshape(len(I), len(CELLS), 2, 2)
    RUNS.mkdir(parents=True, exist_ok=True)
    t = e77.tag(family, repo, rev)
    np.savez_compressed(RUNS / f"{t}.npz", lp=lp.astype(np.float32))
    m = lp[:, :, 0, :] - lp[:, :, 1, :]  # [item, cell, (full, first)]
    ci = {c: k for k, c in enumerate(CELLS)}
    summ = {"family": family, "repo": repo, "rev": rev, "n": len(I), "load_s": t1 - t0, "score_s": time.time() - t1}
    for r, name in ((0, "full"), (1, "first")):
        summ[name] = {"adopt_c1_decl": float(-m[:, ci["c1_decl"], r].mean()),
                      "known_frac": float((m[:, ci["clean_decl"], r] > 0).mean())}
    mt = e77.weight_blob_mtime(repo, e77.hf_rev(family, rev))
    fresh = (not was_cached) or (mt is not None and mt >= t0 - 60)
    summ["fresh_download"] = bool(fresh)
    (RUNS / f"{t}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ), flush=True)
    if fresh:
        del model
        e77.drop_revision(repo, e77.hf_rev(family, rev))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--family")
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    a = ap.parse_args()
    build() if a.build else check() if a.check else compute(a.family, a.repo, a.rev)
