"""E100: change only reviewer C's legal preference in the frozen E99 contexts.

Two conditions are generated afresh, in adjacent fixed batches. No model results
from E99 enter this experiment, and no requests are selected by their outcomes.
"""
import argparse
import collections
import hashlib
import itertools
import json
import os
import platform
import random
import socket
import subprocess
import sys
import time
from pathlib import Path

from e95_source_grouping import body as original_body, parse, world as original_world
from e99_confirm_factor_interface import (
    BATCH_SIZE, N_PARTS, SEED, SYSTEM, cluster_rate, contexts, digest,
    read_jsonl, thinking_records as e99_records, write_json,
)

CONDITIONS = ('opposite', 'aligned')
KINDS = ('criterion', 'native')
LABELS = {'criterion': ('food', 'service'), 'native': ('no', 'yes')}
CONTEXTS_SHA256 = 'bd8fd15d29abb0bffd9f5b64b8d47bc8dbd6be948ddc82c8f96f7b0173fe4f3b'
DECLARED_REVISION = '1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0'
INITIAL_BUDGET = 1024
CONTINUATION_BUDGET = 2048


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def key(row):
    return (row['kind'], row['context'], row['pa'], row['cb'], row['pb'],
            row['condition'], row['query'])


def sort_key(row):
    return (KINDS.index(row['kind']), row['context'], -row['pa'], row['cb'],
            -row['pb'], CONDITIONS.index(row['condition']),
            -1 if row['query'] is None else row['query'])


def world(c, pa, cb, pb, condition):
    assert condition in CONDITIONS
    # Role assignment always comes from the opposite world, before any C flip.
    return [dict(d, y=-d['y'] if condition == 'aligned' and d['role'] == 2 else d['y'])
            for d in original_world(c, pa, cb, pb)]


def render_demo(c, d):
    return (f'Reviewer: {c["names"][d["role"]]}\nReview: {d["text"]}\n'
            f'Label: {"yes" if d["y"] == 1 else "no"}')


def body(c, kind, pa, cb, pb, condition, qi):
    assert kind in KINDS
    original = original_body(c, kind, pa, cb, pb, qi)
    blocks = original.split('\n\n')
    before = original_world(c, pa, cb, pb)
    assert len(blocks) == 26 and len(before) == 24
    for i, (old, new) in enumerate(zip(before, world(c, pa, cb, pb, condition)), 1):
        assert blocks[i] == render_demo(c, old)
        blocks[i] = render_demo(c, new)
    return '\n\n'.join(blocks)


def records(cs, kind):
    assert kind in KINDS
    rows = []
    for c in cs:
        for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            for condition in CONDITIONS:
                for qi in ([None] if kind == 'criterion' else range(4)):
                    x = None if qi is None else c['queries'][qi]['x']
                    gold = (1 if cb == 1 else -1) if x is None else pa*x[cb]
                    rows.append({'kind': kind, 'mode': 'thinking', 'context': c['context'],
                                 'a_position': c['a_position'], 'pa': pa, 'cb': cb, 'pb': pb,
                                 'pc': -pb if condition == 'opposite' else pb,
                                 'condition': condition, 'query': qi,
                                 'preference_relation': 'same' if pa == pb else 'opposed',
                                 'discordant': None if x is None else x[0] != x[1],
                                 'gold': gold, 'body': body(c, kind, pa, cb, pb, condition, qi)})
    return rows


def batch_manifest(cs):
    result = []
    for kind in KINDS:
        rows = records(cs, kind)
        assert len(rows) % BATCH_SIZE == 0
        for offset in range(0, len(rows), BATCH_SIZE):
            batch = rows[offset:offset+BATCH_SIZE]
            if kind == 'native':
                assert len({(r['context'], r['pa'], r['cb'], r['pb']) for r in batch}) == 1
                assert [(r['condition'], r['query']) for r in batch] == [
                    (condition, qi) for condition in CONDITIONS for qi in range(4)]
            result.append({'kind': kind, 'batch_index': offset//BATCH_SIZE,
                           'keys': [list(key(r)) for r in batch]})
    return result


