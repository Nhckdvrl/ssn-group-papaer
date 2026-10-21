#!/usr/bin/env python3
"""Native PUF criterion with complete actor-available before-state, no gold outputs."""
import argparse,json,hashlib,importlib.util
from pathlib import Path

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);vendor=root/'vendor/EvolvingWorld';native=load('ew_native_utils',vendor/'simulation/utils.py');prompts=load('ew_native_prompts',vendor/'evaluation/prompts.py')
 read=lambda p:[json.loads(l) for l in p.read_text().splitlines()]
 originals={r['task_id']:r for r in read(root/'data/update_D-E04/tasks.jsonl')};tasks=[];qualified=[]
 for condition in ['original','identity_line']:
  for model in ['qwen3_8b','qwen3_32b']:
   base=root/'runs/D-E04';base=base/'identity_line' if condition=='identity_line' else base;run=base/model;assert json.loads((run/'metadata.json').read_text())['complete'];rows=read(run/'responses.jsonl');assert len(rows)==64
   for r in rows:
    t=originals[r['task_id']];user=t['messages'][1]['content'];qid=f"puf/{model}/{condition}/{r['task_id']}";meta=dict(task_id=qid,question_id=r['task_id'],actor_model=model,condition=condition,book_name=r['book_name'],role=r['role'],scene_index=r['scene_index'],candidate_sha256=hashlib.sha256(r['response'].encode()).hexdigest());valid=False
    try:
     o=native.extract_json_fragment(r['response']);flag=o.get('profile_updated');p=o.get('updated_profile');profile=native.dict_to_markdown_text(p) if isinstance(p,(dict,list)) else p
     valid=type(flag) is bool and ((flag and isinstance(profile,str) and bool(profile.strip())) or (not flag and 'updated_profile' in o and p is None)) and 'hidden_tracker' in o and isinstance(o.get('short_description'),str) and bool(o['short_description'].strip())
    except Exception:pass
    qualified.append(dict(meta,structural_valid=valid))
    if not valid:continue
    after=dict(profile_updated=flag,profile_after=profile if flag else '(Unchanged from the scene-start profile)',hidden_tracker=o['hidden_tracker'],description=o['short_description'])
    body=f"Target character record: {r['role']}\n\n## Complete input available to the updater\n{user}\n\n## Persisted state after this scene\n{json.dumps(after,ensure_ascii=False,indent=2)}\n\n{prompts.SINGLE_METRIC_OUTPUT_FORMAT}"
    tasks.append(dict(meta,messages=[dict(role='system',content=prompts.build_per_scene_system_prompt('PUF')),dict(role='user',content=body)]))
 tasks.sort(key=lambda t:hashlib.sha256(('PUF-blind|'+t['task_id']).encode()).hexdigest());assert len(tasks)==len({t['task_id'] for t in tasks})
 out=Path(args.out);out.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks));out.with_suffix('.qualification.json').write_text(json.dumps(dict(n_candidates=256,n_qualified=len(tasks),system_sha256=hashlib.sha256(prompts.build_per_scene_system_prompt('PUF').encode()).hexdigest(),adapter='Native PUF system/score formula; complete original actor input + runtime-normalized post-state; no gold/model/condition in judge messages.',details=qualified),ensure_ascii=False,indent=2)+'\n');print('PUF qualified',len(tasks),'/256',flush=True)
if __name__=='__main__':main()
