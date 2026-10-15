#!/usr/bin/env python3
"""E61 full-world comparisons; verb strata are explicitly exploratory."""
import argparse
from collections import Counter
import json
from pathlib import Path
from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--plan-run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads((args.run / 'manifest.json').read_text())
    runtime = json.loads((args.run / 'runtime.json').read_text())
    actual = list(map(json.loads, (args.run / 'branches.jsonl').read_text().splitlines()))
    plan = list(map(json.loads, (args.plan_run / 'branches.jsonl').read_text().splitlines()))
    natural = [r for r in map(json.loads, (Path(manifest['natural_source']) / 'branches.jsonl').read_text().splitlines())
               if r['condition'] == 'direct' and r['persona'].startswith('full_')]
    assert len(actual) == len(plan) == len(natural) == 400
    by = {(r['case_id'], r['persona'], 'common_direct'): r for r in actual}
    by.update({(r['case_id'], r['persona'], 'common_plan'): r for r in plan})
    by.update({(r['case_id'], r['persona'].removeprefix('full_'), 'natural_direct'): r for r in natural})
    ids = sorted({r['case_id'] for r in actual})
    assert len(ids) == 200 and len(by) == 1200
    kinds = {r['case_id']: r['goal_kind'] for r in actual}
    groups = {'all': ids, 'same_verb': [cid for cid in ids if kinds[cid] == 'give'],
              'different_verb': [cid for cid in ids if kinds[cid] != 'give']}
    groups.update({kind: [cid for cid in ids if kinds[cid] == kind] for kind in sorted(set(kinds.values()))})
    report = {'manifest': manifest, 'runtime': runtime, 'graphs': 200,
              'cells': {}, 'contrasts': {}, 'verb_strata': {}}
    conditions = ['natural_direct', 'common_direct', 'common_plan']
    read = lambda cid, p, c, flag: float(by[cid, p, c]['flags'][flag])
    for condition in conditions:
        for persona in ['firm', 'agreeable']:
            rows = [by[cid, persona, condition] for cid in ids]
            events = [e for r in rows for e in r['history']]
            report['cells'][persona+'/'+condition] = {
                flag: estimate([float(r['flags'][flag]) for r in rows]) for flag in ['request', 'own_task']}
            report['cells'][persona+'/'+condition].update({
                'steps': estimate([r['steps'] for r in rows]),
                'protocol_errors': sum(bool(r['protocol_error']) for r in rows),
                'native_error_events': sum(e.get('event_type') == 'ErrorEvent' for e in events),
                'outcome_flags': dict(Counter(json.dumps(r['flags'], sort_keys=True) for r in rows))})
        for flag in ['request', 'own_task']:
            report['contrasts']['persona/'+condition+'/'+flag] = estimate([
                read(cid, 'agreeable', condition, flag)-read(cid, 'firm', condition, flag) for cid in ids])
    for persona in ['firm', 'agreeable']:
        for control in ['natural_direct', 'common_plan']:
            for flag in ['request', 'own_task']:
                report['contrasts'][persona+'/direct-'+control+'/'+flag] = estimate([
                    read(cid, persona, 'common_direct', flag)-read(cid, persona, control, flag) for cid in ids])
    for group, group_ids in groups.items():
        report['verb_strata'][group] = {'graphs': len(group_ids), 'persona_request_effect': {
            c: estimate([read(cid, 'agreeable', c, 'request')-read(cid, 'firm', c, 'request')
                         for cid in group_ids]) for c in conditions}}
    calls = list(map(json.loads, (args.run / 'model_calls.jsonl').read_text().splitlines()))
    assert len(calls) == runtime['calls']
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
                      'prompt_tokens': sum(r['prompt_tokens'] for r in calls),
                      'completion_tokens': sum(r['completion_tokens'] for r in calls), 'cloud_calls': 0}
    report['scope'] = [
        'Same 200 independent worlds, one paired action seed, coherent role packages.',
        'The common utterance is an explicit history intervention and no conflicting persona description is replayed.',
        'Direct versus plan differs in information representation and generated content, not an isolated module effect.',
        'Verb strata come from observed E58 clues and are exploratory; role/resource/goal composition co-varies.',
        'Exact original goal event, recipient allocation and total character interests remain distinct.',
        'No unique persona gold action; native errors and unsettled outcomes retained.']
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'graphs': 200, 'contrasts': {k:v for k,v in report['contrasts'].items() if k.startswith('persona/')},
                      'calls': report['calls'], 'runtime': runtime, 'verb_strata': {
                        g: report['verb_strata'][g] for g in ['same_verb', 'different_verb']}}))


if __name__ == '__main__':
    main()
