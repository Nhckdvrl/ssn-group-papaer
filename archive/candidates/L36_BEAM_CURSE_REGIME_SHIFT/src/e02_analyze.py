"""L36 E02 analysis — the registered statistics, computed from the online measurement stream."""
import json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "results", "e02")
CONDS = ["A_ONLY", "B_ONLY", "MIXED", "A_ONLY_NOEOSLOSS"]


def load(c):
    p = os.path.join(D, f"{c}.jsonl")
    if not os.path.exists(p):
        return None, []
    rows = [json.loads(l) for l in open(p, encoding="utf-8")]
    return rows[0], rows[1:]


def main():
    out = {}
    print("=== boundary placement: p(<END> | prefix ends exactly where the reference ends) ===")
    for c in CONDS:
        h, rows = load(c)
        if not rows:
            print(f"{c:20s} (no data)")
            continue
        print(f"\n-- {c}  ({len(rows)} checkpoints, {h['total_steps']} steps planned)")
        print(f"{'step':>6} {'loss':>9} {'p_end@end A':>12} {'p_end@end B':>12} "
              f"{'learned A':>10} {'learned B':>10} {'prem.mass A':>12} {'prem.mass B':>12}")
        for r in rows:
            b = r.get("boundary")
            if not b:
                continue
            print(f"{r['step']:6d} {r['loss']:9.2f} {b['A']['p_end_at_true_end']:12.3f} "
                  f"{b['B']['p_end_at_true_end']:12.3f} {b['A']['frac_boundary_learned']:10.2f} "
                  f"{b['B']['frac_boundary_learned']:10.2f} {b['A']['p_end_mean_before_end']:12.5f} "
                  f"{b['B']['p_end_mean_before_end']:12.5f}")
        last = rows[-1]
        out[c] = {"final_step": last["step"], "boundary": last.get("boundary"),
                  "behaviour": last.get("behaviour")}

    print("\n=== P1' (trained format only) and P2 (mixed rescues both) ===")
    ratios = {}
    for c in CONDS:
        if c not in out or not out[c]["boundary"]:
            continue
        b = out[c]["boundary"]
        pa, pb = b["A"]["p_end_at_true_end"], b["B"]["p_end_at_true_end"]
        ratios[c] = (pa, pb)
        eps = 1e-6
        print(f"{c:20s} p_end@end  A {pa:.3f}  B {pb:.3f}   ratio A/B {pa/max(pb,eps):10.1f}")
    if "A_ONLY" in ratios and "B_ONLY" in ratios:
        a_a, a_b = ratios["A_ONLY"]
        b_a, b_b = ratios["B_ONLY"]
        rev = (a_a > 10 * max(a_b, 1e-6)) and (b_b > 10 * max(b_a, 1e-6))
        print(f"\nP1' sign reversal between A_ONLY and B_ONLY: {'PASS' if rev else 'FAIL'}")
        out["P1_prime"] = bool(rev)
    if "MIXED" in ratios:
        m_a, m_b = ratios["MIXED"]
        p2 = m_a > 0.5 and m_b > 0.5
        print(f"P2 mixed learns both boundaries (>0.5 each): {'PASS' if p2 else 'FAIL'} "
              f"(A {m_a:.3f}, B {m_b:.3f})")
        out["P2"] = bool(p2)

    print("\n=== P3 behavioural readout at the final checkpoint ===")
    for c in CONDS:
        beh = out.get(c, {}).get("behaviour")
        if not beh:
            continue
        for fmt in ("A", "B"):
            cells = beh[fmt]
            print(f"{c:20s} fmt {fmt}: " + "  ".join(
                f"b{k}: BLEU {v['bleu_multi']:5.2f} empty {100*v['empty_rate']:5.1f}% "
                f"lenR {v['len_ratio']:.2f}" for k, v in sorted(cells.items(), key=lambda x: int(x[0]))))

    json.dump(out, open(os.path.join(D, "e02_summary.json"), "w"), indent=2)
    print("\nwrote results/e02/e02_summary.json")


if __name__ == "__main__":
    main()
