"""E26 scoped constraint access and original final-interpretation controls."""
import argparse
import json
from pathlib import Path
import re
from data import CACHE, sha, write_jsonl
from event_identity import digest

BASE = 'Read the passage and answer the question about what it states or permits. Answer only Yes or No.'
REPAIR = 'Keep the actors and activities distinct: apply each participant restriction only to the actor and activity it specifies.'


def tasks_scope(data,tokenizer,recovery_mode='both'):
    report=json.loads(data.with_suffix('.audit.json').read_text());assert report['audited_sha256']==sha(data)
    rows=list(map(json.loads,data.read_text().splitlines()));assert len(rows)==report['variants']==1536
    modes=('base','repair') if recovery_mode=='both' else (recovery_mode,)
    tasks=[]
    for mode in modes:
        for r in rows:
            content='Passage:\n'+r['passage']+'\n\nProposed '+('additional fact' if r['readout_kind']=='scope_compatibility' else 'proposition')+':\n'+r['proposition']+'\n\nQuestion:\n'+r['question']
            prompt=tokenizer.apply_chat_template([{'role':'system','content':BASE+('\n'+REPAIR if mode=='repair' else '')},{'role':'user','content':content}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            tasks.append((dict(r,mode=mode,repair=mode=='repair'),mode,prompt))
    return tasks


def build(cache,out):
    assert not out.exists()
    p=cache/'E24-material-preparation-v1';fs={r['id']:r for r in json.loads((p/'fields-v3.json').read_text())['rows']}
    old=list(map(json.loads,(p/'audited-v1.jsonl').read_text().splitlines()))
    new=list(map(json.loads,(cache/'E25-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()))
    ni={(r['pair_id'],r['condition'],r['role_evidence'],r['exclusion_style'],r['readout_actor_mode']):r for r in new if r['readout_frame']=='activity' and r['target_kind']=='source_np'}
    sources={r['id']:r for r in json.loads((p/'source-fields-packets.json').read_text())}
    rows=[]
    for r in old:
        if r['readout_frame']!='activity' or r['target_kind']!='source_np':continue
        sid=r['pair_id'].split(':')[1];f=fs[sid];source=sources[sid]['gp_sentence' if r['condition']=='gp' else 'comma_sentence']
        for scope in ('original_activity','same_actor_new_activity','other_actor_new_activity'):
            parent=r if scope=='original_activity' else ni[(r['pair_id'],r['condition'],r['role_evidence'],r['exclusion_style'],'same_actor' if scope=='same_actor_new_activity' else 'other_actor')]
            ww=list(re.finditer(r'\S+',parent['sentence']));passage=parent['sentence'][:ww[parent['authored_followup_start_word']].start()].rstrip()
            actorfields=fs[r['donor_source_item']] if scope=='other_actor_new_activity' else f
            target=f['source_core_patient_np'] if r['role_evidence']=='reference_only' else actorfields['reference_phrase']
            eventword='original' if scope=='original_activity' else 'new'
            proposition='In that '+eventword+' '+f['activity_np']+', '+actorfields['actor']+' '+actorfields['auxiliary']+' '+f['progressive_vp']+' '+target+'.'
            for polarity in ('consistent','contradict'):
                q='Is the proposed additional fact consistent with the stated participant restriction?' if polarity=='consistent' else 'Does the proposed additional fact contradict the stated participant restriction?'
                proposed=('No' if scope=='original_activity' else 'Yes') if polarity=='consistent' else ('Yes' if scope=='original_activity' else 'No')
                rows.append(dict(item_id='E26:'+r['item_id']+':'+scope+':'+polarity,pair_id=r['pair_id'],verb_family=r['verb_family'],condition=r['condition'],
                    role_evidence=r['role_evidence'],exclusion_style=r['exclusion_style'],readout_kind='scope_compatibility',scope=scope,question_polarity=polarity,
                    passage=passage,proposition=proposition,question=q,gold=None,proposed_gold=proposed,
                    prior_faithful=r['faithful_role_frame'] and (scope=='original_activity' or parent['faithful_scope_actor']),
                    sentence_sha256=digest(passage),proposition_sha256=digest(proposition),question_sha256=digest(q),
                    semantics='Compatibility of an additional event fact with the explicitly scoped only statement, not whether the new event patient was already asserted. Distinct discourse actors/entities under ordinary reading; uncertainty must be flagged.'))
        # Source full matrix subject and verb are mechanically retained, then
        # independently reviewed. No inflection generation or vague Did-Q gold.
        assert source.count(f['source_full_subject_np'])==1
        vp=source.split(f['source_full_subject_np'],1)[1].strip()
        assert vp.endswith('.')
        parent=r;ww=list(re.finditer(r'\S+',r['sentence']));passage=r['sentence'][:ww[r['authored_followup_start_word']].start()].rstrip()
        for kind,subject,proposal in [('source_final',f['source_full_subject_np'],'Yes'),('source_actor_swap',f['actor'],'No')]:
            prop=subject[0].upper()+subject[1:]+' '+vp
            q='Is the proposed proposition stated by the first sentence of the passage?'
            rows.append(dict(item_id='E26:'+r['item_id']+':'+kind,pair_id=r['pair_id'],verb_family=r['verb_family'],condition=r['condition'],
                role_evidence=r['role_evidence'],exclusion_style=r['exclusion_style'],readout_kind=kind,scope='first_sentence',question_polarity='stated',
                passage=passage,proposition=prop,question=q,gold=None,proposed_gold=proposal,prior_faithful=r['faithful_role_frame'],
                sentence_sha256=digest(passage),proposition_sha256=digest(prop),question_sha256=digest(q),
                semantics='Whether the exact first sentence asserts the proposition; unasserted world possibility is not a Yes. Later only facts are not evidence for a matrix proposition absent from sentence one.'))
    assert len(rows)==1536 and len({r['item_id'] for r in rows})==1536
    write_jsonl(out,rows);return dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(out))


def adopt(data,reviews,idmap,out):
    annotations={}
    mapping=json.loads(idmap.read_text())
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for a in j['question_reviews']:
            key=mapping[a['id']];assert key not in annotations;annotations[key]=(a,sha(p))
    rows=list(map(json.loads,data.read_text().splitlines()));assert set(annotations)=={r['item_id'] for r in rows}
    for r in rows:
        a,h=annotations[r['item_id']]
        for k in ('sentence_sha256','proposition_sha256','question_sha256'):assert a[k]==r[k]
        assert a['answer'] in ('Yes','No',None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
        assert type(a['question_valid']) is bool
        r.update(audit=a,audit_review_sha256=h,eligible=a['question_valid'],gold=a['answer'] if a['question_valid'] and a['certainty']=='clear' else None)
    write_jsonl(out,rows)
    report=dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(data),audited_sha256=sha(out),eligible=sum(r['eligible'] for r in rows),clear_gold=sum(r['gold'] is not None for r in rows),proposed_label_agreement=sum(r['gold']==r['proposed_gold'] for r in rows),review_sha256=[sha(p) for p in reviews])
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.out),indent=2))
    else:print(json.dumps(adopt(args.data,args.reviews,args.idmap,args.out),indent=2))
