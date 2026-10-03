"""E63 declared expansion of unambiguous public Exp2 specifications only."""
import csv
import itertools
import json
import re
import unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from transformers import AutoTokenizer,AutoConfig
from wording_data import specs,common_path,sha,fingerprint
from social_motive_data import sequences,CONTROL
from run_followup_queue import ROOT

NAMES=[('Kim','John'),('Mary','Will'),('Anne','Steve'),('Heather','Tom'),('Jen','Fred'),('Leah','Ken'),
       ('Mia','Rick'),('Amy','Sal'),('Greg','Susan'),('Bob','Lucy'),('Albert','Cynthia'),('Jeff','Molly'),('Jay','Nancy'),('Dan','Liz')]
TRAITS=['Knowledgeable','Considerate','Competent','Likable']

def dependencies():
    d={f:sha(Path(__file__).with_name(f)) for f in ['wording_data.py','social_motive_data.py','audit_violation_source.py']}
    for f in ['E62-items-exp2.pdf','E62-items-exp2.txt','E62-exp2.csv']:d[f]=sha(ROOT/'data'/f)
    d['E62-audit']=sha(Path(__file__).resolve().parents[1]/'results/E62-violation-source-audit.json')
    return d

def source(root):
    txt=(root/'data/E62-items-exp2.txt').read_text()
    blocks={int(m.group(1)):m.group(2).strip() for m in re.finditer(r'Scenario (\d+)\.\s*(.*?)(?=Scenario \d+\.|\Z)',txt,re.S)}
    assert set(blocks)==set(range(1,17))
    raw=list(csv.DictReader((root/'data/E62-exp2.csv').open()));assert len(raw)==1488
    cells=defaultdict(list)
    for r in raw:cells[int(r['Item']),r['Reason.for.Violation'],r['Informativeness']].append(r)
    items=[]
    for i in range(1,15):
        b=unicodedata.normalize('NFKC',blocks[i]);assert b.count('{')==b.count('}')==1 and b.count('[')==b.count(']')==1
        opener=re.search(r'\{([^{}]+)\}',b).group(1).split('/');assert len(opener)==2
        info=re.search(r'\[([^\[\]]+)\]',b).group(1)
        asker,speaker=NAMES[i-1]
        for reason,level in itertools.product(['Unw','Ina'],['High','Low']):
            chosen=opener[reason=='Ina'];text=b.replace('{'+ '/'.join(opener)+'}',chosen).replace('['+info+']',info if level=='High' else '')
            # Declared presentation changes only. Keep lexical errors, including "ver".
            text=text.replace('“','').replace('”','').replace('"','').replace('+Info: ','')
            if i==6:
                at=text.index(chosen);text=text[:at]+speaker+': '+text[at:]
            text=' '.join(text.split())
            assert '{' not in text and '}' not in text and '[' not in text and ']' not in text
            assert (speaker+':') in text and asker+':' in text
            assert chosen in text and text.count(chosen)==1
            items.append({'scene':str(i),'context':reason,'utterance':level,'dialogue':text,
                          'speaker':speaker,'asker':asker,'opening_choices':opener,'chosen_opening':chosen,
                          'people':cells[i,reason,level]})
        for level in ['High','Low']:
            pair=[r for r in items if r['scene']==str(i) and r['utterance']==level]
            assert len(pair)==2
            assert pair[0]['dialogue'].replace(pair[0]['chosen_opening'],'<OPENING>')==pair[1]['dialogue'].replace(pair[1]['chosen_opening'],'<OPENING>')
    assert len(items)==56
    return items

def question(attribute,speaker,asker):
    return {'Knowledgeable':f'How knowledgeable do you think {speaker} is in this conversation?',
        'Considerate':f'How considerate towards {asker} do you think {speaker} is in this conversation?',
        'Competent':f'How competent do you think {speaker} is as a person?',
        'Likable':f'How likable do you think {speaker} is as a person?'}[attribute]

