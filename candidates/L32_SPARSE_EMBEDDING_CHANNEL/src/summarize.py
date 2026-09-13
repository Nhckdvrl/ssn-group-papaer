"""Paired bootstrap over Flores sentences, with training seed as a second level.

Every arm is decoded on the SAME 1012 sentences, so contrasts are paired: one
bootstrap draw resamples sentences once and applies that draw to every arm.
Seeds are resampled alongside, so the reported interval covers both evaluation
noise and training-seed variance -- the decomposition L30 showed is necessary
before believing any "the effect is small" reading.

spBLEU is a corpus metric, so a bootstrap replicate recomputes the corpus score
on the resampled sentences rather than averaging sentence scores. Per-sentence
n-gram sufficient statistics are extracted once and a replicate just sums the
resampled count vectors, which is what makes 2000 draws x 8 arms affordable.
"""
import argparse
import json
import pathlib
import random
import sys
from collections import defaultdict

sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, read_jsonl  # noqa: E402

ORDER = ["BASE", "ALL", "PREFILL", "INSTRUCTION", "INSTR_HEAD", "INSTR_TAIL",
         "SOURCE", "TARGET"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evals", default=str(ROOT / "results" / "evals"))
    ap.add_argument("--tags", default="s0,s1,s2")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--scoring", default="raw", choices=["raw", "trunc"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from sacrebleu.metrics import BLEU
    bleu = BLEU(tokenize="flores101")
    refs = [r["ref"] for r in read_jsonl(ROOT / "data" / "devtest_en_ca.jsonl")]

    ev = pathlib.Path(args.evals)
    tags = args.tags.split(",")
    hyps = defaultdict(dict)   # arm -> tag -> list[str]
    stats = defaultdict(dict)  # arm -> tag -> list[per-sentence count vector]
    point = defaultdict(dict)
    meta = defaultdict(dict)
    for t in tags:
        for arm in ORDER:
            p = ev / f"{t}__{arm}.json"
            if not p.exists():
                continue
            d = json.loads(p.read_text())
            h = d["hyps_trunc" if args.scoring == "trunc" else "hyps_raw"]
            hyps[arm][t] = h
            stats[arm][t] = bleu._extract_corpus_statistics(h, [refs])
            point[arm][t] = d[f"spbleu_{args.scoring}"]
            meta[arm][t] = {"stop": d["frac_stopped"], "chars": d["mean_raw_chars"],
                            "nll": sum(x["nll"] for x in d["forced"]) / len(d["forced"])
                            if d["forced"] else None}

    arms = [a for a in ORDER if a in hyps]
    rng = random.Random(20260913)
    n = len(refs)
    nstat = len(next(iter(stats[arms[0]].values()))[0])
    draws = defaultdict(list)
    for _ in range(args.n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        for arm in arms:
            ts = list(stats[arm])
            pick = [ts[rng.randrange(len(ts))] for _ in ts]  # resample seeds
            vals = []
            for t in pick:
                st = stats[arm][t]
                acc = [0] * nstat
                for i in idx:
                    row = st[i]
                    for j in range(nstat):
                        acc[j] += row[j]
                vals.append(bleu._compute_score_from_stats(acc).score)
            draws[arm].append(sum(vals) / len(vals))

    def ci(v):
        v = sorted(v)
        return v[int(0.025 * len(v))], v[int(0.975 * len(v))]

    out = {"scoring": args.scoring, "tags": tags, "n_boot": args.n_boot, "arms": {}}
    for arm in arms:
        lo, hi = ci(draws[arm])
        out["arms"][arm] = {
            "mean": sum(point[arm].values()) / len(point[arm]),
            "per_seed": point[arm], "ci": [lo, hi], "meta": meta[arm],
        }
    base = draws["BASE"]
    d_all = [a - b for a, b in zip(draws["ALL"], base)]
    out["contrasts"] = {}
    for arm in arms:
        if arm == "BASE":
            continue
        d = [a - b for a, b in zip(draws[arm], base)]
        lo, hi = ci(d)
        rec = {"delta": sum(d) / len(d), "ci": [lo, hi]}
        if arm != "ALL":
            r = [x / y for x, y in zip(d, d_all) if abs(y) > 1e-6]
            rlo, rhi = ci(r)
            rec["recovery"] = sum(r) / len(r)
            rec["recovery_ci"] = [rlo, rhi]
        out["contrasts"][arm] = rec

    p = args.out or str(ROOT / "results" / f"E01_summary_{args.scoring}.json")
    pathlib.Path(p).write_text(json.dumps(out, indent=2))

    print(f"=== scoring={args.scoring}  seeds={tags}  n_boot={args.n_boot} ===")
    print(f"{'arm':<12}{'spBLEU':>8}{'95% CI':>18}{'stop':>7}{'chars':>7}  per-seed")
    for arm in arms:
        a = out["arms"][arm]
        st = sum(m["stop"] for m in a["meta"].values()) / len(a["meta"])
        ch = sum(m["chars"] for m in a["meta"].values()) / len(a["meta"])
        ps = " ".join(f"{v:.2f}" for v in a["per_seed"].values())
        print(f"{arm:<12}{a['mean']:8.2f}  [{a['ci'][0]:6.2f},{a['ci'][1]:6.2f}]"
              f"{st:7.2f}{ch:7.0f}  {ps}")
    print(f"\n{'contrast':<12}{'delta':>8}{'95% CI':>18}{'recovery':>10}{'CI':>18}")
    for arm, c in out["contrasts"].items():
        r = (f"{c['recovery']:10.2f}  [{c['recovery_ci'][0]:5.2f},{c['recovery_ci'][1]:5.2f}]"
             if "recovery" in c else "")
        print(f"{arm+'-BASE':<12}{c['delta']:8.2f}  [{c['ci'][0]:6.2f},{c['ci'][1]:6.2f}]{r}")


if __name__ == "__main__":
    main()
