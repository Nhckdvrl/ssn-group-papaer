"""E158 cached single-position component interchange; no checkpoint loaded on import."""
import copy
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import numpy as np
import torch
from torch.nn import functional as F


def first(output):
    return output[0] if isinstance(output, (tuple, list)) else output


def with_first(output, hidden):
    if isinstance(output, tuple):
        return (hidden,) + output[1:]
    if isinstance(output, list):
        return [hidden] + output[1:]
    return hidden


def cache_length(cache):
    return int(cache.get_seq_length())


def cache_hash(cache):
    """Only for small preflight tests, never repeated in the intervention loop."""
    d = hashlib.sha256()
    for pair in cache.to_legacy_cache():
        for tensor in pair:
            d.update(tensor.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return d.hexdigest()


@contextmanager
def replace_forward(module, function):
    present = "forward" in module.__dict__
    old = module.__dict__.get("forward")
    module.forward = function
    try:
        yield
    finally:
        if present:
            module.forward = old
        else:
            del module.forward


def single_token(block, hidden, original, layer, tap):
    """Native arithmetic/order, skipping only experts with empty input.

    Callers validate against unmodified cached native execution for every query.
    """
    if hidden.shape[0] * hidden.shape[1] != 1:
        return original(hidden)
    if block.num_shared_experts != 1 or block.always_active_experts not in (None, []) or block.norm_topk_prob:
        raise ValueError("Expected the audited 127 routed + last shared interface")
    batch, length, dim = hidden.shape
    flat = hidden.view(-1, dim)
    logits = block.gate(flat)
    wr = F.softmax(logits[:, :-1], dim=1, dtype=torch.float)
    ws = F.softmax(logits[:, -1:], dim=1, dtype=torch.float)
    wr, er = torch.topk(wr, block.top_k - 1, dim=-1)
    ws, es = torch.topk(ws, 1, dim=-1)
    weights = torch.cat((wr, ws), 1).to(flat.dtype)
    selected = torch.cat((er, es + block.num_experts - 1), 1)
    mask = F.one_hot(selected, num_classes=block.num_experts).permute(2, 1, 0)
    result = torch.zeros((1, dim), dtype=flat.dtype, device=flat.device)
    routed, shared = None, None
    for expert in sorted(set(selected.reshape(-1).tolist())):
        idx, top_x = torch.where(mask[expert])
        if expert == block.num_experts - 1:
            routed = result.clone()
        state = flat[None, top_x].reshape(-1, dim)
        contribution = block.experts[expert](state) * weights[top_x, idx, None]
        if expert == block.num_experts - 1:
            shared = contribution.to(flat.dtype).clone()
        result.index_add_(0, top_x, contribution.to(flat.dtype))
    if routed is None or shared is None:
        raise ValueError("Expected always-selected shared expert")
    result = result.reshape(batch, length, dim)
    routed, shared = routed.reshape_as(result), shared.reshape_as(result)
    if not torch.equal(routed + shared, result):
        raise ValueError("Tapped components do not exactly reconstruct native addition")
    if tap is not None:
        tap(layer, hidden, routed, shared, result)
    return result, logits


@contextmanager
def fast_blocks(model, tap=None):
    contexts = []
    try:
        for layer, decoder in enumerate(model.model.layers):
            block = decoder.mlp
            original = block.forward
            def wrapped(hidden, b=block, old=original, index=layer):
                return single_token(b, hidden, old, index, tap)
            context = replace_forward(block, wrapped)
            context.__enter__()
            contexts.append(context)
        yield
    finally:
        for context in reversed(contexts):
            context.__exit__(None, None, None)


@dataclass
class Query:
    ids: torch.Tensor
    prefix_cache: object
    lp: torch.Tensor
    uncached_lp: torch.Tensor
    hidden: tuple
    routed: tuple
    shared: tuple
    mlp_output: tuple
    final_residual: torch.Tensor
    uncached_to_cached_KL: float
    uncached_gold_logprob_difference: float
    uncached_greedy: int


@torch.no_grad()
def step(model, ids, prefix_cache):
    length = ids.shape[1]
    if cache_length(prefix_cache) != length - 1:
        raise ValueError("Wrong immutable prefix cache length")
    copied = copy.deepcopy(prefix_cache)
    position = torch.tensor([length - 1], dtype=torch.long, device=ids.device)
    out = model(input_ids=ids[:, -1:], attention_mask=torch.ones_like(ids),
                past_key_values=copied, position_ids=position[None], cache_position=position,
                use_cache=True, return_dict=True, output_router_logits=False)
    lp = out.logits[0, -1].float().log_softmax(-1)
    if cache_length(prefix_cache) != length - 1 or cache_length(copied) != length:
        raise ValueError("Prefix cache mutation or incorrect append")
    del out, copied
    return lp


@torch.no_grad()
def capture(model, token_ids, gold_token):
    device = next(model.parameters()).device
    ids = torch.as_tensor(np.asarray(token_ids).copy(), dtype=torch.long, device=device)[None]
    if ids.shape[1] < 2:
        raise ValueError("Need a nonempty prefix and final input token")
    uncached = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False,
                     return_dict=True, output_router_logits=False).logits[0, -1].float().log_softmax(-1)
    prefix = model(input_ids=ids[:, :-1], attention_mask=torch.ones_like(ids[:, :-1]), use_cache=True,
                   return_dict=True, output_router_logits=False).past_key_values
    native_y, final, handles = {}, [], []
    try:
        for layer, decoder in enumerate(model.model.layers):
            handles.append(decoder.mlp.register_forward_hook(
                lambda m, args, out, index=layer: native_y.__setitem__(index, first(out).detach().clone())))
        handles.append(model.model.layers[-1].register_forward_hook(
            lambda m, args, out: final.append(first(out).detach().clone())))
        reference = step(model, ids, prefix)
    finally:
        for handle in handles:
            handle.remove()
    if len(native_y) != len(model.model.layers) or len(final) != 1:
        raise ValueError("Incomplete native layer capture")
    taps = {}
    def collect(layer, hidden, routed, shared, output):
        taps[layer] = tuple(x.detach().clone() for x in (hidden, routed, shared, output))
    with fast_blocks(model, collect):
        actual = step(model, ids, prefix)
    if not torch.equal(actual, reference):
        raise ValueError("Empty-expert skipping changed cached native distribution")
    for layer, (_, _, _, output) in taps.items():
        if not torch.equal(output, native_y[layer]):
            raise ValueError("Empty-expert skipping changed a native MLP output")
    if len(taps) != len(native_y):
        raise ValueError("Incomplete single-token component taps")
    kl = float((uncached.exp() * (uncached - reference)).double().sum())
    gold_difference = float(reference[int(gold_token)] - uncached[int(gold_token)])
    greedy = int(uncached.argmax())
    ordered = [taps[i] for i in range(len(taps))]
    return Query(ids, prefix, reference, uncached, tuple(v[0] for v in ordered), tuple(v[1] for v in ordered),
                 tuple(v[2] for v in ordered), tuple(v[3] for v in ordered), final[0], kl,
                 gold_difference, greedy)


