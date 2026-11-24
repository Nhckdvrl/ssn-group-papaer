#!/usr/bin/env python3
"""E224: behavioural competence gate for variable binding and overwrite (card: experiments/E224-*.md).

For each model, two formats (code / narrative) x five conditions (S2, S4, O1, O1-other, O3), 150 items each.
Score = summed log-probability of each candidate value's full continuation; candidates = all values seen in
the context. No multiple-choice options are shown to the model.

usage: python e224_gate.py <model_dir> <out_json> [--n 150] [--seed 224] [--trust-remote-code]
"""
import argparse, json, math, random, sys, time

NAMES = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Irene", "Jack", "Kate", "Liam"]
PLACES = ["kitchen", "garden", "garage", "office", "bedroom", "attic", "cellar", "library", "hallway",
          "bathroom", "balcony", "basement"]
LETTERS = list("abcdefghjnrstuvwyz")  # no i, l, o; no shot letters p, q, x, m, k
DIGITS = list("123456789")

SHOTS = {
    "code": "p = 3\nq = 8\nprint(q)\n8\n\nx = 5\nm = 2\nk = 7\nprint(x)\n5\n\n",
    "narr": ("Zoe is in the pantry. Yuri is in the studio. Question: Where is Yuri? Answer: the studio.\n\n"
             "Omar is in the lobby. Nina is in the closet. Paul is in the den. Question: Where is Omar? "
             "Answer: the lobby.\n\n"),
}


def stmt(fmt, var, val, kind="set"):
    if fmt == "code":
        return f"{var} = {val}\n"
    if kind == "set":
        return f"{var} is in the {val}. "
    if kind == "again":
        return f"{var} is still in the {val}. "
    return f"Then {var} went to the {val}. "  # overwrite


def query(fmt, var):
    return f"print({var})\n" if fmt == "code" else f"Question: Where is {var}? Answer: the"


def cand_text(fmt, val):
    return val if fmt == "code" else " " + val


def make_items(fmt, cond, n, rng):
    keys, vals = (LETTERS, DIGITS) if fmt == "code" else (NAMES, PLACES)
    items = []
    for _ in range(n):
        nv = {"S2": 2, "S4": 4}.get(cond, 3)
        ks = rng.sample(keys, nv + 1)
        vs = rng.sample(vals, nv + 3)
        binds = list(zip(ks[:nv], vs[:nv]))
        lines = [stmt(fmt, k, v) for k, v in binds]
        if cond in ("S2", "S4"):
            qk, qv = rng.choice(binds)
            items.append(dict(prompt="".join(lines), qk=qk, answer=qv, old=None, cands=[v for _, v in binds]))
            continue
        ti = rng.randrange(nv)
        tk, tv_old = binds[ti]
        tv_new = vs[nv]
        if cond == "O3":  # old value of target restated twice more, interleaved with the other variables
            others = [stmt(fmt, k, v, "again") for j, (k, v) in enumerate(binds) if j != ti]
            again = stmt(fmt, tk, tv_old, "again")
            lines = lines + [again, others[0], again, others[1]]
        lines.append(stmt(fmt, tk, tv_new, "over"))
        extra_k, extra_v = ks[nv], vs[nv + 1]  # unrelated new binding after the overwrite (no last-line shortcut)
        lines.append(stmt(fmt, extra_k, extra_v))
        cands = [v for _, v in binds] + [tv_new, extra_v]
        if cond == "O1-other":
            ok, ov = rng.choice([b for j, b in enumerate(binds) if j != ti])
            items.append(dict(prompt="".join(lines), qk=ok, answer=ov, old=None, cands=cands))
        else:
            items.append(dict(prompt="".join(lines), qk=tk, answer=tv_new, old=tv_old, cands=cands))
    for it in items:
        it["query"] = query(fmt, it["qk"])
    return items


