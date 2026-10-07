"""E89 complete-only frame timing; actual answers and unresolved bounds."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS
from analyze_actual_answer import semantic_label
from analyze_correct_answer_carry import estimate

OPS=['NATIVE','RECOVER','EARLY_FRAME','LATE_FRAME','EARLY_FRAME-minus-LATE_FRAME',
     'EARLY_FRAME-minus-NATIVE','LATE_FRAME-minus-NATIVE','EARLY_FRAME-minus-RECOVER','LATE_FRAME-minus-RECOVER']


def analyze(root):
    rows=list(map(json.loads,(root/'data-v1.jsonl').read_text().splitlines()))
    meta={r['item_id']:dict(r,cluster_id=r['analysis_cluster_id']) for r in rows}
    gps={r['source_unit']:r for r in rows if r['condition']=='gp'}
    def frame(r):
        gp=gps[r['frame_locator']['GP_source_unit']]
        if r['construction']=='NPZ':return 'NPZ_author_alternation' if gp['source']=='cehakova2025' else ('NPZ_reflexive' if 'reflexive' in (gp.get('source_sent_type') or '') else 'NPZ_other')
        if r['construction']=='MVRR':return 'MVRR_dative' if gp['source']=='cehakova2025' else 'MVRR_other'
        return 'NPS_complement'
    runs=json.loads((root/'runner-pids-v1.json').read_text());panels=[];joint=[];coverage=[];provenance=[];noise=[];counts=[]
    for model in MODELS:
        index={}
        for run in json.loads((root.parent/'E87/runner-pids-v1.json').read_text()):
            if run['model']!=model:continue
            out=Path(run['out']);cfg=json.loads((out/'config.json').read_text());assert sha(out/'predictions.jsonl')==cfg['predictions_sha256']
            for p in map(json.loads,(out/'predictions.jsonl').read_text().splitlines()):
                if p['item_id'] not in meta or p['operation'] not in ['QA_STRICT','QA_RECOVER']:continue
                p['label'],p['semantic_parse_status']=semantic_label(p['output_text'],p['mapping'])
                p['lower_correct']=bool(p['stopped'] and p['label']==p['grounded_gold'])
                p['upper_correct']=bool(p['label'] is None or not p['stopped'] or p['label']==p['grounded_gold'])
                p['valid']=p['label'] is not None
                op='NATIVE' if p['operation']=='QA_STRICT' else 'RECOVER';key=p['item_id'],p['mapping'],op
                assert key not in index;index[key]=p
        selected=[r for r in runs if r['model']==model];n=selected[0]['shards'];assert {r['shard'] for r in selected}==set(range(n))
        for run in selected:
            out=Path(run['out']);cfg=json.loads((out/'config.json').read_text())
            assert sha(out/'predictions.jsonl')==cfg['predictions_sha256'] and cfg['data_sha256']==sha(root/'data-v1.jsonl')
            assert cfg['model_manifest_sha256']==sha(root.parent/'models'/model/'manifest.json')
            ps=list(map(json.loads,(out/'predictions.jsonl').read_text().splitlines()));assert len(ps)==cfg['tasks']
            for p in ps:
                r=meta[p['item_id']];key=p['item_id'],p['mapping'],p['operation'];assert key not in index
                assert int(r['frame_locator']['GP_source_unit'].split(':')[-1][:16],16)%n==run['shard']
                old=index[p['item_id'],p['mapping'],'NATIVE'];assert old['prompt_sha256']==p['native_prompt_sha256']
                assert old['grounded_gold']==p['grounded_gold']==r['grounded_gold'];index[key]=p
            provenance.append(dict(model=model,shard=run['shard'],predictions_sha256=cfg['predictions_sha256'],config_sha256=sha(out/'config.json'),
                gpu_hours=cfg['gpu_hours'],code_sha256=cfg['code_sha256'],model_manifest_sha256=cfg['model_manifest_sha256']))
        assert len(index)==len(rows)*2*4
        def value(r,op,metric):
            if '-minus-' in op:
                a,b=op.split('-minus-');return value(r,a,metric)-value(r,b,metric)
            return sum(float(index[r['item_id'],mp,op][metric]) for mp in [0,1])/2
        for ct in ['NPZ','MVRR','NPS']:
            for cond in ['gp','control']:
                rr=[meta[r['item_id']] for r in rows if r['construction']==ct and r['condition']==cond]
                coverage.append(dict(model=model,construction=ct,condition=cond,QA=len(rr),sources=len({r['source_unit'] for r in rr}),
                    clusters=len({r['cluster_id'] for r in rr}),frame_counts=dict(collections.Counter(frame(r) for r in rr))))
                groups={'all':rr,'gold:Yes':[r for r in rr if r['grounded_gold']=='Yes'],'gold:No':[r for r in rr if r['grounded_gold']=='No']}
                for ff in sorted({frame(r) for r in rr}):groups['frame:'+ff]=[r for r in rr if frame(r)==ff]
                for stratum,rs in groups.items():
                    for target in ['initial','final','all']:
                        sub=[r for r in rs if target=='all' or r['analysis_question_target']==target]
                        for metric in ['lower_correct','upper_correct']:
                            for op in OPS:panels.append(dict(model=model,construction=ct,condition=cond,stratum=stratum,target=target,
                                metric=metric,operation=op,**estimate(sub,[value(r,op,metric) for r in sub],seed=89)))
                        for op in OPS[:4]:
                            ps=[index[r['item_id'],mp,op] for r in sub for mp in [0,1]]
                            counts.append(dict(model=model,construction=ct,condition=cond,stratum=stratum,target=target,operation=op,
                                raw_tasks=len(ps),valid=sum(p['valid'] for p in ps),caps=sum(p['cap'] for p in ps),
                                lower_correct=sum(p['lower_correct'] for p in ps),upper_correct=sum(p['upper_correct'] for p in ps),
                                label_counts=dict(collections.Counter(p['label'] or 'UNKNOWN' for p in ps))))
                sources=collections.defaultdict(list)
                for r in rr:sources[r['source_unit']].append(r)
                reps=[g[0] for _,g in sorted(sources.items())];j={}
                for metric in ['lower_correct','upper_correct']:
                    for uid,rs in sources.items():
                        for op in OPS[:4]:j[uid,op]=sum(all(index[r['item_id'],mp,op][metric] for r in rs) for mp in [0,1])/2
                    for op in OPS:
                        if '-minus-' in op:
                            a,b=op.split('-minus-');vals=[j[r['source_unit'],a]-j[r['source_unit'],b] for r in reps]
                        else:vals=[j[r['source_unit'],op] for r in reps]
                        joint.append(dict(model=model,construction=ct,condition=cond,operation=op,metric=metric,target='joint_all_registered_QA',**estimate(reps,vals,seed=89)))
                for op in OPS[:4]:noise.append(dict(model=model,construction=ct,condition=cond,operation=op,
                    mapping_mismatch=sum(index[r['item_id'],0,op]['label']!=index[r['item_id'],1,op]['label'] for r in rr)/len(rr)))
    out=root/'predicate-frame-timing-map-v1.json';assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels,joint_panels=joint,coverage=coverage,runs=provenance,mapping_noise=noise,descriptive_counts=counts,
        data_sha256=sha(root/'data-v1.jsonl'),statistics='Mappings/QA averaged within Source then frozen lexical cluster; 10000 paired bootstrap seed89.',
        limits='A grammatical oracle supplies additional information; timing contrast does not alone identify a native neural frame variable. Unknown/cap bounded; joint is registered QA only.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(map_sha256=sha(out),gpu_hours=sum(r['gpu_hours'] for r in provenance),new_outputs=len(rows)*4*3,
        new_api_calls=0,panels=len(panels),joint_panels=len(joint)),indent=2)+'\n');print('E89 COMPLETE',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args()
    if a.wait:
        while True:
            runs=json.loads((a.root/'runner-pids-v1.json').read_text())
            if all((Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs):break
            time.sleep(20)
    analyze(a.root)
