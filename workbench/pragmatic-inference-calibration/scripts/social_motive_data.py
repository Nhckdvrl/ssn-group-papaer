"""E61 original MIN and original human checkbox marginals; explicitly adapted query."""
import csv
import hashlib
import itertools
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path
from transformers import AutoConfig,AutoTokenizer
from wording_data import specs,common_path,sha,fingerprint
from run_followup_queue import ROOT

UP=ROOT/'upstream/llm-social-calibration'
sys.path.insert(0,str(UP))
from src.config import SCENARIOS,CONTEXTS,UTTERANCES,ATTRIBUTES
from prompts.build_prompts import build_minimal_prompt

MOTIVES=[('t3_appropriate','because it was the appropriate level of detail in the situation'),
 ('t3_giveMore','to give as much information as possible'),('t3_tooMuchInf','to avoid giving too much information'),
 ('t3_didntKnow',"because the speaker didn't know the exact information"),
 ('t3_avoidFalse','to avoid saying something that might be false'),('t3_soundSmart','to sound smart'),
 ('t3_soundEasygoing','to sound easy-going'),('t3_easierUnderstand','to make the information easier to understand'),
 ('t3_easierSpeaker','because it was easier for the speaker'),('t3_none','none of these')]
CONTROL="Evaluate the listener's impression warranted by this particular dialogue, rather than the speaker's actual hidden character or motives."
SCENARIO_MAP={'absence':'office','bike':'bicycle','cinema':'cinema','conference':'conference','cooking':'pasta','house':'house'}


def dependencies():
    out={n:sha(Path(__file__).with_name(n)) for n in ('wording_data.py','audit_social_source.py')}
    for n in ['src/config.py','src/exp_texts.py','prompts/build_prompts.py']:
        out[n]=sha(UP/n)
    for n in ['E60-experiment1.csv','E60-codebook.csv','E60-original-social-prompts.json']:
        out[n]=sha(ROOT/'data'/n)
    return out


