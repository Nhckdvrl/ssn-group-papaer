#!/usr/bin/env python3
"""E68 qualify locked reserve without model calls or modifying original worlds."""
import collections
import hashlib
import json
from pathlib import Path
import random
from light_npc_episodes import CACHE, ViewerHost, execute
from light_native_gate import load_event_modules, parse_event


def main():
    root=CACHE/'runs';source=root/'e68_clean_reserve_lock/cases.jsonl'
    cases=list(map(json.loads,source.read_text().splitlines()))
    assert len(cases)==len({c['graph_sha256'] for c in cases})==109
    m=load_event_modules(CACHE/'sources/LIGHT');rows=[];counts=collections.Counter()
    for c in cases:
        g=m[0].from_json(c['quest']['graph']);a=g.get_node(c['actor_id'])
        original=execute(ViewerHost(g),a,c['goal_command'],*m[1:])
        assert original['legal'] and original.get('executed') and not original['stochastic_failure']
        g=m[0].from_json(c['quest']['graph']);a=g.get_node(c['actor_id'])
        other=sorted([e for e in m[1].GiveObjectEvent.get_valid_actions(g,a)
                      if e.target_nodes[1].node_id==c['requester_id']
                      and e.target_nodes[0].node_id!=c['item_id']
                      and e.target_nodes[0].get_container().node_id==c['actor_id']],
                     key=lambda e:e.target_nodes[0].node_id)
        alternatives=[('goal_item',c['item_id'],c['request_command'])]
        if other:alternatives.append(('other_item',other[0].target_nodes[0].node_id,other[0].to_canonical_form()))
        row={'case':c,'requests':{},'initial_goal_witness':{k:v for k,v in original.items() if k not in ['before','after','messages']}}
        for mode,item_id,command in alternatives:
            g=m[0].from_json(c['quest']['graph']);a=g.get_node(c['actor_id']);item=g.get_node(item_id)
            request='Could you give me '+item.get_prefix_view()+', please?'
            random.seed(6800);event=execute(ViewerHost(g),a,command,*m[1:])
            assert event['legal'] and event.get('executed') and g.get_node(item_id).get_container().node_id==c['requester_id']
            legal=not isinstance(parse_event(g,a,c['goal_command'],*m[1:]),m[2])
            if mode=='other_item':
                witness=execute(ViewerHost(g),a,c['goal_command'],*m[1:])
                assert legal and witness['legal'] and witness.get('executed')
            row['requests'][mode]={'item_id':item_id,'command':command,'request_text':request,
                                  'original_goal_immediately_legal_after_give':legal}
            counts[mode]+=1
        counts['goal_kind/'+c['goal_kind']]+=1;rows.append(row)
    out=root/'e68_native_reserve';out.mkdir(exist_ok=False)
    p=out/'snapshots.jsonl';p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    per_model=6*(3*len(rows)+2*sum(r['case']['goal_kind'] in ['wear','wield'] for r in rows)+counts['other_item'])
    report={'status':'LOCKED_BEFORE_INFERENCE','worlds':len(rows),'counts':dict(counts),
        'episodes_per_model':per_model,'models':['Gemma-3-12B-IT','Qwen3-32B'],'seeds':[6801,6802,6803],
        'all_worlds_retained':True,'all_native_witnesses_passed':True,'world_modified':False,'model_calls':0,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dataset_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Other item nonessential to current native task, not necessarily irrelevant to all private utility.'}
    (out/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
