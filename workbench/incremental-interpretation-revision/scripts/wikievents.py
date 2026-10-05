"""Pinned cache-only WikiEvents loader; annotations are not entailment gold."""
import argparse
import collections
import json
from pathlib import Path
from data import CACHE,sha


def load(directory,split):
    manifest=json.loads((directory/'download-manifest.json').read_text())
    files={r['filename']:r for r in manifest['files']}
    for name in (split+'.jsonl','coref-'+split+'.jsonlines'):assert sha(directory/name)==files[name]['sha256']
    documents=list(map(json.loads,(directory/(split+'.jsonl')).read_text().splitlines()))
    coref={r['doc_key']:r for r in map(json.loads,(directory/('coref-'+split+'.jsonlines')).read_text().splitlines())}
    assert len(documents)==len(coref)==files[split+'.jsonl']['rows']
    for d in documents:
        entities={r['id']:r for r in d['entity_mentions']};assert len(entities)==len(d['entity_mentions'])
        tokens=[t for s in d['sentences'] for t in s[0]];assert [t[0] for t in tokens]==d['tokens']
        offsets=[];cursor=0
        for sentence in d['sentences']:offsets.append(cursor);cursor+=len(sentence[0])
        def span(r):
            a,b=r['start'],r['end'];si=r['sent_idx'];s=d['sentences'][si];off=offsets[si]
            assert off<=a<b<=off+len(s[0]);origin=s[0][0][1]
            return s[1][tokens[a][1]-origin:tokens[b-1][2]-origin]
        ci=coref[d['doc_id']];assert len(ci['clusters'])==len(ci['informative_mentions'])
        clustered=[e for cluster in ci['clusters'] for e in cluster]
        assert len(clustered)==len(set(clustered)) and set(clustered)<=entities.keys()
        for event in d['event_mentions']:
            for arg in event['arguments']:assert arg['entity_id'] in entities
        yield dict(document_id=d['doc_id'],split=split,source_files_sha256={name:files[name]['sha256'] for name in (split+'.jsonl','coref-'+split+'.jsonlines')},
                   sentences=[dict(sentence_index=i,text=s[1],text_sha256=__import__('hashlib').sha256(s[1].encode()).hexdigest(),token_start=offsets[i],token_stop=offsets[i]+len(s[0])) for i,s in enumerate(d['sentences'])],
                   tokens=d['tokens'],entities=[dict(r,source_span_text=span(r),span_text_matches_annotation=span(r)==r['text']) for r in entities.values()],
                   events=[dict(e,source_trigger_span_text=span(e['trigger']),trigger_span_text_matches_annotation=span(e['trigger'])==e['trigger']['text']) for e in d['event_mentions']],
                   entity_coreference=ci,semantic_gold_status='Published argument/coreference annotation, not independently checked prefix entailment or event identity.',
                   event_coreference_status='Not exposed by these six release files; distinct mention IDs do not certify distinct real-world events.')


def audit(directory):
    manifest=json.loads((directory/'download-manifest.json').read_text());out=dict(manifest,statistics={},text_redistribution='Code MIT does not confer news-text redistribution rights. Original text stays cache-only.',
            offset_semantics='Token offsets retain original source spacing; released document text concatenates stripped sentences. Loader uses each published sentence text and offsets relative to its first token; never document text[absolute offsets].')
    for split in ('train','dev','test'):
        counts=collections.Counter();types=collections.Counter();roles=collections.Counter();anomalies=[]
        for d in load(directory,split):
            counts.update(documents=1,tokens=len(d['tokens']),sentences=len(d['sentences']),entity_mentions=len(d['entities']),event_mentions=len(d['events']),
                          argument_links=sum(len(e['arguments']) for e in d['events']),coref_clusters=len(d['entity_coreference']['clusters']))
            for e in d['entities']:
                if not e['span_text_matches_annotation']:anomalies.append(dict(kind='entity',document_id=d['document_id'],id=e['id']))
            for e in d['events']:
                types[e['event_type']]+=1;roles.update(a['role'] for a in e['arguments'])
                if not e['trigger_span_text_matches_annotation']:anomalies.append(dict(kind='trigger',document_id=d['document_id'],id=e['id']))
        out['statistics'][split]=dict(counts,event_types=dict(types),argument_roles=dict(roles),per_sentence_span_disagreements=anomalies)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=CACHE/'upstream/wikievents-audit');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(audit(a.directory),indent=2)+'\n')
