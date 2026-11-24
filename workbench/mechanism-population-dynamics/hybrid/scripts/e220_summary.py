#!/usr/bin/env python3
"""E220 summary: block / all-layer dNLL next to the sum of E219 single-layer dNLLs in the same layers (redundancy ratio).
Usage: e220_summary.py OUT220_DIR E219_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

ORDER = ["H", "T", "GH", "GT", "QH", "QT", "Llamba", "L1B", "FH3", "FM"]


def load(d, name):
    if name == "FM":
        ps = [d / "FM_a.json", d / "FM_b.json"]
        if not all(p.exists() for p in ps):
            return None
        a, b = (json.loads(p.read_text()) for p in ps)
        a["runs"] = a.get("runs", []) + b.get("runs", [])
        return a
    p = d / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def main():
    d220, d219, out = Path(sys.argv[1]), Path(sys.argv[2]), {}
    for name in ORDER:
        r, s = load(d220, name), load(d219, name)
        if r is None or s is None or "runs" not in r:
            continue
        single = {(x["comp"], x["layer"]): x["dnll"] for x in s["runs"]}
        rows = []
        for x in r["runs"]:
            ssum = sum(single.get((x["comp"], l), 0.0) for l in x["layers"])
            rows.append({"group": x["group"], "comp": x["comp"], "n_mod": x["n_mod"], "dnll": x["dnll"], "single_sum": ssum,
                         "ratio": x["dnll"] / ssum if ssum > 0.01 else None, "dnll_internal": x["dnll_internal"],
                         "dnll_initial": x["dnll_initial"], "dnll_w32": x["dnll_w32"], "dnll_w128": x["dnll_w128"]})
        out[name] = {"nll_base": r["nll_base"], "rows": rows, "restore_check": r.get("restore_check_max_abs")}
        print(f"== {name} base {r['nll_base']:.3f} restore {r.get('restore_check_max_abs')}")
        for c in ("conv", "mem", "attn"):
            rc = [x for x in rows if x["comp"] == c]
            if not rc:
                continue
            blocks = " ".join(f"{x['group']}:{x['dnll']:+.2f}/{x['single_sum']:+.2f}" for x in rc if x["group"] != "ALL")
            al = [x for x in rc if x["group"] == "ALL"]
            tail = ""
            if al:
                a = al[0]
                tail = (f" | ALL {a['dnll']:+.2f} (singles {a['single_sum']:+.2f}) int {a['dnll_internal']:+.2f} ini {a['dnll_initial']:+.2f} "
                        f"w32 {' '.join(f'{v:+.2f}' for v in a['dnll_w32'])}")
            print(f"   {c:4s} {blocks}{tail}")
    Path(sys.argv[3]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
