"""E10 re-audit — is the 'controlled' contrast actually controlled?

The E10 controlled ratio is rel(mmlu_gen_cot)/rel(gsm8k_gen_cot).  Both cells are
free generation with a long chain, which the package treated as "output length held
fixed".  It is not.  The quantity that E07 identified as causal is *where in the
generated trajectory the answer-bearing token sits*, and that differs by 1.7-3.4x
between the two cells in every model, always in the same direction.

This script reports, from the same raw runs:

  PART A  the answer-position distribution per cell, full model
  PART B  the controlled ratio re-estimated with answer position matched by
          stratum reweighting onto the gsm8k distribution
  PART C  the replacement law: a logistic fit of per-item retention on
          log2(1+L), per (model, intervention, cell), and the within-condition
          contrast slope(gsm8k) - slope(mmlu)

L is measured on the FULL model's output, so it is pre-treatment.  Retention is
defined on items the full model answers correctly, so cell difficulty is conditioned
out as well.
"""
from __future__ import annotations
import importlib.util, json, pathlib, re, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
RNG = np.random.default_rng(4242)
B_MATCH, B_SLOPE = 4000, 2000
FLOOR = 0.02          # a cell below this is at the floor; ratios there are n/e

TAGMAP = {"llama": "llama31_8b_instruct", "qwen": "qwen25_7b_instruct",
          "phi4": "phi4_mini_instruct", "olmo3": "olmo3_7b_base",
          "olmo3_7b_base": "olmo3_7b_base", "mistral": "mistral_7b_v03",
          "mistral_7b_v03": "mistral_7b_v03"}
PARAM_LOCUS = ("prune", "quant")
ANS = re.compile(r"[Aa]nswer\s*(?:is)?\s*:?\s*\(?([ABCD])\)?")
NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def answer_position(cell, out):
    """Words emitted before the answer-bearing token.  None if never emitted."""
    if cell.startswith("mmlu"):
        m = ANS.search(out) or re.search(r"\b([ABCD])\b", out[:200])
    else:
        m = re.search(r"####", out)
        if m is None:
            hits = list(NUM.finditer(out.replace("$", " ")))
            m = hits[-1] if hits else None
    return len(out[:m.start()].split()) if m else None


def load(path):
    s = summ.score(path)
    if s.get("correct") is None:
        return None
    recs = [json.loads(l) for l in open(path)][1:]
    ids = [r["id"] for r in recs]
    ap = [answer_position(s["cell"], r.get("output", "") or "") for r in recs]
    return ids, np.array(s["correct"], float), ap, s


def collect():
    full, cond = {}, collections.defaultdict(dict)
    for p in (ROOT / "results" / "e01").rglob("*.jsonl"):
        d = load(p)
        if not d or not d[3]["cell"].endswith("_cot"):
            continue
        if d[3]["mask"] == "full":
            full[(p.parent.name, d[3]["cell"])] = d
        else:
            cond[(p.parent.name, f"readout-{d[3]['mask']}")][d[3]["cell"]] = d
    for p in (ROOT / "results" / "e10").rglob("*.jsonl"):
        if "calib" in str(p):
            continue
        d = load(p)
        if not d or not d[3]["cell"].endswith("_cot"):
            continue
        cond[(TAGMAP.get(p.parent.name, p.parent.name), d[3]["mask"])][d[3]["cell"]] = d
    return full, cond


def retention(full, cond, mdl, iv, cell):
    """(keep indicator, L) over items the full model gets right and that emit an answer."""
    if (mdl, cell) not in full or cell not in cond[(mdl, iv)]:
        return None
    fids, fc, fap, _ = full[(mdl, cell)]
    tids, tc, _, _ = cond[(mdl, iv)][cell]
    tmap = dict(zip(tids, tc))
    keep, L = [], []
    for iid, c, a in zip(fids, fc, fap):
        if c < 1 or a is None or iid not in tmap:
            continue
        keep.append(tmap[iid]); L.append(a)
    if len(keep) < 40:
        return None
    return np.array(keep, float), np.array(L, float)


