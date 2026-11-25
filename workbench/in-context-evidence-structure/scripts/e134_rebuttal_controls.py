"""E134: rebuttal controls on the E132 SST-5 engine (same token stream, same confirmation prompts).

Policies added to E132: matched_count / matched_mass (block as many edges, or as much native attention, from
label positions to the other source's non-answer tokens), answer_norenorm (selective blocking by zeroing the
post-softmax weights without renormalisation), *_cf (name tokens see only the header and their own name span),
grouped orderings (all A demos then all B demos, or the reverse), and a 2x2 attention readout (word match x
class match) from A's label positions to B's answer words. See experiments/E134-rebuttal-controls-sst5.md.
"""
import argparse
import copy
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD
from e118_criterion_code_feature_crossing import interval
from e121_sst_materials import make_contexts

WORLDS = ['origin', 'cross']
NAMESPACES = {'shared': (['no', 'yes'], ['no', 'yes']), 'far': (['no', 'yes'], ['pass', 'flag'])}
PLAN = {
    'shared': ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names', 'all_cross_off_cf', 'iso_names_cf',
               'all_cross_off_cl', 'iso_names_cl',
               'matched_count', 'matched_mass', 'answer_norenorm',
               'AB:normal', 'AB:answer_cross_off', 'BA:normal', 'BA:answer_cross_off'],
    'far': ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names', 'all_cross_off_cf', 'iso_names_cf',
            'all_cross_off_cl', 'iso_names_cl',
            'AB:normal', 'BA:normal'],
}
CELLS = ['sameword_sameclass', 'sameword_diffclass', 'diffword_sameclass', 'diffword_diffclass']


