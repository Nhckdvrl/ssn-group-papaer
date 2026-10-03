"""E43: original Experiment 2 materials and conditional human norms, no new labels."""
import collections, hashlib, json, re
from pathlib import Path
import openpyxl
from openpyxl.utils.escape import unescape
from iqap_data import common_model as generic_common
from projection_budget_data import specs

HERE=Path(__file__).resolve().parents[1]
CLARIFICATION=('Evaluate the requested target separately: what the speaker committed to conveying, '
               'whether the reported facts are true, and how reliable the speaker is are distinct judgments.')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def display(text):return unescape(str(text)).replace('\\n','\n').replace('\r','')
def norm(text):return ' '.join(display(text).lower().split())
def table(path):
    it=iter(openpyxl.load_workbook(path,read_only=True,data_only=True).active.values)
    header=next(it);return [dict(zip(header,z)) for z in it]

def prepare(root):
    src=root/'upstream/implicit-dominance-2026';folder=src/'experiment-2'
    transpath=HERE/'results/E40-dialogue-transcriptions.json'
    trans=json.loads(transpath.read_text())['dialogues'];materials={};source_hashes={}
    for path in sorted(folder.glob('*.xlsx')):
        source_hashes[path.name]=sha(path)
        for r in table(path):
            if r['question_type'] not in ['literal','meaning']:continue
            key=(r['speaker'],r['type_SOA'],r['question_type'])
            if key in materials:
                assert all(norm(materials[key][k])==norm(r[k]) for k in ['context','picture','actual_event','Literal_question','Yes_No'])
            else:materials[key]=r
    assert len(materials)==64
    human_path=src/'Experiment_2_data.xlsx';all_human=table(human_path);by=collections.defaultdict(list)
    for r in all_human:by[r['participants']].append(r)
    retained={k:v for k,v in by.items() if sum(r['is_corr_q1']==0 for r in v)<=2}
    human=[r for vs in retained.values() for r in vs if r['ans_match']==1]
    assert len(retained)==93 and len(human)==703
    cell=collections.defaultdict(list);trust=collections.defaultdict(list)
    for r in human:
        key=r['speaker'],r['type_SOA'],r['question_type'];m=materials[key]
        assert all(norm(r[k])==norm(m[k]) for k in ['context','picture','actual_event','Literal_question','Yes_No'])
        assert r['mouse.clicked_name'].lower()==r['Yes_No'].lower()
        assert int(r['SoA_explicit'])==int('literal_true' in r['type_SOA'])
        assert int(r['SoA_implicit'])==int('meaning_true' in r['type_SOA'])
        cell[key].append(float(r['slider_commitment.response']))
        trust[key[:2]].append(float(r['slider_trust.response']))
    assert set(cell)==set(materials) and len(trust)==32
    rows=[];base={};images={}
    for key in sorted(materials):
        speaker,corner,target=key;m=materials[key];image=Path(m['picture']).name;d=trans[image]
        assert d['contact']==speaker
        images[image]=sha(folder/image)
        story=display(m['context'])+'\n\nQuestion: '+d['question']+'\n'+speaker+': '+d['answer']
        facts=display(m['actual_event']);yesno=m['Yes_No'].capitalize()
        base[(speaker,corner)]={'speaker':speaker,'corner':corner,'literal_true':int('literal_true' in corner),
            'meaning_true':int('meaning_true' in corner),'image':image,'story':story,'facts':facts,'source_answer':yesno}
        question=(display(m['Literal_question']) if target=='literal' else
                  'To what extent do you think '+speaker+' committed to answering '+yesno+' to the question?')
        vals=cell[key]
        for condition in ['original','clarification']:
            directive=('\n'+CLARIFICATION if condition=='clarification' else '')
            prompt=story+'\n\nActual event:\n'+facts+directive+'\n\n'+question+\
                '\nRate from 1 (Not committed) to 100 (Fully committed). Reply with only one integer.\nAnswer:'
            rows.append({**base[(speaker,corner)],'id':'/'.join([speaker,corner,target,condition]),
                'task':'commitment','target':target,'condition':condition,'prompt':prompt,
                'human_n':len(vals),'human_mean':sum(vals)/len(vals),'human_values':vals,'min_rating':1,'max_rating':100})
    assert len(rows)==128
    for (speaker,corner),b in sorted(base.items()):
        vals=trust[(speaker,corner)]
        for condition in ['original','clarification']:
            directive=('\n'+CLARIFICATION if condition=='clarification' else '')
            prompt=b['story']+'\n\nActual event:\n'+b['facts']+directive+'\n\nIs '+speaker+\
                ' a reliable person?\nRate from 0 (No) to 100 (Yes). Reply with only one integer.\nAnswer:'
            rows.append({**b,'id':'/'.join([speaker,corner,'trust',condition]),'task':'trust','target':'trust',
                'condition':condition,'prompt':prompt,'human_n':len(vals),'human_mean':sum(vals)/len(vals),
                'human_values':vals,'min_rating':0,'max_rating':100})
    assert len(rows)==192
    for speaker in sorted({k[0] for k in base}):
        b=base[(speaker,'literal_true_meaning_true')]
        prompt=b['story']+'\n\nWhat did '+speaker+' mean to say in reply to the question? Reply with only Yes or No.\nAnswer:'
        rows.append({'id':speaker+'/comprehension','speaker':speaker,'task':'comprehension','target':'meaning',
            'condition':'original','prompt':prompt,'gold':b['source_answer']})
    for (speaker,corner),b in sorted(base.items()):
        # These two affirmative claims are transcribed FROM the actual-event true/true source,
        # not invented from model outputs. No such claim is shown in comprehension/rating calls.
        truefacts=base[(speaker,'literal_true_meaning_true')]['facts'].strip()
        match=re.fullmatch(r'It is revealed that (.*?)\.\s+Additionally, it is revealed that (.*?)\.',truefacts,re.S)
        assert match,truefacts
        for target,claim,gold in [('literal',match[1],b['literal_true']),('meaning',match[2],b['meaning_true'])]:
            prompt='Actual event:\n'+b['facts']+'\n\nTarget claim: '+claim+\
                '.\nAccording to the actual event, is the target claim true? Reply with only Yes or No.\nAnswer:'
            rows.append({'id':'/'.join([speaker,corner,'fact',target]),'speaker':speaker,'corner':corner,
                'task':'fact-verifier','target':target,'condition':'original','prompt':prompt,'gold':'Yes' if gold else 'No'})
    assert len(rows)==264 and len({r['id'] for r in rows})==264
    audit={'source':'OSF unmy6 Experiment 2','source_table_sha256':source_hashes,
        'human_sha256':sha(human_path),'human_n':703,'human_participants':93,'commitment_cells':64,'trust_cells':32,
        'image_sha256':images,'transcription_sha256':sha(transpath),'source_psyexp_sha256':sha(src/'experiment_2.psyexp'),
        'clarification':CLARIFICATION,'n_each_interface':len(rows),'prompt_sha256':hashlib.sha256(json.dumps([r['prompt'] for r in rows]).encode()).hexdigest(),
        'limits':['Text adaptation; UI/timestamps omitted. Root visual transcription rechecked but not independently audited.',
            'Human norms condition on correct initial interpretation; no model-based filtering.',
            'Trust norms pool both preceding commitment probes; model calls have no such previous answer.']}
    return rows,audit

