"""E56c: is there a GENERAL source-routing direction?  Train one query-only module on a mixture of source-conditional
tasks, test without retraining on unseen datasets / label words.
usage: e56c_multitask.py --model Qwen/Qwen3-8B --out JSON [--rank 8 --steps 900]
Generic context: demos [(text, role, word)], names, queries [(text, role, target_word, other_word)], key ('Comment'...).
Train tasks: (T1) MHS race/gender interaction, toxic/safe; (T2) MHS threshold (A toxic iff IRT score > 0, B iff > 1),
toxic/safe; (T3) SST polarity mapping reversal (A natural, B reversed), positive/negative.
Test (unseen): Davidson two conventions (E52; toxic/safe; accuracy on offensive tweets), MovieLens shared account (E51;
yes/no, real labels), GoEmotions raters (E49; neutral/emotional; A-B separation retention)."""
import argparse, copy, json, sys
from pathlib import Path
import numpy as np, torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
HEAD = "Below are {plural} and the labels that individual annotators gave them.\n\n"


def t1(rng, P):
    import e56_query_adapter as e56
    c = e56.contexts(P["race_gender"], 1, rng, nq=4)[0]
    W = ("toxic", "safe")
    demos = [(t, role, W[1 - y]) for t, role, y in c["demos"]]
    qs = [(t, role, W[1 - e56.correct(role, k)], W[e56.correct(role, k)]) for t, k in c["q"] for role in (0, 1)]
    return {"demos": demos, "names": c["names"], "q": qs, "key": "Comment", "plural": "comments"}


