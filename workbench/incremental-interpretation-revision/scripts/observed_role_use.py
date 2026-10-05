"""E49 observed second roles; whole-input semantic gold supplied externally."""
import argparse
import collections
import itertools
import json
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest


def build(cache,directory):
    author=json.loads((directory/'observed-second-role-fields-v2.json').read_text());assert author['model']=='gpt-6-luna'
    ff={r['id']:r for r in author['rows']};assert len(ff)==24
    af={r['id']:r for r in json.loads((cache/'E48-material-preparation-v2/alias-role-fields-v2.json').read_text())['rows']}
    inv={r['id']:r for r in json.loads((cache/'E47-material-preparation-v2/identity-status-fields-v2.json').read_text())['rows']}
    parents={r['pair_id'].split(':')[1]:r for r in map(json.loads,(cache/'E46-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines())}
    rows,packets=[],[]
    for sid,f in ff.items():
        for k in ('source_candidate','other_candidate','source_description','other_description','alias_intro'): assert f[k]==af[sid][k]
        for role in ('source','other'):assert f['facts']['minimal_'+role]==af[sid]['facts']['minimal_'+role]
        for old,new,form,inventory,predicate in itertools.product(('source','other'),('source','other'),('name','description'),(0,1),('same_began','different_began')):
            old_fact=f['facts']['minimal_'+old];unused=f[('other' if old=='source' else 'source')+'_candidate']+' was nearby.'
            second=f['second_facts'][predicate][form+'_'+new]
            passage=' '.join([f['alias_intro']]+([inv[sid]['name_inventory']] if inventory else [])+[old_fact,unused,second])
            metadata=dict(pair_id=parents[sid]['pair_id'],verb_family=parents[sid]['verb_family'],old_role=old,second_role=new,
                          second_fact_form=form,inventory_present=inventory,predicate=predicate,congruence='congruent' if old==new else 'incongruent',
                          old_actor=f['old_event']['actor'],old_action=f['old_event']['progressive_vp'],second_actor=f['second_facts'][predicate]['new_actor'],second_action=f['second_facts'][predicate]['progressive_vp'])
            for query in ('second','recap'):
                q=f['second_name_questions'][predicate] if query=='second' else f['recap_question'];rid=f'N{len(packets):04d}'
                packet=dict(id=rid,task='observed_role_question',query=query,passage=passage,passage_sha256=digest(passage),question=q,question_sha256=digest(q),
                            **{k:f[k] for k in ('source_candidate','other_candidate','source_description','other_description','alias_intro')})
                packets.append(packet)
                for mode in ('base','priority'):
                    rows.append(dict(packet,item_id='E49:'+rid+':'+mode,context_id=rid,mode=mode,**metadata,
                                     proposed_old_answer_class=old+'_candidate',proposed_answer_class=new+'_candidate',
                                     gold_old_answer_class=None,gold_answer_class=None,eligible=False))
    assert len(rows)==3072 and len(packets)==1536 and len({r['item_id'] for r in rows})==3072
    write_jsonl(directory/'question-candidates-v1.jsonl',rows);packets.sort(key=lambda r:digest(r['id']))
    for i in range(2):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]),indent=2)+'\n')
    return dict(native_variants=len(rows),contexts=len(packets),fields_sha256=sha(directory/'observed-second-role-fields-v2.json'),candidate_sha256=sha(directory/'question-candidates-v1.jsonl'))


def adopt(directory,reviews,experiment='E49'):
    annotations={}
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for r in j['reviews']:
            assert r['id'] not in annotations;annotations[r['id']]=(r,sha(p))
    variants,contexts={'E49':(3072,1536),'E50':(4608,2304)}[experiment]
    assert len(annotations)==contexts
    rows=list(map(json.loads,(directory/'question-candidates-v1.jsonl').read_text().splitlines()));assert len(rows)==variants
    for r in rows:
        a,h=annotations[r['context_id']]
        for k in ('passage_sha256','question_sha256'):assert r[k]==a[k]
        for k in ('role_scope_clear','alias_identity_clear','fixed_de_re_descriptions'):assert type(a[k]) is bool
        assert a['grammar'] in ('acceptable','marginal','unacceptable') and a['certainty'] in ('clear','interpretation_dependent','invalid')
        for k in ('old_answer_class','second_answer_class'):assert a[k] in ('source_candidate','other_candidate',None)
        r.update(audit=a,audit_review_sha256=h,acceptable=a['grammar']=='acceptable',gold_old_answer_class=a['old_answer_class'] if a['certainty']=='clear' else None,
                 gold_answer_class=a['second_answer_class'] if a['certainty']=='clear' else None,
                 eligible=a['grammar']!='unacceptable' and all(a[k] for k in ('role_scope_clear','alias_identity_clear','fixed_de_re_descriptions')) and a['certainty']=='clear')
    out=directory/'question-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rows)
    audit=dict(variants=len(rows),contexts=len(annotations),audited_sha256=sha(out),candidate_sha256=sha(directory/'question-candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],
               eligible=sum(r['eligible'] for r in rows),grammar=dict(collections.Counter(r['audit']['grammar'] for r in rows)),
               proposed_agreement=sum(r['gold_answer_class']==r['proposed_answer_class'] and r['gold_old_answer_class']==r['proposed_old_answer_class'] for r in rows))
    out.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2)+'\n');return audit


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews),indent=2))
