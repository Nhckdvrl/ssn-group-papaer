"""E137 native-support component reconstruction; two fixed populations, no fit."""
from __future__ import annotations
import argparse, fcntl, hashlib, json, socket, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers import OlmoeForCausalLM
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
import e136_readout as source

c, assets, base, WB = source.c, source.assets, source.base, source.WB
CONDITIONS = ("copy", "oracle_initial", "oracle_final")
FIELDS = ("on_count", "off_count", "on_teacher_energy", "off_teacher_energy", "on_content_SSE", "off_content_SSE",
          "component_teacher_energy", "component_delta_SSE", "teacher_query_on_shape_floor_SSE", "condition_query_on_shape_floor_SSE",
          "teacher_product_floor_SSE", "condition_product_floor_SSE")
AGG = ("positions", "teacher_native_energy", "FP32_sum_delta_SSE", "native_aggregate_delta_SSE", "native_minus_FP32_sum_delta_SSE",
       "FP32_subtract_reduce_path_difference_SSE", "teacher_sum_to_native_floor_SSE", "condition_sum_to_native_floor_SSE",
       "FP64_sum_delta_SSE", "FP32_minus_FP64_sum_delta_SSE")


class Budget(c.Budget):
    def __init__(self, path): super().__init__(path, "components", limit=900.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E137", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state["experiment"] != "E137" or state["host"] != socket.gethostname(): raise ValueError("Separate E137 node-local ledger required")
            result = operation(state); assets.write(self.path, state); return result
    def check(self):
        used = self.update(lambda state: state["completed_seconds"] + sum(time.monotonic() - value["started"] for value in state["active"].values()))
        if used >= 900: raise TimeoutError("E137900GPU-second budget exhausted")
        return used


def norm2(value): return value.double().square().sum(-1)
def grouped(value, sequence, batch): return torch.bincount(sequence, weights=value.double(), minlength=batch)


@torch.no_grad()
def native_trace(block, hidden, query):
    """Observe actual expert calls; reproduce only the native elementwise product."""
    flat = hidden.reshape(-1, hidden.shape[-1]); inverse = torch.full((len(flat),), -1, device=hidden.device, dtype=torch.long)
    inverse[query] = torch.arange(len(query), device=hidden.device); ctx, experts, handles = {}, {}, []
    total = torch.zeros((len(query), hidden.shape[-1]), dtype=torch.float32, device=hidden.device)
    def gate_hook(module, inputs, logits):
        weights, selected = F.softmax(logits, dim=1, dtype=torch.float32).topk(block.top_k, dim=-1)
        if block.norm_topk_prob: weights = weights / weights.sum(-1, keepdim=True)
        ctx.update({"logits": logits, "weights": weights.to(hidden.dtype), "selected": selected,
                    "mask": F.one_hot(selected, num_classes=block.num_experts).permute(2, 1, 0)})
    handles.append(block.gate.register_forward_hook(gate_hook))
    for e, expert in enumerate(block.experts):
        def expert_hook(module, inputs, output, e=e):
            slot, row = torch.where(ctx["mask"][e])
            expected = flat[None, row].reshape(-1, flat.shape[-1])
            if inputs[0].dtype != expected.dtype or not torch.equal(inputs[0], expected): raise RuntimeError("Native selected subbatch/row order mismatch")
            keep = inverse[row] >= 0; qi = inverse[row[keep]]; f = output[keep].detach().clone()
            weight = ctx["weights"][row[keep], slot[keep]]
            component = (f * weight[:, None]).to(hidden.dtype)
            product_floor = component.float() - f.float() * weight.float()[:, None]
            total.index_add_(0, qi, component.float())
            experts[e] = {"query": qi, "f": f, "component": component, "product_floor": product_floor}
        handles.append(expert.register_forward_hook(expert_hook))
    try: result = block(hidden)
    finally:
        for handle in handles: handle.remove()
    if not isinstance(result, tuple) or not torch.equal(result[1], ctx["logits"]): raise ValueError("Native tuple/router contract differs")
    return {"native": result[0].reshape(-1, hidden.shape[-1])[query].detach().clone(), "sum": total, "experts": experts,
        "selected": ctx["selected"][query], "weights": ctx["weights"][query], "verified_expert_calls": len(experts)}


@torch.no_grad()
def measure_batch(blocks, hidden, query, sequence, budget):
    batch, dimension = int(sequence.max()) + 1, hidden.shape[-1]
    traces = {}
    for name, block in blocks.items():
        budget.check()
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16, enabled=hidden.dtype == torch.bfloat16): traces[name] = native_trace(block, hidden, query)
    teacher = traces["teacher"]; qh = hidden.reshape(-1, dimension)[query]
    stats = {name: torch.zeros((batch, len(blocks["teacher"].experts), len(FIELDS)), dtype=torch.float64, device=hidden.device) for name in CONDITIONS}
    sums = {name: torch.zeros_like(teacher["sum"]) for name in CONDITIONS}; support = {}
    sums64 = {name: torch.zeros_like(teacher["sum"], dtype=torch.float64) for name in CONDITIONS}
    for name in CONDITIONS:
        trace = traces[name]
        support[name] = {"slot_mismatch_rows": int((trace["selected"] != teacher["selected"]).any(-1).sum()),
                         "weight_max_abs_difference": float((trace["weights"] - teacher["weights"]).float().abs().max())}
        if support[name]["slot_mismatch_rows"] or support[name]["weight_max_abs_difference"] != 0:
            raise RuntimeError(f"Native support structural mismatch; no full-query substitution: {support}")
    for e in range(len(blocks["teacher"].experts)):
        budget.check(); ref = teacher["experts"][e]; qi = ref["query"]; on_seq = sequence[qi]
        off = torch.ones(len(query), device=hidden.device, dtype=torch.bool); off[qi] = False
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16, enabled=hidden.dtype == torch.bfloat16): tq = blocks["teacher"].experts[e](qh)
        on_count, off_count = torch.bincount(on_seq, minlength=batch), torch.bincount(sequence[off], minlength=batch)
        for name in CONDITIONS:
            current = traces[name]["experts"][e]
            if not torch.equal(qi, current["query"]): raise RuntimeError("Same support but different native expert row order")
            with torch.autocast(hidden.device.type, dtype=torch.bfloat16, enabled=hidden.dtype == torch.bfloat16): cq = blocks[name].experts[e](qh)
            delta_component = current["component"].float() - ref["component"].float(); sums[name].index_add_(0, qi, delta_component)
            sums64[name].index_add_(0, qi, delta_component.double())
            values = (on_count, off_count, grouped(norm2(ref["f"]), on_seq, batch), grouped(norm2(tq[off]), sequence[off], batch),
                grouped(norm2(current["f"].float() - ref["f"].float()), on_seq, batch), grouped(norm2(cq[off].float() - tq[off].float()), sequence[off], batch),
                grouped(norm2(ref["component"]), on_seq, batch), grouped(norm2(delta_component), on_seq, batch),
                grouped(norm2(tq[qi].float() - ref["f"].float()), on_seq, batch), grouped(norm2(cq[qi].float() - current["f"].float()), on_seq, batch),
                grouped(norm2(ref["product_floor"]), on_seq, batch), grouped(norm2(current["product_floor"]), on_seq, batch))
            for column, value in enumerate(values): stats[name][:, e, column] = value
    aggregate = {}
    for name in CONDITIONS:
        trace = traces[name]; native_delta = trace["native"].float() - teacher["native"].float()
        separate = trace["sum"] - teacher["sum"]
        values = (torch.bincount(sequence, minlength=batch), grouped(norm2(teacher["native"]), sequence, batch),
            grouped(norm2(sums[name]), sequence, batch), grouped(norm2(native_delta), sequence, batch),
            grouped(norm2(native_delta - sums[name]), sequence, batch), grouped(norm2(sums[name] - separate), sequence, batch),
            grouped(norm2(teacher["native"].float() - teacher["sum"]), sequence, batch), grouped(norm2(trace["native"].float() - trace["sum"]), sequence, batch),
            grouped(norm2(sums64[name]), sequence, batch), grouped(norm2(sums[name].double() - sums64[name]), sequence, batch))
        aggregate[name] = torch.stack([value.double() for value in values], -1).cpu().numpy()
        stats[name] = stats[name].cpu().numpy()
    return stats, aggregate, support


