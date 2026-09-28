"""E10 — the protocol confound across intervention families.

For each (model, family), report relative performance per cell.  The question is not
whether a family is damaging, it is whether the *ordering across cells* -- which is
what the literature reads as capability-selectivity -- is reproduced.
"""
import importlib.util, json, pathlib, collections
spec = importlib.util.spec_from_file_location(
    "summ", pathlib.Path(__file__).resolve().parent / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
ROOT = pathlib.Path(__file__).resolve().parents[1]

ORDER = ["mmlu_rank", "mmlu_gen_letter", "mmlu_gen_cot",
         "gsm8k_gen_direct", "gsm8k_gen_cot", "squad_gen"]
LABEL = {"mmlu_rank": "rank/single/know", "mmlu_gen_letter": "gen/short/know",
         "mmlu_gen_cot": "gen/long/know", "gsm8k_gen_direct": "gen/short/reason",
         "gsm8k_gen_cot": "gen/long/reason", "squad_gen": "gen/short/read"}


def key(r):
    return "acc_permissive" if r.get("acc_permissive") is not None else (
        "HasAns_exact" if r.get("HasAns_exact") is not None else "acc")


full = {}
for p in (ROOT / "results" / "e01").rglob("*__full.jsonl"):
    r = summ.score(p); full[(r["model"], r["cell"])] = r

cond = collections.defaultdict(dict)
for p in (ROOT / "results" / "e01").rglob("*__first.jsonl"):
    r = summ.score(p); cond[(r["model"], "readout-first")][r["cell"]] = r
for p in (ROOT / "results" / "e10").rglob("*.jsonl"):
    if "/calib/" in str(p): continue
    r = summ.score(p); cond[(r["model"], r["mask"])][r["cell"]] = r

hdr = "".join(f"{LABEL[c].split('/')[1][:5]+'/'+LABEL[c].split('/')[2][:5]:>13}" for c in ORDER)
print(f"{'model':<14}{'intervention':<15}" + hdr)
for (mdl, iv), cells in sorted(cond.items()):
    line = ""
    for c in ORDER:
        r = cells.get(c); f = full.get((mdl, c))
        if not r or not f: line += f"{'-':>13}"; continue
        k = key(r)
        fv = f.get(k, f["acc"]); av = r.get(k, r["acc"])
        line += f"{(av/fv if fv else float('nan')):>13.3f}"
    print(f"{mdl.split('/')[-1][:13]:<14}{iv:<15}{line}")
print("\nEach number is relative performance vs the same model at full precision on "
      "the same cell.  Columns are (protocol-depth / content).  The literature's "
      "capability claim is the comparison of the rank column against the long-reason "
      "column; the long-know column is the control it never runs.")
