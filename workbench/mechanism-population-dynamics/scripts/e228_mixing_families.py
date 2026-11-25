#!/usr/bin/env python3
"""E228: Gur-Arieh et al. binding-retrieval conclusions across independently trained families
(card: experiments/E228-*.md; same pairs/intervention as E227, read at the paper's layer rule; design after Gur-Arieh, Geva, Geiger, ICLR 2026, arXiv 2510.06182 §3.2).

Step 0 (--make-vocab tok1 tok2 ...): keep names/objects that are a single token (with leading space) in every tokenizer.
Step 1: for each model, build original/counterfactual pairs (n=6 groups, directions A "What does P love?" and
B "Who loves O?"), patch the last-token residual stream of every layer (one batched forward: row r is patched at
layer r) and classify the output as positional / lexical / reflexive / original / other.

usage: python e227_mixing_mechs.py --make-vocab <tok_dir> [<tok_dir> ...] --vocab vocab.json
       python e227_mixing_mechs.py <model_dir> <out_json> --vocab vocab.json [--pairs 120] [--trust-remote-code]
"""
import argparse, json, random, sys, time

NAMES = ["Ann", "Joe", "Tim", "Sam", "Max", "Ben", "Tom", "Dan", "Kim", "Amy", "Eve", "Jack", "Paul", "Mark", "Lisa",
         "Mary", "John", "Bob", "Ted", "Ray", "Roy", "Jim", "Tony", "Alex", "Emma", "Kate", "Luke", "Adam", "Carl", "Rose"]
OBJECTS = ["tea", "pie", "jam", "ale", "egg", "rice", "cake", "milk", "soup", "bread", "fish", "salt", "wine", "corn",
           "beer", "nuts", "pear", "lime", "honey", "cheese", "coffee", "apple", "candy", "pizza", "pasta", "beans",
           "juice", "sugar", "lemon", "melon"]
SHOT = {"A": "Zoe loves kiwi, Omar loves figs, and Nina loves oats. What does Omar love? Answer: figs\n\n",
        "B": "Zoe loves kiwi, Omar loves figs, and Nina loves oats. Who loves oats? Answer: Nina\n\n"}
N_GROUPS = 6


def make_vocab(tok_dirs, out):
    from transformers import AutoTokenizer
    toks = [AutoTokenizer.from_pretrained(d, trust_remote_code=True) for d in tok_dirs]
    ok = lambda w: all(len(t(" " + w, add_special_tokens=False)["input_ids"]) == 1 for t in toks)
    v = dict(names=[w for w in NAMES if ok(w)], objects=[w for w in OBJECTS if ok(w)])
    json.dump(v, open(out, "w"), indent=1)
    print(f"names {len(v['names'])}: {v['names']}\nobjects {len(v['objects'])}: {v['objects']}")


def context(G):
    parts = [f"{p} loves {o}" for p, o in G]
    return ", ".join(parts[:-1]) + ", and " + parts[-1] + "."


