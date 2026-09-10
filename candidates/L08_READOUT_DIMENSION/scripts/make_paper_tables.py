"""Emit the paper's main tables from raw results.  Single source of truth.

T1  the confounded comparison and its three factors, on one model's own data
T2  the full protocol x depth x content factorial, every model, readout intervention
T3  controlled vs uncontrolled capability-selectivity, every model x intervention
T4  the mechanism hunt: what was tested and rejected
"""
import importlib.util, json, pathlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)

CELLS = ["mmlu_rank", "mmlu_gen_letter", "mmlu_gen_cot",
         "gsm8k_gen_direct", "gsm8k_gen_cot", "squad_gen"]
COORD = {"mmlu_rank": ("rank K=4", "single", "knowledge"),
         "mmlu_gen_letter": ("argmax", "short", "knowledge"),
         "mmlu_gen_cot": ("argmax", "long", "knowledge"),
         "gsm8k_gen_direct": ("argmax", "short", "reasoning"),
         "gsm8k_gen_cot": ("argmax", "long", "reasoning"),
         "squad_gen": ("argmax", "short", "reading")}
SHORT = {"llama31_8b_instruct": "Llama-3.1-8B-It", "qwen25_7b_instruct": "Qwen2.5-7B-It",
         "phi4_mini_instruct": "Phi-4-mini-It", "olmo3_7b_base": "OLMo-3-7B",
         "mistral_7b_v03": "Mistral-7B-v0.3"}


def key(r):
    return ("acc_permissive" if r.get("acc_permissive") is not None else
            "HasAns_exact" if r.get("HasAns_exact") is not None else "acc")


def load():
    full, cond = {}, collections.defaultdict(dict)
    for p in (ROOT / "results" / "e01").rglob("*.jsonl"):
        r = summ.score(p)
        if r.get("correct") is None: continue
        m = p.parent.name
        if r["mask"] == "full": full[(m, r["cell"])] = r
        else: cond[(m, f"readout-{r['mask']}")][r["cell"]] = r
    for p in (ROOT / "results" / "e10").rglob("*.jsonl"):
        if "calib" in str(p) or "_invalid" in str(p): continue
        r = summ.score(p)
        if r.get("correct") is None: continue
        cond[(p.parent.name, r["mask"])][r["cell"]] = r
    return full, cond


TAGMAP = {"llama": "llama31_8b_instruct", "qwen": "qwen25_7b_instruct",
          "phi4": "phi4_mini_instruct", "olmo3": "olmo3_7b_base"}


def rel(full, cond, m, iv, cell):
    fm = TAGMAP.get(m, m)
    f = full.get((fm, cell)); t = cond[(m, iv)].get(cell)
    if not f or not t: return None
    k = key(t)
    fv = f.get(k, f["acc"]); tv = t.get(k, t["acc"])
    return tv / fv if fv else None


def main():
    full, cond = load()
    models = sorted({k[0] for k in full})

    print("### T2 — protocol x depth x content factorial, readout truncation\n")
    hdr = "".join(f"{c.replace('_gen','').replace('mmlu','MM').replace('gsm8k','GSM').replace('squad','SQ'):>13}"
                  for c in CELLS)
    print(f"{'model':<18}{'mask':<8}{hdr}")
    for m in models:
        for iv in ("readout-first", "readout-last"):
            if (m, iv) not in cond: continue
            row = "".join(f"{(v if (v := rel(full, cond, m, iv, c)) is not None else float('nan')):>13.3f}"
                          for c in CELLS)
            print(f"{SHORT.get(m,m)[:17]:<18}{iv.split('-')[1]:<8}{row}")
    print("\ncoordinates: " + ", ".join(f"{c}={'/'.join(COORD[c])}" for c in CELLS[:3]) + " ...")

    print("\n### T1 — the three factors, isolated (Llama 3.1 8B, readout first-half)\n")
    m, iv = "llama31_8b_instruct", "readout-first"
    if (m, iv) in cond:
        print(f"  protocol, matched items+prompt+depth : mmlu_rank {rel(full,cond,m,iv,'mmlu_rank'):.3f}"
              f"  ->  mmlu_gen_letter {rel(full,cond,m,iv,'mmlu_gen_letter'):.3f}")
        print(f"  depth, matched protocol+content     : mmlu_gen_letter {rel(full,cond,m,iv,'mmlu_gen_letter'):.3f}"
              f"  ->  mmlu_gen_cot {rel(full,cond,m,iv,'mmlu_gen_cot'):.3f}")
        print(f"  content, matched protocol+depth     : mmlu_gen_cot {rel(full,cond,m,iv,'mmlu_gen_cot'):.3f}"
              f"  vs  gsm8k_gen_cot {rel(full,cond,m,iv,'gsm8k_gen_cot'):.3f}")

    print("\n### T3 — capability-selectivity, uncontrolled vs controlled\n")
    sel = ROOT / "results" / "selectivity.json"
    if sel.exists():
        d = json.loads(sel.read_text())
        A = {(a, b): (p, lo, hi) for a, b, p, lo, hi in d["uncontrolled"]}
        B = {(a, b): (p, lo, hi) for a, b, p, lo, hi in d["controlled"]}
        print(f"{'model':<18}{'intervention':<16}{'uncontrolled':>13}{'controlled':>12}{'95% CI':>18}{'removed':>9}")
        for k in sorted(set(A) & set(B)):
            a, b = A[k][0], B[k][0]
            nm = SHORT.get(TAGMAP.get(k[0], k[0]), k[0])
            print(f"{nm[:17]:<18}{k[1]:<16}{a:>13.2f}{b:>12.2f}"
                  f"   [{B[k][1]:>5.2f},{B[k][2]:>6.2f}]"
                  f"{(1-(b-1)/(a-1) if a>1 else float('nan')):>9.1%}")
    else:
        print("  run scripts/analyze_selectivity.py first")

    print("\n### T4 — mechanism accounts tested\n")
    for line in [
        ("fixed vocabulary prior installed", "E03b, vs norm-matched random", "rejected"),
        ("extreme-value competition over |V|", "E04, survival vs candidate-set size", "rejected (flat beyond K=8)"),
        ("capture by repetition attractors", "E05, no_repeat_ngram", "rejected (0.87->0.006, acc 0.109->0.089)"),
        ("per-step prediction badly damaged", "E04, top-1 agreement", "rejected (0.62-0.92)"),
        ("structural tokens selectively demoted", "E09, class x margin", "rejected (no cross-model replication)"),
        ("margin governs survival", "E06, s(m)", "supported, partial (errors -0.66..+0.22)"),
        ("emission/termination failure", "E08, forced answer marker", "supported, partial (0.000->0.178)"),
    ]:
        print(f"  {line[0]:<40}{line[1]:<38}{line[2]}")


if __name__ == "__main__":
    main()
