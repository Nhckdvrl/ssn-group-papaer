"""E144/E145: prepare, train-side validate, then complete fixed held interventions.

Example (existing mechpop environment; no installs):
  python e144145_run.py prepare --work-root /tmp/xiang-moe-20261026/e144145
  python e144145_run.py preflight --experiment e144 --physical-gpu 0
  python e144145_run.py evaluate --experiment e144 --physical-gpu 0
Each experiment has its own cumulative ledger and immutable held selection.
"""
from __future__ import annotations

import argparse
import gc
import json
import socket
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from torch import nn
from transformers import OlmoeForCausalLM

import e144145_common as c


class Observer(nn.Module):
    def __init__(self, operator, expected_hidden=None, components=False):
        super().__init__()
        self.operator, self.expected_hidden, self.components = operator, expected_hidden, components
        self.observed = None

    def forward(self, hidden):
        if hidden.dtype != torch.bfloat16:
            raise ValueError("Original interface must remain BF16")
        if self.expected_hidden is not None and not torch.equal(hidden, self.expected_hidden):
            raise ValueError("Common prefix/input changed across interventions")
        self.hidden = hidden.detach()
        if self.components:
            self.observed = c.trace(self.operator, hidden)
            return self.observed["native"], self.observed["logits"]
        result = self.operator(hidden)
        self.observed = {"native": result[0].detach()}
        return result


@torch.no_grad()
def forward(model, operator, tokens, hidden=None, components=True):
    watch = Observer(operator, hidden, components)
    model.model.layers[9].mlp = watch
    with torch.autocast("cuda", dtype=torch.bfloat16):
        logits = model(input_ids=tokens[:, :-1], use_cache=False).logits
    if logits.dtype != torch.bfloat16:
        raise ValueError("Whole-model logits precision drifted")
    logp = logits.float().log_softmax(-1)
    del logits
    return logp, watch.observed, watch.hidden


def load(args, proof):
    if transformers.__version__ != "4.57.6" or torch.__version__ != "2.8.0+cu128":
        raise ValueError("Use the existing registered mechpop environment")
    model = OlmoeForCausalLM.from_pretrained(proof["model"], dtype=torch.bfloat16, local_files_only=True,
                                           attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False)
    model.config.use_cache = False
    teacher = model.model.layers[9].mlp
    if c.tensor_hash(teacher.state_dict()) != proof["teacher_block_tensor_sha256"]:
        raise ValueError("Teacher block tensor identity differs")
    if c.base.sampled_parameter_hash(model, "model.layers.9.mlp.") != proof["teacher_prefix_sample_hash"]:
        raise ValueError("Common public model sampled prefix/downstream identity differs")
    names = ("F0", "F1", "F2") if args.experiment == "e144" else ("A", "R0", "R2", "S0", "S2")
    blocks = {}
    for name in names:
        p = proof["sources"][name]
        path = Path(p["staged_state"])
        if c.sha(path) != p["staged_sha256"]:
            raise ValueError(f"Staged file changed: {name}")
        state = torch.load(path, map_location="cpu", mmap=True, weights_only=True)
        if c.tensor_hash(state) != p["tensor_sha256"]:
            raise ValueError(f"Staged source tensor changed: {name}")
        blocks[name] = c.block_from_state(state, model.config, "cuda:0")
        del state
    return model, teacher, blocks


def operators_e145(blocks, proof):
    operators = {"AA": c.Assembled(blocks["A"], range(64), list(blocks["A"].experts))}
    anchor = list(blocks["A"].experts)
    for donor in ("R0", "R2", "S0", "S2"):
        mapping = proof["sources"][donor]["source_to_common"]
        experts = c.common_experts(blocks[donor], mapping)
        operators[donor + "_dd"] = c.Assembled(blocks[donor], mapping, experts)
        operators[donor + "_Ad"] = c.Assembled(blocks["A"], range(64), experts)
        operators[donor + "_dA"] = c.Assembled(blocks[donor], mapping, anchor)
    return operators


