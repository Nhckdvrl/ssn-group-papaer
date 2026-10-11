"""E99: fixed independent-material confirmation; no learned or cache interventions.

Run four fixed, disjoint two-context parts, then merge all four before interpreting
the confirmation.  Generation and parent-to-cue transfer retain every request.
"""
import argparse
import collections
import hashlib
import itertools
import json
import platform
import random
import subprocess
import time
from pathlib import Path

from e95_source_grouping import CELLS, audit as source_audit, body, parse, world

N_CONTEXTS = 8
SEED = 99001
BATCH_SIZE = 8
N_PARTS = 4
SYSTEM = 'Infer rules from the examples. Return only the requested one-word answer.'
NAMES = [
    ['Dana', 'Evan', 'Fiona'], ['Gavin', 'Helen', 'Ivan'],
    ['Julia', 'Kevin', 'Laura'], ['Marco', 'Nina', 'Owen'],
    ['Paula', 'Quinn', 'Rita'], ['Simon', 'Tara', 'Victor'],
    ['Wendy', 'Xavier', 'Yvonne'], ['Zane', 'Maya', 'Noah'],
]
DEMO_TEMPLATES = [
    ['The dish came with a {v} seasoning.',
     'The cook prepared this plate in a {v} style.',
     "The meal's flavor was distinctly {v}.",
     'The food on the table was {v}.'],
    ['The waiters maintained a {v} serving pace.',
     'The table received service at a {v} tempo.',
     "The staff's delivery of the meal was {v}.",
     'The serving process moved at a {v} pace.'],
]
QUERY_TEMPLATES = [
    ['For our main course, the kitchen chose a {v} preparation.',
     'The dish we sampled had a {v} taste.',
     'Our plate arrived with {v} seasoning.',
     'The food we received was {v} in flavor.'],
    ['The pace of our table service was {v}.',
     'The service during our visit proceeded at a {v} tempo.',
     'Our table was served at a {v} pace.',
     'The service we received was {v}.'],
]
VALUES = [{1: 'spicy', -1: 'mild'}, {1: 'quick', -1: 'leisurely'}]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def key(row):
    return (row['kind'], row['context'], row['pa'], row['cb'], row['pb'], row['query'])


def contexts():
    rng = random.Random(SEED)
    out = []
    for ci in range(N_CONTEXTS):
        names = NAMES[ci][:]
        rng.shuffle(names)
        own, foreign, seen = [], [], set()

        def new_text(x):
            while True:
                parts = [rng.choice(DEMO_TEMPLATES[j]).format(v=VALUES[j][x[j]]) for j in (0, 1)]
                rng.shuffle(parts)
                text = ' '.join(parts)
                if text not in seen:
                    seen.add(text)
                    return text

        for x in [CELLS[0], CELLS[3]] * 4:
            own.append({'a': True, 'x': list(x), 'text': new_text(x)})
        for x in CELLS:
            for _ in range(2):
                text = new_text(x)
                for y in (1, -1):
                    foreign.append({'a': False, 'x': list(x), 'text': text, 'y': y})
        rng.shuffle(own)
        rng.shuffle(foreign)
        demos = own + foreign if ci % 2 == 0 else foreign + own
        query_order = [0, 1]
        rng.shuffle(query_order)
        queries = []
        for x in CELLS:
            parts = [QUERY_TEMPLATES[j][ci % 4].format(v=VALUES[j][x[j]]) for j in query_order]
            queries.append({'x': list(x), 'text': ' '.join(parts)})
        out.append({'context': ci, 'names': names, 'demos': demos, 'queries': queries,
                    'a_position': 'first' if ci % 2 == 0 else 'last',
                    'query_template': ci % 4, 'query_aspect_order': query_order})
    return out


def thinking_records(cs, kind):
    assert kind in ('criterion', 'native')
    rows = []
    for c in cs:
        for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            for qi in ([None] if kind == 'criterion' else range(4)):
                x = None if qi is None else c['queries'][qi]['x']
                gold = (1 if cb == 1 else -1) if x is None else pa * x[cb]
                rows.append({'kind': kind, 'mode': 'thinking', 'context': c['context'],
                             'a_position': c['a_position'], 'pa': pa, 'cb': cb, 'pb': pb,
                             'query': qi, 'discordant': None if x is None else x[0] != x[1],
                             'gold': gold, 'body': body(c, kind, pa, cb, pb, qi)})
    return rows


