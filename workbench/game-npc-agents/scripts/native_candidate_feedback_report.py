#!/usr/bin/env python3
"""E72 same-dialogue candidate-set contrast and native feedback recovery."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_request_precondition_execution import SEEDS
from native_request_precondition_report import metrics as base_metrics
from native_rule_cross_report import summarize


def metrics(row):
    m = base_metrics(row); h = row['history']
    commands = {row['goal_command'], row['request_command']}
    feedback = [x['step'] for x in h if x['command'] in commands and not x['legal'] and 'remove' in x.get('error', '').lower()]
    remove = [x['step'] for x in h if x['legal'] and x.get('executed') and not x.get('stochastic_failure')
              and x['event_type'] == 'RemoveObjectEvent' and x['target_node_ids'][0] == row['goal_item_id']]
    received = bool(feedback); then_remove = bool(feedback and remove and remove[-1] > feedback[0])
    transferred = row['first_recipient'] is not None
    then_give = bool(feedback and transferred and len(h)-1 > feedback[0])
    m.update(native_remove_feedback=float(received), feedback_then_remove=float(then_remove),
             feedback_then_source_give=float(then_give), feedback_then_goal=float(then_give and m['to_goal']),
             feedback_then_competitor=float(then_give and m['to_competitor']),
             first_invalid_source_give=float(bool(feedback and feedback[0] == 0)),
             first_attempt_goal_command=float(bool(h and h[0]['command'] == row['goal_command'])),
             first_attempt_request_command=float(bool(h and h[0]['command'] == row['request_command'])))
    return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--prior-runs', type=Path, nargs='+', required=True)
    ap.add_argument('--data', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); sources = {r['case']['case_id']: r for r in map(json.loads,args.data.open())}
    lookup = {}; prior = {}; runtimes = []; manifests = []; calls = Counter(); hashes = {}
    for folder in args.prior_runs:
        assert (folder/'runtime.json').exists()
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            if r['condition'] in ['equipped_aligned', 'equipped_divert']:
                k = r['case_id'], r['seed'], r['persona'], r['direction']
                assert k not in prior; prior[k] = r
    for folder in args.runs:
        runtimes.append(json.loads((folder/'runtime.json').read_text()))
        manifests.append(json.loads((folder/'manifest.json').read_text()))
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            k = r['case_id'],r['seed'],r['persona'],r['condition']
            assert k not in lookup
            assert r['conversation'] == prior[r['case_id'],r['seed'],r['persona'],r['direction']]['conversation']
            lookup[k] = r
        for r in map(json.loads,(folder/'model_calls.jsonl').open()):
            assert r['stage'] == 'exec'
            calls.update(count=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],completion_tokens=r['completion_tokens'])
        hashes[str(folder/'episodes.jsonl')] = hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    conditions = [d+'_'+a for d in ['aligned','divert'] for a in ['valid_candidates','goal_candidates']]
    expected = {(cid,s,p,c) for cid in sources for s in SEEDS for p in ['firm','agreeable'] for c in conditions}
    assert set(lookup) == expected and len(lookup) == 2808
    assert all(m['script_sha256'] == manifests[0]['script_sha256'] and m['model'] == manifests[0]['model']
               and m['data_sha256'] == manifests[0]['data_sha256'] for m in manifests)
    for (cid,s,p,d),r in prior.items(): lookup[cid,s,p,d+'_e70_baseline'] = r
    assert len(lookup) == 4212
    values = {k:metrics(r) for k,r in lookup.items()}; fields = list(next(iter(values.values())))
    def estimate(terms):
        return summarize([np.mean([[sum(w*values[cid,s,p,c][f] for w,p,c in terms) for f in fields]
                                    for s in SEEDS],axis=0) for cid in sorted(sources)],fields)
    cells = {}; contrasts = {}; transitions = {}
    for d in ['aligned','divert']:
        for arm in ['valid_candidates','goal_candidates','e70_baseline']:
            c = d+'_'+arm
            for p in ['firm','agreeable']: cells[p+'/'+c] = estimate([(1,p,c)])
            contrasts['A_minus_F/'+c] = estimate([(1,'agreeable',c),(-1,'firm',c)])
        for p in ['firm','agreeable']:
            a,b = d+'_valid_candidates',d+'_goal_candidates'
            contrasts[p+'/goal_minus_valid/'+d] = estimate([(1,p,b),(-1,p,a)])
            contrasts[p+'/valid_minus_e70/'+d] = estimate([(1,p,a),(-1,p,d+'_e70_baseline')])
            counter = Counter()
            for cid in sources:
                for s in SEEDS:
                    va,vb = values[cid,s,p,a],values[cid,s,p,b]
                    oa = next(k for k in ['to_goal','to_competitor','to_other','no_transfer'] if va[k])
                    ob = next(k for k in ['to_goal','to_competitor','to_other','no_transfer'] if vb[k])
                    counter[oa+' -> '+ob] += 1
            transitions[p+'/'+d] = dict(counter)
        contrasts['persona_x_candidates/'+d] = estimate([(1,'agreeable',d+'_goal_candidates'),(-1,'firm',d+'_goal_candidates'),
                                                        (-1,'agreeable',d+'_valid_candidates'),(1,'firm',d+'_valid_candidates')])
    assert calls['count'] == sum(r['calls'] for r in runtimes)
    result = {'status':'COMPLETE','experiment':'E72','worlds':117,'episodes':2808,'model':manifests[0]['model'],
              'cells':cells,'contrasts':contrasts,'paired_transitions':transitions,'actual_calls':dict(calls),
              'runtime_gpu_hours':sum(r['wall_seconds']+r['model_load_seconds'] for r in runtimes)/3600,
              'runtimes':runtimes,'source_sha256':hashes,'data_sha256':manifests[0]['data_sha256'],
              'scope':['Both arms share exact E70 dialogue and common neutral proposal directive; only candidate list/enum differs.',
                       'Failed native attempts consume steps; no retry, scripted repair or altered engine rule.',
                       'Recovered trajectories do not prove pre-existing internal knowledge; native feedback itself supplies information.',
                       'Candidate expansion also supplies action anchors; feedback-then-recovery describes a path, not an independently isolated necessary mediator.',
                       'Valid-minus-E70 also changes directive wording and is descriptive, not the candidate-set effect.',
                       'First exact-source-item Give, not entire-game private utility; 4000 paired graph bootstrap samples.']}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','episodes','actual_calls','runtime_gpu_hours']}),flush=True)


if __name__ == '__main__': main()
