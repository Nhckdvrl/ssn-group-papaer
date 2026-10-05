"""E36 preregistered realizations and frozen E31 parent cohorts."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE,sha
from aspect_reference import read_run
from analyze_source_ablation import stat,diff

FORMS=('contrast_parent','affirmative_mention_first','affirmative_mention_last')
MODES=('old_activity','same_actor','other_actor')


def analyze(cache,raw,base,repair):
    cfg,rows=read_run(raw);assert len(rows)==1920
    configs=[cfg]
    for ex in ('E29','E31'):
        c,rr=read_run(cache/'runs'/('E29-probability' if ex=='E29' else 'E31-probability'))
        configs.append(c)
        rr=[r for r in rr if r['exclusion_style']=='named' and (ex=='E31' or r['readout_actor_mode']=='original_activity')]
        rows.extend(dict(r,fact_realization='contrast_parent') for r in rr)
    assert len(rows)==2880
    nn=[]
    for path,n in [(base,2016),(repair,672)]:
        c=json.loads((path/'config.json').read_text());assert sha(path/'predictions.jsonl')==c['predictions_sha256']
        rr=list(map(json.loads,(path/'predictions.jsonl').read_text().splitlines()));assert len(rr)==n==c['task_count'];nn.extend(rr);configs.append(c)
    for c in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','torch','transformers'):assert cfg[k]==c[k],k
    for r in rows:
        r['analysis_mode']='old_activity' if r['readout_actor_mode']=='original_activity' else r['readout_actor_mode']
        r['analysis_predicate']='old' if r['analysis_mode']=='old_activity' else r['boundary_marker']
    for r in nn:
        kind=r['readout_kind']
        if kind in ('old_supported','old_excluded'):
            source=(kind=='old_supported')==(r['role_evidence']=='initial_patient_only')
            kind='old_source_patient' if source else 'old_reference_patient'
        r['analysis_kind']=kind
        r['analysis_predicate']='old' if kind.startswith('old_') or kind=='unrelated_unknown_control' else r['boundary_marker']
    wb=Path(__file__).resolve().parents[1];parent=wb/'results/E31-summary.json';pc=json.loads(parent.read_text())['probability']['cohorts']
    sources=collections.defaultdict(set)
    for r in rows:sources[r['verb_family']].add(r['pair_id'])
    out=dict(experiment='E36',raw_tasks=1920,native_tasks=2688,actual_gpu_hours=cfg['gpu_hours']+sum(c['gpu_hours'] for c in configs[-2:]),
             bootstrap_draws=10000,bootstrap_seed=20261005,bootstrap_unit='12 verb families, two sources averaged',
             scores_sha256=[c.get('scores_sha256',c.get('predictions_sha256')) for c in configs],parent_cohorts_sha256=sha(parent),
             probability=dict(units='bits',cells={},contrasts={},per_family={},cohorts={}),nli=dict(units='percentage points',cells={},contrasts={},cohorts={}))
    def qualifies(r,co):
        if co=='eligible':return r['eligible']
        if co=='grammar_common':return r['fact_realization']=='contrast_parent' or r['acceptable']
        return True
    for co in ('all','eligible','grammar_common','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        chosen=[r for r in rows if qualifies(r,co)];counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sorted(sids) for f,sids in sources.items() if all(counts[sid]==120 for sid in sids)}
        if co in pc:keep={f:s for f,s in keep.items() if f in pc[co]}
        out['probability']['cohorts'][co]=keep
        ix={(r['pair_id'],r['fact_realization'],r['analysis_mode'],r['analysis_predicate'],r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen}
        assert len(ix)==len(chosen);vals={};per={f:{} for f in keep}
        def record(store,key,v):
            out['probability'][store][co+'/'+key]=stat(v)
            for f in keep:per[f][key]=v[f]
        for form in FORMS:
            for mode in MODES:
                for pred in (('old',) if mode=='old_activity' else ('same_began','different_began')):
                    for frame in ('activity','neutral_entity'):
                        for role in ('reference_only','initial_patient_only'):
                            v={}
                            for f,sids in keep.items():
                                mm=[]
                                for sid in sids:
                                    a=ix[sid,form,mode,pred,role,frame,'source_np'];b=ix[sid,form,mode,pred,role,frame,'other_source_np']
                                    assert a['target_context_sha256']==b['target_context_sha256'];mm.append(b['target_total_bits']-a['target_total_bits'])
                                v[f]=float(np.mean(mm))
                            vals[form,mode,pred,role,frame]=v;record('cells',f'M/{form}/{mode}/{pred}/{role}/{frame}',v)
                        v=diff(vals[form,mode,pred,'initial_patient_only',frame],vals[form,mode,pred,'reference_only',frame]);vals[form,mode,pred,frame]=v;record('cells',f'D/{form}/{mode}/{pred}/{frame}',v)
                    v=diff(vals[form,mode,pred,'activity'],vals[form,mode,pred,'neutral_entity']);vals[form,mode,pred,'J']=v;record('cells',f'J/{form}/{mode}/{pred}',v)
                if mode!='old_activity':
                    for measure in ('activity','neutral_entity','J'):
                        record('contrasts',f'different_minus_same/{form}/{mode}/{measure}',diff(vals[form,mode,'different_began',measure],vals[form,mode,'same_began',measure]))
        for mode in MODES:
            for pred in (('old',) if mode=='old_activity' else ('same_began','different_began')):
                for measure in ('activity','neutral_entity','J'):
                    for form in FORMS[1:]:record('contrasts',f'{form}_minus_contrast/{mode}/{pred}/{measure}',diff(vals[form,mode,pred,measure],vals['contrast_parent',mode,pred,measure]))
                    record('contrasts',f'mention_last_minus_first/{mode}/{pred}/{measure}',diff(vals[FORMS[2],mode,pred,measure],vals[FORMS[1],mode,pred,measure]))
        out['probability']['per_family'][co]=[dict(verb_family=f,**per[f]) for f in sorted(keep)]
        chosen_n=[r for r in nn if r['gold_relation'] is not None and (co!='eligible' or r['eligible']) and (co!='grammar_common' or r['acceptable'])]
        count_n=collections.Counter(r['pair_id'] for r in chosen_n);nk={f:s for f,s in keep.items() if all(count_n[sid]==112 for sid in s)};out['nli']['cohorts'][co]=nk;nv={}
        for form in FORMS[1:]:
            for kind in ('old_source_patient','old_reference_patient','same_actor_new_activity','other_actor_new_activity','unrelated_unknown_control'):
                for pred in (('old',) if kind.startswith('old_') or kind=='unrelated_unknown_control' else ('same_began','different_began')):
                    for label,mode,maps in [('base_all','base',(0,1,2)),('base_map0','base',(0,)),('base_map1','base',(1,)),('base_map2','base',(2,)),('repair_map0','repair',(0,))]:
                        rr=[r for r in chosen_n if r['fact_realization']==form and r['analysis_kind']==kind and r['analysis_predicate']==pred and r['mode']==mode and r['mapping_shift'] in maps]
                        for measure in ('correct','p_correct','choice_mass','greedy_label_valid'):
                            v={}
                            for f,sids in nk.items():
                                obs=[r for r in rr if r['pair_id'] in sids];assert len(obs)==4*len(maps);v[f]=100*float(np.mean([r[measure] for r in obs]))
                            nv[form,kind,pred,label,measure]=v;out['nli']['cells'][f'{co}/{form}/{kind}/{pred}/{label}/{measure}']=stat(v)
                    out['nli']['contrasts'][f'{co}/repair_minus_base/{form}/{kind}/{pred}/correct']=stat(diff(nv[form,kind,pred,'repair_map0','correct'],nv[form,kind,pred,'base_map0','correct']))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--raw',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--repair',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.raw,a.base,a.repair),indent=2)+'\n')
