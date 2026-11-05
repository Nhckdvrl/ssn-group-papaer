#!/usr/bin/env python3
"""E177 small-scale point: same readouts as E173 (scripts/e173_compare.py, unchanged functions; last layer and
deep half chosen from each model's layer count) for the 6-layer d512 pairs, next to the 12-layer references.
Writes results/e177/{routing.json, functional_route.json, decomp_800000000.json, summary.json, table.md, ratio.md}.
Usage: e177_compare.py [--skip-routing] [--skip-decomp]
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import e173_compare as m  # noqa: E402

m.OUT = m.WB / "results/e177"
m.OUT.mkdir(parents=True, exist_ok=True)
src = m.WB / "results/e173/baseline15_routing_100000000.json"   # 12-layer 15-pair ruler at 1e8 (already computed)
if not (m.OUT / src.name).exists():
    shutil.copy(src, m.OUT / src.name)
m.RECIPES = {
    "base": ("I0D0", "I1D0", "12 层 只换初始化 I0D0–I1D0"),
    "rerun12_I4": ("I4D0", "I4D0R", "12 层 重跑 I4D0–I4D0R"),
    "rerun12_I0": ("I0D0", "BASE_I0", "12 层 重跑 I0D0–BASE_I0"),
    "s6_init": ("S6_I0", "S6_I1", "6 层 只换初始化 S6_I0–S6_I1"),
    "s6_rerun": ("S6_I0", "S6_I0R", "6 层 重跑 S6_I0–S6_I0R"),
}
m.main()
S = json.loads((m.OUT / "summary.json").read_text())["recipes"]
END = str(m.END)


def get(name, key):
    r = S.get(name, {}).get("routing", {}).get(END)
    return None if r is None else r[key]


rows = [("12 层（L11 / 深层 L6–11）", "base", ["rerun12_I4", "rerun12_I0"]), ("6 层（L5 / 深层 L3–5）", "s6_init", ["s6_rerun"])]
f3 = lambda x: "—" if x is None else f"{x:.3f}"
lines = ["| 尺度 | 重跑对 | init 对 最后层 / 深层 | 重跑对 最后层 / 深层 | init÷重跑 最后层 / 深层 |", "|---|---|---|---|---|"]
for label, init, reruns in rows:
    for rr in reruns:
        i_l, i_d, r_l, r_d = get(init, "L11"), get(init, "deep"), get(rr, "L11"), get(rr, "deep")
        ratio = lambda a, b: "—" if a is None or b is None else f"{a / b:.2f}"
        lines.append(f"| {label} | {m.RECIPES[rr][2]} | {f3(i_l)} / {f3(i_d)} | {f3(r_l)} / {f3(r_d)} | {ratio(i_l, r_l)} / {ratio(i_d, r_d)} |")
(m.OUT / "ratio.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
