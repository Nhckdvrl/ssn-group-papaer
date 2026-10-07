"""E77 all conditions, original-gold end-to-end map; complete-only."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from joint_relation_use import MODELS
from analyze_correct_answer_carry import estimate

OPS=['NATIVE','CUT_SOURCE','CUT-minus-NATIVE','CUT-minus-DIRECT']


def analyze(root,parent,direct,runs):
    rows=list(map(json.loads,(root/'data-v1.jsonl').read_text().splitlines()));assert len(rows)==892 and sha(root/'data-v1.jsonl')==sha(parent/'data-v1.jsonl')==sha(direct/'data-v1.jsonl')
    for r in rows:r['cluster_id']=r['analysis_cluster_id']
    expected={(r['item_id'],draft,ro,mp) for r in rows for draft in ['FREE','EVENT_FIRST'] for ro in ['words','letters'] for mp in [0,1]}
    ps=[];provenance=[];noise=[]
    for model in MODELS:
        records=[x for x in runs if x['model']==model];n=records[0]['shards'];assert {x['shard'] for x in records}==set(range(n));cut={};native={}
        basepath=direct/'runs-v1'/model;bcfg=json.loads((basepath/'config.json').read_text());assert bcfg['predictions_sha256']==sha(basepath/'predictions.jsonl')
        baseline={(p['item_id'],p['readout'],p['mapping']):p for p in map(json.loads,(basepath/'predictions.jsonl').read_text().splitlines()) if p['operation']=='NONE'};assert len(baseline)==4*len(rows)
        for run in records:
            d=Path(run['out']);cfg=json.loads((d/'config.json').read_text());old=parent/'runs-v1'/model/str(run['shard']);oldcfg=json.loads((old/'config.json').read_text())
            assert cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['parent_predictions_sha256']==sha(old/'predictions.jsonl') and cfg['model_manifest_sha256']==bcfg['model_manifest_sha256']
            assert cfg['data_sha256']==sha(root/'data-v1.jsonl') and cfg['parent_drafts_sha256']==sha(old/'drafts.jsonl')
            subset=[r for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']];assert cfg['tasks']==8*len(subset)
            cs=list(map(json.loads,(d/'predictions.jsonl').read_text().splitlines()));ns=list(map(json.loads,(old/'predictions.jsonl').read_text().splitlines()));assert len(cs)==len(ns)==cfg['tasks']
            for p in cs:
                key=p['item_id'],p['draft'],p['readout'],p['mapping'];assert key not in cut and p['operation']=='CUT_SOURCE';cut[key]=p
            for p in ns:
                key=p['item_id'],p['operation'],p['readout'],p['mapping'];assert key not in native;native[key]=p
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],config_sha256=sha(d/'config.json'),predictions_sha256=cfg['predictions_sha256'],parent_predictions_sha256=cfg['parent_predictions_sha256'],instrument=cfg['instrument']))
        assert set(cut)==set(native)==expected
        for key,p in cut.items():assert p['prompt_sha256']==native[key]['prompt_sha256'] and p['candidate_gold']==native[key]['candidate_gold']
        def atom(r,draft,ro,mp,operation,metric):
            key=r['item_id'],draft,ro,mp
            a=float(cut[key][metric]);b=float(native[key][metric]);c=float(baseline[r['item_id'],ro,mp][metric])
            return dict(NATIVE=b,CUT_SOURCE=a,**{'CUT-minus-NATIVE':a-b,'CUT-minus-DIRECT':a-c})[operation]
        for construction in ['MVRR','NPZ','NPS','NPVP']:
            for condition in ['gp','control']:
                for readout in ['words','letters']:
                    for draft in ['FREE','EVENT_FIRST']:
                        for target in ['initial','final','all']:
                            selected=[r for r in rows if r['construction']==construction and r['condition']==condition and (target=='all' or r['analysis_question_target']==target)]
                            for metric in ['correct','p_correct']:
                                for op in OPS:
                                    vs=[sum(atom(r,draft,readout,mp,op,metric) for mp in [0,1])/2 for r in selected]
                                    ps.append(dict(model=model,construction=construction,condition=condition,readout=readout,draft=draft,target=target,metric=metric,operation=op,**estimate(selected,vs,seed=77)))
                        selected=[r for r in rows if r['construction']==construction and r['condition']==condition];grouped=collections.defaultdict(list)
                        for r in selected:grouped[r['source_unit']].append(r)
                        reps=[g[0] for _,g in sorted(grouped.items())];joint={}
                        for uid,g in grouped.items():
                            for op,ix in [('NATIVE',native),('CUT_SOURCE',cut)]:joint[uid,op]=sum(all(ix[r['item_id'],draft,readout,mp]['correct'] for r in g) for mp in [0,1])/2
                            joint[uid,'DIRECT']=sum(all(baseline[r['item_id'],readout,mp]['correct'] for r in g) for mp in [0,1])/2
                        for op in OPS:
                            vs=[]
                            for r in reps:
                                uid=r['source_unit'];vs.append(joint[uid,op] if op in ['NATIVE','CUT_SOURCE'] else joint[uid,'CUT_SOURCE']-joint[uid,'NATIVE' if op=='CUT-minus-NATIVE' else 'DIRECT'])
                            ps.append(dict(model=model,construction=construction,condition=condition,readout=readout,draft=draft,target='joint_all_questions',metric='correct',operation=op,**estimate(reps,vs,seed=77)))
                        for op,ix in [('NATIVE',native),('CUT_SOURCE',cut)]:
                            noise.append(dict(model=model,construction=construction,condition=condition,readout=readout,draft=draft,operation=op,mean_QA_correct_flip=sum(abs(ix[r['item_id'],draft,readout,0]['correct']-ix[r['item_id'],draft,readout,1]['correct']) for r in selected)/len(selected)))
    assert len(ps)==2688
    p=root/'retire-original-map-v1.json';assert not p.exists();p.write_text(json.dumps(dict(data_sha256=sha(root/'data-v1.jsonl'),parent_map_sha256=sha(parent/'event-first-draft-map-v1.json'),panels=ps,runs=provenance,mapping_noise=noise,statistics='Mappings averaged per QA, QA mean per Source, lexical cluster paired bootstrap10000 seed77; joint all originalQ per mapping then Source.',limits='Source consumption cut with unchanged text/notes/QA; original source gold evaluates complete pipeline. Draft roles unjudged; not a deployment method or native ability proof.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,panels=len(ps),map_sha256=sha(p),gpu_hours=sum(r['gpu_hours'] for r in provenance)),indent=2)+'\n');print('E77 complete',sha(p),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--direct',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            path=Path(r['out'])/'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,a.parent,a.direct,runs)
