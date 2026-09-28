"""Score E05 decoding conditions against the E02 greedy baselines."""
import importlib.util, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location(
    "summ", pathlib.Path(__file__).resolve().parent / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
spec2 = importlib.util.spec_from_file_location(
    "deg", pathlib.Path(__file__).resolve().parent / "analyze_degeneration.py")

ROOT = pathlib.Path(__file__).resolve().parents[1]
import collections, numpy as np, re


def rep_frac(path, n=8):
    lines = [json.loads(l) for l in open(path)][1:]
    out = []
    for r in lines:
        toks = r["output"].split()
        if len(toks) < n * 2: out.append(0.0); continue
        grams = [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]
        out.append(collections.Counter(grams).most_common(1)[0][1] / len(grams))
    return float(np.mean([x >= 0.10 for x in out]))


base = {}
for p in sorted((ROOT / "results" / "e01").rglob("*_cot__*.jsonl")):
    r = summ.score(p)
    base[(r["model"], r["cell"], r["mask"])] = (r, rep_frac(p))

rows = []
for p in sorted((ROOT / "results" / "e05").rglob("*.jsonl")):
    r = summ.score(p); r["_rep"] = rep_frac(p); r["_path"] = p; rows.append(r)

key = "acc_permissive"
print(f"{'model':<26}{'cell':<15}{'mask':<6}{'decoding':<9}"
      f"{'acc':>8}{'rel_full':>10}{'x_greedy':>10}{'looping':>9}")
seen = set()
for r in sorted(rows, key=lambda x: (x["model"], x["cell"], x["mask"], x["decoding"])):
    k = (r["model"], r["cell"], r["mask"])
    if k not in seen and k in base:                       # print greedy baseline first
        b, br = base[k]
        fullb = base.get((r["model"], r["cell"], "full"), (None,))[0]
        fv = fullb.get(key, fullb.get("acc")) if fullb else None
        av = b.get(key, b["acc"])
        print(f"{r['model'].split('/')[-1]:<26}{r['cell']:<15}{r['mask']:<6}"
              f"{'greedy*':<9}{av:>8.4f}{(av/fv if fv else float('nan')):>10.3f}"
              f"{1.0:>10.2f}{br:>9.3f}")
        seen.add(k)
    fullb = base.get((r["model"], r["cell"], "full"), (None,))[0]
    fv = fullb.get(key, fullb.get("acc")) if fullb else None
    gb = base.get(k, (None,))[0]
    gv = gb.get(key, gb["acc"]) if gb else None
    a = r.get(key, r["acc"])
    print(f"{r['model'].split('/')[-1]:<26}{r['cell']:<15}{r['mask']:<6}"
          f"{r['decoding']:<9}{a:>8.4f}{(a/fv if fv else float('nan')):>10.3f}"
          f"{(a/gv if gv else float('nan')):>10.2f}{r['_rep']:>9.3f}")
print("\n* greedy row is the E02 run.  rel_full = / full-readout greedy accuracy; "
      "x_greedy = / same-mask greedy accuracy; looping = fraction of outputs whose "
      "most frequent 8-gram covers >=10% of the output.")
