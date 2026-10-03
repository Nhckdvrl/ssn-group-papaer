"""Pinned main-task strings and actual-fact human matching; no model-made gold."""
import ast,csv,hashlib,json,re
from collections import defaultdict

REVISION='ad2c36d75f9d14d192d193f7db919035c41619bd'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def factkey(s):return re.sub(r'\s+',' ',s.strip().rstrip('.')).casefold()
def parse_rating(s):
    if not re.fullmatch(r'(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)',s.strip()):return None
    x=float(s.strip());return x if 0<=x<=1 else None

def prepare(root):
    repo=root/'upstream/llm_belief';paths=['stimuli/prior_rate.csv','stimuli/projection_rate_certainty.csv',
        'data/prior/prior_means_human.csv','data/projection/projection_prior.csv','model.py']
    table={p:list(csv.DictReader((repo/p).open())) for p in paths[:-1]}
    constants={}
    for node in ast.parse((repo/'model.py').read_text()).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ['system_prompt','prior_info','projection_info']:
                    constants[target.id]=ast.literal_eval(node.value)
    assert len(constants)==3
    prior=table[paths[0]];proj=table[paths[1]];human=table[paths[3]]
    assert len(prior)==80 and len(proj)==1680 and len(human)==7436
    assert len({(r['item'],r['embedded'],r['prior_type']) for r in prior})==80
    assert len({(r['item'],r['embedded_type'],r['prior_type'],r['verb']) for r in proj})==1680
    hfacts=defaultdict(set);hratings=defaultdict(list)
    for r in human:
        if r['short_trigger']=='MC':continue
        verb={'be_annoyed':'annoyed','be_right':'right'}.get(r['short_trigger'],r['short_trigger'])
        label={'factH':'high_prior','factL':'low_prior'}.get(r['prior_type'],r['prior_type'])
        hfacts[r['content'].casefold(),label].add(factkey(r['prior_fact']))
        hratings[r['content'].casefold(),label,verb].append(float(r['projective']))
    assert len(hfacts)==40 and all(len(v)==1 for v in hfacts.values())
    hmeans={}
    for r in table[paths[2]]:
        item=r['eventItem'].split()[0].casefold();key=item,r['prior_type'];assert key not in hmeans
        hmeans[key]=float(r['Mean'])
    rows=[];mismatches=[]
    for task,rs in [('prior',prior),('projection',proj)]:
        for i,r in enumerate(rs):
            embedded=r.get('embedded',r.get('embedded_type'));item=r['item'].casefold()
            matches=[label for (name,label),texts in hfacts.items() if name==item and factkey(r['prior']) in texts]
            assert len(matches)==1,(task,i,r['prior'],matches)
            actual=matches[0]
            if actual!=r['prior_type']:mismatches.append({'task':task,'index':i,'item':r['item'],
                'source_prior_type':r['prior_type'],'actual_fact_human_prior_type':actual,'fact':r['prior']})
            if task=='projection':
                assert r['prompt']=='Fact: '+r['prior']+' Sentence: '+r['target']+' Question: '+r['question']
                speaker=r['target'].split(' asks: ')[0];assert r['question'].startswith('Is '+speaker+' certain that ')
                h=hratings.get((item,actual,r['verb'])) if embedded=='p' and r['verb']!='polar' else None
                human_mean=sum(h)/len(h) if h else None
            else:
                assert r['background'] in r['prompt']
                assert r['prior'] in r['prompt']
                human_mean=hmeans[item,actual] if embedded=='p' else None
            text=constants['prior_info' if task=='prior' else 'projection_info']+r['prompt']
            rows.append({**r,'id':task+':'+str(i),'task':task,'embedded_type':embedded,
                'actual_fact_human_prior_type':actual,'human_mean':human_mean,'user_text':text,
                'system_text':constants['system_prompt']})
    assert len(mismatches)==4 and all(x['task']=='prior' and x['item']=='Josie' for x in mismatches)
    assert sum(r['human_mean'] is not None for r in rows)==840
    return rows,{'source_revision':REVISION,'source_sha256':{p:sha(repo/p) for p in paths},
        'n':1760,'n_with_original_human_mean':840,'human_projection_match_p_rows':800,'human_prior_match_p_rows':40,
        'source_label_fact_mismatches':mismatches,'source_labels_preserved':True,
        'prior_instruction_duplicate_preserved':True,'n_unique_human_facts':40}

def render(tok,r,interface):
    if interface=='bare':return r['system_text']+'\n\n'+r['user_text']+'\nAnswer:'
    return tok.apply_chat_template([{'role':'system','content':r['system_text']},
        {'role':'user','content':r['user_text']}],tokenize=False,add_generation_prompt=True,enable_thinking=False)

def inputs(tok,rows,interface):
    texts=[render(tok,r,interface) for r in rows];ids=[tok.encode(t,add_special_tokens=False) for t in texts]
    return texts,ids,hashlib.sha256(json.dumps(ids).encode()).hexdigest()
