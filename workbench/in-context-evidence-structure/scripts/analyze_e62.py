"""Paired field-relocation effects and context-bootstrap mediation contrasts."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / "run.json").read_text())
    rows = [json.loads(s) for s in (d / "behavior.jsonl").read_text().splitlines()]
    margins = {c: np.array([np.array(r["scores"][c]) * r["signs"] for r in rows]) for c in rows[0]["scores"]}
    means = {c: x.mean(1) for c, x in margins.items()}
    acc = {c: (x > 0).mean(1) for c, x in margins.items()}
    out = {"run": run, "conditions": {}, "layout_contrasts": {}}
    rng = np.random.default_rng(620)
    ix = rng.integers(len(rows), size=(4000, len(rows)))
    for c in margins:
        out["conditions"][c] = {"accuracy": interval(acc[c]), "correct_margin": interval(means[c])}
        parts = c.split(".")
        if len(parts) == 5:
            vocab, layout, donor, site, channel = parts
            root = vocab + "." + layout + "."
            num = means[root + "base"] - means[c]
            den = means[root + "base"] - means[root + donor]
            out["conditions"][c]["raw_effect"] = interval(num)
            if den.mean() > 0.20:
                rat = num[ix].mean(1) / np.maximum(den[ix].mean(1), 1e-6)
                out["conditions"][c]["fraction"] = {"mean": float(num.mean() / den.mean()), "ci95": np.quantile(rat, [0.025, 0.975]).tolist()}
            else:
                out["conditions"][c]["fraction"] = {"undefined": "Complete donor effect <=0.20 nats"}
    for vocab in ("yes_no", "toxic_safe"):
        result = {}
        for suffix in ("base", "instruction", "query_source_first"):
            result[suffix + "_accuracy_after_minus_before"] = interval(acc[f"{vocab}.after.{suffix}"] - acc[f"{vocab}.before.{suffix}"])
        for donor, site, channel in (("source", "source_name", "key"), ("source", "label_anchor", "kv"),
                                      ("label", "source_name", "kv"), ("label", "label_anchor", "kv")):
            ratios = []
            for layout in ("before", "after"):
                root = vocab + "." + layout + "."
                num = means[root + "base"] - means[root + f"{donor}.{site}.{channel}"]
                den = means[root + "base"] - means[root + donor]
                if den.mean() <= 0.20:
                    ratios = []
                    break
                ratios.append((float(num.mean() / den.mean()), num[ix].mean(1) / np.maximum(den[ix].mean(1), 1e-6)))
            if ratios:
                result[f"{donor}.{site}.{channel}_fraction_after_minus_before"] = {
                    "mean": ratios[1][0] - ratios[0][0],
                    "ci95": np.quantile(ratios[1][1] - ratios[0][1], [0.025, 0.975]).tolist()}
        out["layout_contrasts"][vocab] = result
    (d / "analysis.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["layout_contrasts"], indent=2))


if __name__ == "__main__":
    main()