def prepare(root,tok):
    items=source(root);rows=[];nulls={}
    for alias,interface in itertools.product(['original','one-instruction'],['bare','common-chat']):
        suffix='' if alias=='original' else '\n'+CONTROL
        for item in items:
            for attribute in TRAITS:
                query=question(attribute,item['speaker'],item['asker'])+'\nRate from 1 (lowest) to 7 (highest). Reply with only the number.'
                targets=list(map(str,range(1,8)));counts=Counter(int(r[attribute]) for r in item['people'])
                rows.append({'id':'/'.join((alias,interface,item['scene'],item['context'],item['utterance'],attribute)),
                    'alias':alias,'interface':interface,'scene':item['scene'],'context':item['context'],'utterance':item['utterance'],
                    'kind':'trait','attribute':attribute,'human_counts':[counts[j] for j in range(1,8)],'human_n':len(item['people']),
                    'targets':targets,'plan':sequences(tok,item['dialogue']+'\n'+query+suffix,targets,interface)})
                nulls['/'.join((alias,interface,attribute,item['scene']))]=sequences(tok,'The dialogue is not provided.\n'+query+suffix,targets,interface)
            for k,opening in enumerate(item['opening_choices']):
                targets=['Yes','No'];correct=0 if opening==item['chosen_opening'] else 1
                text=item['dialogue']+f'\nDid {item["speaker"]} actually say "{opening}" as their opening statement?\nReply with only Yes or No.'+suffix
                rows.append({'id':'/'.join((alias,interface,item['scene'],item['context'],item['utterance'],'quote'+str(k))),
                    'alias':alias,'interface':interface,'scene':item['scene'],'context':item['context'],'utterance':item['utterance'],
                    'kind':'quote','attribute':'quote'+str(k),'expected_index':correct,'targets':targets,'plan':sequences(tok,text,targets,interface)})
        for kind,targets in [('number-copy',list(map(str,range(1,8)))),('binary-copy',['Yes','No'])]:
            for j,t in enumerate(targets):
                text=f'The required response is exactly "{t}". Copy only that response; do not give any other answer.'+suffix
                rows.append({'id':'/'.join((alias,interface,kind,t)),'alias':alias,'interface':interface,'kind':kind,
                             'expected_index':j,'targets':targets,'plan':sequences(tok,text,targets,interface)})
    assert len(rows)==len({r['id'] for r in rows})==1380
    audit={'n_natural':1344,'n_copy':36,'n_scenes':14,'n_conditions':56,'excluded_source_scenes':[15,16],
           'exclusion_before_any_predictions':True,'source_version':'public OSF Exp2 PDF specification',
           'source_words_unchanged':True,'quote_is_literal_reading_not_semantic_knowledge':True,
           'rendering':'NFKC printed ligatures; strip layout double quotes/+Info label; collapse whitespace; add source-identified Ken label in scene6',
           'n_null_trait_frames':224}
    return rows,audit,nulls

if __name__=='__main__':
    output=Path(__file__).resolve().parents[1]/'results/E63-source-preflight.json';assert not output.exists()
    assert json.loads((output.parent/'E62-violation-source-audit.json').read_text())['source_arithmetic_gate_pass']
    audits={};families={};prepared={}
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];p=ROOT/'models'/cp;marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text())
        assert marker['model']==m['id'] and marker['revision']==m['sha']
        tok=AutoTokenizer.from_pretrained(common_path(ROOT,m),local_files_only=True);native=AutoTokenizer.from_pretrained(p,local_files_only=True)
        assert native.backend_tokenizer.to_str()==tok.backend_tokenizer.to_str()
        if m['family'] not in prepared:prepared[m['family']]=prepare(ROOT,tok)
        rows,audit,nulls=prepared[m['family']];h=fingerprint(rows,nulls);assert families.setdefault(m['family'],h)==h
        maximum=max(len(ids) for r in rows for ids in r['plan']['ids']);assert maximum<AutoConfig.from_pretrained(p,local_files_only=True).max_position_embeddings
        audits[cp]={'source_audit':audit,'input_sha256':h,'max_tokens':maximum}
    output.write_text(json.dumps({'models':specs(ROOT),'gate_pass':True,'audits':audits,'helper_sha256':sha(Path(__file__)),
                                 'dependencies':dependencies()},indent=2)+'\n')
    print(json.dumps({k:v['max_tokens'] for k,v in audits.items()}))
