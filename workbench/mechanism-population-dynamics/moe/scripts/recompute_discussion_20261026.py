#!/usr/bin/env python3
"""POST-HOC arithmetic from committed summaries; no model, GPU, or raw cache.

Run from any directory. Default writes the discussion JSON; --check verifies
that the committed output is exactly reproducible from the pinned input blobs.
This is not E144/E145/E146 and produces no new model observations.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean


MOE_ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "15b9b1bf78c9c60e32250434de4997e17cbf28f8"
INPUT_BLOBS = {
    "results/e134/necessity.json": "e056e8eae70875650f291349546635a07155167d",
    "results/e135/readout.json": "74c4fc58edb975a8f4bd449f8b79cd11ae6284aa",
    "results/e136/readout.json": "08838f75d44fcd48b1044147fe10386fdfbb2e48",
    "results/e139/readout.json": "8aaf14562c22303d18bd25ebdccbb00224ca4f9c",
    "results/e142/readout_table.json": "5555449eac870ee18e204dfec4b94e9a044991e9",
}


def pointer(obj, path):
    for key in path.strip("/").split("/"):
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    return obj


def near(a, b, label):
    if not math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-12):
        raise ValueError(f"Arithmetic identity failed: {label}: {a} != {b}")


def build():
    data, sources = {}, {}
    for path, expected in INPUT_BLOBS.items():
        raw = (MOE_ROOT / path).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if blob != expected:
            raise ValueError(f"Input differs from reviewed snapshot: {path}: {blob}")
        data[path] = json.loads(raw)
        sources[path] = {
            "git_blob_sha1": blob,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }

    initial = {}
    locations = {
        "R": ("results/e139/readout.json", "/components/free_initial_Dolma_held_positions/summary/global"),
        "T_F": ("results/e139/readout.json", "/components/fixed_initial_Dolma_held_positions/summary/global"),
        "S": ("results/e142/readout_table.json", "/paired_shared_minus_old_groups/initial_Dolma_held_positions/summary/global"),
    }
    for group, (file, path) in locations.items():
        g = pointer(data[file], path)
        fields = {
            "C": "cohort_variance_per_position",
            "component_mean_energy": "cohort_mean_energy_per_position",
            "native_teacher_SSE": "native_mean_teacher_SSE_per_position",
            "FP64_sum_teacher_SSE": "FP64_sum_mean_teacher_SSE_per_position",
            "FP64_sum_V": "FP64_sum_cohort_variance_per_position",
        }
        row = {name: g[key]["point"] for name, key in fields.items()}
        energies = [g[f"energy_seed{s}_per_position"]["point"] for s in range(3)]
        row.update({
            "Q": fmean(energies),
            "energy_per_seed": energies,
            "source": {"file": file, "pointer": path},
            "source_keys": {**fields, "energy_per_seed": "energy_seed{0,1,2}_per_position"},
        })
        row["Q_minus_C_minus_component_mean_energy"] = row["Q"] - row["C"] - row["component_mean_energy"]
        near(row["Q"], row["C"] + row["component_mean_energy"], group + " Q=C+M")
        initial[group] = row

    final = {}
    file = "results/e142/readout_table.json"
    for group, g in data[file]["final_groups"].items():
        c = g["cohort_variance_per_position"]["point"]
        v = g["FP64_sum_cohort_variance_per_position"]["point"]
        cross = g["component_cross_covariance_per_position"]["point"]
        near(v, c + cross, group + " V=C+cross")
        final[group] = {
            "source": {"file": file, "pointer": "/final_groups/" + group},
            "C": c, "V_FP64_sum": v, "cross": cross,
            "C_minus_V": c - v, "cancellation_fraction": (c - v) / c,
            "V_native": g["native_cohort_variance_per_position"]["point"],
            "native_bias_SSE": g["native_mean_bias_SSE_per_position"]["point"],
            "native_teacher_SSE": g["native_mean_teacher_SSE_per_position"]["point"],
        }
    # A shared physical identity is essential for the F recombination prediction.
    fixed_maps = data["results/e139/readout.json"]["components"]["fixed_final_calibration"]["maps"]
    if any(m["source_to_seed1"] != list(range(64)) for m in fixed_maps.values()):
        raise ValueError("F final calibration map is not physical identity")

    geometry, interventions = {}, {}
    e134 = data["results/e134/necessity.json"]
    for setting in e134["settings_order"]:
        s = e134["settings"][setting]
        cal = s["calibration"]
        err = cal["real_cache_squared_l2_error_mean"]
        # Error of retaining c is energy of removed r, and vice versa.
        ec, er, ey = err["r"], err["c"], err["zero"]
        geometry[setting] = {
            "source": {"file": "results/e134/necessity.json", "pointer": f"/settings/{setting}/calibration"},
            "population": "training-side Hcal8192; not Dolma held",
            "E_c_squared": ec, "E_r_squared": er, "E_Y_squared": ey,
            "E_c_squared_over_E_Y_squared": ec / ey,
            "E_r_squared_over_E_Y_squared": er / ey,
            "two_cross_over_E_Y_squared": (ey - ec - er) / ey,
            "rms_c_over_Y": math.sqrt(ec / ey),
            "selected_mass_min_max_mean": cal["mass_min_max_mean"],
        }
        globals_by_mode = {m: s["conditions"][m]["metrics"]["global"] for m in ["c", "r", "zero"]}
        interventions[setting] = summarize_interventions(
            globals_by_mode, "results/e134/necessity.json",
            f"/settings/{setting}/conditions/{{mode}}/metrics/global",
        )
    for experiment, key in [("e135", "final_student_necessity"), ("e136", "final_oracle_necessity")]:
        file = f"results/{experiment}/readout.json"
        conditions = data[file][key]["conditions"]
        interventions[experiment] = summarize_interventions(
            {m: conditions[m]["global"] for m in ["c", "r", "zero"]},
            file, f"/{key}/conditions/{{mode}}/global",
        )

    zero_values = [interventions[x]["zero_absolute_NLL"] for x in ["public_olmoe_main", "e135", "e136"]]
    for z in zero_values[1:]:
        near(z, zero_values[0], "native-interface common zero NLL")
    tf, s, r = initial["T_F"], initial["S"], initial["R"]
    return {
        "status": "POST-HOC: recomputation of existing summaries; no new model runs",
        "date": "2026-10-26", "source_commit": BASE_COMMIT,
        "sources_relative_to_moe": sources,
        "units": {
            "initial_and_final": "raw squared hidden-vector norm per Dolma held position; cohort divisor 3",
            "geometry": "raw squared hidden-vector norm per training calibration position",
            "prediction": "nats per scored token; gap against each model's own native reference",
        },
        "initial": initial,
        "initial_comparisons": {
            "T_F_minus_S_Q": tf["Q"] - s["Q"],
            "T_F_minus_S_native_SSE": tf["native_teacher_SSE"] - s["native_teacher_SSE"],
            "T_F_over_S_Q": tf["Q"] / s["Q"],
            "S_minus_R_Q_over_R_Q": (s["Q"] - r["Q"]) / r["Q"],
        },
        "final": final,
        "S_vs_R_final_C_reduction_fraction": 1 - final["S_shared_random"]["C"] / final["R_free"]["C"],
        "F_final_calibration_maps_are_identity": True,
        "calibration_geometry": geometry,
        "held_interventions": interventions,
        "common_native_interface_zero_NLL": zero_values[0],
        "formulas": {
            "Q": "mean_s(sum_e E_h ||u_se||^2); exactly C + sum_e E_h ||mean_s u_se||^2",
            "geometry": "error(c-only)=E||r||^2; error(r-only)=E||c||^2; error(zero)=E||Y||^2",
            "cross": "E||Y||^2 - E||c||^2 - E||r||^2 = 2 E<c,r>",
            "fixed_gate_recombination": "Expected squared-risk increment of independent sources = C - V; not measured KL/NLL",
        },
        "limits": [
            "Q sums uncentered component energies, not aggregate-output energy; numerical proximity to delta SSE is not causal attribution.",
            "No bootstrap is recomputed here; copied CIs are original input-file CIs, not seed-population CIs. Derived ratios have no new CI.",
            "R/S share the same trained seed1; only two new paired donors and one shared-random gate were observed.",
            "Calibration energy and held prediction are different populations; NLL intervention ratios are not additive functionality fractions.",
            "Calibration energies are reconstructed from the saved intervention SSEs; the original FP32 c/r decomposition has floating-point rounding.",
            "Free-gate C-V is algebraic and need not describe a legal single-router graft; F identity is explicitly verified.",
            "No E144/E145/E146 selected inputs, source maps, GPU drivers or results are generated by this script.",
        ],
    }


def summarize_interventions(globals_by_mode, file, path_template):
    modes = {}
    for mode, metrics in globals_by_mode.items():
        modes[mode] = {k: metrics[k] for k in ["nll_gap", "kl_teacher_to_student"]}
    z = globals_by_mode["zero"]
    return {
        "source": {"file": file, "pointer_template": path_template},
        "reference_prediction": "Each setting's own native predictor; the legacy helper calls it teacher, including E135/E136 students",
        "population": {k: z[k] for k in ["tokens", "sequences", "files"]},
        "native_NLL": z["teacher_nll"]["mean"],
        "zero_absolute_NLL": z["student_nll"]["mean"],
        "conditions": modes,
        "c_loss_over_zero_loss": modes["c"]["nll_gap"]["mean"] / modes["zero"]["nll_gap"]["mean"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=MOE_ROOT / "results/discussion_2026-10-26/reanalysis.json")
    parser.add_argument("--check", action="store_true", help="Verify existing output byte-for-byte; do not write")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        if args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Existing output is not the exact recomputation")
        print("PASS: pinned sources, arithmetic identities, and output match")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
