"""E11 summary: same base (Qwen3-8B-Base), two post-trainings -- distillation (official Qwen3-8B) vs pure RL (DAPO).
Per problem set, on the same problems: B0 base sampling, B1 base argmax at forks, B2_post / B2_dapo (base takes the
post model's argmax at forks), P0 distill sampling, D0 DAPO sampling, BA base with forced "Alright, I have this problem"
opening. All anchors 8 samples at T=0.6/top-p 0.95, cap 4096; grids one sample per problem, cap 4096.
Problems DAPO-Math-17k contains (/tmp/xiang_lmhead/e07/dapo_seen.json) are reported separately ("seen").
Usage (on fvcrc11, after copying the fvcrc13 t_d_B2_* files into /tmp/xiang_lmhead/e11/gen):
  python3 e11_summary.py [sets]     sets default m500e,math_l5,olymp,aime"""
import glob
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E7 = Path("/tmp/xiang_lmhead/e07/gen")
E11 = Path("/tmp/xiang_lmhead/e11/gen")
SEEN = json.load(open("/tmp/xiang_lmhead/e07/dapo_seen.json"))
# set name -> (E07 grid suffix, E07 anchor suffix, E11 anchor suffix, seen key)
SETS = {"m500e": ("m500e", "m500e", "m500e", "m500e"), "math_l5": ("math_l5", "math_l5", "math_l5_300", "math_l5_300"),
        "olymp": ("olymp", "olymp", "olymp", "olymp"), "aime": (None, "aime", "aime", "aime")}


