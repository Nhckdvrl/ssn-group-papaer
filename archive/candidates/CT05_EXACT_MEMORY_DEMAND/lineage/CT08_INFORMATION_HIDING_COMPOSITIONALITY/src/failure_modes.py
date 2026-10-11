"""Descriptive: classify each arm's outcomes (post hoc, no re-scoring)."""
import collections, json, os, re, sys
sys.argv = ["x"]
src = open(os.path.join(os.path.dirname(__file__), "analyze_e00.py")).read().split("# ---- skeletons ----")[0]
exec(src)
for arm in "AB":
    recs = {}
    for l in open(os.path.join(R, f"arm_{arm}.jsonl")):
        r = json.loads(l); recs[r["iid"]] = r
    cat = collections.Counter()
    for r in recs.values():
        f = (r.get("final") or "").strip()
        s = synth_score(insts[r["iid"]], f)
        if r.get("error"):
            cat["error"] += 1; continue
        its = r.get("iters", [])
        assigned = set()
        for it in its:
            for b in it["blocks"]:
                assigned |= set(re.findall(r"^\s*([A-Za-z_]\w*)\s*=", b["code"], re.M))
        if f in assigned:
            cat["FINAL(varname) returned literally"] += 1
        elif len(its) == 1:
            cat["answered in turn 1: " + ("right" if s > 0.5 else "wrong")] += 1
        else:
            cat["multi-turn: " + ("right" if s > 0.5 else "wrong")] += 1
    print(arm, len(recs), dict(sorted(cat.items())))