@torch.no_grad()
def routed_native_identity(model, query):
    """Check direct taps against original S-zero blocks at the identical hidden input."""
    for layer, decoder in enumerate(model.model.layers):
        block = decoder.mlp
        shared = block.experts[-1]
        with replace_forward(shared, lambda x: torch.zeros_like(x)):
            result = first(block(query.hidden[layer]))
        if not torch.equal(result, query.routed[layer]):
            raise ValueError("Direct routed tap differs from the native S-zero block")


@torch.no_grad()
def interchange(model, target, source, layer, component):
    if component == "R":
        replacement = source.routed[layer] + target.shared[layer]
        module = model.model.layers[layer].mlp
    elif component == "S":
        replacement = target.routed[layer] + source.shared[layer]
        module = model.model.layers[layer].mlp
    elif component == "RS":
        replacement = source.routed[layer] + source.shared[layer]
        module = model.model.layers[layer].mlp
    elif component == "residual":
        if layer != len(model.model.layers) - 1:
            raise ValueError("Only the preregistered final residual positive control")
        replacement = source.final_residual
        module = model.model.layers[layer]
    else:
        raise ValueError("Unknown interchange component")
    handle = module.register_forward_hook(lambda m, args, out: with_first(out, replacement))
    try:
        with fast_blocks(model):
            return step(model, target.ids, target.prefix_cache)
    finally:
        handle.remove()


def self_test():
    import e156_loading as loading
    import e144145_common as old
    torch.set_num_threads(1)
    records = {}
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
            before = old.tensor_hash(model.state_dict())
            buffers = old.tensor_hash(dict(model.named_buffers()))
            target = capture(model, np.array([1, 2, 3, 4, 5]), 6)
            source = capture(model, np.array([1, 2, 7, 8, 5]), 9)
            prefix_hash = cache_hash(target.prefix_cache)
            routed_native_identity(model, target)
            identities = 0
            for layer in range(2):
                for component in ("R", "S", "RS"):
                    identity = interchange(model, target, target, layer, component)
                    assert torch.equal(identity, target.lp)
                    changed = interchange(model, target, source, layer, component)
                    assert torch.isfinite(changed).all()
                    identities += 1
            positive = interchange(model, target, source, 1, "residual")
            assert torch.equal(positive, source.lp)
            assert cache_hash(target.prefix_cache) == prefix_hash
            assert old.tensor_hash(model.state_dict()) == before
            assert old.tensor_hash(dict(model.named_buffers())) == buffers
            assert all("forward" not in d.mlp.__dict__ and not d.mlp._forward_hooks and not d._forward_hooks
                       for d in model.model.layers)
            records[label + "/" + str(dtype)] = {"component_identities": identities,
                "final_residual_source_distribution_exact": True, "immutable_prefix_and_source": True,
                "uncached_to_cached_KL": target.uncached_to_cached_KL}
    return {"status": "passed", "CPU_only": True, "native_implementations_and_precisions": records}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
