#!/usr/bin/env python3
"""E56: separate factual answers, instruction scope and executed native events."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    manifest = json.loads((a.directory / 'manifest.json').read_text())
    runtime = json.loads((a.directory / 'runtime.json').read_text())
    rows = list(map(json.loads, (a.directory / 'branches.jsonl').read_text().splitlines()))
    cases = {r['case_id']: r for r in map(json.loads, Path(manifest['arguments']['dataset']).read_text().splitlines())}
    lookup = {(r['case_id'], r['persona'], r['condition']): r for r in rows}
    assert len(rows) == len(lookup) == 2000
    assert len({r['graph_sha256'] for r in rows}) == len(cases) == 200
    conditions = manifest['conditions']
    assert set(lookup) == {(cid, p, c) for cid in cases for p in ['firm', 'agreeable'] for c in conditions}
    report = {'manifest': manifest, 'runtime': runtime, 'graphs': 200, 'branches': 2000,
              'cells': {}, 'contrasts': {}, 'readout_counts': {}, 'engine_rejections': {},
              'protocol_errors': sum(bool(r['protocol_error']) for r in rows)}
    def metric(r, field):
        if field in ['own_task', 'request']: return float(r['flags'][field])
        if field == 'unresolved_or_other': return float(not (r['flags']['own_task'] or r['flags']['request']))
        if field == 'steps': return float(r['steps'])
        answer = r.get('state_readout')
        if not answer: return 0.
        if field == 'holder_correct': return float(answer['holder'] == r['expected_holder'])
        if field == 'request_command_correct': return float(answer['requested_command'] == cases[r['case_id']]['request_command'])
        if field == 'own_completed_answer': return float(answer['own_event_done'] == 'yes')
        if field == 'request_completed_answer': return float(answer['request_event_done'] == 'yes')
        raise ValueError(field)
    def paired(left, right, field):
        points = defaultdict(list)
        for cid in cases:
            for p1, c1, p0, c0 in [(left[0], left[1], right[0], right[1])]:
                points[cid].append(metric(lookup[cid, p1, c1], field) - metric(lookup[cid, p0, c0], field))
        return estimate([np.mean(x) for x in points.values()])
    for p in ['firm', 'agreeable']:
        for c in conditions:
            rs = [lookup[cid, p, c] for cid in cases]
            fields = ['own_task', 'request', 'unresolved_or_other', 'steps']
            if not c.startswith('force_'):
                fields += ['holder_correct', 'request_command_correct', 'own_completed_answer', 'request_completed_answer']
                report['readout_counts'][p + '/' + c] = {
                    f: dict(Counter((r.get('state_readout') or {}).get(f, 'parse_error') for r in rs))
                    for f in ['own_event_done', 'request_event_done']}
            report['cells'][p + '/' + c] = {f: estimate([metric(r, f) for r in rs]) for f in fields}
            report['cells'][p + '/' + c]['first_events'] = dict(Counter(r['history'][0]['event_type'] if r['history'] else 'no_event' for r in rs))
            report['engine_rejections'][p + '/' + c] = dict(Counter(h.get('error', 'unspecified') for r in rs for h in r['history'] if not h['legal']))
        for l, r in [('phase_end', 'original_history'), ('phase_fact', 'phase_end')]:
            for f in ['own_task', 'request', 'unresolved_or_other']:
                report['contrasts'][p + '/' + l + '-' + r + '/' + f] = paired((p, l), (p, r), f)
    for c in conditions:
        for f in ['own_task', 'request', 'unresolved_or_other']:
            report['contrasts']['persona/' + c + '/' + f] = paired(('agreeable', c), ('firm', c), f)
    calls = list(map(json.loads, (a.directory / 'model_calls.jsonl').read_text().splitlines()))
    assert len(calls) == runtime['calls']
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
                       'prompt_tokens': sum(r['prompt_tokens'] for r in calls),
                       'completion_tokens': sum(r['completion_tokens'] for r in calls)}
    report['raw_sha256'] = hashlib.sha256((a.directory / 'branches.jsonl').read_bytes()).hexdigest()
    report['scope'] = ['One new sampling seed per fixed source utterance; 200 graph clusters.',
        'Factual answers use an independent question framing and are not fed to the policy; they do not establish latent beliefs.',
        'The retained authored goal and original identity can compete with exact controller instructions; controller noncompliance is not isolated motor inability.',
        'Unresolved negotiation within six actions is not automatically a failure; first resource disposition is not full-episode utility.',
        'Failed native engine events are retained, including repeated block and equipment-capacity errors.']
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'graphs': 200, 'branches': len(rows), 'calls': report['calls'],
                      'request_persona': {c: report['contrasts']['persona/' + c + '/request'] for c in conditions}}))


if __name__ == '__main__': main()
