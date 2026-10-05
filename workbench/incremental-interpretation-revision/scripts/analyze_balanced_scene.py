"""E44 balanced natural scenes; absolute role directions and neutral separately."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE,sha
from aspect_reference import read_run
from analyze_source_ablation import stat,diff
from analyze_role_controls import average


def analyze(cache,reviews):
    configs=[];rows=[]
    for policy,n in [('no_protocol',1920),('ready',1536)]:
        c,rr=read_run(cache/'runs'/f'E44-{policy}');assert len(rr)==n and all(r['scene_policy']==policy for r in rr)
        configs.append(c);rows.extend(rr)
    for k in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','torch','transformers','git_commit'):
        assert configs[0][k]==configs[1][k],k
    assert len(rows)==len({r['item_id'] for r in rows})==3456
    parent=Path(__file__).resolve().parents[1]/'results/E43-summary.json';pp=json.loads(parent.read_text())['probability']
    out=dict(experiment='E44',raw_tasks=3456,configs=configs,analysis_code_sha256=sha(Path(__file__)),parent_sha256=sha(parent),
             bootstrap_unit='12 verb families, two sources averaged before sampling',bootstrap_draws=10000,bootstrap_seed=20261005,
             probability=dict(units='bits',cells={},contrasts={},cohorts={},per_family={}))
    def condition(r):return (r['fact_realization'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old',r['scene_policy'])
    conditions=sorted({condition(r) for r in rows})
    for cohort,keep0 in pp['cohorts'].items():
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sids for f,sids in keep0.items() if all(counts[s]==144 for s in sids)}
        out['probability']['cohorts'][cohort]=keep
        ix={(r['pair_id'],condition(r),r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen};assert len(ix)==len(chosen)
        vectors={}
        def record(section,key,v):out['probability'][section][cohort+'/'+key]=stat(v);vectors[key]=v
        for form,actor,pred,policy in conditions:
            c=(form,actor,pred,policy);v={}
            for frame in ('activity','neutral_entity'):
                for role in ('source_patient_stated','other_patient_stated'):
                    rv={}
                    for f,sids in keep.items():
                        obs=[]
                        for sid in sids:
                            a=ix[sid,c,role,frame,'source_np'];b=ix[sid,c,role,frame,'other_source_np']
                            assert a['target_context_sha256']==b['target_context_sha256']
                            obs.append(b['target_total_bits']-a['target_total_bits'])
                        rv[f]=float(np.mean(obs))
                    v[role,frame]=rv
                v[frame]=diff(v['source_patient_stated',frame],v['other_patient_stated',frame]);record('cells',f'D/{form}/{actor}/{pred}/{policy}/{frame}',v[frame])
            jv=diff(v['activity'],v['neutral_entity']);record('cells',f'J/{form}/{actor}/{pred}/{policy}',jv)
            if policy=='no_protocol':
                pv={f:pp['per_family'][cohort][f][f'J/minimal_plain/{actor}/{pred}'] for f in keep}
                record('contrasts',f'balanced_minus_single_mention/{form}/{actor}/{pred}/J',diff(jv,pv))
        forms=('balanced_mention_first','balanced_mention_last')
        for actor in ('same_actor','other_actor'):
            for pred in ('same_began','different_began'):
                for form in forms:
                    for measure in ('activity','neutral_entity','J'):
                        def vec(policy):return vectors[f'J/{form}/{actor}/{pred}/{policy}'] if measure=='J' else vectors[f'D/{form}/{actor}/{pred}/{policy}/{measure}']
                        record('contrasts',f'ready_minus_no_protocol/{form}/{actor}/{pred}/{measure}',diff(vec('ready'),vec('no_protocol')))
                for policy in ('no_protocol','ready'):
                    for measure in ('activity','neutral_entity','J'):
                        def vf(form):return vectors[f'J/{form}/{actor}/{pred}/{policy}'] if measure=='J' else vectors[f'D/{form}/{actor}/{pred}/{policy}/{measure}']
                        record('cells',f'{measure}/order_average/{actor}/{pred}/{policy}',average([vf(form) for form in forms]))
                        record('contrasts',f'last_minus_first/{actor}/{pred}/{policy}/{measure}',diff(vf(forms[1]),vf(forms[0])))
            for form in forms:
                for policy in ('no_protocol','ready'):
                    record('contrasts',f'different_minus_same/{form}/{actor}/{policy}/J',diff(vectors[f'J/{form}/{actor}/different_began/{policy}'],vectors[f'J/{form}/{actor}/same_began/{policy}']))
        out['probability']['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in keep}
    if reviews:
        annotations={}
        for path in reviews:
            j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
            for a in j['reviews']:
                assert a['item_id'] not in annotations;annotations[a['item_id']]=a
        native_rows=[];native_configs=[]
        for query,n in [('current',384),('availability',192)]:
            path=cache/'runs'/f'E44-{query}';cfg=json.loads((path/'config.json').read_text());assert sha(path/'generations.jsonl')==cfg['generations_sha256']
            rr=list(map(json.loads,(path/'generations.jsonl').read_text().splitlines()));assert len(rr)==n
            native_rows.extend(rr);native_configs.append(cfg)
        assert len(annotations)==len(native_rows)==576
        for r in native_rows:
            a=annotations[r['item_id']]
            for k in ('passage_sha256','question_sha256','answer_sha256'):assert a[k]==r[k]
            if a['correct'] is True and a['answer_class'] in ('source_candidate','other_candidate','both_ready'):
                assert a['answer_class']==r['gold_answer_class'],r['item_id']
        native=dict(configs=native_configs,review_sha256=[sha(p) for p in reviews],certainty=dict(collections.Counter(a['certainty'] for a in annotations.values())),
                    answer_classes=dict(collections.Counter(a['answer_class'] for a in annotations.values())),correct=sum(a['correct'] is True for a in annotations.values()),cells={},contrasts={})
        for cohort,keep in out['probability']['cohorts'].items():
            for form in forms:
                for query,policy in [('current','no_protocol'),('current','ready'),('availability','ready')]:
                    vals={}
                    for mode in ('base','priority'):
                        v={}
                        for f,sids in keep.items():
                            obs=[annotations[r['item_id']]['correct'] for r in native_rows if r['pair_id'] in sids and r['fact_realization']==form and r['scene_policy']==policy and r['query']==query and r['mode']==mode]
                            assert len(obs)==4
                            if None not in obs:v[f]=100*float(np.mean(obs))
                        vals[mode]=v;native['cells'][f'{cohort}/{form}/{query}/{policy}/{mode}/correct']=stat(v)
                    if vals['base'].keys()==vals['priority'].keys():native['contrasts'][f'{cohort}/{form}/{query}/{policy}/priority_minus_base']=stat(diff(vals['priority'],vals['base']))
        out['native']=native
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='*',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews),indent=2)+'\n')
