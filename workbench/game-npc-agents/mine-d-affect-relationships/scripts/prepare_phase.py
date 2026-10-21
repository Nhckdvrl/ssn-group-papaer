#!/usr/bin/env python3
"""Select paired native LongEvoRoleBench examples; no authored scenarios."""
import argparse,json,hashlib,sys,importlib.util
from pathlib import Path
from collections import defaultdict,deque,Counter

def h(s):return hashlib.sha256(('D-E02-2026-10-22-v1|'+s).encode()).hexdigest()
def wr(p,rs):
 with Path(p).open('w') as f:
  for r in rs:f.write(json.dumps(r,ensure_ascii=False)+'\n')

def main():
 a=argparse.ArgumentParser();a.add_argument('--phase-repo',required=True);a.add_argument('--dataset',required=True);a.add_argument('--assets',required=True);a.add_argument('--manifest',required=True);args=a.parse_args()
 spec=importlib.util.spec_from_file_location('native_phase_prompt',Path(args.phase_repo)/'evaluation/predict_prompt.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 root=Path(args.dataset)/'processed';selected=[];tasks=[];refs=[];hashes={}
 for corpus in ['Friends','TheOffice','HPD','StarTrek_TNG']:
  for split in ['random_test','ood_test']:
   variants={}
   for mode,folder in [('base','m1_context_only'),('raw_profile','m2_raw_profile'),('naive_rewrite','m3_naive_rewrite'),('phase_tree','m6_phase_tree')]:
    path=root/corpus/folder/(split+'.json');data=json.loads(path.read_text());variants[mode]={r['question_id']:r for r in data};assert len(variants[mode])==len(data)
    hashes[str(path.relative_to(root.parent))]=hashlib.sha256(path.read_bytes()).hexdigest()
   common=set.intersection(*(set(d) for d in variants.values()));strata=defaultdict(list)
   for qid in common:strata[variants['base'][qid]['role']].append(qid)
   queues=[deque(sorted(v,key=h)) for k,v in sorted(strata.items(),key=lambda x:h(x[0]))]
   chosen=[]
   while len(chosen)<8:
    n=0
    for q in queues:
     if q and len(chosen)<8:chosen.append(q.popleft());n+=1
    if not n:raise ValueError('not enough cases')
   for qid in chosen:
    base=variants['base'][qid];selected.append(dict(corpus=corpus,split=split,question_id=qid,role=base['role']))
    refs.append(dict(question_id=qid,corpus=corpus,split=split,sample=variants['phase_tree'][qid]))
    for mode,d in variants.items():
     sample=d[qid];assert sample['input']==base['input'] and sample['output']==base['output'] and sample['role']==base['role']
     prompt=mod.build_prompt(sample,'baseline' if mode=='base' else 'profile')
     tasks.append(dict(task_id=qid+'__'+mode,question_id=qid,corpus=corpus,split=split,role=base['role'],mode=mode,messages=[dict(role='user',content=prompt)],profile_chars=0 if mode=='base' else len(sample.get('profile_text',''))))
 out=Path(args.assets);out.mkdir(parents=True,exist_ok=True);wr(out/'tasks.jsonl',tasks);wr(out/'references.jsonl',refs)
 manifest=dict(n_questions=len(selected),n_tasks=len(tasks),n_roles=len({(r['corpus'],r['role']) for r in selected}),selected=selected,source_hashes=hashes,task_sha256=hashlib.sha256((out/'tasks.jsonl').read_bytes()).hexdigest(),selection='8 per corpus×split, role round-robin, fixed SHA256 order; all four variants paired, no outcome filtering')
 Path(args.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');print({k:v for k,v in manifest.items() if k not in ['source_hashes','selected']})

if __name__=='__main__':main()
