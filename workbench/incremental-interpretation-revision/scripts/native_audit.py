"""E07: transfer released questions across assistant boundaries, without new gold."""
import json
from data import amouyal,verified_root
from analyze import estimate

def tasks_native(cache,tokenizer,system_frame='both'):
    from infer import REPAIR
    root=verified_root(cache,'amouyal');rows=amouyal(cache);tasks=[]
    reg=json.loads((root/'prefixes/prefixes.json').read_text())[0]
    rev=json.loads((root/'prefixes/prefixes_rev.json').read_text())[0]
    frames=['neutral','upstream'] if system_frame=='both' else [system_frame]
    for frame in frames:
        base=reg['system'].split('Here are a few examples')[0].strip() if frame=='neutral' else reg['system']
        base+='\n\nAnswer only Yes or No.'
        for order,pref in [('reg',reg),('rev',rev)]:
            for repair in (False,True):
                for boundary in ('native','prefill'):
                    for r in rows:
                        q=pref['question'].replace('SENTENCE',r['sentence']).replace('QUESTION',r['question'])
                        prompt=tokenizer.apply_chat_template([{'role':'system','content':base+('\n\n'+REPAIR if repair else '')},
                            {'role':'user','content':q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                        if boundary=='prefill':prompt+=reg['suffix']
                        pid=f'{frame}_{order}_{"repair" if repair else "base"}_{boundary}'
                        tasks.append((dict(r,system_frame=frame,query_order=order,repair=repair,boundary=boundary),pid,prompt))
    return tasks

def analyze_native(rows):
    out={'cells':{},'condition_gaps':{},'boundary_effects':{},'order_interactions':{}}
    for stratum in ('all69','source_question_clean67'):
        rr=[r for r in rows if stratum=='all69' or r['pair_id'] not in ('hyp5_14','hyp5_18')]
        for subtype in ('pooled','prob','reflexive'):
            sub=rr if subtype=='pooled' else [r for r in rr if r['subtype']==subtype]
            ix={(r['pair_id'],r['prompt_id'],r['condition'],r['question_type']):r for r in sub}
            ids=sorted({r['pair_id'] for r in sub})
            def vals(pid,c,q,m):return {s:ix[(s,pid,c,q)][m] for s in ids if (s,pid,c,q) in ix}
            def diff(a,b):return {s:a[s]-b[s] for s in a.keys()&b.keys()}
            def stats(x):return estimate(list(x.values())) if x else {'estimate':None,'ci95':None,'n_sets':0}
            prefix=f'{stratum}/{subtype}'
            for m in ('correct','p_yes','choice_mass'):
                for pid in sorted({r['prompt_id'] for r in sub}):
                    for q in ('simple','lingering'):
                        for c in ('gp','non_gp'):out['cells'][f'{prefix}/{pid}/{c}/{q}/{m}']=stats(vals(pid,c,q,m))
                        out['condition_gaps'][f'{prefix}/{pid}/{q}/{m}']=stats(diff(vals(pid,'non_gp',q,m),vals(pid,'gp',q,m)))
                for frame in ('neutral','upstream'):
                    for repair in ('base','repair'):
                        for boundary in ('native','prefill'):
                            a=f'{frame}_reg_{repair}_{boundary}';b=f'{frame}_rev_{repair}_{boundary}'
                            for q in ('simple','lingering'):
                                ga=diff(vals(a,'non_gp',q,m),vals(a,'gp',q,m));gb=diff(vals(b,'non_gp',q,m),vals(b,'gp',q,m))
                                out['order_interactions'][f'{prefix}/{frame}/{repair}/{boundary}/{q}/{m}']=stats(diff(ga,gb))
                        for order in ('reg','rev'):
                            a=f'{frame}_{order}_{repair}_native';b=f'{frame}_{order}_{repair}_prefill'
                            for c in ('gp','non_gp'):
                                for q in ('simple','lingering'):out['boundary_effects'][f'{prefix}/{frame}/{order}/{repair}/{c}/{q}/{m}']=stats(diff(vals(a,c,q,m),vals(b,c,q,m)))
    return out
