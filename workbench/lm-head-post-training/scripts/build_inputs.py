"""Fixed input sets for E01 (texts) and E02 (math prompts). Deterministic (seed 0).

Writes manifests with dataset indices + text sha1 only (texts are re-materialised from the local
HF cache by `load_e01_texts` / `load_e02_prompts`, so no third-party text is committed).
  data/e01_texts.json   : 64 Pile-10k documents + 64 MATH-train (problem+solution) documents
  data/e02_prompts.json : 128 MATH-train problems, levels 3-5, stratified over the 7 subjects
"""
import hashlib
import json
import os
import random
import re
from pathlib import Path

os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
import datasets  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SUBJECTS = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra",
            "number_theory", "prealgebra", "precalculus"]


def sha1(s):
    return hashlib.sha1(s.encode()).hexdigest()


def last_boxed(s):
    i = s.rfind("\\boxed")
    if i < 0:
        return None
    j = s.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(s)):
        depth += {"{": 1, "}": -1}.get(s[k], 0)
        if depth == 0:
            return s[j + 1:k]
    return None


def math_split(subject):
    return datasets.load_dataset("EleutherAI/hendrycks_math", subject, split="train")


def load_e01_texts():
    man = json.loads((DATA / "e01_texts.json").read_text())
    pile = datasets.load_dataset("NeelNanda/pile-10k", split="train")
    out = []
    for it in man["items"]:
        if it["source"] == "pile10k":
            t = pile[it["index"]]["text"]
        else:
            r = math_split(it["subject"])[it["index"]]
            t = f"Problem: {r['problem']}\nSolution: {r['solution']}"
        assert sha1(t) == it["sha1"], it
        out.append({**it, "text": t})
    return out


def load_e02_prompts():
    man = json.loads((DATA / "e02_prompts.json").read_text())
    out = []
    for it in man["items"]:
        r = math_split(it["subject"])[it["index"]]
        assert sha1(r["problem"]) == it["sha1"], it
        out.append({**it, "problem": r["problem"], "solution": r["solution"], "answer": last_boxed(r["solution"])})
    return out


def main():
    DATA.mkdir(exist_ok=True)
    rng = random.Random(0)
    pile = datasets.load_dataset("NeelNanda/pile-10k", split="train")
    cand = [i for i in range(len(pile)) if len(pile[i]["text"]) >= 3000]
    items = [{"source": "pile10k", "index": i, "sha1": sha1(pile[i]["text"])} for i in sorted(rng.sample(cand, 64))]
    per = {s: math_split(s) for s in SUBJECTS}
    pool = [(s, i) for s in SUBJECTS for i in range(len(per[s])) if len(per[s][i]["solution"]) >= 400]
    for s, i in sorted(rng.sample(pool, 64)):
        r = per[s][i]
        items.append({"source": "math_train", "subject": s, "index": i,
                      "sha1": sha1(f"Problem: {r['problem']}\nSolution: {r['solution']}")})
    (DATA / "e01_texts.json").write_text(json.dumps({"seed": 0, "items": items}, indent=1))

    used = {(it.get("subject"), it["index"]) for it in items if it["source"] == "math_train"}
    prompts = []
    for k, s in enumerate(SUBJECTS):
        n = 128 // 7 + (1 if k < 128 % 7 else 0)
        ok = [i for i in range(len(per[s])) if (s, i) not in used
              and re.search(r"Level [345]", per[s][i]["level"]) and last_boxed(per[s][i]["solution"])]
        for i in sorted(rng.sample(ok, n)):
            prompts.append({"subject": s, "index": i, "level": per[s][i]["level"], "sha1": sha1(per[s][i]["problem"])})
    (DATA / "e02_prompts.json").write_text(json.dumps({"seed": 0, "items": prompts}, indent=1))
    print(len(items), "texts;", len(prompts), "prompts")


if __name__ == "__main__":
    import sys
    if "--export-math500" in sys.argv:
        out = Path("/tmp/xiang_lmhead/e04"); out.mkdir(parents=True, exist_ok=True)
        d = datasets.load_dataset("HuggingFaceH4/MATH-500", split="test")
        with open(out / "math500.jsonl", "w") as f:
            for i, r in enumerate(d):
                f.write(json.dumps({"index": i, "problem": r["problem"], "answer": r["answer"], "subject": r["subject"],
                                    "level": r["level"], "sha1": sha1(r["problem"])}) + "\n")
    elif "--export-hard" in sys.argv:
        # E07 hard sets: MATH test Level 5 not in MATH-500 (500 sampled, seed 0); OlympiadBench OE_TO_maths_en_COMP,
        # numerical, single answer, no unit. Index manifest (ids + sha1) goes to data/e07_problems.json.
        import ast
        import glob
        import pandas as pd
        out = Path("/tmp/xiang_lmhead/e07"); out.mkdir(parents=True, exist_ok=True)
        m500 = {sha1(r["problem"]) for r in datasets.load_dataset("HuggingFaceH4/MATH-500", split="test")}
        pool = []
        for s in SUBJECTS:
            d = datasets.load_dataset("EleutherAI/hendrycks_math", s, split="test")
            for i, r in enumerate(d):
                if r["level"] == "Level 5" and sha1(r["problem"]) not in m500 and last_boxed(r["solution"]):
                    pool.append({"subject": s, "src_index": i, "problem": r["problem"], "answer": last_boxed(r["solution"]),
                                 "level": 5, "sha1": sha1(r["problem"])})
        rng = random.Random(0)
        l5 = sorted(rng.sample(pool, 500), key=lambda r: (r["subject"], r["src_index"]))
        ob = pd.read_parquet(glob.glob(os.path.expanduser("~/.cache/huggingface/hub/datasets--Hothan--OlympiadBench/snapshots/*/OlympiadBench/OE_TO_maths_en_COMP/*.parquet"))[0])
        ob = ob[(ob.answer_type == "Numerical") & (ob.is_multiple_answer.astype(str) == "False") & (ob.unit.isna() | ob.unit.astype(str).isin(["nan", "None", ""]))]
        olymp = []
        for _, r in ob.iterrows():
            fa = r["final_answer"]
            fa = list(fa) if not isinstance(fa, str) else ast.literal_eval(fa)
            olymp.append({"id": str(r["id"]), "problem": r["question"], "answer": str(fa[0]).strip().strip("$"),
                          "subfield": r["subfield"], "sha1": sha1(r["question"])})
        manifest = {}
        for name, rows in (("math_l5", l5), ("olymp", olymp)):
            with open(out / f"{name}.jsonl", "w") as f:
                for k, r in enumerate(rows):
                    f.write(json.dumps({"index": k, **r}) + "\n")
            manifest[name] = [{k: r[k] for k in r if k not in ("problem", "answer")} for r in rows]
            print(name, len(rows))
        (DATA / "e07_problems.json").write_text(json.dumps({"seed": 0, **manifest}, indent=0))
    elif "--export-e02" in sys.argv:
        out = Path("/tmp/xiang_lmhead/e02"); out.mkdir(parents=True, exist_ok=True)
        with open(out / "prompts.jsonl", "w") as f:
            for p in load_e02_prompts():
                f.write(json.dumps(p) + "\n")
    else:
        main()