def truth(ctx, world, owner):
    gold = np.asarray([(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']])
    if owner == 1 and world != 'cross':
        gold = -gold
    return gold.tolist()


def positive_class(ctx, role, y, world):
    """True sentiment class of a demo's comment (after the world's comment exchange)."""
    if role == 0:
        return bool((y == 1) != ctx['reverse'])
    pos = bool((y == 0) != ctx['reverse'])
    return (not pos) if world == 'cross' else pos


def analyze(dest):
    rows = []
    for path in sorted(dest.glob('behavior*.jsonl')):
        rows += [json.loads(x) for x in path.read_text().splitlines()]
    rows.sort(key=lambda r: r['context'])
    out = {'n_contexts': len(rows), 'accuracy': {}, 'delta': {}, 'contrasts': {}, 'removed_mass': {}, 'attention_2x2': {}}

    def acc(key):
        return np.array([np.mean(r['conditions'][key]['argmax_correct']) for r in rows])

    def z(key):
        return np.array([r['conditions'][key]['z'] for r in rows])

    gA = np.array([r['conditions']['origin_shared_normal_native_0']['gold'] for r in rows])
    summ = {}
    for ns, policies in PLAN.items():
        for policy in policies:
            for scope in ['native', 'gate']:
                cells = {(w, o): acc(f'{w}_{ns}_{policy}_{scope}_{o}') for w in WORLDS for o in [0, 1]}
                s = {'both': np.mean(list(cells.values()), 0), 'A': (cells['origin', 0] + cells['cross', 0]) / 2,
                     'B': (cells['origin', 1] + cells['cross', 1]) / 2,
                     'opposite': (cells['origin', 0] + cells['origin', 1]) / 2,
                     'same': (cells['cross', 0] + cells['cross', 1]) / 2,
                     'other_source_word': np.mean([[np.mean(r['conditions'][f'{w}_{ns}_{policy}_{scope}_{o}']['other_source_word'])
                                                    for r in rows] for w in WORLDS for o in [0, 1]], 0)}
                summ[ns, policy, scope] = s
                out['accuracy'][f'{ns}_{policy}_{scope}'] = {k: interval(v) for k, v in s.items()}
                d = (.5 * (z(f'cross_{ns}_{policy}_{scope}_0') - z(f'origin_{ns}_{policy}_{scope}_0')) * gA).mean(1)
                summ[ns, policy, scope]['delta'] = d
                out['delta'][f'{ns}_{policy}_{scope}'] = {'signed': interval(d), 'flip_rate': interval(
                    (np.sign(z(f'cross_{ns}_{policy}_{scope}_0')) != np.sign(z(f'origin_{ns}_{policy}_{scope}_0'))).mean(1))}
    C = out['contrasts']
    for ns, policies in PLAN.items():
        for policy in policies:
            if policy == 'normal':
                continue
            base = (policy.split(':')[0] + ':normal') if ':' in policy and not policy.endswith('normal') else 'normal'
            for scope in ['native', 'gate']:
                for part in ['both', 'opposite', 'A', 'B']:
                    C[f'{ns}_{policy}_minus_{base}_{scope}_{part}'] = interval(summ[ns, policy, scope][part] - summ[ns, base, scope][part])
                C[f'{ns}_{policy}_delta_reduction_vs_{base}_{scope}'] = interval(summ[ns, base, scope]['delta'] - summ[ns, policy, scope]['delta'])
    for ns in PLAN:
        for scope in ['native', 'gate']:
            for part in ['both', 'opposite']:
                for ctrl in (['matched_count', 'matched_mass', 'answer_norenorm'] if ns == 'shared' else []):
                    C[f'{ns}_answer_cross_off_minus_{ctrl}_{scope}_{part}'] = interval(
                        summ[ns, 'answer_cross_off', scope][part] - summ[ns, ctrl, scope][part])
                g = summ[ns, 'iso_names', scope][part] - summ[ns, 'all_cross_off', scope][part]
                gcf = summ[ns, 'iso_names_cf', scope][part] - summ[ns, 'all_cross_off_cf', scope][part]
                C[f'{ns}_names_gain_{scope}_{part}'] = interval(g)
                C[f'{ns}_names_gain_cf_{scope}_{part}'] = interval(gcf)
                C[f'{ns}_names_gain_cf_minus_gain_{scope}_{part}'] = interval(gcf - g)
                gcl = summ[ns, 'iso_names_cl', scope][part] - summ[ns, 'all_cross_off_cl', scope][part]
                C[f'{ns}_names_gain_cl_{scope}_{part}'] = interval(gcl)
                C[f'{ns}_names_gain_cl_minus_gain_{scope}_{part}'] = interval(gcl - g)
                C[f'{ns}_iso_names_cf_minus_all_cross_off_{scope}_{part}'] = interval(
                    summ[ns, 'iso_names_cf', scope][part] - summ[ns, 'all_cross_off', scope][part])
        for ctrl in (['matched_count', 'matched_mass', 'answer_norenorm'] if ns == 'shared' else []):
            C[f'{ns}_answer_cross_off_minus_{ctrl}_delta_reduction'] = interval(
                summ[ns, ctrl, 'gate']['delta'] - summ[ns, 'answer_cross_off', 'gate']['delta'])
    for policy in ['answer_cross_off', 'matched_count', 'matched_mass']:
        arr = np.array([np.mean([r['removed_mass'][w][policy] for w in WORLDS]) for r in rows])
        out['removed_mass'][policy] = interval(arr)
    for cell in CELLS:
        arr = np.array([r['attention_2x2'][cell] for r in rows], dtype=float)
        out['attention_2x2'][cell] = interval(arr[~np.isnan(arr)])
    a = {c: np.array([r['attention_2x2'][c] for r in rows], dtype=float) for c in CELLS}
    ok = ~np.any([np.isnan(v) for v in a.values()], 0)
    a = {c: v[ok] for c, v in a.items()}
    out['attention_2x2']['word_effect'] = interval(((a['sameword_sameclass'] + a['sameword_diffclass']) - (a['diffword_sameclass'] + a['diffword_diffclass'])) / 2)
    out['attention_2x2']['class_effect'] = interval(((a['sameword_sameclass'] + a['diffword_sameclass']) - (a['sameword_diffclass'] + a['diffword_diffclass'])) / 2)
    out['attention_2x2']['interaction'] = interval((a['sameword_sameclass'] - a['sameword_diffclass']) - (a['diffword_sameclass'] - a['diffword_diffclass']))
    (dest / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=32)
    ap.add_argument('--seed', type=int, default=132101)
    ap.add_argument('--materials', choices=['discovery', 'validation'], default='validation')
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--device-map', default='cuda')
    ap.add_argument('--analyze-only', action='store_true')
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    shard, shards = map(int, args.shard.split('/'))
    behavior_path = dest / ('behavior.jsonl' if shards == 1 else f'behavior.shard{shard}.jsonl')
    assert not behavior_path.exists()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    cs, natural_metadata = make_contexts(tok, args.n, args.seed, args.materials)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    words = sorted({w for a, b in NAMESPACES.values() for w in a + b})
    assert all(len(enc(' ' + w)) == 1 for w in words)
    wid = {w: enc(' ' + w)[0] for w in words}
    ns_ids = {ns: ([wid[w] for w in a], [wid[w] for w in b]) for ns, (a, b) in NAMESPACES.items()}

    def prefix(ctx, world, namespace, order='mix'):
        ids, roles, types = enc(HEAD), [-1] * len(enc(HEAD)), ['h'] * len(enc(HEAD))
        labels, answers, meta = [], [[], []], {}
        demos = list(zip(ctx['demos'], ctx['shown']))
        if order != 'mix':
            first = 0 if order == 'AB' else 1
            demos = [d for d in demos if d[0][1] == first] + [d for d in demos if d[0][1] != first]
        name_spans = []
        for (comment, role, y), name in demos:
            cls = positive_class(ctx, role, y, world)
            if role == 1 and world != 'origin':
                comment = ctx[world + '_map'][comment]
            text = f'Comment: {comment}\nAnnotator: {name}\nLabel:'
            annotated = tok(text, add_special_tokens=False, return_offsets_mapping=True)
            block = annotated['input_ids']
            assert block == enc(text)
            name_start, cue_start = text.index('\nAnnotator:'), text.index('\nLabel:')
            kinds = []
            for a, b in annotated['offset_mapping']:
                mid = (a + b) / 2 if b > a else a
                kinds.append('c' if mid < name_start else 'n' if mid < cue_start else 'q')
            anchor = len(ids) + len(block)
            word = NAMESPACES[namespace][role][y]
            answer = enc(' ' + word) + enc('\n\n')
            labels.append(anchor)
            meta[anchor] = {'role': role, 'word': wid[word], 'cls': cls}
            answers[role].extend(range(anchor, anchor + len(answer)))
            name_spans.append((len(ids), [len(ids) + i for i, k in enumerate(kinds) if k == 'n']))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
            types.extend(kinds + ['a'] * len(answer))
        return {'ids': ids, 'roles': roles, 'labels': labels, 'answers': answers, 'types': types, 'meta': meta,
                'name_spans': name_spans}

    def key(world, ns, policy):
        return (world, ns, policy.split(':')[0] if ':' in policy else 'mix')
    encoded = [{key(w, ns, p): prefix(c, w, ns, key(w, ns, p)[2]) for w in WORLDS for ns in PLAN for p in PLAN[ns]} for c in cs]
    (dest / 'preflight.json').write_text(json.dumps({'args': vars(args), 'plan': PLAN, 'worlds': WORLDS,
        'namespaces': NAMESPACES, 'word_ids': wid, 'natural_materials': natural_metadata,
        'prefix_lengths': [len(e['origin', 'shared', 'mix']['ids']) for e in encoded]}, indent=1) + '\n')

    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
        device_map=args.device_map, attn_implementation='eager').eval()
    model.requires_grad_(False)
    dev = model.get_input_embeddings().weight.device
    layers = model.model.layers
    nl = len(layers)

    # --- eager-attention wrapper: post-softmax zeroing without renormalisation, and attention capture ---
    import importlib
    family = importlib.import_module(type(model).__module__)
    ORIG = family.eager_attention_forward
    STATE = {'removed': None, 'capture': None, 'calls': 0}

    def wrapped(module, query, key_, value, attention_mask, *a, **kw):
        STATE['calls'] += 1
        rem = STATE['removed']
        if rem is not None and query.shape[2] == rem.shape[0]:
            out_full, w_full = ORIG(module, query, key_, value, attention_mask, *a, **kw)
            r = rem.to(device=w_full.device)
            kept = 1 - (w_full * r.to(w_full.dtype)).sum(-1)  # b,h,q: native weight left on kept tokens
            blocked = attention_mask.masked_fill(r[None, None], float('-inf'))
            out_b, w_b = ORIG(module, query, key_, value, blocked, *a, **kw)
            return out_b * kept.transpose(1, 2)[..., None].to(out_b.dtype), w_b
        out, w = ORIG(module, query, key_, value, attention_mask, *a, **kw)
        cap = STATE['capture']
        if cap is not None and query.shape[2] == cap.shape[0]:
            cap += w[0].float().mean(0).to(cap.device)
        return out, w
    family.eager_attention_forward = wrapped

    def causal(n):
        return torch.ones((n, n), dtype=torch.bool, device=dev).tril()

    def block_pairs(allowed, receivers, senders):
        rr = torch.tensor(receivers, device=dev, dtype=torch.long)
        ss = torch.tensor(senders, device=dev, dtype=torch.long)
        if len(rr) and len(ss):
            past = ss[None, :] < rr[:, None]
            allowed[rr[:, None], ss[None, :]] &= ~past

    def allowed_for(d, policy, native_att=None, rng=None):
        n = len(d['ids'])
        allowed = causal(n)
        R, T = np.array(d['roles']), np.array(d['types'])
        base = policy.split(':')[-1]
        if base.endswith('_cf') or base.endswith('_cl'):
            local = base.endswith('_cl')  # cl: names also see their own demonstration's comment
            for start, span in d['name_spans']:
                ok = set(np.where(T == 'h')[0].tolist()) | set(span) | (set(range(start, span[0])) if local else set())
                for i in span:
                    bad = [j for j in range(i) if j not in ok]
                    if bad:
                        allowed[i, torch.tensor(bad, device=dev)] = False
            base = base[:-3]
        if base in ['normal', 'answer_norenorm']:
            return allowed
        for owner in [0, 1]:
            other = 1 - owner
            if base == 'answer_cross_off':
                block_pairs(allowed, [a for a in d['labels'] if d['roles'][a] == owner], d['answers'][other])
            elif base in ['all_cross_off', 'iso_names']:
                keep = '' if base == 'all_cross_off' else 'n'
                block_pairs(allowed, np.where(R == owner)[0].tolist(),
                            [i for i in np.where(R == other)[0].tolist() if T[i] not in keep])
            elif base in ['matched_count', 'matched_mass']:
                ans = set(d['answers'][other])
                for r in [a for a in d['labels'] if d['roles'][a] == owner]:
                    k = sum(1 for j in ans if j < r)
                    if not k:
                        continue
                    if base == 'matched_count':
                        cand = [j for j in range(r) if R[j] == other and T[j] == 'c']
                        pick = rng.choice(cand, min(k, len(cand)), replace=False).tolist()
                    else:
                        cand = [j for j in range(r) if R[j] == other and T[j] in 'cq']
                        target = float(native_att[r, sorted(j for j in ans if j < r)].sum())
                        order = sorted(cand, key=lambda j: -float(native_att[r, j]))
                        pick, got = [], 0.0
                        for j in order:
                            if got >= target:
                                break
                            pick.append(j)
                            got += float(native_att[r, j])
                    block_pairs(allowed, [r], pick)
            else:
                raise ValueError(policy)
        return allowed

    def removed_mass(d, allowed, native_att):
        lab = d['labels']
        cau = causal(len(d['ids']))
        rem = (cau & ~allowed)[lab].float()
        return float((native_att[lab] * rem).sum(-1).mean())

    def prefill(d, allowed, norenorm_removed=None, capture=False):
        n = len(d['ids'])
        mask = torch.zeros((1, 1, n, n), dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        STATE['removed'] = norenorm_removed
        STATE['capture'] = torch.zeros((n, n), dtype=torch.float32, device=dev) if capture else None
        STATE['calls'] = 0
        try:
            pkv = model(input_ids=torch.tensor([d['ids']], device=dev), attention_mask=mask, use_cache=True,
                        logits_to_keep=1).past_key_values
        finally:
            STATE['removed'] = None
        assert STATE['calls'] == nl, (STATE['calls'], nl)
        cap = STATE['capture']
        STATE['capture'] = None
        return pkv, (cap / nl if capture else None)

    def query(cache, roles, queries, owner, gate, ids_out, other_ids):
        plen, n, qlen = len(roles), len(queries), max(map(len, queries))
        ids = torch.zeros((n, qlen), dtype=torch.long, device=dev)
        positions = torch.zeros_like(ids)
        live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i, -len(q):] = torch.tensor(q, device=dev)
            positions[i, -len(q):] = torch.arange(plen, plen + len(q), device=dev)
            live[i, -len(q):] = True
        keep = torch.tensor(roles, device=dev) != 1 - owner if gate else torch.ones(plen, dtype=torch.bool, device=dev)
        allowed = torch.cat([keep[None, None].expand(n, qlen, -1),
            live[:, None].expand(-1, qlen, -1) & torch.ones((qlen, qlen), dtype=torch.bool, device=dev).tril()[None]], -1)
        mask = torch.zeros(allowed.shape, dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(n)
        logits = model(input_ids=ids, position_ids=positions, attention_mask=mask[:, None], past_key_values=cp,
                       use_cache=True, logits_to_keep=1).logits[:, -1].float()
        top = logits.argmax(-1).cpu().tolist()
        return {'z': (logits[:, ids_out[1]] - logits[:, ids_out[0]]).cpu().tolist(), 'argmax_token': top,
                'other_source_word': [t in other_ids and t not in ids_out for t in top]}

    def attention_cells(d, att):
        sums = {c: [] for c in CELLS}
        for r in d['labels']:
            if d['meta'][r]['role'] != 0:
                continue
            for b in d['labels']:
                mb = d['meta'][b]
                if mb['role'] != 1 or b >= r:
                    continue
                cell = ('sameword' if mb['word'] == d['meta'][r]['word'] else 'diffword') + '_' + \
                       ('sameclass' if mb['cls'] == d['meta'][r]['cls'] else 'diffclass')
                sums[cell].append(float(att[r, b]))  # b = first answer token (the label word)
        return sums

    numeric = []
    rng_master = np.random.default_rng(args.seed + 7)
    with torch.inference_mode(), behavior_path.open('w') as stream:
        for ci, ctx in enumerate(cs):
            rng = np.random.default_rng(int(rng_master.integers(1 << 31)) + ci)
            if ci % shards != shard:
                continue
            queries = {o: [enc(f"Comment: {t}\nAnnotator: {ctx['names'][o]}\nLabel:") for t, _ in ctx['q']] for o in [0, 1]}
            conditions, removed, cells = {}, {w: {} for w in WORLDS}, {c: [] for c in CELLS}
            for ns, policies in PLAN.items():
                for world in WORLDS:
                    native_att = None
                    for policy in policies:
                        d = encoded[ci][key(world, ns, policy)]
                        base = policy.split(':')[-1]
                        allowed = allowed_for(d, policy, native_att, rng)
                        norenorm = None
                        if base == 'answer_norenorm':
                            norenorm = causal(len(d['ids'])) & ~allowed_for(d, 'answer_cross_off')
                        cache, att = prefill(d, allowed, norenorm, capture=(policy == 'normal' and ns == 'shared'))
                        if att is not None:
                            native_att = att
                            for c, v in attention_cells(d, att).items():
                                cells[c].extend(v)
                        if ns == 'shared' and base in ['answer_cross_off', 'matched_count', 'matched_mass'] and ':' not in policy:
                            removed[world][base] = removed_mass(d, allowed, native_att)
                        for scope in ['native', 'gate']:
                            for o in [0, 1]:
                                ids_out, other = ns_ids[ns][o], ns_ids[ns][1 - o]
                                v = query(cache, d['roles'], queries[o], o, scope == 'gate', ids_out, other)
                                v['gold'] = truth(ctx, world, o)
                                v['argmax_correct'] = [t == ids_out[int(g > 0)] for t, g in zip(v['argmax_token'], v['gold'])]
                                conditions[f'{world}_{ns}_{policy}_{scope}_{o}'] = v
                        if ci < shards and world == 'origin' and policy == 'normal' and ns == 'shared':
                            for qi, q in enumerate(queries[0][:2]):
                                logits = model(input_ids=torch.tensor([d['ids'] + q], device=dev), use_cache=False,
                                               logits_to_keep=1).logits[0, -1].float()
                                numeric.append(abs(float(logits[ns_ids[ns][0][1]] - logits[ns_ids[ns][0][0]])
                                                   - conditions[f'{world}_{ns}_normal_native_0']['z'][qi]))
                        del cache
            assert not numeric or max(numeric) <= 1e-3, numeric
            stream.write(json.dumps({'context': ci, 'conditions': conditions, 'removed_mass': removed,
                                     'attention_2x2': {c: (float(np.mean(v)) if v else None) for c, v in cells.items()}}) + '\n')
            stream.flush()
            print(ci + 1, '/', args.n, 'numeric', max(numeric) if numeric else None, round(time.time() - started), flush=True)
    elapsed = time.time() - started
    (dest / f'run.shard{shard}.json').write_text(json.dumps({'args': vars(args), 'model_type': model.config.model_type,
        'num_layers': nl, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256': hashlib.sha256((dest / 'contexts.jsonl').read_bytes()).hexdigest(),
        'numeric_max_error': max(numeric) if numeric else None, 'dtype': 'float32', 'attention': 'eager',
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600}, indent=1) + '\n')
    if shards == 1:
        analyze(dest)


if __name__ == '__main__':
    main()