def own_records(cs, parents):
    lookup = {(r['context'], r['pa'], r['cb'], r['pb']): r for r in parents}
    assert len(lookup) == len(parents) == 8 * len(cs)
    rows = []
    for c in cs:
        na, nb, nc = c['names']
        for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            parent = lookup[c['context'], pa, cb, pb]
            assert parent['kind'] == 'criterion' and parent['query'] is None
            cl = parent['score']['class']
            assert cl in (-1, 0, 1)
            cue = None if cl == 0 else (0 if cl == -1 else 1)
            own = ('The reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
                   'or service pace (quick or leisurely). The reviewer has a personal preference for one of the two values '
                   'of that aspect. yes means the experience matches that personal preference; no means it does not. '
                   'Infer the rule from the examples.\n\n')
            for d in world(c, pa, cb, pb):
                if d['role'] == 0:
                    own += f'Reviewer: {na}\nReview: {d["text"]}\nLabel: {"yes" if d["y"] == 1 else "no"}\n\n'
            clause = ('The relevant aspect is unavailable.\n\n' if cue is None else
                      f'{na} judges only {"food spiciness" if cue == 0 else "service pace"}. '
                      'Infer their personal preference from their examples.\n\n')
            for qi, q in enumerate(c['queries']):
                text = own + clause + f'Reviewer: {na}\nReview: {q["text"]}\nGive this reviewer\'s yes/no label for the review.\n'
                assert nb not in text and nc not in text
                rows.append({'kind': 'own_self', 'mode': 'direct', 'context': c['context'],
                             'a_position': c['a_position'], 'pa': pa, 'cb': cb, 'pb': pb,
                             'query': qi, 'discordant': q['x'][0] != q['x'][1],
                             'gold': pa * q['x'][cb], 'cue_criterion': cue,
                             'cue_gold': None if cue is None else pa * q['x'][cue],
                             'parent_key': list(key(parent)), 'parent_class': cl,
                             'parent_score_sha256': digest(parent['score']),
                             'parent_valid': parent['score']['valid'], 'body': text})
    return rows


def design_audit(cs):
    source = source_audit(cs)
    source.pop('n_direct')  # This is the E95 request count, not this protocol's count.
    assert len(cs) == N_CONTEXTS and [c['context'] for c in cs] == list(range(N_CONTEXTS))
    assert collections.Counter(c['a_position'] for c in cs) == {'first': 4, 'last': 4}
    for c in cs:
        positions = [i for i, d in enumerate(c['demos']) if d['a']]
        assert positions == (list(range(8)) if c['a_position'] == 'first' else list(range(16, 24)))
    from e93_selective_sharing import DEMO as OLD_DEMO, QUERY as OLD_QUERY
    old_phrases = {s for pool in OLD_DEMO for values in pool.values() for s in values}
    old_phrases.update(s for pool in OLD_QUERY for s in pool.values())
    new_phrases = {t.format(v=v) for j in (0, 1) for v in VALUES[j].values()
                   for t in DEMO_TEMPLATES[j] + QUERY_TEMPLATES[j]}
    assert old_phrases.isdisjoint(new_phrases)
    criterion = thinking_records(cs, 'criterion')
    native = thinking_records(cs, 'native')
    assert len(criterion) == 64 and len(native) == 256
    assert len({key(r) for r in criterion + native}) == 320
    # Exercise unknown and erroneous parent forwarding without executing a model.
    synthetic = []
    for i, r in enumerate(criterion):
        synthetic.append(dict(r, score={'class': (-1, 0, 1)[i % 3], 'valid': i % 3 != 1}))
    own = own_records(cs, synthetic)
    assert len(own) == 256 and len({key(r) for r in own}) == 256
    for r in own:
        assert (r['cue_criterion'] is None) == (r['parent_class'] == 0)
        assert r['cue_criterion'] is None or r['cue_criterion'] == (1 if r['parent_class'] == 1 else 0)
    return {'n_contexts': 8, 'seed': SEED, 'criterion_rows': 64, 'native_rows': 256,
            'own_rows': 256, 'total_rows': 576, 'parts': [[2*i, 2*i+1] for i in range(4)],
            'a_position_counts': {'first': 4, 'last': 4}, 'new_phrase_overlap_with_e93_e95': 0,
            'unknown_and_wrong_parent_forwarding_checked': True,
            'no_parent_correctness_selection': True, 'contexts_sha256': digest(cs),
            'source_grouping_static_audit': source,
            'scope': 'Static design enumeration; synthetic parents are not model evidence.'}


