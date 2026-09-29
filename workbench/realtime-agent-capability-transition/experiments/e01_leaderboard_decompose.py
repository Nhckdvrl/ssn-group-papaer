"""E01: decompose public tau-voice leaderboard trajectories.

For each voice submission x domain: pass@1, authentication outcome (the harness's own
LLM auth classifier), pass | auth succeeded, termination reasons, and the reviewer's
agent-error tags. Writes results/e01_leaderboard.json and prints a table.
"""
import collections
import glob
import json
import os
import sys

ROOT = "/home/xiang/rt_ext/data/submissions"
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "e01_leaderboard.json")


def load_voice(sub_dir):
    rows = []
    for traj in sorted(glob.glob(f"{sub_dir}/trajectories/*/")):
        name = os.path.basename(traj.rstrip("/"))
        dom = next((d for d in ["banking_knowledge", "airline", "retail", "telecom"] if d in name), None)
        for f in glob.glob(f"{traj}/simulations/*.json"):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            ri = d.get("reward_info") or {}
            auth = (d.get("auth_classification") or {}).get("status")
            rev = d.get("review") or {}
            tags = []
            for e in rev.get("errors") or []:
                if e.get("source") == "agent":
                    tags += [f"{e.get('severity')}:{t}" for t in e.get("error_tags") or []]
            rows.append(dict(domain=dom, task=d["task_id"], reward=ri.get("reward"), auth=auth,
                             term=d.get("termination_reason"), tags=tags,
                             user_error=rev.get("critical_user_error"),
                             dur=float(d.get("duration") or 0)))
    return rows


def summarize(rows):
    out = {}
    for dom in sorted({r["domain"] for r in rows}):
        rs = [r for r in rows if r["domain"] == dom and r["reward"] is not None]
        if not rs:
            continue
        n = len(rs)
        p = sum(r["reward"] >= 1 for r in rs) / n
        au = collections.Counter(r["auth"] for r in rs)
        ok = [r for r in rs if r["auth"] in ("succeeded", "not_needed")]
        pa = sum(r["reward"] >= 1 for r in ok) / len(ok) if ok else None
        tags = collections.Counter(t for r in rs if r["reward"] < 1 for t in r["tags"] if t.startswith("critical"))
        out[dom] = dict(n=n, pass1=p, auth=dict(au), pass_given_auth=pa, n_auth_ok=len(ok),
                        auth_fail_rate=au.get("failed", 0) / n,
                        term=dict(collections.Counter(r["term"] for r in rs)),
                        crit_tags=dict(tags.most_common(8)),
                        critical_user_error=sum(bool(r["user_error"]) for r in rs) / n,
                        mean_dur=sum(r["dur"] for r in rs) / n)
    return out


if __name__ == "__main__":
    subs = sys.argv[1:] or sorted(os.listdir(ROOT))
    res = {}
    for s in subs:
        rows = load_voice(f"{ROOT}/{s}")
        if rows:
            res[s] = summarize(rows)
    prev = json.load(open(OUT)) if os.path.exists(OUT) else {}
    prev.update(res)
    json.dump(prev, open(OUT, "w"), indent=1)
    for s, v in res.items():
        for dom, x in v.items():
            pga = f"{x['pass_given_auth']:.2f}" if x["pass_given_auth"] is not None else "-"
            print(f"{s[:42]:42s} {dom:9s} n={x['n']:3d} pass={x['pass1']:.2f} authfail={x['auth_fail_rate']:.2f} "
                  f"pass|auth={pga} ({x['n_auth_ok']}) userErr={x['critical_user_error']:.2f} dur={x['mean_dur']:.0f}s")