def boot(per, n=4000, seed=0):
    ks = [k for k in per if per[k]]
    if not ks:
        return None
    m = [sum(per[k]) / len(per[k]) for k in ks]
    rng = random.Random(seed)
    bs = sorted(sum(m[rng.randrange(len(m))] for _ in m) / len(m) for _ in range(n))
    return [round(sum(m) / len(m), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(ks)]


def anchor(path):
    """-> ({index: [reward]*8}, {index: [(len, truncated, reward, opens_with_Alright)]*8})"""
    if not path.exists():
        return None, None
    out, raw = {}, {}
    for l in open(path):
        r = json.loads(l)
        out[r["index"]] = [c["reward"] for c in r["completions"]]
        raw[r["index"]] = [(len(c["token_ids"]), c["finish"] == "length", c["reward"],
                            c.get("text", "")[:40].lstrip().startswith(("Alright", "Assistant: Alright"))) for c in r["completions"]]
    return out, raw


def anchor_stats(raw, ks):
    xs = [x for k in ks if k in raw for x in raw[k]]
    mean = lambda v: round(sum(v) / len(v), 1) if v else None
    return {"mean_len": mean([x[0] for x in xs]), "trunc": round(sum(x[1] for x in xs) / len(xs), 4),
            "len_correct": mean([x[0] for x in xs if x[2]]), "len_wrong": mean([x[0] for x in xs if not x[2]]),
            "open_alright": round(sum(x[3] for x in xs) / len(xs), 3)}


def grid(pattern):
    out = {}
    for f in sorted(glob.glob(str(pattern))):
        for l in open(f):
            r = json.loads(l)
            out.setdefault(r["index"], [r["reward"]])   # first file wins on duplicates
    return out or None


def main():
    sets = sys.argv[1].split(",") if len(sys.argv) > 1 else list(SETS)
    res = {}
    for s in sets:
        g7, a7, a11, sk = SETS[s]
        C, stats = {}, {}
        C["B0"], stats["B0"] = anchor(E7 / f"a_qwen3-8b-base_{a7}.jsonl")
        C["P0"], stats["P0"] = anchor(E7 / f"a_qwen3-8b_{a7}.jsonl")
        C["D0"], stats["D0"] = anchor(E11 / f"a_qwen3-8b-dapo_{a11}.jsonl")
        C["BA"], stats["BA"] = anchor(E11 / f"a_qwen3-8b-base-ALR_{a11}.jsonl")
        if g7:
            C["B1"] = grid(E7 / f"t_t_base_basemode_{g7}.jsonl")
            C["B2_post"] = grid(E7 / f"t_t_base_postmode_{g7}.jsonl")
            C["B2_dapo"] = grid(E11 / f"t_d_B2_{g7}*.jsonl")
        C = {k: v for k, v in C.items() if v}
        seen = set(SEEN.get(sk, []))
        if s == "aime":   # clean = AIME 2024-2025 only; treat every 2022-2023 problem as seen
            seen = {json.loads(l)["index"] for l in open("/tmp/xiang_lmhead/e07/aime.jsonl")
                    if json.loads(l)["src"].startswith(("2022", "2023"))}
        # universe = the problems the E11 runs cover (math_l5: E07 anchors have 500 problems, E11 uses the 300 of the grid)
        uni = set(C["D0"]) if "D0" in C else set.union(*[set(v) for v in C.values()])
        C = {c: {k: v for k, v in C[c].items() if k in uni} for c in C}
        R = {"n_universe": len(uni), "subsets": {}}
        mean = lambda v: sum(v) / len(v)
        for sub, keep in (("unseen", lambda k: k not in seen), ("seen", lambda k: k in seen), ("all", lambda k: True)):
            if sub == "seen" and not seen:
                continue
            d = {}
            # absolute accuracies on the problems every available condition covers
            # (B2_dapo may still be partial: it is reported on its own problems and through the paired rows)
            full = [c for c in C if c != "B2_dapo"]
            ks = sorted(k for k in set.intersection(*[set(C[c]) for c in full]) if keep(k))
            d["n_common"] = len(ks)
            d["acc"] = {c: boot({k: C[c][k] for k in ks}) for c in full}
            if "B2_dapo" in C:
                d["acc"]["B2_dapo (own problems)"] = boot({k: v for k, v in C["B2_dapo"].items() if keep(k)})
            # paired differences, each on the problems its two conditions share (so anchor-only gaps use every problem)
            pd = {}
            for name, a, b in (("gap distill P0-B0", "P0", "B0"), ("gap DAPO D0-B0", "D0", "B0"), ("D0-P0", "D0", "P0"),
                               ("derand B1-B0", "B1", "B0"), ("choice distill B2p-B1", "B2_post", "B1"),
                               ("choice DAPO B2d-B1", "B2_dapo", "B1"), ("B2d-B2p", "B2_dapo", "B2_post"),
                               ("remaining DAPO D0-B2d", "D0", "B2_dapo"), ("cue BA-B0", "BA", "B0"),
                               ("post-cue DAPO D0-BA", "D0", "BA"), ("post-cue distill P0-BA", "P0", "BA")):
                if a in C and b in C:
                    kk = sorted(k for k in set(C[a]) & set(C[b]) if keep(k))
                    pd[name] = boot({k: [mean(C[a][k]) - mean(C[b][k])] for k in kk})
            d["paired"] = pd
            # by base solve rate (anchor-only, all problems of the subset)
            if "B0" in C:
                bins = {"p_base=0": lambda p: p == 0, "0<p<=3/8": lambda p: 0 < p <= 0.375,
                        "3/8<p<1": lambda p: 0.375 < p < 1, "p_base=1": lambda p: p == 1}
                by = {}
                for bn, f in bins.items():
                    kb = [k for k in C["B0"] if keep(k) and f(mean(C["B0"][k]))]
                    e = {"n": len(kb)}
                    for nm, a, b in (("P0-B0", "P0", "B0"), ("D0-B0", "D0", "B0"), ("B1-B0", "B1", "B0"),
                                     ("B2p-B1", "B2_post", "B1"), ("B2d-B1", "B2_dapo", "B1"), ("BA-B0", "BA", "B0")):
                        if a in C and b in C:
                            kk = [k for k in kb if k in C[a] and k in C[b]]
                            if len(kk) >= 10:
                                e[nm] = boot({k: [mean(C[a][k]) - mean(C[b][k])] for k in kk})
                    by[bn] = e
                d["by_base_solve_rate"] = by
            # pass@k coverage for the anchors (unbiased estimator, n=8)
            from math import comb
            pk = {}
            for c in ("B0", "P0", "D0", "BA"):
                if c in C:
                    kk = [k for k in C[c] if keep(k)]
                    pk[c] = {kq: round(sum(1 - comb(8 - int(sum(C[c][k])), kq) / comb(8, kq) for k in kk) / len(kk), 4)
                             for kq in (1, 2, 4, 8)}
            d["pass@k"] = pk
            d["anchor_stats"] = {c: anchor_stats(stats[c], [k for k in uni if keep(k)]) for c in stats if stats[c]}
            R["subsets"][sub] = d
        res[s] = R
    out = ROOT / "results" / "e11"; out.mkdir(parents=True, exist_ok=True)
    (out / f"summary_{'_'.join(sets)}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
