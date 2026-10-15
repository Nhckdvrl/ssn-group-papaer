#!/usr/bin/env python3
"""E75 graph-paired task/request outcomes across original authored task families."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_retrieval_execution import CONDITIONS, SEEDS
from native_rule_cross_report import summarize


def successful(h):
    return h['legal'] and h.get('executed') and not h.get('stochastic_failure')


def metrics(r):
    hs = r['history']; first = hs[0] if hs else None
    source = r['goal_item_id']; peer = r['first_source_recipient']
    is_get = lambda h: bool(successful(h) and h['event_type']=='GetObjectEvent' and h['target_node_ids'][0]==source)
    return {'goal':float(r['goal_executed']),
        'request':float(peer==r['requester_id']),
        'other_source_give':float(peer is not None and not r['goal_executed'] and peer!=r['requester_id']),
        'no_decisive_event':float(not r['goal_executed'] and peer is None),
        'retrieved':float(any(is_get(h) for h in hs)),
        'first_retrieve':float(bool(first and is_get(first))),
        'first_goal':float(bool(first and successful(first) and first['matches_bound_source_goal'])),
        'first_request':float(bool(first and successful(first) and first['source_item_give']
                                    and first['target_node_ids'][1]==r['requester_id'])),
        'other_item_give':float(any(successful(h) and h['event_type']=='GiveObjectEvent'
                                  and h['target_node_ids'][0]!=source for h in hs)),
        'invalid_attempts':sum(not h['legal'] for h in hs),
        'failed_event_attempts':sum(bool(h.get('stochastic_failure')) for h in hs),
        'death':float(any(h['after'].get(r['actor_id'],{}).get('dead') for h in hs)),
        'protocol_failure':float(bool(r['protocol_error'])), 'steps':len(hs)}


def validate(row, source):
    goal = source['native_goal_identity']; actual_goal = False; recipients = []; count = Counter()
    for h in row['history']:
        if not successful(h):
            continue
        ident = [h['event_type'],h['target_node_ids']]
        actual_goal |= ident==goal
        if h['event_type']=='GetObjectEvent' and h['target_node_ids'][0]==row['goal_item_id']:
            i = row['goal_item_id']
            assert h['before'][i]['container']==h['target_node_ids'][1]
            assert h['after'][i]['container']==row['actor_id']
            count['source_gets'] += 1
        if h['event_type']=='GiveObjectEvent' and h['target_node_ids'][0]==row['goal_item_id']:
            i = row['goal_item_id']; peer = h['target_node_ids'][1]
            assert h['before'][i]['container']==row['actor_id'] and h['after'][i]['container']==peer
            recipients.append(peer); count['source_gives'] += 1
        if ident==goal:
            count['bound_goal_events'] += 1
            if row['goal_kind']=='wear':
                assert h['after'][row['goal_item_id']]['equipped']
            elif row['goal_kind'] in ['eat','drink']:
                assert h['after'][row['goal_item_id']]['container']=='VOID'
    assert actual_goal==row['goal_executed']
    assert len(recipients)<=1 and (recipients[0] if recipients else None)==row['first_source_recipient']
    return count


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();sources={r['case']['case_id']:r for r in map(json.loads,args.data.open())}
    assert len(sources)==102
    rows={};calls=Counter();validation=Counter();hashes={};hours=0
    model=json.loads((args.runs[0]/'manifest.json').read_text())['model']
    for folder in args.runs:
        rt=json.loads((folder/'runtime.json').read_text())
        assert json.loads((folder/'manifest.json').read_text())['model']==model
        hours+=(rt['wall_seconds']+rt['model_load_seconds'])/3600
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            key=r['case_id'],r['seed'],r['persona'],r['condition'];assert key not in rows;rows[key]=r
            validation.update(validate(r,sources[r['case_id']]))
        for r in map(json.loads,(folder/'model_calls.jsonl').open()):
            calls.update(calls=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],
                         completion_tokens=r['completion_tokens']);calls['stage_'+r['stage']]+=1
        for filename in ['episodes.jsonl','model_calls.jsonl','manifest.json']:
            hashes[str(folder/filename)]=hashlib.sha256((folder/filename).read_bytes()).hexdigest()
    assert len(rows)==2448 and {k[0] for k in rows}==set(sources)
    for cid in sources:
        for seed in SEEDS:
            for p in ['firm','agreeable']:
                for state in ['ready','retrieval']:
                    a=rows[cid,seed,p,state+'_baseline'];b=rows[cid,seed,p,state+'_paths']
                    assert a['conversation']==b['conversation']
                    assert a['native_goal_identity']==b['native_goal_identity']==sources[cid]['native_goal_identity']
    vals={k:metrics(r) for k,r in rows.items()};fields=list(next(iter(vals.values())))
    groups={'all':list(sources),'source_give':[c for c,r in sources.items() if r['case']['goal_kind']=='give'],
            'source_use':[c for c,r in sources.items() if r['case']['goal_kind']!='give']}
    groups.update({'kind_'+k:[c for c,r in sources.items() if r['case']['goal_kind']==k] for k in ['wear','eat','drink']})
    output={}
    for name,cids in groups.items():
        def estimate(terms):
            arrays=[np.mean([[sum(w*vals[cid,s,p,c][f] for w,p,c in terms) for f in fields]
                             for s in SEEDS],axis=0) for cid in cids]
            return summarize(arrays,fields)
        cells={};contrasts={}
        for c in CONDITIONS:
            for p in ['firm','agreeable']:cells[p+'/'+c]=estimate([(1,p,c)])
            contrasts['A_minus_F/'+c]=estimate([(1,'agreeable',c),(-1,'firm',c)])
        for support in ['baseline','paths']:
            contrasts['persona_x_retrieval/'+support]=estimate([(1,'agreeable','retrieval_'+support),
                (-1,'firm','retrieval_'+support),(-1,'agreeable','ready_'+support),(1,'firm','ready_'+support)])
        for p in ['firm','agreeable']:
            for state in ['ready','retrieval']:
                contrasts[p+'/paths_minus_baseline/'+state]=estimate([(1,p,state+'_paths'),(-1,p,state+'_baseline')])
            for support in ['baseline','paths']:
                contrasts[p+'/retrieval_minus_ready/'+support]=estimate([(1,p,'retrieval_'+support),(-1,p,'ready_'+support)])
        contrasts['persona_x_state_x_support']=estimate([(w,p,state+'_'+support)
            for support,ws in [('paths',1),('baseline',-1)]
            for state,wt in [('retrieval',1),('ready',-1)]
            for p,wp in [('agreeable',1),('firm',-1)] for w in [ws*wt*wp]])
        output[name]={'worlds':len(cids),'cells':cells,'contrasts':contrasts}
    result={'status':'COMPLETE','experiment':'E75','model':model,'worlds':102,'episodes':len(rows),
            'groups':output,'actual_calls':dict(calls),'native_validation':dict(validation),
            'physical_flag_mismatches':0,'shard_load_and_inference_gpu_hours':hours,'source_sha256':hashes,
            'scope':['Original authored retrieval states; ready produced by a native Get, original task/motivations unchanged.',
                     'All 102 native-eligible worlds and three seeds; four task types, wield N=0.',
                     'Path support is symmetric across source task/request but is not a pure hidden-knowledge intervention.',
                     'Unconditional joint outcomes; not a causal preference estimated among successful actors.',
                     'First bound authored event/source Give, not complete private utility or irreversible failure.']}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','episodes','actual_calls','native_validation']}))


if __name__=='__main__':main()
