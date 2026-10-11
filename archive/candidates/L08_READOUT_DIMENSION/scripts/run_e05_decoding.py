"""E05 — is the collapse of long generation a decoding-dynamics failure?

State of the evidence entering this experiment:
  E04  truncation leaves per-step top-1 agreement at 0.62-0.92 and does not promote
       tail tokens at all (survival is flat in candidate-set size beyond K~8);
  degeneration analysis  truncation raises the rate of repetition-loop outputs from
       0.00-0.07 to 0.36-0.87, with the loop starting in the first ~10-17% of the text;
  E03b  the damage is not a fixed vocabulary bias (a norm-matched random vector does
       as well or better than the estimated one).

That combination says the next-token distribution is largely intact and the *chain*
is what breaks.  If so, an intervention that only prevents the decoder from entering
a loop -- without restoring a single readout dimension -- should recover a large part
of the lost accuracy.  If it does not, the distribution is broken in a way repetition
does not capture and the accumulation account returns.

Conditions (all under the same readout mask):
  greedy        the E02 baseline
  norep6        greedy + no_repeat_ngram_size=6      (blocks the attractor only)
  sample        top-p 0.9, T=0.7, seeded             (leaves the attractor escapable)
And the same two on the FULL readout, to check the interventions are not themselves
what produces accuracy.
"""
from __future__ import annotations
import argparse, importlib.util, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.readout import ReadoutTruncation, build_mask, mask_id

spec = importlib.util.spec_from_file_location(
    "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

GEN_KWARGS = {
    "greedy": {"do_sample": False},
    "norep6": {"do_sample": False, "no_repeat_ngram_size": 6},
    "sample": {"do_sample": True, "top_p": 0.9, "temperature": 0.7},
}


@torch.no_grad()
def gen(model, tok, items, bs, max_new, stops, kw):
    order = sorted(range(len(items)), key=lambda i: -len(items[i]["prompt"]))
    out = {}
    pad = tok.pad_token_id or tok.eos_token_id
    for s in range(0, len(order), bs):
        idxs = order[s:s + bs]
        enc = tok([items[i]["prompt"] for i in idxs], return_tensors="pt",
                  padding=True, padding_side="left").to(model.device)
        g = model.generate(**enc, max_new_tokens=max_new, pad_token_id=pad, **kw)
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
    ap.add_argument("--cells", default="gsm8k_gen_cot")
    ap.add_argument("--conditions", default="norep6,sample")
    ap.add_argument("--also-full", action="store_true")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    d = model.config.hidden_size

    masks = [a.mask] + (["full"] if a.also_full else [])
    for cell in a.cells.split(","):
        items = run_eval.load_items(cell, a.n, 1234)
        mx, stops = run_eval.CELL_GEN[cell]
        for mk in masks:
            mask = build_mask(d, mk, 0.5)
            for cond in a.conditions.split(","):
                out = root / "results" / "e05" / a.tag / f"{cell}__{mk}__{cond}.jsonl"
                if out.exists(): print("skip", out); continue
                torch.manual_seed(a.seed)
                t0 = time.time()
                with ReadoutTruncation(model, mask):
                    recs = gen(model, tok, items, a.bs, mx, stops, GEN_KWARGS[cond])
                out.parent.mkdir(parents=True, exist_ok=True)
                header = {"_meta": True, "model": a.model, "cell": cell, "mask": mk,
                          "keep_frac": 0.5, "mask_seed": 0, "placement": "post_norm",
                          "hidden_size": d, "n_kept_dims": int(mask.sum()),
                          "mask_id": mask_id(mask), "n_items": len(items),
                          "data_seed": 1234, "decoding": cond,
                          "gen_kwargs": GEN_KWARGS[cond], "torch_seed": a.seed,
                          "runtime_s": round(time.time() - t0, 1)}
                with open(out, "w") as f:
                    f.write(json.dumps(header) + "\n")
                    for r in recs: f.write(json.dumps(r) + "\n")
                print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
