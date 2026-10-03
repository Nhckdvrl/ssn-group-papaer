"""E44/E45: frozen public BWIM materials, original confidence protocol adaptation."""
import csv,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path('/data1/xiangding/work/pragmatic-inference-calibration')
SYSTEM=('CONTEXT: Grid: 9x9 cells. Origin="middle square": center (0,0), is highlighted. '
    'The grid is the x–z plane. In front of you is the bottom left corner (-400,0,400) and '
    'the bottom right corner (400,0,400). Top right corner is (400,0,-400), top left corner is (-400,0,-400). '
    'Valid x,z:[-400,-300,-200,-100,0,100,200,300,400]. Y(ground)=50; each extra block adds +100; '
    'valid y values are [50,150,250,350,450]. The grid may or may not contain an existing structure. '
    '"Existing structure: nan" means that the grid is empty. "A stack" means more than one block.\n'
    'Output:"Coordinates:Color,x,y,z; Color,x,y,z;Rating:"; items separated by ";"; no spaces; '
    'write coordinates of all blocks that are on the grid, including the initial coordinates; color should be capitalized.')

def structure(text):
    blocks=[]
    for b in text.strip().strip(';').split(';'):
        v=b.strip().split(',')
        if len(v)!=4 or not v[0].strip().isalpha():return None
        try:xyz=tuple(int(x.strip()) for x in v[1:])
        except ValueError:return None
        if xyz[0] not in range(-400,401,100) or xyz[2] not in range(-400,401,100) or xyz[1] not in [50,150,250,350,450]:return None
        blocks.append((v[0].strip().capitalize(),*xyz))
    if not blocks or len(set(blocks))!=len(blocks):return None
    return sorted(blocks)

def parse(text):
    # Whole response, only cosmetic whitespace/case of color; no extraction from prose.
    m=re.fullmatch(r'\s*Coordinates:\s*(.*?)\s*Rating:\s*([1-4])\s*;?\s*',text,re.S)
    if not m:return None
    blocks=structure(m[1]);return None if blocks is None else {'blocks':blocks,'rating':int(m[2])}

def prepare(root):
    repo=root/'upstream/build_what_i_mean';path=repo/'pragmatic_builder/building_task.py'
    spec=importlib.util.spec_from_file_location('original_bwim_task',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    files=[repo/'data'/f'List{i}_FINAL_stimuli_list.csv' for i in [1,2]]
    index={};pairs=0
    for i,p in enumerate(files,1):
        rows=list(csv.DictReader(p.open()));assert len(rows)==32
        assert sum(z['trialType']=='fully_spec' for z in rows)==8
        assert sum(z['trialType']=='color_under' for z in rows)==12
        assert sum(z['trialType']=='number_under' for z in rows)==12
        for z in rows:
            index[(i,z['trialNumber'])]=z;assert structure(z['targetStructure']) is not None
            if z['startStructure']:assert structure(z['startStructure']) is not None
        for z in rows:
            if z['trialNumber'].endswith('a'):
                other=index[(i,z['trialNumber'][:-1]+'b')]
                assert z['sentenceW']==other['sentenceW'] and z['startStructure']==other['startStructure']
                assert structure(z['targetStructure'])!=structure(other['targetStructure']);pairs+=1
    assert pairs==24
    episodes=[]
    for seed in range(4):
        trial=module.BuildingGameTask(str(files[0]),str(files[1]),seed=seed).run(None)
        seq=[]
        for bi,block in enumerate([trial['instructions_A'],trial['instructions_B']]):
            assert len(block)==20 and sum(r['trial_type']=='fully_spec' for r in block)==8
            literal=sum(r['trial_id'].endswith('a') for r in block)>0
            assert sum(r['trial_id'].endswith('a') for r in block)==(8 if literal else 0)
            for r in block:
                base=r['trial_id'][:-1] if r['trial_id'][-1] in ['a','b'] else r['trial_id']
                pragmatic=index[(r['list_id'],base+'b')]['targetStructure'] if r['trial_type']!='fully_spec' else r['target_structure']
                seq.append({**r,'seed':seed,'block':bi,'speaker_policy':'literal' if literal else 'pragmatic',
                    'pragmatic_structure':pragmatic,'gold_blocks':structure(r['target_structure']),
                    'pragmatic_blocks':structure(pragmatic)})
        assert seq[0]['speaker_policy']!=seq[20]['speaker_policy'];episodes.append(seq)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    audit={'source_repo':'https://github.com/ltl-uva/build_what_i_mean','commit':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
        'code_sha256':sha(path),'csv_sha256':{p.name:sha(p) for p in files},'n_rows':64,'identical_prompt_different_target_pairs':pairs,
        'seeds':[0,1,2,3],'n_trials_each_seed':40,'episode_sha256':hashlib.sha256(json.dumps(episodes).encode()).hexdigest(),
        'system_sha256':hashlib.sha256(SYSTEM.encode()).hexdigest(),
        'limits':['Public repo implements QA with four sequential seeds; original confidence implementation and raw predictions not released here.',
            'Confidence pilot uses paper Appendix A.1 and original material generator, fresh session per seed; not exact numerical reproduction.',
            'No API QA, no trial-level human responses. Four sequences only, not original 30-sequence estimate.',
            'Same prompt has probabilistic targets for literal partner; b-preference is not inherently an error.']}
    return episodes,audit

def user_prompt(row,transition):
    return (('You are now building with '+row['speaker']+'.\n' if transition else '')+
        'Speaker: '+row['speaker']+'\nYOUR TASK: Existing structure: '+(row['start_structure'] or 'nan')+'. '+row['instruction']+
        '\nOn a scale of 1-4, rate how certain you are that this is the structure that the previous participant saw, '
        '1 means \'not certain at all\', 4 means \'very certain\'.\nYOUR ANSWER:')

def render(tok,messages):
    text=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    # Some Mistral templates move the system into the final user text. It must stay present.
    assert SYSTEM in text
    return text,tok.encode(text,add_special_tokens=False)

def add_user(messages,text):
    if messages and messages[-1]['role']=='user':messages[-1]['content']+='\n\n'+text
    else:messages.append({'role':'user','content':text})

if __name__=='__main__':
    import argparse
    from transformers import AutoTokenizer
    from commitment_data import common_model
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();episodes,audit=prepare(a.root);models={}
    for cp in ['Qwen2.5-3B-Instruct','Qwen3-4B','Qwen3-8B','Qwen3-14B','Mistral-7B-Instruct-v0.3']:
        tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True);sample=[];maximum=0
        for seq in episodes:
            messages=[{'role':'system','content':SYSTEM}]
            for i,r in enumerate(seq):
                add_user(messages,user_prompt(r,i in [0,20]))
                text,ids=render(tok,messages);maximum=max(maximum,len(ids));sample.append(hashlib.sha256(text.encode()).hexdigest())
                gold='Coordinates:'+r['target_structure']+';Rating:4';assert parse(gold)['blocks']==r['gold_blocks']
                messages.append({'role':'assistant','content':gold})
                add_user(messages,'FEEDBACK:True; the structure you built = '+r['target_structure']+'; the correct structure = '+r['target_structure']+';')
            models[cp]={'gold_history_max_input_tokens':maximum,'prompt_sha256':hashlib.sha256(json.dumps(sample).encode()).hexdigest()}
    a.output.write_text(json.dumps({'audit':audit,'models':models,'gate_pass':True},indent=2)+'\n')
    print(json.dumps({'gate_pass':True,'audit':audit,'models':models},indent=2))
