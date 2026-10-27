"""Capture/replay the always-active shared expert output, no weights on import."""
import copy
from contextlib import contextmanager
import torch
from torch import nn


def check(block):
    if block.num_shared_experts != 1 or block.always_active_experts not in (None, []) or block.norm_topk_prob:
        raise ValueError("Requires one always-active last-slot shared expert, coefficient one")


@contextmanager
def capture_shared(model):
    values = [None] * len(model.model.layers)
    handles = []
    try:
        for i, decoder in enumerate(model.model.layers):
            check(decoder.mlp)
            def collect(module, args, output, index=i):
                if values[index] is not None or output.ndim != 2 or output.shape != args[0].shape:
                    raise ValueError("Expected one complete flat shared output per layer")
                values[index] = output.detach().clone()
            handles.append(decoder.mlp.experts[-1].register_forward_hook(collect))
        yield values
        if any(x is None for x in values): raise ValueError("Incomplete shared trajectory")
    finally:
        for handle in handles: handle.remove()


class Replay(nn.Module):
    def __init__(self, value):
        super().__init__()
        self.value = value.detach()
    def forward(self, hidden):
        if hidden.shape != self.value.shape or hidden.dtype != self.value.dtype or hidden.device != self.value.device:
            raise ValueError("Shared replay shape/dtype/device mismatch")
        return self.value.clone()


@contextmanager
def replay_shared(model, values):
    originals = [d.mlp for d in model.model.layers]
    if len(values) != len(originals): raise ValueError("Wrong trajectory layer count")
    try:
        for decoder, original, value in zip(model.model.layers, originals, values):
            check(original)
            block = copy.copy(original)
            block._modules = dict(original._modules)
            block._parameters = dict(original._parameters)
            block._buffers = dict(original._buffers)
            block.experts = nn.ModuleList(list(original.experts[:-1]) + [Replay(value)])
            decoder.mlp = block
        yield
    finally:
        for decoder, original in zip(model.model.layers, originals): decoder.mlp = original


def self_test():
    import numpy as np
    import e156_run as prev
    n, v, h = prev.n, prev.v, prev.h
    torch.set_num_threads(1)
    records = {}
    for dtype in (torch.float32, torch.bfloat16):
        models = []
        for source, label in enumerate(("P", "A", "B")):
            cfg_cls, cls, _ = prev.loading._classes(label, complete=False)
            torch.manual_seed(160 + source)
            cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=3,
                          num_attention_heads=2, num_key_value_heads=2, num_experts=4,
                          num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False,
                          max_position_embeddings=32, pad_token_id=63, eos_token_id=62, output_router_logits=False)
            cfg._attn_implementation = "sdpa"
            model = cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            with torch.no_grad():
                for decoder in model.model.layers:
                    for expert in decoder.mlp.experts[:-1]:
                        for param in expert.parameters(): param.mul_(source + 1)
            models.append(model)
        blocks = n.original_blocks(models)
        before = [n.old.tensor_hash(m.state_dict()) for m in models]
        buffers = [n.old.tensor_hash(n.buffers(m)) for m in models]
        # One candidate avoids CPU SDPA batch-shape rounding in the frozen strict harness.
        seqs = [np.array((1,2,3,4,5,6,7))]
        multi = torch.arange(24, dtype=dtype).reshape(6, 4)
        replay = Replay(multi); original_multi = multi.clone()
        assert torch.equal(replay(torch.zeros_like(multi)), original_multi)
        changed = replay(torch.zeros_like(multi)); changed.zero_()
        assert torch.equal(multi, original_multi) and torch.equal(replay(torch.zeros_like(multi)), original_multi)
        try: replay(torch.zeros((5,4),dtype=dtype))
        except ValueError: pass
        else: raise AssertionError("Replay must reject mismatched multirow shape")
        traces, expected, firsts = [], [], []
        for producer in range(3):
            n.restore(models, blocks); model = n.assemble(models, blocks, (0,0,producer,0))
            with capture_shared(model) as values:
                score, counts, first = h.score_candidates(model, seqs, 4, 63)
            traces.append(tuple(values)); expected.append(score); firsts.append(first)
        if all(torch.equal(traces[0][layer], traces[2][layer]) for layer in range(1,3)):
            raise ValueError("Fixture did not create different shared trajectories")
        trace_hash = [n.old.tensor_hash({str(i): x for i,x in enumerate(t)}) for t in traces]
        fixed_zero = []
        for consumer in range(3):
            zero_shared_reference = None
            for producer in range(3):
                n.restore(models, blocks); model = n.assemble(models, blocks, (0,0,consumer,0))
                with replay_shared(model, traces[producer]):
                    score, counts, first = h.score_candidates(model, seqs, 4, 63)
                    if consumer == producer:
                        assert np.array_equal(score, expected[consumer]) and torch.equal(first, firsts[consumer])
                    with v.suppress(model, "routed"):
                        zero_score, _, zero_first = h.score_candidates(model, seqs, 4, 63)
                    with v.suppress(model, "shared"):
                        zero_shared, _, zero_shared_first = h.score_candidates(model, seqs, 4, 63)
                    if producer == 0: zero_shared_reference = (zero_shared, zero_shared_first)
                    else: assert np.array_equal(zero_shared, zero_shared_reference[0]) and torch.equal(zero_shared_first, zero_shared_reference[1])
                    if consumer == 0: fixed_zero.append((zero_score,zero_first))
                    else: assert np.array_equal(zero_score,fixed_zero[producer][0]) and torch.equal(zero_first,fixed_zero[producer][1])
        n.restore(models, blocks)
        assert [n.old.tensor_hash({str(i): x for i,x in enumerate(t)}) for t in traces] == trace_hash
        assert [n.old.tensor_hash(m.state_dict()) for m in models] == before
        assert [n.old.tensor_hash(n.buffers(m)) for m in models] == buffers
        assert all(d.mlp is blocks[i][j] and not d.mlp.experts[-1]._forward_hooks
                   for i,m in enumerate(models) for j,d in enumerate(m.model.layers))
        records[str(dtype)] = {"three_original_native_implementations":True,"different_producer_signals":True,
            "all_diagonal_scores_and_first_distributions_exact":True,"zero_R_consumer_source_collapse":True,
            "zero_S_producer_source_collapse":True,"single_candidate_fixture_no_multi_candidate_causal_check":True,
            "multirow_replay_shape_and_immutability":True,"cache_and_source_restored":True}
    return {"status":"passed","CPU_only":True,"records":records}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(),indent=2))