def difference(a, b, target, trace_a=None, trace_b=None):
    metric = c.prediction_metrics(a, b, target)
    row = {"logp_max_abs": float((a - b).abs().max()),
           "nll_gap": float((metric[..., 0] + a.gather(-1, target[..., None]).squeeze(-1)).double().mean()),
           "forward_kl": float(metric[..., 1].double().mean()), "reverse_kl": float(metric[..., 2].double().mean())}
    if trace_a is not None:
        row["layer_max_abs"] = float((trace_a["native"] - trace_b["native"]).float().abs().max())
        if "q" in trace_a:
            # Coordinates can differ under a joint relabel; native output remains invariant.
            row["applied_gate_sorted_max_abs"] = float((trace_a["q"].sort(-1).values - trace_b["q"].sort(-1).values).abs().max())
    return row


@torch.no_grad()
def preflight(args, proof, model, teacher, blocks, budget):
    tokens = np.load(c.RECIPE / "train_tokens.npy", mmap_mode="r", allow_pickle=False).reshape(-1, 16, 513)[0]
    tokens = torch.from_numpy(np.array(tokens, dtype=np.int64)).to("cuda:0")
    target = tokens[:, 1:]
    result = {"experiment": args.experiment, "phase": "training_batch0_only", "source_sha256": c.code_proof(),
              "asset_preflight_sha256": c.sha(args.work_root / "assets.json"), "controls": {}, "forward_calls": 0,
              "input_sha256": __import__("hashlib").sha256(tokens.cpu().numpy().astype("<i8").tobytes()).hexdigest()}

    def predict(op, hidden=None, components=True):
        budget.check()
        result["forward_calls"] += 1
        return forward(model, op, tokens, hidden, components)

    if args.experiment == "e144":
        pteacher, tteacher, hidden = predict(teacher)
        copy_state = {"block." + k: v.float() for k, v in teacher.state_dict().items()}
        copied = c.block_from_state(copy_state, model.config, "cuda:0")
        pcopy, tcopy, _ = predict(copied, hidden)
        result["controls"]["teacher_copy"] = difference(pteacher, pcopy, target, tteacher, tcopy)
        del pcopy, tcopy, copied, copy_state
        traces, zero_response = [], None
        for name, block in blocks.items():
            original, original_trace, _ = predict(block, hidden)
            assembled = c.Assembled(block, range(64), list(block.experts))
            same, same_trace, _ = predict(assembled, hidden)
            result["controls"][name + "_same_source"] = difference(original, same, target, original_trace, same_trace)
            fixed = c.FixedOutput(original_trace["sum64"].to(hidden.dtype), block.gate)
            summed, _, _ = predict(fixed, hidden, components=False)
            result["controls"][name + "_sum64_cast"] = difference(original, summed, target)
            result["controls"][name + "_sum64_cast"]["layer_floor_sse_per_position"] = float(
                (original_trace["native"].double() - original_trace["sum64"]).square().sum(-1).mean())
            traces.append(original_trace)
            if name == "F0":
                repeated, repeated_trace, _ = predict(block, hidden)
                result["controls"]["F0_repeat"] = difference(original, repeated, target, original_trace, repeated_trace)
                del repeated, repeated_trace
            del original, same, same_trace, summed
        moments, mu = c.cohort(traces)
        result["training_side_moments"] = {k: float(v.mean()) for k, v in moments.items()}
        result["mu_cast_sse_per_position"] = float((mu - mu.bfloat16().double()).square().sum(-1).mean())
        pzero, _, _ = predict(c.FixedOutput(torch.zeros_like(hidden), teacher.gate), hidden, components=False)
        result["controls"]["zero_response"] = difference(pteacher, pzero, target)
        if result["controls"]["zero_response"]["forward_kl"] <= 1e-8:
            raise ValueError("Zero intervention failed the training-side reader positive control")
    else:
        operators = operators_e145(blocks, proof)
        original, trace_original, hidden = predict(blocks["A"])
        same, trace_same, _ = predict(operators["AA"], hidden)
        result["controls"]["A_self"] = difference(original, same, target, trace_original, trace_same)
        repeated, trace_repeat, _ = predict(operators["AA"], hidden)
        result["controls"]["A_repeat"] = difference(same, repeated, target, trace_same, trace_repeat)
        del same, trace_same, repeated, trace_repeat
        teacherp, _, _ = predict(teacher, hidden)
        result["controls"]["teacher_to_A"] = difference(teacherp, original, target)
        del teacherp
        for donor in ("R0", "R2", "S0", "S2"):
            pn, tn, _ = predict(blocks[donor], hidden)
            pd, td, _ = predict(operators[donor + "_dd"], hidden)
            result["controls"][donor + "_joint_native_diagonal"] = difference(pn, pd, target, tn, td)
            mapped = torch.tensor(proof["sources"][donor]["source_to_common"], device=hidden.device)[tn["selected"]]
            if not torch.equal(mapped, td["selected"]):
                raise ValueError("Joint relabel altered physical native Top-k selection")
            del pn, pd, tn, td
    # Exact identity is expected because native gate traversal and input shape agree.
    for name, row in result["controls"].items():
        if any(s in name for s in ("same_source", "teacher_copy", "_self", "_repeat", "_diagonal")):
            if row["layer_max_abs"] != 0 or row["logp_max_abs"] != 0:
                raise ValueError(f"Assembly/reader identity failed: {name}: {row}")
    result.update(status="passed", peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                  precision="FP32 trained bank storage; BF16 native GEMMs/products/aggregate/logits; FP32 logsoftmax; FP64 layer moments")
    c.write(c.WB / f"results/{args.experiment}/floors.json", result)
    c.emit("training_preflight_passed", experiment=args.experiment, forward_calls=result["forward_calls"],
           peak_gb=result["peak_allocated_bytes"] / 1e9)
    return result