def design_audit(cs):
    assert digest(cs) == CONTEXTS_SHA256, 'E99 context material changed.'
    assert [c['context'] for c in cs] == list(range(8))
    assert collections.Counter(c['a_position'] for c in cs) == {'first': 4, 'last': 4}
    world_checks = []
    for c in cs:
        assert len(c['demos']) == 24 and len(c['queries']) == 4
        a_indices = [i for i, d in enumerate(c['demos']) if d['a']]
        assert a_indices == (list(range(8)) if c['a_position'] == 'first' else list(range(16, 24)))
        assert not {d['text'] for d in c['demos']} & {q['text'] for q in c['queries']}
        for pa, pb in itertools.product((1, -1), repeat=2):
            anonymous_by_c = {condition: [] for condition in CONDITIONS}
            for cb in (0, 1):
                opposite = world(c, pa, cb, pb, 'opposite')
                aligned = world(c, pa, cb, pb, 'aligned')
                assert opposite == original_world(c, pa, cb, pb)
                changed = []
                for i, (old, new) in enumerate(zip(opposite, aligned)):
                    assert {k: v for k, v in old.items() if k != 'y'} == {
                        k: v for k, v in new.items() if k != 'y'}
                    if old['role'] in (0, 1):
                        assert old == new and render_demo(c, old) == render_demo(c, new)
                    else:
                        assert new['y'] == -old['y']
                        changed.append(i)
                assert len(changed) == 8
                for condition, w in zip(CONDITIONS, (opposite, aligned)):
                    pc = -pb if condition == 'opposite' else pb
                    fits = [(cc, ps) for cc in (0, 1) for ps in itertools.product((1, -1), repeat=3)
                            if all(ps[d['role']]*d['x'][cc] == d['y'] for d in w)]
                    assert fits == [(cb, (pa, pb, pc))]
                    own_fits = [(cc, pp) for cc in (0, 1) for pp in (1, -1)
                                if all(pp*d['x'][cc] == d['y'] for d in w if d['role'] == 0)]
                    assert own_fits == [(0, pa), (1, pa)]
                    assert collections.Counter((d['role'], d['y']) for d in w) == {
                        (role, y): 4 for role in range(3) for y in (1, -1)}
                    foreign = [d for d in w if d['role'] != 0]
                    anonymous = [(d['text'], d['y']) for d in foreign]
                    anonymous_by_c[condition].append(anonymous)
                    anonymous_fits = [(cc, pp) for cc in (0, 1) for pp in (1, -1)
                                      if all(pp*d['x'][cc] == d['y'] for d in foreign)]
                    assert anonymous_fits == ([(cb, pb)] if condition == 'aligned' else [])
                    moment = [sum(d['y']*d['x'][j] for d in foreign)/16 for j in (0, 1)]
                    assert moment == ([pb if j == cb else 0 for j in (0, 1)]
                                      if condition == 'aligned' else [0, 0])
                    world_checks.append({'context': c['context'], 'pa': pa, 'cb': cb, 'pb': pb,
                                         'condition': condition, 'pc': pc, 'full_solutions': fits,
                                         'own_solutions': own_fits, 'anonymous_foreign_fits': anonymous_fits,
                                         'anonymous_foreign_sha256': digest(anonymous),
                                         'foreign_first_moment': moment})
            assert anonymous_by_c['opposite'][0] == anonymous_by_c['opposite'][1]
            assert anonymous_by_c['aligned'][0] != anonymous_by_c['aligned'][1]
    all_rows = []
    for kind in KINDS:
        rr = records(cs, kind)
        original = e99_records(cs, kind)
        opposite = [r for r in rr if r['condition'] == 'opposite']
        assert len(opposite) == len(original)
        for a, b in zip(opposite, original):
            assert a['body'] == b['body']
            for field in ('kind', 'context', 'pa', 'cb', 'pb', 'query', 'gold', 'discordant'):
                assert a[field] == b[field]
        for c in cs:
            for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
                for qi in ([None] if kind == 'criterion' else range(4)):
                    blocks = [body(c, kind, pa, cb, pb, condition, qi).split('\n\n')
                              for condition in CONDITIONS]
                    changed_blocks = [i for i, pair in enumerate(zip(*blocks)) if pair[0] != pair[1]]
                    expected = [i+1 for i, d in enumerate(original_world(c, pa, cb, pb)) if d['role'] == 2]
                    assert changed_blocks == expected
                    for i in expected:
                        assert blocks[0][i].splitlines()[:2] == blocks[1][i].splitlines()[:2]
        all_rows.extend(rr)
    assert len(all_rows) == len({key(r) for r in all_rows}) == 640
    batches = {str(part): batch_manifest(cs[2*part:2*part+2]) for part in range(N_PARTS)}
    assert all(sum(len(b['keys']) for b in bbs) == 160 for bbs in batches.values())
    return {'n_contexts': 8, 'seed': SEED, 'contexts_sha256': digest(cs),
            'total_rows': 640, 'criterion_rows': 128, 'native_rows': 512,
            'parts': [[2*i, 2*i+1] for i in range(4)], 'rows_per_part': 160,
            'a_position_counts': {'first': 4, 'last': 4},
            'only_c_labels_changed': 8, 'ab_raw_demo_blocks_unchanged': True,
            'opposite_bodies_exactly_equal_e99': True, 'full_world_unique_solution': True,
            'own_only_criterion_solutions': 2, 'every_source_yes_no_counts': [4, 4],
            'opposite_anonymous_foreign_sequence_identical_across_criterion': True,
            'aligned_anonymous_foreign_identifies_criterion_and_pb': True,
            'no_model_outcome_selection': True, 'world_checks': world_checks,
            'batch_manifest': batches,
            'scope': 'Static enumeration only. Foreign first moments exclude A; no neural algorithm is established.'}