def ratios(expert, aggregate, dimension):
    e = {key: float(expert[..., i].sum()) for i, key in enumerate(FIELDS)}; a = {key: float(aggregate[..., i].sum()) for i, key in enumerate(AGG)}
    divide = lambda x, y: x / y if y > 0 else None
    return {"on_content_MSE": divide(e["on_content_SSE"], e["on_count"] * dimension), "off_content_MSE": divide(e["off_content_SSE"], e["off_count"] * dimension),
        "on_relative_teacher_energy": divide(e["on_content_SSE"], e["on_teacher_energy"]), "off_relative_teacher_energy": divide(e["off_content_SSE"], e["off_teacher_energy"]),
        "component_delta_SSE_per_position": divide(e["component_delta_SSE"], a["positions"]), "component_relative_teacher_energy": divide(e["component_delta_SSE"], e["component_teacher_energy"]),
        "FP32_sum_delta_squared_norm_per_position": divide(a["FP32_sum_delta_SSE"], a["positions"]),
        "cross_term_per_position": divide(a["FP32_sum_delta_SSE"] - e["component_delta_SSE"], a["positions"]),
        "FP64_reference_cross_term_per_position": divide(a["FP64_sum_delta_SSE"] - e["component_delta_SSE"], a["positions"]),
        **{key + "_per_position": divide(a[key], a["positions"]) for key in AGG[3:]},
        "native_aggregate_relative_teacher_energy": divide(a["native_aggregate_delta_SSE"], a["teacher_native_energy"]),
        "teacher_query_on_shape_floor_MSE": divide(e["teacher_query_on_shape_floor_SSE"], e["on_count"] * dimension),
        "condition_query_on_shape_floor_MSE": divide(e["condition_query_on_shape_floor_SSE"], e["on_count"] * dimension),
        "teacher_product_floor_SSE_per_position": divide(e["teacher_product_floor_SSE"], a["positions"]),
        "condition_product_floor_SSE_per_position": divide(e["condition_product_floor_SSE"], a["positions"])}


