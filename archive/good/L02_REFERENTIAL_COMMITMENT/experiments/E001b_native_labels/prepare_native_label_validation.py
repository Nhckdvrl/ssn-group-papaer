"""Freeze an exploratory format validation after E001a's Mistral A-only output."""
from pathlib import Path
import datetime,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    src=ROOT/'experiments/E001a_interpretation';out=ROOT/'experiments/E001b_native_labels';out.mkdir(exist_ok=False)
    jobs=[]
    for j in map(json.loads,(src/'jobs.jsonl').read_text().splitlines()):
        if j['order']!='DNI_INI':continue
        prompt=j['prompt'].rsplit('Options:',1)[0]+'Return exactly DNI or INI, without explanation.'
        jobs.append({'job_id':j['sample_id']+'|'+j['condition'],'sample_id':j['sample_id'],'condition':j['condition'],'prompt':prompt})
    assert len(jobs)==84
    (out/'jobs.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in jobs))
    shutil.copyfile(src/'samples.jsonl',out/'samples.jsonl')
    p={'id':'E001b','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'status':'FROZEN_BEFORE_NATIVE_LABEL_OUTPUTS','trigger':'E001a Mistral argmax chose A on all 168 jobs; all 42 examples show label-order disagreement in each condition.',
       'scope':'Exploratory measurement validation, not H01/H02/H03 or a new method/novelty claim. E001a results remain unchanged.',
       'alignment':['DUST 2024.findings-acl.572 sections 5-6: prompt/measurement sensitivity','SemEval S10-1008: native interpretation labels'],
       'selection':'Exactly the same 42 samples, each sentence/full context; no output-dependent sample exclusions.',
       'change':'Remove arbitrary A/B mapping; request direct DNI/INI free generation with no explanation. Keep definitions, role, target and context identical.',
       'models':json.loads((src/'protocol.json').read_text())['models'],
       'inference':'BF16 SDPA, greedy unconstrained generation, max_new_tokens=8, no prompt truncation, Qwen thinking disabled; no examples or prompt tuning.',
       'scoring':'Strip outer whitespace and accept only exact DNI or INI. All other responses remain invalid and count incorrect in the all-42 denominator. Report confusion, complete-pair accuracy and context transitions. No population CI.',
       'limitations':['Exploratory after a diagnosed A/B failure','One story and gold-balanced frame-role challenge','Free generation differs from conditional single-token likelihood; not an equal-budget method comparison','Native-label accuracy does not measure filler support'],
       'artifact_hashes':{n:sha(out/n) for n in ('jobs.jsonl','samples.jsonl')},
       'source_protocol_sha256':sha(src/'protocol.json')}
    (out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n');shutil.copyfile(__file__,out/Path(__file__).name)
    print('Frozen',len(jobs),'jobs per model')
