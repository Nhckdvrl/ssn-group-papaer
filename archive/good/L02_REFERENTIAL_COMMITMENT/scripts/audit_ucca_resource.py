"""Audit a pinned external corpus for suitability, without inventing filler gold."""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, subprocess, shutil

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'Deictic','Generic','Genre-based','Type-identifiable',
              'Arbitrary/Nonspecific','Iterated/repeated/set'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='experiments/E000b_ucca_audit');args=parser.parse_args()
    source = ROOT/'data/raw/ucca_refined_2021'
    out = ROOT/args.out
    out.mkdir(exist_ok=False)
    path = source/'mrp/imp.aug.mrp'
    graphs = [json.loads(l) for l in path.read_text().splitlines()]
    assert len({d['id'] for d in graphs}) == len(graphs)
    counts = collections.Counter(); rows = []; other = collections.Counter()
    mixed_scenes = []
    for d in graphs:
        nodes = {n['id']:n for n in d['nodes']}
        assert all(e['source'] in nodes and e['target'] in nodes for e in d['edges'])
        by_parent = collections.defaultdict(list)
        outgoing = collections.defaultdict(list)
        for e in d['edges']: outgoing[e['source']].append(e)
        def anchors(n, seen=frozenset()):
            if n in seen: raise ValueError('Graph cycle')
            direct = nodes[n].get('anchors', [])
            return direct + [a for e in outgoing[n] for a in anchors(e['target'],seen|{n})]
        def surface(n):
            spans = sorted({(a['from'],a['to']) for a in anchors(n)})
            return ' '.join(d['input'][a:b] for a,b in spans)
        for n in nodes.values():
            if not dict(zip(n.get('properties',[]), n.get('values',[]))).get('implicit'): continue
            incoming = [e for e in d['edges'] if e['target']==n['id']]
            cats = sorted({e['label'] for e in incoming} & CATEGORIES)
            if not cats:
                other['|'.join(sorted({e['label'] for e in incoming}))] += 1
                continue
            assert len(cats)==1 and not n.get('anchors')
            parents = sorted({e['source'] for e in incoming})
            assert len(parents)==1
            parent = parents[0]
            predicate_nodes = sorted({e['target'] for e in outgoing[parent] if e['label'] in {'P','S'}})
            row = {'id':d['id']+':'+str(n['id']), 'document_id':d['id'].split('-')[0],
                   'passage_id':d['id'], 'text':d['input'], 'implicit_node_id':n['id'],
                   'parent_node_id':parent, 'category':cats[0],
                   'incoming_labels':sorted({e['label'] for e in incoming}),
                   'predicate_surface':[surface(x) for x in predicate_nodes],
                   'parent_surface':surface(parent),
                   'role_identity_gold':None, 'candidate_specific_support_gold':None}
            rows.append(row);counts[cats[0]]+=1;by_parent[parent].append(row)
        for parent, rs in by_parent.items():
            if len({x['category'] for x in rs})>1:
                mixed_scenes.append({'passage_id':d['id'],'parent':parent,'text':d['input'],
                                     'nodes':[x['id'] for x in rs], 'categories':[x['category'] for x in rs]})
    expected = {'Deictic':107,'Generic':86,'Genre-based':147,'Type-identifiable':6,
                'Arbitrary/Nonspecific':36,'Iterated/repeated/set':9}
    assert dict(counts)==expected,counts
    assert len(rows)==391
    (out/'observations.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (out/'mixed_scenes.json').write_text(json.dumps(mixed_scenes,indent=2)+'\n')
    report = {'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'repository':'https://github.com/ruixiangcui/UCCA-Refined-Implicit-EWT_English',
              'commit':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),
              'graphs':len(graphs),'documents':len({d['id'].split('-')[0] for d in graphs}),
              'typed_implicit_participants':len(rows),'category_counts':dict(sorted(counts.items())),
              'other_implicit_nodes_by_incoming_labels':dict(other),
              'mixed_type_parent_scenes':len(mixed_scenes),
              'paper_table_2_reproduced':True,
              'source_files':{str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file() and '.git' not in p.parts},
              'admission':'Native interpretation/scene inventory only. A participant edge A is not a frame-specific role identity. No candidate-specific negative or positive support labels are inferred.',
              'script_sha256':sha(Path(__file__))}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copyfile(__file__,out/Path(__file__).name)
    print(json.dumps({k:v for k,v in report.items() if k!='source_files'},indent=2))

if __name__=='__main__': main()
