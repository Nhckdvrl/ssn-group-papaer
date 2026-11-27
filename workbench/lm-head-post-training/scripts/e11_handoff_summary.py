"""E11 handoff summary: on identical prefixes, how much does the continuation model matter, for pure RL (DAPO) vs
distillation (Qwen3-8B), both on Qwen3-8B-Base?  G_X(s) = V_X(s) - V_Base(s) on the same (problem, prefix, L).
Prefix sources: D = DAPO anchor, P = distill anchor, B = base anchor.  Continuations: 1 per prefix (T=0.6/top-p 0.95,
total cap 8192).  Also reports V_Base(s_D) against the base with a forced "Alright, I have this problem" opening (BA)
and against the full anchors, so the L=32 row can be read against the opening-cue control.
Files: /tmp/xiang_lmhead/e11/gen/h_<S>2<C>_<set>.jsonl (olymp) and, for MATH L5, E08's h_q_* files for the distill pair.
Usage (fvcrc11): python3 e11_handoff_summary.py olymp|l5"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E7, E8, E11 = (Path(f"/tmp/xiang_lmhead/{e}/gen") for e in ("e07", "e08", "e11"))
SEEN = json.load(open("/tmp/xiang_lmhead/e07/dapo_seen.json"))


def boot(per, n=4000, seed=0):
    ks = [k for k in per if per[k]]
    if not ks:
        return None
    m = [sum(per[k]) / len(per[k]) for k in ks]
    rng = random.Random(seed)
    bs = sorted(sum(m[rng.randrange(len(m))] for _ in m) / len(m) for _ in range(n))
    return [round(sum(m) / len(m), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(ks)]


def load(path):
    if not path.exists():
        return None
    return {(r["index"], r["k"], r["L"]): r for r in (json.loads(l) for l in open(path))}


def anchor(path):
    if not path.exists():
        return None
    return {json.loads(l)["index"]: [c["reward"] for c in json.loads(l)["completions"]] for l in open(path)}


def main():
    which = sys.argv[1]
    if which == "olymp":
        H = {n: load(E11 / f"h_{n}_olymp.jsonl") for n in ("D2B", "D2D", "B2D", "B2B", "P2B", "P2P", "B2P")}
        A = {"B0": anchor(E7 / "a_qwen3-8b-base_olymp.jsonl"), "P0": anchor(E7 / "a_qwen3-8b_olymp.jsonl"),
             "D0": anchor(E11 / "a_qwen3-8b-dapo_olymp.jsonl"), "BA": anchor(E11 / "a_qwen3-8b-base-ALR_olymp.jsonl")}
        excl = set(SEEN["olymp"])
    else:   # MATH L5, only the problems DAPO-Math-17k does not contain
        H = {n: load(E11 / f"h_{n}_l5.jsonl") for n in ("D2B", "D2D", "B2D")}
        H |= {n: load(E8 / f"h_q_{n}_math_l5_300.jsonl") for n in ("B2B", "P2B", "P2P", "B2P")}
        A = {"B0": anchor(E7 / "a_qwen3-8b-base_math_l5.jsonl"), "P0": anchor(E7 / "a_qwen3-8b_math_l5.jsonl"),
             "D0": anchor(E11 / "a_qwen3-8b-dapo_math_l5_300.jsonl"), "BA": anchor(E11 / "a_qwen3-8b-base-ALR_math_l5_300.jsonl")}
        excl = set(SEEN["math_l5_300"])
        uni = set(A["D0"] or {})
        excl |= {k for k in (A["B0"] or {}) if k not in uni}
    H = {k: v for k, v in H.items() if v}
    A = {k: v for k, v in A.items() if v}
    res = {"set": which, "have": sorted(H), "by_L": {}}
    for L in ("32", "256", "rel0.5"):
        d = {}
        for n, rows in H.items():
            per = {}
            for (i, k, l), r in rows.items():
                if l == L and i not in excl:
                    per.setdefault(i, []).append(r["reward"])
            d[f"V({n})"] = boot(per)
        # paired G on identical prefixes: same (index, k, L) in both files
        for name, a, b in (("G_DAPO(s_D) = D2D-D2B", "D2D", "D2B"), ("G_DAPO(s_B) = B2D-B2B", "B2D", "B2B"),
                           ("G_distill(s_P) = P2P-P2B", "P2P", "P2B"), ("G_distill(s_B) = B2P-B2B", "B2P", "B2B"),
                           ("source DAPO vs Base, cont Base = D2B-B2B", "D2B", "B2B"),
                           ("source distill vs Base, cont Base = P2B-B2B", "P2B", "B2B"),
                           ("source DAPO vs distill, cont Base = D2B-P2B", "D2B", "P2B")):
            if a in H and b in H:
                same_prefix = a[0] == b[0]
                per = {}
                if same_prefix:
                    for key, r in H[a].items():
                        if key[2] == L and key[0] not in excl and key in H[b]:
                            per.setdefault(key[0], []).append(r["reward"] - H[b][key]["reward"])
                else:   # different sources: per-problem means, problems both cover
                    pa, pb = {}, {}
                    for key, r in H[a].items():
                        if key[2] == L and key[0] not in excl:
                            pa.setdefault(key[0], []).append(r["reward"])
                    for key, r in H[b].items():
                        if key[2] == L and key[0] not in excl:
                            pb.setdefault(key[0], []).append(r["reward"])
                    per = {i: [sum(pa[i]) / len(pa[i]) - sum(pb[i]) / len(pb[i])] for i in set(pa) & set(pb)}
                d[name] = boot(per)
        # base continuation of a DAPO prefix vs the opening-cue control and the anchors, on the problems D2B covers
        if "D2B" in H:
            pd = {}
            for (i, k, l), r in H["D2B"].items():
                if l == L and i not in excl:
                    pd.setdefault(i, []).append(r["reward"])
            for an, av in A.items():
                ks = [i for i in pd if i in av]
                d[f"D2B - {an}"] = boot({i: [sum(pd[i]) / len(pd[i]) - sum(av[i]) / len(av[i])] for i in ks})
        res["by_L"][L] = d
    m = lambda v: sum(v) / len(v)
    ks = sorted(set.intersection(*[set(v) for v in A.values()]) - excl) if A else []
    res["anchors_same_problems"] = {an: boot({i: av[i] for i in ks}) for an, av in A.items()}
    out = ROOT / "results" / "e11"; out.mkdir(parents=True, exist_ok=True)
    (out / f"handoff_{which}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
