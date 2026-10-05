"""E30 preregistered marker intervention; paired families, all label mappings."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE,sha
from aspect_reference import read_run
from analyze_source_ablation import stat,diff


def analyze(cache,probability,nli,repair_second,repair_separate,experiment='E30'):
    cross_predicate=experiment=='E31'
    pc,pr=read_run(probability);assert len(pr)==(1536 if cross_predicate else 768)
    oc,orr=read_run(cache/'runs/E29-probability');assert len(orr)==1152
    for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert pc[k]==oc[k],k
    raw=[dict(r,boundary_marker='original' if r['readout_actor_mode']=='original_activity' else 'separate') for r in orr]+pr
    nr=[];nc=[];fresh_cfg=[]
    jobs=((cache/'runs/E29-nli','separate',1440,False),(nli,'from_row' if cross_predicate else 'second',1152 if cross_predicate else 576,True),
          (repair_second,'from_row' if cross_predicate else 'second',384 if cross_predicate else 192,True),(repair_separate,'separate',192,not cross_predicate))
    for p,marker,count,fresh in jobs:
        c=json.loads((p/'config.json').read_text());assert sha(p/'predictions.jsonl')==c['predictions_sha256']
        rr=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()));assert len(rr)==count==c['task_count']
        nr.extend(dict(r,boundary_marker=r['boundary_marker'] if marker=='from_row' else marker) for r in rr if r['readout_kind'] in ('same_actor_new_activity','other_actor_new_activity'));nc.append(c)
        if fresh:fresh_cfg.append(c)
    assert len(nr)==(2304 if cross_predicate else 1536)
    for c in nc:
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','frozen'):assert c[k]==pc[k],k
        for k in ('base_definition','scope_repair','thinking','batch_size','mapping_policy'):assert c[k]==nc[0][k],k
        assert all(set(c['class_labels'][k])==set(nc[0]['class_labels'][k]) for k in nc[0]['class_labels'])
    out=dict(experiment=experiment,physical_raw_tasks=len(pr),physical_native_tasks=sum(c['task_count'] for c in fresh_cfg),source_items=24,
             actual_gpu_hours=pc['gpu_hours']+sum(c['gpu_hours'] for c in fresh_cfg),bootstrap_unit='12 verb families, two published sources averaged',
             bootstrap_draws=10000,bootstrap_seed=20261005,analysis_code_sha256=sha(Path(__file__)),
             interpretation='Matched began same/different published predicate intervention; both new activities remain distinct. Not isolated lexical semantics or proof of an event graph.' if cross_predicate else 'One-word distinct-event marker intervention. Retention excludes an exact separate-token trigger, not all contrast/pragmatics or proof of a hidden event graph.',
             input_scores_sha256=dict(raw=pc['scores_sha256'],raw_parent=oc['scores_sha256'],native=[c['predictions_sha256'] for c in nc]),
             probability=dict(units='bits',cohorts={},cells={},contrasts={},per_family={}),nli=dict(units='percentage points',cohorts={},cells={},contrasts={},per_family={}))
    families=collections.defaultdict(set)
    for r in raw:families[r['verb_family']].add(r['pair_id'])
    new_markers=('same_began','different_began') if cross_predicate else ('second',)
    markers=('separate',*new_markers)
    comparisons=(('different_began_minus_same_began','different_began','same_began'),('same_began_minus_separate','same_began','separate')) if cross_predicate else (('second_minus_separate','second','separate'),)
    def qualifies(r,co):
        if co=='all':return True
        if co=='eligible':return r['eligible']
        if co=='anchor_cross_clear':return r['anchor_cross_semantics_clear'] is True
        if co=='anchor_cross_acceptable':return r['anchor_cross_grammaticality']=='acceptable'
        if co=='selection_no_odd_common':return r.get('selectional_plausibility')!='odd'
        return r['prior_faithful'] and r['faithful_ablation']
    for cohort in ('all','eligible','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful',*(('selection_no_odd_common',) if cross_predicate else ())):
        sub=[r for r in raw if qualifies(r,cohort)];counts=collections.Counter(r['pair_id'] for r in sub)
        keep={f:sorted(sids) for f,sids in families.items() if all(counts[sid]==(112 if cross_predicate else 80) for sid in sids)}
        out['probability']['cohorts'][cohort]=keep;details={f:{} for f in keep};vectors={}
        ix={(r['pair_id'],r['boundary_marker'],r['readout_actor_mode'],r['role_evidence'],r['exclusion_style'],r['readout_frame'],r['target_kind']):r for r in sub}
        for marker,modes in (('original',('original_activity',)),*((m,('same_actor','other_actor')) for m in markers)):
            for mode in modes:
                for style in ('named','generic'):
                    for frame in ('activity','neutral_entity'):
                        vv={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                mm={}
                                for e in ('reference_only','initial_patient_only'):
                                    k=(sid,marker,mode,e,style,frame);a,b=ix[(*k,'source_np')],ix[(*k,'other_source_np')];assert a['target_context_sha256']==b['target_context_sha256']
                                    mm[e]=b['target_total_bits']-a['target_total_bits']
                                obs.append(mm['initial_patient_only']-mm['reference_only'])
                            vv[f]=float(np.mean(obs))
                        key=f'D/{marker}/{mode}/{style}/{frame}';vectors[marker,mode,style,frame]=vv;out['probability']['cells'][cohort+'/'+key]=stat(vv)
                        for f in keep:details[f][key]=vv[f]
                    vv=diff(vectors[marker,mode,style,'activity'],vectors[marker,mode,style,'neutral_entity']);key=f'J/{marker}/{mode}/{style}';vectors[marker,mode,style,'J']=vv;out['probability']['cells'][cohort+'/'+key]=stat(vv)
                    for f in keep:details[f][key]=vv[f]
        for mode in ('same_actor','other_actor'):
            for style in ('named','generic'):
                for measure in ('activity','neutral_entity','J'):
                    for name,a,b in comparisons:
                        vv=diff(vectors[a,mode,style,measure],vectors[b,mode,style,measure]);key=f'{name}/{mode}/{style}/{measure}';out['probability']['contrasts'][cohort+'/'+key]=stat(vv)
                        for f in keep:details[f][key]=vv[f]
        out['probability']['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
        sub=[r for r in nr if r['gold_relation'] is not None and qualifies(r,cohort)];counts=collections.Counter(r['pair_id'] for r in sub)
        keep={f:sorted(sids) for f,sids in families.items() if all(counts[sid]==(96 if cross_predicate else 64) for sid in sids)}
        out['nli']['cohorts'][cohort]=keep;details={f:{} for f in keep};vectors={}
        for label,mode,maps in (('base_all','base',(0,1,2)),('base_map0','base',(0,)),('base_map1','base',(1,)),('base_map2','base',(2,)),('repair_map0','repair',(0,))):
            for marker in markers:
                for kind in ('same_actor_new_activity','other_actor_new_activity'):
                    rr=[r for r in sub if r['mode']==mode and r['mapping_shift'] in maps and r['boundary_marker']==marker and r['readout_kind']==kind]
                    for measure in ('correct','p_correct','p_entailed','p_contradicted','p_undetermined','choice_mass','greedy_label_valid','signed_role'):
                        vv={}
                        for f,sids in keep.items():
                            obs=[r for r in rr if r['pair_id'] in sids];assert len(obs)==8*len(maps)
                            if measure=='signed_role':
                                ref=[r for r in obs if r['role_evidence']=='reference_only'];np_only=[r for r in obs if r['role_evidence']=='initial_patient_only']
                                value=50*(np.mean([r['p_relation']['contradicted'] for r in ref])-np.mean([r['p_relation']['contradicted'] for r in np_only])+np.mean([r['p_relation']['entailed'] for r in np_only])-np.mean([r['p_relation']['entailed'] for r in ref]))
                            else:value=100*float(np.mean([r['p_relation'][measure[2:]] if measure.startswith('p_') and measure!='p_correct' else r[measure] for r in obs]))
                            vv[f]=value
                        vectors[marker,kind,label,measure]=vv;key=f'{marker}/{kind}/{label}/{measure}';out['nli']['cells'][cohort+'/'+key]=stat(vv)
                        if measure in ('correct','signed_role'):
                            for f in keep:details[f][key]=vv[f]
            for kind in ('same_actor_new_activity','other_actor_new_activity'):
                for measure in ('correct','signed_role'):
                    for name,a,b in comparisons:
                        key=f'{name}/{kind}/{label}/{measure}';vv=diff(vectors[a,kind,label,measure],vectors[b,kind,label,measure]);out['nli']['contrasts'][cohort+'/'+key]=stat(vv)
                        for f in keep:details[f][key]=vv[f]
        for marker in markers:
            for kind in ('same_actor_new_activity','other_actor_new_activity'):
                for measure in ('correct','signed_role'):
                    key=f'repair_minus_base_map0/{marker}/{kind}/{measure}';out['nli']['contrasts'][cohort+'/'+key]=stat(diff(vectors[marker,kind,'repair_map0',measure],vectors[marker,kind,'base_map0',measure]))
        out['nli']['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--experiment',choices=['E30','E31'],default='E30');p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--probability',type=Path,required=True);p.add_argument('--nli',type=Path,required=True);p.add_argument('--repair-second','--repair-new',dest='repair_second',type=Path,required=True);p.add_argument('--repair-separate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.cache,a.probability,a.nli,a.repair_second,a.repair_separate,a.experiment),indent=2)+'\n')
