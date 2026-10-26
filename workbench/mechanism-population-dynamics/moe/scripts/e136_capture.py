"""E136 native-public U/A; coupled initial-U reuse, fresh initial/final A."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import torch
import e135_capture as operator
import e136_train as training

c, protocol = operator.c, operator.protocol
WB, assets = c.WB, c.assets
U_FIELDS = ("U", "background_nll", "zero_nll", "Htarget", "Hcal", "noise_background_identity", "noise_zero_repeat", "noise_inject_repeat")


def teacher_support(args, manifest, metadata):
    path = args.e135_raw / "teacher_functional.npz"; summary = assets.read(WB / "results/e135/functional/teacher.json")
    if not summary or assets.sha(path) != summary["output_sha256"]: raise ValueError("Teacher profile SHA differs")
    plan = assets.read(args.plan)
    with np.load(path, allow_pickle=False) as raw:
        header = json.loads(str(raw["metadata_json"]))
        expected = {"experiment": "E135", "condition": "teacher", "background_kind": "native_public_teacher", "alpha": .125,
            "plan_sha256": assets.PLAN_SHA, "source_sha256": plan["source_sha256"], "selected_inputs_sha256": plan["selected_inputs_sha256"],
            "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"]}
        if any(header.get(key) != value for key, value in expected.items()): raise ValueError("Teacher support header/background/source differs")
        for key in ("item_id", "input_sha256", "word", "label", "document", "split"):
            if not np.array_equal(raw[key], np.array([row[key] for row in metadata])): raise ValueError("Teacher support population differs")
        values = tuple(np.asarray(raw[key]).copy() for key in ("selected_experts", "selected_weights", "selected_mask"))
    return values, {"path": str(path), "sha256": assets.sha(path), "teacher_block_tensor_sha256": header["teacher_block_tensor_sha256"], "population_exact": True}


def reused_initial_u(args, proof, manifest, metadata):
    path = args.e135_raw / "initial_functional.npz"; summary = assets.read(WB / "results/e135/functional/initial.json")
    if not summary or assets.sha(path) != summary["output_sha256"]: raise ValueError("Original E135 initial functional SHA differs")
    with np.load(path, allow_pickle=False) as raw:
        header = json.loads(str(raw["metadata_json"]))
        expected = {"experiment": "E135", "condition": "initial", "alpha": .125, "background_kind": "native_public_teacher",
                    "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"], "plan_sha256": assets.PLAN_SHA,
                    "condition_tensor_sha256": proof["initialization"]["source_initial_full_tensor_sha256"]}
        if any(header.get(key) != value for key, value in expected.items()): raise ValueError("Original initial-U background/source differs")
        if header["condition_proof"]["checkpoint_sha256"] != proof["initialization"]["source_initial_sha256"]:
            raise ValueError("Initial-U lacks its exact original initial-checkpoint binding")
        if proof["expert_only_tensor_sha256"] != proof["initialization"]["source_expert_only_sha256"]:
            raise ValueError("Oracle initial expert functions/order differ from the U source")
        for key in ("item_id", "input_sha256", "word", "split"):
            if not np.array_equal(raw[key], np.array([row[key] for row in metadata])): raise ValueError("Initial-U sample identity differs")
        arrays = {key: np.asarray(raw[key]).copy() for key in U_FIELDS}
    return arrays, {"status": "coupled_reuse", "source": str(path), "source_sha256": assets.sha(path),
        "expert_only_sha256": proof["expert_only_tensor_sha256"], "source_initial_sha256": proof["initialization"]["source_initial_sha256"],
        "reason": "Only the gate changed; common native-teacher U injection uses identical expert functions, inputs andalpha.125; no old A/normal/support reused"}


@torch.no_grad()
def capture(model, original, bank, condition, proof, manifest, args, budget):
    output = args.raw_output / f"{condition}_functional.npz"; summary_path = WB / "results/e136/functional" / f"{condition}.json"
    if output.exists():
        previous = assets.read(summary_path)
        if not previous or previous.get("output_sha256") != assets.sha(output) or previous.get("condition_proof") != proof or previous.get("script_sha256") != assets.sha(__file__):
            raise ValueError("Existing E136 profile has different source proof")
        return output, previous
    plan, items, metadata = protocol.load_plan(args.plan)
    if assets.sha(args.plan) != assets.PLAN_SHA or len(items) != 1024: raise ValueError("Fixed1024 cal/held population required")
    if condition == "oracle_initial": arrays, reuse = reused_initial_u(args, proof, manifest, metadata)
    else:
        arrays = {"U": np.zeros((1024, 64), np.float32), "background_nll": np.zeros(1024, np.float32), "zero_nll": np.zeros(1024, np.float32),
                  "Htarget": np.zeros((1024, 2048), np.float32)}; reuse = {"status": "fresh"}
    arrays.update({"A": np.zeros((1024, 64), np.float32), "normal_nll": np.zeros(1024, np.float32),
        "selected_experts": np.zeros((1024, 8), np.int64), "selected_weights": np.zeros((1024, 8), np.float32),
        "selected_mask": np.zeros((1024, 64), bool), "gate_weights": np.zeros((1024, 64), np.float32),
        "gate": bank.block.gate.weight.detach().float().cpu().numpy().copy()})
    scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16", _head_weight_fp32=model.lm_head.weight.detach().float(),
        _head_bias_fp32=model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None)
    model.model.layers[9].mlp = original
    if condition != "oracle_initial":
        context = {}; hook = original.register_forward_hook(operator.teacher_probe(bank, context))
        try:
            for start, ids, mask, last, targets in protocol.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
                budget.check(); end = start + len(ids); context.update({"rows": torch.arange(len(ids), device="cuda:0"), "last": last, "mode": "native"})
                background = protocol.target_log_prob(model, ids, mask, last, targets, scoring)
                arrays["background_nll"][start:end] = -background.cpu().numpy(); arrays["Htarget"][start:end] = context["Htarget"].numpy()
                context["mode"] = "zero"; zero = protocol.target_log_prob(model, ids, mask, last, targets, scoring)
                arrays["zero_nll"][start:end] = -zero.cpu().numpy(); context["mode"] = "inject"
                for expert in range(64):
                    budget.check(); context["expert"] = expert
                    arrays["U"][start:end, expert] = (protocol.target_log_prob(model, ids, mask, last, targets, scoring) - zero).cpu().numpy()
                c.base.emit("E136_U", condition=condition, completed=end)
        finally: hook.remove()
    (teacher_indices, teacher_weights, teacher_mask), teacher_profile_proof = teacher_support(args, manifest, metadata)
    noise = {key: np.zeros(1024, np.float32) for key in ("natural_repeat", "natural_identity")}
    support = {"rows": 0, "teacher_slot_mismatch_rows": 0, "teacher_mask_mismatch_rows": 0, "teacher_weight_max_abs_difference": 0.}
    model.model.layers[9].mlp = bank
    try:
        for start, ids, mask, last, targets in protocol.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
            budget.check(); end = start + len(ids); bank.inner.measurement = {}
            normal = protocol.target_log_prob(model, ids, mask, last, targets, scoring)
            full = bank.inner.last_router_logits.reshape(-1, 64).float().softmax(-1); weights, selected = full.topk(8, -1)
            rows = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last
            selected, weights = selected[rows], weights[rows]; selected_cpu, weights_cpu = selected.cpu().numpy(), weights.cpu().numpy()
            arrays["normal_nll"][start:end] = -normal.cpu().numpy(); arrays["selected_experts"][start:end] = selected_cpu
            arrays["selected_weights"][start:end] = weights_cpu; np.put_along_axis(arrays["selected_mask"][start:end], selected_cpu, True, axis=1)
            np.put_along_axis(arrays["gate_weights"][start:end], selected_cpu, weights_cpu, axis=1)
            support["rows"] += len(ids); support["teacher_slot_mismatch_rows"] += int(np.any(selected_cpu != teacher_indices[start:end], axis=1).sum())
            support["teacher_mask_mismatch_rows"] += int(np.any(arrays["selected_mask"][start:end] != teacher_mask[start:end], axis=1).sum())
            support["teacher_weight_max_abs_difference"] = max(support["teacher_weight_max_abs_difference"], float(np.max(np.abs(weights_cpu - teacher_weights[start:end]))))
            noise["natural_repeat"][start:end] = (protocol.target_log_prob(model, ids, mask, last, targets, scoring) - normal).cpu().numpy()
            bank.inner.measurement = {"intervention": True, "drop_slot": None, "last": last}
            noise["natural_identity"][start:end] = (protocol.target_log_prob(model, ids, mask, last, targets, scoring) - normal).cpu().numpy()
            for slot in range(8):
                bank.inner.measurement["drop_slot"] = slot
                dropped = protocol.target_log_prob(model, ids, mask, last, targets, scoring)
                arrays["A"][np.arange(start, end), selected_cpu[:, slot]] = (normal - dropped).cpu().numpy()
            c.base.emit("E136_A", condition=condition, completed=end)
    finally: model.model.layers[9].mlp = original; bank.inner.measurement = {}
    for key in ("word", "label", "split", "document", "input_sha256"): arrays[key] = np.array([row[key] for row in metadata], dtype=str)
    arrays["item_id"] = np.array([row["item_id"] for row in metadata], np.int64)
    if "Hcal" not in arrays: arrays["Hcal"] = np.load(manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["path"], allow_pickle=False)
    for key, value in noise.items(): arrays["noise_" + key] = value
    header = {"experiment": "E136", "condition": condition, "alpha": .125, "layer": 9, "experts": 64, "top_k": 8,
        "background_kind": "native_public_teacher", "plan_sha256": assets.sha(args.plan), "source_sha256": plan["source_sha256"],
        "selected_inputs_sha256": plan["selected_inputs_sha256"], "condition_proof": proof, "U_source": reuse,
        "condition_tensor_sha256": c.tensor_state_hash(bank.inner.state_dict()), "gate_tensor_sha256": training.gate_hash(bank.inner.state_dict()),
        "teacher_support": support, "teacher_support_profile": teacher_profile_proof, "script_sha256": assets.sha(__file__),
        "A_selection_scope": "Full [batch*sequence,64] native softmax/topk then target-row selection, same shape as contribution removal",
        "scope": "Initial A is a shared-support control, not pure specialization. Fixed identity is supplied organization, not learned task identification.",
        "noise": {key: {"mean_abs": float(np.abs(value).mean()), "max_abs": float(np.abs(value).max())} for key, value in noise.items()}}
    arrays["metadata_json"] = np.array(json.dumps(header, allow_nan=False)); args.raw_output.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle: np.savez(handle, **arrays)
    summary = {**header, "output": str(output), "output_sha256": assets.sha(output)}; assets.write(summary_path, summary)
    return output, summary
