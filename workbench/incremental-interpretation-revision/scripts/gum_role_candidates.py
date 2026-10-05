"""Mechanical GUM mention spans/UD argument candidates; no semantic gold."""
import argparse
import collections
import json
import hashlib
import re
from pathlib import Path
from data import CACHE,sha


def extract(directory,out):
    audit=json.loads((directory/'audit.json').read_text());documents=[];totals=collections.Counter()
    for source in audit['files']:
        path=directory/'dep'/source['filename'];assert sha(path)==source['sha256']
        sentences=[];mentions=[];active=collections.defaultdict(list)
        for block in path.read_text().strip().split('\n\n'):
            lines=block.splitlines();rows=[l.split('\t') for l in lines if l and not l.startswith('#') and l.split('\t')[0].isdigit()]
            if not rows:continue
            sid=next(l.removeprefix('# sent_id = ') for l in lines if l.startswith('# sent_id = '))
            text=next(l.removeprefix('# text = ') for l in lines if l.startswith('# text = '))
            si=len(sentences);byid={int(r[0]):r for r in rows};assert len(byid)==len(rows)
            for r in rows:
                column=re.search(r'(?:^|\|)Entity=([^|]+)',r[9])
                if not column:continue
                encoded=column.group(1);cursor=0
                while cursor<len(encoded):
                    if encoded[cursor]=='(':
                        stop=min([v for v in (encoded.find('(',cursor+1),encoded.find(')',cursor+1)) if v>=0],default=len(encoded))
                        body=encoded[cursor+1:stop];attrs=body.split('-');assert attrs[0].isdigit() and len(attrs)>=3,(path,sid,encoded)
                        gid=attrs[0]
                        record=dict(entity_id=gid,entity_type=attrs[1],information_status=attrs[2],sentence_index=si,sentence_id=sid,start_token=int(r[0]),attributes=body)
                        if stop<len(encoded) and encoded[stop]==')':record['stop_token']=int(r[0]);mentions.append(record);cursor=stop+1
                        else:active[gid].append(record);cursor=stop
                    else:
                        match=re.match(r'(\d+)\)',encoded[cursor:]);assert match,(path,sid,encoded[cursor:])
                        gid=match.group(1);assert gid in active
                        record=active[gid].pop()
                        if not active[gid]:del active[gid]
                        assert record['sentence_index']==si,'Cross-sentence span needs upstream-specific handling'
                        record['stop_token']=int(r[0]);mentions.append(record);cursor+=len(match.group(0))
            sentences.append(dict(sentence_id=sid,text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),tokens=[dict(id=int(r[0]),form=r[1],lemma=r[2],upos=r[3],head=int(r[6]),deprel=r[7]) for r in rows]))
            assert not active,(path,sid,active)
        chains=collections.defaultdict(list)
        for m in mentions:
            sentence=sentences[m['sentence_index']];tt=[t for t in sentence['tokens'] if m['start_token']<=t['id']<=m['stop_token']]
            m['token_forms']=[t['form'] for t in tt];m['upos']=[t['upos'] for t in tt]
            chains[m['entity_id']].append(m)
        candidates=[]
        for si,sentence in enumerate(sentences):
            words=sentence['tokens'];mm=[m for m in mentions if m['sentence_index']==si]
            def covering(token):return sorted([m for m in mm if m['start_token']<=token<=m['stop_token']],key=lambda m:m['stop_token']-m['start_token'])
            for verb in words:
                if verb['upos']!='VERB':continue
                subjects=[t for t in words if t['head']==verb['id'] and t['deprel']=='nsubj']
                objects=[t for t in words if t['head']==verb['id'] and t['deprel']=='obj']
                for subject in subjects:
                    for obj in objects:
                        am=covering(subject['id']);pm=[m for m in covering(obj['id']) if m['entity_type'] in ('person','animal')]
                        if not am or not pm:continue
                        a,p=am[0],pm[0]
                        if a['entity_id']==p['entity_id']:continue
                        alternatives=[gid for gid,ch in chains.items() if gid not in (a['entity_id'],p['entity_id']) and ch[0]['entity_type']==p['entity_type'] and any(m['sentence_index']<=si for m in ch)]
                        candidates.append(dict(candidate_id=f'{path.stem}:{sentence["sentence_id"]}:{verb["id"]}:{obj["id"]}',sentence_index=si,
                                               verb_token=verb['id'],verb_lemma=verb['lemma'],actor_mention=a,patient_mention=p,
                                               prior_other_same_type_entity_ids=sorted(alternatives)))
        alias_ids=[gid for gid,ch in chains.items() if ch[0]['entity_type'] in ('person','animal') and any('PROPN' in m['upos'] for m in ch) and any('NOUN' in m['upos'] and 'PROPN' not in m['upos'] for m in ch)]
        documents.append(dict(document_id=path.stem,source_sha256=source['sha256'],sentences=sentences,mentions=mentions,alias_entity_ids=alias_ids,ud_role_candidates=candidates))
        totals.update(documents=1,sentences=len(sentences),mentions=len(mentions),person_animal_alias_chains=len(alias_ids),ud_role_candidates=len(candidates),role_candidates_with_prior_alternative=sum(bool(c['prior_other_same_type_entity_ids']) for c in candidates))
    out.mkdir(exist_ok=False,parents=True)
    for i in range(3):(out/f'review-documents-{i}.json').write_text(json.dumps(dict(source_revision=audit['revision'],documents=documents[i::3]),indent=2)+'\n')
    report=dict(source_revision=audit['revision'],totals=dict(totals),documents=[dict(document_id=d['document_id'],source_sha256=d['source_sha256'],role_candidates=len(d['ud_role_candidates']),alias_chains=len(d['alias_entity_ids'])) for d in documents],
                limitations='Entity spans and UD arguments are copied annotation candidates, not event/patient/identity semantic gold. No automatic acceptable subset and no model inference.')
    (out/'mechanical-statistics.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=CACHE/'upstream/gum-audit');p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(extract(a.directory,a.out)['totals'],indent=2))
