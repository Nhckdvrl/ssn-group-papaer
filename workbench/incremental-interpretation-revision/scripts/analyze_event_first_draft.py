"""E76 complete pipeline map; source gold stays original, draft roles unjudged."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from joint_relation_use import MODELS
from analyze_correct_answer_carry import estimate

OPS=['DIRECT','FREE','EVENT_FIRST','FREE-minus-DIRECT','EVENT_FIRST-minus-DIRECT','EVENT_FIRST-minus-FREE']


def analyze(root,direct,freeparent,runs):
    data=root/'data-v1.jsonl';rows=list(map(json.loads,data.read_text().splitlines()));ids={r['item_id'] for r in rows};assert len(ids)==len(rows)==892 and sha(data)==sha(direct/'data-v1.jsonl')
    for r in rows:r['cluster_id']=r['analysis_cluster_id']
    expected={(uid,op,ro,mp) for uid in ids for op in ['FREE','EVENT_FIRST'] for ro in ['words','letters'] for mp in [0,1]};panels=[];provenance=[];draft_lengths=[];mapping_noise=[]
    for model in MODELS:
        bdir=direct/'runs-v1'/model;bcfg=json.loads((bdir/'config.json').read_text());assert bcfg['predictions_sha256']==sha(bdir/'predictions.jsonl') and bcfg['data_sha256']==sha(data)
        records=[x for x in runs if x['model']==model];n=records[0]['shards'];assert {x['shard'] for x in records}==set(range(n));pred=[];drafts=[]
        for run in records:
            d=Path(run['out']);cfg=json.loads((d/'config.json').read_text());assert cfg['data_sha256']==sha(data) and cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['drafts_sha256']==sha(d/'drafts.jsonl')
            assert cfg['model_manifest_sha256']==bcfg['model_manifest_sha256'];part=list(map(json.loads,(d/'predictions.jsonl').read_text().splitlines()));generated=list(map(json.loads,(d/'drafts.jsonl').read_text().splitlines()))
            input_rows=[r for r in rows if int(r['sentence_sha256'][:16],16)%n==run['shard']];uids={r['item_id'] for r in input_rows};source_ids={r['source_unit'] for r in input_rows}
            assert len(part)==cfg['tasks']==8*len(input_rows) and {p['item_id'] for p in part}==uids
            assert len(generated)==cfg['sources']==len(source_ids) and {p['source_unit'] for p in generated}==source_ids
            pred.extend(part);drafts.extend(generated);provenance.append(dict(model=model,shard=run['shard'],gpu_hours=cfg['gpu_hours'],draft_gpu_hours=cfg['draft_gpu_hours'],config_sha256=sha(d/'config.json'),predictions_sha256=cfg['predictions_sha256'],drafts_sha256=cfg['drafts_sha256'],free_predictions_sha256=cfg['free_predictions_sha256'],direct_predictions_sha256=bcfg['predictions_sha256'],instrument_LP_max_delta=cfg['instrument_LP_max_delta']))
        index={(p['item_id'],p['operation'],p['readout'],p['mapping']):p for p in pred};assert len(index)==len(pred)==len(expected) and set(index)==expected
        baseline=[p for p in map(json.loads,(bdir/'predictions.jsonl').read_text().splitlines()) if p['operation']=='NONE'];assert len(baseline)==4*len(rows)
        for p in baseline:index[p['item_id'],'DIRECT',p['readout'],p['mapping']]=p
        fp=freeparent/'runs-v2'/model;fcfg=json.loads((fp/'config.json').read_text());assert fcfg['predictions_sha256']==sha(fp/'predictions.jsonl')
        fd=[p for p in map(json.loads,(fp/'predictions.jsonl').read_text().splitlines()) if p['reading']=='NONE'];source_rows={r['source_unit']:r for r in rows}
        assert len(fd)==len(drafts)==356
        for op,gs in [('FREE',fd),('EVENT_FIRST',drafts)]:
            for construction in ['MVRR','NPZ','NPS','NPVP']:
                for condition in ['gp','control']:
                    selected=[g for g in gs if source_rows[g.get('source_unit',g.get('item_id'))]['construction']==construction and source_rows[g.get('source_unit',g.get('item_id'))]['condition']==condition]
                    lengths=[len(g['generated_token_ids']) for g in selected]
                    draft_lengths.append(dict(model=model,operation=op,construction=construction,condition=condition,sources=len(selected),mean_tokens=sum(lengths)/len(lengths),max_tokens=max(lengths),cap_rate=sum(g['capped'] for g in selected)/len(selected)))
        for r in rows:
            for op in ['DIRECT','FREE','EVENT_FIRST']:
                for ro in ['words','letters']:
                    for mp,shown in enumerate([['Yes','No'],['No','Yes']]):
                        p=index[r['item_id'],op,ro,mp];assert p['candidate_gold']==shown.index(r['grounded_gold'])
        def values(selected,operation,readout,metric):
            def v(r,op):return sum(float(index[r['item_id'],op,readout,mp][metric]) for mp in [0,1])/2
            if '-minus-' in operation:
                a,b=operation.split('-minus-');return [v(r,a)-v(r,b) for r in selected]
            return [v(r,operation) for r in selected]
        for construction in ['MVRR','NPZ','NPS','NPVP']:
            for condition in ['gp','control']:
                for readout in ['words','letters']:
                    for target in ['initial','final','all']:
                        selected=[r for r in rows if r['construction']==construction and r['condition']==condition and (target=='all' or r['analysis_question_target']==target)]
                        for metric in ['correct','p_correct']:
                            for operation in OPS:panels.append(dict(model=model,construction=construction,condition=condition,readout=readout,target=target,metric=metric,operation=operation,**estimate(selected,values(selected,operation,readout,metric),seed=76)))
                    selected=[r for r in rows if r['construction']==construction and r['condition']==condition];grouped=collections.defaultdict(list)
                    for r in selected:grouped[r['source_unit']].append(r)
                    representatives=[g[0] for uid,g in sorted(grouped.items())];joint={}
                    for uid,g in grouped.items():
                        assert {'initial','final'}<={r['analysis_question_target'] for r in g}
                        for op in ['DIRECT','FREE','EVENT_FIRST']:joint[uid,op]=sum(all(index[r['item_id'],op,readout,mp]['correct'] for r in g) for mp in [0,1])/2
                    for operation in OPS:
                        if '-minus-' in operation:
                            a,b=operation.split('-minus-');vs=[joint[r['source_unit'],a]-joint[r['source_unit'],b] for r in representatives]
                        else:vs=[joint[r['source_unit'],operation] for r in representatives]
                        panels.append(dict(model=model,construction=construction,condition=condition,readout=readout,target='joint_all_questions',metric='correct',operation=operation,**estimate(representatives,vs,seed=76)))
                    for op in ['DIRECT','FREE','EVENT_FIRST']:
                        diffs=[abs(float(index[r['item_id'],op,readout,0]['correct'])-float(index[r['item_id'],op,readout,1]['correct'])) for r in selected]
                        mapping_noise.append(dict(model=model,construction=construction,condition=condition,readout=readout,operation=op,mean_QA_correct_flip=sum(diffs)/len(diffs)))
    assert len(panels)==2016
    out=root/'event-first-draft-map-v1.json';assert not out.exists();out.write_text(json.dumps(dict(data_sha256=sha(data),panels=panels,runs=provenance,draft_lengths=draft_lengths,mapping_noise=mapping_noise,statistics='Mean two mappings per QA; mean QA per Source; lexical cluster paired bootstrap10000 seed76. Joint allQA per mapping then Source.',limits='End-to-end original source QA; draft roles not yet audited. Drafts never become gold or replace the original source.'),indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,shards=len(runs),panels=len(panels),map_sha256=sha(out),gpu_hours=sum(x['gpu_hours'] for x in provenance)),indent=2)+'\n');print('E76 complete',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--direct',type=Path,required=True);p.add_argument('--free-parent',type=Path,required=True);p.add_argument('--wait',action='store_true');a=p.parse_args();runs=json.loads((a.root/'runner-pids-v1.json').read_text())
    while a.wait:
        ready=[]
        for r in runs:
            path=Path(r['out'])/'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root,a.direct,a.free_parent,runs)
