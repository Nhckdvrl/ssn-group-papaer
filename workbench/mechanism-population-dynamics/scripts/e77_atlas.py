"""E77: item-level context/memory arbitration atlas across training. Protocol: experiments/E77-*.md.

Usage:
  e77_atlas.py --build                      # build results/e77/items.json (once)
  e77_atlas.py --check                      # print item / prompt sanity checks
  e77_atlas.py --family dd --repo allenai/DataDecide-dolma1_7-1B --rev step69369-seed-default
  e77_atlas.py --family pythia --repo EleutherAI/pythia-410m --rev 143000
  e77_atlas.py --family hf --repo allenai/OLMo-2-0425-1B --rev stage1-step1907359-tokens4001B
Writes results/e77/runs/<tag>.npz (per-item log-probs; stays local) and <tag>.json (summary).
"""
import argparse
import json
import time

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e77"
RUNS = OUT / "runs"
ITEMS = OUT / "items.json"
PER_REL = 250
STEM = {"occupation": "{s}'s occupation is", "place of birth": "{s} was born in", "genre": "The genre of {s} is",
        "father": "The father of {s} is", "country": "{s} is located in the country of", "producer": "The producer of {s} is",
        "director": "The director of {s} is", "capital of": "{s} is the capital of", "screenwriter": "The screenwriter of {s} is",
        "composer": "The composer of {s} is", "color": "The color of {s} is", "religion": "The religion of {s} is",
        "sport": "{s} plays the sport of", "author": "The author of {s} is", "mother": "The mother of {s} is",
        "capital": "The capital of {s} is"}
SYL = ["vor", "tal", "quen", "mir", "dros", "bel", "kar", "sen", "lo", "vash", "tir", "mon", "zel", "rha", "dun",
       "fen", "gal", "ors", "pim", "wex", "nel", "cor", "ith", "bran", "sol", "yev", "ulm", "trek", "aun", "hes"]
KEEP = {}  # repo -> revisions to keep after a fresh download (none: every fresh download is one-off)
CELLS = ("clean_decl", "clean_qa", "c1_decl", "c1_qa", "c1_Q", "c3_decl", "c3_qa", "agree_decl", "agree_qa",
         "nonce_clean", "nonce_c1_decl", "nonce_c1_qa")


def nonce(rng):
    w = lambda n: "".join(rng.choice(SYL, n)).capitalize()  # noqa: E731
    return f"{w(2)} {w(rng.integers(2, 4))}"


def build():
    from datasets import load_dataset
    ds = load_dataset("akariasai/PopQA", split="test")
    rng = np.random.default_rng(77)
    by = {}
    for i, (p, sj, ob, q) in enumerate(zip(ds["prop"], ds["subj"], ds["obj"], ds["question"])):
        if sj and ob and q and sj in q:
            by.setdefault(p, []).append(i)
    out = []
    for p in sorted(by):
        ix = sorted(rng.choice(by[p], min(PER_REL, len(by[p])), replace=False).tolist())
        rows = [ds[int(i)] for i in ix]
        for k, r in enumerate(rows):
            poss = set(json.loads(r["possible_answers"])) | {r["obj"]}
            dist = None
            for step in range(1, len(rows)):
                o = rows[(k + step) % len(rows)]["obj"]
                if o not in poss and o not in r["subj"] and r["obj"] not in o and o not in r["obj"]:
                    dist = o
                    break
            if dist is None:
                continue
            s, o, q = r["subj"], r["obj"], r["question"]
            if o in s or dist in s or s in o or s in dist:  # answer readable off the subject string
                continue
            ns = nonce(rng)
            st, nst, nq = STEM[p].format(s=s), STEM[p].format(s=ns), q.replace(s, ns)
            S, A, N = f"{st} {dist}.", f"{st} {o}.", f"{nst} {dist}."
            qa = lambda ctx, qq, stem: f"{ctx}Question: {qq} Answer: {stem}"  # noqa: E731
            out.append({"prop": p, "subj": s, "ans": o, "dist": dist, "s_pop": r["s_pop"], "o_pop": r["o_pop"],
                        "nonce": ns, "prompts": {
                            "clean_decl": st, "clean_qa": qa("", q, st),
                            "c1_decl": f"{S} {st}", "c1_qa": qa(S + " ", q, st), "c1_Q": f"{S} Q: {q} A: {st}",
                            "c3_decl": f"{S} {S} {S} {st}", "c3_qa": qa(f"{S} {S} {S} ", q, st),
                            "agree_decl": f"{A} {st}", "agree_qa": qa(A + " ", q, st),
                            "nonce_clean": nst, "nonce_c1_decl": f"{N} {nst}", "nonce_c1_qa": qa(N + " ", nq, nst)}})
    OUT.mkdir(parents=True, exist_ok=True)
    ITEMS.write_text(json.dumps(out, indent=0))
    print("items", len(out))


