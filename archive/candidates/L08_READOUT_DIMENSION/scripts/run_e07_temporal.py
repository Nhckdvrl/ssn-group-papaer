"""E07 — is the depth effect causal, and is the damage recoverable?

C1's central finding (depth carries the collapse) currently rests on a *cross-cell*
comparison: short-answer cells survive, long-CoT cells do not.  Cells differ in more
than length, so the claim needs a within-item causal version.

Here the readout mask is switched on and off *during* a single generation:

  all        truncated for every generated token            (the E02 condition)
  firstN     truncated for the first N tokens, then full readout restored
  afterN     full readout for the first N tokens, then truncated for the rest
  none       full readout throughout                        (the E02 baseline)

Readings:
  firstN ~ none      early damage is recoverable; the chain repairs itself and the
                     collapse requires *sustained* exposure -> depth is causal
  firstN ~ all       the opening tokens fix the outcome; length is a red herring and
                     the real quantity is the first few decisions
  afterN ~ all       damage anywhere in the chain is fatal
  afterN ~ none      only the opening matters

The switch is implemented by entering/leaving the same hook mid-generation, so nothing
but the timing differs between conditions.
"""
from __future__ import annotations
import argparse, importlib.util, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.readout import build_mask, mask_id

spec = importlib.util.spec_from_file_location(
    "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)


class Schedule:
    """Applies the readout mask only on generated steps in [lo, hi)."""

    def __init__(self, model, mask, lo, hi):
        self.model, self.lo, self.hi = model, lo, hi
        self.keep = mask.to(model.lm_head.weight.device)
        self.step = 0
        self.h = None

    def __enter__(self):
        def pre(_m, args):
            (x,) = args
            on = self.lo <= self.step < self.hi
            self.step += 1
            return (x * self.keep.to(x.dtype),) if on else (x,)
        self.h = self.model.lm_head.register_forward_pre_hook(pre)
        return self

    def reset(self): self.step = 0

    def __exit__(self, *e):
        if self.h: self.h.remove(); self.h = None


@torch.no_grad()
def gen(model, tok, items, bs, max_new, stops, sched):
    order = sorted(range(len(items)), key=lambda i: -len(items[i]["prompt"]))
    out = {}
    pad = tok.pad_token_id or tok.eos_token_id
    for s in range(0, len(order), bs):
        idxs = order[s:s + bs]
        enc = tok([items[i]["prompt"] for i in idxs], return_tensors="pt",
                  padding=True, padding_side="left").to(model.device)
        sched.reset()          # step 0 is the prefill; generated steps follow
        g = model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                           pad_token_id=pad)
        new = g[:, enc["input_ids"].shape[1]:]
        for j, i in enumerate(idxs):
            txt = tok.decode(new[j], skip_special_tokens=True)
            for st in stops:
                if st in txt: txt = txt.split(st)[0]
            out[i] = {"id": items[i]["id"], "output": txt,
                      "n_new_tokens": int(new[j].shape[0]),
                      "gold": items[i]["gold"], "meta": items[i]["meta"]}
    return [out[i] for i in range(len(items))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--cell", default="gsm8k_gen_cot")
    ap.add_argument("--switch", type=int, default=16)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--bs", type=int, default=16)
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)
    items = run_eval.load_items(a.cell, a.n, 1234)
    mx, stops = run_eval.CELL_GEN[a.cell]
    N = a.switch
    BIG = 10 ** 9
    conds = {"all": (0, BIG), f"first{N}": (0, N + 1), f"after{N}": (N + 1, BIG)}

    for name, (lo, hi) in conds.items():
        out = root / "results" / "e07" / a.tag / f"{a.cell}__{a.mask}__{name}.jsonl"
        if out.exists(): print("skip", out); continue
        t0 = time.time()
        with Schedule(model, mask, lo, hi) as sch:
            recs = gen(model, tok, items, a.bs, mx, stops, sch)
        out.parent.mkdir(parents=True, exist_ok=True)
        header = {"_meta": True, "model": a.model, "cell": a.cell, "mask": a.mask,
                  "keep_frac": 0.5, "mask_seed": 0, "placement": "post_norm",
                  "hidden_size": model.config.hidden_size,
                  "n_kept_dims": int(mask.sum()), "mask_id": mask_id(mask),
                  "n_items": len(items), "data_seed": 1234,
                  "schedule": name, "switch_at": N, "window": [lo, min(hi, mx)],
                  "runtime_s": round(time.time() - t0, 1)}
        with open(out, "w") as f:
            f.write(json.dumps(header) + "\n")
            for r in recs: f.write(json.dumps(r) + "\n")
        print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
