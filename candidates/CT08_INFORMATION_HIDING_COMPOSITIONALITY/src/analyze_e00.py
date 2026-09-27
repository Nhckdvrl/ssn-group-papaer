"""CT08 E00 readout (docs/E00_PROTOCOL.md): gate 1 (A-B score), gate 2 (cross-domain skeleton isomorphism),
descriptive leakage / flat baseline.  usage: analyze_e00.py"""
import ast, builtins, itertools, json, os
from datetime import datetime
import dateutil.parser
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "results", "e00")
rng = np.random.default_rng(0)
insts = {json.loads(l)["iid"]: json.loads(l) for l in open(os.path.join(HERE, "..", "data", "e00_instances.jsonl"))}

# ---- scoring: copied verbatim in logic from vendor/rlm training/environments/oolong/oolong/env.py ----
COMPARISON_PHRASES = ("more common than", "less common than", "same frequency as")


def _find_comparison_phrase(output):
    out_low = output.lower()
    hits = [(out_low.rfind(p), p) for p in COMPARISON_PHRASES if p in out_low]
    return max(hits)[1] if hits else None


def _attempt_answer_parse(answer):
    cmp = _find_comparison_phrase(answer)
    if cmp is not None:
        return cmp, "high"
    if ":" not in answer:
        if len(answer) < 20:
            return answer, "low"
        return answer.split()[-1], "low"
    cand = answer.split(":")[-1].strip().replace("*", "").replace("[", "").replace("]", "")
    if len(cand) < 20:
        return cand, "vhigh"
    return cand, "med"


def synth_score(dp, output):
    answer = str(dp.get("answer", ""))
    try:
        if "datetime" in answer:
            gold = datetime.strptime(answer, "[datetime.date(%Y, %m, %d)]")
        else:
            gold = ast.literal_eval(answer)[0]
    except Exception:
        gold = answer
    trimmed, _ = _attempt_answer_parse(output)
    gold_s = str(gold)
    if str(trimmed) == gold_s or str(trimmed).lower() == gold_s.lower():
        return 1.0
    atype = dp.get("answer_type", "")
    if atype == "ANSWER_TYPE.NUMERIC":
        try:
            return 0.75 ** abs(int(gold) - int(trimmed))
        except Exception:
            return 0.0
    if atype == "ANSWER_TYPE.DATE":
        try:
            return 1.0 if dateutil.parser.parse(trimmed) == gold else 0.0
        except Exception:
            return 0.0
    if gold_s and gold_s.lower() not in [p.lower() for p in COMPARISON_PHRASES]:
        if gold_s.lower() in output.lower():
            return 1.0
    return 0.0


# ---- skeletons ----
API = {"llm_query", "llm_query_batched", "FINAL_VAR", "Counter", "defaultdict"}
BUILTINS = set(dir(builtins))


def code_tokens(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return ["ERR"]
    toks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and (f.id in API or f.id in BUILTINS):
                toks.append(f.id)
            elif isinstance(f, ast.Attribute):
                toks.append("." + f.attr)
        elif isinstance(node, (ast.For, ast.While, ast.If, ast.comprehension, ast.Try)):
            toks.append(type(node).__name__)
    return toks


def skeleton(rec):
    s = []
    for it in rec.get("iters", []):
        s.append("|")
        for b in it["blocks"]:
            s += code_tokens(b["code"])
        if it.get("final") is not None:
            s.append("FINAL")
    return s


def ned(a, b):
    if not a and not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(a), len(b))


def leakage(rec, ctx):
    lines = {l for l in ctx.split("\n") if len(l) >= 20}
    shown = payload = 0
    for it in rec.get("iters", []):
        for b in it["blocks"]:
            for l in b["shown"].split("\n"):
                shown += len(l)
                if l.strip() in lines or l in lines:
                    payload += len(l)
    return payload, shown


def load(arm):
    p = os.path.join(R, f"arm_{arm}.jsonl")
    if not os.path.exists(p):
        return {}
    out = {}
    for l in open(p):
        r = json.loads(l)
        r["score"] = synth_score(insts[r["iid"]], r.get("final") or "")
        out[r["iid"]] = r
    return out


