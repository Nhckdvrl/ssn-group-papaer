#!/usr/bin/env python3
"""E194 R2 Patchscopes: patch a source vector into 'Repeat this word twice: 1) X 2)' at the output of decoder
layer l (position of ' X') and decode greedily; success = the text after the prompt starts with the word.
Random reference: the same with the vector of another item of the same stratum.
Usage: e194_patch.py MODEL_DIR TOK_DIR ITEMS_JSON CAPTURE_DIR [--limit K]
"""
import argparse
import json
import random
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

EOS, PAD = 100257, 100277
LAYERS = list(range(0, 9)) + [12, 16, 20, 24, 28]  # decoder-layer outputs (capture index = l + 1)
N_PER = 300


class Patcher:
    def __init__(self, model):
        self.layers = model.model.layers
        self.layer, self.vec, self.pos = None, None, None
        self.hs = [m.register_forward_hook(self._hook(i)) for i, m in enumerate(self.layers)]

    def _hook(self, i):
        def f(mod, inp, output):
            if i != self.layer:
                return None
            h = output[0] if isinstance(output, tuple) else output
            h = h.clone()
            h[:, self.pos] = self.vec.to(h.dtype)
            return (h,) + tuple(output[1:]) if isinstance(output, tuple) else h
        return f


@torch.no_grad()
def generate(model, patcher, prompt, vecs, layer, n_new):
    B = vecs.shape[0]
    x = torch.tensor([prompt] * B, device="cuda")
    patcher.layer, patcher.vec = layer, vecs.cuda()
    for _ in range(n_new):
        nxt = model(input_ids=x).logits[:, -1].argmax(-1, keepdim=True)
        x = torch.cat([x, nxt], 1)
    patcher.layer = None
    return x[:, len(prompt):].tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("tok"); ap.add_argument("items"); ap.add_argument("cap")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.tok)
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    x_id = enc(" X")
    assert len(x_id) == 1
    prompt = [EOS] + enc("Repeat this word twice: 1)") + x_id + enc(" 2)")
    pos = len(prompt) - 1 - len(enc(" 2)"))
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    patcher = Patcher(model)
    patcher.pos = pos
    I = json.loads(Path(a.items).read_text())
    cap = Path(a.cap)
    rng = random.Random(194)
    jobs = []  # (set, stratum, forms, src[n, L+1, d], m)
    S = torch.load(cap / "S.pt")
    forms = [it["form"] for it in I["S"][:S["src"].shape[0]]]
    for k, name in enumerate(S["src_names"]):
        n = min(N_PER, len(forms), a.limit or 10**9)
        jobs.append(("S", name, forms[:n], S["src"][:n, :, k], 1 if name == "m1" else int(name[1:])))
    Nd = torch.load(cap / "N.pt")
    for st in ["2", "3", "4+"]:
        idx = [i for i, s in enumerate(Nd["stratum"]) if s == st][:min(N_PER, a.limit or 10**9)]
        mmax = max(Nd["m"][i] for i in idx)
        jobs.append(("N", st, [Nd["form"][i] for i in idx], Nd["reps"][idx, :, 0, 0], mmax))
    res, t0 = [], time.time()
    for set_, st, fs, src, m in jobs:
        n = len(fs)
        perm = list(range(n))
        while n > 1 and any(p == i for i, p in enumerate(perm)):
            rng.shuffle(perm)
        for l in LAYERS:
            for kind, vec in (("real", src[:, l + 1]), ("random", src[perm, l + 1])):
                outs = []
                for b in range(0, n, 150):
                    outs += generate(model, patcher, prompt, vec[b:b + 150].float(), l, m + 3)
                ok = [tok.decode(o).strip().lower().startswith(f.lower()) for o, f in zip(outs, fs)]
                res.append({"set": set_, "stratum": st, "layer": l, "kind": kind, "n": n, "succ": ok,
                            "sample": [tok.decode(o) for o in outs[:3]]})
        print(json.dumps({"done": f"{set_}/{st}", "sec": round(time.time() - t0, 1),
                          "acc_real_by_layer": [round(sum(r["succ"]) / r["n"], 3) for r in res
                                                if r["set"] == set_ and r["stratum"] == st and r["kind"] == "real"]}),
              flush=True)
    (cap / "R2.json").write_text(json.dumps({"layers": LAYERS, "prompt": tok.decode(prompt), "results": res}))


if __name__ == "__main__":
    main()
