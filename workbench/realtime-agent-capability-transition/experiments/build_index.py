"""Index per-simulation outcomes of downloaded leaderboard trajectories -> results/sim_index.json."""
import glob, json, os, sys
ROOT = "/home/xiang/rt_ext/data/submissions"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "sim_index.json")
idx = json.load(open(OUT)) if os.path.exists(OUT) else {}
for sub in sys.argv[1:]:
    rows = []
    for traj in sorted(glob.glob(f"{ROOT}/{sub}/trajectories/*")):
        name = os.path.basename(traj)
        dom = next((x for x in ["banking_knowledge", "airline", "retail", "telecom"] if x in name), None)
        if os.path.isdir(traj):
            for f in glob.glob(f"{traj}/simulations/*.json"):
                try: d = json.load(open(f))
                except Exception: continue
                ri = d.get("reward_info") or {}
                rows.append(dict(dom=dom, task=str(d["task_id"]), trial=d.get("trial"), reward=ri.get("reward"),
                                 term=d.get("termination_reason"), auth=(d.get("auth_classification") or {}).get("status"),
                                 dur=float(d.get("duration") or 0), path=os.path.relpath(f, ROOT)))
        elif name.endswith(".json"):
            d = json.load(open(traj))
            for s in d.get("simulations", []):
                ri = s.get("reward_info") or {}
                rows.append(dict(dom=dom, task=str(s["task_id"]), trial=s.get("trial"), reward=ri.get("reward"),
                                 term=s.get("termination_reason"), auth=None, dur=float(s.get("duration") or 0),
                                 path=os.path.relpath(traj, ROOT)))
    idx[sub] = rows
    print(sub, len(rows))
json.dump(idx, open(OUT, "w"))
