"""E78 all strong-model families and original-gold QA conditions, complete-only."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from stronger_draft_pipeline import MODELS
from analyze_correct_answer_carry import estimate

OPS=['DIRECT','SOURCE_AND_DRAFT','DRAFT_ONLY','SOURCE_AND_DRAFT-minus-DIRECT','DRAFT_ONLY-minus-DIRECT','DRAFT_ONLY-minus-SOURCE_AND_DRAFT']


def analyze(root,runs):
    rows=list(map(json.loads,(root/'data-v1.jsonl').read_text().splitlines()));assert len(rows)==892
    assert sha(root/'data-v1.jsonl')==json.loads((root/'data-v1.manifest.json').read_text())['data_sha256']
    for r in rows:r['cluster_id']=r['analysis_cluster_id']
    expected={(r['item_id'],op,ro,mp) for r in rows for op in OPS[:3] for ro in ['words','letters'] for mp in [0,1]};panels=[];provenance=[];lengths=[];noise=[]
    for model in MODELS:
        records=[r for r in runs if r['model']==model];n=records[0]['shards'];assert {r['shard'] for r in records}==set(range(n));index={};drafts={}
        for run in records:
            p=Path(run['out']);cfg=json.loads((p/'config.json').read_text());assert cfg['data_sha256']==sha(root/'data-v1.jsonl') and cfg['predictions_sha256']==sha(p/'predictions.jsonl') and cfg['drafts_sha256']==sha(p/'drafts.jsonl')
            sub=[r for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']];cs=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()));gs=list(map(json.loads,(p/'drafts.jsonl').read_text().splitlines()));assert len(cs)==cfg['tasks']==12*len(sub) and len(gs)==cfg['sources']==len({r['source_unit'] for r in sub})
            for x in cs:
                key=x['item_id'],x['operation'],x['readout'],x['mapping'];assert key not in index;index[key]=x
            for x in gs:assert x['source_unit'] not in drafts;drafts[x['source_unit']]=x
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],draft_gpu_hours=cfg['draft_gpu_hours'],model_manifest_sha256=cfg['model_manifest_sha256'],config_sha256=sha(p/'config.json'),predictions_sha256=cfg['predictions_sha256'],drafts_sha256=cfg['drafts_sha256'],repeat_LP_max_delta=max(c['repeat_LP_max_delta'] for c in cfg['instrument'])))
        assert set(index)==expected and set(drafts)=={r['source_unit'] for r in rows}
        for r in rows:
            for op in OPS[:3]:
                for ro in ['words','letters']:
                    for mp,shown in enumerate([['Yes','No'],['No','Yes']]):assert index[r['item_id'],op,ro,mp]['candidate_gold']==shown.index(r['grounded_gold'])
        def atom(r,op,ro,metric):
            def v(k):return sum(float(index[r['item_id'],k,ro,mp][metric]) for mp in [0,1])/2
            if '-minus-' in op:
                a,b=op.split('-minus-');return v(a)-v(b)
            return v(op)
        sources={r['source_unit']:r for r in rows}
        for ct in ['MVRR','NPZ','NPS','NPVP']:
            for cond in ['gp','control']:
                ls=[drafts[uid] for uid,r in sources.items() if r['construction']==ct and r['condition']==cond];ts=[len(g['generated_token_ids']) for g in ls]
                lengths.append(dict(model=model,construction=ct,condition=cond,sources=len(ls),mean_tokens=sum(ts)/len(ts),max_tokens=max(ts),cap_rate=sum(g['capped'] for g in ls)/len(ls)))
                for ro in ['words','letters']:
                    for target in ['initial','final','all']:
                        selected=[r for r in rows if r['construction']==ct and r['condition']==cond and (target=='all' or r['analysis_question_target']==target)]
                        for met in ['correct','p_correct']:
                            for op in OPS:panels.append(dict(model=model,construction=ct,condition=cond,readout=ro,target=target,metric=met,operation=op,**estimate(selected,[atom(r,op,ro,met) for r in selected],seed=78)))
                    selected=[r for r in rows if r['construction']==ct and r['condition']==cond];group=collections.defaultdict(list)
                    for r in selected:group[r['source_unit']].append(r)
                    reps=[g[0] for _,g in sorted(group.items())];joint={}
                    for uid,g in group.items():
                        for op in OPS[:3]:joint[uid,op]=sum(all(index[r['item_id'],op,ro,mp]['correct'] for r in g) for mp in [0,1])/2
                    for op in OPS:
                        vs=[]
                        for r in reps:
                            uid=r['source_unit']
                            if '-minus-' in op:a,b=op.split('-minus-');vs.append(joint[uid,a]-joint[uid,b])
                            else:vs.append(joint[uid,op])
                        panels.append(dict(model=model,construction=ct,condition=cond,readout=ro,target='joint_all_questions',metric='correct',operation=op,**estimate(reps,vs,seed=78)))
                    for op in OPS[:3]:noise.append(dict(model=model,construction=ct,condition=cond,readout=ro,operation=op,mean_QA_correct_flip=sum(abs(index[r['item_id'],op,ro,0]['correct']-index[r['item_id'],op,ro,1]['correct']) for r in selected)/len(selected)))
    assert len(panels)==2016
    out=root/'stronger-draft-map-v1.json';assert not out.exists();out.write_text(json.dumps(dict(data_sha256=sha(root/'data-v1.jsonl'),panels=panels,runs=provenance,draft_lengths=lengths,mapping_noise=noise,statistics='Mean mappings per QA; mean QA per Source; lexical cluster paired bootstrap10000 seed78. Joint all originalQA per mapping then Source.',limits='Strong-model BF16 panel separately from smaller FP32. Original source gold evaluates complete S-to-draft-to-QA pipeline. Draft roles unjudged; different texts are not a pure neural source-competition intervention.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E78 complete',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            path=Path(r['out'])/'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,runs)
