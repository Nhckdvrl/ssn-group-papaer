#!/usr/bin/env python3
"""E16 shared consumable qualification in unchanged authored LIGHT graphs."""
import argparse
import json
from pathlib import Path
import random
import re
import tarfile

from light_npc_episodes import CACHE,ViewerHost,actor_for,execute
from light_native_gate import load_event_modules,parse_event


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    data=json.loads((CACHE/'light_resource_competition_source_candidates.json').read_text())
    selected=[];seen=set()
    for candidate in data['candidates']:
        if not candidate['both_consume']:continue
        key=tuple(sorted([candidate['consumer']['file'],candidate['other']['file']]))
        if key in seen:continue
        seen.add(key);selected.append(candidate)
    needed={c[k]['file'] for c in selected for k in ['consumer','other']};quests={}
    with tarfile.open(CACHE/'quest_stems.tar.gz','r|gz') as archive:
        for member in archive:
            name=member.name.split('/')[-1]
            if name in needed:quests[name]=json.load(archive.extractfile(member))['data']
    OOGraph,events,ErrorEvent=load_event_modules(CACHE/'sources/LIGHT');results=[]
    normalized=lambda s:re.sub(r'^(the|a|an) ','',s.strip().lower())
    for candidate in selected:
        a=quests[candidate['consumer']['file']];b=quests[candidate['other']['file']]
        assert a['graph']==b['graph']
        graph=OOGraph.from_json(a['graph']);actors=[actor_for(graph,a['character']),actor_for(graph,b['character'])]
        objects=[x for x in graph.objects.values() if normalized(x.name)==candidate['source_item']]
        row={'files':[candidate['consumer']['file'],candidate['other']['file']],
            'characters':[a['character'],b['character']],'goals':[a['goal'],b['goal']],
            'item':candidate['source_item'],'matching_object_count':len(objects),'qualified':False}
        if len(objects)!=1:results.append(row);continue
        item=objects[0];owner=item.get_container();row.update(item_node_id=item.node_id,initial_owner=owner.node_id)
        legal=[parse_event(graph,actor,quest['goal'],events,ErrorEvent) for actor,quest in zip(actors,[a,b])]
        row['initially_legal']=[not isinstance(e,ErrorEvent) for e in legal]
        index=next((i for i,e in enumerate(legal) if not isinstance(e,ErrorEvent)),None)
        if index is None and owner.room:
            host=ViewerHost(graph);prep=execute(host,actors[0],'get '+item.name,events,ErrorEvent)
            row['source_get_preparation']=prep['legal']
            if prep['legal']:index=0
        if index is not None:
            host=ViewerHost(graph);random.seed(161616)
            goal=[a,b][index]['goal'];consume=execute(host,actors[index],goal,events,ErrorEvent)
            after_other=parse_event(graph,actors[1-index],[a,b][1-index]['goal'],events,ErrorEvent)
            row.update(first_consumer=actors[index].node_id,native_event_executed=consume.get('executed',False),
                material_changed=consume['material_changed'],container_after=item.get_container().node_id,
                other_goal_after_legal=not isinstance(after_other,ErrorEvent),native_messages=consume['messages'])
            row['qualified']=consume.get('executed',False) and consume['material_changed'] and isinstance(after_other,ErrorEvent)
        results.append(row)
    summary={'pairs':len(results),'graphs':len(set(c['group_index'] for c in selected)),
        'qualified_irreversible_shared_consumable_pairs':sum(r['qualified'] for r in results),
        'human_demo_joined':len(data['human_joined']),'cases':results,'gpu_hours':0,'model_calls':0,
        'scope':'native shared resource task qualification; no unique personality-correct choice'}
    args.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='cases'}),flush=True)


if __name__=='__main__':main()
