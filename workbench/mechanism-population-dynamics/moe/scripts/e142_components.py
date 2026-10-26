"""E142 shared random-gate cohort: original Dolma held vector components only."""
from __future__ import annotations
import copy
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
import e135_readout as pilot_readout
import e139_components as inherited
import e142_train as training

c, assets, base, WB = training.c, training.assets, training.base, training.WB
STUDENTS = inherited.STUDENTS
TRAIN_SHA = "155001f774c76ad906e40f5571163411243d9f260c9575a5f6d992c2b1e12829"
OLD_COMPONENTS_SHA = "ce8e7029f707b735770a4915bbca4e53406033867bea4d4683a0b0c7fe7342b2"
OLD_READOUT_SHA = "6ac6444b6b61dfc7b4380e8d4ad05c81286dbd6bfec9d6bac386060ff2e359e9"
WARM_READOUT_SHA = "1b69db4bf36d8a0780a295ea9e89970e4bb77e6cea5e31b21f4e5e573ed5ceec"


def preflight(args, *, initial_only=False):
    for name, expected in (("e142_train.py", TRAIN_SHA), ("e139_components.py", OLD_COMPONENTS_SHA),
            ("e139_readout.py", OLD_READOUT_SHA), ("e140_readout.py", WARM_READOUT_SHA)):
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError(f"Frozen E142 dependency differs: {name}")
    old_records = {}
    for group, filename, expected in (("R_F", "e139", OLD_READOUT_SHA), ("T", "e140", WARM_READOUT_SHA)):
        path = WB / f"results/{filename}/readout.json"; record = assets.read(path)
        if not record or record.get("status") != "complete" or record.get("errors") or record.get("script_sha256") != expected:
            raise ValueError(f"Immutable {filename} complete result required")
        old_records[group] = {"path": str(path), "sha256": assets.sha(path), "record": record}
    states = {"initial": {}, "final": {}}; proofs = {}; manifest = None
    old_seed1 = old_records["R_F"]["record"]["condition_proofs"]["free"]["seed1"]
    for seed in (0, 2):
        name = f"seed{seed}"; new_args = copy.copy(args); new_args.seed = seed
        new_args.free_initial = getattr(args, f"e139_seed{seed}_dir") / "initial.pt"
        current_manifest, _, _, _, expected_state, _, expected = training.preflight(new_args)
        if manifest is None: manifest = current_manifest
        directory = getattr(args, f"shared_seed{seed}_dir"); provenance = assets.read(directory / "provenance.json")
        summary = assets.read(directory / "training_summary.json"); proofs[name] = {}
        endpoints = (("initial", 0, "initial.pt"),) if initial_only else (("initial", 0, "initial.pt"), ("final", 4096, "checkpoint.pt"))
        for phase, step, filename in endpoints:
            path = directory / filename; cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp["student_state"]
            if (cp.get("experiment"), cp.get("schema"), cp.get("seed"), cp.get("step"), cp.get("cache_manifest_sha256")) != (
                    "E142", "E142-shared-random-router-v1", seed, step, assets.sha(args.cache_root / "manifest.json")):
                raise ValueError("E142 endpoint schema/seed/step/cache differs")
            if (cp["initialization"] != expected or cp["config_hash"] != provenance["config_hash"]
                    or provenance["scientific"]["driver_sha256"] != TRAIN_SHA or any(value.dtype != torch.float32 for value in state.values())):
                raise ValueError("E142 immutable source/config/FP32 proof differs")
            digest = c.tensor_state_hash(state)
            if step == 0 and (digest != expected["initial_full_tensor_sha256"] or digest != c.tensor_state_hash(expected_state)
                    or cp["optimizer"]["state"] or np.any(cp["cache_batch_counts"])):
                raise ValueError("E142 exact expert/RNG-paired initial tensor/optimizer/exposure differs")
            if step == 4096 and (summary.get("status") != "complete" or summary.get("step") != 4096 or digest != summary["final_tensor_sha256"]
                    or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4))
                    or [row["step"] for row in summary["evaluations"]] != list(range(0, 4097, 512))):
                raise ValueError("Only complete E142 4096 endpoint allowed")
            states[phase][name] = state
            proofs[name][phase] = {"checkpoint": str(path), "checkpoint_sha256": assets.sha(path), "full_tensor_sha256": digest,
                "expert_only_tensor_sha256": training.expert_hash(state), "gate_tensor_sha256": training.gate_hash(state),
                "seed": seed, "step": step, "config_hash": cp["config_hash"]}
        old_r = old_records["R_F"]["record"]["condition_proofs"]["free"][name]["initial"]
        if proofs[name]["initial"]["expert_only_tensor_sha256"] != old_r["expert_only_tensor_sha256"]:
            raise ValueError("E142 initial experts are not exact E139 own initial experts")
    args_pilot = copy.copy(args); args_pilot.student_dir = args.e135_student_dir
    old_states, old_proofs = pilot_readout.condition_states(args_pilot, manifest)
    proofs["seed1"] = {}
    for phase in ("initial", "final"):
        p = old_proofs[phase]; old = old_seed1[phase]
        if p["checkpoint_sha256"] != old["checkpoint_sha256"] or p["tensor_sha256"] != old["full_tensor_sha256"]:
            raise ValueError("Observed shared E135 seed1 pilot differs from E139 free seed1 reference")
        states[phase]["seed1"] = old_states[phase]
        proofs["seed1"][phase] = {"checkpoint": p["checkpoint"], "checkpoint_sha256": p["checkpoint_sha256"],
            "full_tensor_sha256": p["tensor_sha256"], "expert_only_tensor_sha256": training.expert_hash(old_states[phase]),
            "gate_tensor_sha256": training.gate_hash(old_states[phase]), "seed": 1, "step": p["step"], "scope": "Observed E135 full run reused"}
    if len({training.gate_hash(states["initial"][name]) for name in STUDENTS}) != 1:
        raise ValueError("E142 cohort initial gate not exactly shared with observed pilot")
    if len({training.expert_hash(states["initial"][name]) for name in STUDENTS}) != 3:
        raise ValueError("E142 independent expert seeds not distinct")
    return manifest, old_states["teacher"], states, proofs, old_records


