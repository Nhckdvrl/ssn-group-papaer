#!/usr/bin/env python3
"""E67/E68: fixed upstream messages, native 8-action execution, factual feedback."""
import hashlib
import json
import random
from pathlib import Path
import native_dependency_roles as policy
from commitment_snapshots import outcome
from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, chosen_command

NEGATIVE = 'Do not give away any item needed for your quest.'
RETENTION = 'Retain possession of every item needed for your quest.'


def configure():
    policy.RULES.update(negative_only=NEGATIVE, retention_only=RETENTION)
    policy.base.PERSONAS.clear()
    policy.base.PERSONAS.update(policy.TRAITS)


class SharedPrefixClient:
    """Only exact messages/schema/sampling-seed reuse within one model process."""
    def __init__(self, model, out, seed):
        self.inner = policy.base.BatchClient(model, out, seed)
        self.cache = {}
        self.reused = 0
        self.trace = out/'reused_calls.jsonl'

    def batch(self, jobs):
        keys, unique = [], {}
        for job in jobs:
            key = hashlib.sha256(json.dumps({k:job[k] for k in ['messages','schema','seed']},
                                sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            keys.append(key)
            if key not in self.cache and key not in unique:
                unique[key] = {**job,'decision_key':key}
        if unique:
            answers = self.inner.batch(list(unique.values()))
            self.cache.update(zip(unique, answers))
        used = set()
        with self.trace.open('a') as f:
            for key,job in zip(keys,jobs):
                if key not in unique or key in used:
                    self.reused += 1
                    f.write(json.dumps({k:v for k,v in {**job,'decision_key':key}.items()
                                        if k not in ['messages','schema']})+'\n')
                used.add(key)
        return [self.cache[key] for key in keys]


def execution_spec(game, modules):
    c = game['case']
    messages, schema = policy.spec(c,game['persona'],game['exec_rule'],'exec',modules,
        update=game['update'],graph=game['graph'],history=game['history'],flags={
          'original_goal_event_actually_executed':game['goal_executed'],
          'requested_transfer_actually_executed':game['request_given']})
    if game['feedback'] == 'block_status' and game['history']:
        blocked = game['graph'].get_node(c['actor_id']).get_blocking()
        if blocked is not None:
            messages[-1]['content'] += '\nStatus: You are already blocking '+blocked.get_prefix_view()+'.'
        error = game['history'][-1].get('error')
        if error:
            messages[-1]['content'] += '\nLast native action result: '+error
    return messages, schema


def run_execution(bases, client, modules, out):
    games = []
    for b in bases:
        error = 'invalid_conversation' if b['conversation'] is None else 'invalid_update' if b['update'] is None else None
        games.append({**b,'graph':modules[0].from_json(b['case']['quest']['graph']),
                      'history':[],'goal_executed':False,'request_given':False,
                      'target_given_before_goal':False,'protocol_error':error,'done':bool(error)})
    for step in range(8):
        active = [g for g in games if not g['done']]
        if not active:break
        jobs = [policy.base.job(g['case'],g['persona'],'exec',execution_spec(g,modules),
                    g['sampling_seed']+10+step,None,step) | {
                    'upstream_rule':g['upstream_rule'],'exec_rule':g['exec_rule'],
                    'feedback':g['feedback'],'request_mode':g['mode']} for g in active]
        for g,answer in zip(active,client.batch(jobs)):
            if answer is None:
                g['done'],g['protocol_error']=True,'invalid_exec_json'
                continue
            c=g['case'];graph=g['graph'];actor=graph.get_node(c['actor_id'])
            command=chosen_command(answer)
            goal=parse_event(graph,actor,c['goal_command'],*modules[1:])
            event=parse_event(graph,actor,command,*modules[1:])
            matches_goal=(not isinstance(goal,modules[2]) and not isinstance(event,modules[2])
                          and goal.to_canonical_form()==event.to_canonical_form())
            matches_request=(not isinstance(event,modules[2]) and type(event).__name__=='GiveObjectEvent'
                and event.target_nodes[0].node_id==c['request_item_id'] and event.target_nodes[1].node_id==c['requester_id'])
            random.seed(g['sampling_seed']+100+step)
            result=execute(ViewerHost(graph),actor,command,*modules[1:])
            success=result['legal'] and result.get('executed') and not result.get('stochastic_failure')
            if success and matches_request:
                if c['request_item_id']==c['item_id'] and not g['goal_executed']:g['target_given_before_goal']=True
                g['request_given']=True
            if success and matches_goal:g['goal_executed']=True
            result.update(choice=answer,step=step,matches_source_goal=matches_goal,
                matches_requested_transfer=matches_request,goal_executed_after=g['goal_executed'],
                request_given_after=g['request_given'])
            g['history'].append(result)
            item=graph.get_node(c['request_item_id'])
            g['done']=(g['goal_executed'] and (g['mode']=='goal_item' or g['request_given']
                or item.get_container().node_id=='VOID')) or bool(actor.get_prop('dead'))
    with (out/'episodes.jsonl').open('a') as f:
        for g in games:
            c=g['case']
            r={k:v for k,v in g.items() if k not in ['graph','case','sampling_seed','done']}
            r.update(case_id=c['case_id'],graph_sha256=c['graph_sha256'],goal_kind=c['goal_kind'],
                goal_item_id=c['item_id'],request_item_id=c['request_item_id'],
                original_task_state_flags=outcome(g['graph'],c,g['history']),
                both_completed=g['goal_executed'] and g['request_given'],steps=len(g['history']))
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return len(games)
