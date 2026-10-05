"""E39 full-NP role worlds, symmetric lexical bags and original continuations."""
import argparse
import collections
import json
from pathlib import Path
import re
from data import CACHE,sha,write_jsonl
from event_identity import digest

FORMS=('contrast_named','affirmative_mention_first','affirmative_mention_last')


def build(cache,directory):
    fields=json.loads((directory/'named-role-fields-v2.json').read_text());assert fields['model']=='gpt-6-luna';ff={r['id']:r for r in fields['rows']};assert len(ff)==24
    original={r['id']:r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    questions={r['id']:r for r in json.loads((cache/'E37-material-preparation-v1/question-fields-v1.json').read_text())['rows']}
    parents=[]
    for ex,path in [('old',cache/'E29-material-preparation-v2/probability-audited-v2.jsonl'),('new',cache/'E31-material-preparation-v1/probability-audited-v1.jsonl')]:
        rr=[r for r in map(json.loads,path.read_text().splitlines()) if r['exclusion_style']=='named' and (ex=='new' or r['readout_actor_mode']=='original_activity')]
        assert len(rr)==(192 if ex=='old' else 768);parents.extend(rr)
    raw=[];native=[];packets=[]
    for r in parents:
        sid=r['pair_id'].split(':')[1];f=ff[sid];o=original[sid];is_source=r['role_evidence']=='initial_patient_only';role='source' if is_source else 'other'
        oldfact=o['initial_only_named_sentence' if is_source else 'reference_only_named_sentence'];oldprefix=r['source_anchor']+' '+oldfact+' ';assert r['sentence'].startswith(oldprefix)
        for form in FORMS:
            fkey=('contrast' if form=='contrast_named' else 'affirmative_first' if form.endswith('_first') else 'affirmative_last')+'_'+role
            fact=f['facts'][fkey];prefix=r['source_anchor']+' '+f['identity_intro']+' '+fact+' ';nt=prefix+r['sentence'][len(oldprefix):]
            delta=len(prefix)-len(oldprefix);start=r['target_start_char']+delta;stop=r['target_stop_char']+delta;phrase=r['sentence'][r['target_start_char']:r['target_stop_char']];assert nt[start:stop]==phrase
            nr=dict(r,item_id=f'E39:{form}:{r["item_id"]}',parent_item_id=r['item_id'],parent_role_evidence=r['role_evidence'],role_evidence=role+'_patient_only',fact_realization=form,
                    source_candidate=f['source_candidate'],other_candidate=f['other_candidate'],sentence=nt,sentence_sha256=digest(nt),target_start_char=start,target_stop_char=stop,
                    target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',nt)) if w.start()<stop and w.end()>start],target_context_sha256=digest(nt[:start]),
                    authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),eligible=False,faithful_named_roles=False,
                    transformation='Replace reference-only role with second full-NP patient; explicit distinct-entity introduction and symmetric named role worlds. Original event anchor/continuation/target preserved.')
            for k in list(nr):
                if k.startswith('audit'):del nr[k]
            rid='P'+f'{len(raw):04d}';nr['review_id']=rid;raw.append(nr)
            packets.append(dict(id=rid,task='probability',text=nt,sentence_sha256=digest(nt),role_context=prefix.rstrip(),role_context_sha256=digest(prefix.rstrip()),target=phrase,target_phrase_sha256=nr['target_phrase_sha256'],source_candidate=f['source_candidate'],other_candidate=f['other_candidate']))
            nr['role_context_sha256']=digest(prefix.rstrip())
            if r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                nid='N'+f'{len(native)//2:04d}';question=questions[sid]['anchor_current_question'];passage=prefix.rstrip()
                packet=dict(id=nid,task='role_question',passage=passage,passage_sha256=digest(passage),question=question,question_sha256=digest(question),source_candidate=f['source_candidate'],other_candidate=f['other_candidate']);packets.append(packet)
                for mode in ('base','priority'):
                    native.append(dict(packet,item_id=f'E39:{form}:{r["item_id"]}:role_question:{mode}',context_id=nid,query='current',mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],role_evidence=nr['role_evidence'],fact_realization=form,
                                       proposed_answer_class='source_candidate' if is_source else 'other_candidate',gold_answer_class=None,eligible=False))
    assert len(raw)==2880 and len(native)==288 and len(packets)==3024
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(2):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]),indent=2)+'\n')
    return dict(raw=2880,native_contexts=144,native_variants=288,fields_sha256=sha(directory/'named-role-fields-v2.json'),candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def adopt(directory,reviews,experiment='E39',version=1):
    annotations={}
    for path in reviews:
        j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
        for a in j['reviews']:
            detail=a.get('raw',a.get('question',{}))
            assert isinstance(detail,dict) and not (set(detail)&set(a))
            normalized=dict(a,**detail)
            if 'grammaticality' in normalized:
                assert 'grammar' not in normalized or normalized['grammar']==normalized['grammaticality']
                normalized['grammar']=normalized['grammaticality']
            assert a['id'] not in annotations;annotations[a['id']]=(normalized,sha(path))
    sizes={'E39':(2880,288,3024),'E40':(1920,192,2016),'E41':(4608,1152,5184),'E43':(960,96,1008),'E44':(3456,576,3744),'E45':(1920,192,2016),'E46':(9216,1536,9984),'E47':(9216,1920,10176),'E48':(9216,864,9648)}[experiment]
    assert len(annotations)==sizes[2]
    report={};pending=[]
    for task,n in [('probability',sizes[0]),('question',sizes[1])]:
        rr=list(map(json.loads,(directory/f'{task}-candidates-v1.jsonl').read_text().splitlines()));assert len(rr)==n
        for r in rr:
            a,h=annotations[r['review_id'] if task=='probability' else r['context_id']]
            assert a['grammar'] in ('acceptable','marginal','unacceptable') and isinstance(a['role_scope_clear'],bool) and isinstance(a['distinct_recipients'],bool)
            r.update(audit=a,audit_review_sha256=h,acceptable=a['grammar']=='acceptable',eligible=a['grammar']!='unacceptable' and a['role_scope_clear'] and a['distinct_recipients'])
            if experiment in ('E41','E44'):
                assert isinstance(a['availability_scope_clear'],bool)
                r['eligible']=r['eligible'] and a['availability_scope_clear']
            if experiment=='E48':
                for k in ('alias_identity_clear','fixed_de_re_descriptions','fact_form_equivalent'):
                    assert isinstance(a[k],bool)
                    r['eligible']=r['eligible'] and a[k]
            if experiment=='E47':
                assert isinstance(a['identity_status_clear'],bool)
                r['eligible']=r['eligible'] and a['identity_status_clear']
            if task=='probability':
                for k in ('sentence_sha256','role_context_sha256','target_phrase_sha256'):assert a[k]==r[k]
                r['faithful_named_roles']=a['role_scope_clear'] and a['distinct_recipients']
            else:
                for k in ('passage_sha256','question_sha256'):assert a[k]==r[k]
                assert a['answer_class'] in ('source_candidate','other_candidate','both_ready','unspecified','asserted_identity','unverified_quote','not_asserted',None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
                r['gold_answer_class']=a['answer_class'] if a['certainty']=='clear' else None;r['eligible']=r['eligible'] and r['gold_answer_class'] is not None
        out=directory/f'{task}-audited-v{version}.jsonl';assert not out.exists()
        audit=dict(variants=n,candidate_sha256=sha(directory/f'{task}-candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],eligible=sum(r['eligible'] for r in rr),grammar=dict(collections.Counter(r['audit']['grammar'] for r in rr)))
        if task=='question':audit['proposed_agreement']=sum(r['gold_answer_class']==r['proposed_answer_class'] for r in rr)
        pending.append((task,out,rr,audit))
    # Validate every task before writing either audited data file.
    for task,out,rr,audit in pending:
        write_jsonl(out,rr);audit['audited_sha256']=sha(out)
        out.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2)+'\n');report[task]=audit
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews),indent=2))