def make_pairs(vocab, direction, n_pairs, rng):
    pairs = []
    for _ in range(n_pairs):
        P = rng.sample(vocab["names"], N_GROUPS)
        O = rng.sample(vocab["objects"], N_GROUPS)
        G = list(zip(P, O))
        q, iP, iL, iR = rng.sample(range(N_GROUPS), 4)
        # counterfactual matrix: group iP holds (query entity from original group iL, answer from original group iR)
        if direction == "A":  # query person, answer object
            cf_q, cf_a = P[iL], O[iR]
            rest_p = [p for p in P if p != cf_q]; rest_o = [o for o in O if o != cf_a]
        else:                 # query object, answer person
            cf_q, cf_a = O[iL], P[iR]
            rest_p = [p for p in P if p != cf_a]; rest_o = [o for o in O if o != cf_q]
        rng.shuffle(rest_p); rng.shuffle(rest_o)
        Gc = []
        for g in range(N_GROUPS):
            if g == iP:
                Gc.append((cf_q, cf_a) if direction == "A" else (cf_a, cf_q))
            else:
                Gc.append((rest_p.pop(), rest_o.pop()))
        if direction == "A":
            orig_q, orig_a = P[q], O[q]
            ask = lambda x: f" What does {x} love? Answer:"
            pred = dict(original=O[q], positional=O[iP], lexical=O[iL], reflexive=O[iR])
            cands = O
        else:
            orig_q, orig_a = O[q], P[q]
            ask = lambda x: f" Who loves {x}? Answer:"
            pred = dict(original=P[q], positional=P[iP], lexical=P[iL], reflexive=P[iR])
            cands = P
        pairs.append(dict(orig=SHOT[direction] + context(G) + ask(orig_q), cf=SHOT[direction] + context(Gc) + ask(cf_q),
                          pred=pred, cands=list(cands), idx=dict(q=q, iP=iP, iL=iL, iR=iR)))
    return pairs


