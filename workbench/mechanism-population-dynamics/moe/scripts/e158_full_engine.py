"""E158 v3: full-prefix native shapes, causal last-position interventions.

The failed v2 cached implementation remains untouched. Here native forward
uses use_cache=False and its supported logits_to_keep=1. All prefix positions
are evaluated, including within each expert GEMM. Empty experts alone are
skipped. Earlier decoder outputs are clamped to their native values during
intervention: mathematically redundant causal-prefix preservation, preventing
BF16 expert-batch-size changes from propagating to earlier tokens.
"""
# Sparse arithmetic adapted from HuggingFace EmoSparseMoeBlock.forward.
# Copyright 2025 the HuggingFace Team. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# http://www.apache.org/licenses/LICENSE-2.0
# Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
from contextlib import contextmanager, ExitStack
from dataclasses import dataclass
import numpy as np
import torch
from torch.nn import functional as F
from e158_engine import first, with_first, replace_forward


def full_sparse(block, hidden, layer, tap):
    if block.num_shared_experts != 1 or block.always_active_experts not in (None, []) or block.norm_topk_prob:
        raise ValueError("Expected canonical 127 routed + last shared interface")
    shape = hidden.shape
    flat = hidden.view(-1, shape[-1])
    logits = block.gate(flat)
    wr = F.softmax(logits[:, :-1], dim=1, dtype=torch.float)
    ws = F.softmax(logits[:, -1:], dim=1, dtype=torch.float)
    wr, er = torch.topk(wr, block.top_k - 1, dim=-1)
    ws, es = torch.topk(ws, 1, dim=-1)
    weights = torch.cat((wr, ws), 1).to(flat.dtype)
    selected = torch.cat((er, es + block.num_experts - 1), 1)
    mask = F.one_hot(selected, num_classes=block.num_experts).permute(2, 1, 0)
    result = torch.zeros_like(flat)
    routed, shared = None, None
    for expert in sorted(set(selected.reshape(-1).tolist())):
        idx, top_x = torch.where(mask[expert])
        if expert == block.num_experts - 1:
            routed = result.clone()
        state = flat[None, top_x].reshape(-1, shape[-1])
        contribution = (block.experts[expert](state) * weights[top_x, idx, None]).to(flat.dtype)
        if expert == block.num_experts - 1:
            shared = torch.zeros_like(flat)
            shared.index_add_(0, top_x, contribution)
        result.index_add_(0, top_x, contribution)
    if routed is None or shared is None or not torch.equal(routed + shared, result):
        raise ValueError("Native component reconstruction failed")
    result = result.reshape(shape)
    if tap is not None:
        tap(layer, hidden, routed.reshape(shape), shared.reshape(shape), result)
    return result, logits


@contextmanager
def fast_blocks(model, tap=None):
    with ExitStack() as stack:
        for layer, decoder in enumerate(model.model.layers):
            block = decoder.mlp
            stack.enter_context(replace_forward(block, lambda h, b=block, l=layer: full_sparse(b, h, l, tap)))
        yield


@dataclass
class Query:
    ids: torch.Tensor
    lp: torch.Tensor
    uncached_lp: torch.Tensor
    hidden: tuple
    routed: tuple
    shared: tuple
    mlp_output: tuple
    decoder_output: tuple
    final_residual: torch.Tensor
    uncached_to_cached_KL: float
    uncached_gold_logprob_difference: float
    uncached_greedy: int


@torch.no_grad()
def step(model, ids, logits_to_keep=1):
    out = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False,
                logits_to_keep=logits_to_keep, return_dict=True, output_router_logits=False)
    lp = out.logits[0, -1].float().log_softmax(-1)
    if not torch.isfinite(lp).all():
        raise ValueError("Nonfinite full-prefix prediction")
    return lp


@torch.no_grad()
def capture(model, token_ids, gold_token):
    device = next(model.parameters()).device
    ids = torch.as_tensor(np.asarray(token_ids).copy(), dtype=torch.long, device=device)[None]
    full_readout_reference = step(model, ids, logits_to_keep=0)
    native_y, native_dec, handles = {}, {}, []
    try:
        for layer, decoder in enumerate(model.model.layers):
            handles.append(decoder.mlp.register_forward_hook(
                lambda m, args, out, i=layer: native_y.__setitem__(i, first(out).detach().clone())))
            handles.append(decoder.register_forward_hook(
                lambda m, args, out, i=layer: native_dec.__setitem__(i, first(out).detach().clone())))
        reference = step(model, ids)
    finally:
        for h in handles: h.remove()
    taps = {}
    def collect(layer, hidden, routed, shared, output):
        if not torch.equal(output, native_y[layer]):
            raise ValueError("Skipping empty experts changed full native MLP output")
        taps[layer] = (hidden.detach().clone(), routed[:, -1:].detach().clone(),
                       shared[:, -1:].detach().clone(), output[:, -1:].detach().clone())
    with fast_blocks(model, collect): actual = step(model, ids)
    if not torch.equal(actual, reference) or len(taps) != len(native_y):
        raise ValueError("Full native prediction/taps differ")
    ordered = [taps[i] for i in range(len(taps))]
    dec = tuple(native_dec[i] for i in range(len(taps)))
    # Legacy schema fields now contain measured full-readout vs last-only head
    # numerical differences. Neither path uses a KV cache. Fast vs native
    # last-only-head execution is separately required to be bitexact above.
    readout_kl = float((full_readout_reference.exp() * (full_readout_reference - reference)).double().sum())
    gold_difference = float(reference[int(gold_token)] - full_readout_reference[int(gold_token)])
    return Query(ids, actual, full_readout_reference, tuple(v[0] for v in ordered), tuple(v[1] for v in ordered),
                 tuple(v[2] for v in ordered), tuple(v[3] for v in ordered), dec, dec[-1][:, -1:].clone(),
                 readout_kl, gold_difference, int(full_readout_reference.argmax()))


