"""E75 complete-only cross-source causal map; baseline reuse is fully verified."""
import argparse
import json
from pathlib import Path
import time
from data import sha
from joint_relation_use import MODELS
from analyze_correct_answer_carry import estimate


def analyze(root,parent,runs):
    data=root/'data-v1.jsonl';assert sha(data)==sha(parent/'data-v1.jsonl');rows=[dict(json.loads(x)) for x in data.read_text().splitlines()]
    for r in rows:r['sentence_sha256']=r['item_id']
    ids={r['item_id'] for r in rows};expected={(uid,order,t) for uid in ids for order in ['CUE_GP','GP_CUE'] for t in [0,1]};panels=[];provenance=[]
    for model in MODELS:
        records=[x for x in runs if x['model']==model];n=records[0]['shards'];assert {x['shard'] for x in records}==set(range(n));base=[];cut=[]
        for run in records:
            d=Path(run['out']);b=parent/'runs-v1'/model/str(run['shard']);cfg=json.loads((d/'config.json').read_text());bcfg=json.loads((b/'config.json').read_text())
            assert cfg['data_sha256']==bcfg['data_sha256']==sha(data)
            assert cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['parent_predictions_sha256']==bcfg['predictions_sha256']==sha(b/'predictions.jsonl')
            assert cfg['parent_config_sha256']==sha(b/'config.json') and cfg['model_manifest_sha256']==bcfg['model_manifest_sha256']
            part=list(map(json.loads,(d/'predictions.jsonl').read_text().splitlines()));bp=list(map(json.loads,(b/'predictions.jsonl').read_text().splitlines()));uids={r['item_id'] for r in rows if int(r['item_id'][:16],16)%n==run['shard']}
            assert len(part)==len(bp)==cfg['tasks']==bcfg['tasks']==4*len(uids) and {p['item_id'] for p in part}==uids;cut.extend(part);base.extend(bp)
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],predictions_sha256=cfg['predictions_sha256'],parent_predictions_sha256=cfg['parent_predictions_sha256'],config_sha256=sha(d/'config.json'),instrument=cfg['instrument']))
        native={(p['item_id'],p['order'],p['target']):p for p in base};index={(p['item_id'],p['order'],p['target']):p for p in cut}
        assert len(native)==len(base)==len(index)==len(cut)==len(expected) and set(native)==set(index)==expected
        for key,p in index.items():assert p['prompt_sha256']==native[key]['prompt_sha256']
        for r in rows:
            for order in ['CUE_GP','GP_CUE']:
                for t in [0,1]:
                    p=index[r['item_id'],order,t];g=0 if r['gold'][t]=='Yes' else 1;assert abs(sum(p['probabilities'])-1)<1e-6 and p['p_correct']==p['probabilities'][g]
                    assert p['correct']==float(max(range(2),key=p['candidate_logprobs'].__getitem__)==g)
        for construct in ['MVRR','NPZ','NPS','NPVP']:
            for pattern in ['all','Yes/Yes','Yes/No','No/Yes','No/No']:
                selected=[r for r in rows if r['construction']==construct and (pattern=='all' or '/'.join(r['gold'])==pattern)]
                for order in ['CUE_GP','GP_CUE']:
                    for target,t in [('initial',0),('final',1)]:
                        for metric in ['correct','p_correct']:
                            for operation in ['NATIVE','CUT_CROSS','CUT_CROSS-minus-NATIVE']:
                                if operation=='CUT_CROSS-minus-NATIVE':values=[index[r['item_id'],order,t][metric]-native[r['item_id'],order,t][metric] for r in selected]
                                else:values=[(native if operation=='NATIVE' else index)[r['item_id'],order,t][metric] for r in selected]
                                panels.append(dict(model=model,construction=construct,pattern=pattern,order=order,target=target,metric=metric,operation=operation,**estimate(selected,values,seed=75)))
    assert len(panels)==1440
    out=root/'cross-source-consumption-map-v1.json';assert not out.exists();out.write_text(json.dumps(dict(data_sha256=sha(data),panels=panels,runs=provenance,statistics='Paired lexical-cluster bootstrap10000 seed75; both source orders separate.',limits='Only second Source consumes first Source differently; Task reads both. Not latent parse oracle or spontaneous semantic correction.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E75 complete',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            path=Path(r['out'])/'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,a.parent,runs)
