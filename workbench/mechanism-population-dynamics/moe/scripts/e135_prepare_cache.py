"""Prepare native OLMoE L9 H/Y BF16-bit caches for the registered E135 pilot."""
from __future__ import annotations
import argparse, copy, hashlib, json, socket, tempfile, time
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e135_common as c

assets, base, WB = c.assets, c.base, c.WB


class CapturedBlock(Exception): pass


def preflight(args):
    record, proof = c.validate_assets(args.asset_preflight)
    data = c.epoch.EpochCoverageTokenData(args.data, 512)
    hcal_meta = assets.read(record["assets"]["public_native_Hcal.json"]["target_path"])
    if hcal_meta["data_identity_sha256"] != base.digest_json(data.provenance): raise ValueError("Native Hcal/data identity differs")
    if hcal_meta["window_hash"] != base.digest_json(data.fixed_windows("train", 64, 91024)): raise ValueError("Native Hcal calibration windows differ")
    return data, record, {"experiment": "E135", "status": "CPU_preflight_only", "host": socket.gethostname(),
        "driver_sha256": assets.sha(__file__), "common_sha256": assets.sha(WB / "scripts/e135_common.py"), "assets": proof,
        "data_manifest_sha256": assets.sha(args.data), "data_identity_sha256": base.digest_json(data.provenance),
        "train_shape": [1024, 16, 512, 2048], "held_shape": [32, 16, 512, 2048], "stored_dtype": "uint16 BF16 bit pattern",
        "positions": 8_388_608, "four_epoch_position_exposures": 33_554_432, "public_Hcal": hcal_meta}


def token_chain(previous, batch):
    return hashlib.sha256(bytes.fromhex(previous) + batch.numpy().astype("<u2", copy=False).tobytes()).hexdigest()