def find_layers(model):
    import torch.nn as nn
    n = getattr(model.config, "num_hidden_layers", None) or getattr(model.config, "n_layer", None)
    best = None
    for name, mod in model.named_modules():
        if isinstance(mod, nn.ModuleList) and len(mod) == n:
            if best is None or any(k in name for k in ("layers", "blocks")):
                best = (name, mod)
                if any(k in name for k in ("layers", "blocks")):
                    break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", nargs="?"); ap.add_argument("out", nargs="?")
    ap.add_argument("--make-vocab", nargs="+"); ap.add_argument("--vocab", required=True)
    ap.add_argument("--pairs", type=int, default=120); ap.add_argument("--seed", type=int, default=228)
    ap.add_argument("--trust-remote-code", action="store_true"); ap.add_argument("--dump", action="store_true")
    a = ap.parse_args()
    if a.make_vocab:
        return make_vocab(a.make_vocab, a.vocab)
    vocab = json.load(open(a.vocab))
    rng = random.Random(a.seed)
    data = {d: make_pairs(vocab, d, a.pairs, rng) for d in ("A", "B")}
    if a.dump:
        for d, ps in data.items():
            print(f"--- {d} pred={ps[0]['pred']} idx={ps[0]['idx']}\nORIG: {ps[0]['orig']}\nCF:   {ps[0]['cf']}")
        return

    import torch
    try:
        import fla  # noqa: F401
    except Exception:
        pass
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=a.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                 trust_remote_code=a.trust_remote_code).cuda().eval()
    lname, layers = find_layers(model)
    L = len(layers)
    print(f"layers: {lname} x {L}", flush=True)
    bos = [tok.bos_token_id] if getattr(tok, "bos_token_id", None) is not None else []
    # 11-25 fix: follow each tokenizer's own special-token default (forcing a BOS broke Granite: 0.22 -> 0.99)
    enc = lambda s: tok(s)["input_ids"]
    first = lambda w: tok(" " + w, add_special_tokens=False)["input_ids"][0]

    state = dict(mode=None, cap=[None] * L, patch=None)

    def make_hook(li):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if state["mode"] == "capture":
                state["cap"][li] = h[0, -1, :].detach().clone()
            elif state["mode"] == "patch":
                h[li, -1, :] = state["patch"][li]
            return out
        return hook
    handles = [layers[i].register_forward_hook(make_hook(i)) for i in range(L)]

    @torch.no_grad()
    def run(ids, batch=1):
        x = torch.tensor([ids] * batch, device="cuda")
        out = model(input_ids=x, use_cache=False)
        return out.logits[:, -1].float()

    results = {}
    for d, pairs in data.items():
        recs, gate = [], []
        for pr in pairs:
            cid = [first(c) for c in pr["cands"]]
            state["mode"] = None
            lo = run(enc(pr["orig"]))[0]
            base = pr["cands"][int(torch.argmax(lo[cid]))]
            gate.append(base == pr["pred"]["original"])
            state["mode"] = "capture"; run(enc(pr["cf"]))
            state["patch"] = torch.stack(state["cap"]); state["mode"] = "patch"
            lp = run(enc(pr["orig"]), batch=L)
            state["mode"] = None
            outs = [pr["cands"][int(torch.argmax(lp[r][cid]))] for r in range(L)]
            inv = {v: k for k, v in pr["pred"].items()}
            recs.append([inv.get(o, "other") for o in outs])
        cats = ["original", "positional", "lexical", "reflexive", "other"]
        by_layer = [{c: sum(r[li] == c for r in recs) / len(recs) for c in cats} for li in range(L)]
        window = [li for li in range(L) if by_layer[li]["original"] < 0.5 and by_layer[li]["reflexive"] < 0.5]
        ell = window[-1] if window else None
        idx = [pr["idx"] for pr in pairs]
        res = dict(gate_acc=sum(gate) / len(gate), ell=ell, window=window, by_layer=by_layer, n=len(recs),
                   per_pair=[dict(cat=r, **i) for r, i in zip(recs, idx)])
        if ell is not None:
            col = [r[ell] for r in recs]
            ends = [c for c, i in zip(col, idx) if i["iP"] in (0, N_GROUPS - 1)]
            mids = [c for c, i in zip(col, idx) if i["iP"] not in (0, N_GROUPS - 1)]
            frac = lambda xs, cs: (sum(x in cs for x in xs) / len(xs)) if xs else float("nan")
            brng = random.Random(1)
            def boot_diff(a, b, cs):
                d = sorted(frac([brng.choice(a) for _ in a], cs) - frac([brng.choice(b) for _ in b], cs) for _ in range(2000))
                return [d[49], d[1949]]
            res.update(at_ell={c: frac(col, [c]) for c in cats},
                       ends_positional=frac(ends, ["positional"]), n_ends=len(ends), n_mids=len(mids),
                       mid_minus_end_lexref=frac(mids, ["lexical", "reflexive"]) - frac(ends, ["lexical", "reflexive"]),
                       mid_minus_end_lexref_ci=boot_diff(mids, ends, ["lexical", "reflexive"]),
                       lexical_at_ell=frac(col, ["lexical"]))
        results[d] = res
        msg = f"{d}: gate={res['gate_acc']:.3f} ell={ell} window={window[:1]}..{window[-1:] if window else ''}"
        if ell is not None:
            msg += " " + " ".join(f"{c}={res['at_ell'][c]:.2f}" for c in cats)
            msg += f" | ends_pos={res['ends_positional']:.2f} (n={res['n_ends']}) mid-end lex+ref={res['mid_minus_end_lexref']:+.2f} {[round(x,2) for x in res['mid_minus_end_lexref_ci']]}"
        print(msg, flush=True)
    A, B = results["A"], results["B"]
    gate_ok = A["gate_acc"] >= 0.9 and B["gate_acc"] >= 0.9
    verdict = dict(gate_ok=gate_ok)
    if gate_ok:
        verdict["c1_positional_at_ends"] = (None if A["ell"] is None else A["ends_positional"] >= 0.5)
        verdict["c2_middle_lex_ref"] = (None if A["ell"] is None else (A["mid_minus_end_lexref"] >= 0.10 and A["mid_minus_end_lexref_ci"][0] > 0))
        verdict["c3_no_lexical_in_B"] = (None if B["ell"] is None else B["lexical_at_ell"] <= 0.10)
    print("VERDICT", verdict, flush=True)
    for h in handles:
        h.remove()
    json.dump(dict(meta=dict(model=a.model, layers=L, layer_module=lname, pairs=a.pairs, seed=a.seed, n_groups=N_GROUPS,
                             total_s=time.time() - t0), results=results, verdict=verdict), open(a.out, "w"), indent=1)
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