def cluster_rate(rows, numerator, denominator=lambda r: True):
    """A ratio-of-counts CI resampling complete contexts, including zero-denominator ones."""
    ids = sorted({r['context'] for r in rows})
    stats = []
    for ci in ids:
        selected = [r for r in rows if r['context'] == ci and denominator(r)]
        n = sum(bool(numerator(r)) for r in selected)
        stats.append((n, len(selected)))
    total_n, total_d = map(sum, zip(*stats)) if stats else (0, 0)
    rng = random.Random(99099)
    values = []
    for _ in range(10000):
        sampled = [stats[rng.randrange(len(stats))] for _ in stats]
        n = sum(s[0] for s in sampled)
        d = sum(s[1] for s in sampled)
        if d:
            values.append(n/d)
    values.sort()
    ci = None if not values else [values[int(.025*(len(values)-1))], values[int(.975*(len(values)-1))]]
    return {'mean': total_n/total_d if total_d else None, 'ci95': ci,
            'numerator': total_n, 'denominator': total_d, 'n_contexts': len(ids),
            'bootstrap_unit': 'context', 'bootstrap_defined': len(values),
            'bootstrap_undefined': 10000-len(values),
            'per_context': [{'context': i, 'numerator': n, 'denominator': d,
                             'mean': n/d if d else None} for i, (n, d) in zip(ids, stats)]}


def analyze(rows):
    out = {'n_rows': len(rows), 'n_contexts': len({r['context'] for r in rows}),
           'behavior': {}, 'paired': {}, 'prompt_counts': {},
           'interpretation': 'Native thinking versus Own direct is a functional pipeline comparison, not an isolated cue intervention.'}
    for kind in ('criterion', 'native', 'own_self'):
        rr = [r for r in rows if r['kind'] == kind]
        if not rr:
            continue
        out['prompt_counts'][kind] = {'rows': len(rr), 'unique_prompts': len({r['prompt_sha256'] for r in rr}),
                                    'identical_prompt_rows_retained': len(rr)-len({r['prompt_sha256'] for r in rr})}
        metrics = {}
        for subset in (('all',) if kind == 'criterion' else ('all', 'discordant', 'concordant')):
            ss = [r for r in rr if subset == 'all' or r['discordant'] == (subset == 'discordant')]
            result = {'actual_accuracy': cluster_rate(ss, lambda r: r['score']['class'] == r['gold']),
                      'valid_fraction': cluster_rate(ss, lambda r: r['score']['valid'])}
            if kind == 'own_self':
                known = lambda r: r['cue_gold'] is not None
                execution = lambda r: known(r) and r['score']['class'] == r['cue_gold']
                binary_execution = lambda r: known(r) and r['score']['binary_class'] == r['cue_gold']
                result.update(binary_actual_accuracy=cluster_rate(ss, lambda r: r['score']['binary_class'] == r['gold']),
                              cue_coverage=cluster_rate(ss, known),
                              cue_execution_all_rows=cluster_rate(ss, execution),
                              cue_execution_resolved=cluster_rate(ss, execution, known),
                              binary_cue_execution_all_rows=cluster_rate(ss, binary_execution),
                              binary_cue_execution_resolved=cluster_rate(ss, binary_execution, known))
            metrics[subset] = result
        out['behavior'][kind] = metrics
        lookup = {(r['context'], r['pa'], r['cb'], r['pb'], r['query']): r for r in rr}
        pairs = []
        for r in rr:
            ci, pa, cb, pb, qi = r['context'], r['pa'], r['cb'], r['pb'], r['query']
            opposite_c = lookup[ci, pa, 1-cb, pb, qi]
            opposite_pb = lookup[ci, pa, cb, -pb, qi]
            opposite_pa = lookup[ci, -pa, cb, pb, qi]
            pairs.append({'context': ci, 'discordant': r['discordant'], 'cb': cb, 'pa': pa, 'pb': pb,
                          'c_both_correct': r['score']['class'] == r['gold'] and opposite_c['score']['class'] == opposite_c['gold'],
                          'c_pair_valid': r['score']['valid'] and opposite_c['score']['valid'],
                          'c_flip': r['score']['valid'] and opposite_c['score']['valid'] and r['score']['class'] != opposite_c['score']['class'],
                          'pb_pair_valid': r['score']['valid'] and opposite_pb['score']['valid'],
                          'pb_flip': r['score']['valid'] and opposite_pb['score']['valid'] and r['score']['class'] != opposite_pb['score']['class'],
                          'pa_both_correct': r['score']['class'] == r['gold'] and opposite_pa['score']['class'] == opposite_pa['gold']})
        # Count each symmetric pair once. Missing/invalid answers remain in denominators.
        cp = [r for r in pairs if r['cb'] == 0 and (kind == 'criterion' or r['discordant'])]
        bp = [r for r in pairs if r['pb'] == 1]
        pm = {'criterion_pair_both_correct': cluster_rate(cp, lambda r: r['c_both_correct']),
              'criterion_flip_all_pairs': cluster_rate(cp, lambda r: r['c_flip']),
              'criterion_pair_valid_coverage': cluster_rate(cp, lambda r: r['c_pair_valid']),
              'pb_flip_all_pairs': cluster_rate(bp, lambda r: r['pb_flip']),
              'pb_pair_valid_coverage': cluster_rate(bp, lambda r: r['pb_pair_valid'])}
        if kind != 'criterion':
            pp = [r for r in pairs if r['pa'] == 1 and not r['discordant']]
            pm['concordant_private_preference_pair_both_correct'] = cluster_rate(pp, lambda r: r['pa_both_correct'])
        out['paired'][kind] = pm
    own = [r for r in rows if r['kind'] == 'own_self']
    out['parent_transfer'] = {'own_rows': len(own), 'unique_parents': len({tuple(r['parent_key']) for r in own}),
                              'unresolved_parent_rows': sum(r['cue_criterion'] is None for r in own),
                              'incorrect_resolved_parent_rows': sum(r['cue_criterion'] is not None and r['cue_criterion'] != r['cb'] for r in own)}
    return out