@torch.no_grad()
def generate(args):
    data, asset_record, proof = preflight(args)
    if args.cache_root.exists(): raise FileExistsError("Cache root exists; no silent overwrite of fixed cache")
    staging = args.cache_root.with_name(args.cache_root.name + ".partial"); staging.mkdir(parents=True, exist_ok=False)
    gpu = c.select_gpu(args.physical_gpu)
    status_path = WB / "results/e135/cache_status.json"
    with c.Budget(args.budget_file, "prepare_cache") as budget:
        model_path = asset_record["source_pin"]["target_local_nvme_dir"]
        model = OlmoeForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        teacher = model.model.layers[9].mlp
        before = c.tensor_state_hash(teacher.state_dict()); prefix = base.sampled_parameter_hash(model, "model.layers.9.mlp.")
        if prefix != proof["public_Hcal"]["prefix_hash"]: raise ValueError("Teacher native prefix differs from staged public Hcal")
        teacher_state = {name: value.detach().cpu() for name, value in teacher.state_dict().items()}
        c.atomic_torch_save(staging / "teacher_block.pt", {"schema": "E135-native-teacher-block-v1", "state": teacher_state, "tensor_sha256": before})
        captured = {}
        def save_block(module, inputs, result):
            h, y = inputs[0], result[0]
            if h.shape != (16, 512, 2048) or y.shape != h.shape: raise ValueError("Unexpected native block cache shape")
            if h.dtype != torch.bfloat16 or y.dtype != torch.bfloat16: raise ValueError("Actual native H/Y must be BF16")
            if not torch.isfinite(h).all() or not torch.isfinite(y).all(): raise RuntimeError("Nonfinite native cache H/Y")
            captured.update({"H": c.bf16_bits(h), "Y": c.bf16_bits(y), "energy_sum": float(y.double().square().sum())})
            raise CapturedBlock()
        hook = teacher.register_forward_hook(save_block)
        stream = c.epoch.trainer.SplitStream(135); held = data.fixed_windows("held", 512, 91023)
        held_batches = iter(data.iter_fixed("held", held, 16)); split_records = {}
        try:
            for split, count in (("train", 1024), ("held", 32)):
                shape = (count, 16, 512, 2048)
                arrays = {key: np.lib.format.open_memmap(staging / f"{split}_{key}.npy", mode="w+", dtype="<u2", shape=shape) for key in ("H", "Y")}
                tokens = np.lib.format.open_memmap(staging / f"{split}_tokens.npy", mode="w+", dtype="<u2", shape=(count, 16, 513))
                keys = np.empty((count, 16, 2), dtype=np.int64); chain = hashlib.sha256(f"E135-{split}-token-chain-v1".encode()).hexdigest()
                energy_sum, batch_hashes = 0., []
                for index in range(count):
                    budget.check(); captured.clear()
                    if split == "train": batch = data.train_batch(stream, 16); keys[index] = data.last_batch_keys
                    else:
                        batch, _ = next(held_batches); keys[index] = held[index * 16:index * 16 + 16]
                    tokens[index] = batch.numpy(); chain = token_chain(chain, batch)
                    batch_hashes.append(hashlib.sha256(batch.numpy().astype("<u2", copy=False).tobytes()).hexdigest())
                    try:
                        with torch.autocast("cuda", dtype=torch.bfloat16): model.model(input_ids=batch[:, :-1].to("cuda:0"), use_cache=False)
                    except CapturedBlock: pass
                    else: raise RuntimeError("Native L9 hook did not execute")
                    for key in arrays: arrays[key][index] = captured[key]
                    energy_sum += captured["energy_sum"]
                    base.emit("cache_batch", split=split, completed=index + 1, total=count)
                    if (index + 1) % 32 == 0: assets.write(status_path, {"experiment": "E135", "status": "preparing", "split": split, "batches": index + 1})
                for value in arrays.values(): value.flush()
                tokens.flush(); np.save(staging / f"{split}_keys.npy", keys)
                split_records[split] = {"shape": list(shape), "positions": count * 16 * 512, "energy_mean": energy_sum / (count * 16 * 512 * 2048),
                    "energy_sum_float64": energy_sum, "token_chain_sha256": chain, "batch_token_sha256": batch_hashes}
                del arrays, tokens
        finally: hook.remove()
        if c.tensor_state_hash(teacher.state_dict()) != before or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != prefix:
            raise RuntimeError("Read-only teacher/prefix changed")
        if split_records["train"]["energy_mean"] <= 0: raise ValueError("Training energy denominator is zero; objective undefined")
        rng = np.random.default_rng(135); orders = np.stack([rng.permutation(1024) for _ in range(4)]); np.save(staging / "epoch_orders.npy", orders)
        np.savez(staging / "window_counts.npz", **{f"file_{i}": value for i, value in enumerate(data.window_counts)})
        c.atomic_torch_save(staging / "source_stream.pt", {"coverage": data.coverage_state(), "stream_rng": stream.state_dict()})
        # Real dtype/weight-copy oracle on untouched real train/held cache batches.
        copied = c.bank_from_state(teacher_state, "cuda:0", fp32=True).eval().requires_grad_(False)
        oracle = {}
        for split in ("train", "held"):
            h = c.from_bits(np.load(staging / f"{split}_H.npy", mmap_mode="r")[0], "cuda:0")
            y = c.from_bits(np.load(staging / f"{split}_Y.npy", mmap_mode="r")[0], "cuda:0")
            with torch.autocast("cuda", dtype=torch.bfloat16): native = teacher(h)[0]; copy_y = copied(h)
            oracle[split] = {"positions": 8192, "actual_H_dtype": str(h.dtype), "teacher_storage": "bfloat16", "copy_storage": "float32",
                "native_direct_vs_cache_MSE": float((native.float() - y.float()).double().square().mean()),
                "copy_vs_cache_MSE": float((copy_y.float() - y.float()).double().square().mean()),
                "copy_vs_native_MSE": float((copy_y.float() - native.float()).double().square().mean()),
                "scope": "Actual BF16 operator/dtype floor; no scientific acceptance threshold"}
        assets.write(staging / "copy_oracle.json", oracle)
        files = {path.name: {"sha256": assets.sha(path), "size_bytes": path.stat().st_size} for path in staging.iterdir() if path.is_file()}
        manifest = {"schema": "E135-native-function-cache-v1", "status": "complete", "experiment": "E135", "host": socket.gethostname(),
            "cache_root": str(args.cache_root), "model": model_path, "data": str(args.data), "asset_preflight": str(args.asset_preflight),
            "budget_file": str(args.budget_file), "prepare_proof": proof, "gpu_preflight": gpu, "dimensions": c.DIMS,
            "teacher_block_tensor_sha256": before, "teacher_prefix_hash": prefix, "splits": split_records,
            "stored_dtype": "uint16 bit-view of actual bfloat16; never numeric uint16 conversion", "files": files,
            "train_exposure": data.coverage_summary(per_file=True), "held_window_hash": base.digest_json(held),
            "training_orders": "Independent default_rng(135), four successive full permutations of1024; every cache batch exactly4 times",
            "token_uniqueness_scope": "Actual window exposures recorded; distinct windows do not assert distinct token content", "copy_oracle": oracle}
        assets.write(staging / "manifest.json", manifest)
        for path in staging.iterdir(): path.chmod(0o444)
        staging.rename(args.cache_root); assets.write(status_path, {"experiment": "E135", "status": "complete", "manifest_sha256": assets.sha(args.cache_root / "manifest.json"), "cache_root": str(args.cache_root)})
    return manifest


