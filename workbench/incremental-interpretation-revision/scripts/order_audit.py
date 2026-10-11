"""E03: orthogonalize question order from upstream demonstration bundles."""
import json
from data import amouyal, verified_root

ASSERTION='Answer Yes only when the sentence explicitly states the relation asked about. Answer No when the sentence does not state it; do not fill in an unstated object from plausibility.'

def tasks_order(cache,tokenizer):
    root=verified_root(cache,'amouyal');rows=amouyal(cache);tasks=[]
    for demo,file in [('reg','prefixes.json'),('rev','prefixes_rev.json')]:
        pref=json.loads((root/'prefixes'/file).read_text())[0]
        for query in ('reg','rev'):
            for interface in ('raw','chat'):
                for instruction in ('none','assertion'):
                    for r in rows:
                        q=(f'Here is the sentence:\n{r["sentence"]}\n\nAnswer this question:\n{r["question"]}' if query=='reg'
                           else f'Answer this question:\n{r["question"]}\n\nHere is the sentence:\n{r["sentence"]}')
                        system=pref['system']+('\n\n'+ASSERTION if instruction=='assertion' else '')
                        if interface=='raw':prompt=system+'\n\n'+q+'\n\n'+pref['suffix']
                        else:prompt=tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':q}],
                                tokenize=False,add_generation_prompt=True,enable_thinking=False)+pref['suffix']
                        item=dict(r,demo_bundle=demo,query_order=query,interface=interface,instruction=instruction)
                        tasks.append((item,f'demo_{demo}_query_{query}_{interface}_{instruction}',prompt))
    return tasks

def analyze_order(rows):
    import collections
    import numpy as np
    from analyze import estimate
    out={'cells':{},'effects':{},'question_order_interactions':{},'assertion_interactions':{}}
    sets=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in rows:sets[r['pair_id']][(r['demo_bundle'],r['query_order'],r['interface'],r['instruction'],r['condition'],r['question_type'])].append(r)
    for metric in ('correct','p_correct','choice_mass'):
        avg={sid:{k:np.mean([r[metric] for r in rr]) for k,rr in d.items()} for sid,d in sets.items()}
        for key in sorted({k for d in avg.values() for k in d}):
            out['cells'][metric+'/'+ '/'.join(key)]=estimate([d[key] for d in avg.values() if key in d])
        for demo in ('reg','rev'):
            for query in ('reg','rev'):
                for interface in ('raw','chat'):
                    for instr in ('none','assertion'):
                        prefix=(demo,query,interface,instr)
                        for q in ('lingering','simple'):
                            out['effects'][metric+'/'+ '/'.join(prefix)+'/'+q]=estimate([d[prefix+('non_gp',q)]-d[prefix+('gp',q)] for d in avg.values()])
            for interface in ('raw','chat'):
                for instr in ('none','assertion'):
                    def diff(d,query):
                        p=(demo,query,interface,instr)
                        return d[p+('non_gp','lingering')]-d[p+('gp','lingering')]
                    out['question_order_interactions'][f'{metric}/{demo}/{interface}/{instr}']=estimate([diff(d,'reg')-diff(d,'rev') for d in avg.values()])
                for query in ('reg','rev'):
                    def diff_instr(d,instr):
                        p=(demo,query,interface,instr)
                        return d[p+('non_gp','lingering')]-d[p+('gp','lingering')]
                    out['assertion_interactions'][f'{metric}/{demo}/{query}/{interface}']=estimate([diff_instr(d,'assertion')-diff_instr(d,'none') for d in avg.values()])
    return out