def validate_rows(cs, rows):
    criterion = [r for r in rows if r['kind'] == 'criterion']
    expected = thinking_records(cs, 'criterion') + thinking_records(cs, 'native') + own_records(cs, criterion)
    assert len(rows) == 72*len(cs)
    lookup = {key(r): r for r in rows}
    assert len(lookup) == len(rows) and set(lookup) == {key(r) for r in expected}
    for ref in expected:
        actual = lookup[key(ref)]
        assert actual['body_sha256'] == hashlib.sha256(ref['body'].encode()).hexdigest()
        for field in ('mode', 'gold', 'discordant', 'a_position'):
            assert actual[field] == ref[field], (key(ref), field)
        if ref['kind'] == 'own_self':
            for field in ('cue_criterion', 'cue_gold', 'parent_key', 'parent_score_sha256', 'parent_class', 'parent_valid'):
                assert actual[field] == ref[field], (key(ref), field)
        else:
            assert actual['score']['initial_prefix_preserved']
    return {'n_rows': len(rows), 'unique_keys': len(lookup), 'n_contexts': len(cs),
            'all_frozen_requests_retained': True, 'all_parent_predictions_used_without_selection': True,
            'initial_censored': sum(r['score'].get('initial_censored', False) for r in rows),
            'still_censored': sum(r['score'].get('still_censored', False) for r in rows),
            'unresolved': sum(not r['score']['valid'] for r in rows),
            'phase_counts': dict(collections.Counter(r['kind'] for r in rows)),
            'scope': 'Executing-agent completeness audit, not independent scientific review.'}


