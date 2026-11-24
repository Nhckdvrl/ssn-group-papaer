#!/usr/bin/env python3
"""E226: E225 with a calibrated "original" wording per model (card: experiments/E226-*.md).

Step 1 (--calibrate): N0 orig(T) only, 4 wordings x 100 fresh items (seed 9226); picks the best wording (ties -> lowest index).
Step 2: the 7 E225 cells on fresh items (seed 226) with the chosen wording.

Narrative format. Three people in rooms; the target moves N times (N=0 control: a non-moving event);
one unrelated new binding follows. Queries: cur(T) "now", orig(T) "at the beginning", orig(O) for a
non-moved person. Score = summed log-prob of each in-context place's continuation (no options shown).

usage: python e226_keep_replace_calibrated.py <model_dir> <out_json> [--trust-remote-code] [--dump-items]
"""
import argparse, json, random, sys, time

NAMES = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Irene", "Jack", "Kate", "Liam"]
PLACES = ["kitchen", "garden", "garage", "office", "bedroom", "attic", "cellar", "library", "hallway",
          "bathroom", "balcony", "basement"]
WORDINGS = {"W1": "Where was {x} at the beginning?", "W2": "Where was {x} first?",
            "W3": "Where was {x} originally?", "W4": "Where was {x} at the start of the story?"}


def shots(w):
    return ("Zoe is in the pantry. Yuri is in the studio. Question: Where is Yuri now? Answer: the studio.\n\n"
            "Omar is in the lobby. Nina is in the closet. Paul is in the den. Question: "
            + WORDINGS[w].format(x="Omar") + " Answer: the lobby.\n\n")
CELLS = [(0, "orig_T"), (1, "cur_T"), (1, "orig_T"), (1, "orig_O"), (2, "cur_T"), (2, "orig_T"), (2, "orig_O")]


def make_items(N, q, n, rng, w="W1"):
    items = []
    for _ in range(n):
        ks = rng.sample(NAMES, 4)
        vs = rng.sample(PLACES, 6)
        binds = list(zip(ks[:3], vs[:3]))
        ti = rng.randrange(3)
        tk, t_init = binds[ti]
        text = "".join(f"{k} is in the {v}. " for k, v in binds)
        path = [t_init]
        if N == 0:
            text += f"Then {tk} waved. "
        for j in range(N):
            nv = vs[3 + j]
            text += f"Then {tk} went to the {nv}. "
            path.append(nv)
        extra = vs[5]
        text += f"{ks[3]} is in the {extra}. "
        cands = [v for _, v in binds] + path[1:] + [extra]
        if q == "orig_O":
            ok, ov = rng.choice([b for j, b in enumerate(binds) if j != ti])
            query, answer = "Question: " + WORDINGS[w].format(x=ok) + " Answer: the", ov
        elif q == "orig_T":
            query, answer = "Question: " + WORDINGS[w].format(x=tk) + " Answer: the", t_init
        else:
            query, answer = f"Question: Where is {tk} now? Answer: the", path[-1]
        items.append(dict(prompt=text + query, answer=answer, init=t_init, mid=(path[1] if N == 2 else None),
                          new=path[-1], others=[v for j, (_, v) in enumerate(binds) if j != ti], extra=extra,
                          cands=cands))
    return items


def build_all(n, seed, w="W1"):
    rng = random.Random(seed)
    return {f"N{N}/{q}": make_items(N, q, n, rng, w) for N, q in CELLS}


def build_calib(n=100, seed=9226):
    out = {}
    for w in WORDINGS:
        rng = random.Random(seed)  # same contexts for every wording
        out[w] = make_items(0, "orig_T", n, rng, w)
    return out


