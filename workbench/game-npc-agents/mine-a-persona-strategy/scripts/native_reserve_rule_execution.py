#!/usr/bin/env python3
"""E68 preregistered native task/defense/transfer predictions on locked reserve."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from native_rule_execution import configure, run_execution, SharedPrefixClient, policy


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--shard',type=int,default=0);ap.add_argument('--shards',type=int,default=2)
    a=ap.parse_args();configure()
    rows=list(map(json.loads,a.dataset.read_text().splitlines()))
    assert len(rows)==109 and sum('other_item' in r['requests'] for r in rows)==60
    assert hashlib.sha256(a.dataset.read_bytes()).hexdigest()=='5bee70eeda144f3dd176ba1847c18d3a08b815e07e115a844368f2c19be7505b'
    rows=rows[a.shard::a.shards]
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E68','model':str(a.model),'case_ids':[r['case']['case_id'] for r in rows],
        'seeds':[6801,6802,6803],'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'execution_sha256':hashlib.sha256(Path(__file__).with_name('native_rule_execution.py').read_bytes()).hexdigest(),
        'rules':{k:policy.RULES[k] for k in ['generic_priority','asset_protection','negative_only']},
        'personas':policy.TRAITS,'feedback':'block_status','world_modified':False,'cloud_calls':0,
        'max_steps':8,'shard':a.shard,'shards':a.shards,'predictions_frozen_before_inference':True}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    client=SharedPrefixClient(a.model,a.out,6801);start=time.monotonic();episodes=0
    for group in [rows[:1]]+[rows[i:i+6] for i in range(1,len(rows),6)]:
        upstream=[]
        for row in group:
            for mode,req in row['requests'].items():
                case={**row['case'],'request_text':req['request_text'],'request_command':req['command'],'request_item_id':req['item_id']}
                for seed in [6801,6802,6803]:
                    for persona in ['firm','agreeable']:
                        for rule in (['generic_priority'] if mode=='other_item' else ['generic_priority','asset_protection','negative_only']):
                            upstream.append({'case':case,'mode':mode,'seed':seed,'persona':persona,'upstream_rule':rule,
                                'sampling_seed':seed+int(case['case_id'][:7],16)*10})
        jobs=[policy.base.job(b['case'],b['persona'],'conv',policy.spec(b['case'],b['persona'],b['upstream_rule'],'conv',modules),b['sampling_seed'])
                | {'upstream_rule':b['upstream_rule'],'request_mode':b['mode']} for b in upstream]
        for b,answer in zip(upstream,client.batch(jobs)):b['conversation']=answer;b['update']=None
        active=[b for b in upstream if b['conversation'] is not None]
        jobs=[policy.base.job(b['case'],b['persona'],'update',policy.spec(b['case'],b['persona'],b['upstream_rule'],'update',modules,
                conversation=b['conversation']),b['sampling_seed']+1) | {'upstream_rule':b['upstream_rule'],'request_mode':b['mode']} for b in active]
        for b,answer in zip(active,client.batch(jobs)):b['update']=answer
        bases=[]
        for b in upstream:
            cross=b['mode']=='goal_item' and b['case']['goal_kind'] in ['wear','wield'] and b['upstream_rule'] in ['generic_priority','asset_protection']
            for rule in (['generic_priority','asset_protection'] if cross else [b['upstream_rule']]):
                bases.append({**b,'exec_rule':rule,'feedback':'block_status'})
        episodes+=run_execution(bases,client,modules,a.out)
        print(json.dumps({'episodes':episodes,'calls':client.inner.calls,'reused':client.reused,
                          'wall_seconds':time.monotonic()-start}),flush=True)
    expected=6*sum(3+2*(r['case']['goal_kind'] in ['wear','wield'])+('other_item' in r['requests']) for r in rows)
    assert episodes==expected
    result={'worlds':len(rows),'episodes':episodes,'calls':client.inner.calls,'reused_calls':client.reused,
            'wall_seconds':time.monotonic()-start,'model_load_seconds':client.inner.load_seconds,'cloud_calls':0}
    (a.out/'runtime.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
