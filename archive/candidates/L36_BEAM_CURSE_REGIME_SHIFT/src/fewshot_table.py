"""Few-shot-interface beam sweep table (same substrate, newline as the stop symbol)."""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "qwen25-7b-base"
    data = os.path.join(ROOT, "data")
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")]
    unc = [json.loads(l) for l in open(f"{data}/uncertainty.jsonl", encoding="utf-8")]
    u = np.array([r["u_char"] for r in unc]); cuts = np.quantile(u, [.25, .5, .75])
    gen = os.path.join(ROOT, "results", "ext", "gen")
    out = {}
    print(f"{'cell':40s} {'beam':>5} {'n':>4} {'BLEU':>7} {'empty%':>7} {'lenR':>6}  Q1..Q4")
    for fn in sorted(f for f in os.listdir(gen) if f.startswith(tag)):
        recs = [json.loads(l) for l in open(os.path.join(gen, fn), encoding="utf-8")]
        h, body = recs[0], sorted(recs[1:], key=lambda r: r["idx"])
        idxs = [r["idx"] for r in body]; hyps = [r["hyp"] for r in body]
        refs = [[ref_w[i], ref_a[i]] for i in idxs]
        st = np.array([M.bleu_segment_stats(x, r) for x, r in zip(hyps, refs)], float)
        lab = np.digitize(np.array([u[i] for i in idxs]), cuts, right=True)
        qs = [M.bleu_from_stats(st[lab == q].sum(0)) if (lab == q).sum() else float("nan")
              for q in range(4)]
        row = {"beam": h["beam"], "n": len(body), "bleu_multi": M.bleu_from_stats(st.sum(0)),
               "empty_rate": float(np.mean([1.0 if not x.strip() else 0.0 for x in hyps])),
               "len_ratio": float(np.mean([len(x.split()) for x in hyps]) /
                                  np.mean([len(ref_w[i].split()) for i in idxs])),
               "bleu_by_stratum": qs, "prompt_style": h.get("prompt_style")}
        out[fn] = row
        print(f"{fn[:40]:40s} {row['beam']:5d} {row['n']:4d} {row['bleu_multi']:7.2f} "
              f"{100*row['empty_rate']:7.2f} {row['len_ratio']:6.3f}  " + " ".join(f"{x:6.2f}" for x in qs))
    with open(os.path.join(ROOT, "results", "ext", f"fewshot_table_{tag}.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
