"""CPU-first native checkpoint loading for the E156 source cross.

No checkpoint is loaded on import. The CPU conversion intentionally includes
nonpersistent buffers; callers must independently validate the resulting native
models and outputs against their experimental reference.
"""
from __future__ import annotations


def _classes(label, *, complete):
    # Lazy imports avoid initializing the existing experiment modules on import.
    import e150_native as e150
    if label == "P":
        import e154_native as e154
        if complete:
            e154.metadata(complete=True)
        return e154.classes()
    if label in ("A", "B"):
        source = {"A": 0, "B": 1}[label]
        if complete:
            e150.assets(complete=True, required_sources=(source,))
        return e150.classes(source)
    raise ValueError(f"Expected label P, A, or B; got {label!r}")


def _cpu_bf16(model):
    import torch
    tensors = list(model.parameters()) + list(model.buffers())
    if any(t.device.type != "cpu" for t in tensors):
        raise ValueError("Model parameters and buffers must be on CPU before conversion")
    return model.bfloat16()


def load_cpu_bf16(label, device="cuda:0"):
    """Load a pinned P/A/B checkpoint in CPU FP32, cast on CPU, then transfer.

    Requires enough CPU memory for FP32 checkpoint loading and conversion.
    """
    import torch
    cfg_cls, cls, root = _classes(label, complete=True)
    cfg = cfg_cls.from_json_file(root / "config.json")
    model, info = cls.from_pretrained(
        root, config=cfg, dtype=torch.float32, local_files_only=True,
        attn_implementation="sdpa", output_loading_info=True,
    )
    fields = ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")
    if any(field not in info for field in fields):
        raise ValueError(f"Incomplete checkpoint loading report: {info}")
    bad = {field: info[field] for field in fields if info[field]}
    if bad:
        raise ValueError(f"Checkpoint/model keys do not match exactly: {bad}")
    return _cpu_bf16(model).to(device).eval().requires_grad_(False)


def self_test():
    """Check native tiny model conversion on CPU only; load no checkpoint."""
    import torch
    result = {}
    for label in ("P", "A", "B"):
        cfg_cls, cls, _ = _classes(label, complete=False)
        cfg = cfg_cls(
            vocab_size=64, hidden_size=16, intermediate_size=8,
            num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2,
            num_experts=4, num_experts_per_tok=2, num_shared_experts=1,
            norm_topk_prob=False, max_position_embeddings=32, pad_token_id=63,
            eos_token_id=62, output_router_logits=False,
        )
        cfg._attn_implementation = "sdpa"
        model = cls(cfg)
        before_params = {name: t.detach().clone() for name, t in model.named_parameters()}
        before_buffers = {name: t.detach().clone() for name, t in model.named_buffers()}
        rope_attributes = {
            name: (module.original_inv_freq.detach().clone(), "original_inv_freq" in module._buffers)
            for name, module in model.named_modules() if hasattr(module, "original_inv_freq")
        }
        if not rope_attributes:
            raise AssertionError(f"{label}: expected original_inv_freq attribute")
        model = _cpu_bf16(model).to("cpu").eval().requires_grad_(False)
        for kind, old, new in (
            ("parameter", before_params, dict(model.named_parameters())),
            ("buffer", before_buffers, dict(model.named_buffers())),
        ):
            if old.keys() != new.keys():
                raise AssertionError(f"{label}: {kind} names changed")
            for name, original in old.items():
                expected = original.bfloat16() if original.is_floating_point() else original
                actual = new[name]
                if actual.device.type != "cpu" or actual.dtype != expected.dtype or not torch.equal(actual, expected):
                    raise AssertionError(f"{label}: {kind} conversion mismatch: {name}")
        if model.training or any(p.requires_grad for p in model.parameters()):
            raise AssertionError(f"{label}: eval or requires_grad_(False) failed")
        rope_info = {}
        for name, (original, registered) in rope_attributes.items():
            current = model.get_submodule(name).original_inv_freq
            expected = original.bfloat16() if registered and original.is_floating_point() else original
            if current.dtype != expected.dtype or not torch.equal(current, expected):
                raise AssertionError(f"{label}: original_inv_freq semantics changed: {name}")
            rope_info[name] = {"registered_buffer": registered, "dtype_after": str(current.dtype)}
        result[label] = {"parameters": len(before_params), "buffers": len(before_buffers),
                         "original_inv_freq": rope_info,
                         "conversion_exact": True, "eval_and_frozen": True}
    return {"status": "passed", "cpu_only": True, "models": result,
            "cpu_gpu_rounding_equivalence_checked": False}
