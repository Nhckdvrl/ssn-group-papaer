#!/usr/bin/env python3
"""E67/E68 graph-paired physical outcomes; no language judge or selected seeds."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np

G, A, B, C = 'generic_priority', 'asset_protection', 'negative_only', 'retention_only'


def metrics(row):
    history = row['history']
    valid = [h for h in history if h['legal'] and h.get('executed') and not h.get('stochastic_failure')]
    blocks = [h['step'] for h in valid if h['event_type'] == 'BlockEvent']
    goals = [h['step'] for h in valid if h['matches_source_goal']]
    transfers = [h['step'] for h in valid if h['matches_requested_transfer']]
    first = history[0] if history else {}
    first_valid = first in valid and bool(first)
    repeat = sum('already blocking' in h.get('error', '').lower() for h in history)
    values = {
        'goal': float(row['goal_executed']), 'transfer': float(row['request_given']),
        'both': float(row['both_completed']),
        'neither': float(not row['goal_executed'] and not row['request_given']),
        'target_given_before_goal': float(row['target_given_before_goal']),
        'first_step_goal': float(bool(first_valid and first.get('matches_source_goal'))),
        'first_step_transfer': float(bool(first_valid and first.get('matches_requested_transfer'))),
        'first_step_block': float(bool(first_valid and first.get('event_type') == 'BlockEvent')),
        'any_legal_block': float(bool(blocks)),
        'block_then_goal': float(bool(blocks and goals and goals[0] > blocks[0])),
        'block_without_goal': float(bool(blocks and not goals)),
        'repeat_block_errors': float(repeat), 'any_repeat_block_error': float(repeat > 0),
        'native_errors': float(sum(not h['legal'] for h in history)),
        'protocol_error': float(bool(row['protocol_error'])),
        'steps': float(len(history)),
        'goal_step_capped_9': float(goals[0]+1 if goals else 9),
        'transfer_step_capped_9': float(transfers[0]+1 if transfers else 9),
        'any_examine': float(any(h['command'].startswith('examine ') for h in valid)),
        'any_speech': float(any(h['command'].split(' ')[0] in ['say','tell','whisper'] for h in valid)),
        'any_emote': float(any(h['command'].startswith('emote ') for h in valid)),
        'no_material_change_fraction': sum(not h['material_changed'] for h in valid)/max(1,len(history)),
    }
    # Competing first events are exhaustive after adding 'other'; speech/examine are not.
    if first_valid and first.get('matches_source_goal'): category = 'task'
    elif first_valid and first.get('matches_requested_transfer'): category = 'transfer'
    elif first_valid and first.get('event_type') == 'BlockEvent': category = 'defense'
    else: category = 'other'
    for k in ['task','transfer','defense','other']: values['first_category_'+k] = float(category == k)
    return values


def summarize(matrix, fields):
    x = np.asarray(matrix, dtype=float)
    assert x.ndim == 2 and len(x)
    rng = np.random.default_rng(6768)
    weights = rng.multinomial(len(x), np.full(len(x), 1/len(x)), size=4000)/len(x)
    means = weights @ x
    lower, upper = np.quantile(means,[.025,.975],axis=0)
    return {f:{'mean':float(x[:,i].mean()), 'graph_bootstrap_95':[float(lower[i]),float(upper[i])],
               'independent_graphs':len(x)} for i,f in enumerate(fields)}


def key(r):
    return (r['case_id'],r['seed'],r['persona'],r['mode'],r['upstream_rule'],r['exec_rule'],r['feedback'])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--experiment', choices=['E67','E68'],required=True)
    ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    sources={r['case']['case_id']:r for r in map(json.loads,a.dataset.read_text().splitlines())
             if a.experiment=='E68' or r['case']['goal_kind'] in ['wear','wield']}
    rows=[]; manifests=[]; runtimes=[]
    for d in a.runs:
        manifests.append(json.loads((d/'manifest.json').read_text()))
        runtimes.append(json.loads((d/'runtime.json').read_text()))
        rows.extend(map(json.loads,(d/'episodes.jsonl').read_text().splitlines()))
    for field in ['experiment','model','seeds','dataset_sha256','execution_sha256','driver_sha256']:
        assert all(m[field]==manifests[0][field] for m in manifests)
    assert manifests[0]['experiment']==a.experiment
    seeds=manifests[0]['seeds']; expected=set()
    for cid,source in sources.items():
        if a.experiment=='E67':
            conditions=[('goal_item',up,ex,fb) for up in [A,G] for ex in [A,G] for fb in ['legacy','block_status']]
            if manifests[0]['include_bc']:conditions += [('goal_item',up,up,fb) for up in [B,C] for fb in ['legacy','block_status']]
        else:
            conditions=[('goal_item',up,up,'block_status') for up in [A,G,B]]
            if source['case']['goal_kind'] in ['wear','wield']:conditions += [('goal_item',A,G,'block_status'),('goal_item',G,A,'block_status')]
            if 'other_item' in source['requests']:conditions += [('other_item',G,G,'block_status')]
        expected.update((cid,s,p,*condition) for s in seeds for p in ['firm','agreeable'] for condition in conditions)
    lookup={key(r):r for r in rows}
    assert len(lookup)==len(rows) and set(lookup)==expected, (len(lookup),len(expected))
    data={k:metrics(r) for k,r in lookup.items()}; fields=list(next(iter(data.values())))
    arrays={k:np.asarray([v[f] for f in fields]) for k,v in data.items()}
    cells={}; contrasts={}
    kinds=['all','wear_wield']+sorted({r['goal_kind'] for r in rows}) if a.experiment=='E68' else ['all','wear','wield']
    def kind_ids(kind):
        return sorted(cid for cid,r in sources.items() if kind=='all' or
                      (kind=='wear_wield' and r['case']['goal_kind'] in ['wear','wield']) or r['case']['goal_kind']==kind)
    conditions=sorted({key(r)[2:] for r in rows})
    for kind in kinds:
        for condition in conditions:
            ids=[cid for cid in kind_ids(kind) if (cid,seeds[0],*condition) in lookup]
            if not ids:continue
            matrix=[np.mean([arrays[cid,s,*condition] for s in seeds],axis=0) for cid in ids]
            cells['/'.join([kind,*condition])]=summarize(matrix,fields)
    def contrast(label,kind,terms):
        ids=[cid for cid in kind_ids(kind) if all((cid,seeds[0],*c) in lookup for _,c in terms)]
        if not ids:return
        matrix=[np.mean([sum(w*arrays[cid,s,*c] for w,c in terms) for s in seeds],axis=0) for cid in ids]
        contrasts[kind+'/'+label]=summarize(matrix,fields)
    for kind in kinds:
        for p in ['firm','agreeable']:
            for fb in (['legacy','block_status'] if a.experiment=='E67' else ['block_status']):
                cond=lambda up,ex:(p,'goal_item',up,ex,fb)
                for up in [A,G]:
                    contrast(f'{p}/{fb}/exec_G_minus_A_given_{up}',kind,[(1,cond(up,G)),(-1,cond(up,A))])
                for ex in [A,G]:
                    contrast(f'{p}/{fb}/upstream_G_minus_A_given_{ex}',kind,[(1,cond(G,ex)),(-1,cond(A,ex))])
                contrast(f'{p}/{fb}/cross_interaction',kind,[(1,cond(G,G)),(-1,cond(G,A)),(-1,cond(A,G)),(1,cond(A,A))])
                for left,right in [(G,A),(B,G),(A,G),(B,C)]:
                    contrast(f'{p}/{fb}/coherent_{left}_minus_{right}',kind,[(1,cond(left,left)),(-1,cond(right,right))])
            if a.experiment=='E67':
                for up,ex in [(A,A),(A,G),(G,A),(G,G),(B,B),(C,C)]:
                    contrast(f'{p}/{up}/{ex}/status_minus_legacy',kind,[(1,(p,'goal_item',up,ex,'block_status')),(-1,(p,'goal_item',up,ex,'legacy'))])
                contrast(f'{p}/feedback_x_B_minus_C',kind,[(1,(p,'goal_item',B,B,'block_status')),(-1,(p,'goal_item',C,C,'block_status')),(-1,(p,'goal_item',B,B,'legacy')),(1,(p,'goal_item',C,C,'legacy'))])
        if a.experiment=='E68':
            contrast('other_item/A_minus_F_generic',kind,[(1,('agreeable','other_item',G,G,'block_status')),(-1,('firm','other_item',G,G,'block_status'))])
    # Exact shared-prefix pairing is a protocol check, not a feedback effect estimate.
    prefix_equal=None
    if a.experiment=='E67':
        prefix_equal=True
        for k,r in lookup.items():
            if k[-1]=='legacy':
                other=lookup[(*k[:-1],'block_status')]
                assert r['history'][:1]==other['history'][:1]
    calls=Counter()
    for d in a.runs:
        for line in (d/'model_calls.jsonl').open():
            r=json.loads(line);calls.update(count=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],completion_tokens=r['completion_tokens'])
    assert calls['count']==sum(r['calls'] for r in runtimes)
    report={'status':'COMPLETE','experiment':a.experiment,'model':manifests[0]['model'],
        'worlds':len(sources),'episodes':len(rows),'seeds':seeds,'cells':cells,'contrasts':contrasts,
        'calls':dict(calls),'reused_calls':sum(r['reused_calls'] for r in runtimes),
        'gpu_hours':sum(r['wall_seconds']+r['model_load_seconds'] for r in runtimes)/3600,
        'runtimes':runtimes,'prefix_feedback_first_step_equal':prefix_equal,
        'protocol_errors':sum(bool(r['protocol_error']) for r in rows),
        'native_errors':dict(Counter(h.get('error','') for r in rows for h in r['history'] if not h['legal'])),
        'native_stochastic_failures':sum(bool(h.get('stochastic_failure')) for r in rows for h in r['history']),
        'source_sha256':{str(d/'episodes.jsonl'):hashlib.sha256((d/'episodes.jsonl').read_bytes()).hexdigest() for d in a.runs},
        'scope':['Three seeds averaged per graph; graph-paired 4000 bootstrap resamples, pointwise intervals.',
                 'First legal defense and repeated rejection are different outcomes.',
                 'Upstream factor includes conversation and plan/memory together; no additive mediation assumption.',
                 'Other-item outcomes use an independent native feasible item, not an economic welfare label.']}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','experiment','worlds','episodes','calls','gpu_hours']}))


if __name__=='__main__':main()
