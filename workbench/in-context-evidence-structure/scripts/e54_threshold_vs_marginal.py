"""E54: does source binding depend on whether the source difference is input-conditional (threshold shift) or
input-independent (label-frequency shift)?  Real Measuring Hate Speech comments with IRT item scores.
usage: e54_threshold_vs_marginal.py --model M --out NPZ [--pairs 120]
Per pair: 8 demo comments per source (same items in both types), 60 query comments.
  thr: A toxic iff score > 0.0; B toxic iff score > 1.0                         (content-dependent difference)
  mar: both use threshold 0.5, then labels flipped at random (independent of content) until A and B have exactly the
       same toxic counts as in 'thr'                                                (content-independent difference)
Conditions per type: single_A, single_B, mixed (16 interleaved; shared words toxic / safe).
ld = logit(toxic) - logit(safe); separation D = mean_q ld(A) - ld(B); retention = D_mixed / D_single."""
import argparse, copy
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"


def build(n_pairs, seed=5400):
    from datasets import load_dataset
    d = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(["comment_id", "hate_speech_score", "text"]).to_pandas()
    g = d.groupby("comment_id").agg(score=("hate_speech_score", "first"), text=("text", "first"))
    g = g[g.text.map(lambda t: len(t.split()) <= 60) & g.score.between(-2.5, 3.0)]
    rng = np.random.default_rng(seed)
    q = g.sample(60, random_state=seed); g = g.drop(q.index)
    texts, scores = g.text.values, g.score.values
    pairs = []
    for _ in range(n_pairs):
        ia, ib = rng.choice(len(g), 8, replace=False), rng.choice(len(g), 8, replace=False)
        sa, sb = scores[ia], scores[ib]
        thrA, thrB = (sa > 0.0).astype(int), (sb > 1.0).astype(int)
        def marginal(s, k):
            y = (s > 0.5).astype(int)
            while y.sum() < k:
                j = rng.choice(np.flatnonzero(y == 0)); y[j] = 1
            while y.sum() > k:
                j = rng.choice(np.flatnonzero(y == 1)); y[j] = 0
            return y
        marA, marB = marginal(sa, thrA.sum()), marginal(sb, thrB.sum())
        pairs.append({"textA": list(texts[ia]), "textB": list(texts[ib]), "sA": sa.tolist(), "sB": sb.tolist(),
                      "thr": (thrA.tolist(), thrB.tolist()), "mar": (marA.tolist(), marB.tolist()),
                      "names": list(rng.permutation(["Alex", "Sam"])), "order": rng.permutation(16).tolist()})
    return pairs, list(q.text), list(q.score)


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=120)
    a = ap.parse_args()
    pairs, qs, qscore = build(a.pairs)
    print(len(pairs), "pairs; mean toxic count A %.2f B %.2f; content-label corr thr %.2f mar %.2f" % (
        np.mean([sum(p["thr"][0]) for p in pairs]), np.mean([sum(p["thr"][1]) for p in pairs]),
        np.corrcoef(np.concatenate([p["sA"] + p["sB"] for p in pairs]), np.concatenate([p["thr"][0] + p["thr"][1] for p in pairs]))[0, 1],
        np.corrcoef(np.concatenate([p["sA"] + p["sB"] for p in pairs]), np.concatenate([p["mar"][0] + p["mar"][1] for p in pairs]))[0, 1]), flush=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    tox, safe = enc(" toxic")[0], enc(" safe")[0]
    blk = lambda t, n, y: f"Comment: {t}\nAnnotator: {n}\nLabel: {'toxic' if y else 'safe'}\n\n"
    conds = [(ty, c) for ty in ("thr", "mar") for c in ("single_A", "single_B", "mixed")]
    LD = np.full((len(pairs), len(conds), 2, len(qs)), np.nan, np.float32)
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]
        for ci, (ty, c) in enumerate(conds):
            yA, yB = p[ty]
            dA = [blk(t, nA, y) for t, y in zip(p["textA"], yA)]; dB = [blk(t, nB, y) for t, y in zip(p["textB"], yB)]
            demos = dA if c == "single_A" else dB if c == "single_B" else [(dA + dB)[j] for j in p["order"]]
            who = [0] if c == "single_A" else [1] if c == "single_B" else [0, 1]
            prefix = enc(HEAD + "".join(demos))
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
            for wi in who:
                name = nA if wi == 0 else nB
                qids = [enc(f"Comment: {t}\nAnnotator: {name}\nLabel:") for t in qs]
                ql = [len(x) for x in qids]; QL = max(ql)
                cache = copy.deepcopy(out.past_key_values); cache.batch_repeat_interleave(len(qids))
                I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(prefix) + QL), dtype=torch.long)
                M[:, :len(prefix)] = 1
                for qi, x in enumerate(qids):
                    I[qi, :len(x)] = torch.tensor(x); M[qi, len(prefix):len(prefix) + len(x)] = 1
                P = torch.arange(len(prefix), len(prefix) + QL)[None].repeat(len(qids), 1)
                lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=P.cuda(), past_key_values=cache, use_cache=True).logits.float()
                for qi in range(len(qids)):
                    l = lo[qi, ql[qi] - 1]; LD[pi, ci, wi, qi] = float(l[tox] - l[safe])
                del cache
            del out
        if pi % 20 == 0:
            print(pi, flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, ld=LD, qscore=np.array(qscore), conds=np.array(["%s|%s" % x for x in conds]))
    print("done")


if __name__ == "__main__":
    main()
