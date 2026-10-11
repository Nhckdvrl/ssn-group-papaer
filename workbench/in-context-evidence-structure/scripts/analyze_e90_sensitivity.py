"""Rule-contrast coupling: post-hoc in seeds 90001/190001, frozen for 290001.

Keep the original signed readout. Differentiate average direction, sensitivity,
output-label bias, and answer changes; none substitutes for another.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from e90_source_isolation import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    args = ap.parse_args()
    p = Path(args.source)
    rows = [json.loads(s) for s in (p / "behavior.jsonl").read_text().splitlines()]
    run = json.loads((p / "run.json").read_text())
    assert len(rows) == run["args"]["n"]
    assert run["numeric_max_error"] <= .001
    gold = np.array([r["gold"] for r in rows])
    out = {"seed": run["args"]["seed"], "n_contexts": len(rows),
           "analysis_status": "independent frozen readout" if run["args"]["seed"] == 290001 else "POST-HOC exploratory readout",
           "formula": "d_i = mean_q(g_q * (z_aligned - z_conflict)); magnitude = mean_i |d_i|",
           "conditions": {}}
    for k in ["native", "early", "late", "both", "instruction", "adapter", "adapter_late"]:
        c = np.array([r["conditions"][f"conflict_{k}"]["z"] for r in rows])
        a = np.array([r["conditions"][f"aligned_{k}"]["z"] for r in rows])
        d = ((a-c)*gold).mean(1)
        bias = (a-c).mean(1)
        out["conditions"][k] = {
            "signed_rule_effect": interval(d), "absolute_rule_effect": interval(np.abs(d)),
            "signed_bias_effect": interval(bias), "absolute_bias_effect": interval(np.abs(bias)),
            "candidate_answer_flip_rate": interval(((a > 0) != (c > 0)).mean(1)),
            "contexts_positive": int((d > .01).sum()), "contexts_negative": int((d < -.01).sum()),
            "context_rule_effects": d.tolist(),
        }
    (p / "rule_sensitivity.json").write_text(json.dumps(out, indent=2) + "\n")
    for k, v in out["conditions"].items():
        print(k, "absolute rule effect", v["absolute_rule_effect"],
              "sign counts", v["contexts_positive"], v["contexts_negative"],
              "label flips", v["candidate_answer_flip_rate"], flush=True)


if __name__ == "__main__":
    main()
