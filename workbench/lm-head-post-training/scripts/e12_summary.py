"""E12 summary: after the forced "Alright, I have this problem" opening, what is left?
BA = base + opening (E11 anchor, 8 samples); BA1 = base + opening + base argmax at forks (4 samples);
compared with B0 / P0 (E07 anchors), D0 (E11), B1 / B2_post (E07 lockstep), on problems DAPO-Math-17k does not contain.
Usage (fvcrc11): python3 e12_summary.py [sets]   default olymp,math_l5,m500e"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E7, E11, E12 = (Path(f"/tmp/xiang_lmhead/{e}/gen") for e in ("e07", "e11", "e12"))
SEEN = json.load(open("/tmp/xiang_lmhead/e07/dapo_seen.json"))
SETS = {"olymp": ("olymp", "olymp", "olymp"), "math_l5": ("math_l5", "math_l5_300", "math_l5_300"), "m500e": ("m500e", "m500e", "m500e")}


def boot(per, n=4000, seed=0):
    ks = [k for k in per if per[k]]
    if not ks:
        return None
    m = [sum(per[k]) / len(per[k]) for k in ks]
    rng = random.Random(seed)
    bs = sorted(sum(m[rng.randrange(len(m))] for _ in m) / len(m) for _ in range(n))
    return [round(sum(m) / len(m), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(ks)]


def anchor(path):
    if not path.exists():
        return None, None
    out, st = {}, {}
    for l in open(path):
        r = json.loads(l)
        out[r["index"]] = [c["reward"] for c in r["completions"]]
        st[r["index"]] = [(len(c["token_ids"]), c["finish"] == "length") for c in r["completions"]]
    return out, st


def grid(path):
    """one row per problem; path may be a glob (shards merged, first file wins on duplicates)"""
    import glob
    out = {}
    for f in sorted(glob.glob(str(path))):
        for l in open(f):
            r = json.loads(l)
            out.setdefault(r["index"], [r["reward"]])
    return out or None


def main():
    sets = sys.argv[1].split(",") if len(sys.argv) > 1 else list(SETS)
    res = {}
    for s in sets:
        g7, a11, sk = SETS[s]
        a7 = "math_l5" if s == "math_l5" else s
        C, ST = {}, {}
        C["B0"], _ = anchor(E7 / f"a_qwen3-8b-base_{a7}.jsonl")
        C["P0"], _ = anchor(E7 / f"a_qwen3-8b_{a7}.jsonl")
        C["D0"], ST["D0"] = anchor(E11 / f"a_qwen3-8b-dapo_{a11}.jsonl")
        C["BA"], ST["BA"] = anchor(E11 / f"a_qwen3-8b-base-ALR_{a11}.jsonl")
        C["BA1"], ST["BA1"] = anchor(E12 / f"a_qwen3-8b-base-ALR-B1_{a11}.jsonl")
        for cw in ("ALW", "OKL"):   # other opening wordings: single word "Alright", "Okay, let's"
            C[f"cue{cw}"], ST[f"cue{cw}"] = anchor(E12 / f"a_qwen3-8b-base-cue{cw}_{a11}.jsonl")
        C["B1"] = grid(E7 / f"t_t_base_basemode_{g7}.jsonl")
        C["B2_post"] = grid(E7 / f"t_t_base_postmode_{g7}.jsonl")
        C["BA2"] = grid(E12 / f"t_BA2_{g7}_*.jsonl")   # opening + distill argmax at forks (lockstep shards)
        C = {k: v for k, v in C.items() if v}
        if "BA1" not in C:
            continue
        uni = set(C["BA1"]) - set(SEEN.get(sk, []))
        mean = lambda v: sum(v) / len(v)
        R = {"n": len(uni), "acc": {c: boot({k: C[c][k] for k in uni if k in C[c]}) for c in C}, "paired": {}}
        for name, a, b in (("derand after cue BA1-BA", "BA1", "BA"), ("cue BA-B0", "BA", "B0"), ("BA1-B1", "BA1", "B1"),
                           ("P0-BA1", "P0", "BA1"), ("D0-BA1", "D0", "BA1"), ("P0-BA", "P0", "BA"), ("derand B1-B0", "B1", "B0"),
                           ("choice after cue BA2-BA1", "BA2", "BA1"), ("BA2-BA", "BA2", "BA"), ("P0-BA2", "P0", "BA2"),
                           ("choice no cue B2p-B1", "B2_post", "B1"),
                           ("cueALW-B0", "cueALW", "B0"), ("cueOKL-B0", "cueOKL", "B0"), ("cueALW-BA", "cueALW", "BA"),
                           ("cueOKL-BA", "cueOKL", "BA"), ("D0-cueALW", "D0", "cueALW"), ("D0-cueOKL", "D0", "cueOKL")):
            if a in C and b in C:
                R["paired"][name] = boot({k: [mean(C[a][k]) - mean(C[b][k])] for k in uni if k in C[a] and k in C[b]})
        R["len_trunc"] = {c: [round(mean([x[0] for k in uni if k in ST[c] for x in ST[c][k]]), 1),
                              round(mean([x[1] for k in uni if k in ST[c] for x in ST[c][k]]), 4)] for c in ST if ST.get(c)}
        # by base solve rate
        by = {}
        for bn, f in {"p_base=0": lambda p: p == 0, "0<p<=3/8": lambda p: 0 < p <= .375, "3/8<p<1": lambda p: .375 < p < 1, "p_base=1": lambda p: p == 1}.items():
            kb = [k for k in uni if k in C["B0"] and f(mean(C["B0"][k]))]
            by[bn] = {"n": len(kb)} | {nm: boot({k: [mean(C[a][k]) - mean(C[b][k])] for k in kb if k in C[a] and k in C[b]})
                                       for nm, a, b in (("BA-B0", "BA", "B0"), ("BA1-BA", "BA1", "BA"), ("P0-BA1", "P0", "BA1"), ("D0-BA1", "D0", "BA1"))}
        R["by_base_solve_rate"] = by
        res[s] = R
    out = ROOT / "results" / "e12"; out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
