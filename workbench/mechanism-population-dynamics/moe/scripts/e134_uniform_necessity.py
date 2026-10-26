"""E134 native versus expert-uniform component necessity; no training/search.

The uniform component remains input dependent and retains native gate mass.
Its 64-expert cost is not an efficiency claim; r is not the scalar U/A profile.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers import OlmoeForCausalLM
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock
import e132_bank_grafting as old

assets, base, WB = old.assets, old.base, old.WB
E132_SHA = "ed269682c2ad7e62f8fc5bac407e1834e8de304125e6c7d0794c414d6441e8e0"
MODES = ("native", "c", "r", "zero", "recompose", "gamma_c")
SETTINGS = [*old.IDS, "public_olmoe_main"]


def applied_mass(logits, hidden_dtype, top_k, norm_topk):
    weights = F.softmax(logits.reshape(-1, logits.shape[-1]), dim=-1, dtype=torch.float32).topk(top_k, dim=-1).values
    if norm_topk: weights = weights / weights.sum(-1, keepdim=True)
    return weights.to(hidden_dtype).float().sum(-1, keepdim=True)


class UniformDecomposition(nn.Module):
    def __init__(self, original):
        super().__init__(); self.original = original; self.mode = "native"; self.gamma = None
        self.cache = None; self.batch_key = None; self.computations = 0; self.last_router_logits = None; self.training = False

    @property
    def block(self): return self.original.block if hasattr(self.original, "block") else self.original

    def begin_batch(self, key): self.cache = None; self.batch_key = key; self.last_router_logits = None

    def clear(self): self.cache = None; self.batch_key = None; self.last_router_logits = None

    def forward(self, hidden):
        if self.batch_key is None: raise RuntimeError("Call begin_batch before the native/cache forward")
        if self.cache is None:
            result = self.original(hidden); is_tuple = isinstance(result, tuple)
            native, tail = (result[0], result[1:]) if is_tuple else (result, ())
            logits = tail[0] if is_tuple else self.original.last_router_logits
            if logits is None: raise RuntimeError("Original router logits unavailable")
            mass = applied_mass(logits, hidden.dtype, self.block.top_k, self.block.norm_topk_prob).reshape(*hidden.shape[:-1], 1)
            flat = hidden.reshape(-1, hidden.shape[-1]); mean = torch.zeros_like(flat, dtype=torch.float32); f0 = None
            for index, expert in enumerate(self.block.experts):
                value = expert(flat).float()
                if index == 0: f0 = value.detach().clone().reshape_as(hidden)
                mean.add_(value)
            mean = (mean / self.block.num_experts).reshape_as(hidden)
            c = mass * mean; y = native.detach().clone()
            self.cache = {"hidden": hidden.detach().clone(), "native": y, "mean": mean, "mass": mass, "c": c,
                          "r": y.float() - c, "tail": tail, "is_tuple": is_tuple, "logits": logits, "expert0": f0}
            self.computations += 1
        cache = self.cache
        if hidden.shape != cache["hidden"].shape or hidden.dtype != cache["hidden"].dtype or not torch.equal(hidden, cache["hidden"]):
            raise RuntimeError("Cached batch/prefix input differs under another mode")
        if self.mode == "native": output = cache["native"]
        elif self.mode == "c": output = cache["c"]
        elif self.mode == "r": output = cache["r"]
        elif self.mode == "zero": output = torch.zeros_like(cache["native"])
        elif self.mode == "recompose": output = cache["c"] + cache["r"]
        elif self.mode == "gamma_c":
            if self.gamma is None: raise ValueError("Global cal gamma is unmeasurable")
            output = self.gamma * cache["c"]
        else: raise ValueError(self.mode)
        output = output.to(cache["native"].dtype).clone(); self.last_router_logits = cache["logits"]
        return (output, *cache["tail"]) if cache["is_tuple"] else output


class IdenticalExpertControl(nn.Module):
    """First-batch all64 references=f0, preserving its own actual HF gate mass."""
    def __init__(self, decomposition):
        super().__init__(); block = decomposition.block
        self.gate, self.experts = block.gate, nn.ModuleList([block.experts[0]] * block.num_experts)
        self.num_experts, self.top_k, self.norm_topk_prob = block.num_experts, block.top_k, block.norm_topk_prob
        self.f0 = decomposition.cache["expert0"]; self.expected_h = decomposition.cache["hidden"]
        self.tuple_contract = decomposition.cache["is_tuple"]; self.mode = "native"; self.cached = None; self.last_router_logits = None

    def forward(self, hidden):
        if not torch.equal(hidden, self.expected_h): raise RuntimeError("Identical-bank prefix differs")
        if self.mode == "native":
            y, logits = OlmoeSparseMoeBlock.forward(self, hidden); self.cached = (y, logits)
        else:
            native, logits = self.cached
            mass = applied_mass(logits, hidden.dtype, self.top_k, self.norm_topk_prob).reshape(*hidden.shape[:-1], 1)
            y = (mass * self.f0).to(native.dtype)
        self.last_router_logits = logits
        return (y, logits) if self.tuple_contract else y


def gamma_fit(c, y):
    c, y = c.double(), y.double(); numerator, denominator = (c * y).sum(), c.square().sum()
    valid = bool(torch.isfinite(numerator) and torch.isfinite(denominator) and denominator > 0)
    return {"status": "defined" if valid else "unmeasurable", "gamma": float(numerator / denominator) if valid else None,
            "numerator": float(numerator) if torch.isfinite(numerator) else None,
            "denominator": float(denominator) if torch.isfinite(denominator) else None,
            "scope": "One model-level training-Hcal least-squares scalar; no labels/held/clamp/search"}


def tensor_sha(value):
    array = value.detach().float().cpu().numpy() if torch.is_tensor(value) else np.asarray(value)
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def public_assets(args):
    record = assets.read(args.asset_preflight); root = args.public_model
    if root.resolve() != Path(record["source_pin"]["local_asset_dir"]).resolve(): raise ValueError("Public model asset path differs from pinned record")
    if assets.sha(root / "config.json") != record["olmoe_config"]["sha256"] or assets.sha(root / "model.safetensors.index.json") != record["olmoe_config"]["index"]["sha256"]:
        raise ValueError("Public config/index SHA differs")
    config = assets.read(root / "config.json")
    if any(config[key] != value for key, value in {"hidden_size": 2048, "num_experts": 64, "num_experts_per_tok": 8,
        "intermediate_size": 1024, "norm_topk_prob": False, "vocab_size": 50304}.items()): raise ValueError("Public architecture differs")
    verified = {}
    for name, proof in record["source_pin"]["weight_shards"].items():
        actual = assets.sha(root / name)
        if (root / name).stat().st_size != proof["bytes"] or actual != proof["sha256_from_e122_provenance"]: raise ValueError("Public weight shard differs")
        verified[name] = actual
    for name, proof in record["tokenizers"].items():
        if not proof["all_byte_identical"] or assets.sha(root / name) != proof["records"]["dense"]["sha256"]: raise ValueError("Tokenizer identity differs")
    return {"asset_preflight_sha256": assets.sha(args.asset_preflight), "weight_shards_verified": verified,
            "pin_note": record["source_pin"]["revision_note"]}


@torch.no_grad()
def hcal(model, original, name, capture, identity, data, args, prefix_hash):
    windows = data.fixed_windows("train", 64, 91024)
    proof = {"split": "train", "cal_seed": 91024, "seq_len": 512, "stride": 4, "window_hash": base.digest_json(windows),
             "data_identity_sha256": base.digest_json(data.provenance), "prefix_hash": prefix_hash}
    if capture is not None:
        source = Path(identity["metadata"]["functional_capture"]); header = capture["metadata"]["hcal"]
        if any(header.get(key) != proof[key] for key in ("window_hash", "data_identity_sha256", "split", "cal_seed", "seq_len", "stride")):
            raise ValueError("Controlled Hcal source/window proof differs")
        with np.load(source, allow_pickle=False) as raw: values = np.asarray(raw["Hcal"])
        proof.update({"source": str(source), "source_sha256": identity["capture_sha256"], "prefix_kind": "Shared frozen controlled prefix"})
    else:
        path = args.raw_output / "public_native_Hcal.npy"; old_proof = assets.read(path.with_suffix(".json"))
        if path.exists():
            if not old_proof or any(old_proof.get(key) != value for key, value in proof.items()) or assets.sha(path) != old_proof.get("file_sha256"):
                raise ValueError("Public Hcal cache source/window proof differs")
            values = np.load(path, allow_pickle=False)
        else:
            collected = []
            def collect(module, inputs): collected.append(inputs[0][:, ::4].detach().float().cpu().reshape(-1, inputs[0].shape[-1]))
            hook = original.register_forward_pre_hook(collect)
            try:
                for batch, _ in data.iter_fixed("train", windows, 16):
                    with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=batch[:, :-1].to("cuda:0"), use_cache=False)
            finally: hook.remove()
            values = torch.cat(collected).numpy(); path.parent.mkdir(parents=True, exist_ok=True); np.save(path, values)
            assets.write(path.with_suffix(".json"), {**proof, "file_sha256": assets.sha(path)})
        proof.update({"source": str(path), "source_sha256": assets.sha(path), "prefix_kind": "Public model's own native prefix; not dense Hcal"})
    if values.shape != (8192, 2048) or not np.isfinite(values).all(): raise ValueError("Invalid Hcal8192")
    return values, {**proof, "Hcal_sha256": tensor_sha(values)}


@torch.no_grad()
def calibrate(wrapper, values, proof, name, args, attempt):
    wrapper.begin_batch(("train_cal", name)); wrapper.mode = "native"
    hidden = torch.from_numpy(values).to(device="cuda:0", dtype=torch.bfloat16).reshape(16, 512, 2048)
    with torch.autocast("cuda", dtype=torch.bfloat16): wrapper(hidden)
    cache = wrapper.cache; fit = gamma_fit(cache["c"], cache["native"]); wrapper.gamma = fit["gamma"]
    y = cache["native"].double(); amplitudes = {}; errors = {}
    for key in ("native", "c", "r", "mean"):
        value = cache[key].double().square().mean().sqrt(); amplitudes[key] = float(value) if torch.isfinite(value) else None
    for mode, value in (("c", cache["c"]), ("r", cache["r"]), ("zero", torch.zeros_like(cache["native"])),
                        ("recompose", cache["c"] + cache["r"]), ("gamma_c", fit["gamma"] * cache["c"] if fit["gamma"] is not None else None)):
        error = (value.double() - y).square().sum(-1).mean() if value is not None else None
        errors[mode] = float(error) if error is not None and torch.isfinite(error) else None
    path = args.raw_output / f"{name}_attempt{attempt:02d}_cal_vectors.npz"
    np.savez(path, y=cache["native"].float().cpu().numpy(), c=cache["c"].cpu().numpy(), r=cache["r"].cpu().numpy(), mass=cache["mass"].cpu().numpy())
    record = {"fit": fit, "Hcal": proof, "rms_per_component": amplitudes, "real_cache_squared_l2_error_mean": errors,
        "mass_min_max_mean": [float(cache["mass"].min()), float(cache["mass"].max()), float(cache["mass"].mean())],
        "vectors": str(path), "vectors_sha256": assets.sha(path), "hidden_dtype": str(hidden.dtype),
        "expert_storage_dtypes": sorted({str(value.dtype) for value in wrapper.original.parameters()}), "forward": "BF16 autocast; FP32 mean/c/r; returns native y dtype"}
    assets.write(args.raw_output / f"{name}_attempt{attempt:02d}_calibration.json", record); wrapper.clear(); return record


def floor_record(teacher, other, labels, metadata):
    values = old.fidelity.token_metrics(teacher, other, labels)
    return {"tokens": labels.numel(), "kl_max_abs": float(values[..., 0].abs().max()), "nll_delta_max_abs": float(values[..., 3].abs().max()),
            "log_probability_max_abs": float((teacher - other).abs().max()), "metrics": old.summaries(old.rows_from_logps(teacher, other, labels, metadata))}


@torch.no_grad()
def evaluate_setting(name, args, started):
    anchor = assets.read(args.bank_root / old.IDS[0] / "metadata.json"); anchor_prov = assets.read(anchor["staged_provenance"])
    data = base.TokenData(anchor_prov["args"]["data"], 512); capture, identity, legacy = None, None, None
    if name != "public_olmoe_main":
        bank, capture, provenance, legacy, identity = old.load_asset(args.bank_root, name)
        model = old.OlmoForCausalLM.from_pretrained(provenance["args"]["model"], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval(); model.model.layers[9].mlp = bank.to("cuda:0")
        windows = data.fixed_windows("held", 512, provenance["args"]["eval_seed"]); old.fidelity.guard_inputs(provenance, data, windows)
        source_proof = identity
    else:
        source_proof = public_assets(args)
        model = OlmoeForCausalLM.from_pretrained(args.public_model, dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval()
        windows = data.fixed_windows("held", 512, anchor_prov["args"]["eval_seed"]); old.fidelity.guard_inputs(anchor_prov, data, windows)
    model.requires_grad_(False); model.config.use_cache = False; original = model.model.layers[9].mlp
    prefix_hash = base.sampled_parameter_hash(model, "model.layers.9.mlp."); original_hash = old.tensor_state_hash(original.state_dict())
    order_before = tuple(id(module) for module in (original.block if hasattr(original, "block") else original).experts)
    values, hproof = hcal(model, original, name, capture, identity, data, args, prefix_hash)
    args.raw_output.mkdir(parents=True, exist_ok=True); attempt = len(list(args.raw_output.glob(f"{name}_attempt*_sequences.json"))) + 1
    wrapper = UniformDecomposition(original); calibration = calibrate(wrapper, values, hproof, name, args, attempt)
    model.model.layers[9].mlp = wrapper; raw = {mode: [] for mode in MODES}; status = {mode: {"status": "running"} for mode in MODES}
    if wrapper.gamma is None: status["gamma_c"] = {"status": "unmeasurable", "reason": calibration["fit"]}
    scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16"); controls = {}; input_hash = hashlib.sha256(); completed = 0
    for index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
        if time.monotonic() - started >= args.max_hours * 3600: break
        input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); labels = batch[:, 1:]
        wrapper.begin_batch(("held", index)); wrapper.mode = "native"
        teacher = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
        raw["native"].extend(old.rows_from_logps(teacher, teacher, labels, metadata))
        if index == 0:
            model.model.layers[9].mlp = original
            unwrapped = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            controls["original_vs_wrapped_native"] = floor_record(unwrapped, teacher, labels, metadata)
            tied = IdenticalExpertControl(wrapper); model.model.layers[9].mlp = tied
            tied_native = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1); tied.mode = "uniform"
            tied_mean = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            controls["identical_expert_bank"] = {"scope": "All64 references=f0, its own native prediction versus s*f0; actual dtype/operator floor, not a dataset mean",
                **floor_record(tied_native, tied_mean, labels, metadata)}
            model.model.layers[9].mlp = wrapper; del unwrapped, tied_native, tied_mean, tied
        for mode in MODES[1:]:
            if status[mode]["status"] != "running": continue
            try:
                wrapper.mode = mode
                student = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                raw[mode].extend(old.rows_from_logps(teacher, student, labels, metadata)); del student
            except Exception as error: status[mode] = {"status": "failed", "error": f"{type(error).__name__}: {error}", "batch": index}
        wrapper.clear(); completed += 1; del teacher
        base.emit("necessity_batch", setting=name, completed=completed, total=32)
    model.model.layers[9].mlp = original
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != prefix_hash or old.tensor_state_hash(original.state_dict()) != original_hash:
        raise RuntimeError("Original parameters/frozen prefix changed")
    if order_before != tuple(id(module) for module in (original.block if hasattr(original, "block") else original).experts): raise RuntimeError("Source expert order changed")
    for mode, record in status.items():
        if record["status"] == "running":
            record["status"] = "complete" if len(raw[mode]) == 512 else "incomplete_budget"
            if record["status"] == "complete": record["metrics"] = old.summaries(raw[mode])
    legacy_difference = None
    if legacy and status["native"]["status"] == "complete":
        legacy_nll = next(row["held"]["file"]["mean"] for row in legacy["evaluations"] if row["step"] == 62500)
        legacy_difference = status["native"]["metrics"]["global"]["student_nll"]["mean"] - legacy_nll
    raw_path = args.raw_output / f"{name}_attempt{attempt:02d}_sequences.json"; assets.write(raw_path, {"setting": name, "conditions": raw, "status": status, "controls": controls})
    result = {"status": "complete" if completed == 32 and not any(value["status"] == "failed" for value in status.values()) else "incomplete_or_failed",
        "setting": name, "conditions": status, "calibration": calibration, "first_batch_controls": controls, "legacy_controlled_native_NLL_difference": legacy_difference,
        "source_proof": source_proof, "native_prefix_hash": prefix_hash, "original_block_state_hash": original_hash,
        "held_window_hash": base.digest_json(windows), "input_sha256": input_hash.hexdigest(), "completed_batches": completed,
        "raw_sequences": str(raw_path), "raw_sha256": assets.sha(raw_path), "cache_scope": "One native block+64-expert mean per batch, prefix equality checked on every mode; cache cleared between batches"}
    del wrapper, original, model; gc.collect(); torch.cuda.empty_cache(); return result


def run(args):
    if assets.sha(WB / "scripts/e132_bank_grafting.py") != E132_SHA: raise ValueError("Frozen E132 helper differs")
    for name, expected in {**assets.FROZEN, "e124_compare.py": old.COMPARE_SHA, "e130_finalize.py": "2b1bed11f13fc0cd2dbb658383b7d9c973da41760e4ec1236e7f18a10a76039f"}.items():
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError("Frozen source differs")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", ""); physical = args.physical_gpu
    if physical is None:
        if not visible.isdigit(): raise ValueError("Specify one physical GPU")
        physical = int(visible)
    if visible and visible != str(physical): raise ValueError("Visible/requested physical GPU differ")
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA initialized before occupancy check")
    gpu = assets.gpu_status(physical); result = {"experiment": "E134", "status": "partial", "script_sha256": assets.sha(__file__),
        "frozen_E132_sha256": E132_SHA, "gpu_preflight": gpu, "settings_order": SETTINGS, "settings": {},
        "scope": __doc__, "readout": "Each model's own native reference; BF16 logits then FP32 logsoftmax; file CIs only, no cross-model absolute or freezing-only causal comparison"}
    if not assets.gpu_free(gpu): result["status"] = "deferred_gpu_busy_or_unavailable"; assets.write(args.summary, result); return result
    previous = assets.read(args.summary); prior = previous.get("elapsed_wall_seconds", 0.) if previous and previous.get("script_sha256") == result["script_sha256"] else 0.
    result["previous_wall_seconds_charged"] = prior; os.environ["CUDA_VISIBLE_DEVICES"] = str(physical); started = time.monotonic() - prior
    for index, name in enumerate(SETTINGS):
        if index >= args.max_settings or time.monotonic() - started >= args.max_hours * 3600:
            result["settings"][name] = {"status": "not_run_fixed_limit_or_budget"}; continue
        try: result["settings"][name] = evaluate_setting(name, args, started)
        except Exception as error:
            result["settings"][name] = {"status": "failed", "error": f"{type(error).__name__}: {error}"}; gc.collect()
            if torch.cuda.is_initialized(): torch.cuda.empty_cache()
        assets.write(args.summary, result)
    result["elapsed_wall_seconds"] = time.monotonic() - started
    result["status"] = "complete" if all(value["status"] == "complete" for value in result["settings"].values()) else "partial"
    assets.write(args.summary, result); return result


def self_test():
    torch.set_num_threads(1); torch.manual_seed(134); contract_cases = []
    for tuple_contract in (False, True):
        for renorm in (False, True):
            bank = base.TensorMoE(8, 8, 4, 2, .02).eval(); bank.requires_grad_(False); bank.block.norm_topk_prob = renorm
            for expert in bank.block.experts[1:]: expert.load_state_dict(bank.block.experts[0].state_dict())
            original = bank.block if tuple_contract else bank; before = old.tensor_state_hash(original.state_dict())
            wrapper = UniformDecomposition(original); hidden = torch.randn(1, 3, 8)
            wrapper.begin_batch("cal"); native = wrapper(hidden); native_y = native[0] if tuple_contract else native
            manual = wrapper.cache["logits"].float().softmax(-1).topk(2, -1).values
            if renorm: manual = manual / manual.sum(-1, keepdim=True)
            assert torch.equal(wrapper.cache["mass"].reshape(-1, 1), manual.to(hidden.dtype).float().sum(-1, keepdim=True))
            assert torch.allclose(wrapper.cache["c"], native_y, atol=1e-9, rtol=1e-5)
            wrapper.gamma = 1.; computations = wrapper.computations
            for mode in MODES:
                wrapper.mode = mode; output = wrapper(hidden); y = output[0] if tuple_contract else output
                assert y.dtype == native_y.dtype and isinstance(output, tuple) == tuple_contract
                if tuple_contract: assert output[1] is wrapper.cache["logits"]
            assert wrapper.computations == computations
            wrapper.mode = "native"; returned = wrapper(hidden); returned_y = returned[0] if tuple_contract else returned
            snapshot = wrapper.cache["native"].clone(); returned_y.add_(1)
            assert torch.equal(wrapper.cache["native"], snapshot)  # A downstream in-place consumer cannot corrupt the cache.
            wrapper.mode = "recompose"; output = wrapper(hidden); y = output[0] if tuple_contract else output
            assert torch.allclose(y, native_y, atol=1e-9, rtol=1e-5)
            try: wrapper(hidden + 1)
            except RuntimeError: pass
            else: raise AssertionError("Different prefix reused a cached batch")
            wrapper.begin_batch("held"); wrapper.mode = "native"; wrapper(hidden + 1)
            assert wrapper.computations == computations + 1 and wrapper.gamma == 1.
            assert old.tensor_state_hash(original.state_dict()) == before
            # BF16 program floor is measured, not assumed exactly equivariant.
            wrapper.begin_batch("bf16"); hidden_bf16 = hidden.bfloat16()
            with torch.autocast("cpu", dtype=torch.bfloat16): wrapper(hidden_bf16)
            wrapper.mode = "c"
            with torch.autocast("cpu", dtype=torch.bfloat16): output = wrapper(hidden_bf16)
            assert (output[0] if tuple_contract else output).dtype == torch.bfloat16
            contract_cases.append({"tuple": tuple_contract, "renorm": renorm})
    c = torch.randn(5, 3, dtype=torch.float64); fit = gamma_fit(c, 2.5 * c)
    assert abs(fit["gamma"] - 2.5) < 1e-14 and gamma_fit(torch.zeros_like(c), c)["status"] == "unmeasurable"
    logits = torch.tensor([[.2, -.5, 1.7, 2.1]])
    for renorm in (False, True):
        p = logits.softmax(-1).topk(2, -1).values
        if renorm: p /= p.sum(-1, keepdim=True)
        assert torch.equal(applied_mass(logits, torch.bfloat16, 2, renorm), p.bfloat16().float().sum(-1, keepdim=True))
    assert assets.sha(WB / "scripts/e132_bank_grafting.py") == E132_SHA
    result = {"passed": True, "device": "cpu", "script_sha256": assets.sha(__file__), "contracts": contract_cases,
        "identical_function_uniform_component_oracle": True, "actual_applied_mass_dtype_and_normflag": True,
        "Tensor_tuple_metadata_and_native_dtype_preserved": True, "prefix_cache_reset_and_wrong_batch_rejected": True,
        "downstream_mutation_cannot_change_cache": True,
        "gamma_cal_closed_form_and_zero_denominator": True, "held_does_not_change_gamma": True,
        "original_parameter_state_unchanged": True, "recomposition_positive_control": True, "no_GPU_or_full_LLM": True}
    assets.write(WB / "results/e134/self_test.json", result); print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bank-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e132_banks"))
    parser.add_argument("--public-model", type=Path, default=Path("/tmp/xiang-moe-20261025/olmoe"))
    parser.add_argument("--asset-preflight", type=Path, default=WB / "results/e134/asset_preflight.json")
    parser.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e134_necessity"))
    parser.add_argument("--summary", type=Path, default=WB / "results/e134/necessity.json")
    parser.add_argument("--max-settings", type=int, default=6); parser.add_argument("--max-hours", type=float, default=2.)
    parser.add_argument("--physical-gpu", type=int); args = parser.parse_args()
    if args.self_test: self_test()
    else:
        if not 1 <= args.max_settings <= 6 or not 0 < args.max_hours <= 2: parser.error("Fixed six settings, cumulative budget<=2h")
        if args.raw_output.resolve().is_relative_to(WB): parser.error("Raw/cache must remain outside git")
        print(json.dumps(run(args), indent=2), flush=True)