def merge(parts, out):
    assert len(parts) == N_PARTS
    rows, runs = [], []
    cs = contexts()
    for path in parts:
        path = Path(path)
        run = json.loads((path/'run.json').read_text())
        part_rows = read_jsonl(path/'behavior.jsonl')
        assert run['n_rows'] == len(part_rows) == 144
        assert run['contexts_sha256'] == digest(cs)
        local = [cs[2*run['part']], cs[2*run['part']+1]]
        validate_rows(local, part_rows)
        expected_batches = []
        for kind in ('criterion', 'native', 'own_self'):
            phase_rows = [r for r in part_rows if r['kind'] == kind]
            assert read_jsonl(path/(kind+'.jsonl')) == phase_rows
            for offset in range(0, len(phase_rows), BATCH_SIZE):
                expected_batches.append({'kind': kind, 'batch_index': offset//8,
                                         'keys': [list(key(r)) for r in phase_rows[offset:offset+8]]})
        assert run['batch_manifest'] == expected_batches
        runs.append(run)
        rows.extend(part_rows)
    assert sorted(r['part'] for r in runs) == list(range(4))
    for field in ('script_sha256', 'dependency_sha256', 'model_config_sha256', 'torch', 'transformers'):
        assert len({json.dumps(r[field], sort_keys=True) for r in runs}) == 1, field
    audit = validate_rows(cs, rows)
    assert audit['phase_counts'] == {'criterion': 64, 'native': 256, 'own_self': 256}
    rows.sort(key=lambda r: (('criterion', 'native', 'own_self').index(r['kind']), r['context'], -r['pa'], r['cb'], -r['pb'], -1 if r['query'] is None else r['query']))
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'behavior_merged.jsonl').exists(), 'Refusing to overwrite a completed merge.'
    (out/'behavior_merged.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    audit.update(gpu_hours=sum(r['gpu_hours'] for r in runs), contexts_sha256=digest(cs),
                 script_sha256=runs[0]['script_sha256'], parts=sorted(r['part'] for r in runs))
    write_json(out/'analysis.json', analyze(rows))
    write_json(out/'completeness_audit.json', audit)
    print(json.dumps(audit), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--part', type=int, choices=range(4))
    ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--design-only', action='store_true')
    ap.add_argument('--merge', nargs='+', metavar='PART_DIR')
    args = ap.parse_args()
    out = Path(args.out)
    if args.merge:
        assert args.part is None and not args.design_only
        merge(args.merge, out)
        return
    assert args.part is not None, '--part 0..3 is required outside merge mode'
    cs = contexts()
    audit = design_audit(cs)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'behavior.jsonl').exists(), 'Refusing to overwrite prior model results.'
    write_json(out/'design_audit.json', audit)
    (out/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    local = cs[2*args.part:2*args.part+2]
    stages = {kind: thinking_records(local, kind) for kind in ('criterion', 'native')}
    write_json(out/'example.json', {'criterion': stages['criterion'][0]['body'], 'native': stages['native'][0]['body']})
    if args.design_only:
        print(json.dumps({k: v for k, v in audit.items() if k != 'source_grouping_static_audit'}))
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(6)
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    tok.padding_side = 'left'
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    candidates = {'criterion': ('food', 'service'), 'native': ('no', 'yes'), 'own_self': ('no', 'yes')}
    label_ids = {}
    for kind, labels in candidates.items():
        encoded = [tok.encode(' '+s, add_special_tokens=False) for s in labels]
        assert all(len(x) == 1 for x in encoded), (kind, encoded)
        label_ids[kind] = [x[0] for x in encoded]
    config_path = Path(args.model)/'config.json'
    config = json.loads(config_path.read_text())
    assert config.get('text_config', config)['model_type'] == 'qwen3_5_text'
    dependencies = [Path(__file__).with_name(name) for name in ('e95_source_grouping.py', 'e93_selective_sharing.py')]
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    dependency_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}

    def prompt(row):
        return tok.apply_chat_template([{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': row['body']}],
                                       tokenize=False, add_generation_prompt=True,
                                       enable_thinking=row['mode'] == 'thinking', reasoning_effort='medium') + (
                                       'Answer:' if row['mode'] == 'direct' else '')

    write_json(out/'preflight.json', {'part': args.part, 'context_ids': [c['context'] for c in local],
                                    'label_ids': label_ids, 'expected_rows': 144,
                                    'batch_size': 8, 'thinking_budget': [1024, 2048],
                                    'contexts_sha256': digest(cs), 'no_cache_interventions': True,
                                    'script_sha256': code_hash, 'dependency_sha256': dependency_hashes})
    start = time.time()
    print('Loading E99 part', args.part, flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
                       dtype=torch.bfloat16, device_map='cuda', attn_implementation='sdpa', output_loading_info=True)
    model.eval()
    model.requires_grad_(False)
    assert not loading.get('missing_keys'), loading
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    # Transformers may return sets in diagnostic metadata. This conversion is
    # confined to the loader report; scientific records retain strict JSON types.
    write_json(out/'loading_info.json', json.loads(json.dumps(loading, default=str)))
    print('Loaded', flush=True)
    rows, batch_manifest = [], []
    continued = 0
    noop = None
    with torch.inference_mode(), (out/'behavior.jsonl').open('w') as stream, (out/'prompts.jsonl').open('w') as prompts:
        for kind in ('criterion', 'native', 'own_self'):
            stage = own_records(local, [r for r in rows if r['kind'] == 'criterion']) if kind == 'own_self' else stages[kind]
            assert len(stage) == (16 if kind == 'criterion' else 64)
            with (out/(kind+'.jsonl')).open('w') as phase_stream:
                for offset in range(0, len(stage), BATCH_SIZE):
                    batch = stage[offset:offset+BATCH_SIZE]
                    texts = [prompt(r) for r in batch]
                    xx = tok(texts, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
                    width = xx.input_ids.shape[1]
                    if kind == 'own_self':
                        pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
                        logits = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float()
                        if offset == 0:
                            again = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float()
                            noop = float((again-logits).abs().max())
                            assert noop <= .001, noop
                        raw_batch = None
                    else:
                        generated = model.generate(**xx, max_new_tokens=1024, do_sample=False,
                                                   pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                        raw_batch = generated[:, width:].tolist()
                    for j, r in enumerate(batch):
                        if kind == 'own_self':
                            lid = label_ids[kind]
                            z = float(logits[j, lid[1]]-logits[j, lid[0]])
                            top = int(logits[j].argmax())
                            score = {'class': 1 if top == lid[1] else -1 if top == lid[0] else 0,
                                     'binary_class': 1 if z >= 0 else -1, 'valid': top in lid,
                                     'z': z, 'argmax_token': top}
                        else:
                            raw = raw_batch[j]
                            old = raw[:]
                            initial_censored = tok.eos_token_id not in raw
                            if initial_censored:
                                original_prompt_ids = xx.input_ids[j][xx.attention_mask[j].bool()].tolist()
                                full = original_prompt_ids + raw
                                fi = torch.tensor([full], device='cuda')
                                more = model.generate(input_ids=fi, attention_mask=torch.ones_like(fi), max_new_tokens=2048,
                                                      do_sample=False, pad_token_id=tok.pad_token_id,
                                                      eos_token_id=tok.eos_token_id)[0, len(full):].tolist()
                                raw += more
                                assert raw[:len(old)] == old
                                continued += 1
                            if tok.eos_token_id in raw:
                                raw = raw[:raw.index(tok.eos_token_id)+1]
                            text = tok.decode(raw, skip_special_tokens=False)
                            cl, status = parse(text, candidates[kind])
                            score = {'class': cl, 'valid': cl != 0, 'parse_status': status,
                                     'text': text, 'token_ids': raw, 'initial_censored': initial_censored,
                                     'still_censored': tok.eos_token_id not in raw,
                                     'initial_prefix_preserved': True,
                                     'initial_generated_tokens': len(old) if initial_censored else old.index(tok.eos_token_id)+1}
                        record = {k: v for k, v in r.items() if k != 'body'}
                        record.update(score=score, prompt_sha256=hashlib.sha256(texts[j].encode()).hexdigest(),
                                      body_sha256=hashlib.sha256(r['body'].encode()).hexdigest())
                        rows.append(record)
                        line = json.dumps(record)+'\n'
                        stream.write(line)
                        phase_stream.write(line)
                        prompts.write(json.dumps(dict(r, prompt=texts[j]))+'\n')
                    stream.flush()
                    phase_stream.flush()
                    prompts.flush()
                    batch_manifest.append({'kind': kind, 'batch_index': offset//8, 'keys': [list(key(r)) for r in batch]})
                    print(kind, offset+len(batch), '/', len(stage), 'continued', continued, flush=True)
            write_json(out/('analysis_'+kind+'.json'), analyze([r for r in rows if r['kind'] == kind]))
    elapsed = time.time()-start
    completeness = validate_rows(local, rows)
    write_json(out/'analysis.json', analyze(rows))
    write_json(out/'completeness_audit.json', completeness)
    assert code_hash == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'Running script changed on disk.'
    assert dependency_hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}, 'Dependency changed on disk.'
    run = {'part': args.part, 'args': vars(args), 'n_rows': len(rows), 'batch_manifest': batch_manifest,
           'contexts_sha256': digest(cs), 'script_sha256': code_hash,
           'dependency_sha256': dependency_hashes,
           'model_config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
           'actual_model_type': model.config.model_type, 'dtype': 'bfloat16', 'attention': 'sdpa',
           'batch_size': 8, 'training': False, 'noop_max_nats': noop, 'continued': continued,
           'elapsed_seconds': elapsed, 'gpu_hours': elapsed/3600, 'python': platform.python_version(),
           'torch': torch.__version__, 'transformers': transformers.__version__,
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    write_json(out/'run.json', run)
    print('Complete', len(rows), 'rows;', elapsed, 'seconds', flush=True)


if __name__ == '__main__':
    main()