def t2(rng, P):
    texts, scores = P["irt"]
    W = ("toxic", "safe"); thr = (0.0, 1.0)
    idx = rng.choice(len(texts), 24, replace=False)
    demos = [(texts[i], k // 8, W[0 if scores[i] > thr[k // 8] else 1]) for k, i in enumerate(idx[:16])]
    demos = [demos[j] for j in rng.permutation(16)]
    qs = [(texts[i], role, W[0 if scores[i] > thr[role] else 1], W[1 if scores[i] > thr[role] else 0]) for i in idx[16:] for role in (0, 1)]
    return {"demos": demos, "names": list(rng.permutation(["Alex", "Sam"])), "q": qs, "key": "Comment", "plural": "comments"}


def t3(rng, P):
    pos, neg = P["sst"]; W = ("positive", "negative")
    ip, ineg = rng.choice(len(pos), 12, replace=False), rng.choice(len(neg), 12, replace=False)
    lab = lambda role, polar: W[0] if (polar == 1) == (role == 0) else W[1]       # A natural, B reversed
    items = [(pos[i], 1) for i in ip] + [(neg[i], 0) for i in ineg]
    demo_items = items[:8] + items[12:20]; q_items = items[8:12] + items[20:24]
    demos = [(t, k % 2, lab(k % 2, p)) for k, (t, p) in enumerate(demo_items)]
    demos = [demos[j] for j in rng.permutation(16)]
    qs = [(t, role, lab(role, p), W[0] if lab(role, p) == W[1] else W[1]) for t, p in q_items for role in (0, 1)]
    return {"demos": demos, "names": list(rng.permutation(["Alex", "Sam"])), "q": qs, "key": "Review", "plural": "reviews"}


def test_sets(n):
    out = {}
    import e52_conventions as e52
    pairs = e52.build(n)
    W = ("toxic", "safe")
    out["davidson"] = [{"demos": [(t, 0, W[1 - y]) for t, y in p["A"]] + [(t, 1, W[1 - y]) for t, y in p["B"]], "order": p["order"],
                        "names": p["names"], "key": "Tweet", "plural": "tweets",
                        "q": [(t, role, W[1 - (p["yA"] if role == 0 else p["yB"])[i]], W[(p["yA"] if role == 0 else p["yB"])[i]])
                              for i, (t, c) in enumerate(zip(p["q"], p["qc"])) if c == 1 for role in (0, 1)]} for p in pairs]
    import e51_shared_account as e51
    pairs = e51.build(n)
    W = ("yes", "no")
    out["movielens"] = [{"demos": [(t, 0, W[1 - y]) for t, y in p["A"]] + [(t, 1, W[1 - y]) for t, y in p["B"]], "order": p["order"],
                         "names": p["names"], "key": "Movie", "plural": "movies",
                         "q": [(t, role, W[1 - (p["yA"] if role == 0 else p["yB"])[i]], W[(p["yA"] if role == 0 else p["yB"])[i]])
                               for i, t in enumerate(p["q"]) for role in (0, 1)]} for p in pairs]
    import e49_goemotions as e49
    pairs, qs = e49.build(n)
    W = ("neutral", "emotional")
    out["goemotions"] = [{"demos": [(t, 0, W[1 - y]) for t, y in p["A"]] + [(t, 1, W[1 - y]) for t, y in p["B"]], "order": p["order"],
                          "names": p["names"], "key": "Comment", "plural": "comments",
                          "q": [(t, role, W[0], W[1]) for t in qs[:12] for role in (0, 1)]} for p in pairs]   # target = 'neutral' pole (separation only)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--steps", type=int, default=900); ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--n_test", type=int, default=40)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from datasets import load_dataset
    import e56_query_adapter as e56
    from build_marked import sst_pool
    P = {"race_gender": e56.pools()["train"]}
    d = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(["comment_id", "hate_speech_score", "text"]).to_pandas()
    g = d.groupby("comment_id").agg(score=("hate_speech_score", "first"), text=("text", "first"))
    g = g[g.text.map(lambda t: len(t.split()) <= 50) & g.score.between(-2.5, 3.0)]
    P["irt"] = (g.text.values, g.score.values)
    sp = sst_pool(); P["sst"] = (sp[1], sp[0])
    T = test_sets(a.n_test)
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    for p_ in model.parameters():
        p_.requires_grad_(False)
    cfg = model.config; L = cfg.num_hidden_layers; D = cfg.hidden_size; L1 = L // 2 - 2
    QD = model.model.layers[0].self_attn.q_proj.out_features
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    state = {"on": False}
    mods = torch.nn.ModuleDict({str(l): torch.nn.Sequential(torch.nn.Linear(D, a.rank, bias=False), torch.nn.Linear(a.rank, QD, bias=False))
                                for l in range(L1, L)}).cuda().float()
    for m in mods.values():
        torch.nn.init.zeros_(m[1].weight)
    def qhook(l):
        def f(mod, inp, out):
            if not state["on"]:
                return out
            x = inp[0][:, -1].float(); out = out.clone(); out[:, -1] = out[:, -1] + mods[str(l)](x).to(out.dtype)
            return out
        return f
    for l in range(L1, L):
        model.model.layers[l].self_attn.q_proj.register_forward_hook(qhook(l))

    def run(ctx, on, grad=False, only_role=None):
        demos = ctx["demos"] if "order" not in ctx else [ctx["demos"][j] for j in ctx["order"]]
        if only_role is not None:
            demos = [x for x in ctx["demos"] if x[1] == only_role]
        key = ctx["key"]
        prefix = enc(HEAD.format(plural=ctx["plural"]) + "".join(f"{key}: {t}\nAnnotator: {ctx['names'][r]}\nLabel: {w}\n\n" for t, r, w in demos))
        qs = [x for x in ctx["q"] if only_role is None or x[1] == only_role]
        with torch.no_grad():
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
        qids = [enc(f"{key}: {t}\nAnnotator: {ctx['names'][r]}\nLabel:") for t, r, _, _ in qs]
        QL = max(len(x) for x in qids)
        I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(prefix) + QL), dtype=torch.long); Pp = torch.zeros_like(I)
        M[:, :len(prefix)] = 1
        for qi, x in enumerate(qids):
            I[qi, QL - len(x):] = torch.tensor(x); M[qi, len(prefix) + QL - len(x):] = 1; Pp[qi, QL - len(x):] = torch.arange(len(prefix), len(prefix) + len(x))
        cache = copy.deepcopy(out.past_key_values); cache.batch_repeat_interleave(len(qids))
        state["on"] = on
        with torch.set_grad_enabled(grad):
            lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=Pp.cuda(), past_key_values=cache, use_cache=True, logits_to_keep=1).logits[:, -1].float()
        state["on"] = False
        tgt = torch.tensor([enc(" " + t)[0] for _, _, t, _ in qs]).cuda(); oth = torch.tensor([enc(" " + o)[0] for _, _, _, o in qs]).cuda()
        r = torch.arange(len(qs))
        return lo[r, tgt] - lo[r, oth], [x[1] for x in qs]           # margin toward the source-correct word

    rng = np.random.default_rng(7); opt = torch.optim.Adam(mods.parameters(), lr=a.lr); log = {"loss": []}
    for step in range(a.steps):
        ctx = (t1, t2, t3)[step % 3](rng, P)
        m, _ = run(ctx, True, grad=True)
        loss = torch.nn.functional.softplus(-m).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 60 == 0:
            log["loss"].append(round(float(loss), 4)); print(step, round(float(loss), 4), flush=True)
    torch.save([p_.detach().cpu() for p_ in mods.parameters()], a.out.replace(".json", ".pt"))

    @torch.no_grad()
    def evaluate(name, ctxs):
        res = {}
        for cond in ("default", "adapter", "single"):
            acc, sep = [], []
            for ctx in ctxs:
                if cond == "single":
                    m0, r0 = run(ctx, False, only_role=0); m1, r1 = run(ctx, False, only_role=1)
                    m, roles = torch.cat([m0, m1]), r0 + r1
                else:
                    m, roles = run(ctx, cond == "adapter")
                roles = np.array(roles); mm = m.cpu().numpy()
                acc.append(float((mm > 0).mean()))
                sep.append(float(mm[roles == 0].mean() - mm[roles == 1].mean()))      # goemotions: A minus B toward 'neutral' (only meaningful there)
            res[cond] = {"acc": float(np.mean(acc)), "sep": float(np.mean(sep))}
        print(name, res, flush=True)
        return res
    for name, ctxs in T.items():
        log[name] = evaluate(name, ctxs)
    Path(a.out).write_text(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
