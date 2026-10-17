#!/usr/bin/env python3
"""Bounded POST-HOC native event readback of completed E77 Panel B, zero inference.

Recompute from the complete existing native caches, with the existing environment:
    env PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
      /home/xiang/miniconda3/envs/fgvd/bin/python \
      workbench/game-npc-agents/scripts/native_dialogue_outcome_readback_posthoc.py

No model calls, new experiments, changed metrics, or native rule changes.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_dialogue_outcome_report as review
from native_retrieval_report import validate
ROOT=Path('/home/xiang/.cache/game-npc-research/runs')
OUT=Path(__file__).resolve().parents[1]/'results/E77_assigned_execution_readback_POST_HOC.json'
SPEECH={'TellEvent','SayEvent','WhisperEvent','ShoutEvent'}
NONMATERIAL=SPEECH|{'EmoteEvent','ExamineEvent','PointEvent','WaitEvent','HugEvent','InventoryEvent','LookEvent'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def good(h):return bool(h['legal'] and h.get('executed') and not h.get('stochastic_failure'))
def sourceget(h,r):return h['event_type']=='GetObjectEvent' and bool(h.get('target_node_ids')) and h['target_node_ids'][0]==r['goal_item_id']
def getattempt(h,r):return sourceget(h,r) or h['command']==r['retrieve_command']
def type_of(h,r):
 if not good(h):return 'source_get_rejected_or_failed' if getattempt(h,r) else 'other_rejected_or_failed'
 if sourceget(h,r):return 'successful_source_get'
 if h['event_type'] in SPEECH:return 'speech'
 if h['event_type']=='EmoteEvent':return 'emote'
 if h['event_type']=='ExamineEvent':return 'examine'
 if h['event_type']=='BlockEvent':return 'block'
 if h['event_type']=='PointEvent':return 'point'
 if h['event_type']=='WaitEvent':return 'wait'
 if h['event_type']=='GiveObjectEvent' and h['target_node_ids'][0]!=r['goal_item_id']:return 'other_asset_give'
 if h.get('material_changed'):return 'other_material_action'
 return 'other_legal_nonmaterial'
def profile(hs,r):
 ok=[h for h in hs if good(h)]
 if any(type_of(h,r)=='other_asset_give' for h in ok):return 'other_asset_give_present'
 if any(type_of(h,r)=='block' for h in ok):return 'legal_block_present'
 if any(h.get('material_changed') for h in ok):return 'other_material_action_present'
 if ok and len(ok)==len(hs):return 'only_successful_nonmaterial'
 if ok:return 'nonmaterial_with_rejections_or_failures'
 return 'only_rejections_or_empty'
def facts(r):
 v=review.metrics(r,r['assigned_outcome']);hs=r['history'];ok=[h for h in hs if good(h)]
 get=bool(v['retrieved']);assigned=bool(v['physical_assigned_success']);decisive=not bool(v['physical_no_decisive_event'])
 assert not decisive or get
 af=v['physical_wronguse']
 counts={'successful_source_get':int(get),'no_successful_source_get':int(not get),
  'bound_goal_event':int(v['goal']),'physical_original_goal':int(v['physical_goal']),
  'physical_goal_without_bound_event':int(v['physical_goal_without_bound_event']),
  'request_source_give':int(v['request']),'other_source_give':int(v['other_source_give']),
  'physical_assigned_success':int(assigned),'assigned_not_achieved':int(not assigned),
  'get_then_assigned':int(get and assigned),'get_then_wrong_use':int(get and bool(af)),
  'get_then_no_decisive_use':int(get and not decisive),
  'get_then_original_goal_instead_of_assigned_request':int(get and r['assigned_outcome']=='request' and bool(v['physical_goal'])),
  'get_then_request_instead_of_assigned_goal':int(get and r['assigned_outcome']=='goal' and bool(v['request'])),
  'get_then_other_source_give':int(get and bool(v['other_source_give'])),
  'source_get_attempted':int(any(getattempt(h,r) for h in hs)),
  'source_get_rejected':int(any(getattempt(h,r) and not h['legal'] for h in hs)),
  'source_get_failed':int(any(getattempt(h,r) and h['legal'] and not good(h) for h in hs)),
  'death':int(v['death']),'protocol_failure':int(bool(r['protocol_error'])),
  'any_native_rejection':int(any(not h['legal'] for h in hs)),
  'native_rejection_attempts':sum(not h['legal'] for h in hs),
  'any_failed_event':int(any(h.get('stochastic_failure') for h in hs)),
  'failed_event_attempts':sum(bool(h.get('stochastic_failure')) for h in hs),
  'full_eight_action_budget':int(len(hs)==8),'steps':len(hs),
  'any_speech':int(any(h['event_type'] in SPEECH for h in ok)),
  'any_emote':int(any(h['event_type']=='EmoteEvent' for h in ok)),
  'any_examine':int(any(h['event_type']=='ExamineEvent' for h in ok)),
  'any_block':int(any(h['event_type']=='BlockEvent' for h in ok)),
  'any_other_asset_give':int(any(type_of(h,r)=='other_asset_give' for h in ok)),
  'any_other_material_action':int(any(type_of(h,r)=='other_material_action' for h in ok)),
  'only_successful_nonmaterial':int(bool(ok and len(ok)==len(hs) and all(not h.get('material_changed') for h in ok))),
  'source_item_material_changed':int(any(h['before'][r['goal_item_id']]!=h['after'][r['goal_item_id']] for h in ok))}
 assert counts['assigned_not_achieved']==counts['no_successful_source_get']+counts['get_then_wrong_use']+counts['get_then_no_decisive_use']
 assert counts['get_then_wrong_use']==sum(counts[f] for f in ['get_then_original_goal_instead_of_assigned_request','get_then_request_instead_of_assigned_goal','get_then_other_source_give'])
 return counts

def aggregate(rows):
 def sub(rs):
  cnt=Counter();events=Counter();errors=Counter();failed_events=Counter();first=Counter();first_native=Counter();profiles=Counter()
  for r in rs:
   cnt.update(facts(r));first.update([type_of(r['history'][0],r) if r['history'] else 'empty_history'])
   first_native.update([r['history'][0]['event_type'] if r['history'] else 'empty_history'])
   profiles.update([profile(r['history'],r)])
   for h in r['history']:
    if good(h):events.update([h['event_type']])
    if not h['legal']:errors.update([h.get('error','')])
    if h.get('stochastic_failure'):failed_events.update([h['event_type']])
  return {'episodes':len(rs),'counts':dict(cnt),'first_action_categories':dict(first),
    'first_action_native_event_types':dict(first_native),'exclusive_trace_profiles':dict(profiles),
    'successful_event_attempt_counts':dict(events),'native_rejection_message_counts':dict(errors),
    'failed_native_event_counts':dict(failed_events)}
 no_get=[r for r in rows if not review.metrics(r)['retrieved']]
 get_no_assigned=[r for r in rows if review.metrics(r)['retrieved'] and not review.metrics(r,r['assigned_outcome'])['physical_assigned_success']]
 return {'worlds':len({r['case_id'] for r in rows}),'all':sub(rows),
  'no_successful_source_get':sub(no_get),'successful_get_but_assigned_not_achieved':sub(get_no_assigned)}

data=ROOT/'e75_native_retrieval_qualification/snapshots.jsonl';src={r['case']['case_id']:r for r in map(json.loads,data.open())}
hashes={str(data):sha(data),str(Path(review.__file__)):sha(Path(review.__file__))};result={};validated=Counter();alias_disagreements=Counter()
for model in ['gemma','32b']:
 rows=[];seen=set()
 for shard in ['s0','s1']:
  folder=ROOT/f'e77_{model}_{shard}';assert (folder/'runtime.json').exists()
  for filename in ['episodes.jsonl','runtime.json','manifest.json']:hashes[str(folder/filename)]=sha(folder/filename)
  for r in map(json.loads,(folder/'episodes.jsonl').open()):
   if r['assigned_outcome'] is None:continue
   key=r['case_id'],r['seed'],r['persona'],r['condition'];assert key not in seen;seen.add(key)
   assert r['state']=='retrieval' and r['support']=='baseline'
   validated.update(validate(r,src[r['case_id']]))
   for h in r['history']:
    if sourceget(h,r) and h['command']!=r['retrieve_command']:alias_disagreements[h['command']]+=1
   rows.append(r)
 assert len(rows)==1224
 groups={'all':rows,'source_give':[r for r in rows if r['goal_kind']=='give'],
  'source_use':[r for r in rows if r['goal_kind']!='give']}
 groups.update({'kind_'+k:[r for r in rows if r['goal_kind']==k] for k in ['wear','eat','drink']})
 result[model]={g:{p+'/'+a:aggregate([r for r in vals if r['persona']==p and r['assigned_outcome']==a])
  for p in ['firm','agreeable'] for a in ['goal','request']} for g,vals in groups.items()}
assert not alias_disagreements
out={'status':'COMPLETE_POST_HOC','analysis':'Bounded E77 Panel B assigned-outcome native failure composition',
 'model_calls':0,'gpu_hours':0,'episodes':2448,'source_worlds':102,'native_validation':dict(validated),
 'successful_source_get_canonical_alias_disagreements':dict(alias_disagreements),
 'definitions':{'successful':'legal AND executed AND NOT stochastic_failure; target IDs and physical state verified',
  'physical_assigned_success':'Review report physical secondary: same source consumption/wear/authored recipient Give for goal; same source requester Give for request',
  'source_get_attempt':'Stored parsed GetObjectEvent with source target ID OR exact source retrieve_command. All successful source Gets match the original canonical command. Rejected parses lack node IDs; exact source command identifies canonical attempts conservatively.',
  'failure_partition':'Assigned-not-achieved = no successful Get + Get then wrong decisive use + Get then no physical decisive use',
  'counts':'Binary episode-presence unless field explicitly says attempts/steps; action/behavior flags can overlap',
  'profile_precedence':'Other-asset Give > legal Block > other material event > only successful nonmaterial > nonmaterial with failure > only failures/empty'},
 'scope':['POST-HOC composition, not a new experiment, semantic judge, capability equivalence claim or instruction rewrite.',
  'Includes every completed assigned branch, all original graphs/seeds/personas; profiles not double-counted.',
  'Lack of Get can include legal dialogue, negotiation, other actions and native rejection loops, not necessarily inability.',
  'Assigned targets are researcher instructions; failure composition alone does not identify internal adopted goal or intrinsic competence.',
  'Native stochastic_failure is the inherited event.failed flag and need not denote a random physical error.',
  'No new model calls, engine modifications, case-specific prompt tuning, status changes or git commit.'],
 'results':result,'source_sha256':hashes,'analysis_script_path':str(Path(__file__)),
 'analysis_script_sha256':sha(Path(__file__))}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':out['status'],'episodes':out['episodes'],'out':str(OUT)}))
