"""E29 preregistered paired source ablation, keeping the two uses separate."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE, sha
from aspect_reference import read_run
from analyze import estimate


def stat(v):
    return dict(estimate([v[k] for k in sorted(v)]),verb_families=sorted(v)) if len(v)>1 else dict(estimate=None,ci95=None,n_sets=len(v),verb_families=sorted(v))


def diff(a,b):
    assert a.keys()==b.keys()
    return {k:a[k]-b[k] for k in a}


def analyze(cache,probability,nli):
    cfg,anchor=read_run(probability);assert len(anchor)==1152
    old=[];configs=[cfg]
    for ex in ('E24','E25'):
        c,rr=read_run(cache/'runs'/ex);configs.append(c)
        old.extend(dict(r,readout_actor_mode='original_activity' if ex=='E24' else r['readout_actor_mode'],
                        prior_faithful=r['faithful_role_frame'] if ex=='E24' else r['faithful_scope_actor']) for r in rr if r['target_kind']!='source_reference')
    nc=json.loads((nli/'config.json').read_text());assert sha(nli/'predictions.jsonl')==nc['predictions_sha256']
    nn=list(map(json.loads,(nli/'predictions.jsonl').read_text().splitlines()));assert len(nn)==1440
    oc=json.loads((cache/'runs/E28-base/config.json').read_text());assert sha(cache/'runs/E28-base/predictions.jsonl')==oc['predictions_sha256']
    on=list(map(json.loads,(cache/'runs/E28-base/predictions.jsonl').read_text().splitlines()));assert len(on)==2880
    for c in configs[1:]+[nc,oc]:
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','frozen'):assert c[k]==cfg[k],k
    assert cfg['batch_size']==configs[1]['batch_size']==configs[2]['batch_size']==4
    assert nc['batch_size']==oc['batch_size']==8
    for k in ('base_definition','scope_repair','class_labels','mapping_policy','thinking'):assert nc[k]==oc[k],k
    out=dict(experiment='E29',physical_probability_tasks=1152,physical_nli_tasks=1440,source_items=24,
             actual_gpu_hours=cfg['gpu_hours']+nc['gpu_hours'],bootstrap_unit='12 verb families, two published source items averaged',
             bootstrap_draws=10000,bootstrap_seed=20261005,
             interpretation='Full-S1 necessity and correction sufficiency, not an isolated syntax ablation. Probability and NLI are different uses; do not infer hidden states or combine their units.',
             scores_sha256=dict(probability=cfg['scores_sha256'],nli=nc['predictions_sha256'],E24=configs[1]['scores_sha256'],E25=configs[2]['scores_sha256'],E28=oc['predictions_sha256']),
             analysis_code_sha256=sha(Path(__file__)),probability=dict(units='bits',cells={},contrasts={},cohorts={},per_family={}),
             nli=dict(units='percentage points',cells={},contrasts={},cohorts={},per_family={},overall=dict(clear=sum(r['gold_relation'] is not None for r in nn),greedy_valid=sum(r['greedy_label_valid'] for r in nn),min_choice_mass=min(r['choice_mass'] for r in nn))))
    rows=old+anchor;conditions=('gp','explicit_cue','event_anchor_only');modes=('original_activity','same_actor','other_actor')
    families=collections.defaultdict(set)
    for r in rows:families[r['verb_family']].add(r['pair_id'])
    for cohort in ('all','eligible','anchor_acceptable_common','anchor_cross_acceptable_common','anchor_cross_clear_common','prior_and_ablation_faithful'):
        def qualifies(r):
            if cohort=='all':return True
            if cohort=='eligible':return r['eligible']
            if cohort=='anchor_acceptable_common':return r['condition']!='event_anchor_only' or r['acceptable']
            if cohort=='anchor_cross_acceptable_common':return r['condition']!='event_anchor_only' or r['anchor_cross_grammaticality']=='acceptable'
            if cohort=='anchor_cross_clear_common':return r['condition']!='event_anchor_only' or r['anchor_cross_semantics_clear'] is True
            return r['prior_faithful'] and (r['condition']!='event_anchor_only' or r['faithful_ablation'])
        ix={(r['pair_id'],r['condition'],r['readout_actor_mode'],r['role_evidence'],r['exclusion_style'],r['readout_frame'],r['target_kind']):r for r in rows if qualifies(r)}
        keep={f:sorted(sids) for f,sids in families.items() if all((sid,c,m,e,s,fr,t) in ix for sid in sids for c in conditions for m in modes for e in ('reference_only','initial_patient_only') for s in ('named','generic') for fr in ('activity','neutral_entity') for t in ('source_np','other_source_np'))}
        out['probability']['cohorts'][cohort]=keep;details={f:{} for f in keep};v={};kvals={};jvals={}
        for c in conditions:
            for m in modes:
                for e in ('reference_only','initial_patient_only'):
                    for s in ('named','generic'):
                        for fr in ('activity','neutral_entity'):
                            vv={}
                            for f,sids in keep.items():
                                obs=[]
                                for sid in sids:
                                    key=(sid,c,m,e,s,fr);own,other=ix[(*key,'source_np')],ix[(*key,'other_source_np')]
                                    assert own['target_context_sha256']==other['target_context_sha256']
                                    obs.append(other['target_total_bits']-own['target_total_bits'])
                                vv[f]=float(np.mean(obs))
                            v[c,m,e,s,fr]=vv;out['probability']['cells'][f'{cohort}/M/{c}/{m}/{e}/{s}/{fr}']=stat(vv)
                    changes={fr:diff(v[c,m,e,'named',fr],v[c,m,e,'generic',fr]) for fr in ('activity','neutral_entity')}
                    kvals[c,m,e]=diff(changes['activity'],changes['neutral_entity']);key=f'K/{c}/{m}/{e}'
                    out['probability']['contrasts'][cohort+'/'+key]=stat(kvals[c,m,e])
                    for f in keep:details[f][key]=kvals[c,m,e][f]
                for s in ('named','generic'):
                    changes={fr:diff(v[c,m,'initial_patient_only',s,fr],v[c,m,'reference_only',s,fr]) for fr in ('activity','neutral_entity')}
                    jvals[c,m,s]=diff(changes['activity'],changes['neutral_entity']);key=f'J/{c}/{m}/{s}'
                    out['probability']['contrasts'][cohort+'/'+key]=stat(jvals[c,m,s])
                    for f in keep:details[f][key]=jvals[c,m,s][f]
        for name,vectors,levels in (('K',kvals,('reference_only','initial_patient_only')),('J',jvals,('named','generic'))):
            for m in modes:
                for level in levels:
                    for reference in ('gp','explicit_cue'):
                        key=f'{name}/anchor_minus_{reference}/{m}/{level}';vv=diff(vectors['event_anchor_only',m,level],vectors[reference,m,level])
                        out['probability']['contrasts'][cohort+'/'+key]=stat(vv)
                        for f in keep:details[f][key]=vv[f]
        out['probability']['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    rows=on+nn;kinds=('old_supported','old_excluded','same_actor_new_activity','other_actor_new_activity','unrelated_unknown_control')
    for cohort in ('clear_gold','anchor_acceptable_common_clear_gold','anchor_cross_acceptable_common_clear_gold','anchor_cross_clear_common_clear_gold','prior_and_ablation_faithful_clear_gold'):
        sub=[r for r in rows if r['gold_relation'] is not None and (cohort=='clear_gold' or
             (cohort=='anchor_acceptable_common_clear_gold' and (r['condition']!='event_anchor_only' or r['acceptable'])) or
             (cohort=='anchor_cross_acceptable_common_clear_gold' and (r['condition']!='event_anchor_only' or r['anchor_cross_grammaticality']=='acceptable')) or
             (cohort=='anchor_cross_clear_common_clear_gold' and (r['condition']!='event_anchor_only' or r['anchor_cross_semantics_clear'] is True)) or
             (cohort=='prior_and_ablation_faithful_clear_gold' and r['prior_faithful'] and (r['condition']!='event_anchor_only' or r['faithful_ablation'])))]
        bysource=collections.Counter(r['pair_id'] for r in sub)
        keep={f:sorted(sids) for f,sids in families.items() if all(bysource[sid]==180 for sid in sids)}
        out['nli']['cohorts'][cohort]=keep;details={f:{} for f in keep};carry={};accuracies={}
        for mapping,maps in (('all_mappings',(0,1,2)),('map0',(0,)),('map1',(1,)),('map2',(2,))):
            for c in conditions:
                selected=[r for r in sub if r['condition']==c and r['mapping_shift'] in maps]
                for kind in kinds:
                    for measure in ('correct','p_correct','p_entailed','p_contradicted','p_undetermined','choice_mass'):
                        vv={}
                        for f,sids in keep.items():
                            rr=[r for r in selected if r['pair_id'] in sids and r['readout_kind']==kind];assert len(rr)==8*len(maps)
                            vv[f]=100*float(np.mean([r['p_relation'][measure[2:]] if measure.startswith('p_') and measure!='p_correct' else r[measure] for r in rr]))
                        key=f'{kind}/{measure}/{c}/{mapping}';out['nli']['cells'][cohort+'/'+key]=stat(vv)
                        if measure=='correct':
                            accuracies[kind,c,mapping]=vv
                            for f in keep:details[f][key]=vv[f]
                    if kind not in ('same_actor_new_activity','other_actor_new_activity'):continue
                    vv={}
                    for f,sids in keep.items():
                        rr=[r for r in selected if r['pair_id'] in sids and r['readout_kind']==kind]
                        ref=[r for r in rr if r['role_evidence']=='reference_only'];np_only=[r for r in rr if r['role_evidence']=='initial_patient_only']
                        vv[f]=50*(np.mean([r['p_relation']['contradicted'] for r in ref])-np.mean([r['p_relation']['contradicted'] for r in np_only])+np.mean([r['p_relation']['entailed'] for r in np_only])-np.mean([r['p_relation']['entailed'] for r in ref]))
                    key=f'signed_role/{kind}/{c}/{mapping}';carry[kind,c,mapping]=vv;out['nli']['contrasts'][cohort+'/'+key]=stat(vv)
                    for f in keep:details[f][key]=vv[f]
                for kind in kinds:
                    if c!='event_anchor_only':continue
                    for reference in ('gp','explicit_cue'):
                        key=f'accuracy_anchor_minus_{reference}/{kind}/{mapping}';vv=diff(accuracies[kind,c,mapping],accuracies[kind,reference,mapping]);out['nli']['contrasts'][cohort+'/'+key]=stat(vv)
                for kind in ('same_actor_new_activity','other_actor_new_activity'):
                    if c!='event_anchor_only':continue
                    for reference in ('gp','explicit_cue'):
                        key=f'signed_role_anchor_minus_{reference}/{kind}/{mapping}';vv=diff(carry[kind,c,mapping],carry[kind,reference,mapping]);out['nli']['contrasts'][cohort+'/'+key]=stat(vv)
                        for f in keep:details[f][key]=vv[f]
        out['nli']['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--probability',type=Path,required=True);p.add_argument('--nli',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.write_text(json.dumps(analyze(a.cache,a.probability,a.nli),indent=2)+'\n')
