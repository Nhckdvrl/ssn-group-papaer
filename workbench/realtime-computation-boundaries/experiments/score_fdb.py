"""Score driver outputs with FDB-v3's own strict pass logic (tool multiset match + exact args), and
decompose where the pipeline broke: trigger (no delegate) / tools / args / reintegration (result never spoken).
Also scores a slow-only reference: the same backend given the human reference transcript instead of the
fast model's objective (visibility control), computed on the fly with --slow-ref."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/xiang/rt_ext/Full-Duplex-Bench/v3")
from evaluate_pass_rate import evaluate_scenario_pass  # noqa: E402


def score(runs):
    rows = []
    for r in runs:
        ev = evaluate_scenario_pass(r["meta"], r["actual_tool_calls"])
        rows.append(dict(id=r["id"], delegated=bool(r["delegates"]), n_delegates=len(r["delegates"]),
                         tool_ok=ev["checks"]["tool_selection"]["passed"],
                         args_ok=ev["checks"].get("argument_accuracy", {}).get("passed", False),
                         passed=ev["passed"], spoke_result=bool(r.get("spoken_after_backend", "").strip()),
                         reason=ev["failure_reason"]))
    return rows


def summary(name, rows):
    n = len(rows)
    f = lambda k: sum(r[k] for r in rows)
    d = [r for r in rows if r["delegated"]]
    print(f"{name:34s} n={n:3d} delegated={f('delegated')/n:.2f} tool_ok={f('tool_ok')/n:.2f} "
          f"pass={f('passed')/n:.2f} | given delegated: pass={sum(r['passed'] for r in d)/max(1,len(d)):.2f} "
          f"spoke_result={sum(r['spoke_result'] for r in d)/max(1,len(d)):.2f}")
    return dict(n=n, delegated=f("delegated") / n, tool_ok=f("tool_ok") / n, passed=f("passed") / n,
                pass_given_delegated=sum(r["passed"] for r in d) / max(1, len(d)),
                spoke_given_delegated=sum(r["spoke_result"] for r in d) / max(1, len(d)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {}
    for f in a.files:
        rows = score(json.load(open(f)))
        out[Path(f).stem] = dict(summary=summary(Path(f).stem, rows), rows=rows)
    json.dump(out, open(a.out, "w"), indent=1)
