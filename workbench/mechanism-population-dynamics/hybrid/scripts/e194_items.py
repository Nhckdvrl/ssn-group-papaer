#!/usr/bin/env python3
"""E194 items: artificial splits (set S) and natural multi-token words (set N) on UD EWT contexts.

Writes OUT/items.json (token ids only; no model needed). Seed 194, fixed before any model is run.
Usage: e194_items.py PASSAGES TOKENIZER_DIR OUT_DIR
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from transformers import AutoTokenizer

SEED, CTX, N_S, N_N, PER_TYPE, N_DISTRACT = 194, 100, 600, 600, 2, 31
MS = [2, 3, 4, 5, 6]


def main():
    passages, tokdir, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(tokdir)
    P = json.loads(passages.read_text())
    texts = [p["text"] for p in P["passages"]]
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    single = {}

    def one(piece):
        if piece not in single:
            ids = enc(piece)
            single[piece] = ids[0] if len(ids) == 1 else None
        return single[piece]

    rng = random.Random(SEED)
    S_cand, N_cand = [], []
    for pid, s, end, form, upos, _ in P["words"]:
        t = texts[pid]
        if s < 1 or t[s - 1] != " " or not form.isalpha():
            continue
        pre = enc(t[:s - 1])
        wids = enc(" " + form)
        if enc(t[:end]) != pre + wids or len(pre) < 3:
            continue
        ctx = pre[-CTX:]
        if len(wids) == 1 and len(form) >= 6:
            S_cand.append(dict(pid=pid, s=s, form=form, upos=upos, ctx=ctx, wid=wids[0]))
        elif len(wids) >= 2 and wids[-1] is not None:
            N_cand.append(dict(pid=pid, s=s, form=form, upos=upos, ctx=ctx, pieces=wids, m=len(wids)))

    # ---- set S: random valid split per m (each piece one token; first piece keeps the leading space)
    rng.shuffle(S_cand)
    S, per_type = [], Counter()
    for it in S_cand:
        if per_type[it["form"].lower()] >= PER_TYPE:
            continue
        w, L, splits = it["form"], len(it["form"]), {}
        for m in MS:
            comps = []
            for cuts in itertools.combinations(range(1, L), m - 1):
                b = (0,) + cuts + (L,)
                pieces = [(" " if k == 0 else "") + w[b[k]:b[k + 1]] for k in range(m)]
                ids = [one(p) for p in pieces]
                if all(i is not None for i in ids):
                    comps.append(ids)
            if comps:
                splits[m] = rng.choice(comps)
        if 2 not in splits or 3 not in splits:
            continue
        shuf = {}
        for m, ids in splits.items():
            if m >= 3:
                pre = ids[:-1]
                perms = [list(p) for p in itertools.permutations(pre) if list(p) != pre]
                if len(perms) > 500:
                    perms = rng.sample(perms, 500)
                shuf[m] = rng.choice(perms) + [ids[-1]]
        it.update(splits={str(k): v for k, v in splits.items()}, shuf={str(k): v for k, v in shuf.items()})
        S.append(it)
        per_type[w.lower()] += 1
        if len(S) == N_S:
            break
    wids = [it["wid"] for it in S]
    for i, it in enumerate(S):
        pool = [j for j in range(len(S)) if S[j]["form"].lower() != it["form"].lower()]
        it["distract"] = [wids[j] for j in rng.sample(pool, N_DISTRACT)]

    # ---- set N: natural multi-token words, strata m = 2, 3, 4+; nonword = prefix pieces from other
    # words of the same m at the same positions, last piece kept (so the last token is identical)
    rng.shuffle(N_cand)
    N, per_type, by_stratum = [], Counter(), Counter()
    strat = lambda m: str(m) if m < 4 else "4+"
    for it in N_cand:
        st = strat(it["m"])
        if per_type[it["form"].lower()] >= PER_TYPE or by_stratum[st] >= N_N:
            continue
        it["stratum"] = st
        N.append(it)
        per_type[it["form"].lower()] += 1
        by_stratum[st] += 1
    bym = defaultdict(list)
    for it in N:
        bym[it["m"]].append(it)
    for it in N:
        others = [o for o in bym[it["m"]] if o["form"].lower() != it["form"].lower()]
        if not others:
            it["nonword"] = None
            continue
        it["nonword"] = [rng.choice(others)["pieces"][k] for k in range(it["m"] - 1)] + [it["pieces"][-1]]

    summ = {"n_S": len(S), "S_by_m": {m: sum(str(m) in it["splits"] for it in S) for m in MS},
            "n_N": len(N), "N_by_stratum": dict(by_stratum), "n_S_cand": len(S_cand), "n_N_cand": len(N_cand),
            "seed": SEED, "eos_prefix": tok.eos_token_id}
    (out / "items.json").write_text(json.dumps({"S": S, "N": N, "summary": summ}))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
