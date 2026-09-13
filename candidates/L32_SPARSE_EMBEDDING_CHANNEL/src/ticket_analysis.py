"""What does the certified ticket actually track?

Two questions, both of which the parent's framing leaves open:

1. **Language or template?** The parent reports cross-language ticket overlap and
   reads it as a shared multilingual subspace, but every language in that
   comparison shares one English prompt. Comparing ca/explicit vs ca/paraphrase
   (same language and data, different template) against ca/explicit vs
   es|de/explicit (same template, different language and data) breaks that.

2. **Anything beyond token frequency?** Each row's update accumulates once per
   occurrence, so a row's shift may be little more than a count. If the ranking
   is essentially the training-token frequency ranking, the certification adds
   nothing over counting -- which the parent's own Frequency Tuning baseline
   (28.8 vs 27.9 for Embed Tuning) already hints at.

Rows are ranked by shift norm, not by KS p-value: in our reproduction only 4-5
rows clear p<0.05, so any p-based ranking below that is noise.
"""
import itertools
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, SEL_IDS  # noqa: E402

TAGS = ["ca_explicit", "ca_explicit_seed1", "ca_paraphrase",
        "es_explicit", "es_paraphrase", "de_explicit"]

# The comparison that makes the rest readable. Without the seed replicate there
# is no noise floor, and an overlap of 76/100 means nothing on its own.
CONTRASTS = [
    ("noise floor (same data, template, seed differs)", "ca_explicit", "ca_explicit_seed1"),
    ("template differs, language+data fixed", "ca_explicit", "ca_paraphrase"),
    ("template differs, language+data fixed", "es_explicit", "es_paraphrase"),
    ("language+data differ, template fixed", "ca_explicit", "es_explicit"),
    ("language+data differ, template fixed", "ca_explicit", "de_explicit"),
    ("language+data differ, template fixed", "ca_paraphrase", "es_paraphrase"),
]
KS = [18, 50, 100, 500]


def main():
    from transformers import AutoTokenizer
    from scipy import stats
    from ks_select import build_pool
    tok = AutoTokenizer.from_pretrained((ROOT / ".modelpath").read_text().strip(),
                                        use_fast=True)

    d = {t: json.loads((ROOT / "results" / f"ks_select_{t}.json").read_text())
         for t in TAGS if (ROOT / "results" / f"ks_select_{t}.json").exists()}
    out = {"ranking": "shift_norm", "overlaps": {}, "tickets": {},
           "freq_correlation": {}, "template_rows": {}}

    rank, freq = {}, {}
    for t, v in d.items():
        sh = v["shift_all"]
        rank[t] = sorted(range(len(sh)), key=lambda i: -sh[i])
        rows = build_pool(tok, v["lang"], v["head"], v["tail"], 10000, 1732)
        c = Counter()
        for x, y in rows:
            c.update(x)
            c.update(y)
        freq[t] = c
        # how much of the shift ranking is just "this token occurred a lot"?
        ids = [i for i in range(len(sh)) if c[i] > 0]
        r = stats.spearmanr([sh[i] for i in ids], [c[i] for i in ids])
        out["freq_correlation"][t] = {
            "spearman_shift_vs_count": float(r.statistic),
            "n_tokens_seen": len(ids),
            "top18_by_count": [tok.decode([i]) for i, _ in c.most_common(18)],
            "top18_by_shift_also_in_top18_by_count":
                len(set(rank[t][:18]) & {i for i, _ in c.most_common(18)}),
        }
        out["tickets"][t] = [[i, tok.decode([i]), sh[i], c[i]] for i in rank[t][:18]]
        # rows that occur in this condition's template at all
        tpl = set(tok.encode(v["head"], add_special_tokens=False)) | \
            set(tok.encode(v["tail"], add_special_tokens=False))
        out["template_rows"][t] = {
            "n_template_tokens": len(tpl),
            "in_top18": sorted(set(rank[t][:18]) & tpl),
            "in_top18_str": [tok.decode([i]) for i in sorted(set(rank[t][:18]) & tpl)],
        }
        out["overlaps"][f"{t}__vs__published18"] = len(set(SEL_IDS) & set(rank[t][:18]))

    for a, b in itertools.combinations(d, 2):
        rec = {}
        for k in KS:
            A, B = set(rank[a][:k]), set(rank[b][:k])
            rec[f"k{k}"] = {"overlap": len(A & B), "jaccard": len(A & B) / len(A | B)}
        out["overlaps"][f"{a}__vs__{b}"] = rec

    (ROOT / "results" / "ticket_analysis.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))

    print("top-18 by shift norm:")
    for t, v in out["tickets"].items():
        print(f"  {t:<16} {[x[1] for x in v]}")
    print("\nis the ticket just token frequency?")
    for t, v in out["freq_correlation"].items():
        print(f"  {t:<16} spearman(shift, count) = {v['spearman_shift_vs_count']:.3f}"
              f"   top18-by-shift also top18-by-count: "
              f"{v['top18_by_shift_also_in_top18_by_count']}/18")
    print("\ntemplate tokens inside the top-18 ticket:")
    for t, v in out["template_rows"].items():
        print(f"  {t:<16} {v['in_top18_str']}")
    print("\noverlap with the paper's published en->ca 18:")
    for t in d:
        print(f"  {t:<16} {out['overlaps'][f'{t}__vs__published18']}/18")
    print(f"\n{'pair':<36}" + "".join(f"{'k'+str(k):>12}" for k in KS))
    for a, b in itertools.combinations(d, 2):
        r = out["overlaps"][f"{a}__vs__{b}"]
        print(f"{a+' vs '+b:<36}" + "".join(
            f"{r[f'k{k}']['overlap']:>7}/{r[f'k{k}']['jaccard']:.2f}" for k in KS))

    print(f"\n{'contrast':<46}{'pair':<34}" + "".join(f"{'k'+str(k):>12}" for k in KS))
    for label, a, b in CONTRASTS:
        if a not in d or b not in d:
            continue
        key = f"{a}__vs__{b}" if f"{a}__vs__{b}" in out["overlaps"] else f"{b}__vs__{a}"
        r = out["overlaps"][key]
        print(f"{label:<46}{a+' vs '+b:<34}" + "".join(
            f"{r[f'k{k}']['overlap']:>7}/{r[f'k{k}']['jaccard']:.2f}" for k in KS))


if __name__ == "__main__":
    main()
