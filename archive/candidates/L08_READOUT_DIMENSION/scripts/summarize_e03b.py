"""Score E03b against the E02 collapse and the full-readout baseline."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "summ", pathlib.Path(__file__).resolve().parent / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAG2MODEL = {"llama_first": "llama31_8b_instruct", "qwen_first": "qwen25_7b_instruct"}

rows = []
for p in sorted((ROOT / "results" / "e03b").rglob("*.jsonl")):
    r = summ.score(p); r["tag"] = p.parent.name; rows.append(r)

# baselines from E02
base = {}
for p in sorted((ROOT / "results" / "e01").rglob("*.jsonl")):
    r = summ.score(p)
    base[(r["model"], r["cell"], r["mask"])] = r

print(f"{'model':<28}{'cell':<16}{'mask':<7}{'condition':<10}"
      f"{'acc':>8}{'rel_full':>10}{'x_none':>9}   note")
for r in sorted(rows, key=lambda x: (x["model"], x["cell"], x["e03b_condition"])):
    full = base.get((r["model"], r["cell"], "full"), {}).get("acc")
    none = base.get((r["model"], r["cell"], r["mask"]), {}).get("acc")
    key = "acc_permissive" if "acc_permissive" in r else "acc"
    a = r[key]
    fullv = base.get((r["model"], r["cell"], "full"), {}).get(key, full)
    nonev = base.get((r["model"], r["cell"], r["mask"]), {}).get(key, none)
    rel = a / fullv if fullv else float("nan")
    x = (a / nonev) if nonev else float("inf")
    note = "" if r["e03b_condition"] != "random" else "norm-matched control"
    print(f"{r['model'].split('/')[-1]:<28}{r['cell']:<16}{r['mask']:<7}"
          f"{r['e03b_condition']:<10}{a:>8.4f}{rel:>10.3f}{x:>9.2f}   {note}")
print("\nrel_full = accuracy / full-readout accuracy;  x_none = ratio to the "
      "uncorrected truncated run (E02).")