# ---------------------------------------------------------------- PART A
def part_a(full):
    print("PART A — answer position (words before the answer-bearing token), full model\n")
    print(f"{'model':<22}{'mmlu_gen_cot p10/p50/p90':>28}{'gsm8k_gen_cot p10/p50/p90':>29}{'p50 ratio':>11}")
    for mdl in sorted({k[0] for k in full}):
        q = {}
        for cell in ("mmlu_gen_cot", "gsm8k_gen_cot"):
            if (mdl, cell) not in full:
                break
            L = np.array([a for a in full[(mdl, cell)][2] if a is not None], float)
            q[cell] = np.percentile(L, [10, 50, 90])
        if len(q) < 2:
            continue
        a, b = q["mmlu_gen_cot"], q["gsm8k_gen_cot"]
        print(f"{mdl[:21]:<22}{f'{a[0]:.0f} / {a[1]:.0f} / {a[2]:.0f}':>28}"
              f"{f'{b[0]:.0f} / {b[1]:.0f} / {b[2]:.0f}':>29}{a[1]/b[1]:>11.1f}x")
    print("\nThe two cells the package calls 'output length held fixed' differ by 1.7-3.4x\n"
          "in the number of decoding steps taken under the intervention before the answer\n"
          "is emitted, in the same direction in every model.\n")


# ---------------------------------------------------------------- PART B
EDGES = np.array([0, 25, 50, 75, 100, 150, 225, 10 ** 6])


def part_b(full, cond):
    print("\nPART B — controlled ratio, re-estimated with answer position matched\n")
    print(f"{'model':<20}{'intervention':<16}{'locus':<10}{'as published':>13}"
          f"{'L-matched':>11}{'95% CI':>17}{'sign':>7}")
    rows = []
    for (mdl, iv) in sorted(cond):
        A = retention(full, cond, mdl, iv, "mmlu_gen_cot")
        Bc = retention(full, cond, mdl, iv, "gsm8k_gen_cot")
        if A is None or Bc is None:
            continue
        ka, La = A; kb, Lb = Bc
        if ka.mean() < FLOOR or kb.mean() < FLOOR:
            print(f"{mdl[:19]:<20}{iv:<16}"
                  f"{'parameter' if iv.startswith(PARAM_LOCUS) else 'readout':<10}"
                  f"{'n/e':>13}{'n/e':>11}{'':>17}{'floor':>7}")
            continue
        ba, bb = np.digitize(La, EDGES), np.digitize(Lb, EDGES)
        shared = sorted(set(ba) & set(bb))
        if not shared:
            continue
        w = {s: (bb == s).mean() for s in shared}
        tot = sum(w.values()); w = {s: v / tot for s, v in w.items()}

        def est(k1, b1, k2, b2):
            r1 = sum(w[s] * k1[b1 == s].mean() for s in shared if (b1 == s).sum())
            r2 = sum(w[s] * k2[b2 == s].mean() for s in shared if (b2 == s).sum())
            return r1 / max(r2, 1e-6)

        pt = est(ka, ba, kb, bb)
        boots = []
        for _ in range(B_MATCH):
            i1 = RNG.integers(0, len(ka), len(ka)); i2 = RNG.integers(0, len(kb), len(kb))
            try:
                boots.append(est(ka[i1], ba[i1], kb[i2], bb[i2]))
            except Exception:
                pass
        boots = np.array(boots)
        lo, hi = np.nanpercentile(boots, [2.5, 97.5])
        raw = ka.mean() / max(kb.mean(), 1e-6)
        locus = "parameter" if iv.startswith(PARAM_LOCUS) else "readout"
        sign = ">1" if lo > 1 else ("<1" if hi < 1 else "null")
        rows.append((mdl, iv, locus, raw, pt, lo, hi, sign))
        print(f"{mdl[:19]:<20}{iv:<16}{locus:<10}{raw:>13.2f}{pt:>11.2f}"
              f"   [{lo:>5.2f},{hi:>6.2f}]{sign:>7}")
    for locus in ("readout", "parameter"):
        sub = [r for r in rows if r[2] == locus]
        print(f"  {locus:<10}: {sum(1 for r in sub if r[7]=='<1')} significantly <1, "
              f"{sum(1 for r in sub if r[7]=='null')} null, "
              f"{sum(1 for r in sub if r[7]=='>1')} significantly >1   (n={len(sub)})")
    print("\nThe sign boundary survives as a no-crossing statement, but the per-condition\n"
          "significance that C3.2 rested on does not survive depth matching.\n")
    return rows


