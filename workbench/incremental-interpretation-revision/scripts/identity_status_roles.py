"""E47 assertion status versus matched lexical presence and names inventory."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE,sha,write_jsonl
from event_identity import digest
from named_patient_roles import adopt

FORMS=('absent','asserted','quoted_unverified','name_inventory')


def build(cache,directory):
    def fields(ex,name):return {r['id']:r for r in json.loads((cache/f'{ex}-material-preparation-v1'/name).read_text())['rows']}
    author=json.loads((directory/'identity-status-fields-v2.json').read_text());assert author['model']=='gpt-6-luna';ff={r['id']:r for r in author['rows']}
    scaffold=fields('E45','scaffold-name-fields-v1.json');minimal=fields('E43','minimal-role-fields-v1.json');scene=fields('E44','scene-role-fields-v1.json')
    assert len(ff)==24 and ff.keys()==scaffold.keys()
    allparents=list(map(json.loads,(cache/'E46-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()))
    parents=[r for r in allparents if r['identity_intro_present']==0 and r['report_mention_present']==0];assert len(parents)==2304
    asserted_ix={r['item_id'].replace('E46:I1R0','E46:I0R0',1):r for r in allparents if r['identity_intro_present']==1 and r['report_mention_present']==0}
    raw,native,packets=[],[],[];endpoint={'absent':0,'asserted':0}
    for form in FORMS:
        for r in parents:
            sid=r['pair_id'].split(':')[1];f,p,m,s=ff[sid],scaffold[sid],minimal[sid],scene[sid]
            for key in ('source_candidate','other_candidate'):assert f[key]==p[key]
            assert f['asserted_identity']==p['identity_intro'] and f['asserted_identity'] in f['quoted_identity']
            role='source' if r['role_evidence']=='source_patient_stated' else 'other';order=r['fact_order'];event=r['event_reification_present']
            unused=p['other_candidate' if role=='source' else 'source_candidate']
            oldrole=p['facts']['plain_last_'+role].replace('The report also mentions '+unused+'.','').strip() if event else m['facts']['minimal_'+role]
            nearby=unused+' was nearby.';fact=' '.join((nearby,oldrole) if order=='first' else (oldrole,nearby))
            anchor=[r['source_anchor']] if event else []
            oldprefix=' '.join(anchor+[fact])+' '
            status={'absent':'','asserted':f['asserted_identity'],'quoted_unverified':f['quoted_identity'],'name_inventory':f['name_inventory']}[form]
            prefix=' '.join(anchor+([status] if status else [])+[fact])+' '
            assert r['sentence'].startswith(oldprefix)
            text=prefix+r['sentence'][len(oldprefix):];delta=len(prefix)-len(oldprefix)
            a,b=r['target_start_char']+delta,r['target_stop_char']+delta;target=text[a:b];assert target==r['sentence'][r['target_start_char']:r['target_stop_char']]
            if form=='absent':assert text==r['sentence'];endpoint[form]+=1
            if form=='asserted':assert text==asserted_ix[r['item_id']]['sentence'];endpoint[form]+=1
            rid=f'P{len(raw):04d}';realization=f'{form}_E{event}_'+order
            nr=dict(r,item_id='E47:'+form+':'+r['item_id'],parent_item_id=r['item_id'],identity_form=form,fact_realization=realization,
                    sentence=text,sentence_sha256=digest(text),target_start_char=a,target_stop_char=b,target_context_sha256=digest(text[:a]),
                    role_context_sha256=digest(prefix.rstrip()),review_id=rid,eligible=False,acceptable=False,
                    target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<b and w.end()>a],
                    authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),
                    transformation='Keep E46 nearby scenarios and role facts; vary asserted identity, identical unverified quote body, names/descriptions inventory, or absence. Not semantic equivalence or equal length. Old/new readouts unchanged.')
            for k in list(nr):
                if k.startswith('audit'):del nr[k]
            raw.append(nr);packets.append(dict(id=rid,task='probability',text=text,sentence_sha256=digest(text),role_context=prefix.rstrip(),role_context_sha256=digest(prefix.rstrip()),
                                              target=target,target_phrase_sha256=nr['target_phrase_sha256'],source_candidate=f['source_candidate'],other_candidate=f['other_candidate']))
            if r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                queries=[('current',p['current_question'],role+'_candidate')]
                if order=='first' and role=='source':
                    gold={'absent':'not_asserted','asserted':'asserted_identity','quoted_unverified':'unverified_quote','name_inventory':'not_asserted'}[form]
                    queries.append(('identity_status',f['identity_status_question'],gold))
                for query,question,gold in queries:
                    nid=f'N{len(native)//2:04d}';packet=dict(id=nid,task='role_question',query=query,passage=prefix.rstrip(),passage_sha256=digest(prefix.rstrip()),
                                                         question=question,question_sha256=digest(question),source_candidate=f['source_candidate'],other_candidate=f['other_candidate'])
                    packets.append(packet)
                    for mode in ('base','priority'):
                        native.append(dict(packet,item_id=nr['item_id']+':'+query+':'+mode,context_id=nid,mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],
                                           identity_form=form,event_reification_present=event,fact_order=order,role_evidence=r['role_evidence'],fact_realization=realization,
                                           proposed_answer_class=gold,gold_answer_class=None,eligible=False))
    assert len(raw)==9216 and len(native)==1920 and len(packets)==10176 and endpoint=={'absent':2304,'asserted':2304}
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=len(raw),native_variants=len(native),full_audit_packets=len(packets),exact_endpoints=endpoint,fields_sha256=sha(directory/'identity-status-fields-v2.json'),
                candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def split(directory):
    path=directory/'probability-audited-v1.jsonl';rows=list(map(json.loads,path.read_text().splitlines()));assert len(rows)==9216
    for form in FORMS:
        rr=[r for r in rows if r['identity_form']==form];assert len(rr)==2304
        out=directory/f'probability-{form}-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rr)
        j=json.loads(path.with_suffix('.audit.json').read_text());j.update(variants=len(rr),audited_sha256=sha(out),parent_audited_sha256=sha(path),eligible=sum(r['eligible'] for r in rr))
        out.with_suffix('.audit.json').write_text(json.dumps(j,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt','split']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.directory),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews,'E47'),indent=2))
    else:split(a.directory)
