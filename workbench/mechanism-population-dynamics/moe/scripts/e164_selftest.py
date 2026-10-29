"""CPU actual-native interfaces, causal candidates and known route oracles."""
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

import e150_native as n
import e151_native as removal
import e153_harness as scoring
import e156_loading as loading
from e164_routing import RoutingEngine, permute_trace

ROOT = Path(__file__).resolve().parents[1]/'results/e164'
FILES = ('e164_selftest.py', 'e164_routing.py', 'e150_native.py', 'e150_restricted.py',
         'e151_native.py', 'e153_harness.py', 'e156_loading.py', 'e154_native.py', 'e154_assets.py')


def proof():
    return {name: n.sha(Path(__file__).parent/name) for name in FILES}


def hooks(model):
    return [(len(m._forward_pre_hooks), len(m._forward_hooks)) for m in model.modules()]


@torch.no_grad()
def native_interfaces():
    torch.set_num_threads(1)
    records = []
    sequences = [np.array(v) for v in ([1, 2, 3, 4, 5], [1, 2, 3, 6, 7, 8],
                                      [1, 2, 3, 5], [1, 2, 3, 8, 9])]
    permutation = [2, 0, 3, 1]
    for dtype in (torch.float32, torch.bfloat16):
        models = []
        for i, name in enumerate(('P', 'B')):
            torch.manual_seed(164010+i)
            cfg_cls, cls, _ = loading._classes(name, complete=False)
            cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=2,
                          num_attention_heads=2, num_key_value_heads=2, num_experts=4,
                          num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False,
                          pad_token_id=63, eos_token_id=62, max_position_embeddings=32,
                          attention_dropout=0., output_router_logits=False)
            cfg._attn_implementation = 'eager'
            model = cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            for layer in model.model.layers:
                for expert in layer.mlp.experts:
                    for parameter in expert.parameters():
                        parameter.mul_(3)
            models.append(model)
        blocks = n.original_blocks(models)
        states = [(n.old.tensor_hash(m.state_dict()), n.old.tensor_hash(n.buffers(m)), hooks(m)) for m in models]
        full = np.ones((2, 4), bool)
        partial = np.array([[True, True, False, True]]*2)
        traces, baselines = {}, {}
        for policy, keep in enumerate((full, partial)):
            for r in range(2):
                n.restore(models, blocks); model = n.assemble(models, blocks, (0, 0, r, 0))
                natural, count, first = scoring.score_candidates(model, sequences, 3, 63)
                with RoutingEngine(model) as engine:
                    engine.configure(capture=True)
                    with n.restricted.restricted_gates(model, np.broadcast_to(keep, (4, 2, 4)).copy()):
                        score, counts, prefix = scoring.score_candidates(model, sequences, 3, 63)
                    if policy == 0:
                        assert np.array_equal(score, natural) and torch.equal(prefix, first)
                    assert np.array_equal(counts, count)
                    traces[policy, r] = tuple(engine.captured)
                    baselines[policy, r] = (score, counts, prefix)
            assert torch.equal(traces[policy, 0][0], traces[policy, 1][0])
        differences = []
        for policy, keep in enumerate((full, partial)):
            for r in range(2):
                n.restore(models, blocks); model = n.assemble(models, blocks, (0, 0, r, 0))
                for zero in (False, True) if policy == 0 else (False,):
                    for donor in range(2):
                        with RoutingEngine(model) as engine:
                            engine.configure(trace=traces[policy, donor])
                            with removal.suppress(model, 'shared') if zero else nullcontext():
                                with n.restricted.restricted_gates(model, np.broadcast_to(keep, (4, 2, 4)).copy()):
                                    score, counts, prefix = scoring.score_candidates(model, sequences, 3, 63)
                            if donor == r and not zero:
                                expected = baselines[policy, r]
                                assert np.array_equal(score, expected[0]) and np.array_equal(counts, expected[1])
                                assert torch.equal(prefix, expected[2])
                            if not zero:
                                differences.append(float(np.max(np.abs(score-baselines[policy, r][0]))))
                            engine.configure(trace=permute_trace(traces[policy, donor], permutation, 4))
                            with removal.suppress(model, 'shared') if zero else nullcontext():
                                with n.restricted.restricted_gates(model, np.broadcast_to(keep, (4, 2, 4)).copy()):
                                    permuted, pc, pf = scoring.score_candidates(model, [sequences[i] for i in permutation], 3, 63)
                            assert np.array_equal(permuted, score[permutation]) and np.array_equal(pc, counts[permutation])
                            assert torch.equal(pf, prefix)
        n.restore(models, blocks)
        # Static routing oracle: a bank swap may change predictions, but cannot
        # manufacture a trajectory-source effect when the real gate is constant.
        saved = [layer.mlp.gate.weight.detach().clone() for layer in models[0].model.layers]
        for layer in models[0].model.layers:
            layer.mlp.gate.weight.zero_()
        constant_traces = []
        for r in range(2):
            n.restore(models, blocks); model = n.assemble(models, blocks, (0, 0, r, 0))
            with RoutingEngine(model) as engine:
                engine.configure(capture=True)
                scoring.score_candidates(model, sequences, 3, 63)
                constant_traces.append(tuple(engine.captured))
        assert all(torch.equal(a, b) for a, b in zip(*constant_traces))
        for r in range(2):
            n.restore(models, blocks); model = n.assemble(models, blocks, (0, 0, r, 0))
            scores = []
            for donor in range(2):
                with RoutingEngine(model) as engine:
                    engine.configure(trace=constant_traces[donor])
                    scores.append(scoring.score_candidates(model, sequences, 3, 63)[0])
            assert np.array_equal(*scores)
        n.restore(models, blocks)
        for layer, weight in zip(models[0].model.layers, saved):
            layer.mlp.gate.weight.copy_(weight)
        bad_order_rejected = False
        try:
            with n.restricted.restricted_gates(models[0], np.broadcast_to(partial, (4, 2, 4)).copy()):
                with RoutingEngine(models[0]) as engine:
                    engine.configure(capture=True)
                    scoring.score_candidates(models[0], sequences, 3, 63)
        except ValueError as error:
            bad_order_rejected = 'precede' in str(error)
        assert bad_order_rejected
        n.restore(models, blocks)
        for model, original in zip(models, states):
            assert n.old.tensor_hash(model.state_dict()) == original[0]
            assert n.old.tensor_hash(n.buffers(model)) == original[1]
            assert hooks(model) == original[2]
        records.append({'dtype': str(dtype), 'all_native_diagonals_exact': True,
                        'all_mask_zero_permutation_prefix_count_checks_exact': True,
                        'first_layer_R_source_gate_identity': True, 'constant_gate_no_false_route_effect': True,
                        'wrong_mask_hook_order_rejected': True, 'sources_and_hooks_restored': True,
                        'observed_foreign_trace_score_difference': max(differences)})
    return records