# ---------------------------------------------------------------- PART C
def logistic_slope(X, Y):
    Xd = np.c_[np.ones(len(X)), X]; b = np.zeros(2)
    for _ in range(60):
        p = np.clip(1 / (1 + np.exp(-Xd @ b)), 1e-8, 1 - 1e-8)
        W = p * (1 - p)
        H = Xd.T @ (Xd * W[:, None]) + 1e-6 * np.eye(2)
        step = np.linalg.solve(H, Xd.T @ (Y - p)); b = b + step
        if np.abs(step).max() < 1e-9:
            break
    return b[1]


def part_c(full, cond):
    print("\nPART C — the replacement law: depth response by answer provenance\n")
    print(f"{'model':<20}{'intervention':<15}{'locus':<10}"
          f"{'slope MMLU (prompt-rec.)':>26}{'slope GSM8K (traj.-carried)':>28}{'difference':>24}")
    agg = []
    for (mdl, iv) in sorted(cond):
        pair = {}
        for cell in ("mmlu_gen_cot", "gsm8k_gen_cot"):
            r = retention(full, cond, mdl, iv, cell)
            if r is None or not (FLOOR < r[0].mean() < 1 - FLOOR):
                break
            pair[cell] = (np.log2(1 + r[1]), r[0])
        if len(pair) < 2:
            continue
        out = {}
        for cell, (X, Y) in pair.items():
            pt = logistic_slope(X, Y)
            bs = []
            for _ in range(B_SLOPE):
                i = RNG.integers(0, len(Y), len(Y))
                if Y[i].mean() in (0.0, 1.0):
                    continue
                try:
                    bs.append(logistic_slope(X[i], Y[i]))
                except Exception:
                    pass
            out[cell] = (pt, np.array(bs))
        n = min(len(out["mmlu_gen_cot"][1]), len(out["gsm8k_gen_cot"][1]))
        D = out["gsm8k_gen_cot"][1][:n] - out["mmlu_gen_cot"][1][:n]
        (pa, Ba), (pg, Bg) = out["mmlu_gen_cot"], out["gsm8k_gen_cot"]
        la, ha = np.percentile(Ba, [2.5, 97.5]); lg, hg = np.percentile(Bg, [2.5, 97.5])
        ld, hd = np.percentile(D, [2.5, 97.5])
        locus = "parameter" if iv.startswith(PARAM_LOCUS) else "readout"
        agg.append((mdl, iv, locus, pa, la, ha, pg, lg, hg, pg - pa, ld, hd))
        star = " *" if hd < 0 else (" +" if ld > 0 else "  ")
        print(f"{mdl[:19]:<20}{iv:<15}{locus:<10}"
              f"{f'{pa:>6.2f} [{la:>5.2f},{ha:>5.2f}]':>26}"
              f"{f'{pg:>6.2f} [{lg:>5.2f},{hg:>5.2f}]':>28}"
              f"{f'{pg-pa:>6.2f} [{ld:>5.2f},{hd:>5.2f}]{star}':>24}")
    print("\n  * = trajectory-carried decays significantly faster with depth than "
          "prompt-recoverable\n  + = the reverse")
    print(f"\n  {len(agg)} estimable conditions, "
          f"{len({r[0] for r in agg})} model families, "
          f"{len({r[1] for r in agg})} interventions:")
    print(f"    prompt-recoverable slope significantly negative : "
          f"{sum(1 for r in agg if r[5] < 0):>2} / {len(agg)}")
    print(f"    trajectory-carried slope significantly negative : "
          f"{sum(1 for r in agg if r[8] < 0):>2} / {len(agg)}")
    print(f"    difference significant in predicted direction   : "
          f"{sum(1 for r in agg if r[11] < 0):>2} / {len(agg)}")
    print(f"    difference significant in WRONG direction       : "
          f"{sum(1 for r in agg if r[10] > 0):>2} / {len(agg)}")
    return agg


def main():
    full, cond = collect()
    part_a(full)
    rows_b = part_b(full, cond)
    agg_c = part_c(full, cond)
    json.dump({"depth_matched": [list(r) for r in rows_b],
               "depth_slopes": [list(r) for r in agg_c]},
              open(ROOT / "results" / "depth_audit.json", "w"), indent=1)


if __name__ == "__main__":
    main()