def layer_values(trace, teacher, mu):
    native, summed = trace["native"].double(), trace["sum64"]
    return torch.stack(((native - teacher["native"].double()).square().sum(-1),
                        (summed - teacher["sum64"]).square().sum(-1),
                        (native - summed).square().sum(-1),
                        (native - mu).square().sum(-1), (summed - mu).square().sum(-1)), -1)


LAYER_FIELDS = ("native_teacher_sse", "sum64_teacher_sse", "native_sum64_floor_sse", "native_mu_sse", "sum64_mu_sse")


@torch.no_grad()
def batch_e144(args, proof, model, teacher, blocks, tokens, budget):
    source_maps = c.read(c.WB / "results/e144/source_maps.json")
    mixed = [r["name"] for r in source_maps["maps"]]
    names = ["F0", "F1", "F2", "mu", "teacher", "zero", *mixed]
    primary = np.empty((len(names), 16, 512, len(c.METRICS)), np.float32)
    teacher_metrics = np.empty_like(primary)
    layers = np.empty((len(names), 16, 512, len(LAYER_FIELDS)), np.float64)
    target = tokens[:, 1:]
    predictions, traces = {}, {}
    budget.check()
    pt, tt, hidden = forward(model, teacher, tokens)
    predictions["teacher"], traces["teacher"] = pt, tt
    for name in ("F0", "F1", "F2"):
        budget.check()
        p, t, _ = forward(model, blocks[name], tokens, hidden)
        predictions[name], traces[name] = p, t
    moments, mu = c.cohort([traces[n] for n in ("F0", "F1", "F2")])
    budget.check()
    pm, _, _ = forward(model, c.FixedOutput(mu.bfloat16(), teacher.gate), tokens, hidden, components=False)
    predictions["mu"] = pm

    def store(name, logp, tr):
        i = names.index(name)
        primary[i] = c.prediction_metrics(pm, logp, target).cpu().numpy()
        teacher_metrics[i] = c.prediction_metrics(pt, logp, target).cpu().numpy()
        layers[i] = layer_values(tr, tt, mu).cpu().numpy()

    for name in ("F0", "F1", "F2", "teacher"):
        store(name, predictions[name], traces[name])
    mu_trace = {"native": mu.bfloat16(), "sum64": mu}
    store("mu", pm, mu_trace)
    budget.check()
    zero = torch.zeros_like(hidden)
    pz, _, _ = forward(model, c.FixedOutput(zero, teacher.gate), tokens, hidden, components=False)
    store("zero", pz, {"native": zero, "sum64": zero.double()})
    del pz
    mixed_sum = torch.zeros_like(mu)
    component_max_difference = 0.
    for row in source_maps["maps"]:
        budget.check()
        experts = [blocks[f"F{s}"].experts[e] for e, s in enumerate(row["sources"])]
        assembled = c.Assembled(blocks["F0"], range(64), experts)
        p, t, _ = forward(model, assembled, tokens, hidden)
        for e, s in enumerate(row["sources"]):
            observed, expected = t["components"][e], traces[f"F{s}"]["components"][e]
            if not torch.equal(observed["row"], expected["row"]):
                raise ValueError("Mixed bank input support differs")
            if observed["component"].numel():
                component_max_difference = max(component_max_difference, float((observed["component"] - expected["component"]).float().abs().max()))
        store(row["name"], p, t)
        mixed_sum += t["sum64"] / len(source_maps["maps"])
        del p, t
    balance = float((mixed_sum - mu).abs().max())
    if component_max_difference != 0 or balance > 1e-12:
        raise ValueError(f"Component/first-moment assembly differs: {component_max_difference}, {balance}")
    return {"names": np.array(names), "metrics": primary, "teacher_metrics": teacher_metrics, "layer": layers,
            "moment_names": np.array(list(moments)), "moments": torch.stack(list(moments.values()), -1).cpu().numpy(),
            "layer_fields": np.array(LAYER_FIELDS), "metric_fields": np.array(c.METRICS),
            "arithmetic_floors": np.array([balance, component_max_difference, float((mu - mu.bfloat16().double()).square().sum(-1).mean())]),
            "arithmetic_floor_names": np.array(["balanced_sum64_mean_max_abs", "component_selected_native_max_abs", "mu_cast_sse_per_position"])}