def common_model(root,cp):
    return root/'models/Mistral-7B-Instruct-v0.3' if cp.startswith('Mistral') else generic_common(root,cp)

def inputs(tok,rows,interface,cp):
    texts=[]
    for r in rows:
        text=r['prompt']
        if interface=='common-chat':
            text=tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        elif cp.startswith('Mistral'):text=tok.bos_token+text
        texts.append(text)
    ids=[tok.encode(t,add_special_tokens=False) for t in texts]
    assert all(r['prompt'] in t for r,t in zip(rows,texts))
    return texts,ids,hashlib.sha256(json.dumps(ids).encode()).hexdigest()

def parse(text,row):
    text=text.strip()
    if row['task'] in ['comprehension','fact-verifier']:
        return text.capitalize() if text.casefold() in ['yes','no'] else None
    if not re.fullmatch(r'[0-9]+',text):return None
    rating=int(text)
    return rating if row['min_rating']<=rating<=row['max_rating'] else None

if __name__=='__main__':
    import argparse
    from transformers import AutoTokenizer
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();rows,audit=prepare(a.root);models={};seen={}
    for cp,mid,revision,parent in specs(a.root):
        tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
        models[cp]={k:inputs(tok,rows,k,cp)[2] for k in ['bare','common-chat']}
        family='OLMoE' if cp.startswith('OLMoE') else 'Mistral' if cp.startswith('Mistral') else 'Qwen2.5' if cp.startswith('Qwen2.5') else cp
        if family in seen:assert seen[family]==models[cp]
        seen[family]=models[cp]
    a.output.write_text(json.dumps({'audit':audit,'models':models,'gate_pass':True},indent=2)+'\n')
    print(json.dumps({'gate_pass':True,'n_per_model':528,'models':len(models)}))