def cluster_mean(rows, value):
    """Signed paired effects; resample whole contexts, keeping all their requests."""
    ids = sorted({r['context'] for r in rows})
    stats = [(sum(value(r) for r in rows if r['context'] == ci),
              sum(r['context'] == ci for r in rows)) for ci in ids]
    n, d = map(sum, zip(*stats)) if stats else (0, 0)
    rng = random.Random(100099)
    values = []
    for _ in range(10000):
        sample = [stats[rng.randrange(len(stats))] for _ in stats]
        den = sum(t[1] for t in sample)
        if den:
            values.append(sum(t[0] for t in sample)/den)
    values.sort()
    return {'mean': n/d if d else None,
            'ci95': None if not values else [values[int(.025*(len(values)-1))], values[int(.975*(len(values)-1))]],
            'effect_sum': n, 'denominator': d, 'n_contexts': len(ids),
            'bootstrap_unit': 'context', 'bootstrap_defined': len(values),
            'bootstrap_undefined': 10000-len(values),
            'per_context': [{'context': ci, 'effect_sum': num, 'denominator': den,
                             'mean': num/den if den else None} for ci, (num, den) in zip(ids, stats)]}


def subsets(rows, kind):
    result = {'all': rows}
    if kind == 'native':
        result['discordant'] = [r for r in rows if r['discordant']]
        result['concordant'] = [r for r in rows if not r['discordant']]
        for relation in ('same', 'opposed'):
            result['discordant_'+relation+'_preference'] = [
                r for r in rows if r['discordant'] and r['preference_relation'] == relation]
    return result


