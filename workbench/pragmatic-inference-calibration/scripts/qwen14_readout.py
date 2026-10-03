"""E41 exact parent prompts, complete common tokenizer and atomic numeric content."""
import hashlib,json
from run_implicaturex import prepare as implicature_prepare

def plan(tok,messages,choices,bare=False):
    if bare:
        assert len(messages)==1 and messages[0]['role']=='user'
        rendered=messages[0]['content']
    else:
        rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    prefix=tok.encode(rendered,add_special_tokens=False)
    full=[tok.encode(rendered+c,add_special_tokens=False) for c in choices]
    assert all(z[:len(prefix)]==prefix and len(z)==len(prefix)+1 for z in full)
    assert len({z[-1] for z in full})==len(choices)
    return {'input_ids':prefix,'original_prefix_length':len(prefix),'candidate_ids':[z[-1] for z in full],
        'full_choice_ids':full,'choices':choices,'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest(),
        'generated_common_prefix_ids':[]}

def prepare(root,tok,task):
    rows=[]
    if task.startswith('hu-'):
        source=[json.loads(l) for l in (root/'data/hu.jsonl').read_text().splitlines()]
        for r in source:
            p=r['prompt'] if task=='hu-bare' else 'Reply with only the number of the selected answer.\n\n'+r['prompt']
            rows.append({'source':r,'condition':task,'plan':plan(tok,[{'role':'user','content':p}],r['choices'],task=='hu-bare')})
        assert len(rows)==1365
    else:
        assert task=='implicaturex';source,_=implicature_prepare(root)
        for condition in ['parent','format']:
            for r in source:
                p=r['prompt']+('\nReply with only 1 or 2.' if condition=='format' else '')
                rows.append({'source':r,'condition':condition,'plan':plan(tok,[{'role':'system','content':r['system_prompt']},
                    {'role':'user','content':p}],['1','2'])})
        assert len(rows)==6504
    return rows

def fingerprint(rows):
    return hashlib.sha256(json.dumps([r['plan']['full_choice_ids'] for r in rows]).encode()).hexdigest()
