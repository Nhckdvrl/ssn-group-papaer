"""E02 Layer 2 — ticket selection factorial, with the frequency control.

Preregistered quantities (notes/E02_PREREGISTRATION.md, Layer 2). Top-k overlap
is deliberately NOT the primary one.

The design has one perfectly controlled arm and one confounded arm, and they are
labelled as such:

  seed arm      same language, data, prompt; seed differs   -> the ceiling
  prompt arm    same language, data, seed; prompt differs   -> CLEAN
  language arm  same prompt, seed; language AND data differ -> CONFOUNDED

The prompt arm is the one the claim rests on, and it is the clean one.

The frequency control is the load-bearing analysis. KS-Lottery already reports
that winning tickets are high-frequency tokens, and a token placed in the prompt
template gains ~one occurrence per training example, so "template tokens are
frequent tokens" is the null. The control therefore compares each template token
against non-template tokens **matched on total training count**: same number of
occurrences, but spread over varying sentences instead of repeated in one
constant task role. If template membership still predicts the shift, frequency
is not the explanation.
"""
import itertools
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402
from e02_prompts import PROMPTS, prompt  # noqa: E402

LANGS = ("ca", "es", "ro")
SEEDS = (0, 1)
TOPK = (12, 15, 18, 100)
MATCH_TOL = 0.20   # +/-20% on total training count


def load(tok):
    out = {}
    for lang, p, s in itertools.product(LANGS, PROMPTS, SEEDS):
        f = ROOT / "results" / f"ks_select_l2_{lang}_{p}_s{s}.json"
        if f.exists():
            d = json.loads(f.read_text())
            sh = d["shift_all"]
            out[(lang, p, s)] = {
                "shift": sh,
                "rank": {i: r for r, i in enumerate(
                    sorted(range(len(sh)), key=lambda j: -sh[j]))},
                "order": sorted(range(len(sh)), key=lambda j: -sh[j]),
                "head": d["head"], "tail": d["tail"],
            }
    return out


def pool_counts(tok, lang, p, seed):
    from ks_select import build_pool
    head, tail = prompt(p, lang)
    rows = build_pool(tok, lang, head, tail, 10000, 1732)
    c = Counter()
    for x, y in rows:
        c.update(x)
        c.update(y)
    return c


def overlap_block(a, b, data):
    from scipy import stats
    rec = {}
    for k in TOPK:
        A, B = set(data[a]["order"][:k]), set(data[b]["order"][:k])
        rec[f"k{k}"] = len(A & B)
    r = stats.spearmanr(data[a]["shift"], data[b]["shift"])
    rec["spearman_full_vocab"] = float(r.statistic)
    return rec


