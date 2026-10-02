"""Complete numeric option content, with the exact shared generated prefix factored out."""
import hashlib,json
from circa_pair_data import prepare as circa_prepare,prompt as circa_prompt,CATEGORIES
from run_circa_instruction import STRICT
from run_implicaturex import prepare as implicature_prepare

def plan(tok,messages,choices,bare=False):
    if bare:
        assert len(messages)==1 and messages[0]['role']=='user'
        rendered=tok.bos_token+messages[0]['content']
        # Hu source already ends with a space. Never add a second space, which
        # retokenizes the immutable prompt suffix with this tokenizer.
        bodies=[rendered+c for c in choices]
        original=tok.encode(rendered,add_special_tokens=False)
        full=[tok.encode(x,add_special_tokens=False) for x in bodies]
    else:
        rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        original=tok.encode(rendered,add_special_tokens=False)
        full=[]
        for c in choices:
            # This pinned template injects a system message only when user is
            # loop.last; re-rendering with assistant would silently erase it.
            # Freeze the generation prompt and append the template's exact
            # assistant serialization (space + trimmed content + EOS).
            x=tok.encode(rendered+' '+c.strip()+tok.eos_token,add_special_tokens=False)
            assert x[-1]==tok.eos_token_id
            full.append(x[:-1])  # Content probability, matching parent numeric choice, without EOS.
    assert all(x[:len(original)]==original for x in full)
    stop=len(original)
    while all(len(x)>stop and x[stop]==full[0][stop] for x in full):stop+=1
    assert all(len(x)==stop+1 for x in full), 'Full choices do not factor into shared prefix + one token'
    assert len({x[-1] for x in full})==len(choices)
    return {'input_ids':full[0][:stop],'original_prefix_length':len(original),
        'candidate_ids':[x[-1] for x in full],'full_choice_ids':full,'choices':choices,
        'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest(),
        'generated_common_prefix_ids':full[0][len(original):stop]}

def prepare(root,tok,task):
    rows=[]
    if task.startswith('hu-'):
        source=[json.loads(l) for l in (root/'data/hu.jsonl').read_text().splitlines()]
        for r in source:
            p=r['prompt'] if task=='hu-bare' else 'Reply with only the number of the selected answer.\n\n'+r['prompt']
            rows.append({'source':r,'condition':task,'plan':plan(tok,[{'role':'user','content':p}],r['choices'],task=='hu-bare')})
        assert len(rows)==1365
    elif task=='circa':
        source,_,_=circa_prepare(root)
        for interface in ['bare','common-chat']:
            for condition in ['original','strict']:
                for order in [0,1]:
                    options=CATEGORIES if order==0 else list(reversed(CATEGORIES))
                    for r in source:
                        p=(STRICT if condition=='strict' else '')+circa_prompt(r,order)
                        rows.append({'source':r,'interface':interface,'condition':condition,'order':order,
                            'options':options,'plan':plan(tok,[{'role':'user','content':p}],list(map(str,range(1,9))),interface=='bare')})
        assert len(rows)==8*433
    else:
        assert task=='implicaturex'
        source,_=implicature_prepare(root)
        for condition in ['parent','format']:
            for r in source:
                p=r['prompt']+('\nReply with only 1 or 2.' if condition=='format' else '')
                messages=[{'role':'system','content':r['system_prompt']},{'role':'user','content':p}]
                rows.append({'source':r,'condition':condition,'plan':plan(tok,messages,['1','2'])})
        assert len(rows)==6504
    return rows

def fingerprint(rows):
    return hashlib.sha256(json.dumps([r['plan']['full_choice_ids'] for r in rows]).encode()).hexdigest()
