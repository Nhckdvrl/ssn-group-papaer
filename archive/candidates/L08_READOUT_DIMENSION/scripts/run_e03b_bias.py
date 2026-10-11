"""E03b — does adding back only the fixed part of the removed readout recover the task?

Truncation subtracts r_t = W_U[:,S^c] h_t[S^c] from the logits.  E03a showed r_t has a
large, highly reproducible context-independent component b_bar (estimated on held-out
prompts) plus a larger context-varying residual.  Here we add b_bar back and ask what
the model can do again.

Conditions (all with the same readout mask applied):
  none      truncated, no correction                       -> the E02 collapse
  bias      truncated + b_bar from held-out prompts of the SAME cell
  random    truncated + a random vector matched in ||.||    -> rules out "any nudge helps"
  cross     truncated + b_bar estimated on the OTHER cell's contexts

A recovery under `bias` but not `random` identifies the fixed component as causally
responsible.  Recovery under `cross` too means the installed prior is task-independent.
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

# which E03a bias vector plays "own" and which plays the cross-task donor
OWN   = {"mmlu_gen_cot": "mmlu_gen_letter", "gsm8k_gen_cot": "gsm8k_gen_cot"}
CROSS = {"mmlu_gen_cot": "gsm8k_gen_cot",   "gsm8k_gen_cot": "mmlu_gen_letter"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True, help="matches results/e03/bias_<tag>.pt")
    ap.add_argument("--mask", default="first")
    ap.add_argument("--cells", default="mmlu_gen_cot,gsm8k_gen_cot")
    ap.add_argument("--conditions", default="bias,random,cross")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    biases = torch.load(root / "results" / "e03" / f"bias_{a.tag}.pt")
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)
    g = torch.Generator().manual_seed(a.seed)

    for cell in a.cells.split(","):
        # b_bar was estimated on the cell's own contexts where available; for
        # mmlu_gen_cot we use the mmlu_gen_letter contexts (same items, same model,
        # short prompts) -- disjoint from the CoT prompt format, which if anything
        # makes the test harder.
        own = biases[OWN[cell]]
        other = biases.get(CROSS[cell])
        items = run_eval.load_items(cell, a.n, 1234)
        mx, stops = run_eval.CELL_GEN[cell]
        for cond in a.conditions.split(","):
            out = root / "results" / "e03b" / a.tag / f"{cell}__{a.mask}__{cond}.jsonl"
            if out.exists():
                print("skip", out); continue
            if cond == "bias":
                b = own
            elif cond == "random":
                b = torch.randn(own.shape, generator=g)
                b = b / b.norm() * own.norm()          # norm-matched
            elif cond == "cross":
                if other is None or torch.equal(other, own):
                    print("skip cross (no distinct donor) for", cell); continue
                b = other
            elif cond == "none":
                b = None
            else:
                raise ValueError(cond)
            t0 = time.time()
            with ReadoutTruncation(model, mask, logit_bias=b):
                recs = run_eval.run_gen(model, tok, items, a.bs, mx, stops)
            out.parent.mkdir(parents=True, exist_ok=True)
            header = {"_meta": True, "model": a.model, "cell": cell, "mask": a.mask,
                      "keep_frac": 0.5, "mask_seed": 0, "placement": "post_norm",
                      "hidden_size": model.config.hidden_size,
                      "n_kept_dims": int(mask.sum()), "mask_id": mask_id(mask),
                      "n_items": len(items), "data_seed": 1234,
                      "e03b_condition": cond,
                      "bias_norm": float(b.norm()) if b is not None else 0.0,
                      "bias_seed": a.seed if cond == "random" else None,
                      "runtime_s": round(time.time() - t0, 1)}
            with open(out, "w") as f:
                f.write(json.dumps(header) + "\n")
                for r in recs: f.write(json.dumps(r) + "\n")
            print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
