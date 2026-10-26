"""E140 native warmstart cohort: fresh final, SHA-coupled fixed initial reference."""
from __future__ import annotations
import copy
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
import e139_components as inherited
import e140_train as training

c, assets, base, WB = training.c, training.assets, training.base, training.WB
STUDENTS = inherited.STUDENTS
TRAIN_SHA = "1b1c81afa1e2177029c3296324bc6be3dd7c53ad304fcde694ecbd5d81c02f07"
OLD_COMPONENTS_SHA = "ce8e7029f707b735770a4915bbca4e53406033867bea4d4683a0b0c7fe7342b2"
OLD_READOUT_SHA = "6ac6444b6b61dfc7b4380e8d4ad05c81286dbd6bfec9d6bac386060ff2e359e9"
ROUTE_FIELDS = ("positions", "slot_mismatch_rows", "selected_set_overlap_count", "applied_weight_L1_sum",
    "applied_weight_L2_SSE", "applied_weight_max_abs")


def preflight(args, *, initial_only=False):
    for name, expected in (("e140_train.py", TRAIN_SHA), ("e139_components.py", OLD_COMPONENTS_SHA), ("e139_readout.py", OLD_READOUT_SHA)):
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError(f"Frozen E140 dependency differs: {name}")
    old_args = copy.copy(args); old_args.budget_file = args.e139_budget_file
    manifest, teacher, old_states, old_proofs, items, metadata, htarget = inherited.preflight(old_args)
    old_record_path = WB / "results/e139/readout.json"; old_record = assets.read(old_record_path)
    if (not old_record or old_record.get("status") != "complete" or old_record.get("script_sha256") != OLD_READOUT_SHA
            or old_record.get("components_script_sha256") != OLD_COMPONENTS_SHA or old_record.get("condition_proofs") != old_proofs):
        raise ValueError("Immutable E139 complete old cohort/result binding differs")
    states = {"initial": {}, "final": {}}; proofs = {}
    for seed in (0, 1, 2):
        name = f"seed{seed}"; new_args = copy.copy(args); new_args.seed = seed
        new_args.fixed_initial = (args.e136_oracle_dir / "initial.pt" if seed == 1 else getattr(args, f"e138_seed{seed}_dir") / "initial.pt")
        _, _, _, _, expected_state, _, expected = training.preflight(new_args)
        directory = getattr(args, f"warm_seed{seed}_dir"); provenance = assets.read(directory / "provenance.json")
        summary = assets.read(directory / "training_summary.json"); proofs[name] = {}
        endpoints = (("initial", 0, "initial.pt"),) if initial_only else (("initial", 0, "initial.pt"), ("final", 4096, "checkpoint.pt"))
        for phase, step, filename in endpoints:
            path = directory / filename; cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp["student_state"]
            if (cp.get("experiment"), cp.get("schema"), cp.get("seed"), cp.get("step"), cp.get("cache_manifest_sha256")) != (
                    "E140", "E140-native-router-warmstart-v1", seed, step, assets.sha(args.cache_root / "manifest.json")):
                raise ValueError("E140 endpoint schema/seed/step/cache identity differs")
            if (cp["initialization"] != expected or cp["config_hash"] != provenance["config_hash"]
                    or provenance["scientific"]["driver_sha256"] != TRAIN_SHA or any(value.dtype != torch.float32 for value in state.values())):
                raise ValueError("E140 immutable source/config/FP32 proof differs")
            digest = c.tensor_state_hash(state)
            if step == 0 and (digest != expected["initial_full_tensor_sha256"] or digest != c.tensor_state_hash(expected_state)
                    or cp["optimizer"]["state"] or np.any(cp["cache_batch_counts"])):
                raise ValueError("E140 exact fixed initial tensor/optimizer/exposure differs")
            if step == 4096 and (summary.get("status") != "complete" or summary.get("step") != 4096 or digest != summary["final_tensor_sha256"]
                    or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4))
                    or [row["step"] for row in summary["evaluations"]] != list(range(0, 4097, 512))):
                raise ValueError("Only exact full4096 E140 final accepted")
            states[phase][name] = state
            proofs[name][phase] = {"checkpoint": str(path), "checkpoint_sha256": assets.sha(path), "full_tensor_sha256": digest,
                "expert_only_tensor_sha256": training.expert_hash(state), "gate_tensor_sha256": training.gate_hash(state),
                "seed": seed, "step": step, "config_hash": cp["config_hash"]}
        old_initial = old_proofs["fixed"][name]["initial"]
        if proofs[name]["initial"]["full_tensor_sha256"] != old_initial["full_tensor_sha256"]:
            raise ValueError("E140 initial not exactly E139 fixed initial full tensor")
    return manifest, teacher, states, proofs, items, metadata, htarget, old_record


