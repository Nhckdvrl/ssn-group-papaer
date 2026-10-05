"""E41 paired completion/readiness contrasts; preserve all actors and actions."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE, sha
from aspect_reference import read_run
from analyze_source_ablation import stat, diff
from analyze_role_controls import average
from availability_roles import POLICIES


def analyze(cache, reviews):
    rows,configs=[],[]
    for policy in POLICIES:
        cfg,rr=read_run(cache/'runs'/f'E41-{policy}');assert len(rr)==1536
        assert all(r['availability_policy']==policy for r in rr)
        configs.append(cfg);rows.extend(rr)
    for c in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','torch','transformers','git_commit'):
            assert c[k]==configs[0][k],k
    assert len(rows)==len({r['item_id'] for r in rows})==4608
    parent=Path(__file__).resolve().parents[1]/'results/E40-summary.json';pp=json.loads(parent.read_text())['probability']
    out=dict(experiment='E41',raw_tasks=4608,configs=configs,analysis_code_sha256=sha(Path(__file__)),parent_sha256=sha(parent),
             bootstrap_unit='12 verb families, two sources averaged before resampling',bootstrap_draws=10000,bootstrap_seed=20261005,
             probability=dict(units='bits',cells={},contrasts={},cohorts={},per_family={}))
    conditions=sorted({(r['fact_realization'],r['readout_actor_mode'],r['boundary_marker']) for r in rows})
    for cohort,keep0 in pp['cohorts'].items():
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sids for f,sids in keep0.items() if all(counts[s]==192 for s in sids)}
        out['probability']['cohorts'][cohort]=keep
        ix={(r['pair_id'],r['fact_realization'],r['readout_actor_mode'],r['boundary_marker'],r['availability_policy'],r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen}
        assert len(ix)==len(chosen);vectors={}
        def record(section,key,v):out['probability'][section][cohort+'/'+key]=stat(v);vectors[key]=v
        for form,actor,pred in conditions:
            for policy in POLICIES:
                v={}
                for frame in ('activity','neutral_entity'):
                    for role in ('source_patient_stated','other_patient_stated'):
                        rv={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                a=ix[sid,form,actor,pred,policy,role,frame,'source_np'];b=ix[sid,form,actor,pred,policy,role,frame,'other_source_np']
                                assert a['target_context_sha256']==b['target_context_sha256']
                                obs.append(b['target_total_bits']-a['target_total_bits'])
                            rv[f]=float(np.mean(obs))
                        v[role,frame]=rv
                    v[frame]=diff(v['source_patient_stated',frame],v['other_patient_stated',frame])
                    record('cells',f'D/{form}/{actor}/{pred}/{policy}/{frame}',v[frame])
                jv=diff(v['activity'],v['neutral_entity']);record('cells',f'J/{form}/{actor}/{pred}/{policy}',jv)
                pv={f:pp['per_family'][cohort][f][f'J/{form}/{actor}/{pred}'] for f in keep}
                record('contrasts',f'minus_no_protocol/{form}/{actor}/{pred}/{policy}',diff(jv,pv))
            for measure in ('activity','neutral_entity','J'):
                def vector(policy):return vectors[f'J/{form}/{actor}/{pred}/{policy}'] if measure=='J' else vectors[f'D/{form}/{actor}/{pred}/{policy}/{measure}']
                for name,a,b in [('ready_minus_ended','ended_and_ready','ended_only'),('ended_minus_unknown','ended_only','status_unknown'),('ready_minus_unknown','ended_and_ready','status_unknown')]:
                    record('contrasts',f'{name}/{form}/{actor}/{pred}/{measure}',diff(vector(a),vector(b)))
        for actor in ('same_actor','other_actor'):
            for pred in ('same_began','different_began'):
                for policy in POLICIES:
                    record('cells',f'J/order_average/{actor}/{pred}/{policy}',average([vectors[f'J/{form}/{actor}/{pred}/{policy}'] for form in ('plain_mention_first','plain_mention_last')]))
                for name,a,b in [('ready_minus_ended','ended_and_ready','ended_only'),('ended_minus_unknown','ended_only','status_unknown')]:
                    record('contrasts',f'{name}/order_average/{actor}/{pred}/J',diff(vectors[f'J/order_average/{actor}/{pred}/{a}'],vectors[f'J/order_average/{actor}/{pred}/{b}']))
            for form in ('plain_mention_first','plain_mention_last'):
                for policy in POLICIES:
                    record('contrasts',f'different_minus_same/{form}/{actor}/{policy}/J',diff(vectors[f'J/{form}/{actor}/different_began/{policy}'],vectors[f'J/{form}/{actor}/same_began/{policy}']))
        out['probability']['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in keep}
    if reviews:
        annotations={}
        for p in reviews:
            j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
            for a in j['reviews']:
                assert a['item_id'] not in annotations;annotations[a['item_id']]=a
        nr=[];nc=[]
        for query in ('current','availability'):
            p=cache/'runs'/f'E41-{query}';cfg=json.loads((p/'config.json').read_text());assert sha(p/'generations.jsonl')==cfg['generations_sha256']
            rr=list(map(json.loads,(p/'generations.jsonl').read_text().splitlines()));assert len(rr)==576
            nr.extend(rr);nc.append(cfg)
        assert len(annotations)==len(nr)==1152
        for r in nr:
            a=annotations[r['item_id']]
            for k in ('passage_sha256','question_sha256','answer_sha256'):assert a[k]==r[k]
            if a['correct'] is True and a['answer_class'] in ('source_candidate','other_candidate','both_ready','unspecified'):
                assert a['answer_class']==r['gold_answer_class'],r['item_id']
        native=dict(configs=nc,review_sha256=[sha(p) for p in reviews],certainty=dict(collections.Counter(a['certainty'] for a in annotations.values())),
                    answer_classes=dict(collections.Counter(a['answer_class'] for a in annotations.values())),correct=sum(a['correct'] is True for a in annotations.values()),cells={},contrasts={})
        for cohort,keep in out['probability']['cohorts'].items():
            for form in ('plain_mention_first','plain_mention_last'):
                for policy in POLICIES:
                    for query in ('current','availability'):
                        v={}
                        for mode in ('base','priority'):
                            rv={}
                            for f,sids in keep.items():
                                obs=[annotations[r['item_id']]['correct'] for r in nr if r['pair_id'] in sids and r['fact_realization']==form and r['availability_policy']==policy and r['query']==query and r['mode']==mode]
                                assert len(obs)==4
                                if None not in obs:rv[f]=100*float(np.mean(obs))
                            v[mode]=rv;native['cells'][f'{cohort}/{form}/{policy}/{query}/{mode}/correct']=stat(rv)
                        if v['base'].keys()==v['priority'].keys():native['contrasts'][f'{cohort}/{form}/{policy}/{query}/priority_minus_base']=stat(diff(v['priority'],v['base']))
        out['native']=native
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='*',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews),indent=2)+'\n')
