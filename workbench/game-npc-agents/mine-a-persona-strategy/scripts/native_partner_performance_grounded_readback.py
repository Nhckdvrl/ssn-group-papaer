#!/usr/bin/env python3
"""E85 POST-HOC whole-cohort objective speech/material index, zero inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

SOURCE=Path('/home/xiang/.cache/game-npc-research/runs/e85_partner_performance_source/snapshots.jsonl')
SPEECH={'SayEvent','TellEvent','WhisperEvent','ShoutEvent'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(r):return tuple(r[k] for k in ['history_id','seed','panel','branch','control'])
def good(t):return bool(t.get('legal') and t.get('executed') and not t.get('stochastic_failure') and not t.get('native_exception'))
def owner(s,item,actors):
 seen=set()
 while item in s and item not in seen:
  seen.add(item);p=s[item]['container']
  if p in actors or p in [None,'VOID'] or p not in s:return p
  if s[p]['container'] in [None,'VOID']:return p
  item=p
 return None

def descendants(state,root):
 out=[]
 for node in state:
  seen=set();n=node
  while n in state and n not in seen:
   seen.add(n);parent=state[n]['container']
   if parent==root:out.append(node);break
   n=parent
 return sorted(out)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runs',nargs='+',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 hs={h['history_id']:h for h in map(json.loads,SOURCE.open())};rows={};origins={};dups=[];hashes={str(SOURCE):sha(SOURCE)}
 for folder in a.runs:
  assert (folder/'runtime.json').exists(),folder
  runtime=json.loads((folder/'runtime.json').read_text());assert runtime['status']=='COMPLETE'
  path=folder/'episodes.jsonl';hashes[str(path)]=sha(path)
  for r in map(json.loads,path.open()):
   k=key(r)
   if k in rows:assert rows[k]==r;dups.append(list(k))
   else:rows[k]=r;origins[k]=path
 index=[]
 for k,r in sorted(rows.items()):
  h=hs[r['history_id']];order=[h['source_role_map'][z] for z in ['npc','player']];case=h['case'];actors=r['actor_ids'];x,y=h['x_item_id'],h['y_item_id'];speeches=[];material=[];ignored=0;flow=Counter();x_receipts=[];y_gives=[];x_returns=[];x_initial_contents=descendants(r['initial_state'],x);y_releases=[];pending_Y_release=None;player_y_acquisitions=[]
  for t in r['interventions']+r['turns']:
   typ,ids=t['event_identity'];is_script=not t.get('model_decision');actor_role='NPC' if t['index']==0 else 'player'
   if good(t) and typ in SPEECH:
    speeches.append({'turn':t['turn'],'phase':t.get('phase'),'role':actor_role,'scripted':is_script,'event_type':typ,'target_ids':ids,'utterance':t['choice']['utterance'],'actually_delivered_messages':t['messages']})
   elif t.get('model_decision') and typ not in SPEECH and t['choice'].get('utterance'):ignored+=1
   if good(t) and t['before']!=t['after']:
    changed={n:{'before':t['before'].get(n),'after':t['after'].get(n)} for n in sorted(set(t['before'])|set(t['after'])) if t['before'].get(n)!=t['after'].get(n)}
    material.append({'turn':t['turn'],'phase':t.get('phase'),'role':actor_role,'scripted':is_script,'event_identity':t['event_identity'],'changes':changed,'messages':t['messages'],'physical_goal_now':t['physical_goal_now'],'physical_goal_ever':t['physical_goal_ever'],'strict_goal_ever':t['strict_goal_ever']})
    if owner(t['before'],x,actors)!=actors[0] and owner(t['after'],x,actors)==actors[0]:
     x_receipts.append({'turn':t['turn'],'scripted':is_script,'event_identity':t['event_identity'],'initiator':actor_role,'X_contents_at_receipt':descendants(t['after'],x)})
    if t['index']==0 and typ=='GiveObjectEvent' and ids==[y,actors[1]]:
     y_gives.append({'turn':t['turn'],'X_current_owner_before_Y_Give':owner(t['before'],x,actors),'first_X_receipt_so_far':x_receipts[0] if x_receipts else None,'descriptive_order':'after_actual_X_receipt' if x_receipts else 'before_any_actual_X_receipt'})
    if t['index']==0 and typ=='GiveObjectEvent' and ids==[x,actors[1]]:
     x_returns.append({'turn':t['turn'],'contents_still_inside_X_at_return':descendants(t['after'],x),'source_X_descendants_owned_by_NPC_after_return':[n for n in x_initial_contents if owner(t['after'],n,actors)==actors[0]],'source_X_descendants_owned_by_player_after_return':[n for n in x_initial_contents if owner(t['after'],n,actors)==actors[1]]})
    if owner(t['before'],y,actors)!=actors[1] and owner(t['after'],y,actors)==actors[1]:
     player_y_acquisitions.append({'turn':t['turn'],'initiator':actor_role,'event_identity':t['event_identity'],'previous_Y_owner':owner(t['before'],y,actors),'preceding_NPC_Y_release_turn':pending_Y_release['turn'] if pending_Y_release else None})
    if ids and ids[0]==y and t['before'][y]['container']!=t['after'][y]['container']:
     if t['index']==0 and typ in ['DropObjectEvent','PutObjectInEvent'] and owner(t['before'],y,actors)==actors[0] and owner(t['after'],y,actors)!=actors[0]:
      pending_Y_release={'turn':t['turn'],'event_identity':t['event_identity'],'destination':t['after'][y]['container'],'Y_owner_after_release':owner(t['after'],y,actors),'actual_player_Get_turn':None};y_releases.append(pending_Y_release)
     else:
      if pending_Y_release and t['index']==1 and typ=='GetObjectEvent' and owner(t['after'],y,actors)==actors[1]:pending_Y_release['actual_player_Get_turn']=t['turn']
      pending_Y_release=None
   if good(t) and t.get('model_decision') and ids:
    if t['index']==0 and typ=='GiveObjectEvent' and ids[1:]==[actors[1]]:
     flow['NPC_Give_Y' if ids[0]==y else 'NPC_Give_X_back' if ids[0]==x else 'NPC_Give_other_asset']+=1
    if t['index']==1 and typ=='GiveObjectEvent' and ids[1:]==[actors[0]]:
     flow['player_Give_X' if ids[0]==x else 'player_Give_Y_back' if ids[0]==y else 'player_Give_other_asset']+=1
    if t['index']==1 and ids[0]==y and typ in ['GetObjectEvent','StealObjectEvent']:
     flow['player_'+typ+'_Y']+=1
  for give in y_gives:
   give['full_trajectory_receipt_relation']=('after_actual_X_receipt' if give['first_X_receipt_so_far'] is not None else 'before_later_actual_X_receipt' if x_receipts else 'without_any_actual_X_receipt')
  index.append({'episode_key':list(k),'source_episode_path':str(origins[k]),'source_episode_canonical_sha256':hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'case_id':r['case_id'],'graph_sha256':r['graph_sha256'],'source_model_origin':h['model_origin'],'source_seed':h['source_seed'],'source_turn':h['source_turn'],'source_role_map':h['source_role_map'],'actor_ids':actors,'X':x,'Y':y,'original_quests':[case['quests'][i] | {'graph':'[original full graph retained at frozen source]'} for i in order],'source_prior':h['source_boundary'],'actual_speech_events':speeches,'actual_material_actions':material,'actual_freely_selected_flow_counts':dict(flow),'actual_X_receipts':x_receipts,'actual_NPC_Give_Y_timing':y_gives,'Y_Give_without_any_X_receipt_in_full_trajectory':bool(y_gives and not x_receipts),'X_contents_at_source_cut':x_initial_contents,'NPC_X_return_events_and_contents':x_returns,'NPC_Y_release_events':y_releases,'player_actual_Y_acquisitions':player_y_acquisitions,'non_speech_extra_payloads_not_delivered':ignored,'first_NPC_response':r['turns'][0] if r['turns'] else None,'suffix_goal_flags':{z:r[z] for z in ['strict_goal_ever','physical_goal_initial','physical_goal_ever','physical_goal_now']},'final_X_owner':owner(r['final_state'],x,actors),'final_Y_owner':owner(r['final_state'],y,actors),'final_X_state':r['final_state'].get(x),'final_Y_state':r['final_state'].get(y),'final_health':r['final_health'],'final_dead':r['final_dead'],'stop':r['stop']})
 a.out.write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in index))
 meta={'status':'POST_HOC_OBJECTIVE_INDEX_COMPLETE','episodes':len(index),'histories':len({k[0] for k in rows}),'original_graphs':len({r['graph_sha256'] for r in rows.values()}),'exact_profile_duplicates':dups,'source_sha256':hashes,'index':{'path':str(a.out),'sha256':sha(a.out)},'script':{'path':str(Path(__file__).resolve()),'sha256':sha(__file__)},'scope':'All actual native speech and material transitions. No agreement/success/irrationality semantic classification. Non-speech payloads are counted as untransmitted and never quoted as dialogue.','new_model_calls':0}
 a.out.with_suffix('.metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:meta[k] for k in ['status','episodes','histories','original_graphs','index']},indent=2))
if __name__=='__main__':main()
