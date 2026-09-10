"""E08 — computation or emission?

Post-hoc conditioning (scripts/analyze_arithmetic.py) says that when a truncated model
does emit a well-formed GSM8K answer, that answer is as accurate as the full model's
(0.868-1.000 vs 0.782-0.850) and its calculator steps are 94.5-100% correct.  What
collapses is the *rate of emitting an answer at all*: among non-degenerate outputs,
0.000-0.195 emit "#### N" versus 0.945-0.958 at full readout.

That is post-hoc: the outputs that emit an answer are a self-selected minority.  This
experiment tests it causally, by removing the model's need to emit the answer marker
itself.

Conditions (readout truncated throughout in all of them):
  free        the E02 condition: generate, then look for "#### N"
  forced      generate the chain, then APPEND the answer marker to the context and
              let the model complete the number.  The chain is the truncated model's
              own; only the decision to *stop and answer* is supplied.
  forced_cap  same, but the chain is cut at the full model's median chain length
              before the marker is appended, so a truncated model that would have
              rambled is not given extra room.

If `forced` recovers a large share of the accuracy that `free` lost, the truncated
model was computing correctly and failing to emit.  If it does not, the chains
themselves are broken and the emission story is a selection effect.
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

MARKER = "\n#### "


@torch.no_grad()
def batched_generate(model, tok, prompts, bs, max_new, pad):
    out = [None] * len(prompts)
    order = sorted(range(len(prompts)), key=lambda i: -len(prompts[i]))
    for s in range(0, len(order), bs):
        idxs = order[s:s + bs]
        enc = tok([prompts[i] for i in idxs], return_tensors="pt",
                  padding=True, padding_side="left").to(model.device)
        g = model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                           pad_token_id=pad)
        new = g[:, enc["input_ids"].shape[1]:]
        for j, i in enumerate(idxs):
            out[i] = tok.decode(new[j], skip_special_tokens=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--chain-tokens", type=int, default=400)
    ap.add_argument("--cap-chars", type=int, default=240)
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    pad = tok.pad_token_id or tok.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)
    items = run_eval.load_items("gsm8k_gen_cot", a.n, 1234)

    for mk in (a.mask, "full"):
        m = build_mask(model.config.hidden_size, mk, 0.5)
        out = root / "results" / "e08" / a.tag / f"gsm8k__{mk}__emission.jsonl"
        if out.exists(): print("skip", out); continue
        t0 = time.time()
        with ReadoutTruncation(model, m):
            chains = batched_generate(model, tok,
                                      [it["prompt"] for it in items], a.bs,
                                      a.chain_tokens, pad)
            recs = []
            for cap, name in ((None, "forced"), (a.cap_chars, "forced_cap")):
                ctx = []
                for it, ch in zip(items, chains):
                    c = ch.split("\nQuestion:")[0]
                    if cap is not None: c = c[:cap]
                    ctx.append(it["prompt"] + c + MARKER)
                tails = batched_generate(model, tok, ctx, a.bs, 12, pad)
                for it, ch, t in zip(items, chains, tails):
                    recs.append({"id": it["id"], "condition": name,
                                 "chain_chars": len(ch.split("\nQuestion:")[0]),
                                 "output": MARKER + t, "gold": it["gold"],
                                 "meta": {}})
        out.parent.mkdir(parents=True, exist_ok=True)
        header = {"_meta": True, "model": a.model, "cell": "gsm8k_gen_cot", "mask": mk,
                  "keep_frac": 0.5, "mask_seed": 0, "placement": "post_norm",
                  "hidden_size": model.config.hidden_size,
                  "n_kept_dims": int(m.sum()), "mask_id": mask_id(m),
                  "n_items": len(items), "data_seed": 1234,
                  "marker": MARKER, "cap_chars": a.cap_chars,
                  "runtime_s": round(time.time() - t0, 1)}
        with open(out, "w") as f:
            f.write(json.dumps(header) + "\n")
            for r in recs: f.write(json.dumps(r) + "\n")
        print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
