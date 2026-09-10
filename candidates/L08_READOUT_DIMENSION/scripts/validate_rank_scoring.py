"""Audit the batched/windowed rank scorer against a naive single-sequence scorer.

run_rank left-pads, batches, and asks for only the tail logits (`logits_to_keep`).
Each of those is an opportunity to score the wrong position, which would silently
corrupt every ranking number in the paper.  This checks it against an unbatched,
unwindowed, full-logit reference.
"""
import importlib.util, sys, pathlib, torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import tasks

spec = importlib.util.spec_from_file_location(
    "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
dev = "cuda:0" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None: tok.pad_token = tok.eos_token
m = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).to(dev).eval()

items = tasks.build_mmlu(8, 1234, shots=0, protocol="rank")   # short prompts


@torch.no_grad()
def reference(it):
    out = []
    for c in it["candidates"]:
        pi = tok(it["prompt"])["input_ids"]
        ci = tok(c, add_special_tokens=False)["input_ids"]
        ids = torch.tensor([pi + ci], device=dev)
        lp = torch.log_softmax(m(input_ids=ids).logits.float(), -1)
        out.append(sum(lp[0, len(pi) + k - 1, t].item() for k, t in enumerate(ci)))
    return out


got = {r["id"]: r["scores"] for r in run_eval.run_rank(m, tok, items, 5)}  # odd bs
ref = {it["id"]: reference(it) for it in items}
mx = max(abs(a - b) for i in got for a, b in zip(got[i], ref[i]))
agree = all(max(range(4), key=lambda k: got[i][k]) ==
            max(range(4), key=lambda k: ref[i][k]) for i in got)
print(f"items={len(items)}  batch=5 (deliberately not a divisor)")
print(f"max abs logprob diff vs naive reference : {mx:.3e}")
print(f"argmax agreement                        : {agree}")
assert mx < 1e-3 and agree, "batched rank scorer disagrees with reference"
print("PASS")
