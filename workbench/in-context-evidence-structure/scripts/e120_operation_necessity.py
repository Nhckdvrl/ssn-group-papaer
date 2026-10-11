"""E120: native historical formation knockout and restricted-graph restoration.

No donor activations, head selection, layer selection, or fitted coefficients.
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
from e119_native_scale import interval, WORDS

OPERATIONS = ['native', 'cross_answer_off', 'within_answer_off', 'all_B_off', 'answer_only_restore']


def analyze(dest):
    rows = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    g = np.asarray([r['gold'] for r in rows])
    z = {k: np.asarray([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    assert len(z) == 64
    out = {'n_contexts': len(rows), 'accuracy': {}, 'responses': {}, 'contrasts': {}}
    for k, v in z.items():
        out['accuracy'][k] = {'candidate': interval(((v > 0) == (g > 0)).mean(1)),
            'argmax': interval([np.mean(r['conditions'][k]['argmax_correct']) for r in rows])}
    for namespace in ['shared', 'far']:
        for scope in ['native', 'gate']:
            d, w = {}, {}
            for op in OPERATIONS:
                def condition(world): return f'{world}_{namespace}_{op}_{scope}'
                d[op] = ((z[condition('cross')] - z[condition('origin')]) * g).mean(1)
                w[op] = ((z[condition('within')] - z[condition('origin')]) * g).mean(1)
                out['responses'][f'{namespace}_{scope}_{op}'] = {
                    'rule_signed': interval(d[op]), 'rule_absolute': interval(abs(d[op])),
                    'within_signed': interval(w[op]), 'within_absolute': interval(abs(w[op]))}
            for name, left, right in [
                ('cross_answer_removal', 'native', 'cross_answer_off'),
                ('within_answer_removal', 'native', 'within_answer_off'),
                ('cross_vs_within_removal', 'within_answer_off', 'cross_answer_off'),
                ('all_cross_removal', 'native', 'all_B_off'),
                ('answer_path_restoration', 'answer_only_restore', 'all_B_off'),
                ('restoration_residual', 'native', 'answer_only_restore'),
            ]:
                out['contrasts'][f'{namespace}_{scope}_{name}'] = {
                    'rule_signed': interval(d[left] - d[right]),
                    'rule_absolute': interval(abs(d[left]) - abs(d[right])),
                    'excess_over_within': interval((abs(d[left]) - abs(w[left])) - (abs(d[right]) - abs(w[right])))}
    # Namespace interaction is computed from signed responses, not only absolute effects.
    for scope in ['native', 'gate']:
        for op in OPERATIONS:
            key = lambda w, ns: f'{w}_{ns}_{op}_{scope}'
            dd = ((z[key('cross', 'shared')] - z[key('origin', 'shared')]
                   - z[key('cross', 'far')] + z[key('origin', 'far')]) * g).mean(1)
            out['contrasts'][f'namespace_rule_{scope}_{op}'] = {'signed': interval(dd), 'absolute': interval(abs(dd))}
    reverse = np.asarray([c['reverse'] for c in cs])
    out['single_by_polarity'] = {condition: {str(p): interval(((z[condition][reverse == p] > 0)
        == (g[reverse == p] > 0)).mean(1)) for p in [False, True]}
        for condition in ['single_A', 'single_A_within_answer_off']}
    (dest / 'analysis.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'n_contexts': len(rows), 'gated_shared': {
        op: out['responses'][f'shared_gate_{op}']['rule_absolute'] for op in OPERATIONS}}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=120001)
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
    # The original generator provides the same preregistered matched relation worlds.
    material = dest / 'materials'
    subprocess.run([sys.executable, str(Path(__file__).with_name('e115_llama_native_mechanism.py')),
        '--model', args.model, '--out', str(material), '--n', str(args.n), '--seed', str(args.seed),
        '--materials', args.materials, '--preflight-only'], check=True)
    (dest / 'contexts.jsonl').write_bytes((material / 'contexts.jsonl').read_bytes())
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda t: tok.encode(t, add_special_tokens=False)
    label_ids = [enc(' ' + w)[0] for w in WORDS['shared']]
    assert all(len(enc(' ' + w)) == 1 for pair in WORDS.values() for w in pair)

    def prefix(ctx, world, namespace='shared', instruction=False, single=False):
        text = HEAD + ("Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n" if instruction else '')
        ids, roles = enc(text), [-1] * len(enc(text))
        labels, answers_a, answers_b = [], [], []
        for (comment, role, y), name in zip(ctx['demos'], ctx['shown']):
            if single and role == 1:
                continue
            if role == 1 and world != 'origin':
                comment = ctx[world + '_map'][comment]
            block = enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            anchor = len(ids) + len(block)
            answer = enc(' ' + WORDS[namespace if role == 1 else 'shared'][y]) + enc('\n\n')
            (answers_a if role == 0 else answers_b).extend(range(anchor, anchor + len(answer)))
            if role == 0:
                labels.append(anchor)
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
        return ids, roles, labels, answers_a, answers_b

    encoded = [{(w, ns): prefix(c, w, ns) for w in ['origin', 'cross', 'within']
                for ns in ['shared', 'far']} for c in cs]
    for worlds in encoded:
        reference = worlds['origin', 'shared']
        for key, value in worlds.items():
            assert len(value[0]) == len(reference[0]) and value[1:] == reference[1:]
    preflight = {'args': vars(args), 'operations': OPERATIONS, 'conditions': 64, 'scores_per_context': 512,
        'source_generator': 'e115_llama_native_mechanism.py, CPU-only',
        'prefix_lengths': [len(w['origin', 'shared'][0]) for w in encoded],
        'matched_geometry': True, 'restoration': 'allow only historical B answer -> A label among all B -> A edges',
        'intervention': 'prefix-only normalized attention knockout; no donor activations'}
    (dest / 'preflight.json').write_text(json.dumps(preflight, indent=2) + '\n')
    if args.preflight_only:
        print('E120 geometry passed; 64 conditions frozen.', flush=True)
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
    numeric_errors, graph_errors, mask_self_errors, consumption = [], [], [], {}

    def prefill(data, op, record=None):
        ids, roles, labels, answer_a, answer_b = data
        length = len(ids)
        allowed = torch.ones((length, length), dtype=torch.bool, device='cuda').tril()
        recv = torch.tensor(labels if op in ['cross_answer_off', 'within_answer_off']
                            else [i for i, r in enumerate(roles) if r == 0], device='cuda', dtype=torch.long)
        send = torch.tensor(answer_a if op == 'within_answer_off' else answer_b if op == 'cross_answer_off'
                            else [i for i, r in enumerate(roles) if r == 1], device='cuda', dtype=torch.long)
        removed = 0
        if op != 'native' and len(recv) and len(send):
            past = send[None, :] < recv[:, None]
            removed = int((allowed[recv[:, None], send[None, :]] & past).sum())
            allowed[recv[:, None], send[None, :]] &= ~past
        restored = 0
        if op == 'answer_only_restore':
            rr = torch.tensor(labels, device='cuda')
            ss = torch.tensor(answer_b, device='cuda')
            restored = int((ss[None, :] < rr[:, None]).sum())
            allowed[rr[:, None], ss[None, :]] = ss[None, :] < rr[:, None]
        mask = torch.zeros((1, 1, length, length), dtype=torch.float32, device='cuda')
        mask.masked_fill_(~allowed, float('-inf'))
        # Explicit hooks record that the same mask was consumed by every actual layer.
        handles = []
        if record is not None:
            def hook(module, aa, kw):
                actual = kw['attention_mask']
                assert actual.shape == mask.shape and torch.equal(actual, mask)
                k = module.layer_idx
                record[k] = record.get(k, 0) + 1
            handles = [layer.self_attn.register_forward_pre_hook(hook, with_kwargs=True) for layer in model.model.layers]
        try:
            cache = model(input_ids=torch.tensor([ids], device='cuda'), attention_mask=mask,
                          use_cache=True, logits_to_keep=1).past_key_values
        finally:
            for h in handles:
                h.remove()
        return cache, {'removed_causal_edges': removed, 'restored_causal_edges': restored}

    def query(cache, roles, qs, gate=False):
        plen, n, qlen = len(roles), len(qs), max(map(len, qs))
        ids = torch.zeros((n, qlen), dtype=torch.long, device='cuda')
        positions = torch.zeros_like(ids)
        live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(qs):
            ids[i, -len(q):] = torch.tensor(q, device='cuda')
            positions[i, -len(q):] = torch.arange(plen, plen + len(q), device='cuda')
            live[i, -len(q):] = True
        keep = torch.tensor(roles, device='cuda') != 1 if gate else torch.ones(plen, dtype=torch.bool, device='cuda')
        allowed = torch.cat([keep[None, None].expand(n, qlen, -1),
            live[:, None].expand(-1, qlen, -1) & torch.ones((qlen, qlen), dtype=torch.bool, device='cuda').tril()[None]], -1)
        mask = torch.zeros(allowed.shape, dtype=torch.float32, device='cuda').masked_fill_(~allowed, float('-inf'))
        cp = copy.deepcopy(cache)
        assert all(dst.keys.data_ptr() != src.keys.data_ptr() and dst.values.data_ptr() != src.values.data_ptr()
                   for dst, src in zip(cp.layers, cache.layers))
        cp.batch_repeat_interleave(n)
        logits = model(input_ids=ids, position_ids=positions, attention_mask=mask[:, None],
            past_key_values=cp, use_cache=True, logits_to_keep=1).logits[:, -1].float()
        top = logits.argmax(-1)
        assert cache.get_seq_length() == plen
        return {'z': (logits[:, label_ids[1]] - logits[:, label_ids[0]]).cpu().tolist(),
                'argmax_token': top.cpu().tolist(), 'argmax_is_label': ((top == label_ids[0]) | (top == label_ids[1])).cpu().tolist()}

    with torch.inference_mode(), (dest / 'behavior.jsonl').open('w') as stream:
        for ci, ctx in enumerate(cs):
            qs = [enc(f"Comment: {t}\nAnnotator: {ctx['names'][0]}\nLabel:") for t, _ in ctx['q']]
            gold = [(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']]
            conditions, edges = {}, {}
            for namespace in ['shared', 'far']:
                for world in ['origin', 'cross', 'within']:
                    data = encoded[ci][world, namespace]
                    for op in OPERATIONS:
                        name = f'{world}_{namespace}_{op}'
                        record = consumption.setdefault(name, {})
                        cache, edges[name] = prefill(data, op, record)
                        for scope in ['native', 'gate']:
                            conditions[name + '_' + scope] = query(cache, data[1], qs, scope == 'gate')
                        if ci == 0 and world == 'origin' and namespace == 'shared' and op == 'native':
                            default_cache = model(input_ids=torch.tensor([data[0]], device='cuda'),
                                use_cache=True, logits_to_keep=1).past_key_values
                            mask_self_errors.append(max(float((getattr(x, k) - getattr(y, k)).abs().max())
                                for x, y in zip(cache.layers, default_cache.layers) for k in ['keys', 'values']))
                            del default_cache
                            for qi, q in enumerate(qs):
                                full = model(input_ids=torch.tensor([data[0] + q], device='cuda'),
                                    use_cache=False, logits_to_keep=1).logits[0, -1].float()
                                numeric_errors.append(abs(float(full[label_ids[1]] - full[label_ids[0]])
                                    - conditions[name + '_native']['z'][qi]))
                        del cache
                for world in ['cross', 'within']:
                    left = conditions[f'{world}_{namespace}_all_B_off_gate']['z']
                    right = conditions[f'origin_{namespace}_all_B_off_gate']['z']
                    graph_errors.append(max(abs(a - b) for a, b in zip(left, right)))
            own = prefix(ctx, 'origin', single=True)
            for op, name in [('native', 'single_A'), ('within_answer_off', 'single_A_within_answer_off')]:
                cache, _ = prefill(own, op)
                conditions[name] = query(cache, own[1], qs)
            for world in ['origin', 'cross']:
                data = prefix(ctx, world, instruction=True)
                cache, _ = prefill(data, 'native')
                conditions[world + '_instruction'] = query(cache, data[1], qs)
            assert len(conditions) == 64
            assert max(numeric_errors) <= .001 and max(graph_errors) <= .001 and max(mask_self_errors) <= .001
            for value in conditions.values():
                value['argmax_correct'] = [t == label_ids[int(g > 0)] for t, g in zip(value['argmax_token'], gold)]
            stream.write(json.dumps({'context': ci, 'gold': gold, 'conditions': conditions, 'edge_counts': edges}) + '\n')
            stream.flush()
            print(ci + 1, '/', args.n, 'numeric', max(numeric_errors), 'graph_zero', max(graph_errors), flush=True)
    assert all(set(v) == set(range(len(model.model.layers))) and set(v.values()) == {args.n} for v in consumption.values())
    revision = {'qwen3': '40c069824f4251a91eefaf281ebe4c544efd3e18' if model.config.num_hidden_layers == 40 else 'b968826d9c46dd6066d109eabc6255188de91218',
        'mistral': 'caa1feb0e54d415e2df31207e5f4e273e33509b1', 'llama': '1f47e50cdbe801ad8a5174156ec3a0655108fb9f'}[model.config.model_type]
    elapsed = time.time() - started
    run = {'args': vars(args), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256': hashlib.sha256((dest / 'contexts.jsonl').read_bytes()).hexdigest(),
        'numeric_max_error': max(numeric_errors), 'graph_zero_max_error': max(graph_errors),
        'native_mask_cache_max_error': max(mask_self_errors), 'pristine_cache_scope': 'deepcopy data_ptr and sequence length checked',
        'all_layer_consumption': consumption, 'model_revision': revision, 'model_type': model.config.model_type,
        'num_layers': len(model.model.layers), 'dtype': 'float32', 'attention': 'eager', 'training': False,
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600,
        'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'intervention': 'prefix normalized edge knockout and limited allowed-edge restoration, no donors'}
    (dest / 'run.json').write_text(json.dumps(run, indent=2) + '\n')
    analyze(dest)


if __name__ == '__main__':
    main()
