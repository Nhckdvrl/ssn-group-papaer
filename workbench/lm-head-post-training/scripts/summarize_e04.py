"""Compact print of results/e04/fit_*.json."""
import glob, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for p in sorted(glob.glob(str(ROOT / "results/e04/fit_*.json"))):
    if "selftest" in p:
        continue
    r = json.load(open(p))
    print(f"### {r['pair']} ({r['stage']})")
    for s, v in r["sources"].items():
        pk = v["parent"]["kl"]
        row = " | ".join(f"{k} {v[k]['kl_reduction']:+.3f} (τ {v[k]['tau']:.2f})" for k in ("tau", "bias", "tau_bias", "tau_bias_ns"))
        print(f"  {s:10s} KL0 {pk[0]:.4f} [{pk[1][0]:.4f},{pk[1][1]:.4f}] agree0 {v['parent']['top1_agree']:.3f} -> agree {v['tau_bias']['top1_agree']:.3f} | {row}")
        loc = v.get("localisation", {})
        if loc:
            print(f"     ctx-mean share {v['centred_logit_change_share_of_context_mean']:.3f} | corr(b, head ΔWμ) {loc['corr_b_head_global']:+.2f} corr(b, backbone W0Δh̄) {loc['corr_b_backbone_global']:+.2f} R² {loc['r2_b_on_head_and_backbone']:.2f} | |head| {loc['norm_head_global']:.1f} |bb| {loc['norm_backbone_global']:.1f} | μ/h {loc['mu_over_h']:.2f}")
        bs = v["b_structure"]
        print(f"     b: special share {bs['special_energy_share']:.3f} top1% {bs['top1pct_energy_share']:.3f}")
        if "-v" in sys.argv:
            print("       up  ", [t for t, _ in bs["top_up"][:18]]); print("       down", [t for t, _ in bs["top_down"][:18]])
    print("  transfer:", {k: round(x, 3) for k, x in r["transfer"].items()})
