"""E48 prespecified form matching and inventory contrasts, all cells retained."""
import argparse
import collections
import itertools
import json
from pathlib import Path
from data import CACHE, sha
from aspect_reference import read_run
from analyze_source_ablation import stat, diff
from analyze_role_controls import average, analyze_responses
from referent_form_roles import FORMS


def analyze(cache, reviews):
    rows, configs = [], []
    for fact, target in itertools.product(FORMS, repeat=2):
        cfg, rr = read_run(cache/'runs'/f'E48-{fact}-to-{target}')
        assert len(rr)==2304 and all(r['fact_form']==fact and r['target_form']==target for r in rr)
        rows.extend(rr);configs.append(cfg)
    assert len(rows)==len({r['item_id'] for r in rows})==9216
    for cfg in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','git_commit','torch','transformers'): assert cfg[k]==configs[0][k], k
    root=Path(__file__).resolve().parents[1]/'results'
    pc=json.loads((root/'E31-summary.json').read_text())['probability']['cohorts']
    out=dict(experiment='E48',raw_tasks=9216,configs=configs,analysis_code_sha256=sha(Path(__file__)),units='bits',bootstrap_seed=20261005,bootstrap_draws=10000,
             bootstrap_unit='12 verb families; two source items averaged before paired resampling',
             probability=dict(cells={},contrasts={},cohorts={},per_family={}),interpretation='Alias-linked forms, conditional string preference. Neither lexical invariance nor successful mapping QA establishes a latent entity state or world probability.')
    sf=collections.defaultdict(set)
    for r in rows:sf[r['verb_family']].add(r['pair_id'])
    def cond(r):return (r['fact_form'],r['target_form'],'I'+str(r['inventory_present']),r['fact_order'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old')
    conditions=sorted({cond(r) for r in rows})
    for cohort in ('all','eligible','grammar_common','nonpossessive11','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sorted(s) for f,s in sf.items() if all(counts[sid]==384 for sid in s)}
        if cohort in pc:keep={f:s for f,s in keep.items() if f in pc[cohort]}
        if cohort=='nonpossessive11':keep={f:s for f,s in keep.items() if f!='cuddled'}
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
        for fact,target,inv,order,measure in itertools.product(FORMS,FORMS,('I0','I1'),('first','last'),('activity','neutral_entity','J')):
            def v(actor,pred):
                base=f'{fact}/{target}/{inv}/{order}/{actor}/{pred}'
                return vectors['J/'+base] if measure=='J' else vectors['D/'+base+'/'+measure]
            record('contrasts',f'new_minus_old/{fact}/{target}/{inv}/{order}/{measure}',diff(v('other_actor','same_began'),v('original_activity','old')))
            record('contrasts',f'different_minus_same/{fact}/{target}/{inv}/{order}/{measure}',diff(v('other_actor','different_began'),v('other_actor','same_began')))
        for fact,target,inv,measure,readout in itertools.product(FORMS,FORMS,('I0','I1'),('activity','neutral_entity','J'),('old','new_same','new_different','new_minus_old','different_minus_same')):
            vv=[]
            for order in ('first','last'):
                if readout in ('new_minus_old','different_minus_same'):key=f'{readout}/{fact}/{target}/{inv}/{order}/{measure}'
                else:
                    actor='original_activity' if readout=='old' else 'other_actor';pred='old' if readout=='old' else 'same_began' if readout=='new_same' else 'different_began'
                    base=f'{fact}/{target}/{inv}/{order}/{actor}/{pred}';key='J/'+base if measure=='J' else 'D/'+base+'/'+measure
                vv.append(vectors[key])
            record('cells',f'order_average/{fact}/{target}/{inv}/{readout}/{measure}',average(vv))
        for inv,measure,readout in itertools.product(('I0','I1'),('activity','neutral_entity','J'),('old','new_same','new_different','new_minus_old','different_minus_same')):
            def vv(f,t):return vectors[f'order_average/{f}/{t}/{inv}/{readout}/{measure}']
            matching=diff(average([vv('name','name'),vv('description','description')]),average([vv('name','description'),vv('description','name')]))
            record('contrasts',f'matching/{inv}/{readout}/{measure}',matching)
            record('contrasts',f'fact_description_minus_name/{inv}/{readout}/{measure}',diff(average([vv('description',t) for t in FORMS]),average([vv('name',t) for t in FORMS])))
            record('contrasts',f'target_description_minus_name/{inv}/{readout}/{measure}',diff(average([vv(f,'description') for f in FORMS]),average([vv(f,'name') for f in FORMS])))
        for measure,readout in itertools.product(('activity','neutral_entity','J'),('old','new_same','new_different','new_minus_old','different_minus_same')):
            record('contrasts',f'matching/I1_minus_I0/{readout}/{measure}',diff(vectors[f'matching/I1/{readout}/{measure}'],vectors[f'matching/I0/{readout}/{measure}']))
            effects=[]
            for fact,target in itertools.product(FORMS,repeat=2):
                effect=diff(vectors[f'order_average/{fact}/{target}/I1/{readout}/{measure}'],vectors[f'order_average/{fact}/{target}/I0/{readout}/{measure}'])
                record('contrasts',f'inventory/{fact}/{target}/{readout}/{measure}',effect);effects.append(effect)
            record('contrasts',f'inventory/form_average/{readout}/{measure}',average(effects))
        out['probability']['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in keep}
    if reviews:out['native']=analyze_responses('E48',cache,reviews,out['probability']['cohorts'])
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='*',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews),indent=2)+'\n')
