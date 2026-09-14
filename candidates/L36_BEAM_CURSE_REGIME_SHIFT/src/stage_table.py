"""Assemble the stage-wise lineage table and test the rank-onset prediction.

The onset prediction: HuggingFace beam search considers the top `2b` tokens at the first step, so
the stop hypothesis can only enter the beam once `2b >= rank_stop`. The predicted onset beam is
therefore `b* = ceil(rank_stop / 2)`, and the curse should be absent for `b << b*` and present for
`b >= b*`.
"""
import json, math, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SD = os.path.join(ROOT, "results", "stages")


def main():
    rows = []
    for fn in sorted(os.listdir(SD)):
        if not fn.endswith(".json") or fn.startswith("margin_"):
            continue
        d = json.load(open(os.path.join(SD, fn)))
        t = d["termination"]
        row = {"tag": d["tag"], "stage": d["stage"], "interface": d["interface"],
               "margin": t["margin_mean"], "log_p_stop": t["log_p_stop_mean"],
               "rank_median": t["rank_stop_median"],
               "top128": t["frac_stop_in_top128"],
               "beams": {b: {k: c[k] for k in ("bleu_multi", "empty_rate", "len_ratio")}
                         for b, c in d.get("beam", {}).items()}}
        row["b_star"] = math.ceil(row["rank_median"] / 2)
        rows.append(row)
    for fn in sorted(os.listdir(SD)):
        if not fn.startswith("margin_"):
            continue
        d = json.load(open(os.path.join(SD, fn)))
        rows.append({"tag": d["tag"], "stage": "reference", "interface": d["interface"],
                     "margin": d["margin_mean"], "log_p_stop": d["log_p_stop_mean"],
                     "rank_median": d["rank_stop_median"], "top128": d["frac_stop_in_top128"],
                     "beams": {}, "b_star": math.ceil(d["rank_stop_median"] / 2)})

    print(f"{'tag':16s} {'stage':10s} {'iface':8s} {'margin':>7} {'logp_stop':>10} "
          f"{'rank':>7} {'b*':>6} | {'BLEU@1':>7} {'BLEU@16':>8} {'BLEU@64':>8} "
          f"{'empty@64':>9}")
    for r in sorted(rows, key=lambda r: (r["interface"], r["tag"])):
        b = r["beams"]
        def g(k, f):
            return f"{b[k][f]:8.2f}" if k in b else "      --"
        e64 = f"{100*b['64']['empty_rate']:8.2f}%" if "64" in b else "        --"
        print(f"{r['tag']:16s} {r['stage']:10s} {r['interface']:8s} {r['margin']:7.2f} "
              f"{r['log_p_stop']:10.2f} {r['rank_median']:7.0f} {r['b_star']:6d} | "
              f"{g('1','bleu_multi')} {g('16','bleu_multi')} {g('64','bleu_multi')} {e64}")
    json.dump(rows, open(os.path.join(ROOT, "results", "stages", "stage_table.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
