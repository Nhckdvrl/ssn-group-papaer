#!/usr/bin/env python3
"""E73 equal initial engine information versus fixed-dialogue E72 interfaces."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_request_precondition_report import metrics
from native_request_precondition_execution import SEEDS
from native_rule_cross_report import summarize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--candidate-runs',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    lookup={};hashes={};calls=Counter();manifest=json.loads((args.run/'manifest.json').read_text())
    runtime=json.loads((args.run/'runtime.json').read_text())
    for folder in [args.run]+args.candidate_runs:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model']==manifest['model']
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            k=r['case_id'],r['seed'],r['persona'],r['condition'];assert k not in lookup;lookup[k]=r
        hashes[str(folder/'episodes.jsonl')]=hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    cids=sorted({k[0] for k in lookup});assert len(cids)==117 and len(lookup)==4212
    for cid in cids:
        for s in SEEDS:
            for p in ['firm','agreeable']:
                for d in ['aligned','divert']:
                    a=lookup[cid,s,p,d+'_initial_feedback']
                    for arm in ['valid_candidates','goal_candidates']:
                        assert a['conversation']==lookup[cid,s,p,d+'_'+arm]['conversation']
    values={k:metrics(r) for k,r in lookup.items()};fields=list(next(iter(values.values())))
    def estimate(tt):
        return summarize([np.mean([[sum(w*values[cid,s,p,c][f] for w,p,c in tt) for f in fields]
                                   for s in SEEDS],axis=0) for cid in cids],fields)
    cells={};contrasts={}
    for d in ['aligned','divert']:
        for arm in ['initial_feedback','valid_candidates','goal_candidates']:
            c=d+'_'+arm
            for p in ['firm','agreeable']:cells[p+'/'+c]=estimate([(1,p,c)])
            contrasts['A_minus_F/'+c]=estimate([(1,'agreeable',c),(-1,'firm',c)])
        for p in ['firm','agreeable']:
            for arm in ['valid_candidates','goal_candidates']:
                contrasts[p+'/initial_feedback_minus_'+arm+'/'+d]=estimate([(1,p,d+'_initial_feedback'),(-1,p,d+'_'+arm)])
        contrasts['persona_x_initial_feedback/'+d]=estimate([(1,'agreeable',d+'_initial_feedback'),(-1,'firm',d+'_initial_feedback'),
                                                            (-1,'agreeable',d+'_valid_candidates'),(1,'firm',d+'_valid_candidates')])
    for c in map(json.loads,(args.run/'model_calls.jsonl').open()):
        assert c['stage']=='exec'
        calls.update(count=1,parse_errors=int(bool(c['parse_error'])),prompt_tokens=c['prompt_tokens'],completion_tokens=c['completion_tokens'])
    assert calls['count']==runtime['calls']
    result={'status':'COMPLETE','experiment':'E73','model':manifest['model'],'worlds':117,'new_episodes':1404,
            'total_compared_episodes':4212,'cells':cells,'contrasts':contrasts,'actual_calls':dict(calls),
            'runtime_gpu_hours':(runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
            'runtime':runtime,'source_sha256':hashes,
            'scope':['Same dialogue, native menu, neutral directive and eight chosen-action slots as E72 native-menu arm; added genuine initial-state mechanics information.',
                     'The engine check is not an executed NPC action and changes no physical state; no scripted remove/give.',
                     'Information exposure is equal, not proof of equal internal beliefs; salience/message position remain possible mechanisms.',
                     'Expanded-candidate comparison additionally differs in candidate set and endogenous error timing/budget.',
                     'First exact-source-item Give, not full private utility; three-seed graph means and 4000 bootstrap samples.']}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','new_episodes','actual_calls','runtime_gpu_hours']}),flush=True)


if __name__=='__main__':main()
