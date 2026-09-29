"""E03: are retail auth calls issued with zip codes the user has NOT yet said (premature / fabricated slot filling)?
For each find_user_id_by_name_zip call: normalize all user speech before the call to a digit string and
check whether the zip appears; if not, check whether it appears later (premature) or never (fabricated/misheard)."""
import json, sys, re, collections, os
ROOT = "/home/xiang/rt_ext/data/submissions"
idx = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "sim_index.json")))
W = {"zero": "0", "oh": "0", "o": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
     "six": "6", "seven": "7", "eight": "8", "nine": "9"}
def digits(text):
    toks = re.findall(r"[a-z]+|\d", text.lower())
    return "".join(W.get(t, t) if (t in W or t.isdigit()) else "" for t in toks)
for sub in sys.argv[1:]:
    c = collections.Counter()
    for r in idx[sub]:
        if r["dom"] != "retail": continue
        d = json.load(open(f"{ROOT}/{r['path']}"))
        user_before = ""
        ticks = d["ticks"]
        full_user = "".join((t.get("user_chunk") or {}).get("content") or "" for t in ticks)
        for t in ticks:
            for tc in t.get("agent_tool_calls") or []:
                if tc["name"] == "find_user_id_by_name_zip":
                    z = str((tc.get("arguments") or {}).get("zip", ""))
                    c["calls"] += 1
                    if z and z in digits(user_before): c["said_before"] += 1
                    elif z and z in digits(full_user): c["said_after"] += 1
                    else: c["never_said"] += 1
            user_before += (t.get("user_chunk") or {}).get("content") or ""
    n = max(1, c["calls"])
    print(f"{sub[:40]:40s} zip-calls={c['calls']} said_before={c['said_before']/n:.2f} said_after(premature)={c['said_after']/n:.2f} never_said={c['never_said']/n:.2f}")
