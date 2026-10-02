"""Frozen public-source eligibility and scoring shared with E19; no provider imports."""
import hashlib,json
from collections import defaultdict
import pandas as pd

def prepare(root):
 up=root/'upstream/epitome';src=up/'scalar_implicature/data/processed/si_stimuli_qa_parallel_nums_gpt3-text-davinci-002.csv'
 trials=pd.read_csv(src).fillna('');raw=pd.read_csv(up/'scalar_implicature/data/raw/si_stimuli.csv').set_index('item')
 assert len(trials)==360 and trials.item.nunique()==40
 stimuli={};question_versions=defaultdict(int)
 for r in trials.to_dict('records'):
  item=raw.loc[r['item']];a=int(r['access']);n=str(r['n']);exp=int(r['experiment']);num='Some' if exp==1 else n
  update=item['update'].format(a=a,n=num,h='has' if num=='1' else 'have')
  expected_prior=f"{item['intro']}\nQ: {item['q_prior']}\nA:"
  assert r['prior']==expected_prior
  possible={q:f"{item['intro']}\n{update}\nQ:{item[q]}\nA:" for q in ['q_prior','q_posterior']}
  versions=[q for q,p in possible.items() if p==r['speach']];assert versions,(r['item'],a,n)
  question_versions[versions[0]]+=1
  assert r['knowledge']==f"{item['intro']}\n{update}\nQ:{item['q_knowledge']}\nA:"
  for phase in ['prior','speach','knowledge']:
   key=f"si:{r['item']}:{phase}"+(f':{exp}:{a}:{n}' if phase!='prior' else '')
   rec={'key':key,'task':'si','item':int(r['item']),'phase':phase,'experiment':exp,'access':a,'n':n,
        'prompt':r[phase],'choices':['Yes','No'] if phase=='knowledge' else list('0123')}
   if key in stimuli:assert stimuli[key]['prompt']==rec['prompt']
   else:stimuli[key]=rec
 irsrc=up/'indirect_request/data/raw/stims.csv';irs=pd.read_csv(irsrc)
 assert len(irs)==64 and irs.item.nunique()==16
 missing_ir=irs.loc[irs.critical_utterance.isna(),['item','speaker_knowledge','knowledge_cue']].to_dict('records')
 irs=irs.dropna(subset=['critical_utterance'])  # Exact eligibility in released gpt3_predict.py.
 assert len(irs)==24 and irs.item.nunique()==6
 for r in irs.to_dict('records'):
  assert r['critical_a']==('No' if r['speaker_knowledge']=='aware' else 'Yes')
  key=f"ir:{r['item']}:{r['speaker_knowledge']}:{r['knowledge_cue']}"
  stimuli[key]={'key':key,'task':'ir','item':int(r['item']),'phase':'request','speaker_knowledge':r['speaker_knowledge'],
   'knowledge_cue':r['knowledge_cue'],'gold':r['critical_a'],'choices':['Yes','No'],
   'prompt':r['passage']+'\n\n'+r['critical_utterance']+'\n\n'+r['critical_q']+'\n\n'}
 assert len(stimuli)==784
 hashes={str(p.relative_to(up)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,irsrc,up/'scalar_implicature/data/raw/si_stimuli.csv']}
 return list(stimuli.values()),trials,{'source_hashes':hashes,'released_posterior_question_versions':dict(question_versions),
  'n_trials':len(trials),'n_unique_prompts':len(stimuli),'unavailable_ir_conditions':missing_ir,
  'bare_prompt_sha256':hashlib.sha256(json.dumps([(r['key'],r['prompt']) for r in stimuli.values()],ensure_ascii=False).encode()).hexdigest()}

def original_accuracy(exp,a,n,d2,d3):
 if exp==1:return d3<0 if a==3 else d3>=0
 return {(3,3):d3>0,(3,2):d3<0,(3,1):d3<0 and d2<0,
  (2,2):d2>0 and d3>=0,(2,1):d2>=0 and d3<0,(1,1):d2>=0 and d3>=0}[a,int(n)]
