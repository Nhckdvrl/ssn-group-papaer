#!/usr/bin/env python3
"""E67 fixed upstream-rule x execution-rule x feedback native episodes."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from native_rule_execution import configure, run_execution, SharedPrefixClient, policy


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--sources',type=Path,nargs='+',required=True)
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--shards',type=int,default=2)
    ap.add_argument('--include-bc',action='store_true')
    a=ap.parse_args();configure()
    cases={r['case']['case_id']:r for r in map(json.loads,a.dataset.read_text().splitlines())
           if r['case']['goal_kind'] in ['wear','wield']}
    assert len(cases)==79
    upstream={}
    needed=['asset_protection','generic_priority']+(['negative_only','retention_only'] if a.include_bc else [])
    source_hashes={}
    for source in a.sources:
        p=source/'episodes.jsonl';source_hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        for row in map(json.loads,p.read_text().splitlines()):
            if row['case_id'] in cases and row['mode']=='goal_item' and row['rule'] in needed:
                key=(row['case_id'],row['seed'],row['persona'],row['rule'])
                assert key not in upstream
                upstream[key]=row
    expected={(cid,s,p,r) for cid in cases for s in [6301,6302,6303]
              for p in ['firm','agreeable'] for r in needed}
    assert set(upstream)==expected
    ids=sorted(cases)[a.shard::a.shards]
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E67','model':str(a.model),'case_ids':ids,'seeds':[6301,6302,6303],
        'include_bc':a.include_bc,'upstream_outputs_reused':True,'rules':{k:policy.RULES[k] for k in needed},
        'personas':policy.TRAITS,'source_hashes':source_hashes,'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'execution_sha256':hashlib.sha256(Path(__file__).with_name('native_rule_execution.py').read_bytes()).hexdigest(),
        'feedback':['legacy','block_status'],'max_steps':8,'world_modified':False,'cloud_calls':0,
        'exact_message_schema_seed_prefix_reuse':True,'shard':a.shard,'shards':a.shards}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    client=SharedPrefixClient(a.model,a.out,6301)
    started=time.monotonic();episodes=0
    groups=[ids[:1]]+[ids[i:i+6] for i in range(1,len(ids),6)]
    for group in groups:
        bases=[]
        for cid in group:
            row=cases[cid];req=row['requests']['goal_item']
            case={**row['case'],'request_text':req['request_text'],'request_command':req['command'],'request_item_id':req['item_id']}
            for seed in [6301,6302,6303]:
                for persona in ['firm','agreeable']:
                    for up in needed:
                        source=upstream[cid,seed,persona,up]
                        execs=['asset_protection','generic_priority'] if up in ['asset_protection','generic_priority'] else [up]
                        for ex in execs:
                            for feedback in ['legacy','block_status']:
                                bases.append({'case':case,'mode':'goal_item','seed':seed,'persona':persona,
                                    'upstream_rule':up,'exec_rule':ex,'feedback':feedback,
                                    'sampling_seed':seed+int(cid[:7],16)*10,
                                    'conversation':source['conversation'],'update':source['update']})
        episodes+=run_execution(bases,client,modules,a.out)
        print(json.dumps({'episodes':episodes,'calls':client.inner.calls,'reused':client.reused,
                          'wall_seconds':time.monotonic()-started}),flush=True)
    assert episodes==len(ids)*6*(12 if a.include_bc else 8)
    runtime={'worlds':len(ids),'episodes':episodes,'calls':client.inner.calls,'reused_calls':client.reused,
        'wall_seconds':time.monotonic()-started,'model_load_seconds':client.inner.load_seconds,'cloud_calls':0}
    (a.out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps(runtime),flush=True)


if __name__=='__main__':main()
