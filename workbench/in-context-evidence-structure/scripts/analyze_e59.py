"""Paired context bootstrap for E59; do not normalize weak donor effects."""
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
    run = json.loads((d / "run.json").read_text())  # Require completed experiment.
    rows = [json.loads(s) for s in (d / "behavior.jsonl").read_text().splitlines()]
    margins = {c: np.array([np.array(r["scores"][c]) * r["signs"] for r in rows]) for c in rows[0]["scores"]}
    out = {"run": run, "conditions": {}, "donor_effects": {}}
    means = {c: v.mean(1) for c, v in margins.items()}
    rng = np.random.default_rng(590)
    ix = rng.integers(len(rows), size=(4000, len(rows)))
    for donor in ("source", "label"):
        out["donor_effects"][donor] = interval(means["base"] - means[donor])
    for c, v in margins.items():
        numer = means["base"] - means[c]
        result = {"accuracy": interval((v > 0).mean(1)), "correct_margin": interval(means[c]),
                  "base_minus_condition_margin": interval(numer)}
        if "." in c:
            donor, site, channel = c.split(".")
            denom = means["base"] - means[donor]
            if denom.mean() > 0.2:
                denboot = denom[ix].mean(1)
                ratios = numer[ix].mean(1) / np.maximum(denboot, 1e-6)
                result["fraction_of_donor_effect"] = {"mean": float(numer.mean() / denom.mean()),
                                                        "ci95": np.quantile(ratios, [0.025, 0.975]).tolist()}
            else:
                result["fraction_of_donor_effect"] = {"undefined": "Complete donor effect <= 0.20 nats"}
        out["conditions"][c] = result
    # This difference tests relative mediation of two effects, not isolated circuits.
    out["relative_mediation"] = {}
    if all(out["donor_effects"][c]["mean"] > 0.2 for c in ("source", "label")):
        ds = means["base"] - means["source"]
        dl = means["base"] - means["label"]
        for site in ("source_name", "label_prediction", "label_anchor", "post_label", "source_span", "non_anchor", "full"):
            for channel in ("key", "value", "kv"):
                ns = means["base"] - means[f"source.{site}.{channel}"]
                nl = means["base"] - means[f"label.{site}.{channel}"]
                boot = ns[ix].mean(1) / np.maximum(ds[ix].mean(1), 1e-6) - nl[ix].mean(1) / np.maximum(dl[ix].mean(1), 1e-6)
                out["relative_mediation"][f"{site}.{channel}"] = {
                    "source_minus_label_fraction": float(ns.mean() / ds.mean() - nl.mean() / dl.mean()),
                    "ci95": np.quantile(boot, [0.025, 0.975]).tolist()}
    (d / "mediation_analysis.json").write_text(json.dumps(out, indent=2))
    print("base", out["conditions"]["base"]["accuracy"])
    print("donor effects", out["donor_effects"])
    for donor in ("source", "label"):
        for site in ("source_name", "label_prediction", "label_anchor", "post_label", "non_anchor", "full"):
            print(donor, site, {c: out["conditions"][f"{donor}.{site}.{c}"].get("fraction_of_donor_effect") for c in ("key", "value", "kv")})


if __name__ == "__main__":
    main()
