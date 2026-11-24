#!/usr/bin/env python3
"""E219 summary: per model, per component, the dNLL profile over layers; card readouts:
early route (sum over layers 0-2 per component, ratio of largest to the rest), first layer with dNLL >= .05 per component,
far/near ratio (W = 32 tertiles) summed over layers, word-internal vs word-initial.
Usage: e219_summary.py OUT219_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

ORDER = ["H", "T", "GH", "GT", "QH", "QT", "Llamba", "L1B", "FH3", "FM"]


def load(d, name):
    if name == "FM":
        parts = [d / "FM_a.json", d / "FM_b.json"]
        if not all(p.exists() for p in parts):
            return None
        a, b = (json.loads(p.read_text()) for p in parts)
        a["runs"] = a.get("runs", []) + b.get("runs", [])
        return a
    p = d / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def main():
    d = Path(sys.argv[1]); out = {}
    for name in ORDER:
        r = load(d, name)
        if r is None or "runs" not in r:
            continue
        L = r["n_layers"]; comps = sorted({x["comp"] for x in r["runs"]})
        prof = {c: [None] * L for c in comps}; rows = {c: {} for c in comps}
        for x in r["runs"]:
            prof[x["comp"]][x["layer"]] = x["dnll"]; rows[x["comp"]][x["layer"]] = x
        early = {c: sum(v for v in prof[c][:3] if v is not None) for c in comps}
        top = max(early, key=early.get); rest = sum(v for c, v in early.items() if c != top)
        first = {c: next((l for l, v in enumerate(prof[c]) if v is not None and v >= .05), None) for c in comps}
        total = {c: sum(v for v in prof[c] if v is not None) for c in comps}
        far_near = {}
        for c in comps:
            near = sum(x["dnll_w32"][0] for x in rows[c].values()); far = sum(x["dnll_w32"][2] for x in rows[c].values())
            far_near[c] = {"near": near, "far": far}
        out[name] = {"n_layers": L, "nll_base": r["nll_base"], "conv_mode": r.get("conv_mode"), "attn_layers": r.get("attn_layers"),
                     "early_sum": early, "early_top": top, "early_ratio": early[top] / rest if rest > 1e-9 else None,
                     "first_layer_ge_05": first, "total": total, "far_near_w32": far_near, "profile": prof,
                     "restore_check": r.get("restore_check_max_abs")}
        print(f"== {name}: L={L} base {r['nll_base']:.3f} conv_mode={r.get('conv_mode')} restore={r.get('restore_check_max_abs')}")
        print("   early(L0-2): " + " ".join(f"{c}={early[c]:+.3f}" for c in comps) +
              f"  top={top} ratio={out[name]['early_ratio'] if out[name]['early_ratio'] is None else round(out[name]['early_ratio'], 1)}")
        print("   first>=.05: " + " ".join(f"{c}={first[c]}" for c in comps) + "  | total: " + " ".join(f"{c}={total[c]:+.2f}" for c in comps))
        print("   far/near(w32 sums): " + " ".join(f"{c}={far_near[c]['far']:+.2f}/{far_near[c]['near']:+.2f}" for c in comps))
        for c in comps:
            print(f"   {c:4s} " + " ".join("  .  " if v is None else f"{v:+.2f}" for v in prof[c]))
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
