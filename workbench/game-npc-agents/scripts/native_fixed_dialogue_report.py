#!/usr/bin/env python3
"""E76 fixed-dialogue physical-access contrasts, against exact E75 references."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_retrieval_report import metrics,validate
from native_retrieval_execution import SEEDS
from native_rule_cross_report import summarize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--references',type=Path,nargs='+',required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert (a.run/'runtime.json').exists()
    source={r['case']['case_id']:r for r in map(json.loads,a.data.open())};rows={};hashes={};checks=Counter()
    model=json.loads((a.run/'manifest.json').read_text())['model']
    for folder in a.references+[a.run]:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model']==model
        path=folder/'episodes.jsonl';hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        for r in map(json.loads,path.open()):
            if r['condition'] not in ['ready_baseline','retrieval_baseline','ready_frozen_dialogue']:continue
            key=r['case_id'],r['seed'],r['persona'],r['condition'];assert key not in rows;rows[key]=r
            if folder==a.run:checks.update(validate(r,source[r['case_id']]))
    assert len(source)==102 and len(rows)==1836
    identical=0
    for cid in source:
        for seed in SEEDS:
            for p in ['firm','agreeable']:
                new=rows[cid,seed,p,'ready_frozen_dialogue'];ret=rows[cid,seed,p,'retrieval_baseline'];ready=rows[cid,seed,p,'ready_baseline']
                assert new['conversation']==ret['conversation']
                assert new['native_goal_identity']==ret['native_goal_identity']==ready['native_goal_identity']
                if new['conversation']==ready['conversation']:
                    identical+=1;assert new['history']==ready['history']
    values={k:metrics(r) for k,r in rows.items()};fields=list(next(iter(values.values())))
    groups={'all':list(source),'source_give':[c for c,r in source.items() if r['case']['goal_kind']=='give'],
            'source_use':[c for c,r in source.items() if r['case']['goal_kind']!='give']}
    groups.update({'kind_'+k:[c for c,r in source.items() if r['case']['goal_kind']==k] for k in ['wear','eat','drink']})
    output={}
    for name,cids in groups.items():
        def estimate(terms):
            array=[np.mean([[sum(w*values[cid,s,p,c][f] for w,p,c in terms) for f in fields]
                            for s in SEEDS],axis=0) for cid in cids]
            return summarize(array,fields)
        cells={};contrasts={}
        for c in ['ready_baseline','retrieval_baseline','ready_frozen_dialogue']:
            for p in ['firm','agreeable']:cells[p+'/'+c]=estimate([(1,p,c)])
            contrasts['A_minus_F/'+c]=estimate([(1,'agreeable',c),(-1,'firm',c)])
        for p in ['firm','agreeable']:
            contrasts[p+'/access_at_fixed_dialogue']=estimate([(1,p,'ready_frozen_dialogue'),(-1,p,'retrieval_baseline')])
            contrasts[p+'/dialogue_source_at_fixed_ready']=estimate([(1,p,'ready_frozen_dialogue'),(-1,p,'ready_baseline')])
        contrasts['persona_x_access_at_fixed_dialogue']=estimate([(1,'agreeable','ready_frozen_dialogue'),
            (-1,'firm','ready_frozen_dialogue'),(-1,'agreeable','retrieval_baseline'),(1,'firm','retrieval_baseline')])
        contrasts['persona_x_dialogue_source_at_fixed_ready']=estimate([(1,'agreeable','ready_frozen_dialogue'),
            (-1,'firm','ready_frozen_dialogue'),(-1,'agreeable','ready_baseline'),(1,'firm','ready_baseline')])
        output[name]={'worlds':len(cids),'cells':cells,'contrasts':contrasts}
    calls=Counter()
    for r in map(json.loads,(a.run/'model_calls.jsonl').open()):
        calls.update(calls=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],
                     completion_tokens=r['completion_tokens']);assert r['stage']=='exec'
    result={'status':'COMPLETE','experiment':'E76','model':model,'worlds':102,'new_branches':612,
            'groups':output,'actual_full_run_calls':dict(calls),'native_validation':dict(checks),
            'exact_source_conversations_reused':612,'identical_ready_dialogue_and_action_paths':identical,
            'physical_flag_mismatches':0,'source_sha256':hashes,
            'scope':['One additional factorial cell; no complete orthogonal mediation decomposition.',
                     'Previous dialogue and current physical state differ by an explicit initial-state intervention.',
                     'Same original goal/motivations and full persona throughout; no new prompt footer, table or scripted NPC action.',
                     'Physical access changes custody, menu and required action count; not pure abstract effort.',
                     'Reference paths and exact duplicates reused, not new independent samples.']}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','new_branches','actual_full_run_calls','native_validation','identical_ready_dialogue_and_action_paths']}))


if __name__=='__main__':main()
