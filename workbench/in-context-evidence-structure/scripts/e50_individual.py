"""E50 (from e49): predict each rater's OWN held-out labels (log-loss / accuracy), not just A-vs-B separation.
E49 doc: -- GoEmotions raw raters, judgment neutral vs emotional.
A = raters who mark many comments neutral, B = raters who rarely do.
Original E46 doc:  usage: e46_perspective.py --model M --out NPZ [--pairs 120]
Contexts per pair: single_A, single_B, mixed (shared words), mixed_near (B: offensive/okay), mixed_far (B: flag/pass).
Each context is scored for the query annotator A and/or B over 70 reference comments: ld = logit(toxic pole) -
logit(safe pole) in that annotator's vocabulary."""
import argparse, json
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
HEAD = "Below are Reddit comments and whether individual annotators judged them emotionally neutral.\n\n"
HEAD_INSTR = ("Below are comments and the labels that individual annotators gave them. Annotators differ in how often they judge comments neutral. "
              "When asked for an annotator's label, predict the label that this specific annotator would give, judging only from "
              "that annotator's own examples and ignoring the other annotator's examples.\n\n")
WORDS = {"shared": ("neutral", "emotional"), "near": ("calm", "charged"), "far": ("flag", "pass")}


def build(n_pairs, seed=5000, n_hold=40):
    from datasets import load_dataset
    df = load_dataset("google-research-datasets/go_emotions", "raw", split="train").to_pandas()
    df = df[(df.example_very_unclear == False) & (df.text.map(lambda t: 5 <= len(t.split()) <= 40))]
    rate = df.groupby("rater_id").neutral.mean(); n = df.groupby("rater_id").size(); rate = rate[n >= 300]
    A_pool = rate[rate >= rate.quantile(0.8)].index.tolist(); B_pool = rate[rate <= rate.quantile(0.2)].index.tolist()
    rng = np.random.default_rng(seed)
    pairs = []
    for _ in range(n_pairs):
        a, b = int(rng.choice(A_pool)), int(rng.choice(B_pool))
        da = df[df.rater_id == a].sample(8 + n_hold, random_state=int(rng.integers(1e9)))
        db = df[df.rater_id == b].sample(8 + n_hold, random_state=int(rng.integers(1e9)))
        pairs.append({"A": [(t, int(y)) for t, y in zip(da.text[:8], da.neutral[:8])], "B": [(t, int(y)) for t, y in zip(db.text[:8], db.neutral[:8])],
                      "holdA": [(t, int(y)) for t, y in zip(da.text[8:], da.neutral[8:])], "holdB": [(t, int(y)) for t, y in zip(db.text[8:], db.neutral[8:])],
                      "a_rate": float(da.neutral.mean()), "b_rate": float(db.neutral.mean()), "names": list(rng.permutation(["Alex", "Sam"])),
                      "order": rng.permutation(16).tolist()})
    return pairs, None


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=120); ap.add_argument("--only", default="")
    a = ap.parse_args()
    pairs, _ = build(a.pairs)
    NQ = len(pairs[0]["holdA"])
    print(len(pairs), "pairs", NQ, "held-out items per annotator", "mean demo toxic rate A %.2f B %.2f" % (
        np.mean([p["a_rate"] for p in pairs]), np.mean([p["b_rate"] for p in pairs])), flush=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    for w in WORDS.values():
        for x in w:
            assert len(enc(" " + x)) == 1, x
    blk = lambda t, name, w: f"Comment: {t}\nAnnotator: {name}\nLabel: {w}\n\n"
    conds = ["single_A", "single_B", "mixed", "mixed_near", "mixed_far", "mixed_instr", "single_B_near", "single_B_far"]
    conds = ["single_A", "single_B", "mixed", "mixed_far", "mixed_instr", "single_A_as_B", "single_B_as_A", "single_B_far"]
    LD = np.full((len(pairs), len(conds), 2, NQ), np.nan, np.float32)
    Y = np.zeros((len(pairs), 2, NQ), np.int8)    # [pair, cond, query-annotator A/B, q]
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]
        for ci, c in enumerate(conds):
            vB = {"mixed_near": "near", "mixed_far": "far", "single_B_near": "near", "single_B_far": "far"}.get(c, "shared")
            dA = [blk(t, nA, WORDS["shared"][1 - y]) for t, y in p["A"]]
            dB = [blk(t, nB, WORDS[vB][1 - y]) for t, y in p["B"]]
            demos = dA if c in ("single_A", "single_A_as_B") else dB if c in ("single_B", "single_B_far", "single_B_as_A") else [(dA + dB)[j] for j in p["order"]]
            who = {"single_A": [0], "single_B": [1], "single_B_far": [1], "single_A_as_B": [1], "single_B_as_A": [0]}.get(c, [0, 1])
            prefix = enc((HEAD_INSTR if c == "mixed_instr" else HEAD) + "".join(demos))
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
            for wi in who:
                name = nA if wi == 0 else nB; words = WORDS["shared"] if wi == 0 else WORDS[vB]
                tox, safe = enc(" " + words[0])[0], enc(" " + words[1])[0]
                hold = p["holdA"] if wi == 0 else p["holdB"]; Y[pi, wi] = [y for _, y in hold]
                qids = [enc(f"Comment: {t}\nAnnotator: {name}\nLabel:") for t, _ in hold]
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
    np.savez_compressed(a.out, ld=LD, y=Y, a_rate=np.array([p["a_rate"] for p in pairs]), b_rate=np.array([p["b_rate"] for p in pairs]),
                        conds=np.array(conds))
    print("done")


if __name__ == "__main__":
    main()
