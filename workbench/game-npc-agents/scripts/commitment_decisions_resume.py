#!/usr/bin/env python3
"""Continue E50 after dependency failure, replaying only exact recorded requests."""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import time
from commitment_decisions_v2 import BatchClient, PERSONAS, run_group
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE


def key(job):
    fields=['case_id','persona','stage','channel','step','seed','messages','schema']
    return json.dumps({k:job[k] for k in fields},sort_keys=True,ensure_ascii=False)


class ContinuationClient:
    def __init__(self, model, out, seed, source):
        self.model,self.out,self.seed=model,out,seed
        self.saved=defaultdict(deque)
        for row in map(json.loads,(source/'model_calls.jsonl').read_text().splitlines()):
            self.saved[key(row)].append(row)
        self.engine=None;self.calls=0;self.replayed=0;self.load_seconds=0

    def batch(self,jobs):
        answers=[None]*len(jobs);missing=[];positions=[]
        with (self.out/'replayed_calls.jsonl').open('a') as f:
            for i,j in enumerate(jobs):
                k=key(j)
                if self.saved[k]:
                    row=self.saved[k].popleft()
                    f.write(json.dumps(row,ensure_ascii=False)+'\n')
                    answers[i]=row['parsed'];self.replayed+=1
                else:
                    missing.append(j);positions.append(i)
        if missing:
            if self.engine is None:
                self.engine=BatchClient(self.model,self.out,self.seed)
                self.load_seconds=self.engine.load_seconds
            fresh=self.engine.batch(missing)
            for i,value in zip(positions,fresh):answers[i]=value
            self.calls=self.engine.calls
        return answers


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seeds',type=int,nargs='+',required=True)
    ap.add_argument('--limit',type=int,default=0);a=ap.parse_args()
    original=json.loads((a.source/'manifest.json').read_text());args=original['arguments']
    dataset=Path(args['dataset']);rows=[r for r in map(json.loads,dataset.read_text().splitlines()) if r['split']==args['split']]
    rows=rows[args['shard']::args['shards']]
    if args['limit']:rows=rows[:args['limit']]
    if a.limit:rows=rows[:a.limit]
    assert set(a.seeds)<=set(args['seeds'])
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={**original,'arguments':{**args,'out':str(a.out),'seeds':a.seeds},
              'resume_from':str(a.source),'replay_rule':'exact full job JSON; queued duplicates',
              'renderer_dependency':'emoji==1.7.0; native help display compatibility; no game source change',
              'resume_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=load_event_modules(CACHE/'sources/LIGHT')
    client=ContinuationClient(Path(args['model']),a.out,a.seeds[0],a.source)
    started=time.monotonic();summaries=[]
    for seed in a.seeds:
        for i in range(0,len(rows),10):
            summaries.extend(run_group(rows[i:i+10],client,modules,a.out,seed,args['design'],args['controls']))
            (a.out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
            print(json.dumps({'seed':seed,'graphs':min(i+10,len(rows)),
                              'new_calls':client.calls,'replayed_calls':client.replayed}),flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'wall_seconds':time.monotonic()-started,
        'model_load_seconds':client.load_seconds,'calls':client.calls,'replayed_calls':client.replayed,
        'cloud_calls':0,'graphs':len(rows),'branches':len(summaries)},indent=2)+'\n')


if __name__=='__main__':main()
