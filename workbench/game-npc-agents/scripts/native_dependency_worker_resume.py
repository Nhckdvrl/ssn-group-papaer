#!/usr/bin/env python3
"""Move an E63 worker: keep complete worlds and replay its prior decisions."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import native_dependency_roles as policy


class MissingDecision(Exception): pass


def decision_key(j):
    return tuple(j.get(k) for k in ['case_id','persona','rule','request_mode','stage','step','seed'])


def canonical_schema(value):
    if isinstance(value,dict):
        return {k:sorted(v) if k=='enum' else canonical_schema(v) for k,v in value.items()}
    if isinstance(value,list):return [canonical_schema(v) for v in value]
    return value


class Client:
    def __init__(self,source,out,model,seed,cpu):
        rows=list(map(json.loads,(source/'model_calls.jsonl').read_text().splitlines()))
        self.lookup={decision_key(r):r for r in rows};assert len(self.lookup)==len(rows)
        self.source,self.out,self.model,self.seed,self.cpu=source,out,model,seed,cpu
        self.client=None;self.replayed=0
    @property
    def calls(self):return 0 if self.client is None else self.client.calls
    @property
    def load_seconds(self):return 0 if self.client is None else self.client.load_seconds
    def batch(self,jobs):
        answers=[None]*len(jobs);missing=[]
        for i,j in enumerate(jobs):
            old=self.lookup.get(decision_key(j))
            if old is None:missing.append((i,j));continue
            assert old['messages'][0]==j['messages'][0]
            assert canonical_schema(old['schema'])==canonical_schema(j['schema'])
            if j['stage']=='exec':
                assert old['messages'][-1]['content'].rsplit('\nActual episode facts: ',1)[1]==j['messages'][-1]['content'].rsplit('\nActual episode facts: ',1)[1]
            answers[i]=old['parsed'];self.replayed+=1
            with (self.out/'replayed_decisions.jsonl').open('a') as f:
                f.write(json.dumps({'key':decision_key(j),'source':str(self.source),
                    'source_prompt_sha256':old['prompt_sha256'],'exact_rendered_messages':old['messages']==j['messages']})+'\n')
        if missing:
            if self.cpu:raise MissingDecision(str(decision_key(missing[0][1])))
            if self.client is None:self.client=policy.base.BatchClient(self.model,self.out,self.seed)
            for (i,_),answer in zip(missing,self.client.batch([j for _,j in missing])):answers[i]=answer
        return answers


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--validate-only',action='store_true');a=ap.parse_args()
    ref=json.loads((a.source/'manifest.json').read_text());data=Path(ref['arguments']['dataset'])
    assert ref['script_sha256']==hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest()
    rows=list(map(json.loads,data.read_text().splitlines()))
    old=list(map(json.loads,(a.source/'episodes.jsonl').read_text().splitlines()))
    old_lookup={(r['case_id'],r['seed'],r['persona'],r['rule'],r['mode']):r for r in old}
    assert len(old_lookup)==len(old);completed={r['case_id'] for r in old};allowed=set(ref['case_ids'])
    all_groups=[rows[:1]]+[rows[i:i+8] for i in range(1,len(rows),8)]
    groups=[g for g in all_groups if all(r['case']['case_id'] in allowed for r in g)]
    assert {r['case']['case_id'] for g in groups for r in g}==allowed
    for g in groups:
        status=[r['case']['case_id'] in completed for r in g];assert all(status) or not any(status)
    a.out.mkdir(parents=True,exist_ok=False)
    policy.base.PERSONAS.clear();policy.base.PERSONAS.update(policy.TRAITS)
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT');seeds=ref['arguments']['seeds']
    client=Client(a.source,a.out,Path(ref['arguments']['model']),seeds[0],a.validate_only)
    if a.validate_only:
        selected=[g for g in groups if all(r['case']['case_id'] in completed for r in g)][:1]
        assert selected
        for g in selected:policy.run_group(g,seeds,client,modules,a.out)
        replayed=list(map(json.loads,(a.out/'episodes.jsonl').read_text().splitlines()))
        for r in replayed:
            b=old_lookup[r['case_id'],r['seed'],r['persona'],r['rule'],r['mode']]
            for f in ['goal_executed','request_given','target_given_before_goal','protocol_error','original_task_state_flags','steps']:
                assert r[f]==b[f],f
            for t,u in zip(r['history'],b['history']):
                for f in ['command','before','after','legal','event_type','goal_executed_after','request_given_after']:
                    assert t[f]==u[f],f
        result={'validated_episodes':len(replayed),'replayed_decisions':client.replayed,'model_calls':0,'gpu_hours':0}
        (a.out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    previous=json.loads((a.source/'interrupted_runtime.json').read_text())
    assert hashlib.sha256((a.source/'episodes.jsonl').read_bytes()).hexdigest()==previous['episodes_sha256']
    manifest={**ref,'arguments':{**ref['arguments'],'out':str(a.out)},
        'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'resumed_worker_from':str(a.source),'prior_worker_runtime':previous}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (a.out/'episodes.jsonl').write_text((a.source/'episodes.jsonl').read_text())
    count=len(old);start=time.monotonic()
    for g in groups:
        if all(r['case']['case_id'] in completed for r in g):continue
        count+=policy.run_group(g,seeds,client,modules,a.out)
        print(json.dumps({'episodes':count,'calls':client.calls,'replayed':client.replayed}),flush=True)
    expected=sum(len(r['requests']) for g in groups for r in g)*len(seeds)*len(policy.TRAITS)*len(policy.RULES)
    assert count==expected
    (a.out/'runtime.json').write_text(json.dumps({'worlds':len(allowed),'episodes':count,'calls':client.calls,
        'replayed_prior_decisions':client.replayed,'wall_seconds':time.monotonic()-start-client.load_seconds,
        'model_load_seconds':client.load_seconds,'prior_run':previous,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
