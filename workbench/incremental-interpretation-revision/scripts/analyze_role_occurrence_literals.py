"""POST-HOC E51 literal-schema coverage, not an external semantic audit."""
import argparse
import collections
import itertools
import json
import re
from pathlib import Path
from data import CACHE,sha
from analyze_source_ablation import stat,diff

def parse(r):
    text=r['answer'].strip()
    if r['query']=='distinct_name_count':
        m=re.fullmatch(r'(?:[Tt]he answer is\s*)?([12])\s*[.!]?',text)
        return dict(count_correct=(int(m[1])==r['gold_reported_name_count']) if m else None,
                    parsed_count=int(m[1]) if m else None)
    aliases={}
    for key in ('source_candidate','other_candidate'):
        aliases[r[key].casefold()]=key
        aliases[r[key.replace('candidate','description')].casefold()]=key
    choices='|'.join(sorted((re.escape(x) for x in aliases),key=len,reverse=True))
    if r['query']=='neutral_pair':
        pattern=rf'\s*({choices})\s*(?:,|\band\b|;)\s*({choices})\s*[.!]?\s*'
    else:
        # Intentionally no permissive extraction from prose/explanations.
        pattern=rf'\s*Earlier object:\s*\[?({choices})\]?\s*[.;]?\s*Later object:\s*\[?({choices})\]?\s*[.;]?\s*'
    m=re.fullmatch(pattern,text,re.I)
    if not m:return dict(old_correct=None,second_correct=None,joint_correct=None,name_format_correct=None)
    v=[aliases[m[i].casefold()] for i in (1,2)]
    old=v[0]==r['gold_old_answer_class'];new=v[1]==r['gold_answer_class']
    return dict(old_correct=old,second_correct=new,joint_correct=old and new,
                name_format_correct=all(m[i].casefold() in (r['source_candidate'].casefold(),r['other_candidate'].casefold()) for i in (1,2)))

def analyze(cache):
    rows=[];runs=[]
    for q,s in itertools.product(('neutral_pair','keyed_roles','distinct_name_count'),(0,1)):
        p=cache/'runs'/f'E51-{q}-{s}';cfg=json.loads((p/'config.json').read_text());assert sha(p/'generations.jsonl')==cfg['generations_sha256']
        rr=list(map(json.loads,(p/'generations.jsonl').read_text().splitlines()));assert len(rr)==768;rows.extend(rr)
        runs.append(dict(query=q,shard=s,config_sha256=sha(p/'config.json'),generations_sha256=cfg['generations_sha256'],cap_reached=sum(r['cap_reached'] for r in rr),gpu_hours=cfg['gpu_hours']))
    assert len(rows)==len({r['item_id'] for r in rows})==4608
    for r in rows:r['literal']=parse(r)
    out=dict(experiment='E51',status='POST-HOC literal-schema analysis; complete Step Plan semantic review pending',
             parser_sha256=sha(Path(__file__)),runs=runs,bootstrap_unit='12 families, all balanced contexts averaged',bootstrap_draws=10000,bootstrap_seed=20261005,
             limitations='Unparsed answers remain unknown; explicit correct descriptions accepted as entity references using externally audited fixed aliases. No new semantic annotations. Count-wording ambiguity not resolved by this instrument.',counts={},bounds={},contrasts={},per_family={})
    historical=json.loads((Path(__file__).parents[1]/'results/E50-summary.json').read_text())
    for cohort in ('all','eligible','grammar_common','nonpossessive11'):
        rr=[r for r in rows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable']) and (cohort!='nonpossessive11' or r['verb_family']!='cuddled')]
        families=sorted({r['verb_family'] for r in rr});vectors={}
        def bounds(q,mode,metric,**filters):
            selected=[r for r in rr if r['query']==q and r['mode']==mode and all(r[k]==v for k,v in filters.items())]
            obs={f:[r['literal'][metric] for r in selected if r['verb_family']==f] for f in families}
            assert all(len(v)==len(next(iter(obs.values()))) for v in obs.values())
            return ({f:100*sum(v is True for v in vs)/len(vs) for f,vs in obs.items()},
                    {f:100*sum(v is not False for v in vs)/len(vs) for f,vs in obs.items()})
        def record(section,key,v):out[section][cohort+'/'+key]=stat(v);vectors[key]=v
        for q,mode in itertools.product(('neutral_pair','keyed_roles','distinct_name_count'),('base','priority')):
            metrics=('count_correct',) if q=='distinct_name_count' else ('old_correct','second_correct','joint_correct','name_format_correct')
            for metric in metrics:
                k=f'{cohort}/{q}/{mode}/{metric}';out['counts'][k]=dict(collections.Counter(str(r['literal'][metric]) for r in rr if r['query']==q and r['mode']==mode))
                lo,hi=bounds(q,mode,metric);record('bounds',f'pooled_lower/{q}/{mode}/{metric}',lo);record('bounds',f'pooled_upper/{q}/{mode}/{metric}',hi)
                lc,uc=bounds(q,mode,metric,congruence='congruent');li,ui=bounds(q,mode,metric,congruence='incongruent')
                record('contrasts',f'congruence_lower/{q}/{mode}/{metric}',diff(lc,ui));record('contrasts',f'congruence_upper/{q}/{mode}/{metric}',diff(uc,li))
                for form in ('name','description'):
                    lo,hi=bounds(q,mode,metric,second_fact_form=form);record('bounds',f'form_lower/{q}/{form}/{mode}/{metric}',lo);record('bounds',f'form_upper/{q}/{form}/{mode}/{metric}',hi)
                lp,up=bounds(q,'priority',metric);lb,ub=bounds(q,'base',metric)
                if mode=='base':
                    record('contrasts',f'priority_minus_base_lower/{q}/{metric}',diff(lp,ub));record('contrasts',f'priority_minus_base_upper/{q}/{metric}',diff(up,lb))
                for form,inv,pred,cg in itertools.product(('name','description'),(0,1),('same_began','different_began'),('congruent','incongruent')):
                    lo,hi=bounds(q,mode,metric,second_fact_form=form,inventory_present=inv,predicate=pred,congruence=cg)
                    record('bounds',f'cell_lower/{q}/{form}/I{inv}/{pred}/{cg}/{mode}/{metric}',lo);record('bounds',f'cell_upper/{q}/{form}/I{inv}/{pred}/{cg}/{mode}/{metric}',hi)
                if metric=='joint_correct' and mode=='base':
                    lo,hi=bounds(q,mode,metric);old=historical['per_family'][cohort];assert lo.keys()==old.keys()
                    oldlo={f:old[f]['pooled_lower/pair_names/base/joint_correct'] for f in families};oldhi={f:old[f]['pooled_upper/pair_names/base/joint_correct'] for f in families}
                    record('contrasts',f'{q}_minus_E50_pair_lower',diff(lo,oldhi));record('contrasts',f'{q}_minus_E50_pair_upper',diff(hi,oldlo))
        out['per_family'][cohort]={f:{k:v[f] for k,v in vectors.items()} for f in families}
    out['historical_summary_sha256']=sha(Path(__file__).parents[1]/'results/E50-summary.json')
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--out',type=Path,required=True);a=p.parse_args();j=analyze(a.cache)
    # Compact formatting avoids repeated hundreds of thousands of JSON lines.
    a.out.write_text(json.dumps(j,ensure_ascii=False,separators=(',',':'))+'\n')
    for k,v in j['bounds'].items():
        if k.startswith('all/pooled_'):print(k,v['estimate'],v['ci95'])
