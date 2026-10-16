#!/usr/bin/env python3
"""E84 all-source static inventory, not native execution or semantic gold.

Use the existing fgvd environment and LIGHT dependencies. Example:
  env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
    /home/xiang/miniconda3/envs/fgvd/bin/python scripts/native_independent_goal_source_inventory.py \
    --out /path/to/new/cache/output

The requested output directory must not exist; prior runs are never overwritten.
Complete source graphs/quests remain in that cache directory, never in git.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import tarfile
import time
from cooperation_source_inventory import resolve, named, RESOURCE
from light_native_gate import load_event_modules

WB=Path(__file__).resolve().parents[1]
CACHE=Path('/home/xiang/.cache/game-npc-research')
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def write(handle,row):
    handle.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')

def owner(g,nid):
    chain=[];seen=set();n=g.get_node(nid) if nid else None
    while n is not None and n.node_id not in seen:
        seen.add(n.node_id);chain.append(n.node_id)
        if n.agent:return n.node_id,chain
        n=n.get_container()
    return None,chain

def binding_alternatives(g,entry):
    verb,_,arg=entry['goal'].partition(' ');noun=arg
    for delim in [' from ',' to ',' in ',' on ']:noun=noun.split(delim)[0]
    options=named(g.objects.values(),noun) if verb in RESOURCE else []
    target=[]
    if verb=='give' and ' to ' in arg:
        target=named(g.agents.values(),arg.rsplit(' to ',1)[1])
    elif verb=='put':
        import re
        parts=re.split(r' in | on ',arg,maxsplit=1)
        if len(parts)==2:target=named([*g.objects.values(),*g.rooms.values()],parts[1])
    elif verb in ['follow','hug','hit']:target=named(g.agents.values(),arg)
    elif verb in ['get','steal'] and ' from ' in arg:
        target=named([*g.objects.values(),*g.agents.values(),*g.rooms.values()],arg.rsplit(' from ',1)[1])
    return {'file':entry['file'],'graph_sha256':entry['graph_sha256'],'goal':entry['goal'],
        'item_surface_candidate_ids':[n.node_id for n in options],
        'target_surface_candidate_ids':[n.node_id for n in target],
        'initial_native_identity':entry['initial_native_identity'],
        'source_selected_item_id':entry['item_id'],'source_selected_target_id':entry['target_id'],
        'surface_ambiguity':len(options)>1 or len(target)>1,
        'scope':'Surface alternatives are retained, not semantic target gold. Initial native parser binding and unique-name fallback remain separate from alternatives.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--archive',type=Path,default=CACHE/'quest_stems.tar.gz')
    parser.add_argument('--light-source',type=Path,default=CACHE/'sources/LIGHT')
    parser.add_argument('--frozen-bindings',type=Path,
        help='Optional prior quests.jsonl: replay recorded native name bindings without changing the source parser')
    args=parser.parse_args()
    if os.environ.get('PYTHONHASHSEED')!='0':
        parser.error('Run with PYTHONHASHSEED=0 to preserve native parser binding order')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    frozen={r['file']:r for r in map(json.loads,args.frozen_bindings.open())} if args.frozen_bindings else {}
    modules=load_event_modules(args.light_source)
    groups=defaultdict(list);counts=Counter();relations=Counter();relation_graphs=defaultdict(set)
    with tarfile.open(args.archive,'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.json'):continue
            q=json.load(archive.extractfile(member))['data']
            groups[digest(q['graph'])].append((member.name,q));counts['authored_quests']+=1
    counts['raw_graphs']=len(groups)
    handles={name:(out/(name+'.jsonl')).open('w') for name in ['graphs','quests','binding_exclusions','co_present_pairs','candidates','binding_alternatives']}
    try:
        for index,(gh,raw) in enumerate(sorted(groups.items())):
            original_graph=raw[0][1]['graph'];g=modules[0].from_json(original_graph);entries=[]
            write(handles['graphs'],{'graph_sha256':gh,'graph_json':original_graph})
            for file,q in sorted(raw):
                # Preserve ordinary native RNG, while same-name object-set
                # ties are separately disclosed and may use frozen records.
                random.seed(int(digest(gh+'|'+file)[:16],16))
                bound=resolve(g,file,q,modules)
                if bound is None:
                    counts['ambiguous_actor_quests']+=1
                    write(handles['binding_exclusions'],{'file':file,'graph_sha256':gh,'reason':'actor_not_uniquely_bound','quest':{k:v for k,v in q.items() if k!='graph'}})
                    continue
                iid=bound['item_id'];tid=bound['target_id']
                io,ic=owner(g,iid);to,tc=owner(g,tid)
                entry={k:v for k,v in bound.items() if k not in ['quest','trade_marker','market_marker']}
                entry.update(graph_sha256=gh,goal=q['goal'],quest={k:v for k,v in q.items() if k!='graph'},
                    item_owner_agent_id=io,item_ownership_chain=ic,target_owner_agent_id=to,target_ownership_chain=tc,
                    item_initial_equipped=g.get_node(iid).get_prop('equipped') if iid else None,
                    actor_initially_dead=bool(g.get_node(bound['actor_id']).get_prop('dead')))
                if file in frozen:
                    recorded=frozen[file]
                    assert recorded['quest']==entry['quest'] and recorded['graph_sha256']==gh
                    assert recorded['actor_id']==entry['actor_id']
                    for target_id in (recorded.get('initial_native_identity') or [None,[]])[1]:
                        assert g.get_node(target_id) is not None
                    entry=recorded
                entries.append(entry);write(handles['quests'],entry)
                alternatives=binding_alternatives(g,entry)
                write(handles['binding_alternatives'],alternatives)
                counts['surface_ambiguous_quests']+=alternatives['surface_ambiguity']
                counts['bound_quests']+=1;counts['initial_native_goal_parse_success']+=bool(entry['initial_native_identity'])
                counts['goal_verb_'+entry['verb']]+=1
            for a,b in itertools.combinations(entries,2):
                if a['actor_id']==b['actor_id']:continue
                counts['all_different_actor_unordered_quest_pairs']+=1
                copresent=a['room_id']==b['room_id'];counts['co_present_unordered_quest_pairs']+=copresent
                ai,bi=a['item_id'],b['item_id'];types=[];witness=[]
                for who,other,label in [(a,b,'a'),(b,a,'b')]:
                    if who['item_id'] and who['item_owner_agent_id']==other['actor_id']:
                        types.append(label+'_goal_item_owned_by_peer')
                        item=who['item_id'];parent=who['initial_item_parent_id']
                        if parent!=other['actor_id']:witness.append({'actor_id':other['actor_id'],'event_type':'GetObjectEvent','target_node_ids':[item,parent],'purpose':'Possible nested-item prerequisite; native guard must verify'})
                        if who['item_initial_equipped']:witness.append({'actor_id':other['actor_id'],'event_type':'RemoveObjectEvent','target_node_ids':[item],'purpose':'Unequip peer-held goal item before native transfer'})
                        witness.extend([{'actor_id':other['actor_id'],'event_type':'GiveObjectEvent','target_node_ids':[item,who['actor_id']],'purpose':'Possible peer help for this original goal; not a fabricated obligation'},
                                        {'actor_id':other['actor_id'],'event_type':'DropObjectEvent','target_node_ids':[item],'purpose':'Alternative physical release; no guarantee receiver goal is achieved'}])
                    if who['target_id'] and who['target_id'] not in [who['actor_id'],other['actor_id']] and who['target_owner_agent_id']==other['actor_id']:
                        types.append(label+'_goal_target_owned_by_peer')
                        witness.append({'actor_id':other['actor_id'],'event_type':'GiveObjectEvent','target_node_ids':[who['target_id'],who['actor_id']],'purpose':'Possible release of original goal container/target; native guard must verify'})
                if ai and bi and ai!=bi and a['item_owner_agent_id']==b['actor_id'] and b['item_owner_agent_id']==a['actor_id']:
                    types.append('cross_owned_distinct_goal_items')
                    if a['initial_item_parent_id']==b['actor_id'] and b['initial_item_parent_id']==a['actor_id']:
                        types.append('cross_directly_held_distinct_goal_items')
                if ai and ai==bi:types.append('shared_goal_item')
                if ai and bi and ai!=bi and a['verb']=='give' and b['verb']=='give' and a['target_id']==b['actor_id'] and b['target_id']==a['actor_id']:
                    types.append('reciprocal_authored_give_distinct_items')
                cid=digest(gh+'|'+a['file']+'|'+b['file'])[:24]
                pair={'candidate_id':cid,'graph_sha256':gh,'quest_a_file':a['file'],'quest_b_file':b['file'],
                    'actor_a_id':a['actor_id'],'actor_b_id':b['actor_id'],'co_present':copresent,'relationship_types':types,
                    'scope':'Independent same-graph author annotations jointly bound for research; not original simultaneous play or mutual-benefit gold.'}
                write(handles['co_present_pairs'],pair)
                if not types:continue
                row={**pair,'graph_ref':'graphs.jsonl#'+gh,'quest_a':a,'quest_b':b,'witness_candidates':witness,
                    'qualification_status':'STATIC_SOURCE_CANDIDATE_ONLY; no native event executed or success inferred'}
                write(handles['candidates'],row);counts['structural_candidate_pairs']+=1
                for typ in types:relations[typ]+=1;relation_graphs[typ].add(gh)
            if (index+1)%300==0:print(json.dumps({'graphs_indexed':index+1,'structural_candidate_pairs':counts['structural_candidate_pairs'],'seconds':time.monotonic()-started}),flush=True)
    finally:
        for h in handles.values():h.close()
    summary={'status':'COMPLETE_STATIC_SOURCE_INVENTORY','source_archive':str(args.archive),'source_archive_sha256':sha(args.archive),
        'script':str(Path(__file__)),'script_sha256':sha(Path(__file__)),'reuse_builder':str(WB/'scripts/cooperation_source_inventory.py'),'reuse_builder_sha256':sha(WB/'scripts/cooperation_source_inventory.py'),
        'source_light':str(args.light_source),'pythonhashseed':os.environ.get('PYTHONHASHSEED'),
        'native_parser_binding_seed':'Per quest: first16 hex digits of SHA256(graph_sha256|quest_file). Does not resolve equal-name object-set iteration ties; full alternatives remain disclosed. Not a semantic target label or experimental model seed.',
        'frozen_bindings':({'path':str(args.frozen_bindings),'sha256':sha(args.frozen_bindings)} if args.frozen_bindings else None),
        'binding_alternatives_provenance':'POST-HOC source supplement first added after the initial 2026-10-16 static inventory; integrated here for reproducibility. It preserves selected native bindings and never filters candidates.',
        'counts':dict(counts),'relationship_counts':{k:{'quest_pairs':v,'graphs':len(relation_graphs[k])} for k,v in sorted(relations.items())},
        'assets':{str(out/(name+'.jsonl')):{'sha256':sha(out/(name+'.jsonl')),'rows':sum(1 for _ in (out/(name+'.jsonl')).open()),'bytes':(out/(name+'.jsonl')).stat().st_size} for name in handles},
        'limits':['Native parsing used only to bind existing author goal entities. No event execution or physical qualification was run.',
            'No source text or graph edits, invented goals/assets/rewards, semantic labels, model/API calls or GPU.',
            'All same-graph different-author pairs retained in co_present_pairs.jsonl, including no structural cue; name does not impose same-room selection.',
            'Role persona/motives/timeline are source text, not implemented completion flags.',
            'Peer ownership may permit unilateral Steal and does not establish necessity of cooperation.',
            'Structural reciprocal Give and shared-item cases are controls/candidates, not claimed mutual benefit.'],
        'inference_api_calls':0,'GPU_hours':0,'wall_seconds':time.monotonic()-started}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':summary['status'],'counts':summary['counts'],'relationship_counts':summary['relationship_counts'],'wall_seconds':summary['wall_seconds'],'summary':str(out/'summary.json')},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