@torch.no_grad()
def route_batch(teacher, blocks, hidden, query, sequence):
    """Full original row gate program; inspect actual BF16-applied top8 weights."""
    flat = hidden.reshape(-1, hidden.shape[-1]); batch = int(sequence.max()) + 1; experts = teacher.num_experts
    selected, applied = {}, {}
    for name, block in (("teacher", teacher), *[(name, blocks[name]) for name in STUDENTS]):
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16): logits = block.gate(flat)
        weight, index = F.softmax(logits, dim=1, dtype=torch.float32).topk(block.top_k, dim=-1)
        if block.norm_topk_prob: raise ValueError("E140 requires original no-renorm top8")
        selected[name], applied[name] = index[query], weight.to(hidden.dtype)[query]
    reference_index = selected["teacher"]; reference_weight = applied["teacher"]
    ref_mask = torch.zeros((len(query), experts), device=hidden.device, dtype=torch.bool)
    ref_mask.scatter_(1, reference_index, True)
    ref_dense = torch.zeros((len(query), experts), device=hidden.device, dtype=torch.float32)
    ref_dense.scatter_(1, reference_index, reference_weight.float())
    result = {"teacher_support": torch.bincount(reference_index.reshape(-1), minlength=experts).cpu().numpy(), "top_k": teacher.top_k}
    for name in STUDENTS:
        index, weight = selected[name], applied[name]
        mask = torch.zeros_like(ref_mask); mask.scatter_(1, index, True)
        dense = torch.zeros_like(ref_dense); dense.scatter_(1, index, weight.float())
        delta = dense - ref_dense
        values = (torch.bincount(sequence, minlength=batch),
            inherited.native.grouped((index != reference_index).any(-1).double(), sequence, batch),
            inherited.native.grouped((mask & ref_mask).sum(-1).double(), sequence, batch),
            inherited.native.grouped(delta.abs().sum(-1), sequence, batch),
            inherited.native.grouped(delta.double().square().sum(-1), sequence, batch))
        max_abs = torch.stack([delta[sequence == b].abs().max() for b in range(batch)])
        result[name] = {"rows": torch.stack((*values, max_abs), -1).cpu().numpy(),
            "support": torch.bincount(index.reshape(-1), minlength=experts).cpu().numpy()}
    return result


def route_summary(rows, support, teacher_support, top_k=8):
    totals = rows.sum(0); positions = totals[0]
    return {"positions": int(positions), "slot_mismatch_fraction": float(totals[1] / positions),
        "mean_selected_set_overlap_fraction": float(totals[2] / (top_k * positions)),
        "applied_gate_weight_L1_per_position": float(totals[3] / positions),
        "applied_gate_weight_L2_SSE_per_position": float(totals[4] / positions),
        "applied_gate_weight_max_abs": float(rows[:, 5].max()),
        "student_support_counts": support.astype(int).tolist(), "teacher_support_counts": teacher_support.astype(int).tolist(),
        "scope": "Full B16 native gate rows before query selection; actual applied BF16 selected weights, zero outside own support. No route-based remapping."}


def renamed_contrast(warm, old, old_name, population):
    record = inherited.paired_contrast(warm, old, population)
    record["metrics"] = {name: {"warmstart": value["free"], old_name: value["fixed"],
        "warmstart_minus_" + old_name: value["free_minus_fixed"],
        "paired_input_cluster_ci95": value["paired_input_cluster_ci95"], "defined_draws": value["defined_draws"]}
        for name, value in record["metrics"].items()}
    record["scope"] = f"Warmstart minus {old_name}, same file/word draws and fixed observed cohorts/maps. Conditional input CI, not seed treatment-effect CI."
    return record


