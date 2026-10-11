"""S03 / Phase 1 — read the fixed-token natural trajectory.

Refuses to print a curve whose checkpoints did not see byte-identical inputs:
every run records `input_fp`, a fingerprint of the exact token ids, the scored
stop id and the named-token set, so a serialization or stop-set drift is a hard
error instead of a silent confound.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_rawlogit import rows_of, mean, boot_ci, sign_test
from e01_traj import TABLE, OUT

POS = "p2"
DIR = OUT


def load(label):
    p = f"{DIR}/{label}.jsonl"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else None


def main():
    global DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="main")
    a = ap.parse_args()
    DIR = OUT if a.variant == "main" else f"{OUT}/{a.variant}"
    print(f"variant: {a.variant}  ({DIR})")
    pts = []
    for lab, repo, rev, stage, ordinal in sorted(TABLE, key=lambda t: t[4]):
        raw = load(lab)
        if raw is None:
            continue
        pts.append((ordinal, lab, stage, raw, rows_of([f"{DIR}/{lab}.jsonl"], POS)))

    curve = [p for p in pts if not p[1].endswith("_native")]
    # --- stimulus invariance, asserted, not assumed -----------------------
    # keyed by row index, not item_id: three item_ids collide in the stimulus
    # file (A_the_planets_of_the_2/_3, B_Earth_2 each name two distinct items).
    # Every analysis in this repo keys by row order, so nothing is affected, but
    # the labels are not unique and must be made so in E01-v2.
    ref = [r["input_fp"] for r in curve[0][3]]
    for _, lab, _, raw, _ in curve:
        assert len(raw) == len(ref), f"{lab} has {len(raw)} rows, expected {len(ref)}"
        bad = [i for i, r in enumerate(raw) if ref[i] != r["input_fp"]]
        assert not bad, (f"{lab} saw different inputs than {curve[0][1]} on "
                         f"{len(bad)} items, e.g. {bad[:3]} — the curve would "
                         f"not be longitudinal")
    print(f"stimulus invariance OK: {len(curve)} checkpoints, {len(ref)} items, "
          f"identical token ids and identical scored stop id "
          f"(fingerprint {curve[0][3][0]['input_fp']})\n")

    hdr = (f"{'checkpoint':<24}{'stage':<12}{'n':>4}{'d_goal':>9}{'dz_stop':>9}"
           f"{'dz_cont':>9}{'sign':>8}{'cont@1':>8}{'contMdR':>9}")
    print(hdr); print("-" * len(hdr))
    prev = None
    for ordinal, lab, stage, raw, d in pts:
        if prev and prev != stage and not lab.endswith("_native"):
            print()
        prev = stage
        g = [r["d_goal"] for r in d.values()]
        _, a, b = sign_test(g)
        # continuation awareness in the INCOMPLETE condition: does the model
        # still know what the correct missing content is?
        rk = sorted(r[f"inc_{POS}_comp_rank"] for r in raw)
        top1 = 100 * sum(1 for x in rk if x == 0) / len(rk)
        print(f"{lab:<24}{stage:<12}{len(g):>4}{mean(g):>9.2f}"
              f"{mean([r['dz_stop'] for r in d.values()]):>9.2f}"
              f"{mean([r['dz_cont'] for r in d.values()]):>9.2f}"
              f"{f'{a}/{b}':>8}{top1:>7.0f}%{rk[len(rk) // 2]:>9}")

    # --- stage-to-stage paired contrasts ----------------------------------
    ends = [p for p in curve if p[1].endswith(("base", "_final"))]
    print(f"\npaired stage transitions (same 50 items, same stop token)\n")
    hdr = (f"  {'transition':<34}{'D d_goal':>10}{'95% CI':>18}{'sign':>8}"
           f"{'D dz_stop':>11}{'D dz_cont':>11}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for (o0, l0, _, _, d0), (o1, l1, _, _, d1) in zip(ends, ends[1:]):
        ks = sorted(set(d0) & set(d1))
        out = []
        for m in ("d_goal", "dz_stop", "dz_cont"):
            v = [d1[k][m] - d0[k][m] for k in ks]
            out.append((mean(v), *boot_ci(v), sign_test(v)))
        (g, gl, gh, (_, ga, gb)), (s, *_), (c, *_) = out
        print(f"  {l0 + ' -> ' + l1:<34}{g:>10.2f}"
              f"{f'[{gl:+.2f},{gh:+.2f}]':>18}{f'{ga}/{gb}':>8}"
              f"{s:>11.2f}{c:>11.2f}")

    # --- per-stimulus-family breakdown at the stage endpoints -------------
    print(f"\nper-family d_goal at the stage endpoints\n")
    fams = sorted({r["family"] for r in curve[0][3]})
    print(f"  {'checkpoint':<24}" + "".join(f"{f.split('_')[0]:>9}" for f in fams))
    print("  " + "-" * (24 + 9 * len(fams)))
    for _, lab, _, _, d in ends:
        cells = []
        for f in fams:
            v = [r["d_goal"] for r in d.values() if r["family"] == f]
            cells.append(f"{mean(v):>9.2f}")
        print(f"  {lab:<24}" + "".join(cells))

    nat = [p for p in pts if p[1].endswith("_native")]
    if nat:
        print(f"\nformat control (NOT on the curve): Think-SFT in its own "
              f"native thinking template\n")
        for _, lab, _, _, d in nat:
            print(f"  {lab:<30}d_goal {mean([r['d_goal'] for r in d.values()]):>7.2f}"
                  f"  dz_stop {mean([r['dz_stop'] for r in d.values()]):>7.2f}"
                  f"  dz_cont {mean([r['dz_cont'] for r in d.values()]):>7.2f}")


if __name__ == "__main__":
    main()
