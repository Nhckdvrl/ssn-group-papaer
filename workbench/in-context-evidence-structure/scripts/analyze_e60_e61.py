"""Context-paired analysis of matched verbalizers or crossed cache interventions."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["e60", "e61"])
    ap.add_argument("directory")
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / "run.json").read_text())
    rows = [json.loads(s) for s in (d / "behavior.jsonl").read_text().splitlines()]
    margins = {c: np.array([np.array(r["scores"][c]) * r["signs"] for r in rows]) for c in rows[0]["scores"]}
    out = {"run": run, "conditions": {}}
    means = {c: v.mean(1) for c, v in margins.items()}
    acc = {c: (v > 0).mean(1) for c, v in margins.items()}
    for c in margins:
        out["conditions"][c] = {"accuracy": interval(acc[c]), "correct_margin": interval(means[c])}
    if a.kind == "e60":
        out["contrasts"] = {
            "yes_minus_toxic_accuracy": interval(acc["yes_no.base"] - acc["toxic_safe.base"]),
            "yes_minus_toxic_single_accuracy": interval(acc["yes_no.single"] - acc["toxic_safe.single"]),
            "verbalizer_extra_mixed_gap_accuracy": interval((acc["yes_no.base"] - acc["toxic_safe.base"]) -
                                                           (acc["yes_no.single"] - acc["toxic_safe.single"]))}
        for vocab in ("yes_no", "toxic_safe"):
            for c in margins:
                if c.startswith(vocab + "."):
                    out["conditions"][c]["patch_minus_base_accuracy"] = interval(acc[c] - acc[vocab + ".base"])
                    out["conditions"][c]["patch_minus_base_margin"] = interval(means[c] - means[vocab + ".base"])
    else:
        out["interactions"] = {}
        for name in ("V", "YKV"):
            joint = "K+" + name
            out["interactions"][name] = {
                "J": interval(means[joint] - means["K"] - means[name] + means["base"]),
                "joint_minus_base_margin": interval(means[joint] - means["base"]),
                "joint_minus_K_margin": interval(means[joint] - means["K"]),
                "joint_minus_payload_margin": interval(means[joint] - means[name])}
        out["natural_double_minus_base"] = interval(means["natural_double"] - means["base"])
    (d / "analysis.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "run"}, indent=2))


if __name__ == "__main__":
    main()