def analyze(rows):
    result = {'n_rows': len(rows), 'n_contexts': len({r['context'] for r in rows}),
              'behavior': {}, 'condition_effects': {}, 'paired_worlds': {}, 'prompt_counts': {},
              'interaction_definition': '(aligned-opposite) at pA=pB minus (aligned-opposite) at pA=-pB',
              'unknown_policy': 'Unknowns are incorrect and remain in all accuracy and flip denominators; flips require both answers resolved.',
              'interval_scope': 'Empirical whole-context bootstrap; a degenerate all-correct interval is not absence of population uncertainty.',
              'interpretation': 'A functional perturbation on E99 materials, not an independent new-material confirmation or circuit identification.'}
    for kind in KINDS:
        rr = [r for r in rows if r['kind'] == kind]
        if not rr:
            continue
        result['behavior'][kind] = {}
        result['paired_worlds'][kind] = {}
        lookup = {(r['condition'], r['context'], r['pa'], r['cb'], r['pb'], r['query']): r for r in rr}
        assert len(lookup) == len(rr)
        for condition in CONDITIONS:
            cond_rows = [r for r in rr if r['condition'] == condition]
            result['prompt_counts'][kind+'_'+condition] = {
                'rows': len(cond_rows), 'unique_prompts': len({r['prompt_sha256'] for r in cond_rows})}
            result['behavior'][kind][condition] = {
                name: {'accuracy': cluster_rate(ss, lambda r: r['score']['class'] == r['gold']),
                       'valid_fraction': cluster_rate(ss, lambda r: r['score']['valid'])}
                for name, ss in subsets(cond_rows, kind).items()}
            paired = []
            for r in cond_rows:
                ci, pa, cb, pb, qi = r['context'], r['pa'], r['cb'], r['pb'], r['query']
                other_c = lookup[condition, ci, pa, 1-cb, pb, qi]
                other_pb = lookup[condition, ci, pa, cb, -pb, qi]
                c_valid = r['score']['valid'] and other_c['score']['valid']
                pb_valid = r['score']['valid'] and other_pb['score']['valid']
                paired.append({'context': ci, 'cb': cb, 'pb': pb, 'discordant': r['discordant'],
                               'preference_relation': r['preference_relation'],
                               'c_both_correct': r['score']['class'] == r['gold'] and other_c['score']['class'] == other_c['gold'],
                               'c_pair_valid': c_valid,
                               'c_flip': c_valid and r['score']['class'] != other_c['score']['class'],
                               'pb_pair_valid': pb_valid,
                               'pb_flip': pb_valid and r['score']['class'] != other_pb['score']['class']})
            pm = {}
            # Symmetric pairs counted once. pB flip pairs cross preference strata.
            for name, ss in subsets(paired, kind).items():
                cp = [r for r in ss if r['cb'] == 0]
                metric = {'c_pair_both_correct': cluster_rate(cp, lambda r: r['c_both_correct']),
                          'c_pair_valid_coverage': cluster_rate(cp, lambda r: r['c_pair_valid']),
                          'c_flip_all_pairs': cluster_rate(cp, lambda r: r['c_flip'])}
                if not name.endswith('_preference'):
                    bp = [r for r in ss if r['pb'] == 1]
                    metric.update(pb_flip_all_pairs=cluster_rate(bp, lambda r: r['pb_flip']),
                                  pb_pair_valid_coverage=cluster_rate(bp, lambda r: r['pb_pair_valid']))
                pm[name] = metric
            result['paired_worlds'][kind][condition] = pm
        condition_pairs = []
        for r in rr:
            if r['condition'] != 'opposite':
                continue
            a = lookup['aligned', r['context'], r['pa'], r['cb'], r['pb'], r['query']]
            assert r['gold'] == a['gold']
            delta = int(a['score']['class'] == a['gold'])-int(r['score']['class'] == r['gold'])
            condition_pairs.append({'context': r['context'], 'discordant': r['discordant'],
                                    'preference_relation': r['preference_relation'], 'delta': delta,
                                    'valid_delta': int(a['score']['valid'])-int(r['score']['valid'])})
        result['condition_effects'][kind] = {
            name: {'accuracy_aligned_minus_opposite': cluster_mean(ss, lambda r: r['delta']),
                   'valid_aligned_minus_opposite': cluster_mean(ss, lambda r: r['valid_delta'])}
            for name, ss in subsets(condition_pairs, kind).items()}
        if kind == 'native':
            interaction = []
            for ci in sorted({r['context'] for r in condition_pairs}):
                means = {}
                for relation in ('same', 'opposed'):
                    ss = [r for r in condition_pairs if r['context'] == ci and r['discordant']
                          and r['preference_relation'] == relation]
                    assert len(ss) == 8
                    means[relation] = sum(r['delta'] for r in ss)/len(ss)
                interaction.append({'context': ci, 'delta': means['same']-means['opposed']})
            result['mixed_preference_interaction'] = cluster_mean(interaction, lambda r: r['delta'])
    return result