@torch.no_grad()
def route_batch(reference_gate, blocks, hidden, query, sequence, top_k=8):
    """Original full-row top8 then query selection, in physical expert coordinates."""
    flat = hidden.reshape(-1, hidden.shape[-1]); batch = int(sequence.max()) + 1; experts = reference_gate.shape[0]
    selected, applied = {}, {}
    with torch.autocast(hidden.device.type, dtype=torch.bfloat16): logits = F.linear(flat, reference_gate)
    weight, index = F.softmax(logits, dim=1, dtype=torch.float32).topk(top_k, dim=-1)
    selected["reference"], applied["reference"] = index[query], weight.to(hidden.dtype)[query]
    for name in STUDENTS:
        block = blocks[name]
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16): logits = block.gate(flat)
        weight, index = F.softmax(logits, dim=1, dtype=torch.float32).topk(block.top_k, dim=-1)
        if block.norm_topk_prob or block.top_k != top_k: raise ValueError("Original no-renorm gate/topk program required")
        selected[name], applied[name] = index[query], weight.to(hidden.dtype)[query]
    ref_index = selected["reference"]; ref_weight = applied["reference"]
    ref_mask = torch.zeros((len(query), experts), dtype=torch.bool, device=hidden.device); ref_mask.scatter_(1, ref_index, True)
    ref_dense = torch.zeros((len(query), experts), dtype=torch.float32, device=hidden.device); ref_dense.scatter_(1, ref_index, ref_weight.float())
    result = {"reference_support": torch.bincount(ref_index.reshape(-1), minlength=experts).cpu().numpy()}
    for name in STUDENTS:
        index, weight = selected[name], applied[name]
        mask = torch.zeros_like(ref_mask); mask.scatter_(1, index, True)
        dense = torch.zeros_like(ref_dense); dense.scatter_(1, index, weight.float()); delta = dense - ref_dense
        values = (torch.bincount(sequence, minlength=batch),
            inherited.native.grouped((index != ref_index).any(-1).double(), sequence, batch),
            inherited.native.grouped((mask & ref_mask).sum(-1).double(), sequence, batch),
            inherited.native.grouped(delta.abs().sum(-1), sequence, batch),
            inherited.native.grouped(delta.double().square().sum(-1), sequence, batch))
        max_abs = torch.stack([delta[sequence == b].abs().max() for b in range(batch)])
        result[name] = {"rows": torch.stack((*values, max_abs), -1).cpu().numpy(),
            "support": torch.bincount(index.reshape(-1), minlength=experts).cpu().numpy()}
    return result