@torch.no_grad()
def known_route_effect():
    # A native SparseMoeBlock with an algebraic output oracle.
    cfg_cls, _, _ = loading._classes('P', complete=False)
    import sys
    module = sys.modules['codex_e154_parent.modeling_emo']
    cfg = cfg_cls(hidden_size=4, intermediate_size=4, num_experts=4, num_experts_per_tok=2,
                  num_shared_experts=1, norm_topk_prob=False)
    block = module.EmoSparseMoeBlock(cfg, 4, 1, None)
    class Constant(nn.Module):
        def __init__(self, value):
            super().__init__(); self.value = value
        def forward(self, x):
            return torch.full_like(x, self.value)
    class FixedGate(nn.Module):
        def forward(self, x):
            return torch.tensor([4., 2., 1., 1.], dtype=x.dtype, device=x.device).log().expand(len(x), -1).clone()
    class Wrapper(nn.Module):
        def __init__(self, b):
            super().__init__(); self.model = nn.Module(); layer = nn.Module(); layer.mlp = b
            self.model.layers = nn.ModuleList([layer])
        def forward(self, x):
            return self.model.layers[0].mlp(x)[0]
    block.gate = FixedGate(); block.experts = nn.ModuleList([Constant(v) for v in [2., 4., 8., 10.]])
    model = Wrapper(block); x = torch.ones(1, 6, 4)
    with RoutingEngine(model) as engine:
        engine.configure(capture=True); base = model(x); trace = tuple(engine.captured)
        alternate = trace[0][:, [2, 0, 1, 3]]
        engine.configure(trace=(alternate,)); changed = model(x)
    assert torch.allclose(base, torch.full_like(base, 10+8/7), atol=2e-6)
    assert torch.allclose(changed, torch.full_like(base, 10+16/7), atol=2e-6)
    return {'status': 'passed', 'native_output': float(base[0, 0, 0]),
            'counterfactual_output': float(changed[0, 0, 0]), 'known_route_intervention_detected': True}


def main():
    torch.set_num_threads(1)
    record = {'status': 'passed', 'CPU_only': True, 'source_sha256': proof(),
              'native_interfaces': native_interfaces(), 'known_route_oracle': known_route_effect(),
              'CUDA_initialized': torch.cuda.is_initialized()}
    assert not record['CUDA_initialized']
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT/'CPU_routing_test.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
