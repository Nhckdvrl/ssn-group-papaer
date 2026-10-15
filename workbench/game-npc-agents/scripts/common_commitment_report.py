#!/usr/bin/env python3
"""E60 paired native consequences with complete frozen natural comparisons."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads((args.run / 'manifest.json').read_text())
    runtime = json.loads((args.run / 'runtime.json').read_text())
    rows = list(map(json.loads, (args.run / 'branches.jsonl').read_text().splitlines()))
    natural_path = Path(manifest['natural_source']) / 'branches.jsonl'
    assert hashlib.sha256(natural_path.read_bytes()).hexdigest() == manifest['natural_branches_sha256']
    natural = [r for r in map(json.loads, natural_path.read_text().splitlines())
               if r['persona'].startswith('full_') and r['condition'] == 'plan_grounded']
    by = {(r['case_id'], r['persona'], 'fixed_future'): r for r in rows}
    by.update({(r['case_id'], r['persona'].removeprefix('full_'), 'natural'): r for r in natural})
    ids = sorted({r['case_id'] for r in rows})
    assert len(rows) == len(natural) == 400 and len(ids) == 200
    assert set(by) == {(cid, p, c) for cid in ids for p in ['firm', 'agreeable']
                      for c in ['natural', 'fixed_future']}
    case_path = Path(manifest['source_manifest']['arguments']['dataset'])
    cases = {r['case_id']: r for r in map(json.loads, case_path.read_text().splitlines())}
    report = {'manifest': manifest, 'runtime': runtime, 'graphs': 200,
              'new_native_branches': 400, 'frozen_natural_branches': 400,
              'cells': {}, 'contrasts': {}}
    read = lambda cid, p, c, flag: float(by[cid, p, c]['flags'][flag])
    for p in ['firm', 'agreeable']:
        for c in ['natural', 'fixed_future']:
            rs = [by[cid, p, c] for cid in ids]
            native = [event for r in rs for event in r['history']]
            report['cells'][p+'/'+c] = {
                flag: estimate([float(r['flags'][flag]) for r in rs])
                for flag in ['request', 'own_task']}
            report['cells'][p+'/'+c].update({
                'steps': estimate([r['steps'] for r in rs]),
                'outcome_flags': dict(Counter(json.dumps(r['flags'], sort_keys=True) for r in rs)),
                'stances': dict(Counter(r['conversation']['stance'] for r in rs)),
                'plan_contains_request': estimate([
                    float(cases[r['case_id']]['request_command'] in r['update']['priority_actions']) for r in rs]),
                'plan_contains_own': estimate([
                    float(cases[r['case_id']]['goal_command'] in r['update']['priority_actions']) for r in rs]),
                'protocol_errors': sum(bool(r['protocol_error']) for r in rs),
                'native_nonlegal_events': sum(not bool(e.get('legal')) for e in native),
                'native_unexecuted_events': sum(not bool(e.get('executed')) for e in native),
                'native_error_events': sum(e.get('event_type') == 'ErrorEvent' for e in native),
                'native_stochastic_failures': sum(bool(e.get('stochastic_failure')) for e in native)})
        for flag in ['request', 'own_task']:
            report['contrasts'][p+'/fixed-natural/'+flag] = estimate([
                read(cid, p, 'fixed_future', flag) - read(cid, p, 'natural', flag) for cid in ids])
    for c in ['natural', 'fixed_future']:
        for flag in ['request', 'own_task']:
            report['contrasts']['persona/'+c+'/'+flag] = estimate([
                read(cid, 'agreeable', c, flag) - read(cid, 'firm', c, flag) for cid in ids])
    for flag in ['request', 'own_task']:
        report['contrasts']['change_in_persona_effect/'+flag] = estimate([
            read(cid, 'agreeable', 'fixed_future', flag) - read(cid, 'firm', 'fixed_future', flag)
            - read(cid, 'agreeable', 'natural', flag) + read(cid, 'firm', 'natural', flag) for cid in ids])
    calls = list(map(json.loads, (args.run / 'model_calls.jsonl').read_text().splitlines()))
    assert len(calls) == runtime['calls']
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
        'prompt_tokens': sum(r['prompt_tokens'] for r in calls),
        'completion_tokens': sum(r['completion_tokens'] for r in calls), 'cloud_calls': 0}
    report['scope'] = [
        'Same independent 200 graphs, not 800 independent worlds; a single paired action seed.',
        'Persona is coherent, and the experimentally fixed prior utterance contains no persona description.',
        'Natural-to-fixed intervention changes acceptance/content/length, not only tense or memory quality.',
        'Plans and memories are post-intervention variables; differences do not alone identify a mediator.',
        'Factual answers and DATA labels are never policy inputs or world judges.',
        'First resource decision is an event, not total private welfare or a unique persona gold action.',
        'Native errors and unsettled outcomes remain; sampling batch shapes differ from the frozen comparison.']
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'graphs': 200, 'contrasts': report['contrasts'],
                      'calls': report['calls'], 'runtime': runtime}))


if __name__ == '__main__':
    main()
