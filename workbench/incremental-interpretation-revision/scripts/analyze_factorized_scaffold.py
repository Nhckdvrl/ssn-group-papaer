"""E46 preregistered three-factor contrasts, absolute directions, endpoint drift."""
import argparse
import collections
import itertools
import json
from pathlib import Path
from data import CACHE,sha
from aspect_reference import read_run
from analyze_source_ablation import stat,diff
from analyze_role_controls import average,analyze_responses


def analyze(cache,reviews):
    rows=[];configs=[]
    for identity,event in itertools.product((0,1),repeat=2):
        cfg,rr=read_run(cache/'runs'/f'E46-I{identity}E{event}')
        assert len(rr)==2304 and all(r['identity_intro_present']==identity and r['event_reification_present']==event for r in rr)
        configs.append(cfg);rows.extend(rr)
    assert len(rows)==len({r['item_id'] for r in rows})==9216
    for cfg in configs[1:]:
        for key in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','git_commit','torch','transformers'):
            assert cfg[key]==configs[0][key],key
    results=Path(__file__).resolve().parents[1]/'results'
    parent_cohorts=json.loads((results/'E31-summary.json').read_text())['probability']['cohorts']
    out=dict(experiment='E46',raw_tasks=9216,configs=configs,analysis_code_sha256=sha(Path(__file__)),
             units='bits',bootstrap_unit='12 verb families, two sources averaged before sampling',bootstrap_seed=20261005,bootstrap_draws=10000,
             probability=dict(cells={},contrasts={},cohorts={},per_family={}),
             interpretation='Three language manipulations change identity explicitness, discourse status, and event framing; not semantically equivalent or a world-probability assay.')
    sources=collections.defaultdict(set)
    for r in rows:sources[r['verb_family']].add(r['pair_id'])
    def cond(r):return (r['scaffold_cell'],r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old')
    conditions=sorted({cond(r) for r in rows})
    for cohort in ('all','eligible','grammar_common','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sorted(s) for f,s in sources.items() if all(counts[sid]==384 for sid in s)}
        if cohort in parent_cohorts:keep={f:s for f,s in keep.items() if f in parent_cohorts[cohort]}
        out['probability']['cohorts'][cohort]=keep
        ix={(r['pair_id'],cond(r),r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen};assert len(ix)==len(chosen)
        vectors={}
        def record(section,key,v):out['probability'][section][cohort+'/'+key]=stat(v);vectors[key]=v
        for c in conditions:
            name='/'.join(c);v={}
            for frame in ('activity','neutral_entity'):
                for role in ('source_patient_stated','other_patient_stated'):
                    vv={}
                    for family,sids in keep.items():
                        obs=[]
                        for sid in sids:
                            a=ix[sid,c,role,frame,'source_np'];b=ix[sid,c,role,frame,'other_source_np']
                            assert a['target_context_sha256']==b['target_context_sha256']
                            obs.append(b['target_total_bits']-a['target_total_bits'])
                        vv[family]=sum(obs)/len(obs)
                    v[role,frame]=vv;record('cells','M/'+name+'/'+role+'/'+frame,vv)
                v[frame]=diff(v['source_patient_stated',frame],v['other_patient_stated',frame]);record('cells','D/'+name+'/'+frame,v[frame])
            record('cells','J/'+name,diff(v['activity'],v['neutral_entity']))
        for cell in ('I'+str(i)+'R'+str(r)+'E'+str(e) for i,r,e in itertools.product((0,1),repeat=3)):
            for order in ('first','last'):
                for measure in ('activity','neutral_entity','J'):
                    def vector(actor,pred):return vectors[f'J/{cell}/{order}/{actor}/{pred}'] if measure=='J' else vectors[f'D/{cell}/{order}/{actor}/{pred}/{measure}']
                    record('contrasts',f'new_minus_old/{cell}/{order}/{measure}',diff(vector('other_actor','same_began'),vector('original_activity','old')))
                    record('contrasts',f'different_minus_same/{cell}/{order}/{measure}',diff(vector('other_actor','different_began'),vector('other_actor','same_began')))
            for measure in ('activity','neutral_entity','J'):
                for readout in ('old','new_same','new_different','new_minus_old','different_minus_same'):
                    obs=[]
                    for order in ('first','last'):
                        if readout in ('new_minus_old','different_minus_same'):
                            key=f'{readout}/{cell}/{order}/{measure}'
                        else:
                            actor='original_activity' if readout=='old' else 'other_actor';pred='old' if readout=='old' else 'same_began' if readout=='new_same' else 'different_began'
                            key=f'J/{cell}/{order}/{actor}/{pred}' if measure=='J' else f'D/{cell}/{order}/{actor}/{pred}/{measure}'
                        obs.append(vectors[key])
                    record('cells',f'order_average/{cell}/{readout}/{measure}',average(obs))
        # Main and interaction effects average the other factors, never choose
        # a winning cell. Each draw resamples already paired family differences.
        for readout in ('old','new_same','new_different','new_minus_old','different_minus_same'):
            for measure in ('activity','neutral_entity','J'):
                for factor_set in ((0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)):
                    signed=[]
                    for bits in itertools.product((0,1),repeat=3):
                        cell=f'I{bits[0]}R{bits[1]}E{bits[2]}';v=vectors[f'order_average/{cell}/{readout}/{measure}']
                        sign=(-1)**sum(1-bits[f] for f in factor_set)
                        signed.append({f:sign*x for f,x in v.items()})
                    denom=2**(3-len(factor_set))
                    fv={f:sum(v[f] for v in signed)/denom for f in keep}
                    name='x'.join(('identity','report','event')[f] for f in factor_set)
                    record('contrasts',f'factor/{name}/{readout}/{measure}',fv)
        out['probability']['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in keep}
    drift={}
    _,p45=read_run(cache/'runs/E45-probability');ix45={r['item_id']:r for r in p45}
    _,p44=read_run(cache/'runs/E44-no_protocol')
    def key(r):return (r['pair_id'],r['fact_realization'].replace('balanced_','plain_'),r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind'])
    ix44={key(r):r for r in p44}
    for cell,parent in [('I1R1E1','E45'),('I0R0E0','E44')]:
        dd=[]
        for r in rows:
            if r['scaffold_cell']!=cell:continue
            if parent=='E45':pr=ix45[r['parent_item_id']]
            else:
                k=(r['pair_id'],'plain_mention_'+r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind']);pr=ix44[k]
            assert r['sentence_sha256']==pr['sentence_sha256'] and r['target_context_sha256']==pr['target_context_sha256']
            dd.append(r['target_total_bits']-pr['target_total_bits'])
        assert len(dd)==1152
        drift[parent]=dict(tasks=len(dd),max_abs_target_bits=max(abs(x) for x in dd),mean_signed_target_bits=sum(dd)/len(dd))
    out['exact_endpoint_drift']=drift
    if reviews:out['native']=analyze_responses('E46',cache,reviews,out['probability']['cohorts'])
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='*',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews),indent=2)+'\n')