def sequences(tok,text,targets,interface):
    if interface=='bare':
        rendered=text+'\n';content=[rendered+t for t in targets];full=[c+tok.eos_token for c in content]
    else:
        rendered=tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        full=[tok.apply_chat_template([{'role':'user','content':text},{'role':'assistant','content':t}],tokenize=False,add_generation_prompt=False,enable_thinking=False) for t in targets]
        content=[]
        for x,t in zip(full,targets):
            assert x.startswith(rendered);rest=x[len(rendered):];separator='' if rest.startswith(t) else ' '
            assert rest.startswith(separator+t);content.append(rendered+separator+t)
    prefix=tok.encode(rendered,add_special_tokens=False)
    ids=[tok.encode(x,add_special_tokens=False) for x in full];cids=[tok.encode(x,add_special_tokens=False) for x in content]
    assert len(set(map(tuple,ids)))==len(targets)
    for x,y in zip(ids,cids):assert x[:len(prefix)]==prefix and x[:len(y)]==y and len(x)>len(y)>len(prefix)
    return {'ids':ids,'first':len(prefix),'content_ends':[len(x) for x in cids],
            'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest()}


def prepare(root,tok):
    source_path=root/'data/E60-experiment1.csv';raw=list(csv.DictReader(source_path.open()));assert len(raw)==362
    cells=defaultdict(list)
    for r in raw:cells[SCENARIO_MAP[r['scenario']],{'lowPr':'low','highPr':'high'}[r['context']],r['form']].append(r)
    assert len(cells)==24
    codebook={r['column']:r for r in csv.DictReader((root/'data/E60-codebook.csv').open())}
    for k,t in MOTIVES:assert t in codebook[k]['description'] and codebook[k]['group']=='task3_multiplechoice'
    original={tuple(r[k] for k in ('scenario','context','utterance','attribute')):r['prompt'] for r in json.loads((root/'data/E60-original-social-prompts.json').read_text())}
    rows=[];nulls={}
    for alias in ('original','one-instruction'):
        suffix='' if alias=='original' else '\n'+CONTROL
        for interface in ('bare','common-chat'):
            for name,c,u in itertools.product(SCENARIOS,CONTEXTS,UTTERANCES):
                people=cells[name,c,u];scenario=SCENARIOS[name]
                dialogue=scenario[c]+'\n'+scenario[u]
                for attribute in ATTRIBUTES:
                    text=build_minimal_prompt(scenario,c,u,attribute);assert text==original[name,c,u,attribute]
                    counts=Counter(int(r[attribute.replace('-','_')]) for r in people)
                    targets=list(map(str,range(1,8)))
                    rows.append({'id':'/'.join((alias,interface,name,c,u,attribute)),'alias':alias,'interface':interface,'kind':'trait',
                        'scene':name,'context':c,'utterance':u,'attribute':attribute,'human_counts':[counts[j] for j in range(1,8)],
                        'human_n':len(people),'targets':targets,'plan':sequences(tok,text+suffix,targets,interface)})
                speaker=scenario['speaker'];number=scenario[u].split('"')[1]
                alternative=scenario['precise' if u=='approx' else 'approx'].split('"')[1]
                # Keep the ten jointly presented options; each binary readout is a
                # declared adaptation, not the original joint-checkbox procedure.
                text=(dialogue+f'\nWhy do you think {speaker} used "{number}" rather than "{alternative}"?\n'
                      'Which of the following, if any, do you think was a reason? Check all that apply:\n'+
                      '\n'.join('- '+t for _,t in MOTIVES))
                for k,t in MOTIVES:
                    yes=sum(int(r[k]) for r in people);assert all(r[k] in ('0','1') for r in people)
                    query=text+f'\nFor the option "{t}", would you select this option?\nReply with only Yes or No.'+suffix
                    targets=['Yes','No']
                    rows.append({'id':'/'.join((alias,interface,name,c,u,k)),'alias':alias,'interface':interface,'kind':'motive',
                        'scene':name,'context':c,'utterance':u,'attribute':k,'human_counts':[yes,len(people)-yes],
                        'human_n':len(people),'targets':targets,'plan':sequences(tok,query,targets,interface)})
            for kind,targets in [('number-copy',list(map(str,range(1,8)))),('binary-copy',['Yes','No'])]:
                for j,t in enumerate(targets):
                    text=f'The required response is exactly "{t}". Copy only that response; do not give any other answer.'+suffix
                    rows.append({'id':'/'.join((alias,interface,kind,t)),'alias':alias,'interface':interface,'kind':kind,
                        'expected_index':j,'targets':targets,'plan':sequences(tok,text,targets,interface)})
            for kind,targets in [('trait',list(map(str,range(1,8)))),('motive',['Yes','No'])]:
                text=('The dialogue is not provided.\n'+('Rate how competent the speaker sounds on a 1 to 7 scale. Reply with only the number.' if kind=='trait' else 'Was lack of exact knowledge a reason for the wording? Reply with only Yes or No.'))+suffix
                nulls['/'.join((alias,interface,kind))]=sequences(tok,text,targets,interface)
    assert len(rows)==len({r['id'] for r in rows})==1572
    audit={'n_natural':1536,'n_copy_controls':36,'n_scenes':6,'n_original_condition_cells':24,'n_human_participants':362,
           'source_sha256':sha(source_path),'motives':MOTIVES,'control_instruction':CONTROL,
           'task3_is_binary_adaptation':True,'counts_are_listener_ratings_not_truth':True}
    return rows,audit,nulls


if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'results/E61-source-preflight.json';assert not path.exists()
    audits={};families={};prepared={}
    parent=json.loads((Path(__file__).resolve().parents[1]/'results/E60-social-source-audit.json').read_text())
    assert parent['n_min_prompts']==144 and all(z['absolute_delta']<1e-12 for z in parent['author_function_arithmetic_parity'])
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];p=ROOT/'models'/cp
        marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text());assert marker['model']==m['id'] and marker['revision']==m['sha']
        tok=AutoTokenizer.from_pretrained(common_path(ROOT,m),local_files_only=True)
        native=AutoTokenizer.from_pretrained(p,local_files_only=True);assert native.backend_tokenizer.to_str()==tok.backend_tokenizer.to_str()
        if m['family'] not in prepared:prepared[m['family']]=prepare(ROOT,tok)
        rows,audit,nulls=prepared[m['family']];h=fingerprint(rows,nulls);assert families.setdefault(m['family'],h)==h
        maximum=max(len(ids) for r in rows for ids in r['plan']['ids']);assert maximum<AutoConfig.from_pretrained(p,local_files_only=True).max_position_embeddings
        audits[cp]={'input_sha256':h,'source_audit':audit,'max_tokens':maximum}
    path.write_text(json.dumps({'models':specs(ROOT),'audits':audits,'helper_sha256':sha(Path(__file__)),
                               'dependencies':dependencies(),'gate_pass':True},indent=2)+'\n')
    print(json.dumps({cp:v['max_tokens'] for cp,v in audits.items()}))
