"""E132 fixed ring bank grafts; whole-LM held readout, no training/score gates."""
from __future__ import annotations
import argparse, copy, gc, hashlib, inspect, json, os, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers import OlmoForCausalLM
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
import e123_frozen_moe as base
import e124_compare as matching
from e124_functional_capture import tensor_state_hash
import e127_predictive_fidelity as fidelity
import e130_finalize as assets

WB = assets.WB
IDS = ["seed0_anchor", *[f"seed{i}_order0" for i in range(1, 5)]]
FROZEN = "565b9dacb123aab3e1f296bcc1bad8928fa7811492b80aface1809530a0b6c03"
COMPARE_SHA = "1cd3df24aea09e1fb2db86d9e4db52fe53ca42d7564141a0987ff6ccd7313671"
RANDOM_SEEDS = (132, 133, 134)
METRICS = (*fidelity.METRICS, "top1_agreement")


class SharedMoE(nn.Module):
    """Read-only gate/expert references; exactly the installed HF operation order."""
    def __init__(self, gate, experts, top_k):
        super().__init__()
        self.gate, self.experts = gate, nn.ModuleList(experts)
        self.num_experts, self.top_k, self.norm_topk_prob = len(experts), top_k, False
        self.training = False

    def forward(self, hidden):
        return OlmoeSparseMoeBlock.forward(self, hidden)[0]


class PermutedGate(nn.Module):
    """Only the small gate matrix is copied for the simultaneous-label gauge."""
    def __init__(self, original, permutation):
        super().__init__()
        index = torch.as_tensor(permutation, device=original.weight.device, dtype=torch.long)
        self.register_buffer("weight", original.weight.detach().index_select(0, index))
        self.register_buffer("bias", original.bias.detach().index_select(0, index) if original.bias is not None else None)

    def forward(self, hidden):
        return F.linear(hidden, self.weight, self.bias)


class ZeroFFN(nn.Module):
    def forward(self, hidden): return torch.zeros_like(hidden)


def full_mapping(a, b):
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        return {"status": "unmeasurable", "target_to_source": [None] * a.shape[1], "matched_columns": 0,
                "valid_target_columns": None, "valid_source_columns": None, "reason": "Nonfinite cal profile; no invented full mapping", "numeric_std_floor": 1e-8}
    ia, ib, va, vb = matching.match_columns(a, b, 1e-8)
    permutation = [None] * a.shape[1]
    for i, j in zip(ia, ib): permutation[int(i)] = int(j)
    return {"status": "defined" if len(ia) == a.shape[1] == b.shape[1] else "unmeasurable",
            "target_to_source": permutation, "valid_target_columns": int(va.sum()), "valid_source_columns": int(vb.sum()),
            "matched_columns": len(ia), "numeric_std_floor": 1e-8}


def mappings(target, source):
    for key in ("item_id", "input_sha256", "word", "split"):
        if not np.array_equal(target[key], source[key]): raise ValueError(f"Cal anchors differ: {key}")
    cal = target["split"] == "cal"
    values = []
    for capture in (target, source):
        # Only cal U values reach the residualizer/matcher; held cannot fit a map.
        u, words = capture["U"][cal], capture["word"][cal]
        residual, _, _ = matching.residualize(u, words, np.ones(len(u), bool), np.zeros(len(u), bool))
        values.append(residual)
    u_map = full_mapping(*values)
    h = target["Htarget"][cal].astype(np.float64)
    profiles = [h @ capture["gate"].astype(np.float64).T for capture in (target, source)]
    profiles = [value - value.mean(1, keepdims=True) for value in profiles]
    router_map = full_mapping(*profiles)
    return {"U": u_map, "router": router_map, "cal_items": int(cal.sum()),
            "direction": "target slot i -> source expert mapping[i]", "held_used_for_fitting": False,
            "router_profile": "Same cal Htarget @ captured FP32 gate.T; float64 CPU products; row-center across experts then column Pearson/Hungarian",
            "random": {str(seed): np.random.default_rng(seed).permutation(target["U"].shape[1]).tolist() for seed in RANDOM_SEEDS}}