def summarize(expert, aggregate, metadata, cluster, dimension):
    key = lambda row: (row["source"], row["file_id"]) if cluster == "file_id" else row[cluster]
    point = ratios(expert, aggregate, dimension); labels = list(dict.fromkeys(key(row) for row in metadata))
    groups = [np.array([i for i, row in enumerate(metadata) if key(row) == label]) for label in labels]
    eg, ag = np.stack([expert[index].sum(0) for index in groups]), np.stack([aggregate[index].sum(0) for index in groups])
    draws = np.random.default_rng(137).integers(0, len(groups), (1000, len(groups)))
    bootstrap = [ratios(eg[index].sum(0), ag[index].sum(0), dimension) for index in draws]
    result = {key: {"point": value, "ci95": np.quantile([row[key] for row in bootstrap], [.025, .975]).tolist()
              if value is not None and all(row[key] is not None for row in bootstrap) else None,
              "defined_draws": sum(row[key] is not None for row in bootstrap)} for key, value in point.items()}
    by_expert = []
    totals = expert.sum(0)
    for index, values in enumerate(totals):
        counts = {key: float(values[i]) for i, key in enumerate(FIELDS)}
        row = {"expert": index, **counts}
        for kind in ("on", "off"):
            row[kind + "_MSE"] = counts[kind + "_content_SSE"] / (counts[kind + "_count"] * dimension) if counts[kind + "_count"] > 0 else None
            row[kind + "_relative_teacher_energy"] = counts[kind + "_content_SSE"] / counts[kind + "_teacher_energy"] if counts[kind + "_teacher_energy"] > 0 else None
        by_expert.append(row)
    return {"global": result, "per_expert": by_expert, "clusters": len(groups), "cluster": cluster, "bootstrap_seed": 137,
        "scope": "Fixed-population pooled SSE/count or own teacher-energy ratios; no expert/cluster/draw filtering, no seed CI; rounding/shape floors separate from cross-term"}


