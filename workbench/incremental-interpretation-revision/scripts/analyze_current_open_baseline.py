"""E82 complete current-model panel; original gold, all outcomes included."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate

OPS=['DIRECT','ONE_RECOVER','ONE_RECOVER-minus-DIRECT']


def analyze(root,runs):
    data=root/'data-v1.jsonl';rows=list(map(json.loads,data.read_text().splitlines()))
    assert len(rows)==892 and sha(data)==json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    for r in rows:r['cluster_id']=r['analysis_cluster_id']
    expected={(r['item_id'],op,ro,mp) for r in rows for op in OPS[:2] for ro in ['words','letters'] for mp in [0,1]}
    panels=[];provenance=[];lengths=[];noise=[]
    for model in MODELS:
        records=[r for r in runs if r['model']==model];n=records[0]['shards']
        assert {r['shard'] for r in records}==set(range(n));index={}
        for run in records:
            p=Path(run['out']);cfg=json.loads((p/'config.json').read_text())
            assert cfg['data_sha256']==sha(data) and cfg['predictions_sha256']==sha(p/'predictions.jsonl')
            assert cfg['thinking_enabled'] is False and cfg['official_empty_closed_thinking_boundary']
            sub=[r for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']]
            pred=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()))
            assert len(pred)==cfg['tasks']==8*len(sub) and {r['item_id'] for r in pred}=={r['item_id'] for r in sub}
            for x in pred:
                k=x['item_id'],x['operation'],x['readout'],x['mapping'];assert k not in index;index[k]=x
            provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],
                model_manifest_sha256=cfg['model_manifest_sha256'],config_sha256=sha(p/'config.json'),
                predictions_sha256=cfg['predictions_sha256'],repeat_LP_max_delta=max(x['repeat_LP_max_delta'] for x in cfg['instrument']),
                prefix_full_LP_max_delta=cfg['prefix_full_LP_max_delta'],score_function=cfg['score_function'],
                released_quantization=cfg['released_quantization'],dequantized_to_bfloat16=cfg['dequantized_to_bfloat16']))
        assert set(index)==expected
        for r in rows:
            for op in OPS[:2]:
                for ro in ['words','letters']:
                    for mp,shown in enumerate([['Yes','No'],['No','Yes']]):
                        assert index[r['item_id'],op,ro,mp]['candidate_gold']==shown.index(r['grounded_gold'])
        def atom(r,op,ro,metric):
            def v(k):return sum(float(index[r['item_id'],k,ro,mp][metric]) for mp in [0,1])/2
            if '-minus-' in op:
                a,b=op.split('-minus-');return v(a)-v(b)
            return v(op)
        for ct in ['MVRR','NPZ','NPS','NPVP']:
            for cond in ['gp','control']:
                allrows=[r for r in rows if r['construction']==ct and r['condition']==cond]
                for op in OPS[:2]:
                    ts=[index[r['item_id'],op,ro,mp]['prompt_tokens'] for r in allrows for ro in ['words','letters'] for mp in [0,1]]
                    lengths.append(dict(model=model,construction=ct,condition=cond,operation=op,mean_tokens=sum(ts)/len(ts),max_tokens=max(ts),tasks=len(ts)))
                for ro in ['words','letters']:
                    for target in ['initial','final','all']:
                        selected=[r for r in allrows if target=='all' or r['analysis_question_target']==target]
                        for metric in ['correct','p_correct']:
                            for op in OPS:
                                panels.append(dict(model=model,construction=ct,condition=cond,readout=ro,target=target,metric=metric,operation=op,
                                    **estimate(selected,[atom(r,op,ro,metric) for r in selected],seed=82)))
                    groups=collections.defaultdict(list)
                    for r in allrows:groups[r['source_unit']].append(r)
                    reps=[g[0] for _,g in sorted(groups.items())];joint={}
                    for uid,g in groups.items():
                        for op in OPS[:2]:joint[uid,op]=sum(all(index[r['item_id'],op,ro,mp]['correct'] for r in g) for mp in [0,1])/2
                    for op in OPS:
                        if '-minus-' in op:
                            a,b=op.split('-minus-');vs=[joint[r['source_unit'],a]-joint[r['source_unit'],b] for r in reps]
                        else:vs=[joint[r['source_unit'],op] for r in reps]
                        panels.append(dict(model=model,construction=ct,condition=cond,readout=ro,target='joint_all_questions',metric='correct',operation=op,
                            **estimate(reps,vs,seed=82)))
                    for op in OPS[:2]:
                        noise.append(dict(model=model,construction=ct,condition=cond,readout=ro,operation=op,
                            mean_QA_correct_flip=sum(abs(float(index[r['item_id'],op,ro,0]['correct'])-float(index[r['item_id'],op,ro,1]['correct'])) for r in allrows)/len(allrows)))
    assert len(panels)==1008 and len(lengths)==48 and len(noise)==96
    out=root/'current-open-model-map-v1.json';assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data),panels=panels,runs=provenance,prompt_lengths=lengths,mapping_noise=noise,
        statistics='Mean mappings per QA; mean QA per Source; lexical cluster paired bootstrap10000 seed82. Joint all originalQA per mapping then Source.',
        limits='Released 2026/late2025 model panel; nonthinking answer boundary only. Q/G original BF16; Ministral released FP8 dequantized to BF16. No architecture/scaling causal comparison or prompt-only ability certification.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),
        gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E82 complete',sha(out),flush=True)


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