arms = {a: load(a) for a in "ABC"}
common = sorted(set(arms["A"]) & set(arms["B"]))
print({a: len(v) for a, v in arms.items()}, "A∩B:", len(common))
for a, v in arms.items():
    if v:
        errs = sum(1 for r in v.values() if r.get("error"))
        print(f"  arm {a}: mean score {np.mean([r['score'] for r in v.values()]):.3f}, errors {errs}, "
              f"median sec {np.median([r["sec"] for r in v.values() if r.get("sec") is not None]):.0f}")

# gate 1
d = np.array([arms["A"][i]["score"] - arms["B"][i]["score"] for i in common])
bs = [rng.choice(d, len(d)).mean() for _ in range(5000)]
g1 = d.mean() * 100
ci1 = np.percentile(bs, [2.5, 97.5]) * 100
print(f"\n[gate 1] A - B = {g1:.1f} points, 95% CI [{ci1[0]:.1f}, {ci1[1]:.1f}]  -> pass: {g1 >= 5 and ci1[0] > 0}")
for key in ["dataset", "context_len", "task_group"]:
    vals = sorted({insts[i][key] for i in common})
    print(f"   by {key}: " + ", ".join(
        f"{v}: A {np.mean([arms['A'][i]['score'] for i in common if insts[i][key] == v]):.2f} / "
        f"B {np.mean([arms['B'][i]['score'] for i in common if insts[i][key] == v]):.2f}"
        + (f" / C {np.mean([arms['C'][i]['score'] for i in arms['C'] if insts[i][key] == v]):.2f}" if arms['C'] else "")
        for v in vals))

# gate 2
cells = {}
for i in common:
    x = insts[i]
    cells.setdefault((x["task_group"], x["task"], x["context_len"]), []).append(i)
diffs, mA, mB = [], [], []
for c, ids in cells.items():
    per = {}
    for arm in "AB":
        sk = {i: skeleton(arms[arm][i]) for i in ids}
        pairs = [(i, j) for i, j in itertools.combinations(ids, 2) if insts[i]["dataset"] != insts[j]["dataset"]]
        if len(pairs) < 3:
            break
        per[arm] = np.mean([ned(sk[i], sk[j]) for i, j in pairs])
    if len(per) == 2:
        mA.append(per["A"]); mB.append(per["B"]); diffs.append(per["A"] - per["B"])
diffs = np.array(diffs)
bs2 = [rng.choice(diffs, len(diffs)).mean() for _ in range(5000)]
ci2 = np.percentile(bs2, [2.5, 97.5])
print(f"\n[gate 2] cross-domain skeleton distance over {len(diffs)} cells: A {np.mean(mA):.3f}, B {np.mean(mB):.3f}, "
      f"A-B {diffs.mean():.3f} [{ci2[0]:.3f}, {ci2[1]:.3f}]  -> pass: {ci2[1] < 0}")
print(f"   skeleton length median: A {np.median([len(skeleton(arms['A'][i])) for i in common])}, "
      f"B {np.median([len(skeleton(arms['B'][i])) for i in common])}")

# descriptive
for arm in "AB":
    lk = [leakage(arms[arm][i], insts[i]["context"]) for i in common]
    frac = [p / s for p, s in lk if s]
    print(f"\n[leakage] arm {arm}: payload chars shown to root, median {np.median([p for p, s in lk]):.0f}; "
          f"share of shown text that is payload, mean {np.mean(frac):.2f}; "
          f"share of context shown, mean {np.mean([p / len(insts[i]['context']) for (p, s), i in zip(lk, common)]):.2f}")
    it = [len(arms[arm][i].get("iters", [])) for i in common]
    sub = [sum(b["n_llm_calls"] for t in arms[arm][i].get("iters", []) for b in t["blocks"]) for i in common]
    print(f"   iterations median {np.median(it)}, hit-max {np.mean([x >= 20 for x in it]):.2f}; "
          f"sub-calls median {np.median(sub)}, zero-sub-call share {np.mean([s == 0 for s in sub]):.2f}")
print("\nVERDICT (frozen):", "PASS -> E01 may be considered" if (g1 >= 5 and ci1[0] > 0 and ci2[1] < 0) else "KILL")
