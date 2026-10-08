"""E46: perspectivist ICL bridge on Measuring Hate Speech.  usage: e46_perspective.py --model M --out NPZ [--pairs 120]
Contexts per pair: single_A, single_B, mixed (shared words), mixed_near (B: offensive/okay), mixed_far (B: flag/pass).
Each context is scored for the query annotator A and/or B over 70 reference comments: ld = logit(toxic pole) -
logit(safe pole) in that annotator's vocabulary."""
import argparse, json
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"
HEAD_INSTR = ("Below are comments and the labels that individual annotators gave them. Annotators differ in how strict they are. "
              "When asked for an annotator's label, predict the label that this specific annotator would give, judging only from "
              "that annotator's own examples and ignoring the other annotator's examples.\n\n")
WORDS = {"shared": ("toxic", "safe"), "near": ("offensive", "okay"), "far": ("flag", "pass")}


def build(n_pairs, seed=4600):
    from datasets import load_dataset
    df = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(
        ["comment_id", "annotator_id", "hatespeech", "text"]).to_pandas()
    df = df[df.hatespeech != 1].copy(); df["y"] = (df.hatespeech == 2).astype(float)
    cnt = df.groupby("comment_id").size()
    ref = cnt[cnt >= 50].index
    others = df.groupby("comment_id").y.agg(["sum", "count"])
    df = df.join(others, on="comment_id")
    df = df[(df["count"] >= 2) & (~df.comment_id.isin(ref))]
    df["resid"] = df.y - (df["sum"] - df.y) / (df["count"] - 1)
    st = df.groupby("annotator_id").agg(n=("y", "size"), resid=("resid", "mean"), rate=("y", "mean"))
    st = st[st.n >= 10]
    A_pool = st[st.resid >= st.resid.quantile(0.9)].index.tolist()
    B_pool = st[st.resid <= st.resid.quantile(0.1)].index.tolist()
    rng = np.random.default_rng(seed)
    allq = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(["comment_id", "text"]).to_pandas()
    qs = allq[allq.comment_id.isin(ref)].drop_duplicates("comment_id")
    qs = [t for t in qs.text if len(t.split()) <= 60]
    short = lambda t: len(t.split()) <= 60
    pairs = []
    for _ in range(n_pairs):
        a, b = int(rng.choice(A_pool)), int(rng.choice(B_pool))
        da = df[(df.annotator_id == a) & df.text.map(short)]; db = df[(df.annotator_id == b) & df.text.map(short)]
        if len(da) < 8 or len(db) < 8:
            continue
        da = da.sample(8, random_state=int(rng.integers(1e9))); db = db.sample(8, random_state=int(rng.integers(1e9)))
        pairs.append({"A": [(t, int(y)) for t, y in zip(da.text, da.y)], "B": [(t, int(y)) for t, y in zip(db.text, db.y)],
                      "a_rate": float(da.y.mean()), "b_rate": float(db.y.mean()), "names": list(rng.permutation(["Alex", "Sam"])),
                      "order": rng.permutation(16).tolist()})
    return pairs, qs


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=120)
    a = ap.parse_args()
    pairs, qs = build(a.pairs)
    print(len(pairs), "pairs", len(qs), "queries", "mean demo toxic rate A %.2f B %.2f" % (
        np.mean([p["a_rate"] for p in pairs]), np.mean([p["b_rate"] for p in pairs])), flush=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    for w in WORDS.values():
        for x in w:
            assert len(enc(" " + x)) == 1, x
    blk = lambda t, name, w: f"Comment: {t}\nAnnotator: {name}\nLabel: {w}\n\n"
    conds = ["single_A", "single_B", "mixed", "mixed_near", "mixed_far", "mixed_instr"]
    LD = np.full((len(pairs), len(conds), 2, len(qs)), np.nan, np.float32)    # [pair, cond, query-annotator A/B, q]
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]
        for ci, c in enumerate(conds):
            vB = {"mixed_near": "near", "mixed_far": "far"}.get(c, "shared")
            dA = [blk(t, nA, WORDS["shared"][1 - y]) for t, y in p["A"]]
            dB = [blk(t, nB, WORDS[vB][1 - y]) for t, y in p["B"]]
            demos = dA if c == "single_A" else dB if c == "single_B" else [(dA + dB)[j] for j in p["order"]]
            who = [0] if c == "single_A" else [1] if c == "single_B" else [0, 1]
            prefix = enc((HEAD_INSTR if c == "mixed_instr" else HEAD) + "".join(demos))
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
            for wi in who:
                name = nA if wi == 0 else nB; words = WORDS["shared"] if wi == 0 else WORDS[vB]
                tox, safe = enc(" " + words[0])[0], enc(" " + words[1])[0]
                qids = [enc(f"Comment: {t}\nAnnotator: {name}\nLabel:") for t in qs]
                ql = [len(q) for q in qids]; QL = max(ql)
                import copy
                cache = copy.deepcopy(out.past_key_values); cache.batch_repeat_interleave(len(qids))
                I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(prefix) + QL), dtype=torch.long)
                M[:, :len(prefix)] = 1
                for qi, q in enumerate(qids):
                    I[qi, :len(q)] = torch.tensor(q); M[qi, len(prefix):len(prefix) + len(q)] = 1
                P = torch.arange(len(prefix), len(prefix) + QL)[None].repeat(len(qids), 1)
                lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=P.cuda(), past_key_values=cache, use_cache=True).logits.float()
                for qi in range(len(qids)):
                    l = lo[qi, ql[qi] - 1]; LD[pi, ci, wi, qi] = float(l[tox] - l[safe])
                del cache
            del out
        if pi % 10 == 0:
            print(pi, flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, ld=LD, a_rate=np.array([p["a_rate"] for p in pairs]), b_rate=np.array([p["b_rate"] for p in pairs]),
                        conds=np.array(conds))
    print("done")


if __name__ == "__main__":
    main()
