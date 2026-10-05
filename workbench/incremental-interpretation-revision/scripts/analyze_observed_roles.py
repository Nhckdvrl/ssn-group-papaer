"""E49 full-response semantic judgments, paired role-congruence effects."""
import argparse
import collections
import itertools
import json
from pathlib import Path
from data import CACHE,sha
from analyze_source_ablation import stat,diff
from analyze_role_controls import average


def analyze(cache,reviews,experiment='E49'):
    annotations={}
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for a in j['reviews']:
            assert a['item_id'] not in annotations;annotations[a['item_id']]=a
    rows,configs=[],[]
    queries=('second','recap') if experiment=='E49' else ('pair_names','unanchored_recap','anchored_recap')
    total=3072 if experiment=='E49' else 4608
    for query,shard in itertools.product(queries,(0,1)):
        p=cache/'runs'/f'{experiment}-{query}-{shard}';cfg=json.loads((p/'config.json').read_text());assert sha(p/'generations.jsonl')==cfg['generations_sha256']
        rr=list(map(json.loads,(p/'generations.jsonl').read_text().splitlines()));assert len(rr)==768 and cfg['num_shards']==2 and cfg['shard_index']==shard
        configs.append(cfg);rows.extend(rr)
    assert len(rows)==len(annotations)==len({r['item_id'] for r in rows})==total
    for cfg in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','batch_size','git_commit','torch','transformers','max_new_tokens','num_shards'):assert configs[0][k]==cfg[k],k
    sf=collections.defaultdict(set)
    for r in rows:
        a=annotations[r['item_id']]
        for k in ('passage_sha256','question_sha256','answer_sha256'):assert a[k]==r[k]
        for k in ('old_correct','second_correct','joint_correct','unsupported_patient'):assert a[k] in (True,False,None)
        for k,gold,correct in [('old_answer_class','gold_old_answer_class','old_correct'),('second_answer_class','gold_answer_class','second_correct')]:
            if a[correct] is True and a[k] in ('source_candidate','other_candidate'):assert a[k]==r[gold],r['item_id']
        if r['query']!='second':
            expected=False if False in (a['old_correct'],a['second_correct']) else True if a['old_correct'] is True and a['second_correct'] is True else None
            assert a['joint_correct']==expected,r['item_id']
        r['response_audit']=a;sf[r['verb_family']].add(r['pair_id'])
    out=dict(experiment=experiment,native_tasks=total,configs=configs,analysis_code_sha256=sha(Path(__file__)),review_sha256=[sha(p) for p in reviews],
             bootstrap_draws=10000,bootstrap_seed=20261005,bootstrap_unit='12 verb families, two sources and two balanced patient assignments averaged before paired resampling',
             overall={k:dict(collections.Counter(str(a[k]) for a in annotations.values())) for k in ('old_correct','second_correct','joint_correct','unsupported_patient','certainty')},
             cohorts={},cells={},contrasts={},uncertainty_bounds={},per_family={},interpretation='Observed roles, independently audited actual answers. Congruence crosses old/new patient assignments. No latent-state or world-probability claim.')
    components=tuple(f'{event}_{part}_correct' for event in ('old','second') for part in ('actor','action','patient'))
    out['component_counts']={k:dict(collections.Counter(str(a.get(k)) for a in annotations.values())) for k in components}
    def condition(r):return (r['query'],r['second_fact_form'],'I'+str(r['inventory_present']),r['predicate'],r['congruence'],r['mode'])
    conditions=sorted({condition(r) for r in rows})
    for cohort in ('all','eligible','grammar_common','nonpossessive11'):
        chosen=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen);keep={f:sorted(s) for f,s in sf.items() if all(counts[sid]==total//24 for sid in s)}
        if cohort=='nonpossessive11':keep={f:s for f,s in keep.items() if f!='cuddled'}
        out['cohorts'][cohort]=keep;vectors={}
        def record(section,key,v):out[section][cohort+'/'+key]=stat(v);vectors[key]=v
        # Uncertainty sensitivity retains every source family. Lower/upper mean
        # treat unjudged answers as incorrect/correct, not as new semantic gold.
        def pool(query,mode,metric,congruence=None,predicate=None):
            rr=[r for r in chosen if r['query']==query and r['mode']==mode and (congruence is None or r['congruence']==congruence) and (predicate is None or r['predicate']==predicate)]
            lo,hi={},{}
            for f,sids in keep.items():
                obs=[r['response_audit'].get(metric) for r in rr if r['pair_id'] in sids]
                assert len(obs)==(64 if congruence is None else 32)//(2 if predicate is not None else 1)
                lo[f]=100*sum(x is True for x in obs)/len(obs);hi[f]=100*sum(x is not False for x in obs)/len(obs)
            return lo,hi
        for query,mode in itertools.product(queries,('base','priority')):
            metrics=('second_correct','unsupported_patient') if query=='second' else ('old_correct','second_correct','joint_correct','unsupported_patient')
            if all(k in r['response_audit'] for r in chosen if r['query']==query for k in components):metrics=metrics+components
            for metric in metrics:
                lo,hi=pool(query,mode,metric)
                record('uncertainty_bounds',f'pooled_lower/{query}/{mode}/{metric}',lo);record('uncertainty_bounds',f'pooled_upper/{query}/{mode}/{metric}',hi)
                lc,uc=pool(query,mode,metric,'congruent');li,ui=pool(query,mode,metric,'incongruent')
                record('uncertainty_bounds',f'pooled_congruence_lower/{query}/{mode}/{metric}',diff(lc,ui));record('uncertainty_bounds',f'pooled_congruence_upper/{query}/{mode}/{metric}',diff(uc,li))
                for cg in ('congruent','incongruent'):
                    ls,us=pool(query,mode,metric,cg,'same_began');ld,ud=pool(query,mode,metric,cg,'different_began')
                    record('uncertainty_bounds',f'pooled_different_minus_same_lower/{query}/{cg}/{mode}/{metric}',diff(ld,us));record('uncertainty_bounds',f'pooled_different_minus_same_upper/{query}/{cg}/{mode}/{metric}',diff(ud,ls))
        for c in conditions:
            rr=[r for r in chosen if condition(r)==c];query=c[0]
            metrics=('second_correct','unsupported_patient') if query=='second' else ('old_correct','second_correct','joint_correct','unsupported_patient')
            for metric in metrics:
                v={};lower={};upper={}
                for f,sids in keep.items():
                    obs=[r['response_audit'][metric] for r in rr if r['pair_id'] in sids];assert len(obs)==4
                    lower[f]=100*sum(x is True for x in obs)/len(obs);upper[f]=100*sum(x is not False for x in obs)/len(obs)
                    if None not in obs:v[f]=100*sum(obs)/len(obs)
                record('cells','/'.join(c)+'/'+metric,v)
                record('uncertainty_bounds','lower/'+'/'.join(c)+'/'+metric,lower);record('uncertainty_bounds','upper/'+'/'.join(c)+'/'+metric,upper)
        for query,form,inv,pred,mode in itertools.product(queries,('name','description'),('I0','I1'),('same_began','different_began'),('base','priority')):
            metrics=('second_correct','unsupported_patient') if query=='second' else ('old_correct','second_correct','joint_correct','unsupported_patient')
            for metric in metrics:
                v1=vectors[f'{query}/{form}/{inv}/{pred}/congruent/{mode}/{metric}'];v0=vectors[f'{query}/{form}/{inv}/{pred}/incongruent/{mode}/{metric}']
                keys=v1.keys()&v0.keys();record('contrasts',f'congruent_minus_incongruent/{query}/{form}/{inv}/{pred}/{mode}/{metric}',diff({f:v1[f] for f in keys},{f:v0[f] for f in keys}))
                prefix=f'{query}/{form}/{inv}/{pred}'
                record('uncertainty_bounds',f'congruence_lower/{prefix}/{mode}/{metric}',diff(vectors[f'lower/{prefix}/congruent/{mode}/{metric}'],vectors[f'upper/{prefix}/incongruent/{mode}/{metric}']))
                record('uncertainty_bounds',f'congruence_upper/{prefix}/{mode}/{metric}',diff(vectors[f'upper/{prefix}/congruent/{mode}/{metric}'],vectors[f'lower/{prefix}/incongruent/{mode}/{metric}']))
        # Averaging is paired; retain each dimension's cells instead of picking errors.
        for query,mode in itertools.product(queries,('base','priority')):
            metrics=('second_correct','unsupported_patient') if query=='second' else ('old_correct','second_correct','joint_correct','unsupported_patient')
            for metric in metrics:
                vv=[vectors[f'congruent_minus_incongruent/{query}/{form}/{inv}/{pred}/{mode}/{metric}'] for form,inv,pred in itertools.product(('name','description'),('I0','I1'),('same_began','different_began'))]
                keys=set.intersection(*(set(v) for v in vv));record('contrasts',f'congruent_minus_incongruent/form_inventory_predicate_average/{query}/{mode}/{metric}',average([{f:v[f] for f in keys} for v in vv]))
                for form in ('name','description'):
                    vv=[vectors[f'congruent_minus_incongruent/{query}/{form}/{inv}/{pred}/{mode}/{metric}'] for inv,pred in itertools.product(('I0','I1'),('same_began','different_began'))]
                    keys=set.intersection(*(set(v) for v in vv));record('contrasts',f'congruent_minus_incongruent/inventory_predicate_average/{query}/{form}/{mode}/{metric}',average([{f:v[f] for f in keys} for v in vv]))
                a=vectors[f'congruent_minus_incongruent/inventory_predicate_average/{query}/description/{mode}/{metric}'];b=vectors[f'congruent_minus_incongruent/inventory_predicate_average/{query}/name/{mode}/{metric}'];keys=a.keys()&b.keys()
                record('contrasts',f'congruence_description_minus_name/{query}/{mode}/{metric}',diff({f:a[f] for f in keys},{f:b[f] for f in keys}))
        for c in conditions:
            if c[-1]!='priority':continue
            metrics=('second_correct','unsupported_patient') if c[0]=='second' else ('old_correct','second_correct','joint_correct','unsupported_patient')
            for metric in metrics:
                a=vectors['/'.join(c)+'/'+metric];b=vectors['/'.join(c[:-1]+('base',))+'/'+metric];keys=a.keys()&b.keys()
                record('contrasts','priority_minus_base/'+'/'.join(c[:-1])+'/'+metric,diff({f:a[f] for f in keys},{f:b[f] for f in keys}))
        for query,mode,metric in itertools.product(queries,('base','priority'),('second_correct','unsupported_patient')):
            def cg(form,inv,pred):return vectors[f'congruent_minus_incongruent/{query}/{form}/{inv}/{pred}/{mode}/{metric}']
            for dim,label in ((1,'inventory_I1_minus_I0'),(2,'different_minus_same')):
                vv=[]
                for form in ('name','description'):
                    levels=('same_began','different_began') if dim==1 else ('I0','I1')
                    for other in levels:
                        a=cg(form,'I1',other) if dim==1 else cg(form,other,'different_began')
                        b=cg(form,'I0',other) if dim==1 else cg(form,other,'same_began')
                        keys=a.keys()&b.keys();vv.append(diff({f:a[f] for f in keys},{f:b[f] for f in keys}))
                keys=set.intersection(*(set(v) for v in vv));record('contrasts',f'congruence_{label}/{query}/{mode}/{metric}',average([{f:v[f] for f in keys} for v in vv]))
        out['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items() if f in v} for f in keep}
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--experiment',choices=['E49','E50'],default='E49');p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews,a.experiment),indent=2)+'\n')
