"""E102 one fixed diagnostic-evidence oracle; whole reward and all inputs preserved."""
import argparse
import json
from pathlib import Path
from data import sha
from forward_semantic_credit import rank
from analyze_correct_answer_carry import estimate


def analyze(root, regions_map, semantic_map, output_name):
    regions=json.loads(regions_map.read_text());semantics=json.loads(semantic_map.read_text())
    assert regions['E96_data_sha256']==semantics['data_sha256']
    models=regions['models'];assert set(models)<=set(semantics['models'])
    refs={(r['model'],r['item_id']):r for r in semantics['records'] if r['condition']=='gp'}
    records=[]
    for r in regions['records']:
        z=dict(r,metrics={});ref=refs[r['model'],r['item_id']]
        if r['boundary'] is None:
            z['boundary_missing']=True;records.append(z);continue
        for op,region in [('WHOLE','whole'),('REVISION_EVIDENCE','from'),('WORD_ONLY_DIAGNOSTIC','word')]:
            preferred=rank(0,r['metrics'][region+'_delta_reward'])
            if op=='WHOLE':assert preferred==ref['reward_rank']
            z['metrics'][op]={}
            for criterion,gold in ref['metrics'].items():
                gs=gold['possible_ranks'];p=preferred
                z['metrics'][op][criterion]=dict(rank=p,gold_rank=gold['rank'],
                    alignment_lower=min(p*g for g in gs),alignment_upper=max(p*g for g in gs),
                    correct_lower=float(all(p==g for g in gs)),correct_upper=float(any(p==g for g in gs)),
                    opposes_lower=float(all(p*g<0 for g in gs)),opposes_upper=float(any(p*g<0 for g in gs)),tie=float(p==0))
        records.append(z)
    panels,counts=[],[]
    for model in models:
        for ct in ['ALL','MVRR','NPZ','NPS']:
            base=[r for r in records if r['model']==model and (ct=='ALL' or r['construction']==ct)]
            for criterion in ['fidelity','pattern']:
                eligible=[r for r in base if 'WHOLE' in r['metrics'] and criterion in r['metrics']['WHOLE']]
                counts.append(dict(model=model,construction=ct,criterion=criterion,sources=len(base),eligible=len(eligible),
                    boundary_missing=sum(r.get('boundary_missing',False) for r in base),structural_NA=len(base)-len(eligible)))
                for subset in ['ALL','CHANGED_DIAGNOSTIC','TIE_DIAGNOSTIC']:
                    rs=[r for r in eligible if subset=='ALL' or
                        (r['metrics']['WHOLE'][criterion]['gold_rank'] in [-1,1] if subset=='CHANGED_DIAGNOSTIC' else r['metrics']['WHOLE'][criterion]['gold_rank']==0)]
                    for op in ['WHOLE','REVISION_EVIDENCE','WORD_ONLY_DIAGNOSTIC','REVISION_EVIDENCE-minus-WHOLE','WORD_ONLY_DIAGNOSTIC-minus-WHOLE']:
                        for metric in ['alignment_lower','alignment_upper','correct_lower','correct_upper','opposes_lower','opposes_upper','tie']:
                            xs=[]
                            for r in rs:
                                if '-minus-' in op:
                                    new=op.split('-minus-')[0]
                                    opposite=metric[:-6]+'_upper' if metric.endswith('_lower') else metric[:-6]+'_lower' if metric.endswith('_upper') else metric
                                    x=r['metrics'][new][criterion][metric]-r['metrics']['WHOLE'][criterion][opposite]
                                else:x=r['metrics'][op][criterion][metric]
                                xs.append(x)
                            panels.append(dict(model=model,construction=ct,criterion=criterion,subset=subset,
                                operation=op,metric=metric,**estimate(rs,xs,seed=102)))
    root.mkdir(exist_ok=True);out=root/output_name;assert not out.exists()
    out.write_text(json.dumps(dict(models=models,panels=panels,records=records,counts=counts,
        semantic_map_sha256=sha(semantic_map),regions_map_sha256=sha(regions_map),new_GPU_hours=0,new_API_calls=0,
        scope='Full complete registered families, same frozen content and cached LP; original T2 diagnostic-position oracle.',
        limits='Reward aggregation intervention, not neural repair, automatic cue detection, or trained-policy evidence. Word-only secondary diagnostic.'),indent=2)+'\n')
    report=dict(map_sha256=sha(out),models=models,panels=len(panels),new_GPU_hours=0,new_API_calls=0)
    (root/(output_name+'.manifest.json')).write_text(json.dumps(report,indent=2)+'\n');print('E102 sealed',report,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['root','regions-map','semantic-map']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--output-name',default='revision-evidence-oracle-map-v1.json')
    a=p.parse_args();analyze(a.root,a.regions_map,a.semantic_map,a.output_name)
