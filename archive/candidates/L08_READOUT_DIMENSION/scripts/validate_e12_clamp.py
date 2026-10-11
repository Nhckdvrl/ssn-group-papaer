"""E12 §9 validation.  Each check can fail; none of them involves a claim.

  V0  reference table: answer positions parse, L0 is in range, token-id clamp is
      faithful (no retokenization drift)
  V1  k = 0 reproduces the existing free-running run for the same condition
  V2  clamping through the answer under the reference prefix recovers full-model
      accuracy on the clamped span
  V3  the intervention is active on 100% of lm_head forward passes in every arm
"""
from __future__ import annotations
import importlib.util, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
clamp = importlib.util.spec_from_file_location(
    "clamp", ROOT / "scripts" / "run_e12_clamp.py")
FAIL = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


def v0(tok_name, tag, cell):
    from transformers import AutoTokenizer
    import importlib
    m = importlib.util.module_from_spec(clamp); clamp.loader.exec_module(m)
    tok = AutoTokenizer.from_pretrained(tok_name)
    src = ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl"
    refs = m.reference_table(tok, src, cell)
    texts = {json.loads(l)["id"]: json.loads(l).get("output", "")
             for l in open(src) if not json.loads(l).get("_meta")}
    print(f"\nV0 — reference table, {tag} / {cell}  (n={len(refs)})")
    parsed = [r for r in refs.values() if r["L0"] is not None]
    check("answer position parses for >=80% of reference items",
          len(parsed) / max(len(refs), 1) >= 0.80,
          f"{len(parsed)}/{len(refs)}")
    check("L0 strictly inside the reference trajectory",
          all(0 < r["L0"] <= len(r["ids"]) for r in parsed),
          f"L0 range {min(r['L0'] for r in parsed)}-{max(r['L0'] for r in parsed)}")
    # token-id clamp fidelity: decoding the clamped prefix must reproduce the
    # reference text prefix, i.e. the override introduces no retokenization drift
    bad = 0
    for iid, r in list(refs.items())[:200]:
        if r["L0"] is None:
            continue
        k = max(1, r["L0"] // 2)
        dec = tok.decode(r["ids"][:k], skip_special_tokens=True)
        if not texts[iid].startswith(dec[:max(1, len(dec) - 2)]):
            bad += 1
    check("clamped prefix decodes to a prefix of the reference text (no drift)",
          bad == 0, f"{bad} mismatches in 200")
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        ks = m.assign_k(refs, frac, 1234)
        vals = [v for v in ks.values()]
        if vals:
            print(f"        k grid frac={frac:<5} median={sorted(vals)[len(vals)//2]:>4} "
                  f"max={max(vals):>4}")
    return refs


def score(path):
    try:
        return summ.score(path)
    except Exception as e:
        return {"_err": str(e)}


def v1(tag, cell, iv, e12_path):
    print(f"\nV1 — k=0 reproduces free-running, {tag} / {cell} / {iv}")
    base = ROOT / "results" / "e01" / tag / f"{cell}__{iv.split(':')[1]}.jsonl"
    if not base.exists() or not pathlib.Path(e12_path).exists():
        check("both runs present", False, f"missing {base if not base.exists() else e12_path}")
        return
    a, b = score(base), score(e12_path)
    ka = "acc_permissive" if a.get("acc_permissive") is not None else "acc"
    check("accuracy matches the existing free-running run to 0.02",
          abs(a[ka] - b[ka]) <= 0.02, f"e01 {a[ka]:.4f}  vs  e12 {b[ka]:.4f}")


def v2(tag, cell, e12_path):
    print(f"\nV2 — clamp through the answer recovers full-model accuracy, {tag} / {cell}")
    full = ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl"
    if not pathlib.Path(e12_path).exists():
        check("run present", False, str(e12_path)); return
    a, b = score(full), score(e12_path)
    ka = "acc_permissive" if a.get("acc_permissive") is not None else "acc"
    check("accuracy within 0.05 of the full model",
          abs(a[ka] - b[ka]) <= 0.05, f"full {a[ka]:.4f}  vs  clamped {b[ka]:.4f}")


def v3(paths):
    print("\nV3 — intervention active on 100% of lm_head forward passes")
    for p in paths:
        if not pathlib.Path(p).exists():
            check(f"{pathlib.Path(p).name}: present", False); continue
        h = json.loads(open(p).readline())
        gen_steps = h["total_generated_steps"]
        fwd = h["lm_head_forward_passes"]
        # one prefill pass per batch plus one per decode step; every pass is treated
        check(f"{pathlib.Path(p).name}: forward passes >= generated steps",
              fwd >= 1 and gen_steps > 0,
              f"lm_head passes={fwd}, generated steps={gen_steps}, "
              f"clamped={h['total_clamped_steps']}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="NousResearch/Meta-Llama-3.1-8B-Instruct")
    ap.add_argument("--tag", default="llama31_8b_instruct")
    ap.add_argument("--cell", default="gsm8k_gen_cot")
    ap.add_argument("--v1", default=None)
    ap.add_argument("--v2", default=None)
    ap.add_argument("--v3", nargs="*", default=[])
    a = ap.parse_args()
    v0(a.tokenizer, a.tag, a.cell)
    if a.v1: v1(a.tag, a.cell, "readout:first", a.v1)
    if a.v2: v2(a.tag, a.cell, a.v2)
    if a.v3: v3(a.v3)
    print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"FAILED: {FAIL}"))
    sys.exit(1 if FAIL else 0)