class PrefixCaptured(Exception): pass


def preflight(args):
    frozen = {"e136_readout.py": "276d7042fa8e82ead3b8a32cc65514ee7a4e362a6b7bc2ac300e0612ae7a4421",
              "e136_capture.py": "bee7d9144e8e620e855f40f8c8890f0746d4c5aa27f6e5944c45a675adc73a1e"}
    for name, expected in frozen.items():
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError("Frozen source differs")
    manifest, states, proofs, items, metadata = source.preflight(args)
    states["copy"] = {key: value.float() for key, value in states["teacher"].items()}
    proofs["teacher"] = {"condition": "teacher", "tensor_sha256": manifest["teacher_block_tensor_sha256"],
                         "teacher_file_sha256": manifest["files"]["teacher_block.pt"]["sha256"], "storage": "bfloat16"}
    proofs["copy"] = {"condition": "copy", "tensor_sha256": c.tensor_state_hash(states["copy"]),
                      "source_teacher_tensor_sha256": manifest["teacher_block_tensor_sha256"], "storage": "float32 exact BF16 teacher values"}
    teacher_path = args.e135_raw / "teacher_functional.npz"
    with np.load(teacher_path, allow_pickle=False) as raw:
        held = raw["split"] == "held"; archived_h = np.asarray(raw["Htarget"])[held]
        if not np.array_equal(raw["item_id"][held], np.array([row["item_id"] for row in metadata if row["split"] == "held"])): raise ValueError("POS population differs")
    return manifest, states, proofs, items, metadata, archived_h