def route_summary(rows, support, reference_support, top_k=8):
    totals = rows.sum(0); positions = totals[0]
    return {"positions": int(positions), "slot_mismatch_fraction": float(totals[1] / positions),
        "mean_selected_set_overlap_fraction": float(totals[2] / (top_k * positions)),
        "applied_weight_L1_per_position": float(totals[3] / positions),
        "applied_weight_L2_SSE_per_position": float(totals[4] / positions),
        "applied_weight_max_abs": float(rows[:, 5].max()),
        "student_support_counts": support.astype(int).tolist(), "shared_initial_gate_support_counts": reference_support.astype(int).tolist(),
        "scope": "Full B16 gate rows, target query selected after full top8; compared in original physical expert coordinates to shared E135 random initial gate, not cal-matched axes."}


def renamed_contrast(shared, old, old_name):
    record = inherited.paired_contrast(shared, old, "Dolma_held_positions")
    record["metrics"] = {name: {"shared_random": value["free"], old_name: value["fixed"],
        "shared_random_minus_" + old_name: value["free_minus_fixed"],
        "paired_input_cluster_ci95": value["paired_input_cluster_ci95"], "defined_draws": value["defined_draws"]}
        for name, value in record["metrics"].items()}
    record["scope"] = f"Shared-random minus {old_name}, same Dolma held file draws and fixed observed cohorts/maps. Conditional input CI, not seed treatment-effect CI; S/R share observed seed1."
    return record


