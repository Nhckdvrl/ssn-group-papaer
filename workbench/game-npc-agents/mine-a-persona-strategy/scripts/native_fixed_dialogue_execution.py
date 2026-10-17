#!/usr/bin/env python3
"""E76: preserve exact prior dialogue; intervene only on native execution start."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import time
import native_retrieval_execution as base
from native_rule_execution import configure, SharedPrefixClient, policy
from native_matched_task_execution import decision_key

ORIGINAL_SPEC=base.spec
ORIGINAL_BASES=base.bases_for
SOURCES={}
CONDITION='ready_frozen_dialogue'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec(game,stage,modules,graph=None,history=None):
    if stage=='conv':
        game=copy.deepcopy(game);game['state']='retrieval'
        game['case']['quest']['graph']=SOURCES[game['case']['case_id']]['states']['retrieval']
    return ORIGINAL_SPEC(game,stage,modules,graph,history)


def bases(rows):
    return [{**g,'conversation_source_state':'retrieval'} for g in ORIGINAL_BASES(rows)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--model',type=Path)
    ap.add_argument('--prior-runs',type=Path,nargs='*',default=[])
    ap.add_argument('--profile',action='store_true');ap.add_argument('--cpu-check',action='store_true')
    a=ap.parse_args();configure();assert os.environ.get('PYTHONHASHSEED')=='0'
    rows=list(map(json.loads,a.data.open()));assert len(rows)==102
    SOURCES.update({r['case']['case_id']:r for r in rows})
    base.CONDITIONS={CONDITION:('ready','baseline')};base.bases_for=bases;base.spec=spec
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    if a.cpu_check:
        count=0
        for g in bases(rows):
            origin=copy.deepcopy(g);origin['state']='retrieval'
            origin['case']['quest']['graph']=SOURCES[g['case']['case_id']]['states']['retrieval']
            assert spec(g,'conv',modules)==ORIGINAL_SPEC(origin,'conv',modules)
            g['conversation']={'reply':'I will consider the request.','stance':'negotiate'}
            graph=modules[0].from_json(g['case']['quest']['graph'])
            assert spec(g,'exec',modules,graph,[])==ORIGINAL_SPEC(g,'exec',modules,graph,[])
            count+=1
        r={'status':'PASS','worlds':102,'paired_input_checks':count,'data_sha256':sha(a.data),
           'script_sha256':sha(Path(__file__)),'model_calls':0}
        a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));return
    assert a.model and a.prior_runs
    cache={};hashes={}
    for folder in a.prior_runs:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model']==str(a.model)
        path=folder/'model_calls.jsonl'
        for r in map(json.loads,path.open()):cache.setdefault(decision_key(r),r['parsed'])
        hashes[str(path)]=sha(path)
    selected=rows[:1] if a.profile else rows
    for g in bases(selected):
        key=decision_key(policy.base.job(g['case'],g['persona'],'conv',spec(g,'conv',modules),g['sampling_seed']))
        assert key in cache and cache[key] is not None
    a.out.mkdir(parents=True,exist_ok=False);(a.out/'model_calls.jsonl').touch()
    manifest={'experiment':'E76','model':str(a.model),'profile':a.profile,'worlds':len(selected),
        'case_ids':[r['case']['case_id'] for r in selected],'seeds':base.SEEDS,'condition':CONDITION,
        'conversation_state':'retrieval','execution_state':'ready','data_sha256':sha(a.data),
        'script_sha256':sha(Path(__file__)),'base_driver_sha256':sha(Path(base.__file__)),
        'prior_model_calls_sha256':hashes,'exact_conversation_preflight_passed':True,
        'new_cloud_calls':0,'rules_modified':False,'new_scripted_agent_actions':0}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    client=SharedPrefixClient(a.model,a.out,7501);client.cache.update(cache)
    start=time.monotonic();episodes=0
    for chunk in [selected[:1]]+[selected[i:i+8] for i in range(1,len(selected),8)]:
        episodes+=base.run_group(chunk,client,modules,a.out)
        print(json.dumps({'episodes':episodes,'calls':client.inner.calls,'reused':client.reused,
                          'seconds':time.monotonic()-start}),flush=True)
    assert episodes==len(selected)*6
    assert all(r['stage']=='exec' for r in map(json.loads,(a.out/'model_calls.jsonl').open()))
    r={'worlds':len(selected),'episodes':episodes,'calls':client.inner.calls,'reused_calls':client.reused,
       'new_conversation_calls':0,'wall_seconds':time.monotonic()-start,
       'model_load_seconds':client.inner.load_seconds,'new_cloud_calls':0}
    (a.out/'runtime.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)


if __name__=='__main__':main()