def validate_rows(cs, rows):
    expected = sum((records(cs, kind) for kind in KINDS), [])
    assert len(rows) == 80*len(cs)
    lookup = {key(r): r for r in rows}
    assert len(lookup) == len(rows) and set(lookup) == {key(r) for r in expected}
    for ref in expected:
        r = lookup[key(ref)]
        assert r['body_sha256'] == sha_text(ref['body'])
        for field in ('mode', 'gold', 'discordant', 'a_position', 'pc', 'preference_relation'):
            assert r[field] == ref[field], (key(ref), field)
        s = r['score']
        assert s['class'] in (-1, 0, 1) and s['valid'] == (s['class'] != 0)
        assert parse(s['text'], LABELS[r['kind']]) == (s['class'], s['parse_status'])
        eos = r['eos_token_id']
        initial, more, raw = s['initial_token_ids'], s['continuation_token_ids'], s['token_ids']
        assert 0 < len(initial) <= INITIAL_BUDGET and len(more) <= CONTINUATION_BUDGET
        assert s['initial_censored'] == (eos not in initial)
        assert not s['initial_censored'] or len(initial) == INITIAL_BUDGET
        assert bool(more) == s['initial_censored']
        combined = initial + more
        trimmed = combined[:combined.index(eos)+1] if eos in combined else combined
        assert raw == trimmed and s['still_censored'] == (eos not in raw)
        expected_initial_n = len(initial) if s['initial_censored'] else initial.index(eos)+1
        assert s['initial_generated_tokens'] == expected_initial_n
        assert s['initial_prefix_preserved'] and raw[:expected_initial_n] == initial[:expected_initial_n]
        assert s['continuation_prompt_sha256'] is not None if s['initial_censored'] else s['continuation_prompt_sha256'] is None
    return {'n_rows': len(rows), 'unique_keys': len(lookup), 'n_contexts': len(cs),
            'phase_counts': dict(collections.Counter(r['kind'] for r in rows)),
            'condition_counts': dict(collections.Counter(r['condition'] for r in rows)),
            'all_frozen_requests_retained': True, 'all_initial_censored_continued': True,
            'initial_censored': sum(r['score']['initial_censored'] for r in rows),
            'still_censored': sum(r['score']['still_censored'] for r in rows),
            'unresolved': sum(not r['score']['valid'] for r in rows),
            'scope': 'Executing-agent completeness audit, not independent scientific review.'}


def validate_prompts(cs, rows, prompts):
    expected = sum((records(cs, kind) for kind in KINDS), [])
    lookup = {key(r): r for r in rows}
    assert len(prompts) == len(expected) and [key(p) for p in prompts] == [key(r) for r in expected]
    for ref, p in zip(expected, prompts):
        r = lookup[key(p)]
        for k, v in ref.items():
            assert p[k] == v
        assert sha_text(p['prompt']) == r['prompt_sha256']
        assert digest(p['prompt_token_ids']) == r['prompt_token_ids_sha256']
        if r['score']['initial_censored']:
            assert digest(p['prompt_token_ids']+r['score']['initial_token_ids']) == r['score']['continuation_prompt_sha256']