def load_asset(root, name):
    folder = root / name; metadata = assets.read(folder / "metadata.json")
    seed = IDS.index(name)
    expected = {"schema": "E132-model-only-bank-v1", "derived_evaluation_asset": True, "step": 62500,
                "seed": seed, "order_seed": 0, "frozen_sample_hash": FROZEN}
    if not metadata or any(metadata.get(key) != value for key, value in expected.items()): raise ValueError(f"Invalid derived bank metadata: {name}")
    bank_path = folder / "bank.pt"; proof = metadata["bank_file"]
    if (Path(proof["path"]).resolve() != bank_path.resolve() or bank_path.stat().st_size != proof["size_bytes"]
            or assets.sha(bank_path) != proof["sha256"]): raise ValueError("Model-only bank file SHA/path/size differs")
    provenance, summary = assets.read(metadata["staged_provenance"]), assets.read(metadata["staged_training_summary"])
    if not assets.ready(summary, None): raise ValueError("Source training is not fixed62500/512M complete")
    args = provenance["args"]
    if any(args.get(key) != value for key, value in {"seed": seed, "order_seed": 0, "layer": 9, "experts": 64,
            "expert_size": 1024, "top_k": 8, "dtype": "bfloat16", "seq_len": 512, "batch_size": 16, "eval_sequences": 512}.items()):
        raise ValueError("Source training identity/architecture differs")
    capture_path = Path(metadata["functional_capture"])
    capture = matching.load_capture(capture_path)
    with np.load(capture_path, allow_pickle=False) as raw:
        capture["Htarget"], capture["gate"] = np.asarray(raw["Htarget"]), np.asarray(raw["gate"])
    header = capture["metadata"]
    if (header["step"] != 62500 or header["seed"] != seed or header["order_seed"] != 0 or header["plan_sha256"] != assets.PLAN_SHA
            or header["backbone_sample_hash"] != FROZEN or header["script_sha256"] != assets.FROZEN["e124_functional_capture.py"]
            or metadata["source_tensor_sha256"] != header["checkpoint_moe_tensor_sha256"]
            or any(value != metadata["config_hash"] for value in (header["checkpoint_config_hash"], provenance["config_hash"], summary["config_hash"]))
            or provenance["frozen_sample_hash"] != FROZEN or summary["frozen_sample_hash_before"] != FROZEN or summary["frozen_sample_hash_after"] != FROZEN):
        raise ValueError("Derived asset, real functional capture and training fingerprints disagree")
    if capture["U"].shape != (1024, 64) or (capture["split"] == "cal").sum() != 512: raise ValueError("Wrong fixed functional sample plan")
    if capture["Htarget"].shape != (1024, 2048) or capture["gate"].shape != (64, 2048): raise ValueError("Profile input/gate dimensions differ")
    finalization = WB / "results/e128/finalization.json" if seed == 0 else WB / "results/e130/finalization" / f"{name}.json"
    source_proof = assets.read(finalization)
    if not source_proof or source_proof.get("checkpoint_sha256") != metadata["source_checkpoint_sha256"]:
        raise ValueError("Full source checkpoint SHA lacks its matching canonical archive/finalizer proof")
    payload = torch.load(bank_path, map_location="cpu", mmap=True, weights_only=False)
    if set(payload) != {"replacement_state"}: raise ValueError("Bank must contain model-only replacement_state, without optimizer/RNG")
    state = payload["replacement_state"]
    if any(value.dtype != torch.float32 for value in state.values()) or tensor_state_hash(state) != metadata["source_tensor_sha256"]:
        raise ValueError("Full FP32 bank tensor SHA differs from the real trained capture")
    if not np.array_equal(state["block.gate.weight"].numpy(), capture["gate"]): raise ValueError("Captured gate differs from trained gate")
    with torch.device("meta"): bank = base.TensorMoE(2048, 1024, 64, 8, .02)
    bank.load_state_dict(state, strict=True, assign=True); bank.eval(); bank.requires_grad_(False)
    identity = {"metadata": metadata, "metadata_sha256": assets.sha(folder / "metadata.json"), "capture_sha256": assets.sha(capture_path),
                "provenance_sha256": assets.sha(metadata["staged_provenance"]), "training_summary_sha256": assets.sha(metadata["staged_training_summary"]),
                "source_checkpoint_proof": str(finalization), "source_checkpoint_proof_sha256": assets.sha(finalization),
                "gate_precision": "Captured gate exactly equals FP32 master storage; BF16 autocast rounds forward weights separately"}
    if metadata.get("functional_capture_sha256", identity["capture_sha256"]) != identity["capture_sha256"]: raise ValueError("Functional capture file SHA differs")
    return bank, capture, provenance, summary, identity


