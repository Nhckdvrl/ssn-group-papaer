#!/usr/bin/env python3
"""Freeze real appearance chains and their next native role turn, before inference."""
import argparse,json,hashlib,re,ast
from pathlib import Path
from collections import defaultdict,Counter
from index_update_provenance import section

def h(v):return hashlib.sha256(v.encode()).hexdigest()
def canonical(v):return h(json.dumps(v,ensure_ascii=False,sort_keys=True))
def tracker(v):
 if v is None or v in ['', '(Empty)', '(No hidden tracker)']:return ''
 if isinstance(v,str) and v.strip().startswith(('{','[')):
  try:v=ast.literal_eval(v)
  except (ValueError,SyntaxError):pass
 return json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else str(v).strip()
def before(row):
 s=row['conversations'][1]['value'];return dict(profile=section(s,'Current Profile (State At Scene Start)','Hidden Tracker (State At Scene Start)'),hidden_tracker=section(s,'Hidden Tracker (State At Scene Start)','Current Motivation (State At Scene Start)'),short_description='')
def messages(row):return [dict(role={'system':'system','human':'user'}[c['from']],content=c['value']) for c in row['conversations'][:2]]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--manifest',required=True);args=a.parse_args();root=Path(args.asset_root);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);assert not (out/'trajectories.jsonl').exists()
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218',local_files_only=True)
 books=json.loads((Path(__file__).resolve().parents[1]/'results/D-E04-selection.json').read_text())['books'];updates=defaultdict(list);inter=defaultdict(list);fail=Counter();lens=[]
 for l in (root/'data/EvolvingWorld/character_updates_with_details.jsonl').open():
  r=json.loads(l);d=r['details']
  if d['book_name'] in books:updates[d['book_name'],d['character']].append(r)
 for l in (root/'data/EvolvingWorld/first_role_interactions.jsonl').open():
  r=json.loads(l);d=r['details'];inter[d['book_name'],d['character'],d['scene_index']].append(r)
 def tokenlen(m):return len(tok.apply_chat_template(m,tokenize=True,return_dict=False,add_generation_prompt=True,enable_thinking=False))
 def rank(s):return h('D-E06-native-chain|'+s)
 selected=[];references=[];manifest=[];elig=Counter()
 for book in books:
  n=0
  for key in sorted([k for k,v in updates.items() if k[0]==book and len(v)>=9],key=lambda k:rank('|'.join(k))):
   rs=sorted(updates[key],key=lambda r:r['details']['scene_index']);chosen=None
   for start in sorted(range(len(rs)-8),key=lambda j:rank(book+'|'+key[1]+'|'+str(rs[j]['details']['scene_index']))):
    window=rs[start:start+9];queries=[];good=True
    for step in [1,4,8]:
     nxt=window[step];d=nxt['details'];candidates=inter.get((book,key[1],d['scene_index']),[])
     if not candidates:fail['missing_next_first_role_turn']+=1;good=False;break
     q=min(candidates,key=lambda r:r['source_conversation_sha256']);b=before(nxt);s=q['state']
     if s['profile']!=b['profile'] or tracker(s.get('hidden_tracker'))!=tracker(b['hidden_tracker']):fail['interaction_snapshot_not_same_before']+=1;good=False;break
     m=messages(q);length=tokenlen(m)
     if length>24000:fail['native_actor_input_over_24000']+=1;good=False;break
     queries.append(dict(after_updates=step,scene_index=d['scene_index'],native_messages=m,native_state=s,state_json_start=q['state_json_start'],state_json_end=q['state_json_end'],source_details=d,source_conversation_sha256=q['source_conversation_sha256'],native_prompt_tokens=length,reference=q['conversations'][2]['value']))
    if not good:continue
    for prev,nxt in zip(window,window[1:]):
     t=json.loads(prev['conversations'][-1]['value']);bp=before(prev);bn=before(nxt);post=t['updated_profile'] if t['profile_updated'] else bp['profile']
     assert post==bn['profile'] and tracker(t.get('hidden_tracker'))==tracker(bn['hidden_tracker']),'Source continuity violation'
    ul=[tokenlen(messages(r)) for r in window[:8]]
    if max(ul)>18000:fail['native_update_input_over_18000']+=1;continue
    chosen=(window,queries,ul);break
   if chosen is None:continue
   elig[book]+=1
   window,queries,ul=chosen;tid='chain/'+rank(book+'|'+key[1]+'|'+str(window[0]['details']['scene_index']))[:24];review=n==0
   for q in queries:
    qid=tid+'/after'+str(q['after_updates']);target=q.pop('reference');q['question_id']=qid
    references.append(dict(question_id=qid,trajectory_id=tid,book_name=book,role=key[1],after_updates=q['after_updates'],target=target,target_sha256=h(target),source_details=q['source_details']))
   item=dict(trajectory_id=tid,book_name=book,role=key[1],initial_state=before(window[0]),updates=[dict(details=r['details'],messages=messages(r),source_conversation_sha256=canonical(r['conversations']),native_prompt_tokens=ul[i]) for i,r in enumerate(window[:8])],queries=queries,preselected_review=review)
   selected.append(item);manifest.append(dict(trajectory_id=tid,book_name=book,role=key[1],scene_indices=[r['details']['scene_index'] for r in window],preselected_review=review,update_input_sha256=[canonical(v['messages']) for v in item['updates']],queries=[dict(question_id=q['question_id'],scene_index=q['scene_index'],after_updates=q['after_updates'],native_prompt_tokens=q['native_prompt_tokens'],input_sha256=canonical(q['native_messages'])) for q in queries]));lens+=ul+[q['native_prompt_tokens'] for q in queries];n+=1
   if n==4:break
 for name,rr in [('trajectories',selected),('references',references)]: (out/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
 summary=dict(experiment='D-E06',selection='First eligible roles/windows in independent fixed-hash order, up to four per existing source book; no model outputs or source growth flags used.',n_trajectories=len(selected),n_books=len({r['book_name'] for r in selected}),n_update_steps=8*len(selected),n_native_queries=len(references),n_first_actor_calls=5*len(references),by_book=dict(Counter(r['book_name'] for r in selected)),candidate_rejection_events=dict(fail),snapshot_and_update_continuity_verified=True,tokenizer_revision='b968826d9c46dd6066d109eabc6255188de91218',native_input_token_range=[min(lens),max(lens)],trajectories_sha256=h((out/'trajectories.jsonl').read_text()),references_sha256=h((out/'references.jsonl').read_text()),trajectories=manifest)
 Path(args.manifest).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='trajectories'},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
