"""E51: shared-account personalization on MovieLens (real users with opposite tastes; person x item interaction).
usage: e51_shared_account.py --model M --out NPZ [--pairs 120]
Users: >= 60 binary ratings (like = rating >= 4, dislike <= 2.5), like rate in [0.35, 0.65]; pairs with >= 20 co-rated
movies and agreement <= 0.4.  Demos: 8 own-only movies per user (4 liked / 4 disliked).  Queries: up to 20 co-rated
movies (true label for each user).  Conditions: single_A, single_B, cross_A (B's demos, ask A), cross_B, mixed,
mixed_far (B answers flag/pass), single_B_far, mixed_instr.  ld = logit(positive word) - logit(negative word)."""
import argparse, copy
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HEAD = "Below are movies from a shared streaming account and whether each viewer liked them.\n\n"
HEAD_INSTR = ("Below are movies from a shared streaming account and whether each viewer liked them. The viewers have different "
              "tastes. When asked about a viewer, predict that specific viewer's opinion, judging only from that viewer's own "
              "examples and ignoring the other viewer's examples.\n\n")
WORDS = {"shared": ("yes", "no"), "far": ("flag", "pass")}


def build(n_pairs, seed=5100, nq=20):
    from datasets import load_dataset
    df = load_dataset("ashraq/movielens_ratings", split="train").select_columns(["user_id", "movie_id", "rating", "title", "genres"]).to_pandas()
    df = df[(df.rating >= 4) | (df.rating <= 2.5)].copy(); df["y"] = (df.rating >= 4).astype(int)
    df["text"] = df.title + " [" + df.genres.str.replace("|", ", ", regex=False) + "]"
    st = df.groupby("user_id").agg(n=("y", "size"), rate=("y", "mean"))
    users = st[(st.n >= 60) & (st.rate.between(0.35, 0.65))].index
    d = df[df.user_id.isin(users)]
    piv = d.pivot_table(index="user_id", columns="movie_id", values="y")
    M = piv.values; mask = ~np.isnan(M); Mz = np.nan_to_num(M)
    co = mask.astype(np.int32) @ mask.T.astype(np.int32)
    agree = Mz @ Mz.T + (mask & (Mz == 0)).astype(np.int32) @ (mask & (Mz == 0)).T.astype(np.int32)
    ui = np.array(piv.index); iu = np.triu_indices(len(ui), 1)
    ok = (co[iu] >= 20) & (agree[iu] / np.maximum(co[iu], 1) <= 0.4)
    cand = list(zip(ui[iu[0][ok]], ui[iu[1][ok]]))
    rng = np.random.default_rng(seed); rng.shuffle(cand)
    by = {u: g for u, g in d.groupby("user_id")}
    pairs = []
    for a, b in cand:
        ga, gb = by[a], by[b]
        common = list(set(ga.movie_id) & set(gb.movie_id))
        oa, ob = ga[~ga.movie_id.isin(common)], gb[~gb.movie_id.isin(common)]
        if min((oa.y == 1).sum(), (oa.y == 0).sum(), (ob.y == 1).sum(), (ob.y == 0).sum()) < 4:
            continue
        import pandas as pd
        pick = lambda g: pd.concat([g[g.y == 1].sample(4, random_state=int(rng.integers(1e9))), g[g.y == 0].sample(4, random_state=int(rng.integers(1e9)))])
        da, db = pick(oa), pick(ob)
        q = list(rng.permutation(common))[:nq]
        qa = ga.set_index("movie_id").loc[q]; qb = gb.set_index("movie_id").loc[q]
        pairs.append({"A": [(t, int(y)) for t, y in zip(da.text, da.y)], "B": [(t, int(y)) for t, y in zip(db.text, db.y)],
                      "q": list(qa.text), "yA": list(qa.y.astype(int)), "yB": list(qb.y.astype(int)),
                      "names": list(rng.permutation(["Alex", "Sam"])), "order": rng.permutation(16).tolist(),
                      "permA": rng.permutation(8).tolist(), "permB": rng.permutation(8).tolist()})
        if len(pairs) >= n_pairs:
            break
    return pairs


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=120)
    a = ap.parse_args()
    pairs = build(a.pairs)
    nq = max(len(p["q"]) for p in pairs)
    print(len(pairs), "pairs; queries/pair", nq, "; A-B disagreement on queries %.2f" % np.mean(
        [np.mean(np.array(p["yA"]) != np.array(p["yB"])) for p in pairs]), flush=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    blk = lambda t, name, w: f"Movie: {t}\nViewer: {name}\nLiked: {w}\n\n"
    conds = ["single_A", "single_B", "cross_A", "cross_B", "mixed", "mixed_far", "single_B_far", "mixed_instr"]
    LD = np.full((len(pairs), len(conds), 2, nq), np.nan, np.float32); Y = np.full((len(pairs), 2, nq), -1, np.int8)
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]; n = len(p["q"])
        Y[pi, 0, :n] = p["yA"]; Y[pi, 1, :n] = p["yB"]
        for ci, c in enumerate(conds):
            vB = "far" if c in ("mixed_far", "single_B_far") else "shared"
            dA = [blk(t, nA, WORDS["shared"][1 - y]) for t, y in (p["A"][j] for j in p["permA"])]
            dB = [blk(t, nB, WORDS[vB][1 - y]) for t, y in (p["B"][j] for j in p["permB"])]
            demos = {"single_A": dA, "cross_B": dA, "single_B": dB, "single_B_far": dB, "cross_A": dB}.get(c)
            if demos is None:
                demos = [(dA + dB)[j] for j in p["order"]]
            who = {"single_A": [0], "cross_A": [0], "single_B": [1], "single_B_far": [1], "cross_B": [1]}.get(c, [0, 1])
            prefix = enc((HEAD_INSTR if c == "mixed_instr" else HEAD) + "".join(demos))
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
            for wi in who:
                name = nA if wi == 0 else nB; words = WORDS["shared"] if wi == 0 else WORDS[vB]
                pos_id, neg_id = enc(" " + words[0])[0], enc(" " + words[1])[0]
                qids = [enc(f"Movie: {t}\nViewer: {name}\nLiked:") for t in p["q"]]
                ql = [len(q) for q in qids]; QL = max(ql)
                cache = copy.deepcopy(out.past_key_values); cache.batch_repeat_interleave(len(qids))
                I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(prefix) + QL), dtype=torch.long)
                M[:, :len(prefix)] = 1
                for qi, q in enumerate(qids):
                    I[qi, :len(q)] = torch.tensor(q); M[qi, len(prefix):len(prefix) + len(q)] = 1
                P = torch.arange(len(prefix), len(prefix) + QL)[None].repeat(len(qids), 1)
                lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=P.cuda(), past_key_values=cache, use_cache=True).logits.float()
                for qi in range(len(qids)):
                    l = lo[qi, ql[qi] - 1]; LD[pi, ci, wi, qi] = float(l[pos_id] - l[neg_id])
                del cache
            del out
        if pi % 10 == 0:
            print(pi, flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, ld=LD, y=Y, conds=np.array(conds))
    print("done")


if __name__ == "__main__":
    main()