@torch.no_grad()
def batch_e145(args, proof, model, teacher, blocks, tokens, budget):
    operators = operators_e145(blocks, proof)
    donors = ("R0", "R2", "S0", "S2")
    names = ["AA", "teacher", *[d + "_" + kind for d in donors for kind in ("dd", "Ad", "dA")]]
    metrics = {key: np.empty((len(names), 16, 512, len(c.METRICS)), np.float32) for key in ("A", "teacher", "donor")}
    target = tokens[:, 1:]
    predictions, traces = {}, {}
    budget.check()
    predictions["teacher"], traces["teacher"], hidden = forward(model, teacher, tokens)
    for name in ("AA", *[d + "_dd" for d in donors]):
        budget.check()
        predictions[name], traces[name], _ = forward(model, operators[name], tokens, hidden)

    def store(name, logp):
        i = names.index(name)
        donor = name.split("_")[0] if "_" in name else None
        ref = predictions[donor + "_dd"] if donor else predictions[name]
        for key, p in (("A", predictions["AA"]), ("teacher", predictions["teacher"]), ("donor", ref)):
            metrics[key][i] = c.prediction_metrics(p, logp, target).cpu().numpy()

    for name, logp in predictions.items():
        store(name, logp)
    for donor in donors:
        for kind in ("Ad", "dA"):
            budget.check()
            name = donor + "_" + kind
            p, t, _ = forward(model, operators[name], tokens, hidden)
            traces[name] = t
            store(name, p)
            del p
    common_moments = {}
    for group in ("R", "S"):
        values, _ = c.cohort([traces[group + "0_Ad"], traces["AA"], traces[group + "2_Ad"]])
        common_moments[group] = torch.stack(list(values.values()), -1).cpu().numpy()
        native_values, _ = c.cohort_general([traces[group + "0_dd"], traces["AA"], traces[group + "2_dd"]])
        common_moments[group + "_native"] = torch.stack(list(native_values.values()), -1).cpu().numpy()
    four_fields = ("bank_effect_energy", "gate_effect_energy", "interaction_energy", "bank_gate_inner", "bank_interaction_inner", "gate_interaction_inner", "total_energy", "identity_residual")
    four = []
    support_fields = ("selected_mass", "q_squared", "selected_normalized_concentration", "overlap_A_fraction", "Ad_on_native_count", "Ad_receiver_only_count", "Ad_on_native_energy", "Ad_receiver_only_energy")
    support = []
    for donor in donors:
        aa, ad, da, dd = [traces[k]["native"].double() for k in ("AA", donor + "_Ad", donor + "_dA", donor + "_dd")]
        b, g, interaction = ad - aa, da - aa, dd - da - ad + aa
        total = dd - aa
        four.append(torch.stack((b.square().sum(-1), g.square().sum(-1), interaction.square().sum(-1),
                                (b*g).sum(-1), (b*interaction).sum(-1), (g*interaction).sum(-1),
                                total.square().sum(-1), (total-b-g-interaction).square().sum(-1)), -1).cpu().numpy())
        qd, qa = traces[donor + "_dd"]["q"], traces["AA"]["q"]
        mass = qd.sum(-1)
        q2 = qd.double().square().sum(-1)
        overlap = ((qd > 0) & (qa > 0)).sum(-1).double() / 8
        # Support means actual Top-k membership; softmax weights are positive here.
        if torch.any((traces[donor + "_dd"]["weights"] <= 0)) or torch.any(traces["AA"]["weights"] <= 0):
            raise ValueError("Support mask must use explicit selected indices if gate weights underflow")
        counts = torch.zeros((len(mass), 2), device=hidden.device, dtype=torch.float64)
        energies = torch.zeros_like(counts)
        for e in range(64):
            comp = traces[donor + "_Ad"]["components"][e]
            rows = comp["row"]
            on = qd[rows, e] > 0
            energy = comp["component"].double().square().sum(-1)
            for k, keep in enumerate((on, ~on)):
                counts[:, k].index_add_(0, rows[keep], torch.ones_like(energy[keep]))
                energies[:, k].index_add_(0, rows[keep], energy[keep])
        support.append(torch.stack((mass.double(), q2, q2 / mass.double().square(), overlap,
                                    counts[:, 0], counts[:, 1], energies[:, 0], energies[:, 1]), -1).reshape(16, 512, -1).cpu().numpy())
    return {"names": np.array(names), **{key + "_metrics": value for key, value in metrics.items()},
            "metric_fields": np.array(c.METRICS), "donors": np.array(donors),
            "four_grid_layer": np.stack(four), "four_grid_fields": np.array(four_fields),
            "support": np.stack(support), "support_fields": np.array(support_fields),
            "R_moments": common_moments["R"], "S_moments": common_moments["S"],
            "R_native_moments": common_moments["R_native"], "S_native_moments": common_moments["S_native"],
            "moment_names": np.array(["C", "V", "C_minus_V"]),
            "teacher_layer_energy": traces["teacher"]["native"].double().square().sum(-1).cpu().numpy()}