@torch.no_grad()
def run_components(model, teacher, banks, proofs, manifest, items, metadata, archived_h, old_record, args, budget):
    data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
    if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Original Dolma held windows differ")
    hcal_path = Path(manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["path"])
    hcal = np.load(hcal_path, mmap_mode="r", allow_pickle=False)
    if hcal.shape != (8192, 2048) or hcal.dtype != np.float32 or assets.sha(hcal_path) != manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["sha256"]:
        raise ValueError("Original native Hcal8192 asset differs")
    pos_pairs = [(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]
    if len(pos_pairs) != 512 or archived_h.shape != (512, 2048): raise ValueError("Exact POS held512/Htarget required")
    pos_items, pos_meta = map(list, zip(*pos_pairs)); old_components = old_record["components"]
    old_sha = assets.sha(WB / "results/e139/readout.json")
    for population in ("Dolma_held_positions", "POS_held_targets"):
        previous = old_components[f"fixed_initial_{population}"]
        if assets.sha(previous["raw"]) != previous["raw_sha256"] or assets.sha(previous["metadata"]) != previous["metadata_sha256"]:
            raise ValueError("Immutable E139 fixed-initial raw/statistics source differs")
    result = {"source_proofs": proofs, "components_script_sha256": assets.sha(__file__),
        "initial_reuse": {"source": str(WB / "results/e139/readout.json"), "source_sha256": old_sha,
            "reason": "All three E140 initial full parameter tensors equal matched E139 fixed initial tensors; same Hcal/held native program and inputs.",
            "calibration": old_components["fixed_initial_calibration"],
            "populations": {population: old_components[f"fixed_initial_{population}"] for population in ("Dolma_held_positions", "POS_held_targets")},
            "initial_route_vs_teacher": "Exact gate tensor identity implies selected masks/weights identical on same native inputs; no new forward."}}
    blocks = {name: banks[name].block for name in STUDENTS}
    calibration = inherited.calibrate(blocks, hcal, budget)
    cost_path = args.raw_output / "final_Hcal_costs.npz"
    np.savez(cost_path, seed0=calibration["maps"]["seed0"].pop("cost"), seed2=calibration["maps"]["seed2"].pop("cost"))
    maps = {"seed1": list(range(64)), **{name: calibration["maps"][name]["source_to_seed1"] for name in ("seed0", "seed2")}}
    calibration.update({"Hcal_path": str(hcal_path), "Hcal_sha256": assets.sha(hcal_path), "cost_path": str(cost_path),
        "cost_sha256": assets.sha(cost_path), "mapping_scope": "Same original E139 full B16×512 Hcal8192 actual-component squared-distance Hungarian to warmstart seed1; one map, no held refit."})
    result["final_calibration"] = calibration
    hhidden = torch.from_numpy(np.array(hcal, copy=True)).to("cuda:0").bfloat16().reshape(16, 512, 2048)
    hroute = route_batch(teacher, blocks, hhidden, torch.arange(8192, device="cuda:0"),
        torch.arange(16, device="cuda:0").repeat_interleave(512))
    result["routing_Hcal"] = {name: route_summary(hroute[name]["rows"], hroute[name]["support"], hroute["teacher_support"], hroute["top_k"])
        for name in STUDENTS}
    del hhidden
    assets.write(args.raw_output / "components_progress.json", result)
    for population in ("Dolma_held_positions", "POS_held_targets"):
        echunks, achunks, rows = [], [], []
        route_rows = {name: [] for name in STUDENTS}; route_support = {name: np.zeros(64, np.int64) for name in STUDENTS}
        teacher_support = np.zeros(64, np.int64)
        if population == "Dolma_held_positions":
            harray = np.load(args.cache_root / "held_H.npy", mmap_mode="r"); iterator = enumerate(data.iter_fixed("held", windows, 16))
        else: iterator = inherited.native.source.operators.protocol.batches(pos_items, 16, "cuda:0", model.config.pad_token_id or 1)
        for entry in iterator:
            budget.check()
            if population == "Dolma_held_positions":
                index, (_, meta) = entry; hidden = c.from_bits(harray[index], "cuda:0")
                query = torch.arange(8192, device="cuda:0"); sequence = torch.arange(16, device="cuda:0").repeat_interleave(512)
            else:
                start, ids, mask, last, targets = entry; captured = {}
                def collect(module, inputs): captured["H"] = inputs[0].detach().clone(); raise inherited.native.PrefixCaptured()
                handle = teacher.register_forward_pre_hook(collect)
                try:
                    try:
                        with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=ids, attention_mask=mask, use_cache=False)
                    except inherited.native.PrefixCaptured: pass
                finally: handle.remove()
                hidden = captured["H"]; query = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last
                sequence = torch.arange(len(ids), device="cuda:0")
                if not np.array_equal(hidden.reshape(-1, 2048)[query].float().cpu().numpy(), archived_h[start:start + len(ids)]):
                    raise ValueError("Exact native POS Htarget replay differs")
                meta = pos_meta[start:start + len(ids)]
            e, a = inherited.measure_batch(blocks, teacher, hidden, query, sequence, maps, budget)
            routing = route_batch(teacher, blocks, hidden, query, sequence)
            echunks.append(e); achunks.append(a); rows.extend(meta); teacher_support += routing["teacher_support"]
            for name in STUDENTS:
                route_rows[name].append(routing[name]["rows"]); route_support[name] += routing[name]["support"]
            base.emit("E140_joint_components", population=population, sequences=len(rows))
        expert, aggregate = np.concatenate(echunks), np.concatenate(achunks)
        path = args.raw_output / f"final_{population}_components.npz"; np.savez(path, expert=expert, aggregate=aggregate)
        meta_path = path.with_suffix(".json"); assets.write(meta_path, {"rows": rows, "expert_fields": inherited.EXPERT,
            "aggregate_fields": inherited.AGG, "maps_source_to_seed1": maps, "Hcal_sha256": calibration["Hcal_sha256"]})
        route_path = args.raw_output / f"final_{population}_routing.npz"
        np.savez(route_path, teacher_support=teacher_support,
            **{name + "_rows": np.concatenate(route_rows[name]) for name in STUDENTS},
            **{name + "_support": route_support[name] for name in STUDENTS})
        record = {"raw": str(path), "raw_sha256": assets.sha(path), "metadata": str(meta_path),
            "metadata_sha256": assets.sha(meta_path), "sequences": len(rows),
            "summary": inherited.summarize(expert, aggregate, rows, population),
            "routing_raw": str(route_path), "routing_raw_sha256": assets.sha(route_path),
            "routing": {name: route_summary(np.concatenate(route_rows[name]), route_support[name], teacher_support, teacher.top_k) for name in STUDENTS}}
        result[f"final_{population}"] = record
        for old_name in ("fixed", "free"):
            old = old_components[f"{old_name}_final_{population}"]
            if assets.sha(old["raw"]) != old["raw_sha256"] or assets.sha(old["metadata"]) != old["metadata_sha256"]:
                raise ValueError("Immutable old E139 final raw input differs")
            result[f"paired_warmstart_minus_{old_name}_{population}"] = renamed_contrast(record, old, old_name, population)
        assets.write(args.raw_output / "components_progress.json", result)
    return result


