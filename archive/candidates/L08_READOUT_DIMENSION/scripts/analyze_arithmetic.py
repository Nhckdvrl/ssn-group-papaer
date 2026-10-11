"""Conditional analysis: among truncated GSM8K outputs that are NOT degenerate and DO
produce a final answer, is the arithmetic still correct?

E05 showed degeneration is not the cause of the accuracy loss.  The remaining live
possibility is the one the layer-pruning literature proposes for a *different*
intervention: that the damage is to the arithmetic itself.  Our intervention changes
no transformer weight, so if arithmetic is damaged here it cannot be attributed to
lost computation -- it would have to be a readout effect.

GSM8K reference solutions and model chains use the <<a*b=c>> calculator annotation,
and the few-shot prompt teaches it, so intermediate arithmetic is checkable directly.
"""
import json, pathlib, re, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
CALC = re.compile(r"<<([^=<>]+)=([-\d.,]+)>>")
ANS = re.compile(r"#### (\-?[0-9\.\,]+)")


def loops(text, n=8):
    t = text.split()
    if len(t) < 2 * n: return False
    g = [" ".join(t[i:i + n]) for i in range(len(t) - n + 1)]
    return collections.Counter(g).most_common(1)[0][1] / len(g) >= 0.10


def check_calc(text):
    ok = bad = 0
    for expr, res in CALC.findall(text):
        try:
            v = eval(expr.replace(",", ""), {"__builtins__": {}})
            r = float(res.replace(",", ""))
            if abs(v - r) < 1e-4: ok += 1
            else: bad += 1
        except Exception:
            pass
    return ok, bad


print(f"{'model':<26}{'mask':<7}{'n':>5}{'looping':>9}{'has_ans':>9}"
      f"{'clean_n':>9}{'acc|clean':>11}{'calc_ok':>9}{'steps':>7}")
rows = []
for p in sorted((ROOT / "results" / "e01").rglob("gsm8k_gen_cot__*.jsonl")):
    lines = [json.loads(l) for l in open(p)]
    meta, recs = lines[0], lines[1:]
    n = len(recs)
    lp = [loops(r["output"]) for r in recs]
    clean = [r for r, l in zip(recs, lp) if not l]
    with_ans = [r for r in clean if ANS.search(r["output"])]
    corr = sum(1 for r in with_ans
               if ANS.search(r["output"]).group(1).replace(",", "").rstrip(".") == r["gold"])
    ok = bad = steps = 0
    for r in clean:
        a, b = check_calc(r["output"]); ok += a; bad += b
        steps += a + b
    rows.append({"model": meta["model"].split("/")[-1], "mask": meta["mask"],
                 "n": n, "looping": float(np.mean(lp)),
                 "has_ans_of_clean": len(with_ans) / max(1, len(clean)),
                 "clean_n": len(clean),
                 "acc_given_clean_and_ans": corr / max(1, len(with_ans)),
                 "calc_accuracy": ok / max(1, ok + bad),
                 "calc_steps_per_clean_output": steps / max(1, len(clean))})
    r = rows[-1]
    print(f"{r['model']:<26}{r['mask']:<7}{r['n']:>5}{r['looping']:>9.3f}"
          f"{r['has_ans_of_clean']:>9.3f}{r['clean_n']:>9}"
          f"{r['acc_given_clean_and_ans']:>11.3f}{r['calc_accuracy']:>9.3f}"
          f"{r['calc_steps_per_clean_output']:>7.2f}")
print("\nclean = not captured by a repetition loop;  acc|clean = strict answer accuracy "
      "among clean outputs that emitted '#### N';  calc_ok = fraction of <<expr=val>> "
      "calculator steps in clean outputs that evaluate correctly.")
(ROOT / "results" / "arithmetic.json").write_text(json.dumps(rows, indent=1))
