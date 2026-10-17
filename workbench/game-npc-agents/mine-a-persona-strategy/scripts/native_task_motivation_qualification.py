#!/usr/bin/env python3
"""E69 native event witnesses and same-world task pairs; no semantic judge."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short_action(text):
    s = text.strip().lower().rstrip('.! ')
    s = re.sub(r'^(?:i (?:want|need|plan|wish|hope) to|i would like to|to)\s+', '', s)
    s = s.replace('"', '')
    return s if re.match(r'^(?:give|wear|wield|eat|drink|hug|hit|get|steal|put|follow|go) ', s) else None


def event_identity(event, error):
    if event is None or isinstance(event, error):
        return None
    return (type(event).__name__, tuple(n.node_id for n in event.target_nodes))


def witness(case, commands, modules):
    g = modules[0].from_json(case['quest']['graph'])
    actor = g.get_node(case['actor_id'])
    results = []
    for command in commands:
        r = execute(ViewerHost(g), actor, command, *modules[1:])
        results.append({k: r.get(k) for k in ['command','legal','executed','stochastic_failure','error']})
        if not r['legal'] or not r.get('executed') or r.get('stochastic_failure'):
            return False, results
    return True, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--confirm', type=Path, required=True)
    ap.add_argument('--reserve', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    m = load_event_modules(CACHE/'sources/LIGHT')
    sources = [(split,r) for split,p in [('confirm',a.confirm),('reserve',a.reserve)]
               for r in map(json.loads,p.read_text().splitlines())]
    assert len(sources) == 309 and len({r['case']['graph_sha256'] for _,r in sources}) == 309
    records, pairs, continuations, counts, exclusions = [], [], [], Counter(), []
    for split,row in sources:
        c = row['case']; g = m[0].from_json(c['quest']['graph']); actor = g.get_node(c['actor_id'])
        goal = parse_event(g,actor,c['goal_command'],*m[1:])
        req = parse_event(g,actor,row['requests']['goal_item']['command'],*m[1:])
        goal_id, req_id = event_identity(goal,m[2]), event_identity(req,m[2])
        assert goal_id and req_id
        raw_short = c['quest']['short_motivation']; command = short_action(raw_short)
        try:
            short = parse_event(g,actor,command,*m[1:]) if command else None
        except ValueError:
            short = None
        short_id = event_identity(short,m[2]) if short is not None else None
        future = []
        for t in c['quest'].get('timeline',[]):
            label = str(t.get('label','')).lower()
            if not re.search(r'from now|later|^\+',label):
                continue
            try:
                event = parse_event(g,actor,t['action'].strip().lower(),*m[1:])
            except ValueError:
                counts['unsupported_future_command'] += 1
                continue
            eid = event_identity(event,m[2])
            if eid:
                future.append({'label':t['label'],'source_action':t['action'],
                               'canonical':event.to_canonical_form(),'request_match':eid==req_id})
        tag = ('explicit_short_equals_step' if short_id==goal_id else
               'explicit_short_equals_request' if short_id==req_id else
               'other_native_short_action' if short_id else 'unresolved_short_action')
        rec = {'case_id':c['case_id'],'split':split,'goal_kind':c['goal_kind'],
               'goal_command':c['goal_command'],'request_command':req.to_canonical_form(),
               'short_motivation':raw_short,'short_candidate':command,
               'short_native_event':short.to_canonical_form() if short_id else None,
               'source_relation':tag,'future_native_actions':future,
               'future_request_match':any(t['request_match'] for t in future)}
        records.append(rec);counts[split+'/'+tag]+=1
        if split=='reserve' and c['goal_kind'] in ['wear','wield'] and (short_id==req_id or rec['future_request_match']):
            commands=[c['goal_command'],req.to_canonical_form()]
            ok,w=witness(c,commands,m)
            if not ok:
                fg=m[0].from_json(c['quest']['graph']);fa=fg.get_node(c['actor_id'])
                execute(ViewerHost(fg),fa,c['goal_command'],*m[1:])
                removals=[e.to_canonical_form() for e in m[1].RemoveObjectEvent.get_valid_actions(fg,fa)
                          if e.target_nodes[0].node_id==c['item_id']]
                if removals:
                    commands=[c['goal_command'],sorted(removals)[0],req.to_canonical_form()]
                    ok,w=witness(c,commands,m)
            continuations.append({'case':c,'requests':{'goal_item':row['requests']['goal_item']},
                                  'source_evidence':rec,'both_path_exists':ok,'both_path':w})
        if c['goal_kind'] not in ['give','wear','wield']:
            exclusions.append({'case_id':c['case_id'],'reason':'source_goal_not_give_or_equip'});continue
        eq=[]
        for cls in [m[1].WearEvent,m[1].WieldEvent]:
            eq += [e for e in cls.get_valid_actions(g,actor) if e.target_nodes[0].node_id==c['item_id']]
        gives=[e for e in m[1].GiveObjectEvent.get_valid_actions(g,actor)
               if e.target_nodes[0].node_id==c['item_id'] and e.target_nodes[1].node_id not in [c['requester_id'],c['actor_id']]]
        if not eq or not gives:
            exclusions.append({'case_id':c['case_id'],'reason':'no_same_item_equip' if not eq else 'no_third_native_recipient'});continue
        equip=goal if c['goal_kind'] in ['wear','wield'] else eq[0]
        duty=next((e for e in gives if e.target_nodes[1].node_id==c['original_recipient']),None) if c['goal_kind']=='give' else None
        duty=duty or min(gives,key=lambda e:e.target_nodes[1].node_id)
        tasks={'equip':equip.to_canonical_form(),'duty_give':duty.to_canonical_form()}
        ws={k:witness(c,[v],m) for k,v in {**tasks,'request':req.to_canonical_form()}.items()}
        assert all(v[0] for v in ws.values())
        pairs.append({'case':c,'requests':{'goal_item':row['requests']['goal_item']},'split':split,
                      'tasks':tasks,'duty_recipient_id':duty.target_nodes[1].node_id,
                      'source_relation':tag,'native_witnesses':{k:v[1] for k,v in ws.items()}})
    assets={'source_events':records,'paired_tasks':pairs,'continuation_tasks':continuations}
    for name,rows in assets.items():
        (a.out/f'{name}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    report={'status':'COMPLETE','worlds':309,'source_relation_counts':dict(counts),
            'paired_worlds':len(pairs),'paired_source_splits':dict(Counter(r['split'] for r in pairs)),
            'paired_source_goals':dict(Counter(r['case']['goal_kind'] for r in pairs)),
            'continuation_worlds':len(continuations),'continuation_both_paths':sum(r['both_path_exists'] for r in continuations),
            'exclusions':exclusions,'assets':{k:{'path':str(a.out/f'{k}.jsonl'),'sha256':digest(a.out/f'{k}.jsonl')} for k in assets},
            'source_hashes':{str(p):digest(p) for p in [a.confirm,a.reserve]},
            'script_sha256':digest(Path(__file__)),'world_modified':False,'model_calls':0,'gpu_hours':0,
            'scope':'Native parsing supplies source-supported event witnesses, not complete semantic motivation gold labels or a data-noise judgment.'}
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['exclusions','source_hashes']},ensure_ascii=False))


if __name__=='__main__':
    main()
