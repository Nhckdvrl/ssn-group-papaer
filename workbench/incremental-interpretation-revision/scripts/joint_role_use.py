"""E50 frozen E49 contexts; externally authored jointly queried uses."""
import argparse
import json
from pathlib import Path
from data import CACHE,sha,write_jsonl
from event_identity import digest
from observed_role_use import adopt

QUERIES=('pair_names','unanchored_recap','anchored_recap')


def build(cache,directory):
    f=json.loads((directory/'joint-role-use-question-fields-v1.json').read_text());assert f['model']=='gpt-6-luna';ff={r['id']:r for r in f['rows']};assert len(ff)==24
    parents=[r for r in map(json.loads,(cache/'E49-material-preparation-v1/question-audited-v1.jsonl').read_text().splitlines()) if r['query']=='second' and r['mode']=='base'];assert len(parents)==768
    rows,packets=[],[]
    for r in parents:
        sid=r['pair_id'].split(':')[1];author=ff[sid]
        for query in QUERIES:
            q=author['questions'][r['predicate']][query];nid=f'N{len(packets):04d}'
            packet=dict(id=nid,task='observed_role_question',query=query,passage=r['passage'],passage_sha256=r['passage_sha256'],question=q,question_sha256=digest(q),
                        **{k:r[k] for k in ('source_candidate','other_candidate','source_description','other_description','alias_intro')})
            packets.append(packet)
            for mode in ('base','priority'):
                nr=dict(r,**packet,item_id='E50:'+nid+':'+mode,parent_item_id=r['item_id'],context_id=nid,mode=mode,
                        proposed_old_answer_class=r['gold_old_answer_class'],proposed_answer_class=r['gold_answer_class'],
                        gold_old_answer_class=None,gold_answer_class=None,eligible=False,acceptable=False)
                for k in list(nr):
                    if k.startswith('audit'):del nr[k]
                rows.append(nr)
    assert len(rows)==len({r['item_id'] for r in rows})==4608 and len(packets)==2304
    write_jsonl(directory/'question-candidates-v1.jsonl',rows);packets.sort(key=lambda r:digest(r['id']))
    for i in range(2):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]),indent=2)+'\n')
    return dict(contexts=len(parents),audit_packets=len(packets),native_variants=len(rows),fields_sha256=sha(directory/'joint-role-use-question-fields-v1.json'),candidate_sha256=sha(directory/'question-candidates-v1.jsonl'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews,'E50'),indent=2))
