"""E88 complete-only predicate versus NP visibility map; frozen original gold."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from analyze_correct_answer_carry import estimate

MODELS=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']
OPS=['CAUSAL','INSTRUCTION','VERB_ONLY','NOUN_ONLY','VERB_ONLY-minus-CAUSAL',
     'NOUN_ONLY-minus-CAUSAL','VERB_ONLY-minus-NOUN_ONLY']


def analyze(root):
    rows=list(map(json.loads,(root/'data-v1.jsonl').read_text().splitlines()))
    meta={r['item_id']:dict(r,cluster_id=r['analysis_cluster_id']) for r in rows}
    gps={r['source_unit']:r for r in rows if r['condition']=='gp'}
    def frame(r):
        gp=gps[r['frame_locator']['GP_source_unit']]
        if r['construction']=='NPZ':
            return 'NPZ_author_alternation' if gp['source']=='cehakova2025' else ('NPZ_reflexive' if 'reflexive' in (gp['original_source_sent_type'] or '') else 'NPZ_other')
        if r['construction']=='MVRR':return 'MVRR_dative' if gp['source']=='cehakova2025' else 'MVRR_other'
        return 'NPS_complement'
    runs=json.loads((root/'runner-pids-v1.json').read_text())
    panels=[];joint=[];noise=[];coverage=[];provenance=[];edge_summary=[]
    for model in MODELS:
        index={};parent=root.parent/'E54/runs-v1'/model;pc=json.loads((parent/'config.json').read_text())
        assert sha(parent/'predictions.jsonl')==pc['predictions_sha256']
        for p in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines()):
            if p['item_id'] not in meta or p['operation'] not in ['CAUSAL','INSTRUCTION']:continue
            key=p['item_id'],p['readout'],p['mapping'],p['operation'];assert key not in index;index[key]=p
        selected=[r for r in runs if r['model']==model];n=selected[0]['shards'];assert {r['shard'] for r in selected}==set(range(n))
        for run in selected:
            out=Path(run['out']);cfg=json.loads((out/'config.json').read_text())
            assert sha(out/'predictions.jsonl')==cfg['predictions_sha256'] and cfg['data_sha256']==sha(root/'data-v1.jsonl')
            assert cfg['model_manifest_sha256']==sha(root.parent/'models'/model/'manifest.json')
            ps=list(map(json.loads,(out/'predictions.jsonl').read_text().splitlines()));assert len(ps)==cfg['tasks']
            for p in ps:
                r=meta[p['item_id']];key=p['item_id'],p['readout'],p['mapping'],p['operation']
                assert key not in index and int(r['frame_locator']['GP_source_unit'].split(':')[-1][:16],16)%n==run['shard']
                old=index[p['item_id'],p['readout'],p['mapping'],'CAUSAL']
                assert p['prompt_sha256']==old['prompt_sha256'] and p['candidate_gold']==old['candidate_gold']
                index[key]=p
            provenance.append(dict(model=model,shard=run['shard'],predictions_sha256=cfg['predictions_sha256'],config_sha256=sha(out/'config.json'),
                gpu_hours=cfg['gpu_hours'],model_manifest_sha256=cfg['model_manifest_sha256'],instrument=cfg['instrument']))
        assert len(index)==len(rows)*4*4
        def value(r,ro,op,metric):
            if '-minus-' in op:
                a,b=op.split('-minus-');return value(r,ro,a,metric)-value(r,ro,b,metric)
            return sum(float(index[r['item_id'],ro,mp,op][metric]) for mp in [0,1])/2
        for ct in ['NPZ','MVRR','NPS']:
            for cond in ['gp','control']:
                rr=[meta[r['item_id']] for r in rows if r['construction']==ct and r['condition']==cond]
                coverage.append(dict(model=model,construction=ct,condition=cond,QA=len(rr),sources=len({r['source_unit'] for r in rr}),
                    clusters=len({r['analysis_cluster_id'] for r in rr}),frame_counts=dict(collections.Counter(frame(r) for r in rr))))
                groups={'all':rr}
                for ff in sorted({frame(r) for r in rr}):groups['frame:'+ff]=[r for r in rr if frame(r)==ff]
                groups.update({'gold:Yes':[r for r in rr if r['grounded_gold']=='Yes'], 'gold:No':[r for r in rr if r['grounded_gold']=='No']})
                for ro in ['words','letters']:
                    for stratum,rs in groups.items():
                        for target in ['initial','final','all']:
                            sub=[r for r in rs if target=='all' or r['analysis_question_target']==target]
                            for metric in ['correct','p_correct']:
                                for op in OPS:
                                    panels.append(dict(model=model,construction=ct,condition=cond,readout=ro,stratum=stratum,target=target,metric=metric,operation=op,
                                        **estimate(sub,[value(r,ro,op,metric) for r in sub],seed=88)))
                    sources=collections.defaultdict(list)
                    for r in rr:sources[r['source_unit']].append(r)
                    reps=[g[0] for _,g in sorted(sources.items())];j={}
                    for uid,rs in sources.items():
                        for op in OPS[:4]:j[uid,op]=sum(all(index[r['item_id'],ro,mp,op]['correct'] for r in rs) for mp in [0,1])/2
                    for op in OPS:
                        if '-minus-' in op:
                            a,b=op.split('-minus-');vals=[j[r['source_unit'],a]-j[r['source_unit'],b] for r in reps]
                        else:vals=[j[r['source_unit'],op] for r in reps]
                        joint.append(dict(model=model,construction=ct,condition=cond,readout=ro,operation=op,target='joint_all_registered_QA',
                            **estimate(reps,vals,seed=88)))
                    for op in OPS[:4]:
                        noise.append(dict(model=model,construction=ct,condition=cond,readout=ro,operation=op,
                            mapping_flip=sum(index[r['item_id'],ro,0,op]['correct']!=index[r['item_id'],ro,1,op]['correct'] for r in rr)/len(rr)))
                    for op in ['VERB_ONLY','NOUN_ONLY']:
                        ps=[index[r['item_id'],ro,mp,op] for r in rr for mp in [0,1]]
                        edge_summary.append(dict(model=model,construction=ct,condition=cond,readout=ro,operation=op,
                            query_tokens_mean=sum(len(p['query_tokens']) for p in ps)/len(ps),
                            new_future_edges_mean=sum(p['new_future_edges'] for p in ps)/len(ps),
                            new_future_edges_min=min(p['new_future_edges'] for p in ps),new_future_edges_max=max(p['new_future_edges'] for p in ps)))
    out=root/'verb-frame-lookahead-map-v1.json';assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels,joint_panels=joint,mapping_noise=noise,coverage=coverage,edge_summary=edge_summary,runs=provenance,
        data_sha256=sha(root/'data-v1.jsonl'),statistics='Average mappings/QA within Source, then Source within frozen lexical cluster; 10000 paired bootstrap seed88.',
        limits='Source-bounded noncausal visibility is a diagnostic, not ideal grammar or native frame mechanism. Verb and NP have different token/edge counts; frame labels are original input-defined source families. Joint covers registered QA only.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(map_sha256=sha(out),gpu_hours=sum(r['gpu_hours'] for r in provenance),new_api_calls=0,
        new_conditions=len(rows)*8*3,panels=len(panels),joint=len(joint)),indent=2)+'\n');print('E88 COMPLETE',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args()
    if a.wait:
        while True:
            runs=json.loads((a.root/'runner-pids-v1.json').read_text())
            if all((Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs):break
            time.sleep(20)
    analyze(a.root)
