"""E18 audited predicate paraphrases, paired with immutable original E16."""
import argparse
import json
from pathlib import Path
import re
from data import sha, write_jsonl
from event_identity import digest
from patient_crossover import adopt
from entity_accessibility import analyze as compare_frames


def build(cache,fields_path,out):
    assert not out.exists()
    fields={r['pair_id']:r for r in json.loads(fields_path.read_text())['rows']}
    packets=json.loads((fields_path.parent/'paraphrase-packets.json').read_text())['packets']
    assert set(fields)=={r['pair_id'] for r in packets}
    for p in packets:
        assert fields[p['pair_id']]['input_sha256']==p['input_sha256']
        content={k:v for k,v in p.items() if k!='input_sha256'}
        assert digest(json.dumps(content,sort_keys=True,ensure_ascii=False,separators=(',',':')))==p['input_sha256']
    parents=[]
    for ex in ('E14','E15'):
        parents += [(ex,r) for r in map(json.loads,(cache/f'{ex}-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()) if r['target_kind']=='source_np' and r['episode_anchor']!='separate']
    ix={(ex,r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor']):r for ex,r in parents}
    output=[]
    for ex,r in parents:
        f=fields[r['pair_id']];template=f['paraphrased_template'];assert template.count('{TARGET}')==1
        words=list(re.finditer(r'\S+',r['sentence']));prefix=r['sentence'][:words[r['authored_followup_start_word']].start()]
        before,after=template.split('{TARGET}')
        # Whitespace-word targets must not share punctuation or other words.
        assert before.endswith(' ') and after.startswith(' ')
        for kind,o in [('source_np',r['source_np_option']),('other_source_np',1-r['source_np_option'])]:
            other=ix[(ex,r['pair_id'],o,r['condition'],r['episode_anchor'])]
            phrase=other['sentence'][other['target_start_char']:other['target_stop_char']]
            text=prefix+before+phrase+after;start=len(prefix+before);stop=start+len(phrase)
            nw=list(re.finditer(r'\S+',text));span=[i for i,w in enumerate(nw) if w.start()<stop and w.end()>start]
            assert ' '.join(nw[i].group() for i in span)==phrase
            nr=dict(r,item_id='E18:'+r['item_id']+':'+kind,target_kind=kind,sentence=text,parent_item_id=r['item_id'],parent_experiment=ex,
                target_start_char=start,target_stop_char=stop,target_span_word_indices=span,target_phrase_sha256=digest(phrase),target_context_sha256=digest(text[:start]),
                sentence_sha256=digest(text),predicate_fields_sha256=sha(fields_path),proposed_predicate_match=f['semantic_match'],
                transformation='Exact S1 and bridge retained; S2 activity predicate paraphrased by independent annotator, target is own or other author-provided NP.')
            for k in list(nr):
                if k.startswith('audit_'):del nr[k]
            output.append(nr)
    assert len(output)==528
    write_jsonl(out,output)
    return dict(variants=528,candidate_sha256=sha(out),fields_sha256=sha(fields_path))


def adopt_predicate(data,reviews,idmap,out):
    report=adopt(data,reviews,idmap,out)
    mapping=json.loads(idmap.read_text());annotations={}
    for p in reviews:
        for a in json.loads(p.read_text())['variant_reviews']:
            assert a['activity_match'] in ('clear','related_but_changed','changed','uncertain')
            assert type(a['activity_available_before_target']) is bool
            annotations[mapping[a['id']]]=a
    rows=list(map(json.loads,out.read_text().splitlines()))
    for r in rows:
        a=annotations[r['item_id']]
        r.update(audit_activity_match=a['activity_match'],audit_activity_available_before_target=a['activity_available_before_target'],
                 faithful_activity=r['eligible'] and a['activity_match']=='clear' and a['activity_available_before_target'])
        r['episodic_faithful_activity']=r['episodic_reference'] and r['faithful_activity']
    write_jsonl(out,rows)
    report.update(audited_sha256=sha(out),faithful_activity=sum(r['faithful_activity'] for r in rows),
        faithful_source_ids=sorted({r['pair_id'] for r in rows if r['faithful_activity']}))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def analyze(cache,newpath):
    result=compare_frames(cache,newpath,frame='paraphrase',strata=('all','eligible','acceptable','faithful_activity','episodic_reference','episodic_faithful_activity'))
    result.update(experiment='E18',primary='Original-predicate minus paraphrased-predicate GP-minus-comma patient preference; report transfer and same/separate interaction.',
        interpretation='Semantic-match strata defined by independent annotation before model inference. Transfer limits exact surface-verb echo; does not by itself establish event memory or successful prior correction.')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--fields',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.fields,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt_predicate(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
