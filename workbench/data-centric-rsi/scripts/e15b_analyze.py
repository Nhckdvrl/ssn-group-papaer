"""E15b analysis (CPU only): surface/structure readouts of generated questions and admission readouts
under fixed solvers. Thresholds fixed before the run (card E15): near-duplicate = Jaccard >= 0.7 on word
3-gram shingles (MinHash 128 perms, LSH 32x4 then exact check); admission bands [0.3, 0.8] (code) and
[0.3, 0.7] (paper); hard tail = majority share <= 0.3 among non-dropped, scored questions.

Usage: python e15b_analyze.py --gen_dir <dir with gen_<tag>_s<seed>.jsonl> --admit_dir <dir> --out <json>
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics as st
import zlib

import numpy as np

P = (1 << 61) - 1
RNG = np.random.default_rng(12345)
A = RNG.integers(1, P - 1, size=128, dtype=np.uint64)
B = RNG.integers(0, P - 1, size=128, dtype=np.uint64)
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def shingles(text, k=3):
    w = re.findall(r"\w+", text.lower())
    if len(w) < k:
        return {zlib.crc32(" ".join(w).encode())} if w else set()
    return {zlib.crc32(" ".join(w[i:i + k]).encode()) for i in range(len(w) - k + 1)}


def minhash(sh):
    if not sh:
        return np.full(128, P, dtype=np.uint64)
    x = np.fromiter(sh, dtype=np.uint64)
    return ((np.outer(x, A) + B) % P).min(axis=0)


def near_dup_pairs(sigs, shs, thr=0.7, bands=32, rows=4):
    buckets = collections.defaultdict(list)
    for i, s in enumerate(sigs):
        for b in range(bands):
            buckets[(b, s[b * rows:(b + 1) * rows].tobytes())].append(i)
    cand = set()
    for ids in buckets.values():
        if 1 < len(ids) < 2000:
            for a in range(len(ids)):
                for c in range(a + 1, len(ids)):
                    cand.add((ids[a], ids[c]))
    out = []
    for i, j in cand:
        u = len(shs[i] | shs[j])
        if u and len(shs[i] & shs[j]) / u >= thr:
            out.append((i, j))
    return out


def surface(rows):
    qs = [r["question"] for r in rows if r["parse_ok"]]
    nums = [[float(x) for x in NUM.findall(q)] for q in qs]
    digits = [max((len(x.split(".")[0].lstrip("-")) for x in NUM.findall(q)), default=0) for q in qs]
    return {
        "n": len(rows), "parse_rate": len(qs) / max(1, len(rows)),
        "truncated_rate": sum(r["finish"] == "length" for r in rows) / max(1, len(rows)),
        "gen_tokens_mean": st.mean(r["n_tokens"] for r in rows) if rows else None,
        "q_chars_median": st.median(len(q) for q in qs) if qs else None,
        "q_chars_mean": st.mean(len(q) for q in qs) if qs else None,
        "numbers_per_q_mean": st.mean(len(n) for n in nums) if qs else None,
        "max_digits_median": st.median(digits) if qs else None,
        "exact_dup_rate": 1 - len(set(qs)) / max(1, len(qs)),
    }, qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen_dir", required=True); ap.add_argument("--admit_dir", default=None)
    ap.add_argument("--out", required=True); ap.add_argument("--ref_tag", default="base")
    ap.add_argument("--alt_none", action="store_true")
    a = ap.parse_args()
    by_tag = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(a.gen_dir, "gen_*.jsonl"))):
        for l in open(p):
            r = json.loads(l); by_tag[r["tag"]].append(r)
    res = {"surface": {}, "dup": {}, "admit": {}}
    qsets = {}
    for tag, rows in by_tag.items():
        res["surface"][tag], qsets[tag] = surface(rows)
        # per-seed halves for the noise floor
        for s in sorted({r["seed"] for r in rows}):
            res["surface"][f"{tag}|seed{s}"], _ = surface([r for r in rows if r["seed"] == s])
    # near duplicates: within each set (fixed-size random subsample so sets of different size compare fairly)
    rng = np.random.default_rng(0)
    m = min(len(q) for q in qsets.values())
    sub = {t: [q[i] for i in rng.choice(len(q), size=m, replace=False)] for t, q in qsets.items()}
    for tag, qs in sub.items():
        shs = [shingles(q) for q in qs]; sigs = [minhash(s) for s in shs]
        pairs = near_dup_pairs(sigs, shs)
        involved = {i for p in pairs for i in p}
        res["dup"][tag] = {"m": m, "near_dup_pairs": len(pairs), "frac_in_near_dup": len(involved) / m}
    # cross-set: fraction of each set's questions with a near-duplicate in the reference (base) pool
    if a.ref_tag in sub:
        ref = sub[a.ref_tag]; rsh = [shingles(q) for q in ref]; rsig = [minhash(s) for s in rsh]
        for tag, qs in sub.items():
            if tag == a.ref_tag:
                continue
            shs = [shingles(q) for q in qs]; sigs = [minhash(s) for s in shs]
            pairs = near_dup_pairs(rsig + sigs, rsh + shs)
            hit = {j - len(ref) for i, j in pairs if i < len(ref) <= j}
            res["dup"][tag]["frac_near_dup_of_ref"] = len(hit) / m
    if a.admit_dir:
        # generation cost per tag (sum over that tag's files) for "admitted per generation GPU-hour"
        gen_h = collections.defaultdict(float); gen_n = collections.defaultdict(int)
        for p in glob.glob(os.path.join(a.gen_dir, "gen_*.jsonl.meta.json")):
            m = json.load(open(p)); t = os.path.basename(p).split("_")[1]
            gen_h[t] += m["gen_seconds"] / 3600; gen_n[t] += m["n"]
        alt_cluster = None
        if a.alt_none:  # alternative scoring: drop the "None" extraction before clustering (official keeps it)
            ns = {}
            src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "e15b_admit.py")).read()
            src = src.replace("import vllm\n", "").replace("from transformers import AutoTokenizer\n", "")
            exec(compile(src.split("def main():")[0], "e15b_admit", "exec"), ns)
            alt_cluster = lambda xs: ns["cluster"](xs, ns["grade_t"])
        by_solver = collections.defaultdict(list)
        for p in sorted(glob.glob(os.path.join(a.admit_dir, "admit_*__*.jsonl"))):
            solver = os.path.basename(p)[len("admit_"):].split("__")[0]
            by_solver[solver] += [json.loads(l) for l in open(p)]
        for solver, rows in by_solver.items():
            if alt_cluster:
                for r in rows:
                    xs = [x for x in r.get("extracted", []) if x and x != "None"]
                    c = alt_cluster(xs) if xs else {}
                    mj = max(c, key=c.get) if c else ""
                    r["alt_score"] = c[mj] / len(xs) if c else None
                    r["alt_dropped"] = (("证明" in r["question"] or "box" in r["question"].lower() or "text" in mj.lower())
                                        if c else True)
            for tag in sorted({r["tag"] for r in rows}):
                rr = [r for r in rows if r["tag"] == tag]
                for s in [None] + sorted({r["seed"] for r in rr}):
                    xs = [r for r in rr if s is None or r["seed"] == s]
                    ok = [r for r in xs if r["score"] is not None and not r["dropped"]]
                    sc = [r["score"] for r in ok]
                    key = f"{solver}|{tag}" + ("" if s is None else f"|seed{s}")
                    pr = res["surface"].get(tag, {}).get("parse_rate", 0)
                    n = max(1, len(xs))
                    # official pipeline: evaluate.py score band, then upload.py also drops majority "" / "None"
                    adm = [r for r in ok if 0.3 <= r["score"] <= 0.8 and r["majority"] not in ("", "None")]
                    adm8 = len(adm) / n
                    d = {
                        "n": len(xs), "kept_after_drop": len(sc) / n,
                        "admit_03_08": adm8, "admit_03_07": sum(0.3 <= r["score"] <= 0.7 and r["majority"] not in ("", "None") for r in ok) / n,
                        "band_03_08_incl_none": sum(0.3 <= x <= 0.8 for x in sc) / n,
                        "hard_tail_le_03": sum(x <= 0.3 for x in sc) / n,
                        "unanimous": sum(x == 1.0 for x in sc) / n,
                        "agree_setter": sum(r["agree_setter"] for r in xs) / n,
                        "band_majority_none": sum(r["majority"] == "None" for r in ok if 0.3 <= r["score"] <= 0.8) / max(1, sum(0.3 <= x <= 0.8 for x in sc)),
                        "resp_without_box": sum(e == "None" for r in xs for e in r.get("extracted", [])) / max(1, sum(len(r.get("extracted", [])) for r in xs)),
                        "grade_error": sum(r.get("grade_error", False) for r in xs) / n,
                        "admitted_per_1k_samples": 1000 * pr * adm8,
                        "score_hist": np.histogram(sc, bins=[0, .2, .3, .4, .5, .6, .7, .8, .9, 1.0001])[0].tolist(),
                    }
                    if s is None and gen_h.get(tag):
                        d["admitted_per_gen_gpu_hour"] = pr * adm8 * gen_n[tag] / gen_h[tag]
                    if alt_cluster:
                        asc = [r["alt_score"] for r in xs if r["alt_score"] is not None and not r["alt_dropped"]]
                        d["alt_none_dropped_admit_03_08"] = sum(0.3 <= x <= 0.8 for x in asc) / n  # None removed before clustering
                        d["alt_none_dropped_hard_tail_le_03"] = sum(x <= 0.3 for x in asc) / n
                    res["admit"][key] = d
    json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res["surface"], indent=1, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
