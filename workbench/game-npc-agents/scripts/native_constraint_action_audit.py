#!/usr/bin/env python3
"""Post-hoc physical action destinations for all E65 worlds, without a judge."""
import json
import hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    cache = Path('/home/xiang/.cache/game-npc-research/runs')
    out = Path(__file__).resolve().parents[1] / 'results/E65_action_destinations_POST_HOC.json'
    ids = {r['case']['case_id'] for r in map(json.loads, (cache/'e63_native_dependency_qualification/snapshots.jsonl').read_text().splitlines())
           if r['case']['goal_kind'] in ['wear', 'wield']}
    sources = [cache/n/'episodes.jsonl' for n in ['e65_gemma_scope_s0', 'e65_gemma_scope_s1', 'e63_gemma_dependency']]
    rows = [r for p in sources for r in map(json.loads, p.read_text().splitlines())
            if r['case_id'] in ids and r['mode'] == 'goal_item']
    assert len(rows) == 3792
    data, counts = {}, {}
    for r in rows:
        h = r['history']
        block = [a for a in h if a['command'].startswith('block ')]
        repeat = [a for a in block if not a['legal'] and 'already blocking' in a.get('error', '')]
        valid = [a for a in block if a['legal'] and a.get('executed')]
        data[r['case_id'], r['seed'], r['persona'], r['rule']] = {
            'any_valid_block': float(bool(valid)),
            'valid_block_without_original_goal': float(bool(valid) and not r['goal_executed']),
            'any_repeated_block_error': float(bool(repeat)),
            'repeated_block_errors': float(len(repeat)),
            'other_native_errors': float(sum(not a['legal'] for a in h)-len(repeat)),
            'any_native_error': float(any(not a['legal'] for a in h)),
        }
        key = r['persona']+'/'+r['rule']
        counts.setdefault(key, Counter()).update({
            'episodes': 1, 'actions': len(h), 'valid_block_actions': len(valid),
            'repeated_block_errors': len(repeat), 'native_errors': sum(not a['legal'] for a in h)})
    rules = sorted({r['rule'] for r in rows})
    cells, contrasts = {}, {}
    for persona in ['firm', 'agreeable']:
        def aggregate(left, right=None):
            return {f: estimate([np.mean([data[cid,s,persona,left][f] -
                           (data[cid,s,persona,right][f] if right else 0)
                           for s in [6301,6302,6303]]) for cid in sorted(ids)])
                    for f in next(iter(data.values()))}
        for rule in rules:
            cells[persona+'/'+rule] = aggregate(rule)
        for left, right in [('negative_only','retention_only'), ('temporal_permission','negative_only'),
                            ('asset_protection','generic_priority')]:
            contrasts[persona+'/'+left+'-minus-'+right] = aggregate(left,right)
    result = {'status':'COMPLETE','label':'POST-HOC; triggered by complete-cohort native errors',
              'worlds':len(ids),'new_episodes':2370,'reference_episodes':1422,
              'counts':counts,'cells':cells,'contrasts':contrasts,
              'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              'model_calls':0,'scope':['No filtering or changed outcome; all 79 source worlds retained.',
                 'Blocking can implement defense; its presence is not proof of rational utility or safety intent.',
                 'Repeated already-blocking errors are native engine outcomes, not JSON parsing failures.']}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'worlds':len(ids),'rows':len(rows),'model_calls':0}))


if __name__ == '__main__':
    main()