def items():
    return json.loads(ITEMS.read_text())


def check():
    import collections
    I = items()
    print("items", len(I), dict(collections.Counter(x["prop"] for x in I)))
    bad = [x for x in I if x["prompts"]["c1_decl"].count(x["dist"]) != 1 or x["prompts"]["agree_decl"].count(x["ans"]) != 1
           or x["subj"] in x["prompts"]["nonce_c1_qa"]]
    print("bad", len(bad))
    for x in I[:1] + I[-1:]:
        for c in CELLS:
            print(f"  {c:14s} {x['prompts'][c]!r}")
        print("  cands:", x["ans"], "|", x["dist"])


def load(family, repo, rev):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if family == "dd":
        import dd_common as dd
        model, tok = dd.load(repo, rev, dtype=torch.bfloat16)
        return model, tok, tok.eos_token_id, tok.pad_token_id
    if family == "pythia":
        model = mc.load_hf_model(repo, int(rev), dtype=torch.bfloat16, check_manifest=False).cuda()
        tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE))
        return model, tok, tok.eos_token_id, tok.eos_token_id
    tok = AutoTokenizer.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE),
                                                 torch_dtype=torch.bfloat16).cuda().eval()
    start = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    return model, tok, start, pad


def score(model, tok, start, pad, prompts, cands, max_tokens=12000):
    """Sum log-prob of ' '+cand after prompt; length-sorted dynamic batches."""
    import torch
    pi = [tok(p, add_special_tokens=False)["input_ids"] for p in prompts]
    ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in cands]
    seqs = [[start] + a + b for a, b in zip(pi, ci)]
    order = np.argsort([len(s) for s in seqs])[::-1]
    out = np.zeros(len(seqs))
    i = 0
    while i < len(order):
        L = len(seqs[order[i]])
        bs = max(1, max_tokens // L)
        idx = order[i:i + bs]
        ids = torch.full((len(idx), L), pad)
        att = torch.zeros((len(idx), L), dtype=torch.long)
        for j, k in enumerate(idx):
            ids[j, :len(seqs[k])] = torch.tensor(seqs[k])
            att[j, :len(seqs[k])] = 1
        logits = model(ids.cuda(), attention_mask=att.cuda()).logits
        for j, k in enumerate(idx):
            st, n = 1 + len(pi[k]), len(ci[k])
            lp = logits[j, st - 1:st - 1 + n].float().log_softmax(-1)
            out[k] = float(lp[torch.arange(n), torch.tensor(ci[k], device=lp.device)].sum())
        i += bs
    return out


def hf_rev(family, rev):
    return f"step{rev}" if family == "pythia" else rev


def weight_blob_mtime(repo, revision):
    """Oldest mtime of the weight blobs behind repo@revision (None if not fully present)."""
    import os
    d = mc.HF_CACHE / f"models--{repo.replace('/', '--')}"
    ref = d / "refs" / revision
    if not ref.exists():
        return None
    snap = d / "snapshots" / ref.read_text().strip()
    ws = [f for f in snap.glob("*") if f.suffix in (".safetensors", ".bin")]
    if not ws or not all(f.exists() for f in ws):
        return None
    return min(os.stat(os.path.realpath(f)).st_mtime for f in ws)


def is_cached(repo, revision):
    return weight_blob_mtime(repo, revision) is not None


def drop_revision(repo, revision):
    """Delete a checkpoint we downloaded only for this measurement (user rule: don't keep one-off downloads).
    Repo-local: remove the snapshot, its ref, and blobs no other snapshot of the repo points to."""
    import os
    import shutil
    d = mc.HF_CACHE / f"models--{repo.replace('/', '--')}"
    ref = d / "refs" / revision
    commit = ref.read_text().strip()
    snap = d / "snapshots" / commit
    mine = {os.path.realpath(f) for f in snap.rglob("*") if f.is_symlink()}
    others = set()
    for s in (d / "snapshots").iterdir():
        if s.name != commit:
            others |= {os.path.realpath(f) for f in s.rglob("*") if f.is_symlink()}
    still = {r.read_text().strip() for r in (d / "refs").iterdir() if r.name != revision}
    freed = 0
    for b in mine - others:
        if os.path.exists(b):
            freed += os.path.getsize(b)
            os.remove(b)
    if commit not in still:
        shutil.rmtree(snap, ignore_errors=True)
    ref.unlink()
    print(f"dropping {repo}@{revision}: freed {freed / 1e9:.1f} GB", flush=True)


def tag(family, repo, rev):
    return f"{family}__{repo.split('/')[-1]}__{rev}"


def compute(family, repo, rev):
    import torch
    torch.set_grad_enabled(False)
    t0 = time.time()
    was_cached = is_cached(repo, hf_rev(family, rev))
    model, tok, start, pad = load(family, repo, rev)
    t1 = time.time()
    I = items()
    P, C = [], []
    for x in I:
        for c in CELLS:
            P += [x["prompts"][c]] * 2
            C += [x["ans"], x["dist"]]
    lp = score(model, tok, start, pad, P, C).reshape(len(I), len(CELLS), 2)
    RUNS.mkdir(parents=True, exist_ok=True)
    t = tag(family, repo, rev)
    np.savez_compressed(RUNS / f"{t}.npz", lp=lp.astype(np.float32))
    m = lp[..., 0] - lp[..., 1]  # lp(ans) - lp(dist)
    ci = {c: k for k, c in enumerate(CELLS)}
    conf = m[:, ci["clean_decl"]]
    adopt = -m[:, ci["c1_decl"]]
    cap = -(m[:, ci["nonce_c1_decl"]] - m[:, ci["nonce_clean"]])
    summ = {"family": family, "repo": repo, "rev": rev, "n": len(I), "load_s": t1 - t0, "score_s": time.time() - t1,
            "known_frac": float((conf > 0).mean()), "mean_conf": float(conf.mean()),
            "mean_adopt_c1_decl": float(adopt.mean()), "mean_adopt_c1_qa": float(-m[:, ci["c1_qa"]].mean()),
            "mean_capacity": float(cap.mean()),
            "spearman_adopt_conf": float(__import__("scipy.stats").stats.spearmanr(adopt, conf)[0])}
    summ["was_cached"] = was_cached
    mt = weight_blob_mtime(repo, hf_rev(family, rev))
    fresh = (not was_cached) or (mt is not None and mt >= t0 - 60)  # blob written during this job = one-off download
    summ["fresh_download"] = bool(fresh)
    (RUNS / f"{t}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ), flush=True)
    if fresh and hf_rev(family, rev) not in KEEP.get(repo, ()):
        del model
        drop_revision(repo, hf_rev(family, rev))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--family")
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    a = ap.parse_args()
    build() if a.build else check() if a.check else compute(a.family, a.repo, a.rev)
