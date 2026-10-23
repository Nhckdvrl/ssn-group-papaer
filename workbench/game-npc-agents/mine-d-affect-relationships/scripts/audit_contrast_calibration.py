#!/usr/bin/env python3
"""Read-only, post-hoc D-E13 integrity/quotation audit. Never changes scores or calls models."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def norm(text):
    return ' '.join(text.split())


def typography(text):
    return unicodedata.normalize('NFKC', norm(text)).translate(str.maketrans({'“':'"','”':'"','‘':"'",'’':"'",'—':'-','–':'-'}))


def classify_quote(quote, candidate, other):
    """Mechanical diagnostics, not a semantic entailment or hallucination judgment."""
    q,c,o=norm(quote),norm(candidate),norm(other)
    if q and q in c:
        return 'exact_short_below_eight_chars' if len(q)<8 else 'exact'
    if typography(q) and typography(q) in typography(c):
        return 'typography_only'
    pieces=[x.strip() for x in re.split(r'\.{3,}|…+',q) if x.strip()]
    if len(pieces)>1:
        at=0
        for piece in pieces:
            found=c.find(piece,at)
            if found<0:break
            at=found+len(piece)
        else:return 'ordered_ellipsis_fragments'
    if q and q in o:return 'exact_in_other_response'
    return 'requires_semantic_review'


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    data=a.asset_root/'data/contrast_D-E13';run=a.asset_root/'runs/D-E13'
    tasks=read(data/'tasks.jsonl');selected=read(run/'selected.jsonl')
    T={t['task_id']:t for t in tasks};S={s['task_id']:s for s in selected}
    assert len(T)==len(tasks)==230 and set(T)==set(S) and len(S)==len(selected)
    manifest=json.loads((data/'manifest.json').read_text())
    assert hashlib.sha256((data/'tasks.jsonl').read_bytes()).hexdigest()==manifest['task_sha256']
    pairs=defaultdict(list);stats=defaultdict(lambda:dict(judgments=0,valid=0,mappings=Counter(),quote_classes=Counter(),pair_consistency=Counter(),raw_finish=Counter()))
    first={x['task_id']:x for x in read(run/'first/responses.jsonl')}
    recovery={x['task_id']:x for x in read(run/'recovery/responses.jsonl')}
    rows=[]
    for t in tasks:
        pairs[t['probe_id'],t['material']].append(t)
        s=S[t['task_id']];b=json.loads(t['messages'][1]['content']);st=stats[t['material']]
        st['judgments']+=1;st['valid']+=s['valid']
        raw=recovery.get(t['task_id'],first[t['task_id']]);st['raw_finish'][str(raw.get('finish_reason'))]+=1
        row=dict(task_id=t['task_id'],valid=s['valid'],quote_diagnostics=[])
        if s['valid']:
            v=s['result'];st['mappings'][v['mapping']]+=1
            for q in v['quotes']:
                cls=classify_quote(q['quote'],b['response_'+str(q['response'])],b['response_'+str(3-q['response'])])
                st['quote_classes'][cls]+=1
                row['quote_diagnostics'].append(dict(response=q['response'],quote=q['quote'],mechanical_class=cls))
        rows.append(row)
    for (probe,material),pair in pairs.items():
        pair.sort(key=lambda t:t['orientation']);assert [t['orientation'] for t in pair]==[0,1]
        b0,b1=[json.loads(t['messages'][1]['content']) for t in pair]
        assert {k:v for k,v in b0.items() if not k.startswith('response_')}=={k:v for k,v in b1.items() if not k.startswith('response_')}
        assert b0['response_1']==b1['response_2'] and b0['response_2']==b1['response_1']
        if material=='identical_reference':assert b0['response_1']==b0['response_2']
        else:assert {t['expected_mapping'] for t in pair}=={'A1_B2','A2_B1'}
        r0,r1=[S[t['task_id']]['result'] for t in pair]
        category='invalid_one_or_both'
        if r0 is not None and r1 is not None:
            x,y=r0['mapping'],r1['mapping']
            if x==y=='underdetermined':category='both_abstain'
            elif {x,y}=={'A1_B2','A2_B1'}:category='consistent_definite'
            elif x==y:category='same_position_mapping_after_swap'
            else:category='abstention_changes_after_swap'
        stats[material]['pair_consistency'][category]+=1
    result=dict(experiment='D-E13',post_hoc=True,model_calls=0,primary_scores_changed=False,
        source_sha256={str(f.relative_to(a.asset_root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [data/'tasks.jsonl',run/'selected.jsonl']},
        verified_swap_pairs=len(pairs),groups=dict(stats),rows=rows,
        interpretation='Mechanical quote categories retain the original exact-substring score. Ellipsis/typography mismatch is not automatically fabricated evidence; unresolved paraphrases require reading. Position-stable mapping can reflect ambiguity or judge bias; it is not an actor failure rate.')
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