def err_type(pred, it):
    if pred == it["answer"]:
        return "correct"
    if pred == it["init"]:
        return "init"
    if it["mid"] is not None and pred == it["mid"]:
        return "mid"
    if pred == it["new"]:
        return "new"
    if pred in it["others"]:
        return "other_person"
    return "extra"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("--n", type=int, default=150); ap.add_argument("--seed", type=int, default=226)
    ap.add_argument("--trust-remote-code", action="store_true"); ap.add_argument("--dump-items", action="store_true")
    a = ap.parse_args()
    if a.dump_items:
        for w, items in build_calib().items():
            print(f"--- calib {w}\n{shots(w)}{items[0]['prompt']}")
        for c, items in build_all(a.n, a.seed, "W3").items():
            print(f"--- {c} (W3) answer={items[0]['answer']}\n{items[0]['prompt']}")
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
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    bos = [tok.bos_token_id] if getattr(tok, "bos_token_id", None) is not None else []

    @torch.no_grad()
    def logits(ids):
        return torch.log_softmax(model(torch.tensor([ids], device="cuda")).logits[0].float(), -1)

    def run_cells(data, w):
      results = {}
      for c, items in data.items():
        recs = []
        for it in items:
            prompt = shots(w) + it["prompt"]
            p = bos + enc(prompt)
            lp_last = logits(p)[-1]
            scores = {}
            for cand in it["cands"]:
                full = bos + enc(prompt + " " + cand)
                if full[:len(p)] != p:
                    full = p + enc(" " + cand)
                ct = full[len(p):]
                if len(ct) == 1:
                    scores[cand] = lp_last[ct[0]].item()
                else:
                    lp = logits(full)
                    scores[cand] = sum(lp[i - 1, full[i]].item() for i in range(len(p), len(full)))
            pred = max(scores, key=scores.get)
            recs.append(dict(pred=pred, answer=it["answer"], type=err_type(pred, it)))
        acc = [r["type"] == "correct" for r in recs]
        types = {t: sum(r["type"] == t for r in recs) / len(recs) for t in ("correct", "init", "mid", "new", "other_person", "extra")}
        results[c] = dict(acc=sum(acc) / len(acc), types=types, n=len(recs), records=recs)
        print(f"{c:10s} acc={results[c]['acc']:.3f} " + " ".join(f"{k}={v:.2f}" for k, v in types.items() if k != 'correct' and v > 0), flush=True)
      return results

    calib = {}
    for w, items in build_calib().items():
        r = run_cells({f"calib/{w}": items}, w)[f"calib/{w}"]
        calib[w] = dict(acc=r["acc"], types=r["types"])
    best = max(calib, key=lambda w: (calib[w]["acc"], -int(w[1])))
    print("CALIB", {w: round(v["acc"], 3) for w, v in calib.items()}, "-> chosen", best, flush=True)
    if calib[best]["acc"] < 0.9:
        json.dump(dict(meta=dict(model=a.model, excluded=True), calib=calib, chosen=best), open(a.out, "w"), indent=1)
        print("EXCLUDED (best N0 accuracy < 0.9)"); return
    results = run_cells(build_all(a.n, a.seed, best), best)
    # paired-by-construction contrasts via bootstrap over items (cells are independent samples)
    rng = random.Random(1)
    def boot_diff(a_cell, b_cell):
        A = [r["type"] == "correct" for r in results[a_cell]["records"]]
        B = [r["type"] == "correct" for r in results[b_cell]["records"]]
        d = sorted(sum(rng.choice(A) for _ in A) / len(A) - sum(rng.choice(B) for _ in B) / len(B) for _ in range(2000))
        return dict(diff=sum(A) / len(A) - sum(B) / len(B), ci=[d[49], d[1949]])
    contrasts = {}
    for N in (1, 2):
        contrasts[f"N{N}: orig_T - orig_T(N0)"] = boot_diff(f"N{N}/orig_T", "N0/orig_T")
        contrasts[f"N{N}: orig_T - orig_O"] = boot_diff(f"N{N}/orig_T", f"N{N}/orig_O")
    for k, v in contrasts.items():
        print(f"{k:28s} {v['diff']:+.3f} [{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}]", flush=True)
    json.dump(dict(meta=dict(model=a.model, n=a.n, seed=a.seed, total_s=time.time() - t0, torch=torch.__version__),
                   calib=calib, chosen=best, results=results, contrasts=contrasts), open(a.out, "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
