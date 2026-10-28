"""Independent algebraic oracles and actual native tiny-interface controls."""
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
import e150_native as n
import e151_native as removal
import e156_loading as loading
import e153_harness as scoring
from e163_geometry import GeometryEngine, TARGETS, replace_message
from e163_metrics import first_token_KL


def KL_reduction():
    torch.manual_seed(163)
    a=torch.randn(100352).log_softmax(-1)
    b=(torch.randn(100352)*3).log_softmax(-1)
    product=(a.exp()*(a-b)).numpy()
    expected=float(product.astype(np.float64).sum())
    actual=first_token_KL(a,b)
    old_wrong=float(torch.from_numpy(product).sum())
    assert abs(actual-expected)<1e-12 and abs(old_wrong-expected)>1e-10
    assert first_token_KL(a,a)==0.
    return {'status':'passed','vocabulary':100352,'oracle':'FP32 products, independent NumPy FP64 reduction',
            'corrected_absolute_error':abs(actual-expected),'rejected_FP32_sum_absolute_error':abs(old_wrong-expected)}


def algebra():
    generator = np.random.default_rng(163)
    x, b, d = (generator.normal(size=(9, 32)) for _ in range(3))
    x[0] = 0
    b[1] = 0
    d[2] = 0
    d[3] = b[3]
    records = {}
    for dtype in (torch.float32, torch.float64):
        value, witness = replace_message(torch.tensor(x, dtype=dtype), torch.tensor(b, dtype=dtype),
                                         torch.tensor(d, dtype=dtype), 'gram')
        v = value.numpy()
        radius = np.linalg.norm(x, axis=-1)
        norm_error = np.max(np.abs(np.linalg.norm(v, axis=-1) - radius))
        projection_error = np.max(np.abs((v*b).sum(-1) - (x*b).sum(-1)))
        residual_error = np.max(np.abs(np.linalg.norm(v+b, axis=-1) - np.linalg.norm(x+b, axis=-1)))
        limit = 3e-5 if dtype == torch.float32 else 1e-11
        assert max(norm_error, projection_error, residual_error) < limit
        assert torch.isfinite(value).all() and witness['fallback'][2] and witness['fallback'][3]
        assert np.array_equal(v[0], np.zeros(32))
        # Original angular structure may differ while the two witnesses agree.
        u = torch.tensor([[1., 2., 0., 0.], [1., 0., 2., 0.]], dtype=dtype)
        base = torch.tensor([[1., 0., 0., 0.]]*2, dtype=dtype)
        proposal = torch.tensor([0., 1., 1., 1.], dtype=dtype)
        proxy, _ = replace_message(u, base, proposal, 'gram')
        assert torch.equal(proxy[0], proxy[1])
        identical, _ = replace_message(u, base, u.clone(), 'gram')
        assert torch.equal(identical, u), 'Equality must not depend on tensor aliasing'
        records[str(dtype)] = {'max_norm_error': float(norm_error), 'max_projection_error': float(projection_error),
                               'max_residual_norm_error': float(residual_error),
                               'zero_and_parallel_fallbacks': True, 'only_two_message_witnesses_used': True}
    return records


@torch.no_grad()
def native_interfaces():
    torch.set_num_threads(1)
    result = {}
    for label in ('P', 'A', 'B'):
        cfg_cls, cls, _ = loading._classes(label, complete=False)
        for dtype in (torch.float32, torch.bfloat16):
            torch.manual_seed(163)
            cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=2,
                          num_attention_heads=2, num_key_value_heads=2, num_experts=4,
                          num_experts_per_tok=2, num_shared_experts=1, norm_topk_prob=False,
                          pad_token_id=63, eos_token_id=62, max_position_embeddings=32,
                          attention_dropout=0., output_router_logits=False)
            cfg._attn_implementation = 'eager'
            model = cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            for decoder in model.model.layers:
                for expert in decoder.mlp.experts:
                    for parameter in expert.parameters():
                        parameter.mul_(3)
            ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14]])
            attention = torch.ones_like(ids, dtype=torch.bool)
            state = n.old.tensor_hash(model.state_dict())
            buffers = n.old.tensor_hash(n.buffers(model))
            native = n.fwd(model, ids, attention)
            zero_references = {}
            for target in TARGETS:
                with ExitStack() as stack:
                    if target in ('R', 'RS'):
                        stack.enter_context(removal.suppress(model, 'routed'))
                    if target in ('S', 'RS'):
                        stack.enter_context(removal.suppress(model, 'shared'))
                    zero_references[target] = n.fwd(model, ids, attention)
            with GeometryEngine(model) as engine:
                engine.configure(capture=True)
                actual = n.fwd(model, ids, attention)
                assert torch.equal(actual, native), (label, dtype, 'native')
                captured = {key: tuple(value) for key, value in engine.captured.items()}
                means = {key: torch.stack([v.float().mean((0, 1)) for v in value]) for key, value in captured.items()}
                assert engine.last_native_geometry.shape == (3, 2, 3)
                for target in TARGETS:
                    engine.configure(target, 'zero')
                    assert torch.equal(n.fwd(model, ids, attention), zero_references[target]), (label, dtype, target)
                    for mode in ('norm', 'gram'):
                        engine.configure(target, mode, means[target], probes=True)
                        changed = n.fwd(model, ids, attention)
                        assert torch.isfinite(changed).all() and engine.last_diagnostics.shape == (2, 9)
                        assert engine.probes
                engine.configure('S', 'raw', directions=captured['S'], witnesses=captured['S'])
                assert torch.equal(n.fwd(model, ids, attention), native), 'Own complete trajectory replay failed'
                # Geometry correction with a real same-input source also restores its own trajectory.
                for mode in ('norm', 'gram'):
                    engine.configure('S', mode, directions=captured['S'], witnesses=captured['S'])
                    current = n.fwd(model, ids, attention)
                    assert torch.equal(current, native), 'Geometric identity failed'
            assert n.old.tensor_hash(model.state_dict()) == state
            assert n.old.tensor_hash(n.buffers(model)) == buffers
            assert not any(module._forward_hooks or module._forward_pre_hooks for module in model.modules())
            result[label+'/'+str(dtype)] = {'native_program_exact': True, 'three_original_zero_oracles_exact': True,
                'norm_and_Gram_finite_and_geometry_checked': True, 'raw_own_signal_replay_exact': True,
                'geometric_own_signal_replay_exact': True,
                'source_parameters_buffers_hooks_restored': True}
    return result


