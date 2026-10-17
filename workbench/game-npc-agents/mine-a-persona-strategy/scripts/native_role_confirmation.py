#!/usr/bin/env python3
"""E55 independent native NPC cohort, shared dialogue, ordinary grounding control."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import (BatchClient, PERSONAS, conv_spec, update_spec,
                                    exec_spec, pack_messages, schema, job)
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute, observation, legal_commands

CONDITIONS = ['direct_request','direct_history','plan_raw','plan_grounded']
GROUNDING = ('Dialogue expresses intentions, and no physical game action has occurred yet; '
             'only actually executed game events can mark either task as completed, so record '
             'intentions separately from performed actions.')


def spec(g, modules):
    c = g['case']; cond = g['condition']; p = g['persona']
    if cond.startswith('plan_') or cond.startswith('force_') or cond == 'direct_request':
        return exec_spec(c,p,g.get('update') or {}, '11' if cond.startswith('plan_') else '00',
                         g['graph'],g['history'],modules,
                         {'force_own':'own_task','force_request':'request'}.get(cond,'none'))
    view = observation(ViewerHost(g['graph']),g['graph'].get_node(c['actor_id']),*modules[1:])
    menu = legal_commands(g['graph'],g['graph'].get_node(c['actor_id']))
    messages = [dict(m) for m in conv_spec(c,p,modules)[0]]
    messages.append({'role':'assistant','content':g['conversation']['reply']})
    text = 'Current game observation:\n'+view+'\nChoose your next legal game action.'
    if g['history']: text += '\nYour recent actual game actions: '+json.dumps([r['command'] for r in g['history']])
    text += '\nLegal commands:\n'+'\n'.join(menu)
    messages.append({'role':'user','content':text})
    return messages, schema({'action':{'type':'string','enum':menu+['say']},
                            'utterance':{'type':'string'},'reason':{'type':'string'}})


def run(cases, seed, client, modules, out, first_seed):
    bases = [{'case':c,'persona':p,'sampling_seed':seed+int(c['case_id'][:7],16)*10} for c in cases for p in PERSONAS]
    if seed == first_seed:
        jobs = [job(b['case'],b['persona'],'expression',
                    (pack_messages(b['case'],b['persona'],'Introduce yourself and say what you value in two sentences.'),
                     schema({'self_description':{'type':'string'}})),b['sampling_seed']+2) for b in bases]
        answers = client.batch(jobs)
        with (out/'expression.jsonl').open('a') as f:
            for b, answer in zip(bases,answers):
                f.write(json.dumps({'case_id':b['case']['case_id'],'persona':b['persona'],
                                    'seed':seed,'expression':answer,'separate_session':True},ensure_ascii=False)+'\n')
    answers = client.batch([job(b['case'],b['persona'],'conv',conv_spec(b['case'],b['persona'],modules),
                                b['sampling_seed']) for b in bases])
    for b, answer in zip(bases,answers): b['conversation'] = answer
    update_jobs, slots = [], []
    for b in bases:
        if b['conversation'] is None: continue
        for kind in ['raw','grounded']:
            messages, structure = update_spec(b['case'],b['persona'],b['conversation'],modules)
            if kind == 'grounded': messages[-1]['content'] += '\n'+GROUNDING
            update_jobs.append({**job(b['case'],b['persona'],'update',(messages,structure),b['sampling_seed']+1),
                                'update_condition':kind})
            slots.append((b,kind))
    answers = client.batch(update_jobs) if update_jobs else []
    for (b,kind), answer in zip(slots,answers): b[kind] = answer
    branches = []
    for b in bases:
        with (out/'stage_outputs.jsonl').open('a') as f:
            f.write(json.dumps({k:v for k,v in {**b,'case_id':b['case']['case_id'],'seed':seed}.items() if k!='case'},ensure_ascii=False)+'\n')
        conds = CONDITIONS+(['force_own','force_request'] if seed==first_seed else [])
        for cond in conds:
            error = ('invalid_conversation' if b['conversation'] is None and cond!='direct_request' and not cond.startswith('force_') else None)
            update = b.get(cond.removeprefix('plan_')) if cond.startswith('plan_') else None
            if cond.startswith('plan_') and update is None: error = error or 'invalid_update'
            branches.append({**b,'condition':cond,'update':update,
                'graph':modules[0].from_json(b['case']['quest']['graph']),
                'history':[],'done':bool(error),'protocol_error':error})
    for step in range(6):
        active = [g for g in branches if not g['done']]
        if not active: break
        jobs = [{**job(g['case'],g['persona'],'exec',spec(g,modules),g['sampling_seed']+10+step,None,step),
                 'condition':g['condition']} for g in active]
        answers = client.batch(jobs)
        for g, answer in zip(active,answers):
            if answer is None:
                g['done'],g['protocol_error'] = True,'invalid_exec_json'; continue
            command = 'say '+answer['utterance'] if answer['action']=='say' else answer['action'].replace('<SOMETHING>',answer['utterance'])
            random.seed(g['sampling_seed']+100+step)
            row = execute(ViewerHost(g['graph']),g['graph'].get_node(g['case']['actor_id']),command,*modules[1:])
            row['choice'] = answer; g['history'].append(row)
            flags = outcome(g['graph'],g['case'],g['history'])
            g['done'] = bool(flags['own_task'] or flags['request'] or
                             g['graph'].get_node(g['case']['item_id']).get_container().node_id!=g['case']['actor_id'])
    with (out/'branches.jsonl').open('a') as f:
        for g in branches:
            flags = outcome(g['graph'],g['case'],g['history']); assert not(flags['own_task'] and flags['request'])
            row = {'case_id':g['case']['case_id'],'graph_sha256':g['case']['graph_sha256'],
                   'goal_kind':g['case']['goal_kind'],'persona':g['persona'],'condition':g['condition'],'seed':seed,
                   'conversation':g['conversation'],'update':g['update'],'flags':flags,'steps':len(g['history']),
                   'protocol_error':g['protocol_error'],'history':g['history']}
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(branches)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--quality',type=Path,required=True); ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--shards',type=int,default=1); ap.add_argument('--seeds',type=int,nargs='+',default=[5501,5502,5503])
    ap.add_argument('--prepare-only',action='store_true'); a = ap.parse_args()
    rows = list(map(json.loads,a.dataset.read_text().splitlines())); quality = json.loads(a.quality.read_text())
    assert len(rows)==len({r['graph_sha256'] for r in rows})==200 and all(r['split']=='confirm' for r in rows)
    assert {r['case_id'] for r in rows}==set(quality)
    cases = rows[a.shard::a.shards]; a.out.mkdir(parents=True,exist_ok=False)
    manifest = {'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        'case_ids':[c['case_id'] for c in cases], 'conditions':CONDITIONS,'personas':PERSONAS,
        'controls':['force_own','force_request'],'grounding_instruction':GROUNDING,
        'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'quality_sha256':hashlib.sha256(a.quality.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'shared_helpers':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                          for n in ['commitment_decisions_v2.py','commitment_snapshots.py','light_npc_episodes.py']},
        'world_modified':False,'cloud_calls':0,'selection':'all fixed confirm source graphs; quality only a reporting stratum'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    if a.prepare_only: return
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    modules = load_event_modules(CACHE/'sources/LIGHT'); client = BatchClient(a.model,a.out,a.seeds[0]); start=time.monotonic(); count=0
    for seed in a.seeds:
        for i in range(0,len(cases),10):
            count += run(cases[i:i+10],seed,client,modules,a.out,a.seeds[0])
            print(json.dumps({'seed':seed,'graphs':min(i+10,len(cases)),'calls':client.calls,'branches':count}),flush=True)
    assert count == len(cases)*2*(len(a.seeds)*4+2)
    (a.out/'runtime.json').write_text(json.dumps({'graphs':len(cases),'branches':count,'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__': main()
