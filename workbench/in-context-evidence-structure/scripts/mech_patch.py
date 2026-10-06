"""E38: causal test -- is the change-point (noise-direction) signal carried by the new-regime label anchors?

For each base and query role of E28 (imbal): run suffix_3 (clean) and noise_2__suffix_3 (noisy); the two prompts are
token-aligned (they differ only in the single-token labels of demos 1 and 5).  Patch, in the noisy run, the residual
stream entering layer l at a set of positions with the clean run's states, for l in a layer sweep:
  anchors : label tokens of demos 13-15 (the final B run)
  inputs  : the last input token of demos 13-15 (control)
  noise_anchors : label tokens of the two noise demos (1, 5) -- when has the answer position read them?
  all     : every position (positive control: must reproduce the clean output exactly)
Output: logit(B answer) - logit(A answer) for clean, noisy, and each patch.
usage: mech_patch.py --model M --out NPZ [--n_bases 150]"""
import argparse, json, re
PRED = False
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--n_bases", type=int, default=150)
    ap.add_argument("--data", default="imbal")
    ap.add_argument("--pred", action="store_true"); a = ap.parse_args()
    global PRED; PRED = a.pred
    root = __file__.rsplit("/", 2)[0]
    rows = [json.loads(l) for l in open(f"{root}/data/{a.data}/rows.jsonl")]
    by = {}
    for r in rows:
        by[r["uid"]] = r
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    L = model.config.num_hidden_layers; layers = list(range(0, L, 2)) + [L - 1]
    store = {}

    def make_hook(l):
        def pre(mod, args, kwargs):
            if ("patch", l) in store:
                h = args[0] if args else kwargs["hidden_states"]
                pos, src = store[("patch", l)]
                h = h.clone(); h[0, pos] = src.to(h.dtype)
                if args:
                    return (h,) + tuple(args[1:]), kwargs
                kwargs["hidden_states"] = h; return args, kwargs
        return pre

    for l, layer in enumerate(model.model.layers):
        layer.register_forward_pre_hook(make_hook(l), with_kwargs=True)

    def run(prompt, cands, want_states=False):
        enc = tok(prompt, return_offsets_mapping=True, return_tensors="pt"); offs = enc.pop("offset_mapping")[0].tolist()
        o = model(**{k: v.cuda() for k, v in enc.items()}, output_hidden_states=want_states)
        lo = o.logits[0, -1].float(); c = [tok(x, add_special_tokens=False).input_ids[0] for x in cands]
        return float(lo[c[1]] - lo[c[0]]), offs, enc["input_ids"][0], (o.hidden_states if want_states else None)

    def positions(prompt, offs):
        lab = [m.start(1) for m in re.finditer(r"Label: (\S+)\n", prompt)]
        labpos = [next(j for j, (s_, e_) in enumerate(offs) if s_ <= st - 1 < e_ or s_ == st) for st in lab]
        inp = [m.span(1) for m in re.finditer(r"(?:Number|Review): (.+)\n", prompt)][:16]
        inppos = [[j for j, (s_, e_) in enumerate(offs) if s_ >= st and e_ <= en] for st, en in inp]
        return labpos, inppos

    bases = []
    for r in rows:
        if r["base_id"] not in bases and r["cond"].endswith(":suffix_3"):
            bases.append(r["base_id"])
    tasks = {}
    for b in bases:
        tasks.setdefault(b.split("_")[1], []).append(b)
    sel = [b for v in tasks.values() for b in v[: a.n_bases]]
    out = {"uid": [], "clean": [], "noisy": [], "anchors": [], "inputs": [], "noise_anchors": [], "all": []}
    for k, b in enumerate(sel):
        task = "mag_nat" if b.startswith("im_mag_nat") else "sst"
        for role in ("maj", "min"):
            rc = by[f"{task}:suffix_3|{role}|{b}"]; rn = by[f"{task}:noise_2__suffix_3|{role}|{b}"]
            lc, offc, idc, hsc = run(rc["prompt"], rc["cands"], True)
            ln, offn, idn, _ = run(rn["prompt"], rn["cands"])
            assert len(idc) == len(idn), "prompts not token-aligned"
            labc, inpc = positions(rc["prompt"], offc)
            anc = [labc[t] for t in (13, 14, 15)]
            k_in = len(anc)
            inp = [p for t in (13, 14, 15) for p in inpc[t][-1:]][:k_in]      # last token of each of the 3 inputs
            res = {}
            noise_anc = [labc[t] for t in (1, 5)]
            allpos = list(range(len(idc)))
            pred = [labc[t] - 1 for t in range(6, 16)]                       # the ':' of "Label:" just before each label word (demos 6-15)
            assert all(tok.decode(idc[p]).strip() == ":" for p in pred), [tok.decode(idc[p]) for p in pred]
            after = [p for p in range(labc[5] + 1, len(idc) - 1) if p not in anc]   # everything after the last noise demo, except the final-run anchors and the answer
            sets = (("anchors", anc), ("inputs", inp), ("noise_anchors", noise_anc), ("all", allpos)) if not PRED else (("pred", pred), ("after", after))
            for name, pos in sets:
                vals = []
                for l in layers:
                    store.clear(); store[("patch", l)] = (torch.tensor(pos), hsc[l][0, pos])
                    vals.append(run(rn["prompt"], rn["cands"])[0])
                store.clear(); res[name] = vals
            out["uid"].append(rn["uid"]); out["clean"].append(lc); out["noisy"].append(ln)
            for name in res:
                out.setdefault(name, []).append(res[name])
        if k % 20 == 0:
            print(k, len(sel), flush=True)
    np.savez(a.out, layers=np.array(layers), **{k: np.array(v) for k, v in out.items() if len(v)})
    print("done", len(out["uid"]))


if __name__ == "__main__":
    main()
