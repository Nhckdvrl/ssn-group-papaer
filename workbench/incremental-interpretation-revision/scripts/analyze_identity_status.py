"""E47 predeclared assertion/quotation/inventory contrasts and endpoint checks."""
import argparse
import collections
import itertools
import json
from pathlib import Path
from data import CACHE,sha
from aspect_reference import read_run
from analyze_source_ablation import stat,diff
from analyze_role_controls import average,analyze_responses
from identity_status_roles import FORMS


def analyze(cache,reviews):
    rows=[];configs=[]
    for form in FORMS:
        cfg,rr=read_run(cache/'runs'/('E47-'+form));assert len(rr)==2304 and all(r['identity_form']==form for r in rr)
        rows.extend(rr);configs.append(cfg)
    assert len(rows)==len({r['item_id'] for r in rows})==9216
    for cfg in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','git_commit','torch','transformers'):assert cfg[k]==configs[0][k],k
    root=Path(__file__).resolve().parents[1]/'results';pc=json.loads((root/'E31-summary.json').read_text())['probability']['cohorts']
    out=dict(experiment='E47',raw_tasks=9216,configs=configs,analysis_code_sha256=sha(Path(__file__)),units='bits',bootstrap_seed=20261005,bootstrap_draws=10000,
             bootstrap_unit='12 verb families, two sources averaged before sampling',probability=dict(cells={},contrasts={},cohorts={},per_family={}),
             interpretation='Conditional string preference under linguistic framing; quoted body matches assertion, wrapper and inventory differ in length and discourse status. Not world probability.')
    sf=collections.defaultdict(set)
    for r in rows:sf[r['verb_family']].add(r['pair_id'])
    def cond(r):return (r['identity_form'],'E'+str(r['event_reification_present']),r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old')
    conditions=sorted({cond(r) for r in rows})
    for cohort in ('all','eligible','grammar_common','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen);keep={f:sorted(s) for f,s in sf.items() if all(counts[sid]==384 for sid in s)}
        if cohort in pc:keep={f:s for f,s in keep.items() if f in pc[cohort]}
        out['probability']['cohorts'][cohort]=keep
        ix={(r['pair_id'],cond(r),r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen};assert len(ix)==len(chosen)
        vectors={}
        def record(section,key,v):out['probability'][section][cohort+'/'+key]=stat(v);vectors[key]=v
        for c in conditions:
            name='/'.join(c);v={}
            for frame in ('activity','neutral_entity'):
                for role in ('source_patient_stated','other_patient_stated'):
                    vv={}
                    for f,sids in keep.items():
                        obs=[]
                        for sid in sids:
                            a=ix[sid,c,role,frame,'source_np'];b=ix[sid,c,role,frame,'other_source_np'];assert a['target_context_sha256']==b['target_context_sha256']
                            obs.append(b['target_total_bits']-a['target_total_bits'])
                        vv[f]=sum(obs)/len(obs)
                    v[role,frame]=vv;record('cells','M/'+name+'/'+role+'/'+frame,vv)
                v[frame]=diff(v['source_patient_stated',frame],v['other_patient_stated',frame]);record('cells','D/'+name+'/'+frame,v[frame])
            record('cells','J/'+name,diff(v['activity'],v['neutral_entity']))
        for form,event,order in itertools.product(FORMS,('E0','E1'),('first','last')):
            for measure in ('activity','neutral_entity','J'):
                def v(actor,pred):return vectors[f'J/{form}/{event}/{order}/{actor}/{pred}'] if measure=='J' else vectors[f'D/{form}/{event}/{order}/{actor}/{pred}/{measure}']
                record('contrasts',f'new_minus_old/{form}/{event}/{order}/{measure}',diff(v('other_actor','same_began'),v('original_activity','old')))
                record('contrasts',f'different_minus_same/{form}/{event}/{order}/{measure}',diff(v('other_actor','different_began'),v('other_actor','same_began')))
        for form,event,measure,readout in itertools.product(FORMS,('E0','E1'),('activity','neutral_entity','J'),('old','new_same','new_different','new_minus_old','different_minus_same')):
            vv=[]
            for order in ('first','last'):
                if readout in ('new_minus_old','different_minus_same'):key=f'{readout}/{form}/{event}/{order}/{measure}'
                else:
                    actor='original_activity' if readout=='old' else 'other_actor';pred='old' if readout=='old' else 'same_began' if readout=='new_same' else 'different_began'
                    key=f'J/{form}/{event}/{order}/{actor}/{pred}' if measure=='J' else f'D/{form}/{event}/{order}/{actor}/{pred}/{measure}'
                vv.append(vectors[key])
            record('cells',f'order_average/{form}/{event}/{readout}/{measure}',average(vv))
        for plus,minus in [('quoted_unverified','asserted'),('name_inventory','absent'),('quoted_unverified','name_inventory'),('asserted','absent')]:
            name=plus+'_minus_'+minus
            for measure,readout in itertools.product(('activity','neutral_entity','J'),('old','new_same','new_different','new_minus_old','different_minus_same')):
                vv=[]
                for event in ('E0','E1'):
                    dv=diff(vectors[f'order_average/{plus}/{event}/{readout}/{measure}'],vectors[f'order_average/{minus}/{event}/{readout}/{measure}'])
                    record('contrasts',f'{name}/{event}/order_average/{readout}/{measure}',dv);vv.append(dv)
                    for order in ('first','last'):
                        if readout in ('new_minus_old','different_minus_same'):
                            def rk(form):return f'{readout}/{form}/{event}/{order}/{measure}'
                        else:
                            actor='original_activity' if readout=='old' else 'other_actor';pred='old' if readout=='old' else 'same_began' if readout=='new_same' else 'different_began'
                            def rk(form):return f'J/{form}/{event}/{order}/{actor}/{pred}' if measure=='J' else f'D/{form}/{event}/{order}/{actor}/{pred}/{measure}'
                        record('contrasts',f'{name}/{event}/{order}/{readout}/{measure}',diff(vectors[rk(plus)],vectors[rk(minus)]))
                record('contrasts',f'{name}/event_average/order_average/{readout}/{measure}',average(vv))
                record('contrasts',f'{name}/E1_minus_E0/{readout}/{measure}',diff(vv[1],vv[0]))
        out['probability']['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in keep}
    prior=[]
    for i,e in itertools.product((0,1),repeat=2):
        _,rr=read_run(cache/'runs'/f'E46-I{i}E{e}');prior.extend(rr)
    def frozen_key(r):return (r['pair_id'],r['scaffold_cell'],r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind'])
    pi={frozen_key(r):r for r in prior};out['exact_endpoint_drift']={}
    for form in ('absent','asserted'):
        dd=[]
        for r in rows:
            if r['identity_form']!=form:continue
            cell=f'I{int(form=="asserted")}R0E{r["event_reification_present"]}'
            k=(r['pair_id'],cell,r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind']);pr=pi[k]
            assert r['sentence_sha256']==pr['sentence_sha256'] and r['target_context_sha256']==pr['target_context_sha256'];dd.append(r['target_total_bits']-pr['target_total_bits'])
        assert len(dd)==2304
        out['exact_endpoint_drift'][form]=dict(tasks=len(dd),max_abs_target_bits=max(abs(x) for x in dd),mean_signed_target_bits=sum(dd)/len(dd))
    if reviews:out['native']=analyze_responses('E47',cache,reviews,out['probability']['cohorts'])
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='*',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews),indent=2)+'\n')
