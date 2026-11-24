#!/usr/bin/env python3
"""E221: apply the pre-registered readings (card E221) and print the 2x2 tables.
Usage: e221_judge.py OUT221_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

HYB = ["H", "QH", "GH", "FH3"]; OTHER = ["FM", "Llamba"]; TF = ["T", "QT"]
SCALES = ("dnll", "dtop1", "dp")


def R(c, cond, s, num="internal", den="initial"):
    a, b = c[cond]["cells"][num][s], c[cond]["cells"][den][s]
    return a / b if abs(b) > 1e-9 else None


def main():
    d = Path(sys.argv[1]); M = {}
    for n in HYB + OTHER + TF:
        p = d / f"{n}.json"
        if p.exists():
            M[n] = json.loads(p.read_text())
    out = {"ratios": {}, "readings": {}}
    for n, r in M.items():
        b = r["base"]
        print(f"== {n} restore {r.get('restore_check_max_abs')}  base NLL ini {b['initial']['base_nll']:.2f} int {b['internal']['base_nll']:.2f} | "
              f"top1 ini {b['initial']['base_top1']:.2f} int {b['internal']['base_top1']:.2f} | n int_rep {b['internal_rep']['n']} int_first {b['internal_first']['n']} "
              f"ini_rep {b['initial_rep']['n']} ini_first {b['initial_first']['n']}")
        out["ratios"][n] = {}
        for cond, cr in r["conds"].items():
            c = cr["cells"]
            rr = {s: R(r["conds"], cond, s) for s in SCALES}
            rr_same = {s: R(r["conds"], cond, s, "internal", "initial_multi") for s in SCALES}
            out["ratios"][n][cond] = {"R": rr, "R_same_word": rr_same}
            row = lambda k: f"{c[k]['dnll']:+.2f}/{c[k]['dtop1']:+.3f}/{c[k]['dp']:+.3f}"
            print(f"   {cond:8s} all {c['all']['dnll']:+.2f} | ini_rep {row('initial_rep')} ini_first {row('initial_first')} | "
                  f"int_rep {row('internal_rep')} int_first {row('internal_first')} | R(nll/top1/p) "
                  + "/".join("na" if v is None else f"{v:.2f}" for v in rr.values())
                  + " | R_same " + "/".join("na" if v is None else f"{v:.2f}" for v in rr_same.values()))
    rd = out["readings"]
    # 1. memory spares within-word
    ok = []
    for n in HYB:
        if n not in M:
            continue
        rt = out["ratios"][n]
        cond_ok = all(rt["ALL_mem"]["R"][s] < 1 and rt["ALL_attn"]["R"][s] > 1 and rt["ALL_conv"]["R"][s] > 1 for s in ("dnll", "dtop1"))
        ok.append((n, cond_ok))
    rd["memory_spares_within_word"] = {"per_model": dict(ok), "met": sum(v for _, v in ok) >= 3}
    # 2. generic within > initial
    rs = [out["ratios"][n][c]["R"]["dnll"] for n in HYB if n in M for c in ("ALL_attn", "ALL_conv")] + \
         [out["ratios"][n]["ALL_attn"]["R"]["dnll"] for n in TF if n in M]
    rd["generic_within_gt_initial"] = {"R_dnll": rs, "met": all(x > 1 for x in rs) and max(rs) / min(rs) < 2}
    # 3. attention mainly copies / 4. beyond copying (hybrids, ALL_attn)
    cp, bc = {}, {}
    for n in HYB:
        if n not in M:
            continue
        c = M[n]["conds"]["ALL_attn"]["cells"]
        cp[n] = c["internal_rep"]["dnll"] >= 2 * c["internal_first"]["dnll"] and c["internal_rep"]["dtop1"] > c["internal_first"]["dtop1"]
        bc[n] = all(c["internal_first"][s] >= 1.5 * c["initial_first"][s] for s in ("dnll", "dtop1"))
    rd["attention_mainly_copies"] = cp; rd["beyond_copying"] = bc
    # 5. early cliff
    cl = {}
    for n in HYB + OTHER:
        if n in M and "B0_all" in M[n]["conds"]:
            a, b = M[n]["conds"]["B0_all"]["cells"]["all"]["dnll"], M[n]["conds"]["ALL_all"]["cells"]["all"]["dnll"]
            cl[n] = {"B0_all": a, "ALL_all": b, "ratio": a / b, "mark": "cliff" if a / b >= .8 else ("recover" if a / b <= .5 else "middle")}
    rd["early_cliff"] = cl
    print(json.dumps(rd, indent=1, ensure_ascii=False))
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