def merge(parts, out):
    assert len(parts) == N_PARTS
    cs = contexts()
    assert digest(cs) == CONTEXTS_SHA256
    rows, runs = [], []
    for path in map(Path, parts):
        run = json.loads((path/'run.json').read_text())
        assert run['part'] in range(N_PARTS)
        part_rows = read_jsonl(path/'behavior.jsonl')
        local = cs[2*run['part']:2*run['part']+2]
        assert run['n_rows'] == len(part_rows) == 160
        assert run['contexts_sha256'] == CONTEXTS_SHA256
        assert read_jsonl(path/'contexts.jsonl') == cs
        validate_rows(local, part_rows)
        validate_prompts(local, part_rows, read_jsonl(path/'prompts.jsonl'))
        assert [key(r) for r in part_rows] == [key(r) for kind in KINDS for r in records(local, kind)]
        for kind in KINDS:
            assert read_jsonl(path/(kind+'.jsonl')) == [r for r in part_rows if r['kind'] == kind]
        assert run['batch_manifest'] == batch_manifest(local)
        repeat = json.loads((path/'initial_repeat_audit.json').read_text())
        assert repeat['exact_match'] and run['initial_repeat_exact_match']
        assert repeat['keys'] == run['batch_manifest'][0]['keys']
        initial = [r['score']['initial_token_ids'] for r in part_rows[:8]]
        assert initial == repeat['initial_token_ids'] == repeat['repeated_initial_token_ids']
        assert run['continued'] == sum(r['score']['initial_censored'] for r in part_rows)
        runs.append(run)
        rows.extend(part_rows)
    assert sorted(r['part'] for r in runs) == list(range(N_PARTS))
    for field in ('script_sha256', 'dependency_sha256', 'model_assets_sha256', 'actual_model_type',
                  'model_config_sha256', 'torch', 'transformers', 'cuda', 'dtype', 'attention',
                  'batch_size', 'generation', 'declared_model_revision', 'hostname', 'python'):
        assert len({json.dumps(r[field], sort_keys=True) for r in runs}) == 1, field
    assert runs[0]['generation'] == {'initial': 1024, 'continuation': 2048, 'do_sample': False, 'reasoning_effort': 'medium'}
    audit = validate_rows(cs, rows)
    assert audit['phase_counts'] == {'criterion': 128, 'native': 512}
    assert audit['condition_counts'] == {'opposite': 320, 'aligned': 320}
    rows.sort(key=sort_key)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'behavior_merged.jsonl').exists(), 'Refusing to overwrite a completed merge.'
    (out/'behavior_merged.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    audit.update(gpu_hours=sum(r['gpu_hours'] for r in runs), contexts_sha256=CONTEXTS_SHA256,
                 script_sha256=runs[0]['script_sha256'], dependency_sha256=runs[0]['dependency_sha256'],
                 parts=sorted(r['part'] for r in runs), initial_repeat_all_parts_exact=True)
    write_json(out/'analysis.json', analyze(rows))
    write_json(out/'completeness_audit.json', audit)
    write_json(out/'source_runs.json', sorted(runs, key=lambda r: r['part']))
    print(json.dumps(audit), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--part', type=int, choices=range(N_PARTS))
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
    local = cs[2*args.part:2*args.part+2]
    stages = {kind: records(local, kind) for kind in KINDS}
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'behavior.jsonl').exists(), 'Refusing to overwrite prior model results.'
    write_json(out/'design_audit.json', audit)
    (out/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    examples = {kind: {condition: next(r['body'] for r in stages[kind] if r['condition'] == condition)
                       for condition in CONDITIONS} for kind in KINDS}
    write_json(out/'example.json', examples)
    if args.design_only:
        print(json.dumps({k: v for k, v in audit.items() if k not in ('world_checks', 'batch_manifest')}))
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
    assert isinstance(tok.eos_token_id, int)
    config_path = Path(args.model)/'config.json'
    config = json.loads(config_path.read_text())
    assert config.get('text_config', config)['model_type'] == 'qwen3_5_text'
    dependencies = [Path(__file__).with_name(name) for name in
                    ('e99_confirm_factor_interface.py', 'e95_source_grouping.py', 'e93_selective_sharing.py')]
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    dependency_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    asset_names = ('config.json', 'generation_config.json', 'tokenizer.json', 'tokenizer_config.json',
                   'special_tokens_map.json', 'model.safetensors.index.json')
    assets = {name: hashlib.sha256((Path(args.model)/name).read_bytes()).hexdigest()
              for name in asset_names if (Path(args.model)/name).exists()}
    generation_config = {'initial': INITIAL_BUDGET, 'continuation': CONTINUATION_BUDGET,
                         'do_sample': False, 'reasoning_effort': 'medium'}

    def prompt(row):
        return tok.apply_chat_template([{'role': 'system', 'content': SYSTEM},
                                        {'role': 'user', 'content': row['body']}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=True,
                                       reasoning_effort='medium')

    write_json(out/'preflight.json', {'part': args.part, 'context_ids': [c['context'] for c in local],
                                    'expected_rows': 160, 'batch_size': BATCH_SIZE, 'generation': generation_config,
                                    'contexts_sha256': CONTEXTS_SHA256, 'script_sha256': code_hash,
                                    'dependency_sha256': dependency_hashes, 'model_assets_sha256': assets,
                                    'declared_model_revision': DECLARED_REVISION,
                                    'revision_scope': 'Frozen provenance declaration; asset hashes audit the locally supplied model.',
                                    'model_path_resolved': str(Path(args.model).resolve()),
                                    'no_cache_interventions': True})
    start = time.time()
    print('Loading E100 part', args.part, flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
                       dtype=torch.bfloat16, device_map='cuda', attn_implementation='sdpa', output_loading_info=True)
    model.eval()
    model.requires_grad_(False)
    assert not loading.get('missing_keys'), loading
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    write_json(out/'loading_info.json', json.loads(json.dumps(loading, default=str)))
    print('Loaded', flush=True)
    rows, batches, continued = [], [], 0
    repeat_exact = False
    with torch.inference_mode(), (out/'behavior.jsonl').open('w') as stream, (out/'prompts.jsonl').open('w') as prompts:
        for kind in KINDS:
            stage = stages[kind]
            assert len(stage) == (32 if kind == 'criterion' else 128)
            with (out/(kind+'.jsonl')).open('w') as phase_stream:
                for offset in range(0, len(stage), BATCH_SIZE):
                    batch = stage[offset:offset+BATCH_SIZE]
                    texts = [prompt(r) for r in batch]
                    xx = tok(texts, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
                    width = xx.input_ids.shape[1]
                    generated = model.generate(**xx, max_new_tokens=INITIAL_BUDGET, do_sample=False,
                                               pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                    raw_batch = generated[:, width:].tolist()
                    if not rows:
                        repeated = model.generate(**xx, max_new_tokens=INITIAL_BUDGET, do_sample=False,
                                                  pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                        repeated_raw = repeated[:, width:].tolist()
                        repeat_exact = raw_batch == repeated_raw
                        write_json(out/'initial_repeat_audit.json', {'keys': [list(key(r)) for r in batch],
                                   'exact_match': repeat_exact, 'initial_token_ids': raw_batch,
                                   'repeated_initial_token_ids': repeated_raw,
                                   'scope': 'Repeat first eight original initial generations, including batch padding; no answer selection.'})
                        assert repeat_exact, 'First initial generation was not exactly repeatable.'
                    for j, r in enumerate(batch):
                        initial = raw_batch[j]
                        raw, more = initial[:], []
                        initial_censored = tok.eos_token_id not in initial
                        prompt_ids = xx.input_ids[j][xx.attention_mask[j].bool()].tolist()
                        continuation_sha = None
                        if initial_censored:
                            full = prompt_ids + initial
                            continuation_sha = digest(full)
                            fi = torch.tensor([full], device='cuda')
                            more = model.generate(input_ids=fi, attention_mask=torch.ones_like(fi),
                                                  max_new_tokens=CONTINUATION_BUDGET, do_sample=False,
                                                  pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)[0, len(full):].tolist()
                            raw += more
                            assert raw[:len(initial)] == initial
                            continued += 1
                        if tok.eos_token_id in raw:
                            raw = raw[:raw.index(tok.eos_token_id)+1]
                        text = tok.decode(raw, skip_special_tokens=False)
                        cl, status = parse(text, LABELS[kind])
                        score = {'class': cl, 'valid': cl != 0, 'parse_status': status,
                                 'text': text, 'token_ids': raw, 'initial_token_ids': initial,
                                 'continuation_token_ids': more, 'initial_censored': initial_censored,
                                 'still_censored': tok.eos_token_id not in raw,
                                 'initial_prefix_preserved': True, 'continuation_prompt_sha256': continuation_sha,
                                 'initial_generated_tokens': len(initial) if initial_censored else initial.index(tok.eos_token_id)+1}
                        row = {k: v for k, v in r.items() if k != 'body'}
                        row.update(score=score, prompt_sha256=sha_text(texts[j]), body_sha256=sha_text(r['body']),
                                   prompt_token_ids_sha256=digest(prompt_ids), eos_token_id=tok.eos_token_id)
                        rows.append(row)
                        line = json.dumps(row)+'\n'
                        stream.write(line)
                        phase_stream.write(line)
                        prompts.write(json.dumps(dict(r, prompt=texts[j], prompt_token_ids=prompt_ids))+'\n')
                    stream.flush()
                    phase_stream.flush()
                    prompts.flush()
                    batches.append({'kind': kind, 'batch_index': offset//BATCH_SIZE, 'keys': [list(key(r)) for r in batch]})
                    print(kind, offset+len(batch), '/', len(stage), 'continued', continued, flush=True)
            write_json(out/('analysis_'+kind+'.json'), analyze([r for r in rows if r['kind'] == kind]))
    elapsed = time.time()-start
    assert batches == batch_manifest(local)
    completeness = validate_rows(local, rows)
    validate_prompts(local, rows, read_jsonl(out/'prompts.jsonl'))
    write_json(out/'analysis.json', analyze(rows))
    write_json(out/'completeness_audit.json', completeness)
    assert code_hash == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'Running script changed on disk.'
    assert dependency_hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}, 'Dependency changed on disk.'
    gpu = torch.cuda.get_device_properties(0)
    run = {'part': args.part, 'args': vars(args), 'n_rows': len(rows), 'batch_manifest': batches,
           'contexts_sha256': CONTEXTS_SHA256, 'script_sha256': code_hash, 'dependency_sha256': dependency_hashes,
           'model_config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
           'model_assets_sha256': assets, 'declared_model_revision': DECLARED_REVISION,
           'model_path_resolved': str(Path(args.model).resolve()), 'actual_model_type': model.config.model_type,
           'dtype': 'bfloat16', 'attention': 'sdpa', 'batch_size': BATCH_SIZE, 'generation': generation_config,
           'training': False, 'initial_repeat_exact_match': repeat_exact, 'continued': continued,
           'elapsed_seconds': elapsed, 'gpu_hours': elapsed/3600, 'python': platform.python_version(),
           'python_executable': sys.executable, 'torch': torch.__version__, 'transformers': transformers.__version__,
           'transformers_path': transformers.__file__, 'cuda': torch.version.cuda,
           'hostname': socket.gethostname(), 'gpu_name': gpu.name, 'gpu_uuid': str(getattr(gpu, 'uuid', 'unavailable')),
           'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    write_json(out/'run.json', run)
    print('Complete', len(rows), 'rows;', elapsed, 'seconds', flush=True)


if __name__ == '__main__':
    main()
