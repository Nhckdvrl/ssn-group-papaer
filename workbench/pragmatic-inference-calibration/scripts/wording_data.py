"""E59 original IQAP dialogues, three prospectively fixed interpretation wordings."""
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoConfig
import iqap_data
from dense_stage_data import specs as olmo_specs
from run_followup_queue import ROOT

ALIASES = {
    'W0': iqap_data.TARGETS,
    'W1': [f'B\'s intended answer was {a} "{p}".' for p in ('Yes','No') for a in ('definitely','probably')],
    'W2': [f'B\'s intended answer was {a} "{p}".' for p in ('Yes','No') for a in ('certainly','likely')],
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def specs(root):
    out = [{**m,'family':'OLMo2'} for m in olmo_specs(root)]
    for name,family in [('qwen25-14-stage-manifest.json','Qwen2.5'),('mistral-stage-manifest.json','Mistral')]:
        for stage,m in zip(('Base','Instruct'),json.loads((root/'models'/name).read_text())):
            out.append({**m,'family':family,'stage':stage})
    assert len(out)==8
    return out


def common_path(root,m):
    cp = {'OLMo2':'OLMo-2-1124-13B-SFT','Qwen2.5':'Qwen2.5-14B-Instruct',
          'Mistral':'Mistral-7B-Instruct-v0.3'}[m['family']]
    return root/'models'/cp


def sequences(tok,text,targets,interface):
    if interface=='bare':
        rendered=text
        content=[text+t for t in targets]
        full=[t+tok.eos_token for t in content]
    else:
        rendered=tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,
                    add_generation_prompt=True,enable_thinking=False)
        full=[tok.apply_chat_template([{'role':'user','content':text},{'role':'assistant','content':t}],
                    tokenize=False,add_generation_prompt=False,enable_thinking=False) for t in targets]
        # Mistral inserts a leading assistant space. Score that real separator,
        # rather than appending a different string to its generation prefix.
        content=[]
        for x,t in zip(full,targets):
            assert x.startswith(rendered)
            rest=x[len(rendered):]
            separator='' if rest.startswith(t) else ' '
            assert rest.startswith(separator+t)
            content.append(rendered+separator+t)
    prefix=tok.encode(rendered,add_special_tokens=False)
    ids=[tok.encode(t,add_special_tokens=False) for t in full]
    cids=[tok.encode(t,add_special_tokens=False) for t in content]
    assert len(set(map(tuple,ids)))==4
    for x,y in zip(ids,cids):
        assert x[:len(prefix)]==prefix and x[:len(y)]==y and len(x)>len(y)>len(prefix)
    return {'ids':ids,'first':len(prefix),'content_ends':[len(x) for x in cids],
            'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest()}


def prompt(source,targets):
    # Preserve original instructions except the visible candidate wordings.
    text=iqap_data.prompt(source)
    old='\n'.join(iqap_data.TARGETS)
    assert text.count(old)==1
    return text.replace(old,'\n'.join(targets))


def prepare(root,tok):
    source,source_sha=iqap_data.prepare(root)
    rows=[];nulls={}
    for alias,targets in ALIASES.items():
        for interface in ('bare','common-chat'):
            nulls[alias+'/'+interface]=sequences(tok,prompt({'Question':'[not provided]','Answer':'[not provided]'},targets),targets,interface)
            for r in source:
                plan=sequences(tok,prompt(r,targets),targets,interface)
                if alias=='W0' and tok.name_or_path.split('/')[-1]!='Mistral-7B-Instruct-v0.3':
                    assert plan==iqap_data.sequences(tok,iqap_data.prompt(r),interface)
                rows.append({'id':alias+'/'+interface+'/'+r['Item'],'alias':alias,'interface':interface,
                             'kind':'natural','source':r,'targets':targets,'plan':plan})
            for j,reference in enumerate(iqap_data.TARGETS):
                text=('Copy the interpretation specified in the reference. Choose its corresponding '
                      'interpretation below; do not guess a different answer.\nReference: '+reference+
                      '\nInterpretations:\n'+'\n'.join(targets)+'\nReply with only the selected interpretation sentence.\n')
                rows.append({'id':alias+'/'+interface+'/copy'+str(j),'alias':alias,'interface':interface,
                             'kind':'copy','expected_index':j,'reference':reference,'targets':targets,
                             'plan':sequences(tok,text,targets,interface)})
    assert len(rows)==len({r['id'] for r in rows})==924
    return rows,{'n_natural_items':150,'source_sha256':source_sha,'aliases':ALIASES,
                 'n_natural':900,'n_copy':24,'copy_is_not_human_gold':True},nulls


def fingerprint(rows,nulls):
    return hashlib.sha256(json.dumps({'rows':rows,'nulls':nulls},sort_keys=True).encode()).hexdigest()


def dependencies():
    return {n:sha(Path(__file__).with_name(n)) for n in ('iqap_data.py','dense_stage_data.py')}


if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'results/E59-source-preflight.json';assert not path.exists()
    audits={};family={}
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];p=ROOT/'models'/cp
        marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text())
        assert marker['model']==m['id'] and marker['revision']==m['sha']
        tok=AutoTokenizer.from_pretrained(common_path(ROOT,m),local_files_only=True)
        native=AutoTokenizer.from_pretrained(p,local_files_only=True)
        assert tok.backend_tokenizer.to_str()==native.backend_tokenizer.to_str()
        rows,audit,nulls=prepare(ROOT,tok);h=fingerprint(rows,nulls)
        assert family.setdefault(m['family'],h)==h
        maximum=max(len(z) for r in rows for z in r['plan']['ids'])
        assert maximum<AutoConfig.from_pretrained(p,local_files_only=True).max_position_embeddings
        audits[cp]={'input_sha256':h,'source_audit':audit,'max_tokens':maximum,
                    'native_special_map':native.special_tokens_map,'common_special_map':tok.special_tokens_map}
    path.write_text(json.dumps({'models':specs(ROOT),'audits':audits,'helper_sha256':sha(__file__),
                               'dependencies':dependencies(),'gate_pass':True},indent=2)+'\n')
    print(json.dumps({cp:v['max_tokens'] for cp,v in audits.items()}))
