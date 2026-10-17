#!/usr/bin/env python3
"""POST-HOC: E70 persona-by-state and persona-by-mechanics, all source worlds."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from native_request_precondition_report import metrics
from native_request_precondition_execution import SEEDS
from native_rule_cross_report import summarize


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    lookup={}; hashes={}
    for folder in args.runs:
        assert (folder/'runtime.json').exists()
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            k=r['case_id'],r['seed'],r['persona'],r['condition']; assert k not in lookup
            lookup[k]=metrics(r)
        hashes[str(folder/'episodes.jsonl')]=hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    cids=sorted({k[0] for k in lookup}); assert len(cids)==117 and len(lookup)==6318
    fields=['to_goal','to_competitor','to_other','no_transfer','source_remove','first_necessary_step']
    terms={}
    for d in ['aligned','divert']:
        terms['persona_x_state/'+d]=[(1,'agreeable','equipped_'+d),(-1,'firm','equipped_'+d),
                                    (-1,'agreeable','ready_'+d),(1,'firm','ready_'+d)]
        terms['persona_x_mechanics/'+d]=[(1,'agreeable','equipped_'+d+'_mechanics'),(-1,'firm','equipped_'+d+'_mechanics'),
                                        (-1,'agreeable','equipped_'+d),(1,'firm','equipped_'+d)]
    contrasts={}; graph_values={}
    for name,tt in terms.items():
        matrix=[np.mean([[sum(w*lookup[cid,s,p,c][f] for w,p,c in tt) for f in fields] for s in SEEDS],axis=0) for cid in cids]
        contrasts[name]=summarize(matrix,fields)
        graph_values[name]={cid:dict(zip(fields,map(float,v))) for cid,v in zip(cids,matrix)}
    result={'status':'COMPLETE','experiment':'E70','analysis':'POST-HOC interactions after full E70 readout; all four contrasts retained',
            'worlds':117,'episodes':6318,'contrasts':contrasts,'graph_values':graph_values,'source_sha256':hashes,
            'scope':['These linear contrasts supplement rather than replace registered first-recipient outcomes.',
                     'State changes native stats, observation/menu and generated conversation; not pure extra-step cognition.',
                     'Mechanics text also supplies action anchors and changes upstream conversation; not isolated knowledge mediation.',
                     'Paired three-seed graph means; 4000 graph bootstrap samples, pointwise 95% intervals.']}
    args.out.write_text(json.dumps(result,indent=2)+'\n');print({k:v['to_goal'] for k,v in contrasts.items()})


if __name__=='__main__':main()
