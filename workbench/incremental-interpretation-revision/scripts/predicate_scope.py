"""E31: matched began boundary, published same/different activity predicates."""
import argparse
import json
from pathlib import Path
import re
from data import CACHE,sha,write_jsonl
from event_identity import digest


def build(cache,out):
    assert not out.exists();out.mkdir(parents=True)
    parent=cache/'E29-material-preparation-v2';fields=json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']
    fs={r['id']:r for r in fields};byverb={}
    for r in fields:byverb.setdefault(r['source_past_vp'],r)
    verbs=sorted(byverb);assert len(verbs)==12
    pairs={v:verbs[(i+5)%12] for i,v in enumerate(verbs)}
    (out/'predicate-map.json').write_text(json.dumps(dict(policy='Alphabetical verb families, fixed +5 cyclic offset. Declared before scores; no winner/semantic selection.',mapping=pairs,fields_sha256=sha(cache/'E24-material-preparation-v1/fields-v3.json')),indent=2)+'\n')
    packets=[];mapping={};built={}
    for task in ('probability','nli'):
        parents=list(map(json.loads,(parent/f'{task}-audited-v2.jsonl').read_text().splitlines()))
        chosen=[r for r in parents if (r['readout_actor_mode']!='original_activity' if task=='probability' else r['readout_kind'] in ('same_actor_new_activity','other_actor_new_activity'))]
        result=[]
        for mode in ('same_began','different_began'):
            for r in chosen:
                f=fs[r['pair_id'].split(':')[1]];g=f if mode=='same_began' else byverb[pairs[f['source_past_vp']]]
                text=r['sentence'] if task=='probability' else r['passage'];needle=' continued a separate '+f['activity_np']+'.';assert text.count(needle)==1
                before,after=text.split(needle);bridge=' began a separate '+g['activity_np']+'.'
                row=dict(r,item_id='E31:'+r['item_id']+':'+mode,parent_item_id=r['item_id'],condition=mode,boundary_marker=mode,
                         old_predicate_family=f['source_past_vp'],new_predicate_family=g['source_past_vp'],
                         new_activity_np=g['activity_np'],new_progressive_vp=g['progressive_vp'],
                         eligible=False,acceptable=False,faithful_ablation=False,
                         transformation='Old anchor and role fact/actor/targets exact. Both new activities began a separate occurrence. New bridge/readout predicate stays same or uses predeclared +5 published verb-family rotation; no lexical or outcome cherry-pick.')
                for k in list(row):
                    if k.startswith('audit'):del row[k]
                if task=='probability':
                    prefix=r['sentence'][:r['target_start_char']];pre,tail=prefix.split(needle)
                    tail=tail.replace('In that new '+f['activity_np']+', ','In that new '+g['activity_np']+', ')
                    # The old fact is in pre and cannot be touched here.
                    if r['readout_frame']=='activity':
                        assert (' '+f['progressive_vp']+' ') in tail
                        tail=tail.replace(' '+f['progressive_vp']+' ',' '+g['progressive_vp']+' ')
                    prefix=pre+bridge+tail;suffix=r['sentence'][r['target_start_char']:];newtext=prefix+suffix
                    phrase=r['sentence'][r['target_start_char']:r['target_stop_char']];start=len(prefix);stop=start+len(phrase)
                    row.update(sentence=newtext,target_start_char=start,target_stop_char=stop,
                               target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',newtext)) if w.start()<stop and w.end()>start],
                               target_context_sha256=digest(prefix),authored_followup_start_word=r['authored_followup_start_word']+len((pre+bridge).split())-len((before+needle).split()))
                    assert newtext[start:stop]==phrase
                else:
                    newtext=before+bridge+after;hyp=r['proposition'].replace('In that new '+f['activity_np']+', ','In that new '+g['activity_np']+', ').replace(' '+f['progressive_vp']+' ',' '+g['progressive_vp']+' ')
                    row.update(passage=newtext,proposition=hyp,proposition_sha256=digest(hyp),gold_relation=None,prior_relation=r['gold_relation'])
                row['sentence_sha256']=digest(newtext);result.append(row)
                key=('P' if task=='probability' else 'N')+f'{len(result)-1:04d}';mapping[key]=row['item_id']
                p=dict(id=key,task=task,text=newtext,previous_text=text,sentence_sha256=row['sentence_sha256'],anchor=row['source_anchor'],old_predicate=f['progressive_vp'],new_predicate=g['progressive_vp'])
                if task=='probability':p.update(target=phrase,target_phrase_sha256=row['target_phrase_sha256'],readout_frame=row['readout_frame'])
                else:p.update(proposition=row['proposition'],proposition_sha256=row['proposition_sha256'])
                packets.append(p)
        assert len(result)==(1536 if task=='probability' else 384)
        path=out/f'{task}-candidates-v1.jsonl';write_jsonl(path,result);built[task]=dict(variants=len(result),sha256=sha(path))
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    for shard in (0,1):
        pp=[p for i,p in enumerate(packets) if i%2==shard];assert len(pp)==960
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return built


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.cache,a.out),indent=2))
