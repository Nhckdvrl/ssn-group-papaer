"""CPU summaries from sealed E144/E145 per-token raw arrays; no model selection.

File bootstrap is paired and conditional on the fixed trained cohort/maps.
E144 also reports the eight independent source-map units and a crossed bootstrap.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import e144145_common as c


def file_groups(rows):
    labels = list(dict.fromkeys((r["source"], r["file_id"]) for r in rows))
    return [np.array([i for i, r in enumerate(rows) if (r["source"], r["file_id"]) == label]) for label in labels]


def input_stats(values, rows, seed=144001):
    values = np.asarray(values, np.float64)
    if values.shape != (len(rows),) or not np.isfinite(values).all():
        raise ValueError("One finite token-average per fixed equal-length sequence required")
    groups = file_groups(rows)
    sums = np.array([values[i].sum() for i in groups])
    counts = np.array([len(i) for i in groups])
    draws = np.random.default_rng(seed).integers(0, len(groups), (1000, len(groups)))
    samples = sums[draws].sum(-1) / counts[draws].sum(-1)
    return {"point": float(values.mean()), "input_file_ci95": np.quantile(samples, [.025, .975]).tolist(),
            "file_clusters": len(groups), "sequences": len(rows), "bootstrap_seed": seed}


def crossed_stats(by_mc_sequence, rows):
    """Eight independent iid base maps, each with its three cyclic shifts intact."""
    values = np.asarray(by_mc_sequence, np.float64)
    if values.shape != (8, len(rows)):
        raise ValueError("Eight MC units required")
    point = input_stats(values.mean(0), rows)
    point["source_base_points"] = values.mean(1).tolist()
    point["source_mc_se"] = float(values.mean(1).std(ddof=1) / np.sqrt(8))
    groups = file_groups(rows)
    rng = np.random.default_rng(144002)
    samples = []
    for _ in range(1000):
        mc = rng.integers(0, 8, 8)
        inputs = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        samples.append(float(values[np.ix_(mc, inputs)].mean()))
    point["crossed_file_source_ci95"] = np.quantile(samples, [.025, .975]).tolist()
    point["crossed_bootstrap_seed"] = 144002
    point["scope"] = "Conditional on these three trained students; MC units are source assignments, not training seeds."
    return point


def read_batches(experiment):
    manifest = c.read(c.WB / f"results/{experiment}/manifest.json")
    if manifest["status"] != "complete" or manifest.get("read_only_source_checks") != "passed" or len(manifest["raw_batches"]) != 4:
        raise ValueError("All four batches and post-run read-only checks required")
    if manifest["source_sha256"] != c.code_proof():
        raise ValueError("Analysis/run code differs; preserve old run and register a new analysis if needed")
    batches = []
    for info in manifest["raw_batches"]:
        if c.sha(info["path"]) != info["sha256"]:
            raise ValueError("Raw batch SHA mismatch")
        with np.load(info["path"], allow_pickle=False) as raw:
            batches.append({k: np.array(raw[k], copy=True) for k in raw.files})
    rows = c.read(c.WB / "results/e144/selected.json")["rows"]
    if manifest["selected_sha256"] != c.sha(c.WB / "results/e144/selected.json"):
        raise ValueError("Input selection SHA mismatch")
    return manifest, batches, rows


def summaries_by_source(values, rows, seed):
    result = {}
    for source in sorted({r["source"] for r in rows}):
        indices = np.array([i for i, r in enumerate(rows) if r["source"] == source])
        result[source] = input_stats(values[indices], [rows[i] for i in indices], seed)
    return result


def analyze_e144(manifest, batches, rows):
    names = batches[0]["names"].tolist()
    pred = np.concatenate([b["metrics"] for b in batches], axis=1)
    teacher = np.concatenate([b["teacher_metrics"] for b in batches], axis=1)
    layer = np.concatenate([b["layer"] for b in batches], axis=1)
    moments = np.concatenate([b["moments"] for b in batches], axis=0)
    pr, tr, lr, mr = pred.astype(np.float64).mean(2), teacher.astype(np.float64).mean(2), layer.mean(2), moments.mean(1)
    fields = batches[0]["metric_fields"].tolist()
    layer_fields = batches[0]["layer_fields"].tolist()
    mix = [names.index(r["name"]) for r in c.read(c.WB / "results/e144/source_maps.json")["maps"]]
    natives = [names.index(n) for n in ("F0", "F1", "F2")]
    result = {"experiment": "E144", "status": "complete", "rows": len(rows), "positions": 32768,
              "input_file_clusters": len(file_groups(rows)), "source_MC_units": 8,
              "manifest_sha256": c.sha(c.WB / "results/e144/manifest.json"),
              "scope": manifest["scope"], "variants": {}, "effects": {}, "moments": {}}
    for i, name in enumerate(names):
        result["variants"][name] = {**{f: input_stats(pr[i, :, j], rows) for j, f in enumerate(fields)},
                                       "teacher_to_variant_kl": input_stats(tr[i, :, 1], rows),
                                       **{f: input_stats(lr[i, :, j], rows) for j, f in enumerate(layer_fields)}}
    for j, name in enumerate(batches[0]["moment_names"].tolist()):
        result["moments"][name] = input_stats(mr[:, j], rows)
    effects = {}
    for label, values in (("delta_nll", pr[:, :, 0]), ("delta_mu_to_variant_kl", pr[:, :, 1]),
                          ("delta_native_teacher_sse", lr[:, :, 0]), ("delta_sum64_teacher_sse", lr[:, :, 1])):
        baseline = values[natives].mean(0)
        delta = values[mix].reshape(8, 3, 64).mean(1) - baseline[None, :]
        result["effects"][label] = crossed_stats(delta, rows)
        result["effects"][label]["by_source"] = summaries_by_source(delta.mean(0), rows, 144001)
        effects[label] = delta
    result["arithmetic"] = {"finite_MC_delta_minus_expected_C_minus_V":
         crossed_stats(effects["delta_sum64_teacher_sse"] - mr[:, 2][None, :], rows),
         "batch_floors": [dict(zip(b["arithmetic_floor_names"].tolist(), b["arithmetic_floors"].tolist())) for b in batches],
         "note": "C-V predicts infinite independent-source squared-risk difference; 24 cyclic maps have exact first but finite second moments."}
    result["native_average_nll"] = input_stats(pr[natives, :, 0].mean(0), rows)
    result["mixed_average_nll"] = input_stats(pr[mix, :, 0].mean(0), rows)
    result["native_average_mu_kl"] = input_stats(pr[natives, :, 1].mean(0), rows)
    result["mixed_average_mu_kl"] = input_stats(pr[mix, :, 1].mean(0), rows)
    # Per-token scalar examples, never a frequency claim or held-based selection.
    token_mean_kl = pred[mix, :, :, 1].mean(0)
    largest = np.unravel_index(int(token_mean_kl.argmax()), token_mean_kl.shape)
    selected_pairs = [(0, 31), (1, 127), (2, 255), tuple(int(i) for i in largest)]
    old = np.load(c.RECIPE / "held_tokens.npy", mmap_mode="r").reshape(512, 513)
    examples = []
    for k, (seq, pos) in enumerate(selected_pairs):
        m = int(np.argmax(pred[mix, seq, pos, 1]))
        idx = mix[m]
        tokens = old[rows[seq]["old_sequence_index"]]
        examples.append({"selection": "SHA-fixed-sequence/position" if k < 3 else "explanatory maximum mean KL; not prevalence evidence",
                         "sequence": seq, "position": pos, "source": rows[seq]["source"], "file_id": rows[seq]["file_id"],
                         "short_context_token_ids": tokens[max(0, pos-15):pos+1].astype(int).tolist(),
                         "target_token_id": int(tokens[pos+1]), "chosen_variant": names[idx],
                         "chosen_variant_selection": "maximum KL at the displayed position, explanatory selection",
                         "correct_token_probability_native_F": np.exp(-pred[natives, seq, pos, 0].astype(float)).tolist(),
                         "correct_token_probability_mu": float(np.exp(-pred[names.index("mu"), seq, pos, 0])),
                         "correct_token_probability_recombined": float(np.exp(-pred[idx, seq, pos, 0])),
                         "mu_to_recombined_kl": float(pred[idx, seq, pos, 1])})
    c.write(c.WB / "results/e144/examples.json", {"scope": "Short explanatory token-ID excerpts; no independent prevalence evidence", "rows": examples})
    return result


def analyze_e145(manifest, batches, rows):
    names = batches[0]["names"].tolist()
    pred = {key: np.concatenate([b[key + "_metrics"] for b in batches], axis=1).astype(np.float64).mean(2)
            for key in ("A", "teacher", "donor")}
    fields = batches[0]["metric_fields"].tolist()
    result = {"experiment": "E145", "status": "complete", "rows": len(rows), "positions": 32768,
              "input_file_clusters": len(file_groups(rows)), "trained_donor_pairs": 2,
              "manifest_sha256": c.sha(c.WB / "results/e145/manifest.json"), "scope": manifest["scope"],
              "variants": {}, "donors": {}, "paired_S_minus_R": {}, "common_gate_moments": {}, "native_moments": {}}
    for i, name in enumerate(names):
        result["variants"][name] = {ref: {f: input_stats(pred[ref][i, :, j], rows, 139) for j, f in enumerate(fields)}
                                       for ref in pred}
    for kind in ("common_gate", "native"):
        suffix = "" if kind == "common_gate" else "_native"
        for group in ("R", "S"):
            values = np.concatenate([b[group + suffix + "_moments"] for b in batches], axis=0).mean(1)
            result[kind + "_moments"][group] = {f: input_stats(values[:, j], rows, 139)
                for j, f in enumerate(batches[0]["moment_names"].tolist())}
        rv = np.concatenate([b["R" + suffix + "_moments"] for b in batches], axis=0).mean(1)
        sv = np.concatenate([b["S" + suffix + "_moments"] for b in batches], axis=0).mean(1)
        result[kind + "_moments"]["S_minus_R"] = {f: input_stats(sv[:, j]-rv[:, j], rows, 139)
            for j, f in enumerate(batches[0]["moment_names"].tolist())}
    four = np.concatenate([b["four_grid_layer"] for b in batches], axis=1).mean(2)
    support = np.concatenate([b["support"] for b in batches], axis=1).mean(2)
    nll = pred["A"][:, :, 0]
    aa = names.index("AA")
    donor_arrays = {}
    for d, donor in enumerate(batches[0]["donors"].tolist()):
        ad, da, dd = [names.index(donor+"_"+k) for k in ("Ad", "dA", "dd")]
        delta = {"bank_nll_minus_A": nll[ad]-nll[aa], "gate_nll_minus_A": nll[da]-nll[aa],
                 "native_nll_minus_A": nll[dd]-nll[aa], "bank_nll_minus_donor_native": nll[ad]-nll[dd],
                 "nll_four_grid_interaction": nll[dd]-nll[da]-nll[ad]+nll[aa],
                 "A_to_bank_kl": pred["A"][ad, :, 1], "A_to_gate_kl": pred["A"][da, :, 1],
                 "A_to_donor_native_kl": pred["A"][dd, :, 1]}
        donor_arrays[donor] = delta
        result["donors"][donor] = {f: input_stats(v, rows, 139) for f, v in delta.items()}
        result["donors"][donor]["layer_four_grid"] = {f: input_stats(four[d, :, j], rows, 139) for j, f in enumerate(batches[0]["four_grid_fields"].tolist())}
        result["donors"][donor]["support"] = {f: input_stats(support[d, :, j], rows, 139) for j, f in enumerate(batches[0]["support_fields"].tolist())}
    for seed in (0, 2):
        result["paired_S_minus_R"][f"seed{seed}"] = {f: input_stats(donor_arrays[f"S{seed}"][f]-donor_arrays[f"R{seed}"][f], rows, 139)
                                                       for f in donor_arrays[f"S{seed}"]}
    result["paired_S_minus_R"]["finite_two_pair_average"] = {f: input_stats(np.mean([
        donor_arrays[f"S{s}"][f] - donor_arrays[f"R{s}"][f] for s in (0, 2)], axis=0), rows, 139)
        for f in donor_arrays["R0"]}
    result["interval_scope"] = "Paired input-file bootstrap only: two expert-init pairs, one shared gate and one receiver; no seed treatment-effect interval."
    return result


def main(experiment):
    manifest, batches, rows = read_batches(experiment)
    result = (analyze_e144 if experiment == "e144" else analyze_e145)(manifest, batches, rows)
    result["analysis_sha256"] = c.sha(__file__)
    c.write(c.WB / f"results/{experiment}/summary.json", result)
    print(json.dumps({"experiment": experiment, "status": result["status"], "file_clusters": result["input_file_clusters"],
                      **({"effects": {k: v["point"] for k, v in result["effects"].items()}} if experiment == "e144" else {})}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("experiment", choices=("e144", "e145"))
    main(p.parse_args().experiment)
