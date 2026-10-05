"""E38 audit-first reported selection contexts, not world probabilities from logprobs."""
import argparse
import collections
import json
from pathlib import Path
import re
from data import CACHE,sha,write_jsonl
from event_identity import digest

POLICIES=('candidate_only','procedure_unknown','independent_fair','selected_source','selected_other')
ORDERS=('source_first','other_first')


def build(cache,directory):
    fields=json.loads((directory/'selection-fields-v3.json').read_text());assert fields['model']=='gpt-6-luna';ff={r['id']:r for r in fields['rows']};assert len(ff)==24
    parents=[]
    for ex,path in [('contrast_parent',cache/'E31-material-preparation-v1/probability-audited-v1.jsonl'),('affirmative_mention_first',cache/'E36-material-preparation-v1/probability-audited-v1.jsonl')]:
        rr=[r for r in map(json.loads,path.read_text().splitlines()) if r['exclusion_style']=='named' and r['readout_actor_mode']=='other_actor' and r['boundary_marker']=='same_began' and (ex=='contrast_parent' or r['fact_realization']==ex)];assert len(rr)==192
        parents.extend((ex,r) for r in rr)
    raw=[];native=[];packets=[]
    for form,r in parents:
        f=ff[r['pair_id'].split(':')[1]];text=r['sentence'];words=list(re.finditer(r'\S+',text));pos=words[r['authored_followup_start_word']].start();prefix=text[:pos]
        assert r['target_start_char']>=pos and prefix.endswith(' ')
        for policy in POLICIES:
            for order in ORDERS:
                addition=f['policies'][policy][order]+' ';nt=prefix+addition+text[pos:];delta=len(addition)
                start=r['target_start_char']+delta;stop=r['target_stop_char']+delta;phrase=text[r['target_start_char']:r['target_stop_char']];assert nt[start:stop]==phrase
                nr=dict(r,item_id=f'E38:{form}:{policy}:{order}:{r["item_id"]}',parent_item_id=r['item_id'],fact_realization=form,selection_policy=policy,candidate_order=order,
                        condition=r['condition']+':'+policy+':'+order,sentence=nt,sentence_sha256=digest(nt),target_start_char=start,target_stop_char=stop,
                        target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',nt)) if w.start()<stop and w.end()>start],target_context_sha256=digest(nt[:start]),
                        authored_followup_start_word=r['authored_followup_start_word']+len(addition.split()),selection_context=prefix+addition.rstrip(),selection_context_sha256=digest(prefix+addition.rstrip()),
                        eligible=False,faithful_selection=False,transformation='Add independently authored new-target protocol after the new activity bridge; original source role facts and target-bearing continuation unchanged.')
                for k in list(nr):
                    if k.startswith('audit'):del nr[k]
                raw.append(nr);pid='P'+f'{len(raw)-1:04d}';nr['review_id']=pid
                packets.append(dict(id=pid,task='probability',text=nt,sentence_sha256=digest(nt),selection_context=nr['selection_context'],selection_context_sha256=nr['selection_context_sha256'],target=phrase,target_phrase_sha256=nr['target_phrase_sha256'],readout_frame=r['readout_frame'],policy=policy,source_candidate=f['source_candidate'],other_candidate=f['other_candidate']))
                if r['readout_frame']=='activity' and r['target_kind']=='source_np' and policy!='candidate_only':
                    question=f['fair_question'] if policy=='independent_fair' else f['selection_question'];query='fair' if policy=='independent_fair' else 'current'
                    nid='N'+f'{len(native)//2:04d}';passage=nr['selection_context']
                    packet=dict(id=nid,task='selection_question',passage=passage,passage_sha256=digest(passage),question=question,question_sha256=digest(question),policy=policy,source_candidate=f['source_candidate'],other_candidate=f['other_candidate'])
                    packets.append(packet)
                    for mode in ('base','priority'):
                        native.append(dict(packet,item_id=f'E38:{form}:{policy}:{order}:{r["item_id"]}:selection:{mode}',context_id=nid,query=query,mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],fact_realization=form,candidate_order=order,selection_policy=policy,
                                           role_evidence=r['role_evidence'],gold_answer_class=None,eligible=False,proposed_answer_class='equal_half' if policy=='independent_fair' else 'unspecified' if policy=='procedure_unknown' else 'source_candidate' if policy=='selected_source' else 'other_candidate'))
    assert len(raw)==3840 and len(native)==1536 and len(packets)==4608
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    # Assign by hash of id, avoiding form/order/policy confounding with auditor.
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=3840,native_contexts=768,native_variants=1536,full_rendered_packets=4608,fields_sha256=sha(directory/'selection-fields-v3.json'),candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def adopt(directory,reviews):
    annotations={}
    for path in reviews:
        j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
        for a in j['reviews']:
            assert a['id'] not in annotations;annotations[a['id']]=(a,sha(path))
    assert len(annotations)==4608
    report={}
    for task,n in [('probability',3840),('question',1536)]:
        rr=list(map(json.loads,(directory/f'{task}-candidates-v1.jsonl').read_text().splitlines()));assert len(rr)==n
        for r in rr:
            a,h=annotations[r['review_id'] if task=='probability' else r['context_id']]
            assert a['grammar'] in ('acceptable','marginal','unacceptable') and isinstance(a['selection_scope_clear'],bool)
            r.update(audit=a,audit_review_sha256=h,acceptable=a['grammar']=='acceptable',eligible=a['grammar']!='unacceptable' and a['selection_scope_clear'])
            if task=='probability':
                for k in ('sentence_sha256','selection_context_sha256','target_phrase_sha256'):assert a[k]==r[k]
                r['faithful_selection']=a['selection_scope_clear']
            else:
                for k in ('passage_sha256','question_sha256'):assert a[k]==r[k]
                assert a['answer_class'] in ('equal_half','unspecified','source_candidate','other_candidate',None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
                r['gold_answer_class']=a['answer_class'] if a['certainty']=='clear' else None;r['eligible']=r['eligible'] and r['gold_answer_class'] is not None
        out=directory/f'{task}-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rr)
        audit=dict(variants=n,audited_sha256=sha(out),candidate_sha256=sha(directory/f'{task}-candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],eligible=sum(r['eligible'] for r in rr),grammar=dict(collections.Counter(r['audit']['grammar'] for r in rr)))
        if task=='question':audit['proposed_agreement']=sum(r['gold_answer_class']==r['proposed_answer_class'] for r in rr)
        out.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2)+'\n');report[task]=audit
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews),indent=2))
