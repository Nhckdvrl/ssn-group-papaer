"""E89 identical grammatical frame information before or after original Source."""
import argparse
import json
from pathlib import Path
from data import sha
from data_v2 import digest
from current_open_baseline import prepare as native_prepare


def build(root):
    parent=root.parent/'E88/data-v1.jsonl'
    rows=list(map(json.loads,parent.read_text().splitlines()))
    originals={r['item_id']:r for r in map(json.loads,(root.parent/'E82/data-v1.jsonl').read_text().splitlines())}
    out=[]
    for r in rows:
        old=originals[r['item_id']]
        for k in ['sentence','question','grounded_gold','analysis_cluster_id','analysis_question_target']:
            assert r[k]==old[k]
        v=r['frame_locator']['verb_surface']
        if r['construction']=='NPZ':frame='is used intransitively, without a direct object'
        elif r['construction']=='MVRR':frame='is a passive past participle in a relative clause'
        else:frame='takes a finite clause as its complement'
        hint=f'Grammatical information about the supplied sentence: the verb "{v}" {frame}.'
        assert r['question'] not in hint and 'Yes' not in hint and 'No' not in hint
        out.append(dict(old,frame_locator=r['frame_locator'],frame_hint=hint))
    root.mkdir(exist_ok=True);p=root/'data-v1.jsonl';assert not p.exists()
    p.write_text(''.join(json.dumps(r)+'\n' for r in out))
    (root/'data-v1.manifest.json').write_text(json.dumps(dict(data_sha256=sha(p),parent_E88_sha256=sha(parent),
        original_E82_sha256=sha(root.parent/'E82/data-v1.jsonl'),QA=len(out),GP_sources=151,new_outputs=len(out)*4*3,new_api_calls=0,
        hint_origin='Grammatical construction and author cue, target surface word; no entity/gold/question'),indent=2)+'\n')
    print('E89 data',len(out),sha(p),flush=True)


def prepare(rows,tok):
    native=[t for t in native_prepare(rows,tok) if t['operation']=='DIRECT' and t['readout']=='words']
    tasks=[]
    for old in native:
        r=old['row'];hint=r['frame_hint']
        content_start='Read this sentence carefully.\nSentence:\n'
        task_suffix=old['prompt'][old['prompt'].index('\n\nTask:\n'):]
        # Rebuild the user body with the original Task bytes, then the same native template.
        # Extract original Task user text separately to avoid copying assistant template suffix.
        shown=['Yes','No'] if old['mapping']==0 else ['No','Yes']
        from current_open_baseline import RULE
        tail='\n\nTask:\n'+RULE+'\nQuestion:\n'+r['question']+'\n'+'\n'.join(f'{a}. {b}' for a,b in zip(['A','B'],shown))+'\nAnswer only Yes or No.'
        for op in ['EARLY_FRAME','LATE_FRAME']:
            if op=='EARLY_FRAME':body='Read this sentence carefully.\nHint:\n'+hint+'\n\nSentence:\n'+r['sentence']+tail
            else:body=content_start+r['sentence']+'\n\nHint:\n'+hint+tail
            prompt=tok.apply_chat_template([dict(role='user',content=body)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            if op=='LATE_FRAME':
                end=prompt.index('\n\nHint:\n');oe=old['prompt'].index('\n\nTask:\n')
                assert prompt[:end]==old['prompt'][:oe]
                assert tok.encode(prompt[:end],add_special_tokens=False)==tok.encode(old['prompt'][:oe],add_special_tokens=False)
            assert old['prompt'].endswith(task_suffix) and prompt.endswith(task_suffix)
            tasks.append(dict(old,operation=op,prompt=prompt,native_prompt_sha256=digest(old['prompt'])))
    assert len(tasks)==len(rows)*4
    return tasks


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();build(a.root)
