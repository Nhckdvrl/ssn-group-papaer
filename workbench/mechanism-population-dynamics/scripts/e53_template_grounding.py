"""E53: in Dolma-1.7 Flan, how often is the answer after each QA template grounded in the preceding passage?

Protocol: experiments/E53-*.md.  e53_template_grounding.py [--show 20]
"""
import argparse
import json
import re

import numpy as np

import mp_common as mc

FLAN = "/home/xiang/mechpop_cache/e46_data/flan_orig.u16"
EOS = 50279
TEMPLATES = {  # name -> (question marker regex, answer marker regex)
    "Question:": (r"Question:", r"Answer:"),
    "Q:": (r"(?<![A-Za-z])Q:", r"(?<![A-Za-z])A:"),
    "question:": (r"(?<![A-Za-z])question:", r"(?<![A-Za-z])answer:"),
    "QUESTION:": (r"QUESTION:", r"ANSWER:"),
}
LABELS = re.compile(r"^\(?[A-Ha-h1-8]\)?[.)]?$|^(yes|no|true|false|it is not possible to tell|not enough information|"
                    r"positive|negative|neutral|entailment|contradiction)\.?$", re.I)


def occurrences(text, qpat, apat):
    out = []
    for m in re.finditer(qpat, text):
        a = re.compile(apat).search(text, m.end(), m.end() + 600)
        if not a:
            continue
        ans = text[a.end():].split("\n")[0].strip()[:80]
        pre = text[max(0, m.start() - 2000):m.start()]
        label = bool(LABELS.match(ans)) or len(ans) < 3
        grounded = (not label) and ans.lower().rstrip(".") in pre.lower()
        out.append({"ans": ans, "label_like": label, "grounded": grounded, "long_pre": len(pre.strip()) >= 300,
                    "ctx": text[max(0, m.start() - 300):a.end() + 80]})
    return out


def main(show):
    from e46_train import tokenizer
    tok = tokenizer()
    x = np.fromfile(FLAN, dtype=np.uint16)
    cut = np.flatnonzero(x == EOS)
    starts = np.concatenate([[0], cut[:-1] + 1])
    rng = np.random.default_rng(0)
    pick = np.sort(rng.choice(len(cut), min(50_000, len(cut)), replace=False))
    texts = tok.batch_decode([x[starts[i]:cut[i]].tolist() for i in pick])
    out, samples = {}, {}
    for name, (qp, ap) in TEMPLATES.items():
        per_doc = []
        occ_all = []
        for t in texts:
            o = occurrences(t, qp, ap)
            if o:
                per_doc.append((sum(r["grounded"] for r in o), sum(r["label_like"] for r in o), sum(r["long_pre"] for r in o), len(o)))
                occ_all += o
        if not per_doc:
            continue
        P = np.array(per_doc, dtype=float)
        frac = lambda col: P[:, col].sum() / P[:, 3].sum()
        boots = []
        for _ in range(1000):
            s = P[rng.integers(0, len(P), len(P))]
            boots.append(s[:, 0].sum() / s[:, 3].sum())
        out[name] = {"docs": len(P), "occurrences": int(P[:, 3].sum()), "grounded": frac(0),
                     "grounded_ci95": np.percentile(boots, [2.5, 97.5]).tolist(), "label_like": frac(1), "long_pre": frac(2),
                     "grounded_among_non_label": P[:, 0].sum() / (P[:, 3].sum() - P[:, 1].sum())}
        samples[name] = [occ_all[i] for i in rng.choice(len(occ_all), min(show, len(occ_all)), replace=False)]
    (mc.RESULTS / "e53").mkdir(exist_ok=True)
    (mc.RESULTS / "e53" / "analysis.json").write_text(json.dumps(out, indent=1))
    (mc.RESULTS / "e53" / "samples_for_manual_check.json").write_text(json.dumps(samples, indent=1))
    for k, v in out.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})




# ---------------- v2 (registered after the v1 instrument check failed; see the E53 card) ----------------
V2_TEMPLATES = {"Question:": (r"Question:", r"Answer:"), "Q:": (r"(?<![A-Za-z])Q:", r"(?<![A-Za-z])A:"),
                "question:": (r"(?<![A-Za-z])question:", r"(?<![A-Za-z])answer:")}


def first_answer_line(text, start):
    for line in text[start:].split("\n"):
        if line.strip():
            return line.strip()[:80]
    return ""


def v2(show=20):
    from pathlib import Path
    from e46_train import tokenizer
    tok = tokenizer()
    texts = []
    for f in sorted(Path("/home/xiang/mechpop_cache/e46_data").glob("flanshard*.u16")):
        x = np.fromfile(f, dtype=np.uint16)
        cut = np.flatnonzero(x == EOS)
        starts = np.concatenate([[0], cut[:-1] + 1])
        texts += tok.batch_decode([x[s:e].tolist() for s, e in zip(starts[1:], cut[1:])])  # skip the first (cut) doc
    rng = np.random.default_rng(0)
    out, samples = {"n_docs": len(texts)}, {}
    for name, (qp, ap) in V2_TEMPLATES.items():
        per_doc, occ = [], []
        for t in texts:
            ctx_dep = sub = n = 0
            for ex in t.split("\n\n\n"):
                m = re.search(qp, ex)
                if not m:
                    continue
                a = re.compile(ap).search(ex, m.end())
                if not a:
                    continue
                pre = ex[:m.start()].strip()
                ans = first_answer_line(ex, a.end())
                n += 1
                ctx_dep += len(pre) >= 200
                sub += len(ans) >= 3 and ans.lower().rstrip(".") in pre.lower()
                occ.append({"pre_len": len(pre), "ans": ans, "example": ex[:700]})
            if n:
                per_doc.append((ctx_dep, sub, n))
        P = np.array(per_doc, dtype=float)
        boots = [P[i][:, 0].sum() / P[i][:, 2].sum() for i in (rng.integers(0, len(P), len(P)) for _ in range(1000))]
        out[name] = {"docs": len(P), "examples": int(P[:, 2].sum()), "context_dependent": P[:, 0].sum() / P[:, 2].sum(),
                     "context_dependent_ci95": np.percentile(boots, [2.5, 97.5]).tolist(),
                     "answer_in_passage": P[:, 1].sum() / P[:, 2].sum()}
        samples[name] = [occ[i] for i in rng.choice(len(occ), min(show, len(occ)), replace=False)]
    (mc.RESULTS / "e53").mkdir(exist_ok=True)
    (mc.RESULTS / "e53" / "analysis_v2.json").write_text(json.dumps(out, indent=1))
    (mc.RESULTS / "e53" / "samples_v2_for_manual_check.json").write_text(json.dumps(samples, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--v2", action="store_true")
    a = ap.parse_args()
    v2(a.show) if a.v2 else main(a.show)
