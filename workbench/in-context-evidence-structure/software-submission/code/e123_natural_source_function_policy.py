"""E123: native source-function formation policies on real SST5, output namespace crossing.

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
from e118_criterion_code_feature_crossing import interval
from e121_sst_materials import make_contexts

WORLDS = ['origin', 'cross', 'within']
WORDS = {'shared': ['no', 'yes'], 'far': ['pass', 'flag']}

POLICIES = ['normal', 'answer_cross_off', 'all_cross_off']


def truth(ctx, world, owner):
    gold = np.asarray([(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']])
    if owner == 1 and world != 'cross':
        gold = -gold
    return gold.tolist()


def analyze(dest):
    rows = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    z = {k: np.asarray([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    out = {'n_contexts': len(rows), 'conditions': {}, 'policy_accuracy': {}, 'contrasts': {}, 'A_B_code_response': {}}
    for key, value in z.items():
        gold = np.asarray([r['conditions'][key]['gold'] for r in rows])
        out['conditions'][key] = {'candidate_accuracy': interval(((value > 0) == (gold > 0)).mean(1)),
            'argmax_accuracy': interval([np.mean(r['conditions'][key]['argmax_correct']) for r in rows]),
            'correct_label_margin': interval((value * gold).mean(1))}
    ga = np.asarray([truth(c, 'origin', 0) for c in cs])
    aggregates = {}
    for namespace in WORDS:
        for policy in POLICIES:
            for scope in ['native', 'gate']:
                values = np.stack([np.stack([((z[f'{w}_{namespace}_{policy}_{scope}_{owner}'] > 0)
                    == (np.asarray([truth(c, w, owner) for c in cs]) > 0)) for owner in [0, 1]], 1)
                    for w in ['origin', 'cross']], 1)
                summary = {'both': values.mean((1, 2, 3)), 'A': values[:, :, 0].mean((1, 2)),
                    'B': values[:, :, 1].mean((1, 2)), 'opposite_convention': values[:, 0].mean((1, 2)),
                    'same_convention': values[:, 1].mean((1, 2))}
                aggregates[namespace, policy, scope] = summary
                out['policy_accuracy'][f'{namespace}_{policy}_{scope}'] = {k: interval(v) for k, v in summary.items()}
                response = .5 * (z[f'cross_{namespace}_{policy}_{scope}_0'] - z[f'origin_{namespace}_{policy}_{scope}_0'])
                oriented = (response * ga).mean(1)
                within = ((z[f'within_{namespace}_{policy}_{scope}_0'] - z[f'origin_{namespace}_{policy}_{scope}_0']) * ga).mean(1)
                out['A_B_code_response'][f'{namespace}_{policy}_{scope}'] = {
                    'signed': interval(oriented), 'absolute': interval(abs(oriented)),
                    'within_signed': interval(within), 'within_absolute': interval(abs(within))}
        for scope in ['native', 'gate']:
            for policy in POLICIES[1:]:
                out['contrasts'][f'{namespace}_{policy}_minus_normal_{scope}'] = {k: interval(
                    aggregates[namespace, policy, scope][k] - aggregates[namespace, 'normal', scope][k])
                    for k in aggregates[namespace, 'normal', scope]}
            out['contrasts'][f'{namespace}_answer_minus_all_{scope}'] = {k: interval(
                aggregates[namespace, 'answer_cross_off', scope][k] - aggregates[namespace, 'all_cross_off', scope][k])
                for k in aggregates[namespace, 'normal', scope]}
        for policy in POLICIES:
            out['contrasts'][f'{namespace}_query_isolation_{policy}'] = {k: interval(
                aggregates[namespace, policy, 'gate'][k] - aggregates[namespace, policy, 'native'][k])
                for k in aggregates[namespace, policy, 'native']}
        out['contrasts'][f'{namespace}_answer_by_query_interaction'] = {k: interval(
            aggregates[namespace, 'answer_cross_off', 'gate'][k] - aggregates[namespace, 'normal', 'gate'][k]
            - aggregates[namespace, 'answer_cross_off', 'native'][k] + aggregates[namespace, 'normal', 'native'][k])
            for k in aggregates[namespace, 'normal', 'native']}
    for scope in ['native', 'gate']:
        out['contrasts'][f'targeted_gain_shared_minus_far_{scope}'] = {k: interval(
            aggregates['shared', 'answer_cross_off', scope][k] - aggregates['shared', 'normal', scope][k]
            - aggregates['far', 'answer_cross_off', scope][k] + aggregates['far', 'normal', scope][k])
            for k in aggregates['shared', 'normal', scope]}
    (dest / 'analysis.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'n_contexts': len(rows), 'both_actor_accuracy': {k: v['both'] for k, v in out['policy_accuracy'].items()}}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=123001)
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
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    cs, natural_metadata = make_contexts(tok, args.n, args.seed, args.materials)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    assert all(len(enc(' ' + w)) == 1 for words in WORDS.values() for w in words)
    word_ids = {ns: [enc(' ' + w)[0] for w in words] for ns, words in WORDS.items()}
    label_ids = word_ids['shared']

    def prefix(ctx, world, namespace, single=None, instruction=False):
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
            answer = enc(' ' + WORDS[namespace if role == 1 else 'shared'][y]) + enc('\n\n')
            labels.append(anchor)
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
        return ids, roles, labels, answers

    encoded = [{(w, ns): prefix(c, w, ns) for w in WORLDS for ns in WORDS} for c in cs]
    for worlds in encoded:
        reference = worlds['origin', 'shared']
        for value in worlds.values():
            assert len(value[0]) == len(reference[0]) and value[1:] == reference[1:]
        for ns in WORDS:
            ref = worlds['origin', ns]
            for w in WORLDS:
                data = worlds[w, ns]
                assert all(data[0][i] == ref[0][i] for i, role in enumerate(ref[1]) if role != 1)
                assert all(data[0][i] == ref[0][i] for i in ref[2])
    (dest / 'preflight.json').write_text(json.dumps({'args': vars(args), 'conditions': 85,
        'policies': POLICIES, 'worlds': WORLDS, 'namespaces': WORDS, 'word_ids': word_ids,
        'owners': [0, 1], 'matched_geometry': True, 'natural_materials': natural_metadata,
        'prefix_lengths': [len(w['origin', 'shared'][0]) for w in encoded],
        'shared_prefix_for_both_owners': True, 'primary_worlds': ['origin', 'cross'],
        'scope': 'real SST5 text, inferred private conventions; within-world secondary control'}, indent=2) + '\n')
    if args.preflight_only:
        print('E123 both-owner truth and all namespace/world geometry passed.', flush=True)
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

    def query(cache, roles, queries, owner, gate, ids_out):
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
        return {'z': (logits[:, ids_out[1]] - logits[:, ids_out[0]]).cpu().tolist(),
                'argmax_token': top.cpu().tolist(), 'argmax_is_label': ((top == ids_out[0]) | (top == ids_out[1])).cpu().tolist()}

    with torch.inference_mode(), (dest / 'behavior.jsonl').open('w') as stream:
        for ci, ctx in enumerate(cs):
            queries = {owner: [enc(f"Comment: {t}\nAnnotator: {ctx['names'][owner]}\nLabel:") for t, _ in ctx['q']] for owner in [0, 1]}
            conditions, edge_counts = {}, {}
            def score(name, cache, roles, world, namespace, owner, gate=False):
                ids_out = word_ids[namespace if owner == 1 else 'shared']
                value = query(cache, roles, queries[owner], owner, gate, ids_out)
                value['gold'] = truth(ctx, world, owner)
                value['argmax_correct'] = [t == ids_out[int(g > 0)] for t, g in zip(value['argmax_token'], value['gold'])]
                conditions[name] = value
            for namespace in WORDS:
                for world in WORLDS:
                    data = encoded[ci][world, namespace]
                    for policy in POLICIES:
                        name = world + '_' + namespace + '_' + policy
                        cache, edge_counts[name] = prefill(data, policy, consumption.setdefault(name, {}))
                        for scope in ['native', 'gate']:
                            for owner in [0, 1]:
                                score(f'{name}_{scope}_{owner}', cache, data[1], world, namespace, owner, scope == 'gate')
                        if ci == 0 and world == 'origin' and policy == 'normal':
                            default = model(input_ids=torch.tensor([data[0]], device='cuda'), use_cache=True, logits_to_keep=1).past_key_values
                            self_errors.append(max(float((getattr(a, k) - getattr(b, k)).abs().max()) for a, b in zip(cache.layers, default.layers) for k in ['keys', 'values']))
                            for owner in [0, 1]:
                                ids_out = word_ids[namespace if owner == 1 else 'shared']
                                for qi, q in enumerate(queries[owner]):
                                    logits = model(input_ids=torch.tensor([data[0] + q], device='cuda'), use_cache=False, logits_to_keep=1).logits[0, -1].float()
                                    numeric.append(abs(float(logits[ids_out[1]] - logits[ids_out[0]]) - conditions[f'{name}_native_{owner}']['z'][qi]))
                            del default
                        del cache
                for world in WORLDS[1:]:
                    left = conditions[f'{world}_{namespace}_all_cross_off_gate_0']['z']
                    right = conditions[f'origin_{namespace}_all_cross_off_gate_0']['z']
                    graph_zero.append(max(abs(a - b) for a, b in zip(left, right)))
                for owner in [0, 1]:
                    if owner == 0 and namespace == 'far':
                        continue
                    for world in (['origin'] if owner == 0 else ['origin', 'cross']):
                        data = prefix(ctx, world, namespace, single=owner)
                        cache, _ = prefill(data, 'normal')
                        score('single_A' if owner == 0 else 'single_B_' + world + '_' + namespace,
                            cache, data[1], world, namespace, owner)
                        if ci == 0 and world == 'origin':
                            for policy in POLICIES[1:]:
                                no_op, counts = prefill(data, policy)
                                assert counts == {'0': 0, '1': 0}
                                self_errors.append(max(float((getattr(a, k) - getattr(b, k)).abs().max())
                                    for a, b in zip(cache.layers, no_op.layers) for k in ['keys', 'values']))
                                del no_op
                        del cache
                for world in ['origin', 'cross']:
                    data = prefix(ctx, world, namespace, instruction=True)
                    cache, _ = prefill(data, 'normal')
                    for owner in [0, 1]:
                        score(f'{world}_{namespace}_instruction_{owner}', cache, data[1], world, namespace, owner)
                    del cache
            assert len(conditions) == 85
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
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600,
        'git_head': None}, indent=2) + '\n')
    analyze(dest)


if __name__ == '__main__':
    main()