@torch.no_grad()
def cross_interface():
    models=[]
    for i,label in enumerate(('P','A','B')):
        cfg_cls,cls,_=loading._classes(label,complete=False)
        cfg=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,
            num_attention_heads=2,num_key_value_heads=2,num_experts=4,num_experts_per_tok=2,
            num_shared_experts=1,norm_topk_prob=False,pad_token_id=63,eos_token_id=62,
            max_position_embeddings=32,attention_dropout=0.,output_router_logits=False)
        cfg._attn_implementation='eager';torch.manual_seed(163+i)
        model=cls(cfg).bfloat16().eval().requires_grad_(False)
        for decoder in model.model.layers:
            for expert in decoder.mlp.experts:
                for parameter in expert.parameters():parameter.mul_(3)
        models.append(model)
    before=[n.old.tensor_hash(m.state_dict()) for m in models]
    blocks=n.original_blocks(models)
    seqs=[np.array(v) for v in ((1,2,3,4),(1,2,3,5,6),(1,2,3,7),(1,2,3,8,9,10))]
    traces=[];native=[]
    for producer in range(3):
        n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,producer,0))
        with GeometryEngine(model) as engine:
            engine.configure(capture=True)
            values,counts,first=scoring.score_candidates(model,seqs,3,63,check_causal=True)
            traces.append(tuple(engine.captured['S']));native.append((values,counts,first))
    cells=0;perm=[2,0,3,1]
    for consumer in range(3):
        n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,consumer,0))
        with GeometryEngine(model) as engine:
            for producer in range(3):
                for rule in ('raw','norm','gram'):
                    engine.configure('S',rule,directions=traces[producer],witnesses=traces[consumer])
                    values,counts,first=scoring.score_candidates(model,seqs,3,63,check_causal=True)
                    assert np.array_equal(counts,[1,2,1,3])
                    if producer==consumer:
                        assert np.array_equal(values,native[consumer][0]) and torch.equal(first,native[consumer][2])
                    engine.configure('S',rule,directions=tuple(u[perm] for u in traces[producer]),witnesses=tuple(u[perm] for u in traces[consumer]))
                    ps,pc,pf=scoring.score_candidates(model,[seqs[i] for i in perm],3,63,check_causal=True)
                    assert np.array_equal(ps,values[perm]) and np.array_equal(pc,counts[perm]) and torch.equal(pf,first)
                    cells+=1
    n.restore(models,blocks)
    assert before==[n.old.tensor_hash(m.state_dict()) for m in models]
    assert not any(module._forward_hooks or module._forward_pre_hooks for m in models for module in m.modules())
    return {'status':'passed','actual_three_source_cross_cells':cells,'padded_multitoken_prefix_and_counts':True,
            'all_diagonal_and_permutation_checks_exact':True,'source_state_hooks_restored':True}


def main():
    report = {'status': 'passed', 'CPU_only': True, 'KL_reduction':KL_reduction(), 'algebra': algebra(), 'native_interfaces': native_interfaces(),
              'cross_interface':cross_interface()}
    root = Path(__file__).resolve().parents[1]/'results/e163'
    root.mkdir(exist_ok=True)
    report['source_sha256'] = {name: hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                         for name in ('e163_geometry.py', 'e163_selftest.py','e163_metrics.py')}
    (root/'CPU_geometry_test.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'status': 'passed', 'CPU_only': True, 'native_source_dtype_cases': len(report['native_interfaces'])}))


if __name__ == '__main__':
    main()
