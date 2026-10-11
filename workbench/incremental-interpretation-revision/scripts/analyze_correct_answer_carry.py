"""E73 complete-only, all truth patterns and both relation directions."""
import argparse
import collections
import json
from pathlib import Path
import time
import numpy as np
from data import sha
from joint_relation_use import MODELS


def estimate(rows, values, seed=73):
    sources=collections.defaultdict(list)
    for r,v in zip(rows,values):sources[r['cluster_id'],r['sentence_sha256']].append(float(v))
    clusters=collections.defaultdict(list)
    for (c,s),vs in sources.items():clusters[c].append(float(np.mean(vs)))
    x=np.array([np.mean(clusters[c]) for c in sorted(clusters)])
    if not len(x):return dict(value=None,CI95=None,clusters=0,sources=0)
    rng=np.random.default_rng(seed);boot=x[rng.integers(len(x),size=(10000,len(x)))].mean(-1)
    return dict(value=float(x.mean()),CI95=list(map(float,np.quantile(boot,[.025,.975]))),clusters=len(x),sources=len(sources))


def analyze(root,runs):
    data=root/'data-v1.jsonl';rows=[json.loads(x) for x in data.read_text().splitlines()]
    ids={r['item_id'] for r in rows};expected={(uid,op,order) for uid in ids for op in ['NATIVE','CUT_FIRST'] for order in [0,1]}
    panels=[];provenance=[]
    for model in MODELS:
        records=[x for x in runs if x['model']==model];n=records[0]['shards'];assert {x['shard'] for x in records}==set(range(n));pred=[]
        for run in records:
            directory=Path(run['out']);cfg=json.loads((directory/'config.json').read_text());path=directory/'predictions.jsonl'
            assert cfg['data_sha256']==sha(data) and cfg['predictions_sha256']==sha(path)
            part=[json.loads(x) for x in path.read_text().splitlines()]
            input_ids={r['item_id'] for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']}
            assert len(part)==cfg['tasks']==4*len(input_ids) and {x['item_id'] for x in part}==input_ids
            pred.extend(part);provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],config_sha256=sha(directory/'config.json'),predictions_sha256=sha(path),instrument=cfg['instrument']))
        index={(p['item_id'],p['operation'],p['order']):p for p in pred}
        assert len(index)==len(pred)==len(expected) and set(index)==expected
        for r in rows:
            for order in [0,1]:
                for op in ['NATIVE','CUT_FIRST']:
                    p=index[r['item_id'],op,order];assert p['first_gold']==r['gold'][order] and p['second_gold']==r['gold'][1-order]
                    gold=0 if r['gold'][1-order]=='Yes' else 1;probs=p['probabilities']
                    assert abs(sum(probs)-1)<1e-6 and p['p_correct']==probs[gold]
                    assert p['correct']==float(max(range(2),key=p['candidate_logprobs'].__getitem__)==gold)
        for construct in ['MVRR','NPZ','NPS','NPVP']:
            for target,order in [('initial',1),('final',0)]:
                for pattern in ['all','Yes/Yes','Yes/No','No/Yes','No/No']:
                    cell={}
                    for condition in ['gp','control']:
                        selected=[r for r in rows if r['construction']==construct and r['condition']==condition and (pattern=='all' or '/'.join(r['gold'])==pattern)]
                        for metric in ['correct','p_correct']:
                            delta=[index[r['item_id'],'CUT_FIRST',order][metric]-index[r['item_id'],'NATIVE',order][metric] for r in selected]
                            for operation in ['NATIVE','CUT_FIRST','CUT_FIRST-minus-NATIVE']:
                                values=delta if operation=='CUT_FIRST-minus-NATIVE' else [index[r['item_id'],operation,order][metric] for r in selected]
                                panels.append(dict(model=model,construction=construct,target=target,condition=condition,pattern=pattern,metric=metric,operation=operation,**estimate(selected,values)))
                            cell[condition,metric]=selected,delta
                    for metric in ['correct','p_correct']:
                        pairs=collections.defaultdict(dict)
                        for condition in ['gp','control']:
                            selected,values=cell[condition,metric]
                            for r,v in zip(selected,values):pairs[r['pair_id']][condition]=r,v
                        selected=[];values=[]
                        for pid,g in sorted(pairs.items()):
                            assert set(g)=={'gp','control'};selected.append(g['gp'][0]);values.append(g['gp'][1]-g['control'][1])
                        panels.append(dict(model=model,construction=construct,target=target,condition='gp-minus-cue',pattern=pattern,metric=metric,operation='interaction',**estimate(selected,values)))
    assert len(panels)==1680
    report=dict(data_sha256=sha(data),panels=panels,runs=provenance,statistics='Same-source then lexical cluster; paired bootstrap10000 seed73; both second-relation directions separate.',limits='Oracle correct first label; only direct consumption edges removed. Not spontaneous correction or full latent parse certification.')
    out=root/'correct-answer-carry-map-v1.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n')
    print('E73 complete',len(panels),sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args()
    runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            path=Path(r['out'])/'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,runs)
