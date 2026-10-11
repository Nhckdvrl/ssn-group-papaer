"""E74 complete map, with verified E72 single-source baseline reuse."""
import argparse
import json
from pathlib import Path
import time
from data import sha
from joint_relation_use import MODELS
from analyze_correct_answer_carry import estimate


def analyze(root,parent,runs):
    data=root/'data-v1.jsonl';rows=[dict(json.loads(x)) for x in data.read_text().splitlines()]
    for r in rows:r['sentence_sha256']=r['item_id']
    assert json.loads(data.with_suffix('.manifest.json').read_text())['parent_sha256']==sha(parent/'data-v1.jsonl')
    baseline_runs=json.loads((parent/'runner-pids-v1.json').read_text());panels=[];provenance=[];base_provenance=[]
    for model in MODELS:
        base={}
        for run in [x for x in baseline_runs if x['model']==model]:
            d=Path(run['out']);cfg=json.loads((d/'config.json').read_text());assert cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['data_sha256']==sha(parent/'data-v1.jsonl')
            base_provenance.append(dict(model=model,shard=run['shard'],config_sha256=sha(d/'config.json'),predictions_sha256=cfg['predictions_sha256']))
            for p in map(json.loads,(d/'predictions.jsonl').read_text().splitlines()):
                if p['operation']=='SEPARATE':base[p['item_id'],p['order']]=p
        records=[x for x in runs if x['model']==model];n=records[0]['shards'];assert {x['shard'] for x in records}==set(range(n));pred=[]
        for run in records:
            d=Path(run['out']);cfg=json.loads((d/'config.json').read_text());assert cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['data_sha256']==sha(data)
            part=list(map(json.loads,(d/'predictions.jsonl').read_text().splitlines()));uids={r['item_id'] for r in rows if int(r['item_id'][:16],16)%n==run['shard']}
            assert len(part)==cfg['tasks']==4*len(uids) and {p['item_id'] for p in part}==uids;pred.extend(part)
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],config_sha256=sha(d/'config.json'),predictions_sha256=cfg['predictions_sha256'],native_LP_max_delta=cfg['native_LP_max_delta']))
        index={(p['item_id'],p['order'],p['target']):p for p in pred};expected={(r['item_id'],op,t) for r in rows for op in ['GP_CUE','CUE_GP'] for t in [0,1]};assert len(index)==len(pred)==len(expected) and set(index)==expected
        outcomes={}
        for r in rows:
            for context,condition in [('GP','gp'),('CUE','control')]:
                for t in [0,1]:
                    p=base[r['parent_item_ids'][condition],t];g=0 if r['gold'][t]=='Yes' else 1;v=p['probabilities'];assert len(v)==2 and abs(sum(v)-1)<1e-6
                    outcomes[r['item_id'],context,t]=dict(correct=float(max(range(2),key=p['candidate_logprobs'].__getitem__)==g),p_correct=v[g])
            for context in ['GP_CUE','CUE_GP']:
                for t in [0,1]:
                    p=index[r['item_id'],context,t];g=0 if r['gold'][t]=='Yes' else 1;v=p['probabilities'];assert abs(sum(v)-1)<1e-6 and p['p_correct']==v[g]
                    assert p['correct']==float(max(range(2),key=p['candidate_logprobs'].__getitem__)==g)
                    outcomes[r['item_id'],context,t]=p
        for construct in ['MVRR','NPZ','NPS','NPVP']:
            for pattern in ['all','Yes/Yes','Yes/No','No/Yes','No/No']:
                selected=[r for r in rows if r['construction']==construct and (pattern=='all' or '/'.join(r['gold'])==pattern)]
                for target,t in [('initial',0),('final',1)]:
                    for metric in ['correct','p_correct']:
                        for operation in ['GP','CUE','GP_CUE','CUE_GP','CUE_GP-minus-CUE','GP_CUE-minus-CUE','CUE_GP-minus-GP_CUE']:
                            if '-minus-' in operation:
                                a,b=operation.split('-minus-');values=[outcomes[r['item_id'],a,t][metric]-outcomes[r['item_id'],b,t][metric] for r in selected]
                            else:values=[outcomes[r['item_id'],operation,t][metric] for r in selected]
                            panels.append(dict(model=model,construction=construct,pattern=pattern,target=target,metric=metric,operation=operation,**estimate(selected,values,seed=74)))
    assert len(panels)==1680
    out=root/'cue-interpretation-retention-map-v1.json';assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data),panels=panels,runs=provenance,baseline_runs=base_provenance,statistics='Lexical cluster paired bootstrap10000 seed74.',limits='Original paired versions, source-support QA. Joint context not latent parse certification; order effect may be general recency.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E74 complete',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            d=Path(r['out'])/'config.json';ready.append(d.exists() and 'predictions_sha256' in json.loads(d.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,a.parent,runs)
