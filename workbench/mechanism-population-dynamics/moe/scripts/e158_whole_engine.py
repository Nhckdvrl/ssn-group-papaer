"""Whole last-position pathways, fixed native causal prefix, no KV cache.

R/S sources reuse bit-preserved full-prefix traces from the failed v3 timing
preflight. Fresh native query replay verifies hidden inputs and readouts.
Nonreplaced components are evaluated at the current, endogenous hidden state.
"""
from dataclasses import dataclass
from contextlib import ExitStack
import numpy as np
import torch
import e158_full_engine as full
from e158_engine import first, with_first


@dataclass
class Query:
    ids: torch.Tensor
    lp: torch.Tensor
    routed: tuple
    shared: tuple
    attention: tuple
    decoder_output: tuple
    final_residual: torch.Tensor


@torch.no_grad()
def capture(model, token_ids, reference=None):
    device = next(model.parameters()).device
    ids = torch.as_tensor(np.asarray(token_ids).copy(), dtype=torch.long, device=device)[None]
    hidden, dec, attn, mlp, handles = {}, {}, {}, {}, []
    try:
        for layer, decoder in enumerate(model.model.layers):
            handles.append(decoder.mlp.register_forward_pre_hook(
                lambda m, args, i=layer: hidden.__setitem__(i, args[0][:, -1:].detach().clone())))
            handles.append(decoder.mlp.register_forward_hook(
                lambda m, args, out, i=layer: mlp.__setitem__(i, first(out)[:, -1:].detach().clone())))
            handles.append(decoder.self_attn.register_forward_hook(
                lambda m, args, out, i=layer: attn.__setitem__(i, first(out)[:, -1:].detach().clone())))
            handles.append(decoder.register_forward_hook(
                lambda m, args, out, i=layer: dec.__setitem__(i, first(out).detach().clone())))
        lp = full.step(model, ids)
    finally:
        for h in handles: h.remove()
    layers = len(model.model.layers)
    if any(len(d) != layers for d in (hidden, dec, attn, mlp)):
        raise ValueError("Incomplete native query capture")
    if reference is None:
        rs = {}
        def collect(i, h, r, s, y):
            if not torch.equal(y[:, -1:], mlp[i]): raise ValueError("Fresh native component output differs")
            rs[i] = (r[:, -1:].detach().clone(), s[:, -1:].detach().clone())
        with full.fast_blocks(model, collect): fast = full.step(model, ids)
        if not torch.equal(fast, lp): raise ValueError("Full native component capture differs")
        routed = tuple(rs[i][0] for i in range(layers)); shared = tuple(rs[i][1] for i in range(layers))
    else:
        tensors = {k: torch.from_numpy(np.array(reference[k], copy=True)).view(torch.bfloat16).to(device)
                   for k in ("hidden", "routed", "shared", "final_residual")}
        for i in range(layers):
            if not torch.equal(hidden[i], tensors["hidden"][i].view(1, 1, -1)):
                raise ValueError("Last native MLP input differs from preserved v3 trace")
            if not torch.equal(mlp[i], (tensors["routed"][i] + tensors["shared"][i]).view(1, 1, -1)):
                raise ValueError("Preserved component sum differs from native MLP output")
        if not torch.equal(dec[layers-1][:, -1:], tensors["final_residual"].view(1, 1, -1)):
            raise ValueError("Final residual differs from preserved v3 trace")
        routed = tuple(tensors["routed"][i].view(1, 1, -1) for i in range(layers))
        shared = tuple(tensors["shared"][i].view(1, 1, -1) for i in range(layers))
    return Query(ids, lp, routed, shared, tuple(attn[i] for i in range(layers)),
                 tuple(dec[i] for i in range(layers)), dec[layers-1][:, -1:].clone())


