"""E122: symmetric formation policies, two owners, inferred criterion x code.

Compare formation-time relational isolation with query-time positional isolation.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD
from e118_criterion_code_feature_crossing import WORLDS, interval

POLICIES = ['normal', 'answer_cross_off', 'all_cross_off']


def truth(ctx, world, owner):
    food = np.asarray([(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']])
    if owner == 0:
        return food.tolist()
    gold = np.asarray(ctx['service_gold']) if world in ['origin', 'service_negative'] else food
    if world.endswith('negative'):
        gold = -gold
    return gold.tolist()


def analyze(dest):
    rows = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    z = {k: np.asarray([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    out = {'n_contexts': len(rows), 'conditions': {}, 'policy_accuracy': {}, 'contrasts': {}, 'A_code_responses': {}}
    for key, value in z.items():
        gold = np.asarray([r['conditions'][key]['gold'] for r in rows])
        out['conditions'][key] = {'candidate_accuracy': interval(((value > 0) == (gold > 0)).mean(1)),
            'argmax_accuracy': interval([np.mean(r['conditions'][key]['argmax_correct']) for r in rows]),
            'correct_label_margin': interval((value * gold).mean(1))}
    ga = np.asarray([truth(c, 'origin', 0) for c in cs])
    gs = np.asarray([c['service_gold'] for c in cs])
    gb = {w: np.asarray([truth(c, w, 1) for c in cs]) for w in WORLDS}
    disagreement = np.stack([ga != gb[w] for w in WORLDS], 1)[:, :, None, :]
    disagreement = np.repeat(disagreement, 2, axis=2)
    assert np.all(disagreement.sum((1, 2, 3)) == 32)
    assert np.all((~disagreement).sum((1, 2, 3)) == 32)
    aggregates = {}
    for policy in POLICIES:
        for scope in ['native', 'gate']:
            values = np.stack([np.stack([((z[f'{w}_{policy}_{scope}_{owner}'] > 0)
                == ((ga if owner == 0 else gb[w]) > 0)) for owner in [0, 1]], 1) for w in WORLDS], 1)
            summary = {'both': values.mean((1, 2, 3)), 'A': values[:, :, 0].mean((1, 2)),
                'B': values[:, :, 1].mean((1, 2)),
                'agree': (values * ~disagreement).sum((1, 2, 3)) / 32,
                'disagree': (values * disagreement).sum((1, 2, 3)) / 32}
            aggregates[policy, scope] = summary
            out['policy_accuracy'][f'{policy}_{scope}'] = {k: interval(v) for k, v in summary.items()}
            p = np.asarray([-1 if c['reverse'] else 1 for c in cs])[:, None]
            responses = {}
            for task, positive, negative in [('food', 'food_positive', 'food_negative'),
                                               ('service', 'origin', 'service_negative')]:
                difference = .5 * (z[f'{positive}_{policy}_{scope}_0'] - z[f'{negative}_{policy}_{scope}_0'])
                responses[task] = {name: interval((difference * feature).mean(1)) for name, feature in [
                    ('bias', p), ('food', ga), ('service', gs), ('food_service', ga * gs * p)]}
            out['A_code_responses'][f'{policy}_{scope}'] = responses
    for scope in ['native', 'gate']:
        for policy in POLICIES[1:]:
            out['contrasts'][f'{policy}_minus_normal_{scope}'] = {k: interval(aggregates[policy, scope][k]
                - aggregates['normal', scope][k]) for k in aggregates['normal', scope]}
        out['contrasts'][f'answer_minus_all_{scope}'] = {k: interval(aggregates['answer_cross_off', scope][k]
            - aggregates['all_cross_off', scope][k]) for k in aggregates['normal', scope]}
    for policy in POLICIES:
        out['contrasts'][f'query_isolation_{policy}'] = {k: interval(aggregates[policy, 'gate'][k]
            - aggregates[policy, 'native'][k]) for k in aggregates[policy, 'native']}
    out['contrasts']['answer_by_query_interaction'] = {k: interval(
        aggregates['answer_cross_off', 'gate'][k] - aggregates['normal', 'gate'][k]
        - aggregates['answer_cross_off', 'native'][k] + aggregates['normal', 'native'][k])
        for k in aggregates['normal', 'native']}
    (dest / 'analysis.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'n_contexts': len(rows), 'both_actor_accuracy': {k: v['both'] for k, v in out['policy_accuracy'].items()}}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=122001)
    ap.add_argument('--materials', choices=['discovery', 'validation'], default='discovery')
    ap.add_argument('--preflight-only', action='store_true')
    ap.add_argument('--analyze-only', action='store_true')
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / 'behavior.jsonl').exists()
    generator = 'e118_mistral_materials.py' if 'Mistral' in args.model else 'e119_criterion_scale.py'
    material = dest / 'materials'
    subprocess.run([sys.executable, str(Path(__file__).with_name(generator)), '--model', args.model,
        '--out', str(material), '--n', str(args.n), '--seed', str(args.seed), '--materials', args.materials,
        '--preflight-only'], check=True)
    (dest / 'contexts.jsonl').write_bytes((material / 'contexts.jsonl').read_bytes())
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    assert all(len(enc(' ' + w)) == 1 for w in ['no', 'yes'])
    label_ids = [enc(' ' + w)[0] for w in ['no', 'yes']]

    def prefix(ctx, world, single=None, instruction=False):
        header = HEAD + ("Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n" if instruction else '')
        ids, roles = enc(header), [-1] * len(enc(header))
        labels, answers = [], [[], []]
        for (comment, role, y), name in zip(ctx['demos'], ctx['shown']):
            if single is not None and role != single:
                continue
            if role == 1 and world != 'origin':
                comment = ctx[world + '_map'][comment]
            block = enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            anchor = len(ids) + len(block)
            answer = enc(' ' + ['no', 'yes'][y]) + enc('\n\n')
            labels.append(anchor)
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
        return ids, roles, labels, answers

    encoded = [{w: prefix(c, w) for w in WORLDS} for c in cs]
    for worlds in encoded:
        reference = worlds['origin']
        for value in worlds.values():
            assert len(value[0]) == len(reference[0]) and value[1:] == reference[1:]
    (dest / 'preflight.json').write_text(json.dumps({'args': vars(args), 'conditions': 61,
        'policies': POLICIES, 'worlds': WORLDS, 'owners': [0, 1], 'matched_geometry': True,
        'prefix_lengths': [len(w['origin'][0]) for w in encoded], 'source_generator': generator,
        'shared_prefix_for_both_owners': True, 'disagree_observations_per_context': 32,
        'scope': 'fixed aspect order, controlled source criterion and convention'}, indent=2) + '\n')
    if args.preflight_only:
        print('E122 both-owner truth and matched geometry passed.', flush=True)
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        dtype=torch.float32, device_map='cuda', attn_implementation='eager').eval()
    model.requires_grad_(False)
    numeric, self_errors, graph_zero, consumption = [], [], [], {}

    def prefill(data, policy, record=None):
        ids, roles, labels, answers = data
        length = len(ids)
        allowed = torch.ones((length, length), dtype=torch.bool, device='cuda').tril()
        counts = {}
        for owner in [0, 1]:
            receivers = [a for a in labels if roles[a] == owner] if policy == 'answer_cross_off' else [i for i, r in enumerate(roles) if r == owner]
            senders = answers[1 - owner] if policy == 'answer_cross_off' else [i for i, r in enumerate(roles) if r == 1 - owner]
            rr = torch.tensor(receivers, device='cuda', dtype=torch.long)
            ss = torch.tensor(senders, device='cuda', dtype=torch.long)
            counts[str(owner)] = 0
            if policy != 'normal' and len(rr) and len(ss):
                past = ss[None, :] < rr[:, None]
                counts[str(owner)] = int((allowed[rr[:, None], ss[None, :]] & past).sum())
                allowed[rr[:, None], ss[None, :]] &= ~past
        mask = torch.zeros((1, 1, length, length), dtype=torch.float32, device='cuda').masked_fill_(~allowed, float('-inf'))
        handles = []
        if record is not None:
            def hook(module, aa, kw):
                assert kw['attention_mask'].shape == mask.shape and torch.equal(kw['attention_mask'], mask)
                k = module.layer_idx
                record[k] = record.get(k, 0) + 1
            handles = [layer.self_attn.register_forward_pre_hook(hook, with_kwargs=True) for layer in model.model.layers]
        try:
            cache = model(input_ids=torch.tensor([ids], device='cuda'), attention_mask=mask,
                use_cache=True, logits_to_keep=1).past_key_values
        finally:
            for h in handles:
                h.remove()
        return cache, counts

    def query(cache, roles, queries, owner, gate):
        plen, n, qlen = len(roles), len(queries), max(map(len, queries))
        ids = torch.zeros((n, qlen), dtype=torch.long, device='cuda')
        positions = torch.zeros_like(ids)
        live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i, -len(q):] = torch.tensor(q, device='cuda')
            positions[i, -len(q):] = torch.arange(plen, plen + len(q), device='cuda')
            live[i, -len(q):] = True
        keep = torch.tensor(roles, device='cuda') != 1 - owner if gate else torch.ones(plen, dtype=torch.bool, device='cuda')
        allowed = torch.cat([keep[None, None].expand(n, qlen, -1),
            live[:, None].expand(-1, qlen, -1) & torch.ones((qlen, qlen), dtype=torch.bool, device='cuda').tril()[None]], -1)
        mask = torch.zeros(allowed.shape, dtype=torch.float32, device='cuda').masked_fill_(~allowed, float('-inf'))
        cp = copy.deepcopy(cache)
        assert all(a.keys.data_ptr() != b.keys.data_ptr() and a.values.data_ptr() != b.values.data_ptr() for a, b in zip(cp.layers, cache.layers))
        cp.batch_repeat_interleave(n)
        logits = model(input_ids=ids, position_ids=positions, attention_mask=mask[:, None], past_key_values=cp,
            use_cache=True, logits_to_keep=1).logits[:, -1].float()
        assert cache.get_seq_length() == plen
        top = logits.argmax(-1)
        return {'z': (logits[:, label_ids[1]] - logits[:, label_ids[0]]).cpu().tolist(),
                'argmax_token': top.cpu().tolist(), 'argmax_is_label': ((top == label_ids[0]) | (top == label_ids[1])).cpu().tolist()}

    with torch.inference_mode(), (dest / 'behavior.jsonl').open('w') as stream:
        for ci, ctx in enumerate(cs):
            queries = {owner: [enc(f"Comment: {t}\nAnnotator: {ctx['names'][owner]}\nLabel:") for t, _ in ctx['q']] for owner in [0, 1]}
            conditions, edge_counts = {}, {}
            def score(name, cache, roles, world, owner, gate=False):
                value = query(cache, roles, queries[owner], owner, gate)
                value['gold'] = truth(ctx, world, owner)
                value['argmax_correct'] = [t == label_ids[int(g > 0)] for t, g in zip(value['argmax_token'], value['gold'])]
                conditions[name] = value
            for world in WORLDS:
                data = encoded[ci][world]
                for policy in POLICIES:
                    name = world + '_' + policy
                    cache, edge_counts[name] = prefill(data, policy, consumption.setdefault(name, {}))
                    for scope in ['native', 'gate']:
                        for owner in [0, 1]:
                            score(f'{name}_{scope}_{owner}', cache, data[1], world, owner, scope == 'gate')
                    if ci == 0 and world == 'origin' and policy == 'normal':
                        default = model(input_ids=torch.tensor([data[0]], device='cuda'), use_cache=True, logits_to_keep=1).past_key_values
                        self_errors.append(max(float((getattr(a, k) - getattr(b, k)).abs().max()) for a, b in zip(cache.layers, default.layers) for k in ['keys', 'values']))
                        for owner in [0, 1]:
                            for qi, q in enumerate(queries[owner]):
                                logits = model(input_ids=torch.tensor([data[0] + q], device='cuda'), use_cache=False, logits_to_keep=1).logits[0, -1].float()
                                numeric.append(abs(float(logits[label_ids[1]] - logits[label_ids[0]]) - conditions[f'{name}_native_{owner}']['z'][qi]))
                        del default
                    del cache
            for world in WORLDS[1:]:
                left = conditions[f'{world}_all_cross_off_gate_0']['z']
                right = conditions['origin_all_cross_off_gate_0']['z']
                graph_zero.append(max(abs(a - b) for a, b in zip(left, right)))
            for owner in [0, 1]:
                for world in (['origin'] if owner == 0 else WORLDS):
                    data = prefix(ctx, world, single=owner)
                    cache, _ = prefill(data, 'normal')
                    score('single_A' if owner == 0 else 'single_B_' + world, cache, data[1], world, owner)
                    if ci == 0 and world == 'origin':
                        for policy in POLICIES[1:]:
                            no_op, counts = prefill(data, policy)
                            assert counts == {'0': 0, '1': 0}
                            self_errors.append(max(float((getattr(a, k) - getattr(b, k)).abs().max())
                                for a, b in zip(cache.layers, no_op.layers) for k in ['keys', 'values']))
                            del no_op
            for world in WORLDS:
                data = prefix(ctx, world, instruction=True)
                cache, _ = prefill(data, 'normal')
                for owner in [0, 1]:
                    score(f'{world}_instruction_{owner}', cache, data[1], world, owner)
            assert len(conditions) == 61
            assert max(numeric) <= .001 and max(self_errors) <= .001 and max(graph_zero) <= .001
            stream.write(json.dumps({'context': ci, 'conditions': conditions, 'edge_counts': edge_counts}) + '\n')
            stream.flush()
            print(ci + 1, '/', args.n, 'numeric', max(numeric), 'graph_zero', max(graph_zero), flush=True)
    assert all(set(v) == set(range(len(model.model.layers))) and set(v.values()) == {args.n} for v in consumption.values())
    elapsed = time.time() - started
    revision = {'qwen3': '40c069824f4251a91eefaf281ebe4c544efd3e18' if model.config.num_hidden_layers == 40 else 'b968826d9c46dd6066d109eabc6255188de91218',
        'mistral': 'caa1feb0e54d415e2df31207e5f4e273e33509b1', 'llama': '1f47e50cdbe801ad8a5174156ec3a0655108fb9f'}[model.config.model_type]
    (dest / 'run.json').write_text(json.dumps({'args': vars(args), 'model_revision': revision, 'model_type': model.config.model_type,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256': hashlib.sha256((dest / 'contexts.jsonl').read_bytes()).hexdigest(),
        'numeric_max_error': max(numeric), 'native_mask_cache_max_error': max(self_errors), 'graph_zero_max_error': max(graph_zero),
        'all_layer_consumption': consumption, 'num_layers': len(model.model.layers), 'training': False,
        'dtype': 'float32', 'attention': 'eager', 'pristine_cache_scope': 'deepcopy data_ptr and sequence length checked',
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600}, indent=2) + '\n')
    analyze(dest)


if __name__ == '__main__':
    main()
