#!/usr/bin/env python3
"""Source-authored resource exchange dependencies, qualified in native physics."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import tarfile
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, actor_for, ViewerHost, execute


def sha(text):return hashlib.sha256(text.encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    groups=defaultdict(list)
    with tarfile.open(CACHE/'quest_stems.tar.gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.json'):continue
            q=json.load(archive.extractfile(member))['data']
            q['source_file']=member.name.rsplit('/',1)[-1]
            groups[sha(q['graph'])].append(q)
    m=load_event_modules(CACHE/'sources/LIGHT');pairs=[];counts=Counter()
    for gh,quests in sorted(groups.items()):
        graph=m[0].from_json(quests[0]['graph']);entries=[]
        for q in quests:
            verb,_,noun=q['goal'].partition(' ')
            if verb not in ['get','steal']:continue
            if verb=='steal':noun=noun.partition(' from ')[0]
            try:actor=actor_for(graph,q['character'])
            except AssertionError:counts['ambiguous_actor']+=1;continue
            matches=[n for n in graph.objects.values() if noun.lower().strip() in
                     [n.name.lower(),*[str(x).lower() for x in (n.get_prop('names') or [])]]]
            if len(matches)!=1:counts['ambiguous_or_absent_goal_object']+=1;continue
            item=matches[0];holder=item.get_container()
            if not holder.agent or holder.node_id==actor.node_id or holder.get_room()!=actor.get_room():continue
            entries.append((q,actor.node_id,item.node_id,holder.node_id))
        for q0,a0,t0,h0 in entries:
            for q1,a1,t1,h1 in entries:
                if a0!=h1 or a1!=h0 or t0==t1 or a0>=a1:continue
                g=m[0].from_json(q0['graph']);commands=[]
                for actor_id,item_id,recipient_id in [(a0,t1,a1),(a1,t0,a0)]:
                    choices=[e for e in m[1].GiveObjectEvent.get_valid_actions(g,g.get_node(actor_id))
                             if e.target_nodes[0].node_id==item_id and e.target_nodes[1].node_id==recipient_id]
                    if not choices:break
                    command=choices[0].to_canonical_form()
                    result=execute(ViewerHost(g),g.get_node(actor_id),command,*m[1:])
                    assert result['legal'] and result['executed'];commands.append(command)
                if len(commands)!=2:counts['native_exchange_unavailable']+=1;continue
                assert g.get_node(t0).get_container().node_id==a0 and g.get_node(t1).get_container().node_id==a1
                cid=sha(gh+'|'+q0['source_file']+'|'+q1['source_file'])[:20]
                pairs.append({'case_id':cid,'graph_sha256':gh,'quests':[q0,q1],
                    'actor_ids':[a0,a1],'goal_item_ids':[t0,t1],
                    'initial_goal_holders':[h0,h1],'native_exchange_witness':commands,
                    'attainment_scope':'Author Get/Steal acquisition via partner-Give reverse path; strict own event measured separately.'})
    selected={}
    for row in sorted(pairs,key=lambda r:r['case_id']):selected.setdefault(row['graph_sha256'],row)
    rows=sorted(selected.values(),key=lambda r:r['case_id'])
    (a.out/'snapshots.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    report={'source_graphs':len(groups),'eligible_pairs':len(pairs),'independent_worlds':len(rows),
        'pair_verbs':dict(Counter('/'.join(q['goal'].split()[0] for q in r['quests']) for r in rows)),
        'source_issues':dict(counts),'archive_sha256':hashlib.sha256((CACHE/'quest_stems.tar.gz').read_bytes()).hexdigest(),
        'dataset_sha256':hashlib.sha256((a.out/'snapshots.jsonl').read_bytes()).hexdigest(),
        'raw':str(a.out),'model_calls':0,'gpu_hours':0,'world_modified':False,
        'selection':'minimum SHA pair per unchanged source graph, before model outcomes'}
    (a.out/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
