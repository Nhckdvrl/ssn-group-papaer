"""E135 U/A in a common NATIVE public-teacher U background; tuple-safe."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import torch
import e124_functional_capture as protocol
import e135_common as c

WB = c.WB


class MeasuredPublic(torch.nn.Module):
    def __init__(self, state, device="cuda:0", dims=None):
        super().__init__(); dims = dims or c.DIMS
        with torch.device("meta"): self.inner = protocol.MeasuredMoE(dims["hidden"], dims["expert_size"], dims["experts"], dims["top_k"], .02)
        state = {key if key.startswith("block.") else "block." + key: value for key, value in state.items()}
        self.inner.load_state_dict(state, strict=True, assign=True); self.inner = self.inner.to(device).eval().requires_grad_(False)
    @property
    def block(self): return self.inner.block
    def forward(self, hidden):
        output = self.inner(hidden)
        return output, self.inner.last_router_logits


def teacher_probe(bank, context):
    def hook(module, inputs, result):
        if not isinstance(result, tuple): raise ValueError("E135 U background must be native public tuple-MoE")
        output, tail = result[0], result[1:]; mode = context["mode"]
        rows, last = context["rows"], context["last"]
        if mode == "native":
            context["Htarget"] = inputs[0][rows, last].detach().float().cpu()
            return result
        changed = output.clone()
        if mode == "identity": return (changed, *tail)
        if mode == "zero": changed[rows, last] = 0
        elif mode == "inject": changed[rows, last] = .125 * bank.block.experts[context["expert"]](inputs[0][rows, last])
        else: raise ValueError(mode)
        return changed, *tail
    return hook


@torch.no_grad()
def capture(model, original, bank, condition, proof, manifest, args, budget):
    output = args.raw_output / f"{condition}_functional.npz"
    summary_path = WB / "results/e135/functional" / f"{condition}.json"
    if output.exists():
        previous = c.assets.read(summary_path)
        if (not previous or previous.get("output_sha256") != c.assets.sha(output) or previous.get("capture_script_sha256") != c.assets.sha(__file__)
                or previous.get("condition_proof") != proof or previous.get("background_kind") != "native_public_teacher"
                or previous.get("condition_tensor_sha256") != c.tensor_state_hash(bank.inner.state_dict())):
            raise ValueError("Existing functional array has different/missing source proof")
        return output, previous
    plan, items, metadata = protocol.load_plan(args.plan)
    if c.assets.sha(args.plan) != c.assets.PLAN_SHA or len(items) != 1024: raise ValueError("Fixed plan population differs")
    count, experts = len(items), 64
    arrays = {"U": np.zeros((count, experts), np.float32), "A": np.zeros((count, experts), np.float32),
        "background_nll": np.zeros(count, np.float32), "zero_nll": np.zeros(count, np.float32), "normal_nll": np.zeros(count, np.float32),
        "Htarget": np.zeros((count, 2048), np.float32), "selected_experts": np.zeros((count, 8), np.int64),
        "selected_weights": np.zeros((count, 8), np.float32), "selected_mask": np.zeros((count, experts), bool),
        "gate_weights": np.zeros((count, experts), np.float32), "gate": bank.block.gate.weight.detach().float().cpu().numpy().copy()}
    noise = {key: np.zeros(count, np.float32) for key in ("background_identity", "zero_repeat", "inject_repeat", "natural_repeat", "natural_identity")}
    scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16", _head_weight_fp32=model.lm_head.weight.detach().float(),
        _head_bias_fp32=model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None)
    context = {}; tie_audit = {"rows": 0, "row_only_slot_order_mismatch_rows": 0, "row_only_selected_set_mismatch_rows": 0}
    model.model.layers[9].mlp = original
    hook = original.register_forward_hook(teacher_probe(bank, context))
    try:
        for start, ids, mask, last, target in protocol.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
            budget.check(); end = start + len(ids); context.update({"rows": torch.arange(len(ids), device="cuda:0"), "last": last, "mode": "native"})
            background = protocol.target_log_prob(model, ids, mask, last, target, scoring)
            arrays["background_nll"][start:end] = -background.cpu().numpy(); arrays["Htarget"][start:end] = context["Htarget"].numpy()
            context["mode"] = "identity"; noise["background_identity"][start:end] = (protocol.target_log_prob(model, ids, mask, last, target, scoring) - background).cpu().numpy()
            context["mode"] = "zero"; zero = protocol.target_log_prob(model, ids, mask, last, target, scoring)
            arrays["zero_nll"][start:end] = -zero.cpu().numpy()
            noise["zero_repeat"][start:end] = (protocol.target_log_prob(model, ids, mask, last, target, scoring) - zero).cpu().numpy()
            context["mode"] = "inject"
            for expert in range(experts):
                budget.check(); context["expert"] = expert; injected = protocol.target_log_prob(model, ids, mask, last, target, scoring)
                arrays["U"][start:end, expert] = (injected - zero).cpu().numpy()
                if expert == 0: noise["inject_repeat"][start:end] = (protocol.target_log_prob(model, ids, mask, last, target, scoring) - injected).cpu().numpy()
            c.base.emit("native_background_U", condition=condition, completed=end, total=count)
    finally: hook.remove()
    model.model.layers[9].mlp = bank
    try:
        for start, ids, mask, last, target in protocol.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
            budget.check(); end = start + len(ids); bank.inner.measurement = {}
            normal = protocol.target_log_prob(model, ids, mask, last, target, scoring)
            logits = bank.inner.last_router_logits.reshape(-1, experts).float()
            full_weights, full_selected = logits.softmax(-1).topk(8, -1)
            target_rows = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last
            weights, selected = full_weights[target_rows], full_selected[target_rows]
            row_selected = logits[target_rows].softmax(-1).topk(8, -1).indices
            tie_audit["rows"] += len(ids)
            tie_audit["row_only_slot_order_mismatch_rows"] += int((row_selected != selected).any(-1).sum())
            tie_audit["row_only_selected_set_mismatch_rows"] += int((row_selected.sort(-1).values != selected.sort(-1).values).any(-1).sum())
            selected_cpu = selected.cpu().numpy()
            arrays["normal_nll"][start:end] = -normal.cpu().numpy(); arrays["selected_experts"][start:end] = selected_cpu
            arrays["selected_weights"][start:end] = weights.cpu().numpy()
            np.put_along_axis(arrays["selected_mask"][start:end], selected_cpu, True, axis=1)
            np.put_along_axis(arrays["gate_weights"][start:end], selected_cpu, weights.cpu().numpy(), axis=1)
            noise["natural_repeat"][start:end] = (protocol.target_log_prob(model, ids, mask, last, target, scoring) - normal).cpu().numpy()
            bank.inner.measurement = {"intervention": True, "drop_slot": None, "last": last}
            noise["natural_identity"][start:end] = (protocol.target_log_prob(model, ids, mask, last, target, scoring) - normal).cpu().numpy()
            for slot in range(8):
                bank.inner.measurement["drop_slot"] = slot
                dropped = protocol.target_log_prob(model, ids, mask, last, target, scoring)
                arrays["A"][np.arange(start, end), selected_cpu[:, slot]] = (normal - dropped).cpu().numpy()
            c.base.emit("native_natural_A", condition=condition, completed=end, total=count)
    finally: model.model.layers[9].mlp = original; bank.inner.measurement = {}
    for key in ("word", "label", "split", "document", "input_sha256"): arrays[key] = np.array([row[key] for row in metadata], dtype=str)
    arrays["item_id"] = np.array([row["item_id"] for row in metadata], np.int64)
    hcal_path = manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["path"]
    arrays["Hcal"] = np.load(hcal_path, allow_pickle=False)
    for key, values in noise.items(): arrays["noise_" + key] = values
    header = {"experiment": "E135", "condition": condition, "alpha": .125, "layer": 9, "experts": 64, "top_k": 8,
        "seed": 1 if condition in ("initial", "final") else None, "order_seed": 135 if condition in ("initial", "final") else None,
        "step": 4096 if condition == "final" else 0, "plan_sha256": c.assets.sha(args.plan), "source_sha256": plan["source_sha256"],
        "selected_inputs_sha256": plan["selected_inputs_sha256"], "condition_proof": proof,
        "condition_tensor_sha256": c.tensor_state_hash(bank.inner.state_dict()), "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"],
        "background_kind": "native_public_teacher", "U_scope": "Common native-public teacher background; at last input position zero versus1/8 expert injection",
        "A_scope": "Each condition's natural full-model bank at all positions; last-position selected weight removed, no renormalization",
        "readout_precision": "BF16 backbone/experts, genuine FP32 last-hidden lm_head/logsoftmax", "expert_storage_dtypes": sorted({str(value.dtype) for value in bank.parameters()}),
        "public_Hcal_sha256": c.assets.sha(hcal_path), "capture_script_sha256": c.assets.sha(__file__),
        "A_selection_scope": "Native full [batch*sequence,64] softmax/top8 before indexing target rows; same full shape as the drop-slot operator",
        "row_shape_tie_audit": tie_audit,
        "noise": {key: {"mean_abs": float(np.abs(value).mean()), "max_abs": float(np.abs(value).max())} for key, value in noise.items()}}
    arrays["metadata_json"] = np.array(json.dumps(header, allow_nan=False))
    with output.open("wb") as handle: np.savez(handle, **arrays)
    summary = {**header, "output": str(output), "output_sha256": c.assets.sha(output), "shapes": {key: list(value.shape) for key, value in arrays.items()}}
    c.assets.write(summary_path, summary)
    return output, summary


def self_test():
    torch.set_num_threads(1); torch.manual_seed(135)
    tensor = c.base.TensorMoE(8, 8, 4, 2, .02).eval().requires_grad_(False); original = tensor.block
    dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2}
    bank = MeasuredPublic(tensor.state_dict(), "cpu", dims); hidden = torch.randn(2, 3, 8)
    with torch.no_grad():
        native = original(hidden); measured = bank(hidden)
        assert torch.equal(native[0], measured[0]) and torch.equal(native[1], measured[1])
        context = {"rows": torch.arange(2), "last": torch.tensor([1, 2]), "mode": "zero"}
        hook = teacher_probe(bank, context); changed = hook(original, (hidden,), native)
        assert changed[1] is native[1] and torch.equal(changed[0][context["rows"], context["last"]], torch.zeros(2, 8))
        context["mode"] = "inject"; context["expert"] = 0
        injected = hook(original, (hidden,), native)
        expected = .125 * bank.block.experts[0](hidden[context["rows"], context["last"]])
        assert torch.equal(injected[0][context["rows"], context["last"]], expected)
        keep = torch.ones((2, 3), dtype=torch.bool); keep[context["rows"], context["last"]] = False
        assert torch.equal(injected[0][keep], native[0][keep])
    return {"passed": True, "CPU_only": True, "native_tuple_hook_and_last_position_scope": True, "measured_public_natural_matches_native": True,
            "native_background_not_dense": True, "script_sha256": c.assets.sha(__file__)}


if __name__ == "__main__":
    result = self_test(); c.assets.write(WB / "results/e135/capture_self_test.json", result); print(json.dumps(result, indent=2))
