"""Score E08: forced answer emission under truncation."""
import json, pathlib, re, collections
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
NUM = re.compile(r"-?\d[\d,]*\.?\d*")

base = {}
for p in sorted((ROOT / "results" / "e01").rglob("gsm8k_gen_cot__*.jsonl")):
    L = [json.loads(l) for l in open(p)]
    m = L[0]
    hit = 0
    for r in L[1:]:
        g = re.search(r"#### (\-?[0-9\.\,]+)", r["output"])
        hit += bool(g and g.group(1).replace(",", "").rstrip(".") == r["gold"])
    base[(m["model"], m["mask"])] = hit / len(L[1:])

print(f"{'model':<26}{'mask':<7}{'condition':<12}{'acc':>8}{'rel_full':>10}"
      f"{'x_free':>8}{'chain_chars':>12}")
for p in sorted((ROOT / "results" / "e08").rglob("*.jsonl")):
    L = [json.loads(l) for l in open(p)]
    meta = L[0]
    by = collections.defaultdict(list)
    for r in L[1:]: by[r["condition"]].append(r)
    free = base.get((meta["model"], meta["mask"]))
    full = base.get((meta["model"], "full"))
    mm = meta["model"].split("/")[-1]
    print(f"{mm:<26}{meta['mask']:<7}{'free (E02)':<12}{free:>8.4f}"
          f"{(free/full):>10.3f}{1.0:>8.2f}{'-':>12}")
    for cond, rs in by.items():
        ok = 0
        for r in rs:
            m = NUM.findall(r["output"].replace("$", ""))
            ok += bool(m and m[0].replace(",", "").rstrip(".") == r["gold"])
        a = ok / len(rs)
        print(f"{mm:<26}{meta['mask']:<7}{cond:<12}{a:>8.4f}"
              f"{(a/full):>10.3f}{(a/free if free else float('inf')):>8.2f}"
              f"{np.mean([r['chain_chars'] for r in rs]):>12.0f}")
print("\nfree = the model must emit '#### N' itself.  forced = the answer marker is "
      "appended to the model's own truncated chain and it completes the number.  "
      "rel_full = / the full-readout free-running accuracy.")
