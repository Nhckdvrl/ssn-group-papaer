"""E30 one-word boundary intervention: separate -> second, both distinct events."""
import argparse
import json
from pathlib import Path
import re
from data import CACHE,sha,write_jsonl
from event_identity import digest


def build(cache,out):
    assert not out.exists();out.mkdir(parents=True)
    parent=cache/'E29-material-preparation-v2';built={};packets=[];mapping={}
    for task in ('probability','nli'):
        rows=list(map(json.loads,(parent/f'{task}-audited-v2.jsonl').read_text().splitlines()))
        chosen=[r for r in rows if (r['readout_actor_mode']!='original_activity' if task=='probability' else r['readout_kind'] in ('same_actor_new_activity','other_actor_new_activity'))]
        assert len(chosen)==(768 if task=='probability' else 192)
        result=[]
        for i,r in enumerate(chosen):
            text=r['sentence'] if task=='probability' else r['passage'];needle=' continued a separate ';assert text.count(needle)==1
            pos=text.index(needle)+len(' continued a ');newtext=text[:pos]+'second'+text[pos+len('separate'):]
            row=dict(r,item_id='E30:'+r['item_id'],parent_item_id=r['item_id'],boundary_marker='second',eligible=False,acceptable=False,faithful_ablation=False,
                     sentence_sha256=digest(newtext),transformation='Only separate -> second in the activity bridge; same second occurrence, actor, role fact, readout and target. Original source S1 is absent in both boundary conditions.')
            for k in list(row):
                if k.startswith('audit'):del row[k]
            if task=='probability':
                start,stop=r['target_start_char']-2,r['target_stop_char']-2;assert pos<start
                row.update(sentence=newtext,target_start_char=start,target_stop_char=stop,
                           target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',newtext)) if w.start()<stop and w.end()>start],target_context_sha256=digest(newtext[:start]))
                assert newtext[start:stop]==text[r['target_start_char']:r['target_stop_char']]
            else:row.update(passage=newtext,gold_relation=None,prior_relation=r['gold_relation'])
            result.append(row)
            key=('P' if task=='probability' else 'N')+f'{i:04d}';mapping[key]=row['item_id']
            p=dict(id=key,task=task,text=newtext,previous_text=text,sentence_sha256=row['sentence_sha256'],anchor=row['source_anchor'])
            if task=='probability':p.update(target=newtext[start:stop],target_phrase_sha256=row['target_phrase_sha256'],readout_frame=row['readout_frame'])
            else:p.update(proposition=row['proposition'],proposition_sha256=row['proposition_sha256'])
            packets.append(p)
        path=out/f'{task}-candidates-v1.jsonl';write_jsonl(path,result);built[task]=dict(variants=len(result),sha256=sha(path))
        if task=='nli':
            # Existing separately audited branch retained exactly for R8;
            # only the scope instruction is new at inference, not data/gold.
            path=out/'nli-separate-audited-v1.jsonl';write_jsonl(path,chosen)
            report=json.loads((parent/'nli-audited-v2.audit.json').read_text());report.update(variants=192,audited_sha256=sha(path),parent_audited_sha256=sha(parent/'nli-audited-v2.jsonl'))
            path.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    for shard in (0,1):
        pp=[p for i,p in enumerate(packets) if i%2==shard];assert len(pp)==480
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return built


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.cache,a.out),indent=2))
