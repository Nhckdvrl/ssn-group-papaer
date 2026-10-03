"""E55 source-unaltered baseline; literal goal is an explicit R8 control."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/data1/xiangding/work/pragmatic-inference-calibration')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def specs(root):
    selected = []
    for file in ['qwen25-14-stage-manifest.json', 'mistral-stage-manifest.json',
                 'olmoe-stage-manifest.json', 'qwen3-scale-manifest.json']:
        ms = json.loads((root/'models'/file).read_text())
        if file == 'olmoe-stage-manifest.json':
            ms = ms[1:2]
        selected.extend({k:m[k] for k in ('id','sha')} for m in ms)
    small=json.loads((root/'models/qwen3-4b-revision.json').read_text())
    selected.append({'id':small['model'],'sha':small['revision']})
    assert len(selected) == 8
    return selected


def tokenizer_path(root, cp):
    for base, instruct in [('Qwen2.5-14B','Qwen2.5-14B-Instruct'),
                           ('Mistral-7B-v0.3','Mistral-7B-Instruct-v0.3'),
                           ('OLMoE-1B-7B-0125-DPO','OLMoE-1B-7B-0125-SFT')]:
        if cp in (base,instruct):return root/'models'/instruct
    return root/'models'/cp


def prepare(root, tok):
    path=root/'data/E54-original-critical-materials.json'
    source=json.loads(path.read_text());assert len(source)==400
    instructions={'default':'', 'literal':'Answer the question using the sentence exactly as written, even if it describes an unlikely event.\n'}
    rows=[];nulls={}
    def plan(material, interface, instruction):
        question=material['Input.question_1_'];sentence=material['Input.trial_']
        prompt=instructions[instruction]+'Sentence: '+sentence+'\nQuestion: '+question
        if interface=='bare':rendered=(tok.bos_token or '')+prompt+'\nAnswer:'
        else:rendered=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,
                        add_generation_prompt=True,enable_thinking=False)+'Answer:'
        prefix=tok.encode(rendered,add_special_tokens=False)
        content=[tok.encode(rendered+c,add_special_tokens=False) for c in (' Yes',' No')]
        full=[tok.encode(rendered+c+'.',add_special_tokens=False) for c in (' Yes',' No')]
        assert all(z[:len(prefix)]==prefix and len(z)>len(prefix) for z in content+full)
        assert len({tuple(z) for z in full})==2 and max(map(len,full))<4096
        return {'prefix_ids':prefix,'content_ids':content,'full_ids':full,
                'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest()}
    for interface in ('bare','common-chat'):
        for instruction in instructions:
            nulls[interface+'/'+instruction]=plan({'Input.trial_':'[not provided]','Input.question_1_':'[not provided]'},interface,instruction)
            for r in sorted(source,key=lambda x:(x['source_file'],int(x['Item']),x['Condition'])):
                sid=r['source_file']+'/'+r['Item']+'/'+r['Condition']
                rows.append({'id':sid+'/'+interface+'/'+instruction,'source':r,
                    'interface':interface,'instruction':instruction,'literal_index':0 if r['CorrectAnswer1']=='Yes' else 1,
                    'plan':plan(r,interface,instruction)})
    assert len(rows)==len({r['id'] for r in rows})==1600
    return rows, {'source_file':str(path),'source_sha256':sha(path),'n_source':400}, nulls


def fingerprint(rows,nulls):
    return hashlib.sha256(json.dumps({'rows':rows,'nulls':nulls},sort_keys=True).encode()).hexdigest()


if __name__=='__main__':
    from transformers import AutoTokenizer,AutoConfig
    out=Path(__file__).resolve().parents[1]/'results/E55-source-preflight.json';assert not out.exists()
    audit={}
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];p=ROOT/'models'/cp
        marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text());assert marker['model']==m['id'] and marker['revision']==m['sha']
        native=AutoTokenizer.from_pretrained(p,local_files_only=True)
        common=AutoTokenizer.from_pretrained(tokenizer_path(ROOT,cp),local_files_only=True)
        assert native.backend_tokenizer.to_str()==common.backend_tokenizer.to_str()
        cfg=AutoConfig.from_pretrained(p,local_files_only=True)
        rows,source,nulls=prepare(ROOT,common)
        audit[cp]={'input_sha256':fingerprint(rows,nulls),'source_audit':source,
            'tokenizer_backend_sha256':hashlib.sha256(common.backend_tokenizer.to_str().encode()).hexdigest(),
            'native_eos_id':native.eos_token_id,'common_eos_id':common.eos_token_id,
            'max_tokens':max(len(z) for r in rows for z in r['plan']['full_ids']),
            'candidate_lengths':sorted({len(z)-len(r['plan']['prefix_ids']) for r in rows for z in r['plan']['full_ids']})}
        assert audit[cp]['max_tokens']<cfg.max_position_embeddings
    out.write_text(json.dumps({'models':specs(ROOT),'audits':audit,'helper_sha256':sha(Path(__file__)), 'gate_pass':True},indent=2)+'\n')
    print(json.dumps({k:{'max_tokens':v['max_tokens'],'candidate_lengths':v['candidate_lengths']} for k,v in audit.items()},indent=2))