def summarize(rows, names=METRICS, iterations=1000):
    if not rows: return None
    groups = {}
    for row in rows:
        groups.setdefault((row["source"], row["file_id"]), np.zeros(len(names) + 1))[:] += np.array([row[key] for key in names] + [row["tokens"]])
    values = np.array(list(groups.values())); draws = np.random.default_rng(127).integers(0, len(values), (iterations, len(values)))
    samples = values[draws].sum(1); intervals = np.quantile(samples[:, :-1] / samples[:, -1:], [.025, .975], axis=0)
    totals = values.sum(0)
    return {"files": len(values), "sequences": len(rows), "tokens": int(totals[-1]), "file_bootstrap_iterations": iterations,
            "ci_degenerate": len(values) < 2, **{key: {"mean": float(totals[i] / totals[-1]), "ci95": intervals[:, i].tolist()} for i, key in enumerate(names)}}


def summaries(rows, names=METRICS):
    return {"global": summarize(rows, names), "sources": {source: summarize([row for row in rows if row["source"] == source], names)
            for source in sorted({row["source"] for row in rows})}}


def contrast(method, randoms):
    if not method or any(len(rows) != len(method) for rows in randoms): raise ValueError("Incomplete paired random/method evaluation")
    result = []
    for index, row in enumerate(method):
        random = [values[index] for values in randoms]
        if any(any(value[key] != row[key] for key in ("source", "file_id", "window", "tokens")) for value in random):
            raise ValueError("Paired method/random rows differ")
        result.append({"source": row["source"], "file_id": row["file_id"], "window": row["window"], "tokens": row["tokens"],
            "nll_method_minus_mean_random": row["student_nll"] - float(np.mean([value["student_nll"] for value in random])),
            "kl_method_minus_mean_random": row["kl_teacher_to_student"] - float(np.mean([value["kl_teacher_to_student"] for value in random]))})
    return summaries(result, ("nll_method_minus_mean_random", "kl_method_minus_mean_random"))


def rows_from_logps(teacher, student, targets, metadata):
    values = fidelity.token_metrics(teacher, student, targets)
    if not torch.isfinite(values).all(): raise RuntimeError("Nonfinite whole-LM token metrics")
    sums = values.double().sum(1).cpu().numpy(); same = (teacher.argmax(-1) == student.argmax(-1)).sum(1).cpu().tolist()
    return [{**meta, "tokens": targets.shape[1], **dict(zip(fidelity.METRICS, values.tolist())), "top1_agreement": float(agreement)}
            for meta, values, agreement in zip(metadata, sums, same)]


