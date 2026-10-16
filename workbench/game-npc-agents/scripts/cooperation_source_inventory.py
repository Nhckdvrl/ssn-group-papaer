#!/usr/bin/env python3
"""CPU SOURCE INVENTORY: unchanged LIGHT authored purposes and physical chains.

No models/API, source edits, invented items/goals/rewards, or semantic gold.
Native actions execute only on disposable forks to verify existing affordances.
  env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
    /home/xiang/miniconda3/envs/fgvd/bin/python \
    workbench/game-npc-agents/scripts/cooperation_source_inventory.py
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import tarfile

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, actor_for, ViewerHost, execute
from native_owned_container_qualification import event_id

WB = Path(__file__).resolve().parents[1]
OUT = CACHE/'runs/e81_cooperation_source_inventory'
TRADE = re.compile(r'\btrad(?:e|es|ed|ing)\b|\bexchang\w*\b|\bin return\b|\bbarter\w*\b|\bbargain\w*\b|\bborrow\w*\b|\blen[dt]\w*\b|\brepay\w*\b', re.I)
MARKET = re.compile(r'\bbuy\b|\bpurchas\w*\b|\bsell\w*\b|\bpay(?:ment|ing|ments)?\b|\bpaid\b', re.I)
RESOURCE = {'get','steal','give','eat','drink','wear','wield','put','drop','remove'}
USE = {'eat','drink','wear','wield','put'}
EVENT = {'get':'GetObjectEvent','steal':'StealObjectEvent','give':'GiveObjectEvent','eat':'EatEvent','drink':'DrinkEvent','wear':'WearEvent','wield':'WieldEvent','put':'PutObjectInEvent','drop':'DropObjectEvent','remove':'RemoveObjectEvent'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
def norm(s):return re.sub(r'^(?:the|an?|some)\s+','',s.strip().lower()).strip()
def named(nodes,text):
    n=norm(text)
    return [x for x in nodes if n in {norm(y) for y in [x.name,x.get_prefix_view(),*x.get_names()]}]
def success(r):return r['legal'] and r.get('executed') and not r.get('stochastic_failure')
def identity(e,m):
    value=event_id(e,m)
    return [value[0],list(value[1])] if value else None


def resolve(g,file,q,m):
    try:a=actor_for(g,q['character'])
    except AssertionError:return None
    verb,_,arg=q['goal'].partition(' ');ident=None
    try:ident=identity(parse_event(g,a,q['goal'],*m[1:]),m)
    except (ValueError,AssertionError,AttributeError,KeyError):pass
    noun=arg
    for delim in [' from ',' to ',' in ',' on ']:noun=noun.split(delim)[0]
    options=named(g.objects.values(),noun) if verb in RESOURCE else []
    item=(g.get_node(ident[1][0]) if ident and ident[1] and g.get_node(ident[1][0]).object and verb in RESOURCE
          else options[0] if len(options)==1 else None)
    target=None
    if ident and len(ident[1])>1:target=g.get_node(ident[1][1])
    elif verb=='give' and ' to ' in arg:
        opts=named(g.agents.values(),arg.rsplit(' to ',1)[1]);target=opts[0] if len(opts)==1 else None
    elif verb=='put':
        parts=re.split(r' in | on ',arg,maxsplit=1)
        if len(parts)==2:
            opts=named([*g.objects.values(),*g.rooms.values()],parts[1]);target=opts[0] if len(opts)==1 else None
    text='\n'.join(q.get(k,'') for k in ['short_motivation','mid_motivation','long_motivation'])
    return {'file':file,'quest':q,'actor_id':a.node_id,'room_id':a.get_room().node_id,'verb':verb,
        'initial_native_identity':ident,'item_id':item.node_id if item else None,
        'initial_item_parent_id':item.get_container().node_id if item and item.get_container() else None,
        'target_id':target.node_id if target else None,'trade_marker':bool(TRADE.search(text)),
        'market_marker':bool(MARKET.search(text))}


def parsed_candidates(g,aid,event_name,ids,m):
    cls=getattr(m[1],event_name);actor=g.get_node(aid);out=[]
    for e in cls.get_valid_actions(g,actor):
        if identity(e,m)!=[event_name,ids]:continue
        command=e.to_canonical_form()
        try:parsed=identity(parse_event(g,actor,command,*m[1:]),m)
        except (ValueError,AssertionError):continue
        if parsed==[event_name,ids]:out.append(command)
    return sorted(set(out))


def transfer_path(g,aid,iid,bid,m):
    """Verified text-native Give, at most one existing Get/Remove prerequisite."""
    original=g.to_json();options=[]
    direct=parsed_candidates(g,aid,'GiveObjectEvent',[iid,bid],m)
    if direct:options.append([direct[0]])
    if not direct:
        for event_name in ['GetObjectEvent','RemoveObjectEvent']:
            for e in getattr(m[1],event_name).get_valid_actions(g,g.get_node(aid)):
                ident=identity(e,m)
                if not ident[1] or ident[1][0]!=iid:continue
                command=e.to_canonical_form()
                if identity(parse_event(g,g.get_node(aid),command,*m[1:]),m)!=ident:continue
                fork=m[0].from_json(original)
                r=execute(ViewerHost(fork),fork.get_node(aid),command,*m[1:])
                if not success(r):continue
                last=parsed_candidates(fork,aid,'GiveObjectEvent',[iid,bid],m)
                if last:options.append([command,last[0]])
    assert g.to_json()==original
    if not options:return None
    commands=min(options,key=lambda x:(len(x),x));fork=m[0].from_json(original);w=[]
    for command in commands:
        ident=identity(parse_event(fork,fork.get_node(aid),command,*m[1:]),m)
        r=execute(ViewerHost(fork),fork.get_node(aid),command,*m[1:])
        if not success(r):return None
        w.append({'actor_id':aid,'command':command,'identity':ident,'source_before':r['before'][iid],
                  'source_after':r['after'][iid],'legal':r['legal'],'executed':r['executed']})
    if fork.get_node(iid).get_container().node_id!=bid:return None
    return {'commands':commands,'events':w,'final_graph':fork}


def qualify(g,a,b,gh,m):
    iid=a['item_id'];give=transfer_path(g,a['actor_id'],iid,b['actor_id'],m)
    if give is None:return None,'giver_has_no_short_existing_native_transfer_path'
    end=give.pop('final_graph');last=None;kind=b['verb']
    if kind in ['get','steal']:
        physical={'type':'acquisition_by_partner_transfer','item_id':iid,'holder_id':b['actor_id'],
                  'scope':'Native acquisition, not execution of authored Get/Steal and not full private utility.'}
    else:
        try:e=parse_event(end,end.get_node(b['actor_id']),b['quest']['goal'],*m[1:]);ident=identity(e,m)
        except (ValueError,AssertionError,AttributeError):ident=None
        if not ident or not ident[1] or ident[1][0]!=iid:return None,'recipient_authored_use_unavailable_after_transfer'
        if ident[0]!=EVENT[kind]:return None,'recipient_authored_event_type_mismatch'
        r=execute(ViewerHost(end),end.get_node(b['actor_id']),b['quest']['goal'],*m[1:])
        if not success(r) or not r['material_changed']:return None,'recipient_use_no_successful_material_effect'
        last={'actor_id':b['actor_id'],'command':b['quest']['goal'],'identity':ident,
              'source_before':r['before'][iid],'source_after':r['after'][iid],'legal':True,'executed':True}
        after=r['after'][iid]
        if kind in ['eat','drink'] and after['container']!='VOID':return None,'consume_effect_mismatch'
        if kind in ['wear','wield'] and (after['container']!=b['actor_id'] or after.get('equipped')!=kind):return None,'equipment_effect_mismatch'
        if kind=='put' and after['container']!=ident[1][1]:return None,'put_effect_mismatch'
        physical={'type':'authored_native_'+kind,'item_id':iid,'native_identity':ident,
                  'scope':'Exact original authored immediate action plus source physical consequence; not full private utility.'}
    case_id=digest(gh+'|'+a['file']+'|'+b['file'])[:20]
    own_get=any(e.target_nodes[0].node_id==iid for e in m[1].GetObjectEvent.get_valid_actions(g,g.get_node(b['actor_id'])))
    witnesses=give['events']+([last] if last else [])
    witnesses=[{**e,'role':'npc' if e['actor_id']==a['actor_id'] else 'player',
                'event_type':e['identity'][0],'target_node_ids':e['identity'][1]} for e in witnesses]
    return {'case_id':case_id,'graph_sha256':gh,'npc_quest_file':a['file'],'player_quest_file':b['file'],
        'npc_quest':a['quest'],'player_quest':b['quest'],'npc_id':a['actor_id'],'player_id':b['actor_id'],
        'quests':[{**a['quest'],'source_file':a['file'].rsplit('/',1)[-1]},
                  {**b['quest'],'source_file':b['file'].rsplit('/',1)[-1]}],
        'actor_ids':[a['actor_id'],b['actor_id']],'source_item_id':iid,'source_item_name':g.get_node(iid).name,
        'npc_goal_kind':'give','player_goal_kind':kind,'npc_goal_command':give['commands'][-1],
        'player_goal_command':b['quest']['goal'],'npc_native_goal_identity':['GiveObjectEvent',[iid,b['actor_id']]],
        'give_command':give['commands'][-1],
        'receiver_goal_identity':last['identity'] if last else None,
        'receiver_goal_identity_scope':'Post-delivery native parser identity for use; acquisition has no executable Get/Steal after already receiving the item and is evaluated as source possession separately.',
        'player_original_initial_native_identity':b['initial_native_identity'],'player_physical_outcome':physical,
        'source_initial_parent_id':a['initial_item_parent_id'],
        'source_initially_held_by_npc':a['initial_item_parent_id']==a['actor_id'],
        'player_can_initially_get_source_without_npc':own_get,
        'native_cooperation_witness':witnesses,'native_witness':witnesses,
        'role_direction':'NPC is the original authored giver; simulated player is the original authored recipient/acquirer/user.',
        'scope':'Two independent authored quests on the identical original graph. Complementary physical path, not simultaneous original coauthor play or mutual-benefit gold.'},None


def brief(q):return {k:q.get(k) for k in ['character','persona','goal','short_motivation','mid_motivation','long_motivation','timeline']}
def inventory(a):return [{'item_id':n.node_id,'name':n.name,'equipped':n.get_prop('equipped')} for n in a.get_contents() if n.object]
def mention(text,n):
    # Literal surface support only; not a reward, value judgment or semantic gold.
    names={norm(x) for x in [n.name,n.get_prefix_view(),*n.get_names()]}
    matches=[]
    for name in names:
        if len(name)<3:continue
        match=re.search(r'(?<!\w)'+re.escape(name)+r'(?:s)?(?!\w)',text,re.I)
        if match:matches.append(text[max(0,match.start()-75):min(len(text),match.end()+75)])
    return sorted(set(matches))


def main():
    OUT.mkdir(parents=True,exist_ok=True);m=load_event_modules(CACHE/'sources/LIGHT')
    archive=CACHE/'quest_stems.tar.gz';groups=defaultdict(list);total=Counter()
    with tarfile.open(archive,'r|gz') as handle:
        for member in handle:
            if member.isfile() and member.name.endswith('.json'):
                q=json.load(handle.extractfile(member))['data'];groups[digest(q['graph'])].append((member.name,q));total['authored_quest_records']+=1
    total['raw_graphs']=len(groups);structural=defaultdict(list);eligible=[];exclusions=Counter();explicit=[]
    by_graph_entries={};join_path=CACHE/'light_npc_human_join.json'
    joins=json.loads(join_path.read_text());demo_lookup=defaultdict(list)
    for row in joins:
        for nq in row['npc_goals']:demo_lookup[(nq['file'],row['quest_file'])].append(row['demo_index'])
    for gh,source in groups.items():
        g=m[0].from_json(source[0][1]['graph']);original=g.to_json();entries=[]
        for file,q in source:
            r=resolve(g,file,q,m)
            if r is None:total['ambiguous_actor_quests']+=1;continue
            entries.append(r);total['uniquely_bound_quests']+=1;total['initially_native_legal_quests']+=bool(r['initial_native_identity'])
        actors={r['actor_id'] for r in entries};total['graphs_with_multiple_bound_authors']+=len(actors)>=2
        total['distinct_actor_goal_bindings']+=len(actors);total['unordered_bound_actor_pairs']+=len(actors)*(len(actors)-1)//2
        by_graph_entries[gh]=entries
        for a in entries:
            for b in entries:
                if a['actor_id']==b['actor_id'] or a['room_id']!=b['room_id']:continue
                total['ordered_same_room_authored_quest_pairs']+=1
                if a['verb']!='give' or not a['item_id'] or a['item_id']!=b['item_id'] or a['target_id']!=b['actor_id'] or b['verb'] not in ['get','steal',*USE]:continue
                family='give_to_acquisition' if b['verb'] in ['get','steal'] else 'give_to_use'
                structural[family].append((gh,a['file'],b['file']))
                row,reason=qualify(g,a,b,gh,m)
                if row is None:exclusions[reason]+=1;continue
                row['archived_same_role_human_demo_indices']=demo_lookup.get((a['file'].split('/')[-1],b['file'].split('/')[-1]),[])
                eligible.append(row)
        # All lexical trade/market source annotations and actual partner assets;
        # zero-asset and missing-return cases are retained, not silently filtered.
        for a in entries:
            if not (a['trade_marker'] or a['market_marker']):continue
            q=a['quest'];text='\n'.join(q.get(k,'') for k in ['short_motivation','mid_motivation','long_motivation'])
            partners=[]
            for bid in sorted(actors-{a['actor_id']}):
                p=g.get_node(bid)
                if p.get_room().node_id!=a['room_id']:continue
                give_options=[]
                for item in sorted(g.objects.values(),key=lambda x:x.node_id):
                    if item.get_container() is None or item.get_container().node_id!=bid:continue
                    path=transfer_path(g,bid,item.node_id,a['actor_id'],m)
                    if path:
                        give_options.append({'item_id':item.node_id,'name':item.name,'equipped':item.get_prop('equipped'),
                            'native_return_commands':path['commands'],'literal_motivation_mentions':mention(text,item),
                            'literal_timeline_mentions':mention(json.dumps(q.get('timeline',[]),ensure_ascii=False),item)})
                intended_offer=None
                if a['verb']=='give' and a['target_id']==bid and a['item_id']:
                    path=transfer_path(g,a['actor_id'],a['item_id'],bid,m)
                    if path:intended_offer={'item_id':a['item_id'],'name':g.get_node(a['item_id']).name,
                        'native_offer_commands':path['commands'],'initial_parent_id':a['initial_item_parent_id']}
                partners.append({'actor_id':bid,'name':p.name,'original_persona':p.get_prop('persona'),
                    'inventory':inventory(p),'native_return_asset_options':give_options,'authored_goal_annotations':[brief(x['quest']) for x in entries if x['actor_id']==bid],
                    'authored_give_offer_path':intended_offer})
            mentioned_existing=[{'item_id':n.node_id,'name':n.name,'parent_id':n.get_container().node_id if n.get_container() else None,
                'motivation_spans':mention(text,n)} for n in g.objects.values() if mention(text,n)]
            explicit.append({'quest_file':a['file'],'graph_sha256':gh,'case_id':gh[:16],
                'actor_id':a['actor_id'],'source_authored_context':brief(q),
                'trade_lexical_marker':a['trade_marker'],'market_lexical_marker':a['market_marker'],
                'original_goal_initial_native_identity':a['initial_native_identity'],
                'motivation_mentions_existing_objects':mentioned_existing,'co_present_partners':partners,
                'source_only_scope':'Literal mentions and native inventory/transfer affordances; not semantic certification of desired return, real value or mutual benefit.'})
        assert g.to_json()==original,'Original source graph changed during qualification'
    selected={}
    for row in sorted(eligible,key=lambda r:r['case_id']):selected.setdefault(row['graph_sha256'],row)
    rows=sorted(selected.values(),key=lambda r:r['case_id'])
    dataset=OUT/'snapshots.jsonl';dataset.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    allpath=OUT/'all_qualified_author_pairs.jsonl';allpath.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in eligible))
    tradepath=OUT/'trade_source_catalog.jsonl';tradepath.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in explicit))
    concrete=[]
    for r in explicit:
        for partner in r['co_present_partners']:
            offer=partner['authored_give_offer_path']
            if not offer:continue
            matches=[x for x in partner['native_return_asset_options'] if x['item_id']!=offer['item_id'] and (x['literal_motivation_mentions'] or x['literal_timeline_mentions'])]
            if matches:concrete.append({'quest_file':r['quest_file'],'graph_sha256':r['graph_sha256'],'npc_id':r['actor_id'],
                'player_id':partner['actor_id'],'offer':offer,'physically_existing_literal_return_candidates':matches,
                'authored_context':r['source_authored_context'],'classification':'Needs manual semantic review; object mention is not desired-return gold.'})
    returnpath=OUT/'literal_return_candidates.jsonl';returnpath.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in concrete))
    summary={'status':'COMPLETE_CPU_SOURCE_INVENTORY','model_calls':0,'API_calls':0,'GPU_hours':0,'source_world_edited':False,
        'pool':dict(total),'structural_complementarity':{k:{'authored_quest_pairs':len(v),'unique_source_graphs':len({x[0] for x in v})} for k,v in structural.items()},
        'native_qualified_author_pairs':len(eligible),'native_qualified_graphs':len(rows),
        'native_qualified_player_goal_kinds_all_pairs':dict(Counter(r['player_goal_kind'] for r in eligible)),
        'fixed_minSHA_selected_goal_kinds':dict(Counter(r['player_goal_kind'] for r in rows)),
        'selected_source_initial_parent_types':dict(Counter('npc_held' if r['source_initially_held_by_npc'] else 'other_existing_container' for r in rows)),
        'selected_player_direct_get_without_npc':sum(r['player_can_initially_get_source_without_npc'] for r in rows),
        'selected_with_same_role_archived_human_demo':sum(bool(r['archived_same_role_human_demo_indices']) for r in rows),
        'native_witness_exclusion_counts':dict(exclusions),'lexical_trade_market_annotations':len(explicit),
        'lexical_trade_annotations':sum(r['trade_lexical_marker'] for r in explicit),
        'physically_existing_literal_return_candidate_annotations':len(concrete),
        'literal_return_candidate_graphs':len({r['graph_sha256'] for r in concrete}),
        'selection':'All native qualified complementary pairs; one per unchanged source graph by minimum SHA of graph|NPC quest file|player quest file. NPC is authored giver, player authored recipient/user. No model outcome used.',
        'source_facts_vs_interpretation':['Same-graph author quest annotations are independent alternatives; activating two together is the declared research task binding, not evidence they co-occurred in the original data.','Give→Get/Steal physical possession does not execute authored Get/Steal; report bound event separately.','Give→consume/equip/Put witnesses verify actual material consequences of the original immediate action; they do not prove whole private purposes or double-win.','Literal trade/market text and object mentions are a recall-oriented source index, not semantic exchange labels. Missing assets stay missing.','Native fork actions verify existing affordances only; original graph/source files unchanged. Player direct Get opportunities remain disclosed.'],
        'assets':{str(p):{'sha256':sha(p),'rows':sum(1 for _ in p.open())} for p in [dataset,allpath,tradepath,returnpath]},
        'source_sha256':{str(p):sha(p) for p in [archive,join_path,Path(__file__)]},
        'selected_case_index':[{'case_id':r['case_id'],'graph_sha256':r['graph_sha256'],'npc_quest_file':r['npc_quest_file'],'player_quest_file':r['player_quest_file'],
            'npc_id':r['npc_id'],'player_id':r['player_id'],'source_item_id':r['source_item_id'],'player_goal_kind':r['player_goal_kind']} for r in rows],
        'literal_return_candidates':concrete}
    out=WB/'results/E81_source_inventory.json';out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['assets','source_sha256','selected_case_index','literal_return_candidates','source_facts_vs_interpretation']},ensure_ascii=False))


if __name__=='__main__':main()
