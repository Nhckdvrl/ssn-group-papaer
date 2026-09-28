"""E10 — does the protocol confound reproduce across compression families?

C1 established, for readout truncation, that the knowledge-vs-reasoning asymmetry is
carried by evaluation protocol and output length rather than by the capability.  The
same comparison structure -- ranking-scored knowledge/classification benchmarks
against generation-scored reasoning benchmarks -- is how the compression literature
generally establishes capability-selective damage.  If the confound is real it should
appear for weight pruning and for quantization too, which touch the model's
computation, and not only for a readout intervention, which does not.

Runs the same six-cell factorial under each family, at a level chosen so the family's
GSM8K damage is comparable to the parent's.
"""
from __future__ import annotations
import argparse, importlib.util, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import interventions

spec = importlib.util.spec_from_file_location(
    "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

CELLS = {"mmlu_rank": (1000, 8), "mmlu_gen_letter": (1000, 32),
         "mmlu_gen_cot": (400, 16), "gsm8k_gen_cot": (500, 16),
         "gsm8k_gen_direct": (500, 32), "squad_gen": (1000, 16)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--family", required=True, choices=["prune", "quant", "none"])
    ap.add_argument("--level", type=float, required=True)
    ap.add_argument("--cells", default=",".join(CELLS))
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()

    lvl = f"{a.level:g}".replace(".", "p")
    with interventions.make(model, a.family, a.level) as iv:
        extra = {"prune_threshold": getattr(iv, "threshold", None)}
        for cell in a.cells.split(","):
            n, bs = CELLS[cell]
            out = (root / "results" / "e10" / a.tag /
                   f"{cell}__{a.family}{lvl}.jsonl")
            if out.exists(): print("skip", out); continue
            items = run_eval.load_items(cell, n, 1234)
            t0 = time.time()
            if cell.endswith("_rank"):
                recs = run_eval.run_rank(model, tok, items, bs * 2)
            else:
                mx, stops = run_eval.CELL_GEN[cell]
                recs = run_eval.run_gen(model, tok, items, bs, mx, stops)
            out.parent.mkdir(parents=True, exist_ok=True)
            header = {"_meta": True, "model": a.model, "cell": cell,
                      "mask": f"{a.family}{lvl}", "family": a.family,
                      "level": a.level, "n_items": len(items), "data_seed": 1234,
                      "hidden_size": model.config.hidden_size,
                      "runtime_s": round(time.time() - t0, 1), **extra}
            with open(out, "w") as f:
                f.write(json.dumps(header) + "\n")
                for r in recs: f.write(json.dumps(r) + "\n")
            print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
