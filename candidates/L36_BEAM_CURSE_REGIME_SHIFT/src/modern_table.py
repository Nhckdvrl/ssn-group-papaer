"""Descriptive table for the modern arm (and any cell set), on a common segment subset."""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M

def load(p):
    rows = [json.loads(l) for l in open(p, encoding="utf-8")]
    return rows[0], sorted(rows[1:], key=lambda r: r["idx"])

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "gemma3-12b"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    data = os.path.join(ROOT, "data")
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    gen_dir = os.path.join(ROOT, "results", "ext", "gen")
    files = sorted(f for f in os.listdir(gen_dir) if f.startswith(tag))
    print(f"{'cell':34s} {'n':>5} {'BLEUm':>7} {'chrF2':>7} {'lenRatio':>9} {'empty%':>7} {'trunc%':>7}  Q1..Q4 BLEU")
    out = {}
    for fn in files:
        h, rows = load(os.path.join(gen_dir, fn))
        if limit:
            rows = [r for r in rows if r["idx"] < limit]
        idxs = [r["idx"] for r in rows]
        hyps = [r["hyp"] for r in rows]
        refs = [[ref_w[i], ref_a[i]] for i in idxs]
        st = np.array([M.bleu_segment_stats(x, r) for x, r in zip(hyps, refs)], float)
        ch = np.array([M.chrf_segment_stats(x, r) for x, r in zip(hyps, refs)], float)
        u = np.array([unc[i]["u_char"] for i in idxs])
        cuts = np.quantile([r["u_char"] for r in unc], [.25, .5, .75])
        lab = np.digitize(u, cuts, right=True)
        qs = []
        for q in range(4):
            sel = np.where(lab == q)[0]
            qs.append(M.bleu_from_stats(st[sel].sum(0)) if len(sel) else float("nan"))
        lr = np.mean([len(x.split()) for x in hyps]) / np.mean([len(ref_w[i].split()) for i in idxs])
        empty = np.mean([1.0 if not x.strip() else 0.0 for x in hyps])
        trunc = np.mean([float(r["truncated"]) for r in rows]) if "truncated" in rows[0] else float("nan")
        row = {"n": len(rows), "bleu_multi": M.bleu_from_stats(st.sum(0)),
               "chrf2": M.chrf_from_stats(ch.sum(0)), "len_ratio": float(lr),
               "empty_rate": float(empty), "truncation_rate": float(trunc),
               "bleu_by_stratum": qs, "beam": h.get("beam"), "semantics": h.get("semantics"),
               "eos_bias": h.get("eos_bias", 0)}
        out[fn] = row
        print(f"{fn[:34]:34s} {len(rows):5d} {row['bleu_multi']:7.2f} {row['chrf2']:7.2f} "
              f"{lr:9.3f} {100*empty:7.2f} {100*trunc:7.2f}  " + " ".join(f"{x:6.2f}" for x in qs))
    with open(os.path.join(ROOT, "results", "ext", f"modern_table_{tag}{'_first'+str(limit) if limit else ''}.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
