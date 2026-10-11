"""Build decision checkpoints from natural agent trajectories (model-agnostic messages).

Sources (logged trajectories, not constructed for this study):
  swe  : SWE-bench/SWE-smith-trajectories shard 0 (SWE-agent harness, text commands, Claude 3.7 logs)
  tau  : Salesforce/APIGen-MT-5k (tau-bench airline/retail harness, native function calls)

Each checkpoint = (trajectory, decision index k). History = messages[:k]; target = messages[k].
Event types: system / task / assistant / think / call / obs / user.
"""
import glob, json, random, re, sys
import pandas as pd

H = "/home/xiang/.cache/huggingface/hub/"
rng = random.Random(0)
N_TRAJ = int(sys.argv[1]) if len(sys.argv) > 1 else 40
out = sys.argv[2] if len(sys.argv) > 2 else "checkpoints.jsonl"


def pick_decisions(cands, n=3):
    """spread picks over early / mid / late decision candidates"""
    if len(cands) <= n:
        return cands
    idx = sorted({round(i * (len(cands) - 1) / (n - 1)) for i in range(n)})
    return [cands[i] for i in idx]


def swe():
    d = pd.read_parquet(glob.glob(H + "datasets--SWE-bench--SWE-smith-trajectories/snapshots/*/data/ticks-00000-of-00008.parquet")[0])
    rows = list(d.itertuples())
    rng.shuffle(rows)
    recs = []
    for r in rows:
        m = json.loads(r.messages)
        if not (12 <= len(m) <= 60):
            continue
        msgs = []
        for i, x in enumerate(m):
            c = x["content"] if isinstance(x["content"], str) else "".join(p.get("text", "") for p in x["content"])
            role = x["role"]
            if role == "system":
                ev = "system"
            elif role == "user" and i <= 1:
                ev = "task"
            elif role == "user":
                ev = "obs" if c.startswith("OBSERVATION") else "user"
            else:
                ev = "assistant"
            msgs.append({"role": role, "content": c, "ev": ev})
        cands = [k for k, x in enumerate(msgs) if x["ev"] == "assistant" and k >= 6 and "```" in x["content"]]
        if len(cands) < 3:
            continue
        for k in pick_decisions(cands):
            tgt = msgs[k]["content"]
            blocks = [mm.span(1) for mm in re.finditer(r"```(?:\w*\n)?(.*?)```", tgt, re.S)]
            recs.append({"src": "swe", "traj": r.traj_id, "k": k, "messages": msgs[:k + 1],
                         "action_char_span": list(blocks[-1]) if blocks else None})
        if len({x["traj"] for x in recs}) >= N_TRAJ:
            break
    return recs


def _args(call):
    a = call.get("arguments", {})
    if isinstance(a, str):
        try:
            a = json.loads(a)
        except Exception:
            a = {"input": a}
    return a if isinstance(a, dict) else {"input": a}


def tau():
    a = json.load(open(glob.glob(H + "datasets--Salesforce--APIGen-MT-5k/snapshots/*/apigen-mt_5k.json")[0]))
    idx = list(range(len(a)))
    rng.shuffle(idx)
    recs = []
    for j in idx:
        x = a[j]
        conv = x["conversations"]
        if len(conv) < 16:
            continue
        tools = json.loads(x["tools"]) if isinstance(x["tools"], str) else x["tools"]
        msgs = [{"role": "system", "content": x["system"], "ev": "system"}]
        first_user = True
        for y in conv:
            f, v = y["from"], y["value"]
            if f == "human":
                msgs.append({"role": "user", "content": v, "ev": "task" if first_user else "user"})
                first_user = False
            elif f == "gpt":
                msgs.append({"role": "assistant", "content": v, "ev": "assistant"})
            elif f == "function_call":
                call = json.loads(v)
                msgs.append({"role": "assistant", "content": "", "ev": "think" if call["name"] == "think" else "call",
                             "tool_calls": [{"type": "function", "function": {"name": call["name"], "arguments": _args(call)}}]})
            elif f == "observation":
                msgs.append({"role": "tool", "content": v if v else "", "ev": "obs"})
        cands = [k for k, m in enumerate(msgs) if m["ev"] == "call" and k >= 5]
        if len(cands) < 2:
            continue
        for k in pick_decisions(cands):
            recs.append({"src": "tau", "traj": f"apigen-{j}", "k": k, "messages": msgs[:k + 1], "tools": tools,
                         "action_char_span": None})
        if len({r["traj"] for r in recs}) >= N_TRAJ:
            break
    return recs


recs = swe() + tau()
with open(out, "w") as f:
    for i, r in enumerate(recs):
        r["cid"] = i
        f.write(json.dumps(r) + "\n")
print(len(recs), "checkpoints", {s: sum(r["src"] == s for r in recs) for s in ("swe", "tau")})
