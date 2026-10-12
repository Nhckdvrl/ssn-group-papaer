"""E132: which cross-source formation edges let the model tell two sources' rules apart?

Extends the E123 SST-5 engine (identical token stream) with edge-type policies, label-word role swaps,
layer-band localisation of the answer-to-label path and attention-mass readouts. See
experiments/E132-which-cross-source-edges-separate-rules.md.
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

WORLDS = ['origin', 'cross', 'within']
NAMESPACES = {'shared': (['no', 'yes'], ['no', 'yes']), 'far': (['no', 'yes'], ['pass', 'flag']),
              'shared_pf': (['pass', 'flag'], ['pass', 'flag']), 'far_swap': (['pass', 'flag'], ['no', 'yes'])}
FULL_POLICIES = ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names', 'iso_comments', 'iso_answers',
                 'no_answer_senders']
CORE_POLICIES = ['normal', 'answer_cross_off', 'all_cross_off']
LARGE_POLICIES = ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names', 'iso_comments', 'iso_answers']
BANDS = 4
ATT_KEYS = ['B_answer_same', 'B_answer_diff', 'A_answer_same', 'A_answer_diff', 'B_name', 'B_comment', 'A_comment']


def truth(ctx, world, owner):
    gold = np.asarray([(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']])
    if owner == 1 and world != 'cross':
        gold = -gold
    return gold.tolist()


def design(large):
    if large:
        return {ns: LARGE_POLICIES for ns in ['shared', 'far']}, ['origin', 'cross'], False
    return {'shared': FULL_POLICIES, 'far': FULL_POLICIES, 'shared_pf': CORE_POLICIES, 'far_swap': CORE_POLICIES}, WORLDS, True


def analyze(dest):
    rows = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    run = json.loads((dest / 'preflight.json').read_text())
    plan, worlds, bands = design(run['args']['large'])
    C = rows[0]['conditions']
    out = {'n_contexts': len(rows), 'accuracy': {}, 'delta': {}, 'contrasts': {}, 'bands': {}, 'attention': {}}

    def acc(key):  # context-level full-vocabulary accuracy
        return np.array([np.mean(r['conditions'][key]['argmax_correct']) for r in rows])

    def other_word(key):
        return np.array([np.mean(r['conditions'][key]['other_source_word']) for r in rows])

    def z(key):
        return np.array([r['conditions'][key]['z'] for r in rows])

    gA = np.array([r['conditions'][f'origin_shared_normal_native_0']['gold'] for r in rows])
    for ns, policies in plan.items():
        for policy in policies:
            for scope in ['native', 'gate']:
                cells = {(w, o): acc(f'{w}_{ns}_{policy}_{scope}_{o}') for w in ['origin', 'cross'] for o in [0, 1]}
                summary = {'both': np.mean(list(cells.values()), 0), 'A': (cells['origin', 0] + cells['cross', 0]) / 2,
                           'B': (cells['origin', 1] + cells['cross', 1]) / 2,
                           'opposite': (cells['origin', 0] + cells['origin', 1]) / 2,
                           'same': (cells['cross', 0] + cells['cross', 1]) / 2,
                           'other_source_word': np.mean([other_word(f'{w}_{ns}_{policy}_{scope}_{o}')
                                                         for w in ['origin', 'cross'] for o in [0, 1]], 0)}
                out['accuracy'][f'{ns}_{policy}_{scope}'] = {k: interval(v) for k, v in summary.items()}
                orig, cross = z(f'origin_{ns}_{policy}_{scope}_0'), z(f'cross_{ns}_{policy}_{scope}_0')
                d = (.5 * (cross - orig) * gA).mean(1)
                flips = (np.sign(cross) != np.sign(orig)).mean(1)
                entry = {'signed': interval(d), 'absolute': interval(abs(d)), 'flip_rate': interval(flips),
                         'query_abs': interval(abs(.5 * (cross - orig)).mean(1))}
                if 'within' in worlds:
                    wz = z(f'within_{ns}_{policy}_{scope}_0')
                    dw = (.5 * (wz - orig) * gA).mean(1)
                    entry.update({'within_signed': interval(dw), 'within_absolute': interval(abs(dw)),
                                  'within_flip_rate': interval((np.sign(wz) != np.sign(orig)).mean(1)),
                                  'within_query_abs': interval(abs(.5 * (wz - orig)).mean(1)),
                                  'flip_minus_within': interval(flips - (np.sign(wz) != np.sign(orig)).mean(1))})
                out['delta'][f'{ns}_{policy}_{scope}'] = entry
            if policy != 'normal':
                for scope in ['native', 'gate']:
                    def cell(p, part):
                        k = f'{ns}_{p}_{scope}'
                        cells = {(w, o): acc(f'{w}_{ns}_{p}_{scope}_{o}') for w in ['origin', 'cross'] for o in [0, 1]}
                        return {'both': np.mean(list(cells.values()), 0),
                                'opposite': (cells['origin', 0] + cells['origin', 1]) / 2}[part]
                    for part in ['both', 'opposite']:
                        out['contrasts'][f'{ns}_{policy}_minus_normal_{scope}_{part}'] = interval(cell(policy, part) - cell('normal', part))
                        if policy.startswith('iso_') or policy == 'no_answer_senders':
                            out['contrasts'][f'{ns}_{policy}_minus_all_{scope}_{part}'] = interval(cell(policy, part) - cell('all_cross_off', part))
    if bands:
        base = (.5 * (z('cross_shared_normal_gate_0') - z('origin_shared_normal_gate_0')) * gA).mean(1)
        for k in range(BANDS):
            d = (.5 * (z(f'cross_shared_band{k}_gate_0') - z(f'origin_shared_band{k}_gate_0')) * gA).mean(1)
            out['bands'][str(k)] = {'signed': interval(d), 'reduction': interval(base - d)}
    att = [r['attention'] for r in rows]
    for ns in ['shared', 'far']:
        for key in ATT_KEYS:
            arr = np.array([a[ns][key] for a in att])  # contexts x layers
            out['attention'][f'{ns}_{key}'] = {'per_layer_mean': arr.mean(0).tolist(), 'all_layers': interval(arr.mean(1))}
    sh_b = np.array([np.array(a['shared']['B_answer_same']) + np.array(a['shared']['B_answer_diff']) for a in att]).mean(1)
    far_b = np.array([np.array(a['far']['B_answer_same']) + np.array(a['far']['B_answer_diff']) for a in att]).mean(1)
    out['attention']['B_answer_shared_minus_far'] = interval(sh_b - far_b)
    same = np.array([a['shared']['B_answer_same_per_token'] for a in att]).mean(1)
    diff = np.array([a['shared']['B_answer_diff_per_token'] for a in att]).mean(1)
    out['attention']['shared_B_answer_same_minus_diff_per_token'] = interval(same - diff)
    (dest / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=132001)
    ap.add_argument('--materials', choices=['discovery', 'validation'], default='discovery')
    ap.add_argument('--large', action='store_true')
    ap.add_argument('--shard', default='0/1')
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
    plan, worlds, bands = design(args.large)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    cs, natural_metadata = make_contexts(tok, args.n, args.seed, args.materials)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    words = sorted({w for a, b in NAMESPACES.values() for w in a + b})
    assert all(len(enc(' ' + w)) == 1 for w in words)
    wid = {w: enc(' ' + w)[0] for w in words}
    ns_ids = {ns: ([wid[w] for w in a], [wid[w] for w in b]) for ns, (a, b) in NAMESPACES.items()}

    def prefix(ctx, world, namespace):
        ids, roles, types = enc(HEAD), [-1] * len(enc(HEAD)), ['h'] * len(enc(HEAD))
        labels, answers, label_word = [], [[], []], {}
        for (comment, role, y), name in zip(ctx['demos'], ctx['shown']):
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
            label_word[anchor] = wid[word]
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
            types.extend(kinds + ['a'] * len(answer))
        return ids, roles, labels, answers, types, label_word

    encoded = [{(w, ns): prefix(c, w, ns) for w in worlds for ns in plan} for c in cs]
    for worlds_data in encoded:
        ref = worlds_data[worlds[0], 'shared']
        for value in worlds_data.values():
            assert len(value[0]) == len(ref[0]) and value[1:4] == ref[1:4] and value[4] == ref[4]
    (dest / 'preflight.json').write_text(json.dumps({'args': vars(args), 'plan': plan, 'worlds': worlds,
        'bands': bands, 'namespaces': NAMESPACES, 'word_ids': wid, 'natural_materials': natural_metadata,
        'prefix_lengths': [len(w[worlds[0], 'shared'][0]) for w in encoded],
        'token_type_counts': [{t: w[worlds[0], 'shared'][4].count(t) for t in 'hcnqa'} for w in encoded]}, indent=1) + '\n')
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
        device_map='auto' if args.large else 'cuda', attn_implementation='eager').eval()
    model.requires_grad_(False)
    dev = model.get_input_embeddings().weight.device
    layers = model.model.layers
    nl = len(layers)
    numeric, consumption = [], {}

    def build_mask(data, policy):
        ids, roles, labels, answers, types, _ = data
        n = len(ids)
        allowed = torch.ones((n, n), dtype=torch.bool, device=dev).tril()
        R = np.array(roles)
        T = np.array(types)
        for owner in [0, 1]:
            other = 1 - owner
            if policy in ['normal']:
                continue
            if policy.startswith('answer_cross_off') or policy.startswith('band'):
                receivers = [a for a in labels if roles[a] == owner]
                senders = answers[other]
            elif policy == 'no_answer_senders':
                receivers = np.where(R == owner)[0].tolist()
                senders = answers[other]
            else:
                keep = {'all_cross_off': '', 'iso_names': 'n', 'iso_comments': 'c', 'iso_answers': 'a'}[policy]
                receivers = np.where(R == owner)[0].tolist()
                senders = [i for i in np.where(R == other)[0].tolist() if T[i] not in keep]
            rr = torch.tensor(receivers, device=dev, dtype=torch.long)
            ss = torch.tensor(senders, device=dev, dtype=torch.long)
            if len(rr) and len(ss):
                past = ss[None, :] < rr[:, None]
                allowed[rr[:, None], ss[None, :]] &= ~past
        return torch.zeros((1, 1, n, n), dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))

    def prefill(data, policy, attention=False):
        n = len(data[0])
        full = torch.zeros((1, 1, n, n), dtype=torch.float32, device=dev).masked_fill_(
            ~torch.ones((n, n), dtype=torch.bool, device=dev).tril(), float('-inf'))
        if policy.startswith('band'):
            k = int(policy[4:])
            block = build_mask(data, 'answer_cross_off')
            lo, hi = k * nl // BANDS, (k + 1) * nl // BANDS
            per_layer = {i: (block if lo <= i < hi else full) for i in range(nl)}
            mask = full
        else:
            mask = build_mask(data, policy)
            per_layer = None
        record = consumption.setdefault(policy, {})

        def hook(module, aa, kw):
            i = module.layer_idx
            record[i] = record.get(i, 0) + 1
            if per_layer is not None:
                kw['attention_mask'] = per_layer[i].to(kw['attention_mask'].device)
            return aa, kw
        handles = [layer.self_attn.register_forward_pre_hook(hook, with_kwargs=True) for layer in layers]
        try:
            outputs = model(input_ids=torch.tensor([data[0]], device=dev), attention_mask=mask, use_cache=True,
                            logits_to_keep=1, output_attentions=attention)
        finally:
            for h in handles:
                h.remove()
        return outputs.past_key_values, (outputs.attentions if attention else None)

    def attention_summary(data, attentions):
        ids, roles, labels, answers, types, label_word = data
        R, T = np.array(roles), np.array(types)
        a_labels = [a for a in labels if roles[a] == 0]
        out = {k: [] for k in ATT_KEYS}
        out['B_answer_same_per_token'], out['B_answer_diff_per_token'] = [], []

        def span(a):
            i = a
            while i < len(T) and T[i] == 'a' and R[i] == R[a]:
                i += 1
            return list(range(a, i))
        for att in attentions:
            m = att[0].float().mean(0).cpu().numpy()  # heads averaged: [T, T]
            sums = {k: [] for k in ATT_KEYS}
            per_tok = {'same': [], 'diff': []}
            for r in a_labels:
                earlier = np.arange(r)
                own_word = label_word[r]
                for side, owner in [('B', 1), ('A', 0)]:
                    ans_first = [a for a in labels if roles[a] == owner and a < r]
                    same = [i for a in ans_first if label_word[a] == own_word for i in span(a) if i < r]
                    diff = [i for a in ans_first if label_word[a] != own_word for i in span(a) if i < r]
                    sums[f'{side}_answer_same'].append(m[r, same].sum())
                    sums[f'{side}_answer_diff'].append(m[r, diff].sum())
                    if side == 'B':
                        per_tok['same'].append(m[r, same].mean() if same else np.nan)
                        per_tok['diff'].append(m[r, diff].mean() if diff else np.nan)
                sums['B_name'].append(m[r, earlier[(R[:r] == 1) & (T[:r] == 'n')]].sum())
                sums['B_comment'].append(m[r, earlier[(R[:r] == 1) & (T[:r] == 'c')]].sum())
                sums['A_comment'].append(m[r, earlier[(R[:r] == 0) & (T[:r] == 'c')]].sum())
            for k in ATT_KEYS:
                out[k].append(float(np.mean(sums[k])))
            out['B_answer_same_per_token'].append(float(np.nanmean(per_tok['same'])))
            out['B_answer_diff_per_token'].append(float(np.nanmean(per_tok['diff'])))
        return out

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

    with torch.inference_mode(), behavior_path.open('w') as stream:
        for ci, ctx in enumerate(cs):
            if ci % shards != shard:
                continue
            queries = {o: [enc(f"Comment: {t}\nAnnotator: {ctx['names'][o]}\nLabel:") for t, _ in ctx['q']] for o in [0, 1]}
            conditions, attention = {}, {}
            for ns, policies in plan.items():
                for world in worlds:
                    data = encoded[ci][world, ns]
                    todo = list(policies) + ([f'band{k}' for k in range(BANDS)] if bands and ns == 'shared' and world != 'within' else [])
                    for policy in todo:
                        want_att = policy == 'normal' and world == 'origin' and ns in ['shared', 'far']
                        cache, att = prefill(data, policy, attention=want_att)
                        if want_att:
                            attention[ns] = attention_summary(data, att)
                            del att
                        scopes = ['gate'] if policy.startswith('band') else ['native', 'gate']
                        owners = [0] if policy.startswith('band') else [0, 1]
                        for scope in scopes:
                            for o in owners:
                                ids_out = ns_ids[ns][o]
                                other = ns_ids[ns][1 - o]
                                v = query(cache, data[1], queries[o], o, scope == 'gate', ids_out, other)
                                v['gold'] = truth(ctx, world, o)
                                v['argmax_correct'] = [t == ids_out[int(g > 0)] for t, g in zip(v['argmax_token'], v['gold'])]
                                conditions[f'{world}_{ns}_{policy}_{scope}_{o}'] = v
                        if ci < shards and world == worlds[0] and policy == 'normal' and ns == 'shared':
                            for qi, q in enumerate(queries[0][:2]):
                                logits = model(input_ids=torch.tensor([data[0] + q], device=dev), use_cache=False,
                                               logits_to_keep=1).logits[0, -1].float()
                                ref = conditions[f'{world}_{ns}_normal_native_0']['z'][qi]
                                numeric.append(abs(float(logits[ns_ids[ns][0][1]] - logits[ns_ids[ns][0][0]]) - ref))
                        del cache
            assert not numeric or max(numeric) <= 1e-3, numeric
            stream.write(json.dumps({'context': ci, 'conditions': conditions, 'attention': attention}) + '\n')
            stream.flush()
            print(ci + 1, '/', args.n, 'numeric', max(numeric) if numeric else None, round(time.time() - started), flush=True)
    elapsed = time.time() - started
    (dest / f'run.shard{shard}.json').write_text(json.dumps({'args': vars(args), 'model_type': model.config.model_type,
        'num_layers': nl, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256': hashlib.sha256((dest / 'contexts.jsonl').read_bytes()).hexdigest(),
        'numeric_max_error': max(numeric) if numeric else None,
        'all_layer_consumption': {k: sorted(set(v.values())) for k, v in consumption.items()},
        'dtype': 'float32', 'attention': 'eager', 'python': platform.python_version(), 'torch': torch.__version__,
        'transformers': transformers.__version__, 'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600 * (
            torch.cuda.device_count() if args.large else 1)}, indent=1) + '\n')
    if shards == 1:
        analyze(dest)


if __name__ == '__main__':
    main()
