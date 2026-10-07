"""E71 complete-only qualification, three offline runs and paired whole map."""
import argparse
import collections
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from data import CACHE,sha


def estimate(values,clusters):
    grouped=collections.defaultdict(list)
    for v,c in zip(values,clusters):grouped[c].append(float(v))
    x=np.array([np.mean(grouped[c]) for c in sorted(grouped)])
    if not len(x):return dict(value=None,CI95=None,clusters=0,sources=0)
    rng=np.random.default_rng(71);boot=x[rng.integers(len(x),size=(10000,len(x)))].mean(-1)
    return dict(value=float(x.mean()),CI95=list(map(float,np.quantile(boot,[.025,.975]))),clusters=len(x),sources=len(values))


def analyze(root):
    rows=[json.loads(x) for x in (root/'qualified-v1.jsonl').read_text().splitlines()];ids={r['item_id'] for r in rows};panels=[];runs=[]
    for name in ['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']:
        run=root/'runs-v1'/name;cfg=json.loads((run/'config.json').read_text());assert cfg['data_sha256']==sha(root/'qualified-v1.jsonl')
        assert cfg['predictions_sha256']==sha(run/'predictions.jsonl');data=[json.loads(x) for x in (run/'predictions.jsonl').read_text().splitlines()]
        index={(r['item_id'],r['operation']):r for r in data};assert len(index)==len(data)==2*len(ids)
        assert set(index)=={(uid,op) for uid in ids for op in ['NATIVE','CUT_P1']}
        runs.append(dict(model=name,config_sha256=sha(run/'config.json'),predictions_sha256=sha(run/'predictions.jsonl'),gpu_hours=cfg['gpu_hours']))
        for c in ['MVRR','NPZ']:
            for condition in ['gp','cue']:
                selected=[r for r in rows if r['construction']==c and r['condition']==condition]
                for metric in ['correct','p_correct','margin']:
                    for op in ['NATIVE','CUT_P1','CUT-minus-NATIVE']:
                        values=[]
                        for r in selected:
                            a=index[(r['item_id'],'NATIVE')][metric];b=index[(r['item_id'],'CUT_P1')][metric]
                            values.append(float(a) if op=='NATIVE' else float(b) if op=='CUT_P1' else float(b)-float(a))
                        panels.append(dict(model=name,construction=c,condition=condition,metric=metric,operation=op,**estimate(values,[r['cluster_id'] for r in selected])))
            bypair=collections.defaultdict(dict)
            for r in rows:
                if r['construction']==c:bypair[r['pair_id']][r['condition']]=r
            for metric in ['correct','p_correct','margin']:
                values=[];clusters=[]
                for pair,g in sorted(bypair.items()):
                    assert set(g)=={'gp','cue'};d={}
                    for cond,r in g.items():d[cond]=float(index[(r['item_id'],'CUT_P1')][metric])-float(index[(r['item_id'],'NATIVE')][metric])
                    values.append(d['gp']-d['cue']);clusters.append(g['gp']['cluster_id'])
                panels.append(dict(model=name,construction=c,condition='gp-minus-cue',metric=metric,operation='interaction',**estimate(values,clusters)))
    out=root/'correct-prefix-binding-map-v1.json';assert not out.exists()
    result=dict(data_sha256=sha(root/'qualified-v1.jsonl'),qualification_manifest=json.loads((root/'qualified-v1.manifest.json').read_text()),
        runs=runs,panels=panels,statistics='cluster means, 10000 paired lexical cluster bootstrap, seed71',
        limits='Forced correct assistant prefill, paired full-candidate likelihood; not spontaneous correctness or latent parse/ability proof.')
    out.write_text(json.dumps(result,indent=2)+'\n');(root/'complete-map-v1.json').write_text(json.dumps(dict(map_sha256=sha(out),all_models_complete=True,panels=len(panels)),indent=2)+'\n')
    print('E71 complete whole map',len(panels),sha(out),flush=True)


def main(root):
    scripts=Path(__file__).parent.resolve();summary=root/'step5/summary.json'
    while not summary.exists():time.sleep(20)
    if not (root/'qualified-v1.jsonl').exists():subprocess.run([sys.executable,str(scripts/'run_correct_prefix_binding.py'),'freeze','--root',str(root)],check=True)
    manifest=json.loads((root/'qualified-v1.manifest.json').read_text());assert manifest['sources']>0
    ps=[]
    for gpu,name in enumerate(['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']):
        out=root/'runs-v1'/name
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
        for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:env.pop(key,None)
        with (root/('run-v1-'+name+'.log')).open('w') as f:
            p=subprocess.Popen([sys.executable,'-u',str(scripts/'run_correct_prefix_binding.py'),'run','--data',str(root/'qualified-v1.jsonl'),'--model',str(CACHE/'models'/name),'--out',str(out),'--gpu',str(gpu)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        ps.append(p)
    (root/'runner-pids-v1.json').write_text(json.dumps([dict(pid=p.pid,gpu=i) for i,p in enumerate(ps)])+'\n')
    for p in ps:assert p.wait()==0,'E71 run failed; preserve before retry'
    analyze(root)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--analyze-only',action='store_true');a=p.parse_args()
    if a.analyze_only:analyze(a.root)
    else:main(a.root)
