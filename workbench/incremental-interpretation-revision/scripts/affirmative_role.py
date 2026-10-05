"""E36 independent affirmative role realizations; raw inputs stay in cache."""
import argparse
import collections
import json
from pathlib import Path
import re
import numpy as np
from data import CACHE,sha,write_jsonl
from event_identity import digest
from aspect_reference import read_run
from analyze_source_ablation import stat,diff

FORMS=('affirmative_mention_first','affirmative_mention_last')


def build(cache,directory):
    fields=json.loads((directory/'fields-proposed-v1.json').read_text())
    assert fields['model']=='gpt-6-luna'
    ff={r['id']:r for r in fields['rows']}
    original={r['id']:r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    assert ff.keys()==original.keys()
    rows={};packets=[];idmap={}
    for task in ('probability','nli'):
        p29=list(map(json.loads,(cache/f'E29-material-preparation-v2/{task}-audited-v2.jsonl').read_text().splitlines()))
        p31=list(map(json.loads,(cache/f'E31-material-preparation-v1/{task}-audited-v1.jsonl').read_text().splitlines()))
        old=[r for r in p29 if r['exclusion_style']=='named' and (r['readout_actor_mode']=='original_activity' if task=='probability' else r['readout_kind'] in ('old_supported','old_excluded','unrelated_unknown_control'))]
        new=[r for r in p31 if r['exclusion_style']=='named']
        out=[]
        for r in old+new:
            sid=r['pair_id'].split(':')[1];source=original[sid];proposed=ff[sid]
            key='reference_only' if r['role_evidence']=='reference_only' else 'initial_only'
            oldfact=source[key+'_named_sentence'];fact=proposed['affirmative_'+key+'_sentence']
            clauses=fact.split('. ');assert len(clauses)==2 and clauses[1].startswith('The report also mentions ') and clauses[1].endswith('.')
            assert not any(re.search(r'\b'+w+r'\b',fact,re.I) for w in ('not','but','rather','instead'))
            text=r['sentence'] if task=='probability' else r['passage'];oldprefix=r['source_anchor']+' '+oldfact+' ';assert text.startswith(oldprefix)
            for form in FORMS:
                nf=fact if form.endswith('_last') else clauses[1]+' '+clauses[0]+'.'
                prefix=r['source_anchor']+' '+nf+' ';nt=prefix+text[len(oldprefix):]
                nr=dict(r,item_id='E36:'+form+':'+r['item_id'],parent_item_id=r['item_id'],fact_realization=form,
                        sentence_sha256=digest(nt),eligible=False,faithful_role_realization=False,
                        transformation='Independently authored affirmative only fact plus non-role report mention; the same two sentences exchanged. Original event anchor/continuation/target preserved.')
                for k in list(nr):
                    if k.startswith('audit'):del nr[k]
                if task=='probability':
                    delta=len(prefix)-len(oldprefix);start=r['target_start_char']+delta;stop=r['target_stop_char']+delta
                    phrase=text[r['target_start_char']:r['target_stop_char']];assert nt[start:stop]==phrase
                    nr.update(sentence=nt,target_start_char=start,target_stop_char=stop,target_context_sha256=digest(nt[:start]),
                              target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',nt)) if w.start()<stop and w.end()>start],
                              authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()))
                    packet=dict(task=task,target=phrase,target_phrase_sha256=nr['target_phrase_sha256'])
                else:
                    nr.update(passage=nt,gold_relation=None,parent_relation=r['gold_relation'])
                    packet=dict(task=task,proposition=r['proposition'],proposition_sha256=r['proposition_sha256'])
                out.append(nr);rid=('P' if task=='probability' else 'N')+f'{len(out)-1:04d}'
                packet.update(id=rid,text=nt,sentence_sha256=digest(nt),source_role_fact=oldfact,affirmative_role_fact=nf)
                packets.append(packet);idmap[rid]=nr['item_id']
        rows[task]=out;write_jsonl(directory/f'{task}-candidates-v1.jsonl',out)
    assert len(rows['probability'])==1920 and len(rows['nli'])==672
    (directory/'review-id-map.json').write_text(json.dumps(idmap,indent=2)+'\n')
    for i in range(2):
        pp=packets[i::2];assert len(pp)==1296
        (directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return dict(raw=1920,nli=672,fields_sha256=sha(directory/'fields-proposed-v1.json'),candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in rows})


def adopt(directory,reviews):
    mapping=json.loads((directory/'review-id-map.json').read_text());ann={}
    for path in reviews:
        review=json.loads(path.read_text());assert review['model']=='gpt-6-luna'
        for a in review['reviews']:
            key=mapping[a['id']];assert key not in ann;ann[key]=(a,sha(path))
    assert len(ann)==2592
    report={}
    for task,n in [('probability',1920),('nli',672)]:
        rr=list(map(json.loads,(directory/f'{task}-candidates-v1.jsonl').read_text().splitlines()));assert len(rr)==n
        for r in rr:
            a,h=ann[r['item_id']]
            assert a['sentence_sha256']==r['sentence_sha256']
            assert a['grammar'] in ('acceptable','marginal','unacceptable')
            assert isinstance(a['faithful_role'],bool) and isinstance(a['mention_only'],bool)
            r.update(audit=a,audit_review_sha256=h,faithful_role_realization=a['faithful_role'] and a['mention_only'],acceptable=a['grammar']=='acceptable',eligible=a['grammar']!='unacceptable' and a['faithful_role'] and a['mention_only'])
            if task=='probability':assert a['target_phrase_sha256']==r['target_phrase_sha256']
            else:
                assert a['proposition_sha256']==r['proposition_sha256'] and a['relation'] in ('entailed','contradicted','undetermined',None)
                assert a['certainty'] in ('clear','interpretation_dependent','invalid')
                r['gold_relation']=a['relation'] if a['certainty']=='clear' else None
        out=directory/f'{task}-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rr)
        audit=dict(variants=n,audited_sha256=sha(out),candidate_sha256=sha(directory/f'{task}-candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],eligible=sum(r['eligible'] for r in rr),faithful=sum(r['faithful_role_realization'] for r in rr),grammar=dict(collections.Counter(r['audit']['grammar'] for r in rr)))
        if task=='nli':audit.update(clear_gold=sum(r['gold_relation'] is not None for r in rr),parent_relation_agreement=sum(r['gold_relation']==r['parent_relation'] for r in rr))
        out.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2)+'\n');report[task]=audit
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews),indent=2))
