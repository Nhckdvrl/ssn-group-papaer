#!/usr/bin/env python3
"""Freeze complete experiences and later native contexts, before model outputs."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
from experience_store import ExperienceStore,file_sha
from build_adaptation_views import update_messages,prior_state,update_target,future_readout_ids
from prepare_closed_loop import tracker
from adaptation_protocol import sections,messages,actor_messages,motivation_messages,decode_motivation


def rank(v):return hashlib.sha256(('D-E10-future-interaction-v1|'+v).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--index',required=True);p.add_argument('--inventory',required=True)
    p.add_argument('--tokenizer',required=True);p.add_argument('--out',required=True);p.add_argument('--manifest',required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    inv=json.loads(Path(a.inventory).read_text());books=sorted(b for b,v in inv['books'].items() if v['partition']=='test')
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(a.tokenizer,local_files_only=True)
    def length(m):return len(tok.apply_chat_template(m,tokenize=True,return_dict=False,add_generation_prompt=True,enable_thinking=False))
    store=ExperienceStore(a.index);chosen=[];refs=[];excluded=[]
    for book in books:
        candidates=[dict(r) for r in store.db.execute('SELECT * FROM updates WHERE book=?',(book,))]
        candidates.sort(key=lambda r:rank(book+'|'+r['role']+'|'+str(r['row_id'])))
        roles=set();number=0
        for m in candidates:
            if m['role'] in roles:continue
            uid=m['row_id'];role=m['role'];reason=None
            if any(x in role.casefold() for x in ['narrator','environment']):reason='explicit_narration_target'
            nxt=future_readout_ids(store,uid)
            if not nxt or not nxt['motivation_ids'] or not nxt['interaction_ids']:reason=reason or 'missing_later_tasks'
            if reason:excluded.append(dict(row_id=uid,reason=reason));continue
            row=store.get(uid);before=prior_state(row);before['short_description']=''
            raw,t=update_target(row);after=dict(profile=t['updated_profile'] if t['profile_updated'] else before['profile'],hidden_tracker=t['hidden_tracker'],short_description=t['short_description'])
            mr=store.get(nxt['motivation_ids'][0]);s=sections(mr['conversations'][1]['value'])
            if s['Current Profile'][2]!=after['profile'].strip() or tracker(s['Hidden Tracker'][2])!=tracker(after['hidden_tracker']):
                excluded.append(dict(row_id=uid,reason='motivation_prior_not_same_post_state'));continue
            pub_m=decode_motivation(mr['conversations'][2]['value'])
            if pub_m is None:raise ValueError('Invalid published motivation')
            irs=[store.get(i) for i in nxt['interaction_ids']]
            ir=min(irs,key=lambda r:r['details'].get('segment_start',0));c=ir['conversations']
            system=c[0]['value'];marker='## Your Character State\n'
            if marker not in system:
                excluded.append(dict(row_id=uid,reason='no_target_actor_state'));continue
            state=json.JSONDecoder().raw_decode(system.split(marker,1)[1].lstrip())[0]
            if list(state)!=[role]:
                excluded.append(dict(row_id=uid,reason='non_single_character'));continue
            state=state[role]
            if state['profile']!=after['profile'] or tracker(state.get('hidden_tracker'))!=tracker(after['hidden_tracker']) or state.get('motivation','').strip()!=pub_m.strip():
                excluded.append(dict(row_id=uid,reason='actor_snapshot_mismatch'));continue
            targets=[i for i,v in enumerate(c) if v['from']=='assistant']
            positions=sorted({targets[0],targets[len(targets)//2],targets[-1]})
            eid=f'ew/{uid}';queries=[]
            for i in positions:
                qid=eid+'/turn'+str(i)
                queries.append(dict(question_id=qid,messages=messages(c[:i]),source_turn=i))
            ep=dict(episode_id=eid,book=book,role=role,update_id=uid,next_update_id=nxt['next_update_id'],
                source_scene=m['scene'],query_scene=nxt['scene'],before_state=before,update_input=update_messages(row),
                motivation_input=messages(mr['conversations'][:2]),queries=queries,
                preselected_review=number<2)
            sizes=[length(ep['update_input']),length(motivation_messages(ep,after,True))]
            sizes += [length(actor_messages(ep,q,after,pub_m,True)) for q in queries]
            if max(sizes)>24576:
                excluded.append(dict(row_id=uid,reason='complete_condition_over_24576',max_tokens=max(sizes)));continue
            ep['max_registered_input_tokens']=max(sizes)
            chosen.append(ep);refs.append(dict(episode_id=eid,state=after,update_target=t,motivation=pub_m,
                responses={eid+'/turn'+str(i):c[i]['value'] for i in positions},
                motivation_source_id=nxt['motivation_ids'][0],interaction_source_details=ir['details']))
            roles.add(role);number+=1
            if number==8:break
    store.close()
    for name,rows in [('episodes',chosen),('references',refs),('exclusions',excluded)]:
        (out/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    manifest=dict(experiment='D-E10',n_episodes=len(chosen),n_books=len({e['book'] for e in chosen}),
        n_queries=sum(len(e['queries']) for e in chosen),by_book=dict(Counter(e['book'] for e in chosen)),
        exclusions=dict(Counter(e['reason'] for e in excluded)),source_revision=inv['source_revision'],
        selection_salt='D-E10-future-interaction-v1',script_sha256=file_sha(__file__),
        files={f.name:dict(sha256=file_sha(f),bytes=f.stat().st_size) for f in out.iterdir()},
        samples=[{k:e[k] for k in ['episode_id','book','role','update_id','next_update_id','source_scene','query_scene','max_registered_input_tokens','preselected_review']} for e in chosen],
        note='Published source-order component transitions and independent later contexts, not autonomous long dialogue or certified original-book chronology. No model-outcome selection.')
    Path(a.manifest).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ['samples','files']},indent=2))


if __name__=='__main__':main()