def self_test():
    import e139_components as old
    old_test = old.self_test()
    class Gate(torch.nn.Module):
        def __init__(self, logits): super().__init__(); self.logits = logits
        def forward(self, h): return torch.tensor(self.logits, dtype=h.dtype).expand(len(h), -1)
    class Block(torch.nn.Module):
        def __init__(self, logits): super().__init__(); self.gate = Gate(logits); self.num_experts = 3; self.top_k = 2; self.norm_topk_prob = False
    h = torch.ones(2, 3, 2).bfloat16(); q = torch.tensor([1, 5]); sequence = torch.tensor([0, 1])
    reference = Block([3., 2., -100.]); students = {"seed0": Block([3., 2., -100.]),
        "seed1": Block([-100., 2., 3.]), "seed2": Block([3., 2., -100.])}
    route = route_batch(reference, students, h, q, sequence)
    assert route_summary(route["seed0"]["rows"], route["seed0"]["support"], route["teacher_support"])["slot_mismatch_fraction"] == 0
    assert route_summary(route["seed1"]["rows"], route["seed1"]["support"], route["teacher_support"], top_k=2)["mean_selected_set_overlap_fraction"] == .5
    return {"passed": True, "CPU_only": True, "E139_contract_reused": old_test["passed"],
        "route_fullrow_support_weight_math": True, "source_sha256": assets.sha(__file__)}
