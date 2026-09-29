"""Render a tick-based voice simulation as a readable transcript (utterances + tool calls, in seconds)."""
import glob
import json
import sys

TICK = 0.2


def render(d, maxlen=400):
    lines, cur = [], {}

    def flush(role):
        if role in cur:
            s, txt, _ = cur.pop(role)
            lines.append((s, f"{'AGENT' if role == 'a' else 'USER '} {txt.strip()[:maxlen]}"))

    for t in d["ticks"]:
        tid = t["tick_id"]
        for role, key in (("a", "agent_chunk"), ("u", "user_chunk")):
            txt = (t.get(key) or {}).get("content")
            if txt:
                if role in cur and tid - cur[role][2] <= 4:
                    cur[role] = (cur[role][0], cur[role][1] + txt, tid)
                else:
                    flush(role)
                    cur[role] = (tid, txt, tid)
        res = {r.get("id"): r for r in t.get("agent_tool_results") or []}
        for c in t.get("agent_tool_calls") or []:
            r = res.get(c.get("id")) or {}
            lines.append((tid, f"  TOOL {c['name']}({json.dumps(c.get('arguments'))[:200]}) -> "
                               f"{'ERR ' if r.get('error') else ''}{str(r.get('content'))[:160]}"))
        for c in t.get("user_tool_calls") or []:
            lines.append((tid, f"  UTOOL {c['name']}({json.dumps(c.get('arguments'))[:120]})"))
    for role in list(cur):
        flush(role)
    lines.sort(key=lambda x: x[0])
    out = [f"{s*TICK:7.1f}s {l}" for s, l in lines]
    ri = d.get("reward_info") or {}
    out.append(f"== task {d['task_id']} reward={ri.get('reward')} term={d.get('termination_reason')} "
               f"db={ri.get('db_check')} nl={[(a.get('nl_assertion'), a.get('met')) for a in ri.get('nl_assertions') or []]}")
    return "\n".join(out)


def find(sub, domain, task):
    for f in glob.glob(f"/home/xiang/rt_ext/data/submissions/{sub}/trajectories/*{domain}*/simulations/*.json"):
        d = json.load(open(f))
        if str(d["task_id"]) == str(task):
            return d


if __name__ == "__main__":
    sub, domain, task = sys.argv[1:4]
    print(render(find(sub, domain, task)))
