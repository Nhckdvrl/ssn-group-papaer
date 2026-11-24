#!/usr/bin/env python3
"""E227: positional / lexical / reflexive retrieval of bound entities across memory architectures
(card: experiments/E227-*.md; design after Gur-Arieh, Geva, Geiger, ICLR 2026, arXiv 2510.06182 §3.2).

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
    ap.add_argument("--pairs", type=int, default=120); ap.add_argument("--seed", type=int, default=227)
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
    enc = lambda s: bos + tok(s, add_special_tokens=False)["input_ids"]
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
        best = min(range(L), key=lambda li: (by_layer[li]["original"], li))
        brng = random.Random(1)
        col = [r[best] for r in recs]
        ci = {}
        for c in cats:
            bs = sorted(sum(brng.choice(col) == c for _ in col) / len(col) for _ in range(2000))
            ci[c] = [bs[49], bs[1949]]
        results[d] = dict(gate_acc=sum(gate) / len(gate), best_layer=best, at_best=by_layer[best], ci_at_best=ci,
                          by_layer=by_layer, n=len(recs))
        print(f"{d}: gate={results[d]['gate_acc']:.3f} best_layer={best}/{L} " +
              " ".join(f"{c}={by_layer[best][c]:.2f}[{ci[c][0]:.2f},{ci[c][1]:.2f}]" for c in cats), flush=True)
        for li in range(0, L, max(1, L // 16)):
            print(f"   L{li:02d} " + " ".join(f"{c[:3]}={by_layer[li][c]:.2f}" for c in cats), flush=True)
    for h in handles:
        h.remove()
    json.dump(dict(meta=dict(model=a.model, layers=L, layer_module=lname, pairs=a.pairs, seed=a.seed, n_groups=N_GROUPS,
                             total_s=time.time() - t0), results=results), open(a.out, "w"), indent=1)
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