@torch.no_grad()
def run(args):
    proof_path = args.work_root / "assets.json"
    proof = c.read(proof_path)
    if proof["source_sha256"] != c.code_proof():
        raise ValueError("Code changed after CPU prepare; rerun prepare before GPU work")
    if proof["selected_sha256"] != c.sha(c.WB / "results/e144/selected.json") or proof["source_maps_sha256"] != c.sha(c.WB / "results/e144/source_maps.json"):
        raise ValueError("Frozen held/source selection changed")
    result_root = c.WB / "results" / args.experiment
    ledger = result_root / "budget.json"
    lock = c.gpu_lock(args.physical_gpu)
    try:
        with c.Budget(ledger, args.experiment, args.mode) as budget:
            model, teacher, blocks = load(args, proof)
            start = time.monotonic()
            if args.mode == "preflight":
                result = preflight(args, proof, model, teacher, blocks, budget)
            else:
                floors = c.read(result_root / "floors.json")
                if floors["status"] != "passed" or floors["source_sha256"] != c.code_proof() or floors["asset_preflight_sha256"] != c.sha(proof_path):
                    raise ValueError("Matching train-side preflight must pass before held")
                selected = c.read(c.WB / "results/e144/selected.json")
                old_tokens = np.load(c.RECIPE / "held_tokens.npy", mmap_mode="r").reshape(512, 513)
                rows = selected["rows"]
                raw_root = c.ARCHIVE / ("e144_prediction_recombination" if args.experiment == "e144" else "e145_history_cross")
                raw_root.mkdir(parents=True, exist_ok=True)
                result = {"experiment": args.experiment, "status": "partial", "source_sha256": c.code_proof(),
                          "asset_preflight_sha256": c.sha(proof_path), "selected_sha256": proof["selected_sha256"],
                          "source_maps_sha256": proof["source_maps_sha256"], "host": socket.gethostname(),
                          "physical_gpu": args.physical_gpu, "batch_size": 16, "seq_len": 512, "planned_batches": 4,
                          "raw_batches": [], "source_commit": proof["source_commit"], "scope": proof["scope"]}
                manifest_path = result_root / "manifest.json"
                if manifest_path.exists():
                    previous = c.read(manifest_path)
                    for key in ("source_sha256", "asset_preflight_sha256", "selected_sha256", "source_maps_sha256"):
                        if previous[key] != result[key]:
                            raise ValueError("Existing result belongs to a different frozen run")
                    if previous["status"] == "complete":
                        raise ValueError("Already complete; do not silently repeat held work")
                c.write(manifest_path, result)
                for batch in range(4):
                    budget.check()
                    row_slice = rows[batch*16:(batch+1)*16]
                    token_array = np.stack([old_tokens[r["old_sequence_index"]] for r in row_slice]).astype(np.int64)
                    tokens = torch.from_numpy(token_array).to("cuda:0")
                    batch_start = time.monotonic()
                    function = batch_e144 if args.experiment == "e144" else batch_e145
                    values = function(args, proof, model, teacher, blocks, tokens, budget)
                    path = raw_root / f"batch{batch:02d}.npz"
                    if path.exists():
                        raise ValueError("Raw result already exists; audit partial attempt before replacing")
                    np.savez_compressed(path, **values)
                    result["raw_batches"].append({"path": str(path), "sha256": c.sha(path), "size_bytes": path.stat().st_size,
                                                  "batch": batch, "forward_seconds": time.monotonic()-batch_start})
                    c.write(manifest_path, result)
                    c.emit("held_batch_complete", experiment=args.experiment, batch=batch,
                           seconds=result["raw_batches"][-1]["forward_seconds"], peak_gb=torch.cuda.max_memory_allocated()/1e9)
                    del values, tokens
                    gc.collect()
                result["status"] = "complete"
                result["peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
                result["evaluation_seconds"] = time.monotonic() - start
                c.write(manifest_path, result)
            model.model.layers[9].mlp = teacher
            if c.tensor_hash(teacher.state_dict()) != proof["teacher_block_tensor_sha256"] or c.base.sampled_parameter_hash(model, "model.layers.9.mlp.") != proof["teacher_prefix_sample_hash"]:
                raise RuntimeError("Teacher/prefix/downstream mutated during read-only evaluation")
            for name, block in blocks.items():
                digest = c.tensor_hash({"block."+k: v for k, v in block.state_dict().items()})
                if digest != proof["sources"][name]["tensor_sha256"]:
                    raise RuntimeError(f"Source parameters mutated: {name}")
            result["read_only_source_checks"] = "passed"
            c.write(result_root / ("floors.json" if args.mode == "preflight" else "manifest.json"), result)
    finally:
        lock.close()
    return {"status": result["status"], "experiment": args.experiment, "mode": args.mode}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "preflight", "evaluate"))
    p.add_argument("--experiment", choices=("e144", "e145"), default="e144")
    p.add_argument("--work-root", type=Path, default=Path("/tmp/xiang-moe-20261026/e144145"))
    p.add_argument("--physical-gpu", type=int, default=0)
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    torch.set_num_threads(4)
    output = c.prepare(args.work_root) if args.mode == "prepare" else run(args)
    print(json.dumps({"status": output["status"], "mode": args.mode}, allow_nan=False), flush=True)
