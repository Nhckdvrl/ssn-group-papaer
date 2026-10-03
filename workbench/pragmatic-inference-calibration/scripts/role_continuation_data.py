"""E50 same source scenes; complete lexical continuation probabilities."""
import hashlib,json
from pathlib import Path
from speaker_listener_data import prepare as source_prepare,descriptor,IDENTITY,CODE,WORDS,specs,tokenizer_path

def prepare(root,tok):
    source,audit=source_prepare(root)
    source=[r for r in source if r['task']=='listener' or r['order']==0]
    assert len(source)==432
    rows=[]
    for interface in ['bare','common-chat']:
        for r in source:
            objs=[r['source'][k] for k in ['target','competitor','distractor']]
            roles=r['output_roles'] if r['task']=='listener' else list(range(3))
            scene='\n'.join(f'Object {j+1}: {descriptor(objs[k])}.' for j,k in enumerate(roles))
            context=('In a reference game there are exactly three objects. Both the speaker and the listener see all three.\n'+scene
                +'\nThe speaker must use exactly one of these four available words to tell the listener which object the speaker means: triangle, circle, red, green.\n'
                +IDENTITY[r['identity']])
            if r['task']=='listener':
                context+='\nThe listener hears the speaker say "'+CODE[r['source']['msg']]+'".'
                prefill='The speaker was referring to Object';choices=[' 1',' 2',' 3']
            else:
                context+=f"\nThe speaker wants the listener to identify Object {r['target_role']+1}."
                prefill='The speaker says:';choices=[' '+w for w in WORDS]
            if interface=='bare': rendered=(tok.bos_token or '')+context+'\n'+prefill
            else:
                rendered=tok.apply_chat_template([{'role':'user','content':context}],tokenize=False,add_generation_prompt=True,enable_thinking=False)+prefill
            prefix=tok.encode(rendered,add_special_tokens=False)
            content=[tok.encode(rendered+c,add_special_tokens=False) for c in choices]
            full=[tok.encode(rendered+c+'.',add_special_tokens=False) for c in choices]
            assert all(z[:len(prefix)]==prefix and len(z)>len(prefix) for z in content+full)
            assert len({tuple(z) for z in full})==len(choices)
            rows.append({'row':r,'interface':interface,'plan':{'prefix_ids':prefix,'content_ids':content,'full_ids':full,
                'choices':choices,'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest()}})
    assert len(rows)==864
    return rows,audit

def fingerprint(rows):
    return hashlib.sha256(json.dumps([r['plan'] for r in rows]).encode()).hexdigest()

if __name__=='__main__':
    import argparse
    from transformers import AutoTokenizer
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();checks={};common=None
    for cp,mid,revision in specs(a.root):
        tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,cp),local_files_only=True)
        rows,audit=prepare(a.root,tok)
        if common is None: common=audit
        else:assert audit==common
        checks[cp]={'input_token_sha256':fingerprint(rows),'n':len(rows),'max_prefix_tokens':max(len(r['plan']['prefix_ids']) for r in rows),
            'candidate_suffix_lengths':sorted({len(z)-len(r['plan']['prefix_ids']) for r in rows for z in r['plan']['full_ids']})}
    assert checks['OLMoE-1B-7B-0125-SFT']==checks['OLMoE-1B-7B-0125-DPO']
    sha=lambda name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    out={'models':checks,'source_audit':common,'helper_sha256':sha('role_continuation_data.py'),
        'original_dependency_sha256':sha('speaker_listener_data.py'),'gate_pass':True}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(checks,indent=2))
