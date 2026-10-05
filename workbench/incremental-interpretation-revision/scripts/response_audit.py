"""E05: unchanged upstream questions, orthogonalized response labels/meaning."""
import json
from data import amouyal, verified_root

def tasks_response(cache,tokenizer):
    root=verified_root(cache,'amouyal');pref=json.loads((root/'prefixes/prefixes.json').read_text())[0]
    tasks=[]
    for order in ('reg','rev'):
        for mode in ('standard','letter','asserted'):
            for yes_label in (['Yes'] if mode=='standard' else ['A','B']):
                for r in amouyal(cache):
                    q=(f'Here is the sentence:\n{r["sentence"]}\n\nAnswer this question:\n{r["question"]}' if order=='reg'
                       else f'Answer this question:\n{r["question"]}\n\nHere is the sentence:\n{r["sentence"]}')
                    if mode=='standard':labels={'Yes':'Yes','No':'No'}
                    else:
                        descriptions={'Yes':'Yes','No':'No'} if mode=='letter' else {
                            'Yes':'The sentence explicitly states the relation asked about (Yes).',
                            'No':'The sentence does not explicitly state the relation asked about (No; this does not claim the event is impossible).'}
                        labels={'Yes':yes_label,'No':'B' if yes_label=='A' else 'A'}
                        options=sorted([(labels[v],descriptions[v]) for v in ('Yes','No')])
                        q+='\n\nAnswer with the option letter only:\n'+'\n'.join(f'{label}. {desc}' for label,desc in options)
                    text=tokenizer.apply_chat_template([{'role':'system','content':pref['system']},{'role':'user','content':q}],
                         tokenize=False,add_generation_prompt=True,enable_thinking=False)+'My answer is: '
                    item=dict(r,query_order=order,response_mode=mode,yes_label=labels['Yes'],no_label=labels['No'])
                    tasks.append((item,f'{order}_{mode}_{yes_label}',text))
    return tasks

def analyze_response(rows):
    import collections
    import numpy as np
    from analyze import estimate
    sets=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in rows:sets[r['pair_id']][(r['response_mode'],r['query_order'],r['condition'],r['question_type'])].append(r)
    out={'cells':{},'effects':{},'label_variation':{},'interactions':{}}
    for metric in ('correct','p_correct','choice_mass'):
        avg={sid:{k:np.mean([r[metric] for r in rr]) for k,rr in d.items()} for sid,d in sets.items()}
        for key in sorted({k for d in avg.values() for k in d}):out['cells'][metric+'/'+ '/'.join(key)]=estimate([d[key] for d in avg.values()])
        for mode in ('standard','letter','asserted'):
            for order in ('reg','rev'):
                for q in ('lingering','simple'):
                    out['effects'][f'{metric}/{mode}/{order}/{q}']=estimate([d[(mode,order,'non_gp',q)]-d[(mode,order,'gp',q)] for d in avg.values()])
                out['effects'][f'{metric}/{mode}/{order}/specificity_DiD']=estimate([d[(mode,order,'non_gp','lingering')]-d[(mode,order,'gp','lingering')]-d[(mode,order,'non_gp','simple')]+d[(mode,order,'gp','simple')] for d in avg.values()])
            out['interactions'][f'{metric}/{mode}/order']=estimate([d[(mode,'reg','non_gp','lingering')]-d[(mode,'reg','gp','lingering')]-d[(mode,'rev','non_gp','lingering')]+d[(mode,'rev','gp','lingering')] for d in avg.values()])
    for mode in ('letter','asserted'):
        for order in ('reg','rev'):
            for condition in ('gp','non_gp'):
                for q in ('simple','lingering'):
                    ds=[]
                    for sid,d in sets.items():
                        rr=d[(mode,order,condition,q)]
                        a=next(r for r in rr if r['yes_label']=='A');b=next(r for r in rr if r['yes_label']=='B')
                        ds.append(a['p_correct']-b['p_correct'])
                    out['label_variation'][f'{mode}/{order}/{condition}/{q}/A_minus_B']=estimate(ds)
    return out
