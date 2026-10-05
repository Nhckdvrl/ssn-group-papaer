"""Does a single flipped demo's influence depend on its similarity to the query?
usage: analyze_similarity.py DATA_DIR RESULT_GLOB"""
import glob, json, sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
rows = {}
for l in open(sys.argv[1] + "/rows.jsonl"):
    r = json.loads(l)
    if r["cond"] == "allA" or r["cond"].startswith("single_"):
        rows[r["uid"]] = r
sc = {}
for f in glob.glob(sys.argv[2]):
    for l in open(f):
        s = json.loads(l)
        if s["uid"] in rows:
            sc[s["uid"]] = s["lp"]
recs = []
for uid, r in rows.items():
    lo1 = sc[uid][1] - sc[uid][0]; lo = lo1 if r["query_label_B"] == 1 else -lo1
    b = r["base"]; X = np.array(b["X"]); xq = np.array(b["xq"]); a = b["rule_attr"]
    rec = {"base": r["base_id"], "cond": r["cond"], "lo_B": lo}
    if r["cond"].startswith("single_"):
        t = int(r["cond"].split("_")[1]) - 1
        x = X[t]
        rec.update({"t": t + 1, "same_rule_val": int(x[a] == xq[a]),
                    "distractor_sim": int(sum(x[j] == xq[j] for j in range(len(xq)) if j != a))})
    recs.append(rec)
df = pd.DataFrame(recs)
ref = df[df.cond == "allA"].set_index("base").lo_B
s = df[df.cond != "allA"].copy(); s["d"] = s.lo_B - s.base.map(ref)
print(s.groupby("same_rule_val").d.agg(["mean", "sem", "size"]).round(3))
print(s.groupby("distractor_sim").d.agg(["mean", "sem", "size"]).round(3))
print(s.groupby(["same_rule_val", "distractor_sim"]).d.mean().unstack().round(2))
m = smf.mixedlm("d ~ same_rule_val + distractor_sim + t", s, groups=s["base"]).fit()
print(m.summary().tables[1])
s["sim"] = s.same_rule_val * 2 - 1  # +1 same rule value, -1 opposite
s["late"] = (s.t > 8).astype(int)
m2 = smf.mixedlm("d ~ same_rule_val * t + distractor_sim * t", s, groups=s["base"]).fit()
print(m2.summary().tables[1])
print(s.groupby(["same_rule_val", "late"]).d.mean().unstack().round(3))