@torch.no_grad()
def evaluate_pair(target_id, source_id, args, started):
    target, tc, tp, ts, ti = load_asset(args.bank_root, target_id)
    source, sc, sp, ss, si = load_asset(args.bank_root, source_id)
    for key in ("plan_sha256", "source_sha256", "selected_inputs_sha256", "backbone_sample_hash"):
        if tc["metadata"][key] != sc["metadata"][key]: raise ValueError("Target/source fixed capture identity differs")
    if not np.array_equal(tc["Htarget"], sc["Htarget"]): raise ValueError("Cal/held common profile inputs differ")
    if Path(tp["args"]["model"]).resolve() != Path(sp["args"]["model"]).resolve(): raise ValueError("Backbone source model differs")
    maps = mappings(tc, sc)
    data = base.TokenData(tp["args"]["data"], 512); windows = data.fixed_windows("held", 512, tp["args"]["eval_seed"])
    fidelity.guard_inputs(tp, data, windows); fidelity.guard_inputs(sp, data, windows)
    model = OlmoForCausalLM.from_pretrained(tp["args"]["model"], dtype=torch.bfloat16, local_files_only=True,
                                         attn_implementation="sdpa").to("cuda:0").eval()
    model.requires_grad_(False); model.config.use_cache = False
    original = model.model.layers[9].mlp
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != FROZEN: raise ValueError("Loaded frozen backbone differs")
    target, source = target.to("cuda:0"), source.to("cuda:0")
    def graft(permutation): return SharedMoE(target.block.gate, [source.block.experts[i] for i in permutation], 8)
    modules = {"natural_target": target, "source_coupled": source, "zero_FFN": ZeroFFN(),
               **{f"random_{seed}": graft(maps["random"][str(seed)]) for seed in RANDOM_SEEDS}}
    status = {name: {"status": "running"} for name in modules}
    for method in ("U", "router"):
        name = f"graft_{method}"
        if maps[method]["status"] == "defined": modules[name] = graft(maps[method]["target_to_source"]); status[name] = {"status": "running"}
        else: status[name] = {"status": "unmeasurable", "reason": "No complete one-to-one cal mapping; no slots filled or model dropped"}
    if maps["U"]["status"] == "defined":
        permutation = maps["U"]["target_to_source"]
        modules["source_gauge_U"] = SharedMoE(PermutedGate(source.block.gate, permutation), [source.block.experts[i] for i in permutation], 8)
        status["source_gauge_U"] = {"status": "running"}; status["gauge_direct_source"] = {"status": "running"}
    else:
        for name in ("source_gauge_U", "gauge_direct_source"): status[name] = {"status": "unmeasurable", "reason": "U mapping undefined"}
    raw = {name: [] for name in status}; identity_floor = None; scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16")
    input_hash = hashlib.sha256(); completed_batches = 0
    for batch_index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
        if time.monotonic() - started >= args.max_hours * 3600: break
        input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); labels = batch[:, 1:]
        model.model.layers[9].mlp = target
        teacher = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
        raw["natural_target"].extend(rows_from_logps(teacher, teacher, labels, metadata))
        if batch_index == 0:
            model.model.layers[9].mlp = SharedMoE(target.block.gate, list(target.block.experts), 8)
            identity = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            delta = fidelity.token_metrics(teacher, identity, labels)
            identity_floor = {"scope": "First complete batch; actual original TensorMoE versus shared-reference unbound-HF wrapper",
                "tokens": labels.numel(), "kl_max_abs": float(delta[..., 0].abs().max()), "nll_delta_max_abs": float(delta[..., 3].abs().max()),
                "log_probability_max_abs": float((teacher - identity).abs().max()), "summary": summaries(rows_from_logps(teacher, identity, labels, metadata))}
            del identity, delta
        source_lp = None
        # Source comes first so gauge is scored directly against p_source too.
        for name in ["source_coupled", *[value for value in modules if value not in ("natural_target", "source_coupled")]]:
            if status[name]["status"] != "running": continue
            try:
                model.model.layers[9].mlp = modules[name]
                student = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                raw[name].extend(rows_from_logps(teacher, student, labels, metadata))
                if name == "source_coupled": source_lp = student
                if name == "source_gauge_U":
                    if source_lp is None: raise RuntimeError("Source baseline unavailable for direct gauge KL")
                    raw["gauge_direct_source"].extend(rows_from_logps(source_lp, student, labels, metadata))
                if name != "source_coupled": del student
            except Exception as error:
                status[name] = {"status": "failed", "error": f"{type(error).__name__}: {error}", "batch": batch_index}
                if name in ("source_coupled", "source_gauge_U"): status["gauge_direct_source"] = {"status": "failed", "error": "Source/gauge evaluation failed"}
        completed_batches += 1
        target.last_router_logits = source.last_router_logits = None
        del teacher, source_lp
        base.emit("graft_batch", target=target_id, source=source_id, completed=completed_batches, total=32)
    model.model.layers[9].mlp = original
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != FROZEN: raise RuntimeError("Frozen backbone changed")
    if tensor_state_hash(target.state_dict()) != ti["metadata"]["source_tensor_sha256"] or tensor_state_hash(source.state_dict()) != si["metadata"]["source_tensor_sha256"]:
        raise RuntimeError("A supposedly read-only bank was modified")
    for name, record in status.items():
        if record["status"] == "running":
            record["status"] = "complete" if len(raw[name]) == 512 else "incomplete_budget"
            if record["status"] == "complete": record["metrics"] = summaries(raw[name])
    for name, summary in (("natural_target", ts), ("source_coupled", ss)):
        if status[name]["status"] == "complete":
            legacy = next(row["held"]["file"] for row in summary["evaluations"] if row["step"] == 62500)
            status[name]["legacy_training_reference"] = {"held_file_summary": legacy,
                "observed_nll_minus_legacy": status[name]["metrics"]["global"]["student_nll"]["mean"] - legacy["mean"],
                "scope": "Continuous coupled-model numerical/readout control; no eligibility threshold"}
    contrasts = {}
    for method in ("U", "router"):
        name = f"graft_{method}"; random_names = [f"random_{seed}" for seed in RANDOM_SEEDS]
        contrasts[method] = contrast(raw[name], [raw[value] for value in random_names]) if status[name]["status"] == "complete" and all(status[value]["status"] == "complete" for value in random_names) else None
    pair_id = f"target{IDS.index(target_id)}_from_source{IDS.index(source_id)}"
    attempt = len(list(args.raw_output.glob(f"{pair_id}_attempt*_sequences.json"))) + 1
    raw_path = args.raw_output / f"{pair_id}_attempt{attempt:02d}_sequences.json"
    assets.write(raw_path, {"conditions": raw, "status": status, "target": target_id, "source": source_id})
    result = {"status": "complete" if completed_batches == 32 and not any(value["status"] == "failed" for value in status.values()) else "incomplete_or_failed",
        "target": target_id, "source": source_id, "mapping": maps, "conditions": status, "identity_numeric_floor": identity_floor,
        "method_minus_mean_three_random": contrasts, "source_assets": {"target": ti, "source": si}, "held_window_hash": base.digest_json(windows),
        "input_sha256": input_hash.hexdigest(), "completed_batches": completed_batches, "raw_sequences": str(raw_path), "raw_sha256": assets.sha(raw_path),
        "missing_sources": sorted(set(data.sources_available) - {row["source"] for row in raw["natural_target"]}),
        "gauge_note": "gauge_direct_source uses KL(p_source||p_source_gauge) and paired gauge NLL minus source, not subtraction of KL-to-target values"}
    del model, target, source, modules; gc.collect(); torch.cuda.empty_cache()
    return result


