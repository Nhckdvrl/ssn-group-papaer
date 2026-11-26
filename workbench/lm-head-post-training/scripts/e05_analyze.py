"""E05 analysis: is the post-trained model's re-ranking at forks aligned with the parent's soft value?
Reads /tmp/xiang_lmhead/e05/rollouts_<pair>.jsonl, writes results/e05/fork_value_<pair>.json.
Usage: python e05_analyze.py <pair_key>"""
import json
import math
import random
import sys
from pathlib import Path

import models

ROOT = Path(__file__).resolve().parents[1]


def boot_by_prompt(items, key, n=2000, seed=0):
    by = {}
    for it in items:
        by.setdefault(it["prompt_index"], []).append(key(it))
    means = [sum(v) / len(v) for v in by.values()]
    rng = random.Random(seed)
    bs = sorted(sum(means[rng.randrange(len(means))] for _ in means) / len(means) for _ in range(n))
    return {"mean_over_prompts": sum(means) / len(means), "ci95": [bs[int(0.025 * n)], bs[int(0.975 * n)]],
            "mean_over_forks": sum(key(it) for it in items) / len(items), "n_forks": len(items), "n_prompts": len(means)}


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx > 0 and sy > 0 else float("nan")


def main():
    pair = sys.argv[1]
    rows = [json.loads(l) for l in open(f"/tmp/xiang_lmhead/e05/rollouts_{pair}.jsonl")]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(models.PAIRS[pair][1]))
    dec = lambda i: tok.convert_ids_to_tokens(int(i))
    agree = [r for r in rows if r["kind"] == "agree" and "base_rep" in r["cands"]]
    ch = [r for r in rows if r["kind"] == "changed" and "post" in r["cands"] and "base" in r["cands"]]
    res = {"pair": pair, "n_agree": len(agree), "n_changed": len(ch)}
    res["noise_floor_abs_dv_agree"] = sum(abs(r["cands"]["base"]["v"] - r["cands"]["base_rep"]["v"]) for r in agree) / max(1, len(agree))
    res["agree_v"] = boot_by_prompt(agree, lambda r: r["cands"]["base"]["v"]) if agree else None
    res["changed_v_base"] = boot_by_prompt(ch, lambda r: r["cands"]["base"]["v"])
    res["changed_v_post"] = boot_by_prompt(ch, lambda r: r["cands"]["post"]["v"])
    res["dv_post_minus_base"] = boot_by_prompt(ch, lambda r: r["cands"]["post"]["v"] - r["cands"]["base"]["v"])
    res["dell_post_minus_base"] = boot_by_prompt(ch, lambda r: r["cands"]["post"]["ell"] - r["cands"]["base"]["ell"])
    with_alt = [r for r in ch if "alt" in r["cands"]]
    if with_alt:
        res["dv_alt_minus_base"] = boot_by_prompt(with_alt, lambda r: r["cands"]["alt"]["v"] - r["cands"]["base"]["v"])
        res["dv_post_minus_alt"] = boot_by_prompt(with_alt, lambda r: r["cands"]["post"]["v"] - r["cands"]["alt"]["v"])
    res["frac_post_better"] = sum(r["cands"]["post"]["v"] > r["cands"]["base"]["v"] for r in ch) / len(ch)
    res["frac_post_worse"] = sum(r["cands"]["post"]["v"] < r["cands"]["base"]["v"] for r in ch) / len(ch)
    # soft-value alignment: child's relative logit change vs log value ratio (only where both lp known)
    xs, ys, ys2 = [], [], []
    for r in ch:
        cb, cp = str(r["c_base"]), str(r["c_post"])
        l0, l1 = r["lp0"], r["lp1"]
        if None in (l0.get(cb), l0.get(cp), l1.get(cb), l1.get(cp)):
            continue
        xs.append((l1[cp] - l0[cp]) - (l1[cb] - l0[cb]))
        vb, vp = r["cands"]["base"]["v"], r["cands"]["post"]["v"]
        ys.append(math.log((vp + 0.0625) / (vb + 0.0625))); ys2.append(vp - vb)
    res["corr_dlogit_vs_logvalue_ratio"] = pearson(xs, ys) if xs else None
    res["corr_dlogit_vs_dv"] = pearson(xs, ys2) if xs else None
    res["n_corr"] = len(xs)
    # token-type strata on the child's choice
    reflect = {"Wait", "ĠWait", "Hmm", "ĠHmm", "Therefore", "ĠTherefore", "Ġno", "No", "ĠNo", "Ġperhaps", "Alternatively", "ĠAlternatively", "Ġactually", "ĠActually"}
    for name, pred in [("child_choice_reflective", lambda r: dec(r["c_post"]) in reflect),
                       ("child_choice_other", lambda r: dec(r["c_post"]) not in reflect)]:
        sub = [r for r in ch if pred(r)]
        if len(sub) >= 10:
            res[f"dv_{name}"] = boot_by_prompt(sub, lambda r: r["cands"]["post"]["v"] - r["cands"]["base"]["v"])
    res["examples"] = [(dec(r["c_base"]), dec(r["c_post"]), round(r["cands"]["base"]["v"], 3), round(r["cands"]["post"]["v"], 3)) for r in ch[:40]]
    res["trunc_rate"] = sum(c["trunc"] for r in rows for c in r["cands"].values()) / sum(len(r["cands"]) for r in rows)
    out = ROOT / "results" / "e05"; out.mkdir(parents=True, exist_ok=True)
    (out / f"fork_value_{pair}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "examples"}, indent=1))
    print(res["examples"][:20])


if __name__ == "__main__":
    main()
