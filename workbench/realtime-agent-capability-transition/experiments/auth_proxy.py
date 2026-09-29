"""Programmatic auth proxy for retail: did any find_user_id_* call succeed? Also counts failed auth attempts
and 'premature' auth calls (issued before the user has said anything since the agent's last request)."""
import json, sys, collections, os
ROOT = "/home/xiang/rt_ext/data/submissions"
idx = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "sim_index.json")))
AUTH = {"find_user_id_by_email", "find_user_id_by_name_zip"}
for sub in sys.argv[1:]:
    rows = [r for r in idx[sub] if r["dom"] == "retail" and r["reward"] is not None]
    c = collections.Counter()
    for r in rows:
        d = json.load(open(f"{ROOT}/{r['path']}"))
        ok, fails = False, 0
        for t in d["ticks"]:
            res = {x.get("id"): x for x in t.get("agent_tool_results") or []}
            for tc in t.get("agent_tool_calls") or []:
                if tc["name"] in AUTH:
                    e = (res.get(tc.get("id")) or {}).get("error")
                    if e: fails += 1
                    else: ok = True
        c["n"] += 1; c["auth_ok"] += ok; c["pass"] += r["reward"] >= 1
        c["pass_auth_ok"] += ok and r["reward"] >= 1; c["auth_fail_calls"] += fails
    n = max(1, c["n"])
    print(f"{sub[:40]:40s} n={n} pass={c['pass']/n:.2f} auth_ok={c['auth_ok']/n:.2f} "
          f"pass|auth={c['pass_auth_ok']/max(1,c['auth_ok']):.2f} failed_auth_calls/sim={c['auth_fail_calls']/n:.2f}")