def global_descriptive(pairs):
    names = sorted({name for pair in pairs.values() for name in pair.get("conditions", {})})
    result = {}
    for name in names:
        metrics = {}
        for metric in METRICS:
            values = {edge: pair.get("conditions", {}).get(name, {}).get("metrics", {}).get("global", {}).get(metric, {}).get("mean") for edge, pair in pairs.items()}
            finite = [value for value in values.values() if value is not None]
            metrics[metric] = {"descriptive_mean": float(np.mean(finite)) if finite else None, "edge_values": values,
                               "observed_edges": len(finite), "expected_edges": 5}
        result[name] = metrics
    return {"conditions": result, "scope": "Descriptive averages of the fixed five-edge ring; no across-edge CI or seed inference. Undefined/missing edge values remain null."}


def run(args):
    frozen = {**assets.FROZEN, "e124_compare.py": COMPARE_SHA, "e130_finalize.py": "2b1bed11f13fc0cd2dbb658383b7d9c973da41760e4ec1236e7f18a10a76039f"}
    if {name: assets.sha(WB / "scripts" / name) for name in frozen} != frozen: raise ValueError("Frozen source SHA differs")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", ""); physical = args.physical_gpu
    if physical is None:
        if not visible.isdigit(): raise ValueError("Specify one physical GPU via CUDA_VISIBLE_DEVICES or --physical-gpu")
        physical = int(visible)
    if visible and visible != str(physical): raise ValueError("Visible GPU differs from requested physical GPU")
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA was initialized before physical GPU occupancy check")
    gpu = assets.gpu_status(physical)
    result = {"experiment": "E132", "status": "partial", "script_sha256": assets.sha(__file__), "frozen_sources": frozen,
              "gpu_preflight": gpu, "precision": "BF16 backbone/autocast, FP32 replacement weights; logits then FP32 log_softmax; no FP32 head substitution",
              "HF_forward_sha256": hashlib.sha256(inspect.getsource(OlmoeSparseMoeBlock.forward).encode()).hexdigest(),
              "fixed_ring": [{"target": IDS[i], "source": IDS[(i + 1) % 5]} for i in range(5)], "pairs": {},
              "sampling_note": "Five directed ring edges share five models; no edge-based confidence interval or independent-seed inference. File CIs describe held evaluation only."}
    if not assets.gpu_free(gpu): result["status"] = "deferred_gpu_busy_or_unavailable"; assets.write(args.summary, result); return result
    previous = assets.read(args.summary)
    prior_wall = previous.get("elapsed_wall_seconds", 0.) if previous and previous.get("script_sha256") == result["script_sha256"] else 0.
    result["previous_wall_seconds_charged"] = prior_wall
    os.environ["CUDA_VISIBLE_DEVICES"] = str(physical); started = time.monotonic() - prior_wall
    for i, edge in enumerate(result["fixed_ring"]):
        name = f"target{i}_from_source{(i + 1) % 5}"
        if i >= args.max_pairs or time.monotonic() - started >= args.max_hours * 3600:
            result["pairs"][name] = {"status": "not_run_fixed_pair_limit_or_budget", **edge}; continue
        try: result["pairs"][name] = evaluate_pair(edge["target"], edge["source"], args, started)
        except Exception as error:
            result["pairs"][name] = {"status": "failed", **edge, "error": f"{type(error).__name__}: {error}"}
            gc.collect()
            if torch.cuda.is_initialized(): torch.cuda.empty_cache()
        assets.write(args.summary, result)
    statuses = [value["status"] for value in result["pairs"].values()]
    result["status"] = "complete" if all(value == "complete" for value in statuses) else "partial"
    result["elapsed_wall_seconds"] = time.monotonic() - started
    result["global_descriptive"] = global_descriptive(result["pairs"])
    assets.write(args.summary, result); return result


