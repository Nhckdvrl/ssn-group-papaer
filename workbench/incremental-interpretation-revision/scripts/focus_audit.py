"""E08: hold final question position fixed; intervene on reading focus."""
import collections
from data import amouyal
from analyze import estimate

def tasks_focus(cache,tokenizer):
    from infer import REPAIR
    rows=amouyal(cache);sets=collections.defaultdict(dict)
    for r in rows:sets[r['pair_id']][r['question_type']]=r['question']
    ids=sorted(sets);other={s:ids[(i+1)%len(ids)] for i,s in enumerate(ids)}
    assert all(other[s]!=s for s in ids)
    base='Answer the final reading comprehension question only, using the supplied sentence. A reading focus is optional background, not an instruction to answer it. Answer only Yes or No.'
    tasks=[]
    for repair in (False,True):
        for position in ('none','before','after'):
            for focus in (['none'] if position=='none' else ['initial','final','unrelated_initial','unrelated_final']):
                for r in rows:
                    sentence=f'Here is the sentence:\n{r["sentence"]}'
                    target=f'Answer this final question:\n{r["question"]}'
                    if focus=='none':q=sentence+'\n\n'+target
                    else:
                        sid=other[r['pair_id']] if focus.startswith('unrelated') else r['pair_id']
                        fq=sets[sid]['lingering' if focus.endswith('initial') else 'simple']
                        context=f'Reading focus:\n{fq}'
                        q='\n\n'.join([context,sentence,target] if position=='before' else [sentence,context,target])
                    assert q.endswith(r['question'])
                    prompt=tokenizer.apply_chat_template([{'role':'system','content':base+('\n\n'+REPAIR if repair else '')},
                        {'role':'user','content':q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                    pid=f'{position}_{focus}_{"repair" if repair else "base"}'
                    tasks.append((dict(r,focus=focus,focus_position=position,repair=repair),pid,prompt))
    return tasks

def analyze_focus(rows):
    out={'cells':{},'effects':{},'interactions':{}}
    for stratum in ('all69','clean67'):
        rr=[r for r in rows if stratum=='all69' or r['pair_id'] not in ('set_hyp5_14','set_hyp5_18')]
        for subtype in ('pooled','prob','reflexive'):
            sub=rr if subtype=='pooled' else [r for r in rr if r['subtype']==subtype]
            ix={(r['pair_id'],r['prompt_id'],r['condition'],r['question_type']):r for r in sub};ids=sorted({r['pair_id'] for r in sub})
            def values(pid,c,q,m):return {s:ix[(s,pid,c,q)][m] for s in ids}
            def diff(a,b):return {s:a[s]-b[s] for s in a.keys()&b.keys()}
            def stat(v):return estimate([v[s] for s in sorted(v)])
            prefix=f'{stratum}/{subtype}'
            for q in ('simple','lingering'):
                for m in ('p_yes','correct','choice_mass'):
                    for pid in sorted({r['prompt_id'] for r in sub}):
                        for c in ('gp','non_gp'):out['cells'][f'{prefix}/{pid}/{c}/{q}/{m}']=stat(values(pid,c,q,m))
                    for repair in ('base','repair'):
                        contrasts={}
                        for position in ('before','after'):
                            for f1,f2 in [('initial','final'),('initial','unrelated_initial'),('final','unrelated_final')]:
                                contrasts[f'{position}/{f1}_minus_{f2}']=(f'{position}_{f1}_{repair}',f'{position}_{f2}_{repair}')
                        for focus in ('initial','final','unrelated_initial','unrelated_final'):
                            contrasts[f'{focus}/before_minus_after']=(f'before_{focus}_{repair}',f'after_{focus}_{repair}')
                            contrasts[f'{focus}/before_minus_none']=(f'before_{focus}_{repair}',f'none_none_{repair}')
                        for name,(a,b) in contrasts.items():
                            d={c:diff(values(a,c,q,m),values(b,c,q,m)) for c in ('gp','non_gp')}
                            for c in d:out['effects'][f'{prefix}/{repair}/{name}/{c}/{q}/{m}']=stat(d[c])
                            out['interactions'][f'{prefix}/{repair}/{name}/GP_minus_nonGP/{q}/{m}']=stat(diff(d['gp'],d['non_gp']))
    return out
