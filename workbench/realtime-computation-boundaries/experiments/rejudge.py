"""Re-judge saved epistemic replies with the current judge prompt (keeps DELEGATE labels)."""
import json, sys
from openai import OpenAI
from epistemic_eval import judge
jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
qs = {q["id"]: q for q in json.load(open("probes/epistemic.json"))}
for f in sys.argv[1:]:
    d = json.load(open(f))
    for x in d:
        if x["label"] != "DELEGATE":
            x["label"] = judge(jc, x["cat"], qs[x["id"]][x["lang"]], x["reply"])
    json.dump(d, open(f, "w"), indent=1, ensure_ascii=False)
    import collections
    c = collections.Counter((x["cat"], x["label"]) for x in d)
    for cat in ["live", "private", "action", "known"]:
        print(f.split("/")[-1], cat, dict(sorted({k[1]: v for k, v in c.items() if k[0] == cat}.items())))