def main():
    from transformers import AutoTokenizer
    from scipy import stats
    tok = AutoTokenizer.from_pretrained((ROOT / ".modelpath").read_text().strip(),
                                        use_fast=True)
    data = load(tok)
    print(f"loaded {len(data)}/18 cells", flush=True)
    if len(data) < 18:
        print("  (incomplete -- numbers below are partial)", flush=True)

    out = {"cells": sorted(f"{l}_{p}_s{s}" for l, p, s in data), "arms": {},
           "frequency_control": {}, "tickets": {}}

    # ---- the three arms -------------------------------------------------
    arms = {"seed_ceiling": [], "prompt_clean": [], "language_confounded": []}
    for lang, p in itertools.product(LANGS, PROMPTS):
        if (lang, p, 0) in data and (lang, p, 1) in data:
            arms["seed_ceiling"].append(((lang, p, 0), (lang, p, 1)))
    for lang, s in itertools.product(LANGS, SEEDS):
        for pa, pb in itertools.combinations(PROMPTS, 2):
            if (lang, pa, s) in data and (lang, pb, s) in data:
                arms["prompt_clean"].append(((lang, pa, s), (lang, pb, s)))
    for p, s in itertools.product(PROMPTS, SEEDS):
        for la, lb in itertools.combinations(LANGS, 2):
            if (la, p, s) in data and (lb, p, s) in data:
                arms["language_confounded"].append(((la, p, s), (lb, p, s)))

    for name, pairs in arms.items():
        blocks = [overlap_block(a, b, data) for a, b in pairs]
        if not blocks:
            continue
        out["arms"][name] = {
            "n_pairs": len(blocks),
            **{key: sum(b[key] for b in blocks) / len(blocks)
               for key in blocks[0]},
        }

    print(f"\n{'arm':<24}{'pairs':>6}" + "".join(f"{'k'+str(k):>7}" for k in TOPK)
          + f"{'spearman':>11}")
    for name in ("seed_ceiling", "prompt_clean", "language_confounded"):
        if name not in out["arms"]:
            continue
        a = out["arms"][name]
        print(f"{name:<24}{a['n_pairs']:>6}"
              + "".join(f"{a['k'+str(k)]:>7.1f}" for k in TOPK)
              + f"{a['spearman_full_vocab']:>11.3f}")

    # ---- frequency control ----------------------------------------------
    print(f"\nfrequency control (count-matched, +/-{int(MATCH_TOL*100)}%)", flush=True)
    print(f"{'cell':<22}{'n_tpl':>7}{'matched':>9}{'tpl rank':>10}"
          f"{'ctrl rank':>11}{'wilcoxon p':>12}{'beta_tpl':>10}")
    for (lang, p, s), v in sorted(data.items()):
        cnt = pool_counts(tok, lang, p, s)
        tpl = set(tok.encode(v["head"], add_special_tokens=False)) | \
            set(tok.encode(v["tail"], add_special_tokens=False))
        seen = [i for i in range(len(v["shift"])) if cnt[i] > 0]
        tpl_seen = [i for i in tpl if cnt[i] > 0]
        non = [i for i in seen if i not in tpl]

        pairs_t, pairs_c = [], []
        for t in tpl_seen:
            lo, hi = cnt[t] * (1 - MATCH_TOL), cnt[t] * (1 + MATCH_TOL)
            m = [i for i in non if lo <= cnt[i] <= hi]
            if not m:
                continue
            pairs_t.append(v["rank"][t])
            pairs_c.append(sorted(v["rank"][i] for i in m)[len(m) // 2])
        if len(pairs_t) >= 5:
            w = stats.wilcoxon(pairs_t, pairs_c)
            wp = float(w.pvalue)
        else:
            wp = float("nan")

        # OLS: shift ~ log1p(count) + is_template, standardized
        import numpy as np
        X = np.column_stack([np.log1p([cnt[i] for i in seen]),
                             [1.0 if i in tpl else 0.0 for i in seen],
                             np.ones(len(seen))])
        y = np.array([v["shift"][i] for i in seen])
        Xs = X.copy()
        for c in (0, 1):
            Xs[:, c] = (Xs[:, c] - Xs[:, c].mean()) / (Xs[:, c].std() + 1e-12)
        ys = (y - y.mean()) / (y.std() + 1e-12)
        beta = np.linalg.lstsq(Xs, ys, rcond=None)[0]

        rec = {"n_template_tokens_seen": len(tpl_seen), "n_matched": len(pairs_t),
               "median_template_rank": float(np.median(pairs_t)) if pairs_t else None,
               "median_matched_control_rank": float(np.median(pairs_c)) if pairs_c else None,
               "wilcoxon_p": wp,
               "beta_log_count": float(beta[0]), "beta_is_template": float(beta[1])}
        out["frequency_control"][f"{lang}_{p}_s{s}"] = rec
        out["tickets"][f"{lang}_{p}_s{s}"] = [
            [i, tok.decode([i]), i in tpl] for i in v["order"][:18]]
        print(f"{lang+'_'+p+'_s'+str(s):<22}{len(tpl_seen):>7}{len(pairs_t):>9}"
              f"{rec['median_template_rank'] or -1:>10.0f}"
              f"{rec['median_matched_control_rank'] or -1:>11.0f}"
              f"{wp:>12.2e}{rec['beta_is_template']:>10.3f}")

    (ROOT / "results" / "e02_l2_analysis.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))

    # ---- preregistered gate ---------------------------------------------
    a = out["arms"]
    if all(k in a for k in ("seed_ceiling", "prompt_clean", "language_confounded")):
        ceil, pr, lg = (a["seed_ceiling"]["k18"], a["prompt_clean"]["k18"],
                        a["language_confounded"]["k18"])
        betas = [r["beta_is_template"] for r in out["frequency_control"].values()]
        freq_ok = sum(b > 0 for b in betas) >= 0.9 * len(betas)
        print(f"\nPREREGISTERED GATE (Layer 2):")
        print(f"  k18 seed ceiling {ceil:.1f} | prompt arm {pr:.1f} | language arm {lg:.1f}")
        print(f"  prompt effect at least comparable to language effect: {pr <= lg + 1.0}")
        print(f"  both clearly below ceiling: {pr < ceil - 1 and lg < ceil - 1}")
        print(f"  is_template beta > 0 after frequency control in "
              f"{sum(b>0 for b in betas)}/{len(betas)} cells: {freq_ok}")
        ok = (pr <= lg + 1.0) and pr < ceil - 1 and lg < ceil - 1 and freq_ok
        print(f"  => LAYER 2 {'PASSES -- proceed to Layer 3' if ok else 'FAILS -- stop, write Findings'}")


if __name__ == "__main__":
    main()
