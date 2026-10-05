"""E06: syntactic attachment vs released event questions on unchanged sentences."""
import collections
import hashlib
import json
from data import amouyal, verified_root

SOURCE_QUESTION_FLAGS={
 'set_hyp5_14':'Released simple question uses singular tomato; both sentences use plural tomatoes.',
 'set_hyp5_18':'Released simple question asks floor; both sentences state road.',
}

def attachment_rows(cache):
    original=amouyal(cache);sets=collections.defaultdict(dict)
    for r in original:sets[r['pair_id']][(r['condition'],r['question_type'])]=r
    result=[]
    for sid,group in sets.items():
        initial=group[('gp','lingering')]['question'].removesuffix('?').split()
        final=group[('gp','simple')]['question'].removesuffix('?').split()
        assert initial[0]=='Did' and final[0] in ('Did','Was','Were')
        initial=initial[1:];final=final[1:]
        lengths=[n for n in range(1,min(len(initial),len(final))+1) if initial[-n:]==final[:n]]
        if sid=='set_hyp5_14':np='the tomatoes' # explicit source singular/plural audit
        else:
            assert lengths,sid
            np=' '.join(final[:max(lengths)])
        assert len(np.split())>=2
        for condition in ('gp','non_gp'):
            base=group[(condition,'lingering')]
            assert base['sentence'].lower().count(np.lower())==1,(sid,np)
            assert base['sentence'].lower().count('while ')==1
            for qtype in ('simple','lingering'):
                r=group[(condition,qtype)]
                common=dict(target_np=np,source_question_flag=SOURCE_QUESTION_FLAGS.get(sid),source_question_clean=sid not in SOURCE_QUESTION_FLAGS)
                result.append(dict(r,**common,readout='event',source_item_id=r['item_id']))
                question=(f'In this sentence, is "{np}" the grammatical subject of the main clause?' if qtype=='simple'
                          else f'In this sentence, is "{np}" the direct object of the verb in the while-clause?')
                result.append(dict(r,**common,readout='attachment',source_item_id=r['item_id'],
                                   item_id=r['item_id']+':attachment',question=question,
                                   question_sha256=hashlib.sha256(question.encode()).hexdigest()))
    assert len(result)==552 and len({r['item_id'] for r in result})==552
    return result

def tasks_attachment(cache,tokenizer):
    from infer import REPAIR
    root=verified_root(cache,'amouyal');pref=json.loads((root/'prefixes/prefixes.json').read_text())[0]
    tasks=[]
    for order in ('reg','rev'):
        for repair in (False,True):
            for r in attachment_rows(cache):
                q=(f'Here is the sentence:\n{r["sentence"]}\n\nAnswer this question:\n{r["question"]}' if order=='reg'
                   else f'Answer this question:\n{r["question"]}\n\nHere is the sentence:\n{r["sentence"]}')
                system=pref['system']+('\n\n'+REPAIR if repair else '')
                prompt=tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':q}],
                  tokenize=False,add_generation_prompt=True,enable_thinking=False)+'My answer is: '
                tasks.append((dict(r,query_order=order,repair=repair),f'{order}_{"repair" if repair else "base"}',prompt))
    return tasks

def analyze_attachment(rows):
    import numpy as np
    from analyze import estimate
    out={'cells':{},'paired_effects':{},'readout_contrasts':{},'joint':{}}
    for stratum in ('all','source_question_clean'):
        selected=[r for r in rows if stratum=='all' or r['source_question_clean']]
        sets=collections.defaultdict(dict)
        for r in selected:
            k=(r['readout'],r['query_order'],r['repair'],r['condition'],r['question_type'])
            assert k not in sets[r['pair_id']]
            sets[r['pair_id']][k]=r
        for metric in ('correct','p_correct','choice_mass'):
            avg={sid:{k:r[metric] for k,r in d.items()} for sid,d in sets.items()}
            for k in sorted(next(iter(avg.values()))):
                out['cells'][stratum+'/'+metric+'/'+ '/'.join(map(str,k))]=estimate([d[k] for d in avg.values()])
            for readout in ('event','attachment'):
                for order in ('reg','rev'):
                    for repair in (False,True):
                        for qt in ('simple','lingering'):
                            key=f'{stratum}/{metric}/{readout}/{order}/{repair}/{qt}'
                            out['paired_effects'][key]=estimate([d[(readout,order,repair,'non_gp',qt)]-d[(readout,order,repair,'gp',qt)] for d in avg.values()])
            for order in ('reg','rev'):
                for repair in (False,True):
                    for condition in ('gp','non_gp'):
                        for qt in ('simple','lingering'):
                            key=f'{stratum}/{metric}/{order}/{repair}/{condition}/{qt}/attachment_minus_event'
                            out['readout_contrasts'][key]=estimate([d[('attachment',order,repair,condition,qt)]-d[('event',order,repair,condition,qt)] for d in avg.values()])
        for order in ('reg','rev'):
            for repair in (False,True):
                for condition in ('gp','non_gp'):
                    # Both structural roles must be correct for the mismatch
                    # diagnostic; mere attachment-No bias does not suffice.
                    key=f'{stratum}/{order}/{repair}/{condition}/both_roles_correct_event_initial_yes'
                    out['joint'][key]=estimate([int(d[('attachment',order,repair,condition,'simple')]['correct'] and d[('attachment',order,repair,condition,'lingering')]['correct'] and not d[('event',order,repair,condition,'lingering')]['correct']) for d in sets.values()])
    return out