def self_test():
    torch.set_num_threads(1); torch.manual_seed(132)
    target = base.TensorMoE(8, 8, 4, 2, .02).eval(); source = copy.deepcopy(target)
    permutation = np.array([2, 0, 3, 1]); inverse = np.argsort(permutation)
    original = copy.deepcopy(target.state_dict()); permuted = {}
    for key, value in original.items():
        if key == "block.gate.weight": permuted[key] = value[permutation].clone()
        else:
            parts = key.split("."); old_index = int(permutation[int(parts[2])]); parts[2] = str(old_index)
            permuted[key] = original[".".join(parts)].clone()
    source.load_state_dict(permuted)
    before = (tensor_state_hash(target.state_dict()), tensor_state_hash(source.state_dict()))
    experts_before = tuple(id(value) for value in source.block.experts)
    hidden = torch.randn(2, 5, 8)
    identity = SharedMoE(target.block.gate, list(target.block.experts), 2)
    assert torch.equal(target(hidden), identity(hidden))
    graft = SharedMoE(target.block.gate, [source.block.experts[i] for i in inverse], 2)
    assert torch.equal(target(hidden), graft(hidden))
    gauge = SharedMoE(PermutedGate(source.block.gate, inverse), [source.block.experts[i] for i in inverse], 2)
    assert torch.allclose(source(hidden), gauge(hidden), atol=1e-9, rtol=1e-5)
    with torch.device("meta"): rebuilt = base.TensorMoE(8, 8, 4, 2, .02)
    assert all(value.is_meta for value in rebuilt.parameters())
    rebuilt.load_state_dict(original, assign=True)
    assert tensor_state_hash(rebuilt.state_dict()) == before[0]
    rng = np.random.default_rng(132); n = 128
    t = {"U": rng.normal(size=(n, 4)), "word": np.array([f"w{i%8}" for i in range(n)]),
         "split": np.array(["cal"] * 64 + ["held"] * 64), "item_id": np.arange(n),
         "input_sha256": np.array([str(i) for i in range(n)]), "Htarget": rng.normal(size=(n, 8)),
         "gate": target.block.gate.weight.detach().numpy()}
    # Frozen capture stores the FP32 gate, even though forward AMP uses BF16.
    assert np.array_equal(t["gate"], target.block.gate.weight.detach().numpy())
    assert not np.array_equal(t["gate"], target.block.gate.weight.detach().to(torch.bfloat16).float().numpy())
    s = {**t, "U": t["U"][:, permutation], "gate": t["gate"][permutation]}
    maps = mappings(t, s)
    assert maps["U"]["target_to_source"] == maps["router"]["target_to_source"] == inverse.tolist()
    altered = {**s, "U": s["U"].copy(), "Htarget": s["Htarget"].copy()}
    altered["U"][64:] = rng.normal(size=(64, 4)) * 100
    altered["Htarget"][64:] = rng.normal(size=(64, 8)) * 100
    changed = mappings(t, altered)
    assert changed["U"] == maps["U"] and changed["router"] == maps["router"]
    undefined = mappings({**t, "U": np.zeros_like(t["U"])}, s)
    assert undefined["U"]["status"] == "unmeasurable" and undefined["U"]["target_to_source"] == [None] * 4
    assert before == (tensor_state_hash(target.state_dict()), tensor_state_hash(source.state_dict())) and experts_before == tuple(id(value) for value in source.block.experts)
    rows = [{"source": "s", "file_id": str(i), "window": 0, "tokens": tokens, "student_nll": 2 * tokens, "kl_teacher_to_student": tokens} for i, tokens in enumerate((2, 4))]
    random = [{**row, "student_nll": row["student_nll"] + row["tokens"], "kl_teacher_to_student": row["kl_teacher_to_student"] + row["tokens"]} for row in rows]
    paired = contrast(rows, [random, random, random])["global"]
    assert paired["nll_method_minus_mean_random"]["ci95"] == [-1., -1.] and paired["kl_method_minus_mean_random"]["mean"] == -1.
    result = {"passed": True, "device": "cpu", "script_sha256": assets.sha(__file__), "unbound_HF_identity_exact": True,
              "source_original_weights_and_module_order_unchanged": True, "mapping_target_to_source_direction_known_answer": True,
              "held_never_fits_U_or_router_map": True, "undefined_mapping_not_filled": True, "meta_assign_without_random_big_bank": True,
              "FP32_gate_storage_separate_from_BF16_forward": True,
              "paired_file_method_minus_mean_random_math": True, "no_full_LM_or_GPU": True}
    assets.write(WB / "results/e132/self_test.json", result); print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bank-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e132_banks"))
    parser.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e132_grafting"))
    parser.add_argument("--summary", type=Path, default=WB / "results/e132/bank_grafting.json")
    parser.add_argument("--max-pairs", type=int, default=5); parser.add_argument("--max-hours", type=float, default=1.)
    parser.add_argument("--physical-gpu", type=int)
    args = parser.parse_args()
    if args.self_test: self_test()
    else:
        if not 1 <= args.max_pairs <= 5 or not 0 < args.max_hours <= 1: parser.error("Fixed ring has1..5 pairs and <=1h total wall budget")
        if args.raw_output.resolve().is_relative_to(WB): parser.error("Raw per-sequence evaluation assets must remain outside git")
        print(json.dumps(run(args), indent=2), flush=True)
