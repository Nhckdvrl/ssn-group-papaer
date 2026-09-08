"""Preserve released full-story coreference; never infer window-local support."""
from pathlib import Path
import argparse, collections, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from corpus import Corpus
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='experiments/E000c_coreference_audit');args=parser.parse_args()
    config=json.loads((ROOT/'experiments/E000_data_audit/protocol.json').read_text())
    c=Corpus(ROOT/config['source']); rows,issues,_=c.inventory();assert not issues
    out=ROOT/args.out;out.mkdir(exist_ok=False)
    parent={};spans={};edges=[]
    def key(refs):
        span=c.span(refs);k=tuple(span['leaf_ids']);assert k
        spans.setdefault(k,span);parent.setdefault(k,k);return k
    def find(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for s in c.sentences:
        for f in s.findall('./sem/frames/frame'):
            if f.get('name')!='Coreference':continue
            fes={e.get('name'):e for e in f.findall('fe')}
            assert set(fes)=={'Current','Coreferent'}
            a=key([n.get('idref') for n in fes['Current'].findall('fenode')])
            b=key([n.get('idref') for n in fes['Coreferent'].findall('fenode')])
            parent[find(a)]=find(b)
            edges.append({'frame_id':f.get('id'),'current':list(a),'coreferent':list(b)})
    groups=collections.defaultdict(list)
    for k in parent:groups[find(k)].append(k)
    groups={k:sorted(v) for k,v in groups.items()}
    results=[];counts=collections.Counter()
    for r in rows:
        if not r['source_link_present']:continue
        k=tuple(r['source_link']['leaf_ids'])
        equivalents=groups[find(k)] if k in parent else [k]
        ss=[spans.get(x,r['source_link']) for x in equivalents]
        source_local=set(r['source_link']['sentence_ids'])=={r['sentence_id']}
        any_local=any(set(s['sentence_ids'])=={r['sentence_id']} for s in ss)
        counts['linked_NIs']+=1;counts['exact_span_in_coreference_graph']+=int(k in parent)
        counts['source_span_in_target_sentence']+=int(source_local)
        counts['any_global_equivalent_in_target_sentence']+=int(any_local)
        counts['source_nonlocal_but_global_equivalent_local']+=int(any_local and not source_local)
        results.append({'id':r['id'],'interpretation':r['interpretation'],
                        'source_link':r['source_link'],'exact_source_span_in_graph':k in parent,
                        'full_story_equivalent_spans':ss,
                        'source_span_local':source_local,'any_global_equivalent_local':any_local,
                        'window_local_support':None})
    (out/'source_edges.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in edges))
    (out/'linked_NI_equivalents.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in results))
    report={'source_sha256':c.sha256,'source_coreference_edges':len(edges),
            'unique_mention_spans':len(parent),'equivalence_classes':len(groups),
            'largest_class_mentions':max(map(len,groups.values())), 'counts':dict(counts),
            'matching':'Exact complete terminal-span equality; Current FE, not target head; never split multi-node phrases into separate referents; no heuristic head/substring merging.',
            'scope':'Source guide section 1.2 explicitly allows identities revealed later in the story. Global equivalence is not proof of window-local recoverability or support.',
            'script_sha256':sha(Path(__file__))}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copyfile(__file__,out/Path(__file__).name)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
