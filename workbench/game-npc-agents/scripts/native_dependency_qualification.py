#!/usr/bin/env python3
"""E63 witnesses for current authored-goal asset dependencies; no model/edits."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    cases = list(map(json.loads, a.dataset.read_text().splitlines()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 200
    m = load_event_modules(CACHE/'sources/LIGHT')
    a.out.mkdir(parents=True, exist_ok=False)
    qualified, issues, counts = [], [], Counter()
    for case in cases:
        graph = m[0].from_json(case['quest']['graph'])
        actor = graph.get_node(case['actor_id'])
        gives = [e for e in m[1].GiveObjectEvent.get_valid_actions(graph, actor)
                 if e.target_nodes[1].node_id == case['requester_id']
                 and e.target_nodes[0].get_container().node_id == case['actor_id']]
        other = sorted([e for e in gives if e.target_nodes[0].node_id != case['item_id']],
                       key=lambda e:e.target_nodes[0].node_id)
        alternatives = [('goal_item', case['item_id'], case['request_command'])]
        if other:
            e = other[0]
            alternatives.append(('other_item', e.target_nodes[0].node_id, e.to_canonical_form()))
        row = {'case':case, 'requests':{}, 'non_goal_candidate_count':len(other)}
        for label, item_id, command in alternatives:
            g = m[0].from_json(case['quest']['graph']); actor = g.get_node(case['actor_id'])
            item = g.get_node(item_id)
            request_text = 'Could you give me ' + item.get_prefix_view() + ', please?'
            random.seed(6300)
            transfer = execute(ViewerHost(g), actor, command, *m[1:])
            assert transfer['legal'] and transfer['executed']
            assert g.get_node(item_id).get_container().node_id == case['requester_id']
            goal = parse_event(g, actor, case['goal_command'], *m[1:])
            legal = not isinstance(goal, m[2])
            recovery = [e for e in m[1].StealObjectEvent.get_valid_actions(g, actor)
                        if e.target_nodes[0].node_id == case['item_id']]
            paths=[]
            for e in recovery:
                victim=e.target_nodes[1]
                chance=max(1, 1+actor.dexterity-victim.dexterity)
                paths.append({'command':e.to_canonical_form(),
                    'native_success_probability':min(21, int(chance)+1)/21,
                    'basis':'uniform randint(0,20) succeeds when r <= max(1,1+actor_dex-victim_dex)'})
            witness = None
            if legal:
                goal_target_ids = [n.node_id for n in goal.target_nodes]
                witness = execute(ViewerHost(g),actor,case['goal_command'],*m[1:])
                assert witness['legal'] and witness['executed']
            else: goal_target_ids=[]
            row['requests'][label]={'item_id':item_id,'command':command,'request_text':request_text,
                'original_goal_immediately_legal_after_give':legal,
                'goal_resolved_targets_after_give':goal_target_ids,
                'goal_execution_witness_after_give':witness,
                'goal_item_steal_recovery_paths':paths,
                'scope':'Native current authored goal, not all long-term utility or irreversible impossibility.'}
            counts[label+'/worlds']+=1
            counts[label+'/goal_still_legal']+=legal
            counts[label+'/steal_recovery']+=bool(recovery)
        if other:
            assert row['requests']['other_item']['original_goal_immediately_legal_after_give']
            counts['paired_worlds']+=1
        else: issues.append({'case_id':case['case_id'],'reason':'no_other_directly_owned_native_giveable_item'})
        qualified.append(row)
    (a.out/'snapshots.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in qualified))
    report={'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'counts':dict(counts),'issues':issues,'raw':str(a.out),'model_calls':0,'gpu_hours':0,
        'world_modified':False,'all_fixed_worlds_retained':True,
        'interpretation':'Goal-item handover usually removes immediate task access; native recovery and substitute bindings kept. Other item only nonessential to current explicit goal.'}
    (a.out/'qualification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='issues'},ensure_ascii=False))


if __name__=='__main__':main()