@torch.no_grad()
def run_components(model, teacher, banks, proofs, manifest, old_records, initial_gate_weight, args, budget):
    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Original Dolma held windows differ")
    hcal_path = Path(manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["path"])
    hcal = np.load(hcal_path, mmap_mode="r", allow_pickle=False)
    if hcal.shape != (8192, 2048) or hcal.dtype != np.float32 or assets.sha(hcal_path) != manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["sha256"]:
        raise ValueError("Original native training Hcal8192 asset differs")
    result = {"source_proofs": proofs, "components_script_sha256": assets.sha(__file__), "population": "Dolma_held_positions_only",
        "old_reference": {name: {"path": value["path"], "sha256": value["sha256"]} for name, value in old_records.items()}}
    for phase in ("initial", "final"):
        blocks = {name: banks[phase][name].block for name in STUDENTS}
        calibration = inherited.calibrate(blocks, hcal, budget)
        cost_path = args.raw_output / f"{phase}_Hcal_costs.npz"
        np.savez(cost_path, seed0=calibration["maps"]["seed0"].pop("cost"), seed2=calibration["maps"]["seed2"].pop("cost"))
        maps = {"seed1": list(range(64)), **{name: calibration["maps"][name]["source_to_seed1"] for name in ("seed0", "seed2")}}
        calibration.update({"Hcal_path": str(hcal_path), "Hcal_sha256": assets.sha(hcal_path), "cost_path": str(cost_path),
            "cost_sha256": assets.sha(cost_path), "mapping_scope": "Same original E139 full B16×512 Hcal8192 actual-component squared-distance Hungarian to shared pilot seed1; one map per phase, held locked."})
        result[f"{phase}_calibration"] = calibration
        assets.write(args.raw_output / "components_progress.json", result)
        harray = np.load(args.cache_root / "held_H.npy", mmap_mode="r"); echunks, achunks, rows = [], [], []
        route_rows = {name: [] for name in STUDENTS}; route_support = {name: np.zeros(64, np.int64) for name in STUDENTS}
        reference_support = np.zeros(64, np.int64)
        for index, (_, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
            budget.check(); hidden = c.from_bits(harray[index], "cuda:0")
            query = torch.arange(8192, device="cuda:0"); sequence = torch.arange(16, device="cuda:0").repeat_interleave(512)
            e, a = inherited.measure_batch(blocks, teacher, hidden, query, sequence, maps, budget)
            if phase == "final":
                routing = route_batch(initial_gate_weight, blocks, hidden, query, sequence)
                reference_support += routing["reference_support"]
                for name in STUDENTS:
                    route_rows[name].append(routing[name]["rows"]); route_support[name] += routing[name]["support"]
            echunks.append(e); achunks.append(a); rows.extend(metadata)
            base.emit("E142_joint_components", phase=phase, sequences=len(rows))
        expert, aggregate = np.concatenate(echunks), np.concatenate(achunks)
        path = args.raw_output / f"{phase}_Dolma_held_positions_components.npz"; np.savez(path, expert=expert, aggregate=aggregate)
        meta_path = path.with_suffix(".json"); assets.write(meta_path, {"rows": rows, "expert_fields": inherited.EXPERT,
            "aggregate_fields": inherited.AGG, "maps_source_to_seed1": maps, "Hcal_sha256": calibration["Hcal_sha256"]})
        record = {"raw": str(path), "raw_sha256": assets.sha(path), "metadata": str(meta_path),
            "metadata_sha256": assets.sha(meta_path), "sequences": len(rows),
            "summary": inherited.summarize(expert, aggregate, rows, "Dolma_held_positions")}
        if phase == "final":
            route_path = args.raw_output / "final_Dolma_held_positions_routing.npz"
            np.savez(route_path, reference_support=reference_support,
                **{name + "_rows": np.concatenate(route_rows[name]) for name in STUDENTS},
                **{name + "_support": route_support[name] for name in STUDENTS})
            record["routing_raw"] = str(route_path); record["routing_raw_sha256"] = assets.sha(route_path)
            record["routing"] = {name: route_summary(np.concatenate(route_rows[name]), route_support[name], reference_support) for name in STUDENTS}
        else:
            record["routing"] = {"initial_gate_identity": "All three initial gate tensors have exact E135 seed1 gate SHA; on same native H, physical top8/weights are identical. No extra route forward."}
        result[f"{phase}_Dolma_held_positions"] = record
        if phase == "final":
            old_components = {"R": old_records["R_F"]["record"]["components"]["free_final_Dolma_held_positions"],
                "F": old_records["R_F"]["record"]["components"]["fixed_final_Dolma_held_positions"],
                "T": old_records["T"]["record"]["components"]["final_Dolma_held_positions"]}
            for old_name, old in old_components.items():
                if assets.sha(old["raw"]) != old["raw_sha256"] or assets.sha(old["metadata"]) != old["metadata_sha256"]:
                    raise ValueError(f"Immutable {old_name} old final raw differs")
                result[f"paired_shared_minus_{old_name}_Dolma_held_positions"] = renamed_contrast(record, old, old_name)
        assets.write(args.raw_output / "components_progress.json", result)
    return result


def self_test():
    old = inherited.self_test()
    class Gate(torch.nn.Module):
        def __init__(self, logits): super().__init__(); self.logits = logits
        def forward(self, h): return torch.tensor(self.logits, dtype=h.dtype).expand(len(h), -1)
    class Block(torch.nn.Module):
        def __init__(self, logits): super().__init__(); self.gate = Gate(logits); self.top_k = 2; self.norm_topk_prob = False
    h = torch.ones(2, 3, 2).bfloat16(); query = torch.tensor([1, 5]); seq = torch.tensor([0, 1])
    ref = torch.tensor([[3., 0.], [2., 0.], [-100., 0.]], dtype=torch.float32)
    blocks = {"seed0": Block([3., 2., -100.]), "seed1": Block([3., 2., -100.]), "seed2": Block([-100., 2., 3.])}
    route = route_batch(ref, blocks, h, query, seq, top_k=2)
    equal = route_summary(route["seed0"]["rows"], route["seed0"]["support"], route["reference_support"], top_k=2)
    changed = route_summary(route["seed2"]["rows"], route["seed2"]["support"], route["reference_support"], top_k=2)
    assert equal["mean_selected_set_overlap_fraction"] == 1 and equal["applied_weight_L1_per_position"] == 0
    assert changed["mean_selected_set_overlap_fraction"] == .5 and changed["applied_weight_L1_per_position"] > 0
    assert old["known_permutation_hungarian"] and old["paired_input_cluster_free_minus_fixed"]
    return {"passed": True, "CPU_only": True, "E139_native_vector_contract": True,
        "original_gate_reference_is_seed1_random_initial": True, "physical_route_overlap_weight_math": True,
        "source_sha256": assets.sha(__file__)}
