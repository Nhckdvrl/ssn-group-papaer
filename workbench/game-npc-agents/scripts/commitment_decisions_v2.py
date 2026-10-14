#!/usr/bin/env python3
"""E50 v2: executed agenda items advance; immutable native LIGHT snapshots."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute, legal_commands, observation, system_message

PERSONAS = {
    'firm': 'I am firm, dutiful, and independent in my judgment. I take my existing responsibilities seriously.',
    'agreeable': 'I am agreeable, accommodating, and attentive to others. I take my personal relationships seriously.'}


def header(case, persona):
    return system_message(case['quest'])+'\nPersonal disposition: '+PERSONAS[persona]


def schema(properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


def pack_messages(case, persona, context):
    return [{'role': 'system', 'content': header(case, persona)}, {'role': 'user', 'content': context}]


def native_view(case, modules):
    g = modules[0].from_json(case['quest']['graph'])
    a = g.get_node(case['actor_id'])
    return observation(ViewerHost(g), a, *modules[1:]), legal_commands(g, a)


def conv_spec(case, persona, modules):
    view, menu = native_view(case, modules)
    text = (view+'\nYour current authored agenda: '+case['goal_command']
            +'\n'+case['requester_name']+' says: '+case['request_text']
            +'\nReply to this character. You may accept, decline, or negotiate the request. '
            'Do not execute a physical action in this conversation.')
    return pack_messages(case, persona, text), schema({
        'reply': {'type': 'string'},
        'stance': {'type': 'string', 'enum': ['accept', 'decline', 'negotiate']}})


def update_spec(case, persona, conversation, modules):
    view, menu = native_view(case, modules)
    text = (view+'\nOriginal agenda: '+case['goal_command']
            +'\nConversation:\n'+case['requester_name']+': '+case['request_text']
            +'\nYou: '+conversation['reply']
            +'\nUpdate your immediate plan and record one intention memory from this interaction. '
            'Choose plan actions from the current legal commands.\n'+'\n'.join(menu))
    return pack_messages(case, persona, text), schema({
        'priority_actions': {'type': 'array', 'items': {'type': 'string', 'enum': menu},
                             'minItems': 1, 'maxItems': 3},
        'intention_memory': {'type': 'string'}, 'reason': {'type': 'string'}})


def exec_spec(case, persona, update, channel, graph, history, modules, control='none'):
    actor = graph.get_node(case['actor_id'])
    view = observation(ViewerHost(graph), actor, *modules[1:])
    menu = legal_commands(graph, actor)
    text = (view+'\nOriginal authored task: '+case['goal_command']
            +'\nRecent request from '+case['requester_name']+': '+case['request_text'])
    if channel[0] == '1':
        remaining = list(update['priority_actions'])
        completed = []
        for past in history:
            if (remaining and past.get('legal') and past.get('executed')
                    and not past.get('stochastic_failure')
                    and past.get('choice', {}).get('action') == remaining[0]):
                completed.append(remaining.pop(0))
        text += '\nCompleted agenda actions: '+json.dumps(completed)
        text += '\nRemaining agenda actions: '+json.dumps(remaining)
        if not remaining:
            text += '\nThe listed agenda actions have been completed; choose what to do next.'
    else:
        text += '\nCurrent agenda: '+case['goal_command']
    if channel[1] == '1':
        text += '\nRetrieved intention memory: '+update['intention_memory']
    if history:
        text += '\nRecent actions: '+json.dumps([x['command'] for x in history])
    if control == 'information':
        text += '\nBefore choosing, check the item ownership and whether your original task and the request can both be fulfilled.'
    elif control == 'own_task':
        text += '\nFor this control, carry out your original authored task.'
    elif control == 'request':
        text += '\nFor this control, carry out the requested transfer.'
    text += '\nChoose your next legal game action.\n'+'\n'.join(menu)
    return pack_messages(case, persona, text), schema({
        'action': {'type': 'string', 'enum': menu+['say']},
        'utterance': {'type': 'string'}, 'reason': {'type': 'string'}})


class BatchClient:
    def __init__(self, model, out, seed):
        from vllm import LLM
        t = time.monotonic()
        self.llm = LLM(model=str(model), tensor_parallel_size=1, dtype='bfloat16',
                       gpu_memory_utilization=.80, max_model_len=8192, enforce_eager=True,
                       enable_prefix_caching=True, seed=seed, language_model_only=True,
                       max_num_seqs=16)
        self.tokenizer = self.llm.get_tokenizer()
        self.load_seconds = time.monotonic()-t
        self.trace = out/'model_calls.jsonl'
        self.calls = 0

    def batch(self, jobs):
        from vllm import SamplingParams
        from vllm.sampling_params import StructuredOutputsParams
        prompts, params = [], []
        for j in jobs:
            messages = [dict(m) for m in j['messages']]
            messages[0]['content'] += '\nReturn only JSON matching this schema: '+json.dumps(j['schema'])
            prompts.append(self.tokenizer.apply_chat_template(messages, tokenize=False,
                           add_generation_prompt=True, enable_thinking=False))
            params.append(SamplingParams(max_tokens=512, temperature=.7, seed=j['seed'],
                          structured_outputs=StructuredOutputsParams(json=j['schema'])))
        t = time.monotonic()
        outputs = self.llm.generate(prompts, params, use_tqdm=False)
        elapsed = time.monotonic()-t
        answers = []
        with self.trace.open('a') as f:
            for job, prompt, output in zip(jobs, prompts, outputs):
                completion = output.outputs[0]
                try:
                    answer, error = json.loads(completion.text), None
                except Exception as exc:
                    answer, error = None, str(exc)
                row = {**job, 'response': completion.text, 'parsed': answer, 'parse_error': error,
                       'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                       'finish_reason': completion.finish_reason,
                       'prompt_tokens': len(output.prompt_token_ids),
                       'completion_tokens': len(completion.token_ids),
                       'batch_size': len(jobs), 'batch_seconds': elapsed}
                f.write(json.dumps(row, ensure_ascii=False)+'\n')
                self.calls += 1
                answers.append(answer)
        return answers


def job(case, persona, stage, spec, seed, channel=None, step=None):
    return {'case_id': case['case_id'], 'persona': persona, 'stage': stage,
            'channel': channel, 'step': step, 'seed': seed,
            'messages': spec[0], 'schema': spec[1]}


def run_group(cases, client, modules, out, seed, design, controls):
    group = []
    for case in cases:
        for p in PERSONAS:
            case_seed = seed+int(case['case_id'][:7], 16)*10
            group.append({'case': case, 'conv_persona': p, 'seed': case_seed})
    jobs = [job(g['case'], g['conv_persona'], 'conv', conv_spec(g['case'], g['conv_persona'], modules), g['seed']) for g in group]
    answers = client.batch(jobs)
    bases = []
    for g, answer in zip(group, answers):
        if answer is None:
            with (out/'protocol_failures.jsonl').open('a') as f:
                f.write(json.dumps({'case_id': g['case']['case_id'], 'stage': 'conv'})+'\n')
            continue
        for down in ([g['conv_persona']] if design == 'coherent' else list(PERSONAS)):
            bases.append({**g, 'conversation': answer, 'down_persona': down})
    jobs = [job(g['case'], g['down_persona'], 'update',
                update_spec(g['case'], g['down_persona'], g['conversation'], modules), g['seed']+1) for g in bases]
    updates = client.batch(jobs)
    branches = []
    for g, update in zip(bases, updates):
        if update is None:
            with (out/'protocol_failures.jsonl').open('a') as f:
                f.write(json.dumps({'case_id': g['case']['case_id'], 'stage': 'update'})+'\n')
            continue
        with (out/'stage_outputs.jsonl').open('a') as f:
            f.write(json.dumps({k:v for k,v in {**g,'case_id':g['case']['case_id'],'update':update}.items() if k!='case'},ensure_ascii=False)+'\n')
        for channel in ['00', '10', '01', '11']:
            for control in (['none']+controls if channel=='11' else ['none']):
                graph = modules[0].from_json(g['case']['quest']['graph'])
                branches.append({**g,'update':update,'channel':channel,'control':control,
                                 'graph':graph,'history':[], 'done':False})
    for step in range(6):
        active = [g for g in branches if not g['done']]
        if not active:
            break
        jobs = [job(g['case'], g['down_persona'], 'exec',
                    exec_spec(g['case'],g['down_persona'],g['update'],g['channel'],
                              g['graph'],g['history'],modules,g['control']),
                    g['seed']+10+step, g['channel'],step) for g in active]
        answers = client.batch(jobs)
        for g, answer in zip(active, answers):
            if answer is None:
                g['done'], g['protocol_error'] = True, 'invalid_exec_json'
                continue
            command = ('say '+answer['utterance'] if answer['action']=='say'
                       else answer['action'].replace('<SOMETHING>',answer['utterance']))
            random.seed(g['seed']+100+step)
            row = execute(ViewerHost(g['graph']),g['graph'].get_node(g['case']['actor_id']),
                          command,*modules[1:])
            row['choice'] = answer
            g['history'].append(row)
            flags = outcome(g['graph'],g['case'],g['history'])
            item = g['graph'].get_node(g['case']['item_id'])
            g['done'] = bool(flags['own_task'] or flags['request']
                             or item.get_container().node_id!=g['case']['actor_id'])
    summaries = []
    with (out/'branches.jsonl').open('a') as f:
        for g in branches:
            flags = outcome(g['graph'],g['case'],g['history'])
            r = {'case_id':g['case']['case_id'],'graph_sha256':g['case']['graph_sha256'],
                 'quest_file':g['case']['quest_file'],'split':g['case']['split'],
                 'seed':seed,'conv_persona':g['conv_persona'],'down_persona':g['down_persona'],
                 'channel':g['channel'],'control':g['control'],'goal_kind':g['case']['goal_kind'],
                 'conversation':g['conversation'],'update':g['update'],'flags':flags,
                 'steps':len(g['history']),'all_legal':all(x['legal'] for x in g['history']),
                 'protocol_error':g.get('protocol_error'),
                 'first_action':g['history'][0]['command'] if g['history'] else None,
                 'history':g['history']}
            assert not (flags['own_task'] and flags['request'])
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
            summaries.append({k:v for k,v in r.items() if k not in ('history','conversation','update')})
    return summaries


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--split',default='pilot')
    ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--shards',type=int,default=1)
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--seeds',type=int,nargs='+',default=[5001])
    ap.add_argument('--design',choices=['coherent','cross'],default='coherent')
    ap.add_argument('--controls',nargs='*',default=[])
    a=ap.parse_args()
    rows=[json.loads(x) for x in a.dataset.read_text().splitlines()]
    rows=[r for r in rows if r['split']==a.split][a.shard::a.shards]
    if a.limit:rows=rows[:a.limit]
    assert rows
    a.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
              'case_ids':[r['case_id'] for r in rows],
              'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'snapshot_script_sha256':hashlib.sha256(Path(__file__).with_name('commitment_snapshots.py').read_bytes()).hexdigest(),
              'model_config_sha256':hashlib.sha256((a.model/'config.json').read_bytes()).hexdigest(),
              'personas':PERSONAS,'cloud_calls':0,'max_decision_actions':6,
              'agenda_cursor':'consume one matching successful leading action',
              'model_load_policy':'one engine reused across all assigned graphs/seeds'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=load_event_modules(CACHE/'sources/LIGHT')
    client=BatchClient(a.model,a.out,a.seeds[0])
    start=time.monotonic();summaries=[]
    for seed in a.seeds:
        for i in range(0,len(rows),10):
            batch=run_group(rows[i:i+10],client,modules,a.out,seed,a.design,a.controls)
            summaries.extend(batch)
            (a.out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
            print(json.dumps({'graphs_completed':min(i+10,len(rows)),'seed':seed,
                              'branches':len(summaries),'calls':client.calls}),flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'wall_seconds':time.monotonic()-start,
        'model_load_seconds':client.load_seconds,'calls':client.calls,'cloud_calls':0,
        'graphs':len(rows),'branches':len(summaries)},indent=2)+'\n')


if __name__=='__main__':main()