@torch.no_grad()
def routed_native_identity(model, query):
    for layer, decoder in enumerate(model.model.layers):
        block = decoder.mlp
        with replace_forward(block.experts[-1], lambda x: torch.zeros_like(x)):
            result = first(block(query.hidden[layer]))[:, -1:]
        if not torch.equal(result, query.routed[layer]):
            raise ValueError("Native full-shape S-zero differs from R tap")
        with ExitStack() as stack:
            for expert in block.experts[:-1]:
                stack.enter_context(replace_forward(expert, lambda x: torch.zeros_like(x)))
            result = first(block(query.hidden[layer]))[:, -1:]
            if not torch.equal(result, query.shared[layer]):
                raise ValueError("Native full-shape R-zero differs from S tap")
            with replace_forward(block.experts[-1], lambda x: torch.zeros_like(x)):
                if torch.count_nonzero(first(block(query.hidden[layer]))):
                    raise ValueError("Native both-zero block nonzero")


@contextmanager
def fixed_prefix(model, query):
    handles = []
    try:
        for layer, decoder in enumerate(model.model.layers):
            def clamp(module, args, output, index=layer):
                h = first(output).clone()
                h[:, :-1] = query.decoder_output[index][:, :-1]
                return with_first(output, h)
            handles.append(decoder.register_forward_hook(clamp))
        yield
    finally:
        for h in handles: h.remove()


@torch.no_grad()
def interchange(model, target, source, layer, component):
    module = model.model.layers[layer].mlp
    if component == "R": replacement = source.routed[layer] + target.shared[layer]
    elif component == "S": replacement = target.routed[layer] + source.shared[layer]
    elif component == "RS": replacement = source.routed[layer] + source.shared[layer]
    elif component == "zero_R": replacement = target.shared[layer]
    elif component == "zero_S": replacement = target.routed[layer]
    elif component == "zero_RS": replacement = torch.zeros_like(target.mlp_output[layer])
    elif component == "residual":
        if layer != len(model.model.layers) - 1: raise ValueError("Final residual control only")
        replacement = source.final_residual
        module = model.model.layers[layer]
    else: raise ValueError("Unknown component")
    def patch(module, args, output):
        h = first(output).clone()
        h[:, -1:] = replacement
        return with_first(output, h)
    with fixed_prefix(model, target):
        handle = module.register_forward_hook(patch)
        try:
            with fast_blocks(model): return step(model, target.ids)
        finally: handle.remove()


def self_test():
    import e156_loading as loading
    import e144145_common as old
    records = {}
    torch.set_num_threads(1)
    for label in ("P", "A", "B"):
        cfg_cls, cls, _ = loading._classes(label, complete=False)
        for dtype in (torch.float32, torch.bfloat16):
            torch.manual_seed(158)
            cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=2,
                          num_attention_heads=2, num_key_value_heads=2, num_experts=4,
                          num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False,
                          max_position_embeddings=32, pad_token_id=63, eos_token_id=62,
                          output_router_logits=False)
            cfg._attn_implementation = "sdpa"
            model = cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            ph, bh = old.tensor_hash(model.state_dict()), old.tensor_hash(dict(model.named_buffers()))
            target = capture(model, np.array([1, 2, 3, 4, 5]), 6)
            source = capture(model, np.array([1, 7, 8, 5]), 9)
            routed_native_identity(model, target)
            for layer in range(2):
                replacements = {"R": source.routed[layer] + target.shared[layer],
                    "S": target.routed[layer] + source.shared[layer],
                    "RS": source.routed[layer] + source.shared[layer],
                    "zero_R": target.shared[layer], "zero_S": target.routed[layer],
                    "zero_RS": torch.zeros_like(target.mlp_output[layer])}
                for component in ("R", "S", "RS"):
                    assert torch.equal(interchange(model, target, target, layer, component), target.lp)
                for component, replacement in replacements.items():
                    def patch(module, args, out):
                        h = first(out).clone(); h[:, -1:] = replacement
                        return with_first(out, h)
                    with fixed_prefix(model, target):
                        handles = []
                        def observe(module, args, out, index):
                            assert torch.equal(first(out)[:, :-1], target.decoder_output[index][:, :-1])
                        for i, decoder in enumerate(model.model.layers):
                            handles.append(decoder.register_forward_hook(lambda m, a, o, index=i: observe(m, a, o, index)))
                        handle = model.model.layers[layer].mlp.register_forward_hook(patch)
                        try: expected = step(model, target.ids)
                        finally:
                            handle.remove()
                            for h in handles: h.remove()
                    actual = interchange(model, target, source, layer, component)
                    assert torch.equal(actual, expected), (label, dtype, layer, component)
            assert torch.equal(interchange(model, target, source, 1, "residual"), source.lp)
            assert old.tensor_hash(model.state_dict()) == ph and old.tensor_hash(dict(model.named_buffers())) == bh
            assert all("forward" not in d.mlp.__dict__ and not d.mlp._forward_hooks and not d._forward_hooks for d in model.model.layers)
            records[label + "/" + str(dtype)] = {"full_native_bitexact": True, "different_length_source_residual_exact": True,
                "same_query_identity_all_layers_paths": True, "component_native_removals_exact": True, "sources_restored": True,
                "perturbed_fast_vs_original_native_exact": True, "causal_prefix_clamp_observed_all_layers": True}
    return {"status": "passed", "CPU_only": True, "records": records}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
