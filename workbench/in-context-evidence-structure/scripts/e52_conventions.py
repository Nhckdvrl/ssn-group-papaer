"""E52: two real labeling conventions over the same label words (Davidson et al. 2017 tweets).
Convention A (offensive-style, as in OLID): toxic = hate or offensive.  Convention B (hate-style): toxic = hate only.
They disagree exactly on "offensive but not hateful" tweets.  usage: e52_conventions.py --model M --out NPZ [--pairs 120]
Per base: 8 demos per source (A: 3 offensive->toxic, 2 hate->toxic, 3 neither->safe; B: 3 offensive->safe, 2 hate->toxic,
3 neither->safe); 30 held-out queries (10 hate / 10 offensive / 10 neither, clear-majority tweets).  Conditions as E51.
ld = logit(toxic word) - logit(safe word); query labels follow each source's convention."""
import argparse, copy
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HEAD = "Below are tweets and the labels that two content moderators gave them.\n\n"
HEAD_INSTR = ("Below are tweets and the labels that two content moderators gave them. The moderators follow different "
              "labeling policies. When asked for a moderator's label, predict the label that this specific moderator would give, "
              "judging only from that moderator's own examples and ignoring the other moderator's examples.\n\n")
WORDS = {"shared": ("toxic", "safe"), "far": ("flag", "pass")}


def build(n_pairs, seed=5200):
    from datasets import load_dataset
    df = load_dataset("tdavidson/hate_speech_offensive", split="train").to_pandas()
    top = df[["hate_speech_count", "offensive_language_count", "neither_count"]].max(1)
    df = df[(top / df["count"] >= 0.67) & df.tweet.map(lambda t: 4 <= len(t.split()) <= 35)].copy()
    df["tweet"] = df.tweet.str.replace(r"\s+", " ", regex=True).str.strip()
    pool = {c: list(df[df["class"] == c].tweet) for c in (0, 1, 2)}           # 0 hate, 1 offensive, 2 neither
    rng = np.random.default_rng(seed)
    yA = {0: 1, 1: 1, 2: 0}; yB = {0: 1, 1: 0, 2: 0}
    pairs = []
    for _ in range(n_pairs):
        take = lambda c, k: [pool[c][i] for i in rng.choice(len(pool[c]), k, replace=False)]
        hA, oA, nA_ = take(0, 2), take(1, 3), take(2, 3); hB, oB, nB_ = take(0, 2), take(1, 3), take(2, 3)
        used = set(hA + oA + nA_ + hB + oB + nB_)
        q = []
        for c in (0, 1, 2):
            cand = [t for t in take(c, 20) if t not in used][:10]; q += [(t, c) for t in cand]
        A = [(t, yA[c]) for c, ts in ((0, hA), (1, oA), (2, nA_)) for t in ts]
        B = [(t, yB[c]) for c, ts in ((0, hB), (1, oB), (2, nB_)) for t in ts]
        pairs.append({"A": A, "B": B, "q": [t for t, _ in q], "qc": [c for _, c in q], "yA": [yA[c] for _, c in q], "yB": [yB[c] for _, c in q],
                      "names": list(rng.permutation(["Alex", "Sam"])), "order": rng.permutation(16).tolist(),
                      "permA": rng.permutation(8).tolist(), "permB": rng.permutation(8).tolist()})
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
    blk = lambda t, name, w: f"Tweet: {t}\nModerator: {name}\nLabel: {w}\n\n"
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
                qids = [enc(f"Tweet: {t}\nModerator: {name}\nLabel:") for t in p["q"]]
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
    np.savez_compressed(a.out, ld=LD, y=Y, qc=np.array([p["qc"] for p in pairs]), conds=np.array(conds))
    print("done")


if __name__ == "__main__":
    main()