@torch.no_grad()
def interchange(model, target, source, component):
    if component == "residual":
        return full.interchange(model, target, source, len(model.model.layers)-1, "residual")
    which = component.removeprefix("zero_")
    zero = component.startswith("zero_")
    if which not in ("R", "S", "RS", "A"): raise ValueError("Unknown whole pathway")
    taps, handles = {}, []
    def collect(layer, hidden, routed, shared, output):
        taps[layer] = (routed[:, -1:], shared[:, -1:])
    try:
        with full.fixed_prefix(model, target):
            for layer, decoder in enumerate(model.model.layers):
                def patch(module, args, output, index=layer):
                    h = first(output).clone()
                    if which == "A": value = torch.zeros_like(source.attention[index]) if zero else source.attention[index]
                    else:
                        current_r, current_s = taps[index]
                        if which == "R": value = (torch.zeros_like(current_r) if zero else source.routed[index]) + current_s
                        elif which == "S": value = current_r + (torch.zeros_like(current_s) if zero else source.shared[index])
                        else: value = torch.zeros_like(current_r) if zero else source.routed[index] + source.shared[index]
                    h[:, -1:] = value
                    return with_first(output, h)
                module = decoder.self_attn if which == "A" else decoder.mlp
                handles.append(module.register_forward_hook(patch))
            with full.fast_blocks(model, collect): return full.step(model, target.ids)
    finally:
        for h in handles: h.remove()


def self_test():
    import e156_loading as loading
    import e144145_common as old
    from e158_engine import replace_forward
    torch.set_num_threads(1)
    records = {}
    for label in ("P", "A", "B"):
        cfg_cls, cls, _ = loading._classes(label, complete=False)
        for dtype in (torch.float32, torch.bfloat16):
            torch.manual_seed(158)
            cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=3,
                          num_attention_heads=2, num_key_value_heads=2, num_experts=4,
                          num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False,
                          max_position_embeddings=32, pad_token_id=63, eos_token_id=62, output_router_logits=False)
            cfg._attn_implementation = "sdpa"
            model = cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            ph, bh = old.tensor_hash(model.state_dict()), old.tensor_hash(dict(model.named_buffers()))
            target = capture(model, np.array([1, 2, 3, 4, 5])); source = capture(model, np.array([1, 7, 8, 5]))
            for path in ("R", "S", "RS", "A"):
                assert torch.equal(interchange(model, target, target, path), target.lp)
                assert torch.isfinite(interchange(model, target, source, path)).all()
                # Independent original-native zero oracle; no fast component taps.
                handles = []
                try:
                    with full.fixed_prefix(model, target), ExitStack() as stack:
                        for decoder in model.model.layers:
                            block = decoder.mlp
                            if path == "A":
                                handles.append(decoder.self_attn.register_forward_hook(
                                    lambda m, a, o: with_first(o, torch.cat((first(o)[:, :-1], torch.zeros_like(first(o)[:, -1:])), dim=1))))
                            else:
                                indices = range(block.num_experts) if path == "RS" else (range(block.num_experts-1) if path == "R" else [block.num_experts-1])
                                for index in indices:
                                    expert = block.experts[index]; original = expert.forward
                                    def last_zero(x, old_forward=original, b=block, expert_index=index):
                                        # Native expert selection order is captured at the gate.
                                        result = old_forward(x).clone()
                                        slots, rows = torch.where(b._whole_test_mask[expert_index])
                                        result[rows == target.ids.shape[1]-1] = 0
                                        return result
                                    stack.enter_context(replace_forward(expert, last_zero))
                                def gate_hook(m, args, logits, b=block):
                                    wr, er = torch.softmax(logits[:, :-1].float(), 1).topk(b.top_k-1, -1)
                                    selected = torch.cat((er, torch.full((len(er),1),b.num_experts-1,device=er.device,dtype=er.dtype)),1)
                                    b._whole_test_mask = torch.nn.functional.one_hot(selected,b.num_experts).permute(2,1,0)
                                handles.append(block.gate.register_forward_hook(gate_hook))
                        expected = full.step(model, target.ids)
                finally:
                    for h in handles: h.remove()
                    for decoder in model.model.layers:
                        if hasattr(decoder.mlp, "_whole_test_mask"): del decoder.mlp._whole_test_mask
                assert torch.equal(interchange(model, target, target, "zero_"+path), expected), (label,dtype,path)
            assert torch.equal(interchange(model, target, source, "residual"), source.lp)
            assert old.tensor_hash(model.state_dict()) == ph and old.tensor_hash(dict(model.named_buffers())) == bh
            assert all("forward" not in d.mlp.__dict__ and not d.mlp._forward_hooks and not d.mlp._forward_pre_hooks
                       and not d.self_attn._forward_hooks and not d._forward_hooks for d in model.model.layers)
            records[label+"/"+str(dtype)] = {"all_four_whole_identities_exact":True,"original_native_zero_oracles_exact":True,
                "different_length_source_residual_exact":True,"source_and_hooks_restored":True}
    return {"status":"passed","CPU_only":True,"records":records}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(),indent=2))
