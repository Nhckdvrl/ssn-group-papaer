"""E26 paired scoped access and source final interpretation, label/mass reported."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from data import sha
from infer import clean_word


def analyze(paths):
    assert len(paths)==2;rows=[];cfgs=[]
    for p in paths:
        cfg=json.loads((p/'config.json').read_text());assert cfg['predictions_sha256']==sha(p/'predictions.jsonl')
        rr=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()));assert len(rr)==1536==cfg['task_count']
        cfgs.append(cfg);rows.extend(rr)
    for k in ('model_manifest','dtype','attention','seed','torch','transformers','batch_size','frozen','git_commit','code_sha256','data_sha256'):assert cfgs[0][k]==cfgs[1][k],k
    assert len(rows)==3072 and len({(r['item_id'],r['mode']) for r in rows})==3072
    assert {r['mode'] for r in rows}=={'base','repair'}
    for r in rows:
        r['greedy_label_valid']=clean_word(r['greedy_token']) in ('yes','no')
        r['greedy_label_correct']=None if r['gold'] is None else int(clean_word(r['greedy_token'])==r['gold'].lower())
    result=dict(experiment='E26',physical_tasks=3072,source_items=24,verb_families=12,bootstrap_unit='verb family after averaging its two source items',
                bootstrap_draws=10000,bootstrap_seed=20261005,units='percentage points',
                interpretation='Native answer-label agreement with independently audited scope compatibility and original matrix propositions. Joint access does not prove an internal event graph or erase portable language-prediction traces.',
                predictions_sha256={c['recovery_mode']:c['predictions_sha256'] for c in cfgs},analysis_code_sha256=sha(Path(__file__)),
                actual_gpu_hours=sum(c['gpu_hours'] for c in cfgs),cells={},contrasts={},per_family={},cohorts={},overall={})
    result['overall']=dict(clear_gold_tasks=sum(r['gold'] is not None for r in rows),greedy_label_valid=sum(r['greedy_label_valid'] for r in rows),
                           mean_choice_mass=float(np.mean([r['choice_mass'] for r in rows])),min_choice_mass=min(r['choice_mass'] for r in rows))
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,verb_families=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    def metric(r,m):
        if m=='correct' or m=='greedy_label_correct':return 100*r[m]
        return 100*r[m]
    for stratum in ('clear_gold','prior_faithful_clear_gold'):
        sub=[r for r in rows if r['gold'] is not None and (stratum=='clear_gold' or r['prior_faithful'])]
        bysource=collections.defaultdict(list)
        for r in sub:bysource[r['pair_id']].append(r)
        families=collections.defaultdict(set)
        for r in rows:families[r['verb_family']].add(r['pair_id'])
        # Complete original eight-readout factorial, two modes, both conditions,
        # role facts and styles: 128 tasks per original source, before outcomes.
        keep={f:sorted(sids) for f,sids in families.items() if all(len(bysource[sid])==128 for sid in sids)}
        result['cohorts'][stratum]=keep;vectors={};details={f:{} for f in keep}
        for mode in ('base','repair'):
            for condition in ('gp','explicit_cue'):
                rr=[r for r in sub if r['mode']==mode and r['condition']==condition]
                for endpoint in ('original_activity','same_actor_new_activity','other_actor_new_activity','source_final','source_actor_swap','joint_all_eight'):
                    for m in ('correct','p_correct','choice_mass','greedy_label_correct','greedy_label_valid'):
                        if endpoint=='joint_all_eight' and m not in ('correct','greedy_label_correct'):continue
                        v={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                source=[r for r in rr if r['pair_id']==sid]
                                if endpoint=='joint_all_eight':
                                    cases=collections.defaultdict(list)
                                    for r in source:cases[(r['role_evidence'],r['exclusion_style'])].append(r)
                                    assert len(cases)==4 and all(len(x)==8 for x in cases.values())
                                    obs.extend(100*int(all(r[m] for r in case)) for case in cases.values())
                                else:
                                    selected=[r for r in source if r['scope']==endpoint or r['readout_kind']==endpoint]
                                    assert len(selected)==(8 if endpoint in ('original_activity','same_actor_new_activity','other_actor_new_activity') else 4)
                                    obs.extend(metric(r,m) for r in selected)
                            v[f]=float(np.mean(obs));details[f][f'{endpoint}_{m}_{mode}_{condition}']=v[f]
                        vectors[(endpoint,m,mode,condition)]=v;result['cells'][f'{stratum}/{endpoint}/{m}/{mode}/{condition}']=stat(v)
        for endpoint in ('original_activity','same_actor_new_activity','other_actor_new_activity','source_final','source_actor_swap','joint_all_eight'):
            for m in ('correct','p_correct','choice_mass','greedy_label_correct','greedy_label_valid'):
                if endpoint=='joint_all_eight' and m not in ('correct','greedy_label_correct'):continue
                for mode in ('base','repair'):
                    result['contrasts'][f'{stratum}/{endpoint}/{m}/GP_minus_cue/{mode}']=stat(diff(vectors[(endpoint,m,mode,'gp')],vectors[(endpoint,m,mode,'explicit_cue')]))
                for c in ('gp','explicit_cue'):
                    result['contrasts'][f'{stratum}/{endpoint}/{m}/repair_minus_base/{c}']=stat(diff(vectors[(endpoint,m,'repair',c)],vectors[(endpoint,m,'base',c)]))
        result['per_family'][stratum]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.runs),indent=2)+'\n')