def build_all(n, seed):
    rng = random.Random(seed)
    data = {}
    for fmt in ("code", "narr"):
        for cond in ("S2", "S4", "O1", "O1-other", "O3"):
            data[(fmt, cond)] = make_items(fmt, cond, n, rng)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("--n", type=int, default=150); ap.add_argument("--seed", type=int, default=224)
    ap.add_argument("--trust-remote-code", action="store_true")
    ap.add_argument("--dump-items", action="store_true", help="print 2 items per cell and exit (no model)")
    a = ap.parse_args()
    data = build_all(a.n, a.seed)
    if a.dump_items:
        for (fmt, cond), items in data.items():
            for it in items[:2]:
                print(f"--- {fmt} {cond} answer={it['answer']} old={it['old']} cands={it['cands']}\n"
                      + SHOTS[fmt] + it["prompt"] + it["query"])
        return

    import torch
    try:
        import fla  # noqa: F401  registers fla-hub model types
    except Exception as e:
        print("fla not importable:", e, file=sys.stderr)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=a.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16,
                                                 trust_remote_code=a.trust_remote_code).cuda().eval()
    load_s = time.time() - t0

    def enc(s):
        return tok(s, add_special_tokens=False)["input_ids"]

    bos = [tok.bos_token_id] if getattr(tok, "bos_token_id", None) is not None else []

    @torch.no_grad()
    def logprobs_next(ids):
        out = model(torch.tensor([ids], device="cuda"))
        return torch.log_softmax(out.logits[0, -1].float(), -1)

    @torch.no_grad()
    def seq_logprob(ids, start):
        out = model(torch.tensor([ids], device="cuda"))
        lp = torch.log_softmax(out.logits[0].float(), -1)
        return sum(lp[i - 1, ids[i]].item() for i in range(start, len(ids)))

    results, n_multi = {}, 0
    for (fmt, cond), items in data.items():
        recs = []
        for it in items:
            prompt = SHOTS[fmt] + it["prompt"] + it["query"]
            p_ids = bos + enc(prompt)
            conts = {}
            for c in it["cands"]:
                full = bos + enc(prompt + cand_text(fmt, c))
                if full[:len(p_ids)] != p_ids:  # boundary merge: fall back to separate encoding
                    full = p_ids + enc(cand_text(fmt, c))
                conts[c] = full[len(p_ids):]
            nxt = logprobs_next(p_ids)
            scores = {}
            for c, ct in conts.items():
                if len(ct) == 1:
                    scores[c] = nxt[ct[0]].item()
                else:
                    n_multi += 1
                    scores[c] = seq_logprob(p_ids + ct, len(p_ids))
            pred = max(scores, key=scores.get)
            recs.append(dict(pred=pred, answer=it["answer"], old=it["old"], correct=pred == it["answer"],
                             is_old=(it["old"] is not None and pred == it["old"]), n_cands=len(it["cands"])))
        acc = [r["correct"] for r in recs]
        rng = random.Random(1)
        boots = sorted(sum(rng.choice(acc) for _ in acc) / len(acc) for _ in range(2000))
        results[f"{fmt}/{cond}"] = dict(
            acc=sum(acc) / len(acc), ci=[boots[49], boots[1949]],
            old_rate=(sum(r["is_old"] for r in recs) / len(recs)) if items[0]["old"] else None,
            chance=1 / recs[0]["n_cands"], n=len(recs), records=recs)
        print(f"{fmt:4s} {cond:8s} acc={results[f'{fmt}/{cond}']['acc']:.3f} "
              f"ci=[{boots[49]:.3f},{boots[1949]:.3f}] old={results[f'{fmt}/{cond}']['old_rate']}", flush=True)
    meta = dict(model=a.model, n=a.n, seed=a.seed, load_s=load_s, total_s=time.time() - t0,
                multi_token_scores=n_multi, torch=torch.__version__)
    json.dump(dict(meta=meta, results=results), open(a.out, "w"), indent=1)
    print("done", json.dumps(meta))


if __name__ == "__main__":
    main()
