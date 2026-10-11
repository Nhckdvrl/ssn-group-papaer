"""E98: fixed one-position, all-layer criterion trajectory transport.

All receivers are recomputed from raw Own-only text with no past cache. This is
an external trajectory intervention, not a single latent vector or native cut.
"""
import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import time
from collections import Counter
from pathlib import Path

from e95_source_grouping import body, estimate, world
from e97_goal_comparison import key as e97_key

SYSTEM = 'Infer rules from the examples. Return only the requested one-word answer.'
OWN_HEADER = ('The reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
              'or service pace (quick or leisurely). The reviewer has a personal preference for one of the two values '
              'of that aspect. yes means the experience matches that personal preference; no means it does not. '
              'Infer the rule from the examples.\n\n')


def jsonl(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def own(c, preference):
    text = OWN_HEADER
    for d in world(c, preference, 0, 1):
        if d['role'] == 0:
            text += f'Reviewer: {c["names"][0]}\nReview: {d["text"]}\nLabel: {"yes" if d["y"] == 1 else "no"}\n\n'
    assert all(name not in text for name in c['names'][1:])
    return text


def cue(c, criterion):
    aspect = 'food spiciness' if criterion == 0 else 'service pace'
    return f'{c["names"][0]} judges only {aspect}. Infer their personal preference from their examples.\n\n'


def build(tok, source, e97, stage):
    contexts = jsonl(source/'contexts.jsonl')[:2]
    assert len(contexts) == 2
    donors, rows = {}, []
    all_parent_prompts = [r for i in range(3) for r in jsonl(e97/f'qwen35_part{i}'/'prompts.jsonl')]
    all_parent_rows = jsonl(e97/'behavior_merged.jsonl')
    prompts = {e97_key(r): r for r in all_parent_prompts}
    assert len(prompts) == len(all_parent_prompts) == len(all_parent_rows) == 160
    parents = [r for r in all_parent_rows if r['kind'] == 'bool_no_review']
    assert len(parents) == 32 and len({e97_key(r) for r in parents}) == 32
    assert all(r['query'] is None for r in parents)

    def encode(s):
        return tok.encode(s, add_special_tokens=False)

    def chat(s, thinking=False):
        return tok.apply_chat_template([{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': s}],
                                       tokenize=False, add_generation_prompt=True, enable_thinking=thinking,
                                       reasoning_effort='medium')

    def port(c):
        return f'Reviewer: {c["names"][0]}\nReview:'

    def one_turn_prefix(c, prelude):
        full = chat(prelude+port(c))
        end = full.rfind(port(c))+len(port(c))
        assert end >= len(port(c)) and full[:end].endswith(port(c))
        ids = encode(full[:end])
        assert encode(full)[:len(ids)] == ids
        return ids

    def donor_id(kind, ci, pd, criterion, pb=None, asked=None):
        return f'{kind}:ctx{ci}:pd{pd}:c{criterion}:pb{pb}:asked{asked}'

    def add_donor(c, kind, pd, criterion, pb=None, asked=None, parent=None):
        identity = donor_id(kind, c['context'], pd, criterion, pb, asked)
        if identity in donors:
            return identity
        previous_answer = None
        if kind == 'explicit':
            ids = one_turn_prefix(c, own(c, pd)+cue(c, criterion))
        elif kind == 'raw':
            full = body(c, 'criterion', pd, criterion, pb, None)
            full = full[:full.index('Which single aspect do all three reviewers judge?')]
            ids = one_turn_prefix(c, full)
        elif kind == 'prepared':
            actual = prompts[e97_key(parent)]
            for field in ('context', 'pa', 'cb', 'pb', 'kind', 'query', 'asked', 'gold'):
                assert actual[field] == parent[field]
            prompt_ids = encode(chat(actual['body'], thinking=True))
            generated_ids = parent['score']['token_ids'][:]
            assert generated_ids and generated_ids[-1] == tok.eos_token_id
            assert tok.eos_token_id not in generated_ids[:-1]
            assert tok.convert_tokens_to_ids('</think>') in generated_ids
            # Preserve the exact generated IDs. In particular, never decode the
            # reasoning and retokenize it as a freshly formatted assistant turn.
            tail_ids = encode('\n<|im_start|>user\n'+port(c))
            ids = prompt_ids+generated_ids+tail_ids
            assert ids[:len(prompt_ids)] == prompt_ids
            assert ids[len(prompt_ids):len(prompt_ids)+len(generated_ids)] == generated_ids
            previous_answer = parent['score']['class']
            assert previous_answer in (-1, 0, 1)
        else:
            raise ValueError(kind)
        donors[identity] = {'id': identity, 'kind': kind, 'context': c['context'], 'pd': pd,
                            'criterion': criterion, 'pb': pb, 'asked': asked,
                            'previous_bool': previous_answer, 'input_ids': ids,
                            'carrier_index': len(ids)-1, 'future_review_seen': False}
        # Literal held-out reviews must not occur in donor text or generation.
        decoded = tok.decode(ids, skip_special_tokens=False)
        assert all(q['text'] not in decoded for q in c['queries'])
        return identity

    def add_receiver(c, kind, pr, criterion, qi, did=None):
        prelude = own(c, pr)+(cue(c, criterion) if kind == 'text' else '')
        q = c['queries'][qi]
        text = prelude+port(c)+f' {q["text"]}\nGive this reviewer\'s yes/no label for the review.\n'
        full = chat(text)+'Answer:'
        start = full.rfind(port(c))
        assert start >= 0
        end = start+len(port(c))
        prefix_ids = encode(full[:end]); ids = encode(full)
        assert ids[:len(prefix_ids)] == prefix_ids
        assert prefix_ids == one_turn_prefix(c, prelude)
        assert all(name not in full for name in c['names'][1:])
        d = donors[did] if did else {}
        r = {'kind': kind, 'context': c['context'], 'pr': pr, 'pd': d.get('pd'),
             'criterion': criterion, 'pb': d.get('pb'), 'asked': d.get('asked'),
             'previous_bool': d.get('previous_bool'), 'query': qi, 'x': q['x'],
             'discordant': q['x'][0] != q['x'][1], 'donor_id': did,
             'gold': pr*q['x'][criterion] if criterion is not None else None,
             'donor_gold': d['pd']*q['x'][criterion] if did else None,
             'input_ids': ids, 'carrier_index': len(prefix_ids)-1,
             'own_text': full, 'foreign_source_names_absent': True}
        r['id'] = '|'.join(str(r[k]) for k in ('kind', 'context', 'pr', 'pd', 'criterion', 'pb', 'asked', 'query'))
        rows.append(r)

    if stage == 'positive':
        for c in contexts:
            for pr, qi in itertools.product((1, -1), range(4)):
                add_receiver(c, 'base', pr, None, qi)
            for pr, criterion, qi in itertools.product((1, -1), (0, 1), range(4)):
                add_receiver(c, 'text', pr, criterion, qi)
            for pd, criterion in itertools.product((1, -1), (0, 1)):
                did = add_donor(c, 'explicit', pd, criterion)
                for pr, qi in itertools.product((1, -1), range(4)):
                    add_receiver(c, 'explicit', pr, criterion, qi, did)
        assert Counter(r['kind'] for r in rows) == {'base': 16, 'text': 32, 'explicit': 64}
    else:
        by_context = {c['context']: c for c in contexts}
        for parent in parents:
            c = by_context[parent['context']]
            did = add_donor(c, 'prepared', parent['pa'], parent['cb'], parent['pb'], parent['asked'], parent)
            for pr, qi in itertools.product((1, -1), range(4)):
                add_receiver(c, 'prepared', pr, parent['cb'], qi, did)
        for c in contexts:
            for pd, criterion, pb in itertools.product((1, -1), (0, 1), (1, -1)):
                did = add_donor(c, 'raw', pd, criterion, pb)
                for pr, qi in itertools.product((1, -1), range(4)):
                    add_receiver(c, 'raw', pr, criterion, qi, did)
        assert Counter(r['kind'] for r in rows) == {'prepared': 256, 'raw': 128}
    assert len({r['id'] for r in rows}) == len(rows)
    carrier_ids = {r['input_ids'][r['carrier_index']] for r in rows}
    carrier_ids |= {r['input_ids'][r['carrier_index']] for r in donors.values()}
    assert len(carrier_ids) == 1, carrier_ids
    # Compare Own prefixes to the actual E96 prompts, not only duplicated code.
    old_own = [r for r in jsonl(Path('results/e96/qwen35_direct/prompts.jsonl')) if r['kind'] == 'own_none']
    for c in contexts:
        for pr in (1, -1):
            refs = [r for r in old_own if r['context'] == c['context'] and r['pa'] == pr]
            assert refs and all(r['body'].startswith(own(c, pr)) for r in refs)
    audit = {'stage': stage, 'n_rows': len(rows), 'unique_keys': len({r['id'] for r in rows}),
             'kind_counts': dict(Counter(r['kind'] for r in rows)), 'n_donors': len(donors),
             'carrier_token_id': next(iter(carrier_ids)), 'all_64_layer_inputs_one_position': True,
             'future_review_excluded_from_donors': True, 'recipient_foreign_names_absent': True,
             'recipient_cache_policy': 'fresh raw Own forward; past_key_values=None; use_cache=False',
             'pd_pr_full_cross': True, 'e97_parent_rows': len(parents), 'parent_selection_by_correctness': False,
             'prepared_generated_token_ids_preserved_exactly': True if stage == 'transfer' else None,
             'context_sha256': hashlib.sha256((source/'contexts.jsonl').read_bytes()).hexdigest(),
             'e97_behavior_sha256': hashlib.sha256((e97/'behavior_merged.jsonl').read_bytes()).hexdigest(),
             'baseline_gold_policy': 'average over both compatible criteria; no unique mixed gold'}
    return contexts, donors, rows, audit


def analyze(rows, errors):
    """All estimates average contexts; no filtering by prediction or donor success."""
    out = {'n_rows': len(rows), 'behavior': {}, 'contrasts': {}, 'profile_accuracy': {}, 'errors': errors}

    def summarize(rr, fn):
        ids = sorted({r['context'] for r in rr})
        return estimate([sum(fn(r) for r in rr if r['context'] == ci)/sum(r['context'] == ci for r in rr) for ci in ids])

    def criterion_acc(r, binary=False):
        pred = r['score']['binary_class' if binary else 'class']
        if r['criterion'] is None:
            return sum(pred == r['pr']*r['x'][c] for c in (0, 1))/2
        return pred == r['gold']

    for kind in sorted({r['kind'] for r in rows}):
        rr = [r for r in rows if r['kind'] == kind]
        stats = {}
        for subset in ('all', 'mixed', 'concordant', 'opposite_mixed', 'opposite_concordant', 'same_mixed'):
            ss = [r for r in rr if subset == 'all' or
                  subset == 'mixed' and r['discordant'] or
                  subset == 'concordant' and not r['discordant'] or
                  subset == 'opposite_mixed' and r['pd'] == -r['pr'] and r['discordant'] or
                  subset == 'opposite_concordant' and r['pd'] == -r['pr'] and not r['discordant'] or
                  subset == 'same_mixed' and r['pd'] == r['pr'] and r['discordant']]
            if not ss:
                continue
            sm = {'n_rows': len(ss), 'argmax_accuracy': summarize(ss, criterion_acc),
                  'binary_accuracy': summarize(ss, lambda r: criterion_acc(r, True)),
                  'valid_fraction': summarize(ss, lambda r: r['score']['valid']),
                  'mean_z_nats': summarize(ss, lambda r: r['score']['z'])}
            if kind != 'base':
                sm['recipient_margin_nats'] = summarize(ss, lambda r: r['gold']*r['score']['z'])
            if all(r['donor_gold'] is not None for r in ss):
                sm['donor_function_accuracy'] = summarize(ss, lambda r: r['score']['class'] == r['donor_gold'])
            if all(r['previous_bool'] is not None for r in ss):
                sm['previous_bool_match'] = summarize(ss, lambda r: r['score']['class'] == r['previous_bool'])
            stats[subset] = sm
        if kind != 'base':
            stats['private_criterion_profiles'] = {}
            for pr, criterion in itertools.product((1, -1), (0, 1)):
                ss = [r for r in rr if r['pr'] == pr and r['criterion'] == criterion and r['discordant']]
                stats['private_criterion_profiles'][f'pr{pr}_c{criterion}'] = {
                    'argmax_accuracy': summarize(ss, criterion_acc),
                    'recipient_margin_nats': summarize(ss, lambda r: r['gold']*r['score']['z'])}
        out['behavior'][kind] = stats
        if kind == 'base':
            continue
        lut = {(r['context'], r['pd'], r['pr'], r['criterion'], r['pb'], r['asked'], r['query']): r for r in rr}
        paired = []
        for r in rr:
            if not r['discordant']:
                continue
            other = lut[r['context'], r['pd'], r['pr'], 1-r['criterion'], r['pb'], r['asked'], r['query']]
            paired.append({'context': r['context'], 'response': r['gold']*(r['score']['z']-other['score']['z'])/2,
                           'both': r['score']['class'] == r['gold'] and other['score']['class'] == other['gold'],
                           'flip': r['score']['valid'] and other['score']['valid'] and r['score']['class'] != other['score']['class']})
        out['contrasts'][kind] = {'criterion_response_nats': summarize(paired, lambda r: r['response']),
                                 'criterion_pair_both_correct': summarize(paired, lambda r: r['both']),
                                 'criterion_flip_rate': summarize(paired, lambda r: r['flip'])}
        groups = {}
        for r in rr:
            k = tuple(r[f] for f in ('context', 'pd', 'pr', 'criterion', 'pb', 'asked'))
            groups.setdefault(k, []).append(r)
        profiles = []
        for k, pp in groups.items():
            assert sorted(r['query'] for r in pp) == list(range(4))
            profiles.append({'context': k[0], 'correct': all(r['score']['class'] == r['gold'] for r in pp)})
        out['profile_accuracy'][kind] = summarize(profiles, lambda r: r['correct'])
        if kind == 'prepared':
            v = []
            for r in rr:
                other = lut[r['context'], r['pd'], r['pr'], r['criterion'], r['pb'], 1-r['asked'], r['query']]
                v.append({'context': r['context'], 'flip': r['score']['valid'] and other['score']['valid'] and r['score']['class'] != other['score']['class'],
                          'abs_z': abs(r['score']['z']-other['score']['z'])})
            out['contrasts'][kind]['asked_aspect_flip_rate'] = summarize(v, lambda r: r['flip'])
            out['contrasts'][kind]['asked_aspect_absolute_z_difference'] = summarize(v, lambda r: r['abs_z'])
    if 'explicit' in out['behavior']:
        rr = [r for r in rows if r['kind'] == 'explicit' and r['pd'] == -r['pr']]
        mixed = [r for r in rr if r['discordant']]; concordant = [r for r in rr if not r['discordant']]
        m = sum(r['score']['class'] == r['gold'] for r in mixed)
        c = sum(r['score']['class'] == r['gold'] for r in concordant)
        assert len(mixed) == len(concordant) == 16
        out['interface_gate'] = {'opposite_mixed_correct': m, 'opposite_mixed_n': 16,
                                 'opposite_concordant_correct': c, 'opposite_concordant_n': 16,
                                 'pass': m >= 12 and c >= 14 and errors['self_copy_max_nats'] <= .001}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--source', default='results/e95/qwen35_discovery')
    ap.add_argument('--e97', default='results/e97')
    ap.add_argument('--out', required=True)
    ap.add_argument('--stage', choices=('positive', 'transfer'), required=True)
    ap.add_argument('--positive-result', default='results/e98/qwen35_positive/analysis.json')
    ap.add_argument('--batch-size', type=int, default=4)
    ap.add_argument('--design-only', action='store_true')
    a = ap.parse_args(); p = Path(a.out); p.mkdir(parents=True, exist_ok=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True); tok.padding_side = 'left'
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    cs, donors, planned, audit = build(tok, Path(a.source), Path(a.e97), a.stage)
    config = json.loads((Path(a.model)/'config.json').read_text()); config = config.get('text_config', config)
    assert config['num_hidden_layers'] == 64 and config['model_type'] == 'qwen3_5_text'
    lids = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]
    assert all(len(v) == 1 for v in lids); lids = [v[0] for v in lids]
    audit.update(model_type=config['model_type'], num_layers=64, label_ids=lids,
                 model_config_sha256=hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (p/'design_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    if a.design_only:
        print(json.dumps(audit)); return
    if a.stage == 'transfer':
        gate = json.loads(Path(a.positive_result).read_text())['interface_gate']
        assert gate['pass'], 'Frozen interface gate did not pass; do not run transfer.'
    assert not (p/'behavior.jsonl').exists(), 'Refuse to overwrite scientific rows.'
    (p/'donors.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in donors.values()))
    (p/'planned.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in planned))
    import torch, transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0)
    t0 = time.time(); print('Loading float32/eager two-GPU', a.stage, flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
        device_map='auto', max_memory={0: '64GiB', 1: '64GiB'}, attn_implementation='eager', output_loading_info=True)
    model.eval(); model.requires_grad_(False)
    assert not loading.get('missing_keys'), loading
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    assert set(model.hf_device_map.values()) <= {0, 1, 'cuda:0', 'cuda:1'}, model.hf_device_map
    assert len(model.model.layers) == 64
    (p/'loading_info.json').write_text(json.dumps(loading, indent=2, default=str)+'\n')
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'audit': audit,
        'device_map': model.hf_device_map, 'precision': 'float32', 'attention': 'eager',
        'cache': None, 'use_cache': False}, indent=2)+'\n')
    errors = {'self_copy_max_nats': 0., 'non_carrier_max': 0., 'self_copy_checked': False}
    captured_norms = []; output = []

    def forward(records, trajectory=None, capture=False):
        width = max(len(r['input_ids']) for r in records)
        xx = torch.tensor([[tok.pad_token_id]*(width-len(r['input_ids']))+r['input_ids'] for r in records], device='cuda:0')
        mask = torch.tensor([[0]*(width-len(r['input_ids']))+[1]*len(r['input_ids']) for r in records], device='cuda:0')
        positions = (mask.cumsum(-1)-1).clamp_min(0)
        carrier = [width-len(r['input_ids'])+r['carrier_index'] for r in records]
        caught = {}; handles = []
        for layer, module in enumerate(model.model.layers):
            def hook(mod, args, kwargs, layer=layer):
                from_args = bool(args)
                h = args[0] if from_args else kwargs['hidden_states']
                assert h.shape[0] == len(records) and h.shape[1] == width
                if capture:
                    caught[layer] = torch.stack([h[i, pos].detach().cpu().clone() for i, pos in enumerate(carrier)])
                if trajectory is None:
                    return None
                value = trajectory[layer]
                assert value.shape[-1] == h.shape[-1] and value.shape[0] in (1, len(records))
                edited = h.clone(); value = value.to(h.device, dtype=h.dtype)
                for i, pos in enumerate(carrier):
                    edited[i, pos] = value[0 if value.shape[0] == 1 else i]
                changed = torch.zeros(h.shape[:2], dtype=torch.bool, device=h.device)
                for i, pos in enumerate(carrier):
                    changed[i, pos] = True
                er = float((edited[~changed]-h[~changed]).abs().max()) if (~changed).any() else 0.
                errors['non_carrier_max'] = max(errors['non_carrier_max'], er); assert er == 0
                if from_args:
                    return (edited,)+args[1:], kwargs
                revised = dict(kwargs); revised['hidden_states'] = edited
                return args, revised
            handles.append(module.register_forward_pre_hook(hook, with_kwargs=True))
        try:
            result = model(input_ids=xx, attention_mask=mask, position_ids=positions,
                           past_key_values=None, use_cache=False, logits_to_keep=1)
            assert result.past_key_values is None
            logits = result.logits[:, -1].float().cpu()
        finally:
            for handle in handles:
                handle.remove()
        assert not capture or len(caught) == 64
        return logits, caught

    def score(records, logits, stream):
        for r, lo in zip(records, logits):
            z = float(lo[lids[1]]-lo[lids[0]]); top = int(lo.argmax())
            item = {k: v for k, v in r.items() if k not in ('input_ids', 'own_text')}
            item['score'] = {'z': z, 'class': 1 if top == lids[1] else -1 if top == lids[0] else 0,
                             'binary_class': 1 if z >= 0 else -1, 'argmax_token': top, 'valid': top in lids}
            output.append(item); stream.write(json.dumps(item)+'\n'); stream.flush()
        print(a.stage, len(output), '/', len(planned), flush=True)

    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as stream:
        # Self-copy is a numerical control, not an extra scientific condition.
        check = planned[:min(2, len(planned))]
        native, native_trajectory = forward(check, capture=True)
        copied, _ = forward(check, trajectory=native_trajectory)
        errors['self_copy_max_nats'] = float((native-copied).abs().max())
        errors['self_copy_checked'] = True
        assert errors['self_copy_max_nats'] <= .001, errors
        plain = [r for r in planned if r['donor_id'] is None]
        for i in range(0, len(plain), a.batch_size):
            rr = plain[i:i+a.batch_size]; lo, _ = forward(rr); score(rr, lo, stream)
        for did, donor in donors.items():
            _, trajectory = forward([donor], capture=True)
            captured_norms.append({'donor_id': did, 'norm_by_layer': [float(trajectory[i].norm()) for i in range(64)]})
            rr = [r for r in planned if r['donor_id'] == did]
            for i in range(0, len(rr), a.batch_size):
                batch = rr[i:i+a.batch_size]; lo, _ = forward(batch, trajectory=trajectory); score(batch, lo, stream)
            del trajectory
    expected = {r['id'] for r in planned}; actual = {r['id'] for r in output}
    assert expected == actual and len(actual) == len(output) == (112 if a.stage == 'positive' else 384)
    elapsed = time.time()-t0
    analysis = analyze(output, errors)
    (p/'analysis.json').write_text(json.dumps(analysis, indent=2)+'\n')
    (p/'trajectory_norms.json').write_text(json.dumps(captured_norms, indent=2)+'\n')
    (p/'completeness_audit.json').write_text(json.dumps({'n_rows': len(output), 'unique_keys': len(actual),
        'all_expected_rows_retained': True, 'pd_pr_crossed': True, 'no_recipient_past_cache': True,
        'foreign_data_present_only_in_donor': True, 'non_carrier_edit_max': errors['non_carrier_max'],
        'self_copy_max_nats': errors['self_copy_max_nats'],
        'audit_type': 'executing-agent completeness check, not independent scientific review'}, indent=2)+'\n')
    run = {'args': vars(a), 'n_rows': len(output), 'elapsed_seconds': elapsed, 'gpu_hours': 2*elapsed/3600,
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'actual_model_type': model.config.model_type, 'num_layers': 64, 'dtype': 'float32', 'attention': 'eager',
           'device_map': model.hf_device_map, 'training': False, 'errors': errors,
           'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (p/'run.json').write_text(json.dumps(run, indent=2)+'\n')
    print(json.dumps({'complete': len(output), 'gpu_hours': run['gpu_hours'], 'gate': analysis.get('interface_gate')}), flush=True)


if __name__ == '__main__':
    main()
