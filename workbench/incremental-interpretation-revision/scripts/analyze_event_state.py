"""E28 NLI calibration, cyclic-label sensitivity and signed scope carryover."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from data import sha


def analyze(base,repair):
    cfgs=[];rows=[]
    for p,count in ((base,2880),(repair,960)):
        c=json.loads((p/'config.json').read_text());assert c['predictions_sha256']==sha(p/'predictions.jsonl')
        rr=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()));assert len(rr)==count==c['task_count'];cfgs.append(c);rows.extend(rr)
    for k in ('model_manifest','dtype','tf32','attention','seed','frozen','thinking','torch','transformers','batch_size','git_commit','code_sha256','data_sha256'):assert cfgs[0][k]==cfgs[1][k],k
    assert len({(r['item_id'],r['mode'],r['mapping_shift']) for r in rows})==3840
    kinds=('old_supported','old_excluded','same_actor_new_activity','other_actor_new_activity','unrelated_unknown_control')
    result=dict(experiment='E28',physical_tasks=3840,source_items=24,bootstrap_unit='12 published verb families after two-source averaging',
                bootstrap_draws=10000,bootstrap_seed=20261005,units='percentage points',
                interpretation='Independently audited event-fact relations. Undetermined is kept separate from contradicted. Correct classifications measure accessible scoped interpretation, not hidden state before the question.',
                source_shards=[dict(mode=c['mode'],config_sha256=sha(p/'config.json'),predictions_sha256=c['predictions_sha256'],gpu_hours=c['gpu_hours']) for p,c in zip((base,repair),cfgs)],
                actual_gpu_hours=sum(c['gpu_hours'] for c in cfgs),analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={},cohorts={},per_family={},overall={})
    result['overall']=dict(clear_gold=sum(r['gold_relation'] is not None for r in rows),greedy_valid=sum(r['greedy_label_valid'] for r in rows),mean_choice_mass=float(np.mean([r['choice_mass'] for r in rows])),min_choice_mass=min(r['choice_mass'] for r in rows))
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,verb_families=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    configs=(('base_all_mappings','base',(0,1,2)),('base_map0','base',(0,)),('base_map1','base',(1,)),('base_map2','base',(2,)),('repair_map0','repair',(0,)))
    for stratum in ('clear_gold','prior_faithful_clear_gold'):
        sub=[r for r in rows if r['gold_relation'] is not None and (stratum=='clear_gold' or r['prior_faithful'])]
        bysource=collections.defaultdict(list);families=collections.defaultdict(set)
        for r in rows:families[r['verb_family']].add(r['pair_id'])
        for r in sub:bysource[r['pair_id']].append(r)
        keep={f:sorted(sids) for f,sids in families.items() if all(len(bysource[sid])==160 for sid in sids)}
        result['cohorts'][stratum]=keep;details={f:{} for f in keep};vectors={}
        for label,mode,mappings in configs:
            for condition in ('gp','explicit_cue'):
                rr=[r for r in sub if r['mode']==mode and r['mapping_shift'] in mappings and r['condition']==condition]
                for kind in kinds:
                    for measure in ('correct','p_correct','choice_mass','greedy_label_valid','p_entailed','p_contradicted','p_undetermined'):
                        v={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                selected=[r for r in rr if r['pair_id']==sid and r['readout_kind']==kind];assert len(selected)==4*len(mappings)
                                obs.extend(100*(r['p_relation'][measure[2:]] if measure.startswith('p_') and measure!='p_correct' else r[measure]) for r in selected)
                            v[f]=float(np.mean(obs));details[f][f'{kind}_{measure}_{label}_{condition}']=v[f]
                        vectors[(kind,measure,label,condition)]=v;result['cells'][f'{stratum}/{kind}/{measure}/{label}/{condition}']=stat(v)
                for kind in ('same_actor_new_activity','other_actor_new_activity'):
                    signed={}
                    for f,sids in keep.items():
                        selected=[r for r in rr if r['pair_id'] in sids and r['readout_kind']==kind]
                        ref=[r for r in selected if r['role_evidence']=='reference_only'];np_only=[r for r in selected if r['role_evidence']=='initial_patient_only']
                        signed[f]=50*(np.mean([r['p_relation']['contradicted'] for r in ref])-np.mean([r['p_relation']['contradicted'] for r in np_only])+np.mean([r['p_relation']['entailed'] for r in np_only])-np.mean([r['p_relation']['entailed'] for r in ref]))
                    result['contrasts'][f'{stratum}/signed_role_carryover/{kind}/{label}/{condition}']=stat(signed)
                for endpoint in ('joint_four_states','joint_five_with_unknown_control'):
                    v={}
                    for f,sids in keep.items():
                        cases=collections.defaultdict(list)
                        for r in rr:
                            if r['pair_id'] in sids and (endpoint=='joint_five_with_unknown_control' or r['readout_kind']!='unrelated_unknown_control'):
                                cases[(r['pair_id'],r['role_evidence'],r['exclusion_style'],r['mapping_shift'])].append(r)
                        assert all(len(case)==(5 if endpoint=='joint_five_with_unknown_control' else 4) for case in cases.values())
                        v[f]=float(100*np.mean([all(r['correct'] for r in case) for case in cases.values()]));details[f][f'{endpoint}_{label}_{condition}']=v[f]
                    vectors[(endpoint,'correct',label,condition)]=v;result['cells'][f'{stratum}/{endpoint}/correct/{label}/{condition}']=stat(v)
                # Class-balanced macro accuracy; the unrelated-control U does
                # not inflate the primary four-state score or majority chance.
                v={f:float(np.mean([vectors[('old_supported','correct',label,condition)][f],vectors[('old_excluded','correct',label,condition)][f],.5*(vectors[('same_actor_new_activity','correct',label,condition)][f]+vectors[('other_actor_new_activity','correct',label,condition)][f])])) for f in keep}
                vectors[('class_macro','correct',label,condition)]=v;result['cells'][f'{stratum}/class_macro/correct/{label}/{condition}']=stat(v)
        for kind in (*kinds,'joint_four_states','joint_five_with_unknown_control','class_macro'):
            for c in ('gp','explicit_cue'):
                result['contrasts'][f'{stratum}/{kind}/repair_map0_minus_base_map0/{c}']=stat(diff(vectors[(kind,'correct','repair_map0',c)],vectors[(kind,'correct','base_map0',c)]))
            result['contrasts'][f'{stratum}/{kind}/GP_minus_cue/base_all_mappings']=stat(diff(vectors[(kind,'correct','base_all_mappings','gp')],vectors[(kind,'correct','base_all_mappings','explicit_cue')]))
        result['per_family'][stratum]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--repair',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.base,a.repair),indent=2)+'\n')
