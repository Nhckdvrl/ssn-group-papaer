"""E46 composition of independently authored E43/E44/E45 fields, all rendered audited."""
import argparse
import itertools
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt


def build(cache, directory):
    def fields(ex, filename):
        return {r['id']:r for r in json.loads((cache/f'{ex}-material-preparation-v1'/filename).read_text())['rows']}
    scaffold=fields('E45','scaffold-name-fields-v1.json')
    minimal=fields('E43','minimal-role-fields-v1.json')
    scene=fields('E44','scene-role-fields-v1.json')
    parents=[r for r in map(json.loads,(cache/'E45-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()) if r['readout_actor_mode'] in ('original_activity','other_actor')]
    assert len(parents)==1152
    endpoint={}
    for r in map(json.loads,(cache/'E44-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()):
        if r['scene_policy']=='no_protocol' and r['readout_actor_mode'] in ('original_activity','other_actor'):
            key=(r['pair_id'],r['fact_realization'].replace('balanced_','plain_'),r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind'])
            assert key not in endpoint;endpoint[key]=r
    assert len(endpoint)==1152
    raw,native,packets=[],[],[];endpoints={'E45':0,'E44':0}
    for identity,report,event in itertools.product((0,1),repeat=3):
        cell=f'I{identity}R{report}E{event}'
        for r in parents:
            sid=r['pair_id'].split(':')[1];f,m,s=scaffold[sid],minimal[sid],scene[sid]
            role='source' if r['role_evidence']=='source_patient_stated' else 'other'
            order='first' if r['fact_realization'].endswith('_first') else 'last'
            unused=f['other_candidate' if role=='source' else 'source_candidate']
            report_sentence=f'The report also mentions {unused}.'
            oldfact=f['facts'][f'plain_{order}_{role}']
            assert oldfact.count(report_sentence)==1
            reified_role=oldfact.replace(report_sentence,'').strip()
            ordinary_role=m['facts']['minimal_'+role]
            nearby=s['facts']['balanced_last_'+role].removeprefix(ordinary_role).strip()
            assert nearby==unused+' was nearby.'
            role_sentence=reified_role if event else ordinary_role
            unused_sentence=report_sentence if report else nearby
            fact=' '.join((unused_sentence,role_sentence) if order=='first' else (role_sentence,unused_sentence))
            oldprefix=r['source_anchor']+' '+f['identity_intro']+' '+oldfact+' '
            parts=([r['source_anchor']] if event else [])+([f['identity_intro']] if identity else [])+[fact]
            prefix=' '.join(parts)+' '
            assert r['sentence'].startswith(oldprefix)
            text=prefix+r['sentence'][len(oldprefix):]
            delta=len(prefix)-len(oldprefix);a,b=r['target_start_char']+delta,r['target_stop_char']+delta
            target=text[a:b];assert target==r['sentence'][r['target_start_char']:r['target_stop_char']]
            if cell=='I1R1E1':
                assert text==r['sentence'];endpoints['E45']+=1
            if cell=='I0R0E0':
                key=(r['pair_id'],r['fact_realization'],r['readout_actor_mode'],r.get('boundary_marker'),r['role_evidence'],r['readout_frame'],r['target_kind'])
                assert text==endpoint[key]['sentence'];endpoints['E44']+=1
            rid=f'P{len(raw):05d}';form=cell+'_'+r['fact_realization']
            nr=dict(r,item_id='E46:'+cell+':'+r['item_id'],parent_item_id=r['item_id'],review_id=rid,fact_realization=form,
                    scaffold_cell=cell,identity_intro_present=identity,report_mention_present=report,event_reification_present=event,
                    fact_order=order,sentence=text,sentence_sha256=digest(text),target_start_char=a,target_stop_char=b,
                    target_context_sha256=digest(text[:a]),role_context_sha256=digest(prefix.rstrip()),
                    target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<b and w.end()>a],
                    authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),eligible=False,acceptable=False,
                    transformation='Factorize identity roster, unused report versus nearby, and event anchor plus nominal role restatement. All role/mention components independently authored earlier; combined full rendered inputs newly audited. Exact frozen E45/E44 endpoints.')
            for k in list(nr):
                if k.startswith('audit'):del nr[k]
            raw.append(nr)
            packets.append(dict(id=rid,task='probability',text=text,sentence_sha256=digest(text),role_context=prefix.rstrip(),role_context_sha256=digest(prefix.rstrip()),
                                target=target,target_phrase_sha256=nr['target_phrase_sha256'],source_candidate=f['source_candidate'],other_candidate=f['other_candidate']))
            if r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                nid=f'N{len(native)//2:04d}'
                packet=dict(id=nid,task='role_question',passage=prefix.rstrip(),passage_sha256=digest(prefix.rstrip()),question=f['current_question'],question_sha256=digest(f['current_question']),
                            source_candidate=f['source_candidate'],other_candidate=f['other_candidate'])
                packets.append(packet)
                for mode in ('base','priority'):
                    native.append(dict(packet,item_id=nr['item_id']+':current:'+mode,context_id=nid,query='current',mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],
                                       role_evidence=r['role_evidence'],fact_realization=form,scaffold_cell=cell,fact_order=order,
                                       proposed_answer_class=role+'_candidate',gold_answer_class=None,eligible=False))
    assert len(raw)==9216 and len(native)==1536 and len(packets)==9984 and endpoints=={'E45':1152,'E44':1152}
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=len(raw),native_variants=len(native),full_audit_packets=len(packets),exact_endpoints=endpoints,
                candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def split(directory):
    path=directory/'probability-audited-v1.jsonl';rows=list(map(json.loads,path.read_text().splitlines()))
    assert len(rows)==9216
    for identity,event in itertools.product((0,1),repeat=2):
        rr=[r for r in rows if r['identity_intro_present']==identity and r['event_reification_present']==event]
        assert len(rr)==2304
        out=directory/f'probability-I{identity}E{event}-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rr)
        j=json.loads(path.with_suffix('.audit.json').read_text());j.update(variants=len(rr),audited_sha256=sha(out),parent_audited_sha256=sha(path),eligible=sum(r['eligible'] for r in rr))
        out.with_suffix('.audit.json').write_text(json.dumps(j,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt','split']);p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.directory),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews,'E46'),indent=2))
    else:split(a.directory)