@torch.no_grad()
def run(args):
    manifest, states, proofs, items, metadata, archived_h = preflight(args); gpu = c.select_gpu(args.physical_gpu)
    args.raw_output.mkdir(parents=True, exist_ok=True); result = {"experiment": "E137", "status": "partial", "script_sha256": assets.sha(__file__),
        "gpu_preflight": gpu, "condition_proofs": proofs, "populations": {}, "scope": __doc__, "errors": {},
        "precision": "Actual BF16 selected expert outputs/weight-cast products; FP32 delta and sum main readout; parallel FP64 accumulation of the same FP32 deltas. Native aggregate/product/shape floors and F32-vs-F64 sum residual separate from reference cross-term."}
    with Budget(args.budget_file) as budget:
        model = OlmoeForCausalLM.from_pretrained(manifest["model"], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        teacher = model.model.layers[9].mlp; teacher_hash = c.tensor_state_hash(teacher.state_dict())
        if teacher_hash != manifest["teacher_block_tensor_sha256"]: raise ValueError("Native teacher differs")
        prefix_hash = base.sampled_parameter_hash(model, "model.layers.9.mlp.")
        if prefix_hash != manifest["teacher_prefix_hash"]: raise ValueError("Native prefix/source differs")
        result["teacher_prefix_hash"] = prefix_hash; result["cache_manifest_sha256"] = assets.sha(args.cache_root / "manifest.json")
        blocks = {name: c.bank_from_state(state, "cuda:0").block.eval().requires_grad_(False) for name, state in states.items()}; states.clear()
        hashes = {name: c.tensor_state_hash(block.state_dict()) for name, block in blocks.items()}
        data = base.TokenData(manifest["data"], 512); held_windows = data.fixed_windows("held", 512, 91023)
        if base.digest_json(held_windows) != manifest["held_window_hash"]: raise ValueError("Dolma held windows differ")
        held_pairs = [(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]
        for population in ("POS_held_targets", "Dolma_held_positions"):
            expert_chunks, aggregate_chunks, meta_rows, support_rows = {name: [] for name in CONDITIONS}, {name: [] for name in CONDITIONS}, [], []
            try:
                if population == "POS_held_targets":
                    pos_items, pos_meta = map(list, zip(*held_pairs)); iterator = source.operators.protocol.batches(pos_items, 16, "cuda:0", model.config.pad_token_id or 1)
                else:
                    ha = np.load(args.cache_root / "held_H.npy", mmap_mode="r"); iterator = enumerate(data.iter_fixed("held", held_windows, 16))
                for entry in iterator:
                    budget.check()
                    if population == "POS_held_targets":
                        start, ids, mask, last, targets = entry; captured = {}
                        def collect(module, inputs): captured["H"] = inputs[0].detach().clone(); raise PrefixCaptured()
                        handle = teacher.register_forward_pre_hook(collect)
                        try:
                            try:
                                with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=ids, attention_mask=mask, use_cache=False)
                            except PrefixCaptured: pass
                        finally: handle.remove()
                        hidden = captured["H"]; query = torch.arange(len(ids), device="cuda:0") * ids.shape[1] + last
                        if not np.array_equal(hidden.reshape(-1, 2048)[query].float().cpu().numpy(), archived_h[start:start + len(ids)]): raise ValueError("Replayed POS target H differs from archived Htarget")
                        sequence = torch.arange(len(ids), device="cuda:0"); meta = pos_meta[start:start + len(ids)]
                    else:
                        index, (tokens, meta) = entry; hidden = c.from_bits(ha[index], "cuda:0")
                        query = torch.arange(16 * 512, device="cuda:0"); sequence = torch.arange(16, device="cuda:0").repeat_interleave(512)
                    e, a, support = measure_batch(blocks, hidden, query, sequence, budget)
                    for name in CONDITIONS: expert_chunks[name].append(e[name]); aggregate_chunks[name].append(a[name])
                    meta_rows.extend(meta); support_rows.append(support)
                    base.emit("component_batch", population=population, sequences=len(meta_rows), total=512)
            except Exception as error: result["errors"][population] = f"{type(error).__name__}: {error}"
            raw = args.raw_output / f"{population}_sufficient_statistics.npz"
            payload = {f"{name}_expert": np.concatenate(expert_chunks[name]) for name in CONDITIONS if expert_chunks[name]}
            payload.update({f"{name}_aggregate": np.concatenate(aggregate_chunks[name]) for name in CONDITIONS if aggregate_chunks[name]})
            np.savez(raw, **payload); meta_path = raw.with_suffix(".json"); assets.write(meta_path, {"rows": meta_rows, "expert_fields": FIELDS, "aggregate_fields": AGG, "support": support_rows})
            output = {"status": "complete" if len(meta_rows) == 512 else "partial", "sequences": len(meta_rows), "positions": len(meta_rows) if population == "POS_held_targets" else len(meta_rows) * 512,
                      "raw": str(raw), "raw_sha256": assets.sha(raw), "metadata": str(meta_path), "metadata_sha256": assets.sha(meta_path), "conditions": {}}
            if len(meta_rows) == 512:
                for name in CONDITIONS: output["conditions"][name] = summarize(payload[f"{name}_expert"], payload[f"{name}_aggregate"], meta_rows, "word" if population == "POS_held_targets" else "file_id", 2048)
            result["populations"][population] = output; assets.write(args.summary, result)
        if (c.tensor_state_hash(teacher.state_dict()) != teacher_hash or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != prefix_hash
                or any(c.tensor_state_hash(block.state_dict()) != hashes[name] for name, block in blocks.items())): raise RuntimeError("Original parameter mutation")
        result["status"] = "complete" if not result["errors"] else "partial"; assets.write(args.summary, result)
    return result


def self_test():
    class Gate(nn.Module):
        def forward(self, hidden): return torch.zeros((len(hidden), 2), dtype=hidden.dtype)
    class Constant(nn.Module):
        def __init__(self, value): super().__init__(); self.value = value
        def forward(self, hidden): return torch.full_like(hidden, self.value)
    class Block(nn.Module):
        def __init__(self, values):
            super().__init__(); self.gate = Gate(); self.experts = nn.ModuleList([Constant(value) for value in values]); self.num_experts = self.top_k = 2; self.norm_topk_prob = False
        def forward(self, hidden): return OlmoeSparseMoeBlock.forward(self, hidden)
    class NoBudget:
        def check(self): pass
    hidden = torch.randn(2, 3, 2).bfloat16(); query = torch.tensor([1, 5]); sequence = torch.tensor([0, 1])
    blocks = {"teacher": Block([1., 1.]), "copy": Block([1., 1.]), "oracle_initial": Block([2., 0.]), "oracle_final": Block([2., 0.])}
    e, a, support = measure_batch(blocks, hidden, query, sequence, NoBudget())
    copy = ratios(e["copy"], a["copy"], 2); cancellation = ratios(e["oracle_final"], a["oracle_final"], 2)
    assert copy["on_content_MSE"] == copy["component_delta_SSE_per_position"] == copy["native_aggregate_relative_teacher_energy"] == 0
    assert cancellation["component_delta_SSE_per_position"] > 0 and cancellation["FP32_sum_delta_squared_norm_per_position"] == 0
    assert cancellation["cross_term_per_position"] < 0 and cancellation["native_aggregate_delta_SSE_per_position"] == 0
    assert cancellation["FP64_reference_cross_term_per_position"] < 0 and cancellation["FP32_minus_FP64_sum_delta_SSE_per_position"] == 0
    assert copy["off_content_MSE"] is None and copy["off_relative_teacher_energy"] is None
    assert all(value["slot_mismatch_rows"] == 0 for value in support.values())
    fp32, fp64 = torch.tensor(0., dtype=torch.float32), torch.tensor(0., dtype=torch.float64)
    for value in torch.tensor([1e8, 1., -1e8], dtype=torch.float32): fp32 += value; fp64 += value.double()
    assert float(fp32) == 0 and float(fp64) == 1 and float((fp32.double() - fp64).square()) == 1
    return {"passed": True, "CPU_only": True, "copy_zero": True, "opposite_equal_weight_component_errors_cancel": True,
            "selected_subbatch_row_order_checked": True, "BF16_product_then_FP32_sum": True, "parallel_FP64_sum_reference_roundoff_oracle": True,
            "script_sha256": assets.sha(__file__)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="preflight")
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache")); p.add_argument("--oracle-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_oracle"))
    p.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt")); p.add_argument("--phase", choices=("all",), default="all")
    p.add_argument("--e135-raw", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_readout")); p.add_argument("--plan", type=Path, default=WB / "results/e124/plan.json")
    p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e137_budget.json")); p.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e137_components"))
    p.add_argument("--summary", type=Path, default=WB / "results/e137/components.json"); p.add_argument("--physical-gpu", type=int, default=0); args = p.parse_args()
    if args.mode == "self-test": result = self_test(); assets.write(WB / "results/e137/self_test.json", result)
    elif args.mode == "preflight":
        manifest, states, proofs, items, metadata, h = preflight(args); result = {"status": "CPU_preflight_only", "proofs": proofs, "POS_held_H_shape": list(h.shape), "conditions": ["teacher", *CONDITIONS], "script_sha256": assets.sha(__file__)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
