"""E79 complete source versus correct-P1 consumption map, original E71 data."""
import argparse,json,time
from pathlib import Path
from data import sha
from joint_relation_use import MODELS
import collections
import numpy as np

def estimate(values,clusters):
    grouped=collections.defaultdict(list)
    for v,c in zip(values,clusters):grouped[c].append(float(v))
    x=np.array([np.mean(grouped[c]) for c in sorted(grouped)])
    if not len(x):return dict(value=None,CI95=None,clusters=0,sources=0)
    rng=np.random.default_rng(71);boot=x[rng.integers(len(x),size=(10000,len(x)))].mean(-1)
    return dict(value=float(x.mean()),CI95=list(map(float,np.quantile(boot,[.025,.975]))),clusters=len(x),sources=len(values))

OPS=['NATIVE','CUT_P1','CUT_SOURCE_LATE','CUT_P1-minus-NATIVE','CUT_SOURCE_LATE-minus-NATIVE','CUT_SOURCE_LATE-minus-CUT_P1']

def analyze(root,parent,runs):
    rows=list(map(json.loads,(root/'qualified-v1.jsonl').read_text().splitlines()));assert len(rows)==76 and sha(root/'qualified-v1.jsonl')==sha(parent/'qualified-v1.jsonl');ids={r['item_id'] for r in rows};ps=[];provenance=[]
    for model in MODELS:
        d=parent/'runs-v1'/model;bcfg=json.loads((d/'config.json').read_text());assert bcfg['predictions_sha256']==sha(d/'predictions.jsonl') and bcfg['data_sha256']==sha(root/'qualified-v1.jsonl')
        ix={(p['item_id'],p['operation']):p for p in map(json.loads,(d/'predictions.jsonl').read_text().splitlines())};assert set(ix)=={(uid,op) for uid in ids for op in ['NATIVE','CUT_P1']}
        rs=[r for r in runs if r['model']==model];n=rs[0]['shards'];assert {r['shard'] for r in rs}==set(range(n))
        for run in rs:
            d=Path(run['out']);cfg=json.loads((d/'config.json').read_text());assert cfg['data_sha256']==sha(root/'qualified-v1.jsonl') and cfg['model_manifest_sha256']==bcfg['model_manifest_sha256'] and cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['parent_predictions_sha256']==bcfg['predictions_sha256']
            sub=[r for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']];xs=list(map(json.loads,(d/'predictions.jsonl').read_text().splitlines()));assert cfg['tasks']==len(xs)==len(sub)
            for x in xs:
                key=x['item_id'],x['operation'];assert key not in ix and x['operation']=='CUT_SOURCE_LATE' and x['prompt_sha256']==ix[x['item_id'],'NATIVE']['prompt_sha256'];ix[key]=x
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],config_sha256=sha(d/'config.json'),predictions_sha256=cfg['predictions_sha256'],parent_predictions_sha256=cfg['parent_predictions_sha256'],instrument=cfg['instrument']))
        assert set(ix)=={(uid,op) for uid in ids for op in OPS[:3]}
        def value(r,metric,op):
            if '-minus-' in op:
                a,b=op.split('-minus-');return float(ix[r['item_id'],a][metric])-float(ix[r['item_id'],b][metric])
            return float(ix[r['item_id'],op][metric])
        for ct in ['MVRR','NPZ']:
            for cond in ['gp','cue']:
                selected=[r for r in rows if r['construction']==ct and r['condition']==cond]
                for metric in ['correct','p_correct','margin']:
                    for op in OPS:ps.append(dict(model=model,construction=ct,condition=cond,metric=metric,operation=op,**estimate([value(r,metric,op) for r in selected],[r['cluster_id'] for r in selected])))
            bypair={}
            for r in rows:
                if r['construction']==ct:bypair.setdefault(r['pair_id'],{})[r['condition']]=r
            for metric in ['correct','p_correct','margin']:
                vs=[];cs=[]
                for _,g in sorted(bypair.items()):assert set(g)=={'gp','cue'};vs.append(value(g['gp'],metric,'CUT_SOURCE_LATE-minus-NATIVE')-value(g['cue'],metric,'CUT_SOURCE_LATE-minus-NATIVE'));cs.append(g['gp']['cluster_id'])
                ps.append(dict(model=model,construction=ct,condition='gp-minus-cue',metric=metric,operation='interaction',**estimate(vs,cs)))
    assert len(ps)==234
    p=root/'source-versus-correct-prefix-map-v1.json';assert not p.exists();p.write_text(json.dumps(dict(data_sha256=sha(root/'qualified-v1.jsonl'),qualification_manifest=json.loads((root/'qualified-v1.manifest.json').read_text()),parent_map_sha256=sha(parent/'correct-prefix-binding-map-v1.json'),panels=ps,runs=provenance,statistics='lexical cluster means, paired bootstrap10000 seed71 as mother E71',limits='Correct P1 is forced, candidate whole-clause likelihood. Only later direct Source consumption cut; Source information may still flow through P1/Task. Not spontaneous correctness or latent parse proof.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,panels=len(ps),map_sha256=sha(p),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E79 complete',sha(p),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();rs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in rs:
            f=Path(r['out'])/'config.json';ready.append(f.exists() and 'predictions_sha256' in json.loads(f.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,a.parent,rs)