def self_test():
    torch.set_num_threads(1); torch.manual_seed(135)
    values = torch.tensor([0., -0., 1., -1., 3.14159, 1e-3]).bfloat16(); bits = c.bf16_bits(values)
    assert torch.equal(c.from_bits(bits).view(torch.uint16), values.view(torch.uint16))
    teacher = base.TensorMoE(8, 8, 4, 2, .02).bfloat16().eval(); dims = {"hidden": 8, "expert_size": 8, "experts": 4, "top_k": 2}
    copied = c.bank_from_state(teacher.block.state_dict(), fp32=True, dims=dims).eval()
    h = torch.randn(2, 4, 8).bfloat16()
    with torch.no_grad(), torch.autocast("cpu", dtype=torch.bfloat16): y = teacher(h); copy_y = copied(h); tuple_y, logits = c.PublicStudent(copied)(h)
    assert tuple_y.dtype == y.dtype == torch.bfloat16 and logits.shape == (8, 4)
    assert torch.equal(copy_y, tuple_y)
    assert all(value.dtype == torch.float32 for value in copied.parameters())
    rng = np.random.default_rng(135); orders = np.stack([rng.permutation(8) for _ in range(4)])
    assert np.array_equal(np.bincount(orders.reshape(-1), minlength=8), np.full(8, 4))
    with tempfile.TemporaryDirectory(prefix="e135_budget_cpu_") as directory:
        path = Path(directory) / "budget.json"
        with c.Budget(path, "CPU_contract", limit=10): pass
        ledger = assets.read(path); assert not ledger["active"] and ledger["completed_seconds"] >= 0
    return {"passed": True, "CPU_only": True, "BF16_bit_roundtrip_exact_including_negative": True,
        "copy_FP32_storage_and_BF16_forward_tuple_contract": True, "tiny_copy_MSE_numeric_floor": float((copy_y.float() - y.float()).square().mean()),
        "four_exact_cache_passes": True, "ledger_contract": True, "driver_sha256": assets.sha(__file__),
        "common_sha256": assets.sha(WB / "scripts/e135_common.py"), "frozen_sources": c.source_proof()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--mode", choices=("preflight", "prepare", "self-test"), default="preflight")
    parser.add_argument("--asset-preflight", type=Path, default=WB / "results/e135/asset_preflight.json")
    parser.add_argument("--data", type=Path, default=Path("/tmp/xiang-moe-20261025/e125_data_cover/manifest.json"))
    parser.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    parser.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_budget.json")); parser.add_argument("--physical-gpu", type=int, default=0)
    args = parser.parse_args()
    if args.mode == "self-test": result = self_test(); assets.write(WB / "results/e135/cache_self_test.json", result)
    elif args.mode == "preflight": result = preflight(args)[-1]
    else:
        try: result = generate(args)
        except Exception as error:
            assets.write(WB / "results/e135/cache_status.json", {"experiment": "E135", "status": "failed_or_incomplete", "error": f"{type(error).__name__}: {error}"})
            raise
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
