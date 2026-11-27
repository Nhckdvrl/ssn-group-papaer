"""E15a: pull AZR's public W&B training histories (anonymous GraphQL), no GPU.

Writes results/E15a_azr_wandb_history.csv (one row per run x logged step, selected metrics).
"""
import csv, json, sys, time, urllib.request

ENTITY, PROJECT = "andrewzhao112", "AbsoluteZeroReasoner"
URL = "https://api.wandb.ai/graphql"
KEYS = []
for t in ("gen_code_i", "gen_code_o", "gen_code_f"):
    KEYS += [f"{t}/num_valid_programs", f"{t}/response_length/mean"]
for t in ("gen_code_i", "gen_code_o"):
    KEYS += [f"{t}/complexity", f"{t}/halstead", f"{t}/answer_diversity"]
KEYS += ["gen_code_f/input_answer_diversity", "gen_code_f/output_answer_diversity"]
for t in ("pred_code_i", "pred_code_o", "pred_code_f"):
    KEYS += [f"{t}/correct_response_length/mean", f"{t}/response_length/mean"]
KEYS += ["types/input_types/total_unique_values", "types/output_types/total_unique_values",
         "types/input_types/distinct_types", "types/output_types/distinct_types", "accuracy"]


def gql(query, variables):
    req = urllib.request.Request(URL, data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            if "errors" in d:
                raise RuntimeError(d["errors"])
            return d["data"]
        except Exception as e:  # retry transient failures
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("gql failed")


runs = gql("""query($e:String!,$p:String!){project(name:$p,entityName:$e){runs(first:50){edges{node{name displayName state}}}}}""",
           {"e": ENTITY, "p": PROJECT})["project"]["runs"]["edges"]
rows = []
for edge in runs:
    n = edge["node"]
    # sampledHistory only returns rows where every key in a spec is present, so query one key per spec
    bystep = {}
    for k in KEYS:
        spec = json.dumps({"keys": ["_step", k], "samples": 100000})
        d = gql("""query($e:String!,$p:String!,$r:String!,$s:JSONString!){project(name:$p,entityName:$e){run(name:$r){sampledHistory(specs:[$s])}}}""",
                {"e": ENTITY, "p": PROJECT, "r": n["name"], "s": spec})
        for h in d["project"]["run"]["sampledHistory"][0]:
            bystep.setdefault(h["_step"], {})[k] = h.get(k)
    print(n["displayName"], n["state"], len(bystep), "steps", file=sys.stderr)
    for s in sorted(bystep):
        row = {"run": n["displayName"], "state": n["state"], "step": s}
        row.update({k: bystep[s].get(k) for k in KEYS})
        rows.append(row)

out = sys.argv[1]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["run", "state", "step"] + KEYS)
    w.writeheader()
    w.writerows(rows)
print("wrote", out, len(rows), file=sys.stderr)
