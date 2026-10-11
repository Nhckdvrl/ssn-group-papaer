"""Execute an immutable, offline, descriptive corpus audit."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import platform
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from corpus import Corpus, AUXILIARY


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prior_diagnostic(rows, n_sentences):
    predictions = []
    for fold in range(5):
        train = [r for r in rows if min(4, r['sentence_index'] * 5 // n_sentences) != fold
                 and 'Uncertain_Interpretation' not in r['flags']]
        test = [r for r in rows if min(4, r['sentence_index'] * 5 // n_sentences) == fold
                and 'Uncertain_Interpretation' not in r['flags']]
        counts = defaultdict(Counter)
        global_counts = Counter(r['interpretation'] for r in train)
        for r in train:
            counts[(r['frame'], r['role'])][r['interpretation']] += 1
        def majority(c):
            return sorted(('DNI', 'INI'), key=lambda x: (-c[x], x))[0]
        for r in test:
            c = counts[(r['frame'], r['role'])]
            predictions.append({'id': r['id'], 'fold': fold, 'gold': r['interpretation'],
                                'prediction': majority(c or global_counts),
                                'global_prediction': majority(global_counts), 'seen_pair': bool(c)})
    total = len(predictions)
    return {'n': total, 'frame_role_correct': sum(p['gold'] == p['prediction'] for p in predictions),
            'global_correct': sum(p['gold'] == p['global_prediction'] for p in predictions),
            'seen_pair_n': sum(p['seen_pair'] for p in predictions),
            'predictions': predictions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    if not args.run_id.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Run ID must be a simple directory name')
    protocol_path = ROOT / 'experiments/E000_data_audit/protocol.json'
    protocol = json.loads(protocol_path.read_text())
    source = ROOT / protocol['source']
    if sha(source) != protocol['source_sha256']:
        raise ValueError('Source checksum mismatch')
    out = ROOT / 'runs' / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    for name, path in [('protocol.json', protocol_path), ('run_data_audit.py', Path(__file__)),
                       ('corpus.py', ROOT / 'src/corpus.py')]:
        shutil.copyfile(path, out / name)
    corpus = Corpus(source)
    rows, issues, frames = corpus.inventory()
    graph_issues = corpus.graph_audit()
    counterpart = Corpus(ROOT / protocol['companion'])
    other, _, _ = counterpart.inventory()
    comparable = lambda rs: [(r['id'], r['frame'], r['role'], r['flags'], r['target_node_ids'],
                              r['source_link_node_ids']) for r in rs]
    all_fes = [fe for s in corpus.sentences for f in s.findall('./sem/frames/frame')
               if f.attrib['name'] not in AUXILIARY for fe in f.findall('fe')]
    matrix = Counter((r['interpretation'], r['source_link_present']) for r in rows)
    terminal_count = sum(n.tag == 't' for n in corpus.nodes.values())
    part_count = sum(n.tag == 'part' for n in corpus.nodes.values())
    counts = {'sentences': len(corpus.sentences), 'terminal_tokens': terminal_count,
              'splitword_parts': part_count, 'terminal_plus_part_nodes': terminal_count + part_count,
              'frames': sum(frames.values()), 'frame_types': len(frames),
              'DNI': sum(r['interpretation'] == 'DNI' for r in rows),
              'INI': sum(r['interpretation'] == 'INI' for r in rows),
              'DNI_linked': matrix['DNI', True], 'DNI_unlinked': matrix['DNI', False],
              'INI_linked': matrix['INI', True], 'INI_unlinked': matrix['INI', False],
              'non_NI_fe_elements': len(all_fes) - len(rows),
              'non_NI_fe_with_fenode': sum(bool(fe.findall('fenode')) for fe in all_fes
                                         if fe.attrib['id'] not in {r['id'] for r in rows})}
    flag_counts = Counter(f for r in rows for f in r['flags'])
    groups = defaultdict(Counter)
    for row in rows:
        groups[(row['frame'], row['role'])][row['interpretation']] += 1
    mixed = {k: v for k, v in groups.items() if len(v) > 1}
    summary = {'experiment': 'E000', 'counts': counts,
               'published_count_comparison': {k: {'published': v, 'observed': counts.get(k),
                                                 'matches': counts.get(k) == v}
                                              for k, v in protocol['published_training_counts'].items()},
               'count_caveats': ['Published tokens equal terminals + splitword parts; this counts overlapping representations, not unique surface tokens.',
                                 'Published overt FE count not reproduced by naive non-NI span-bearing FE element count. No forced reconciliation.'],
               'companion_annotation_agrees': comparable(rows) == comparable(other),
               'ni_issues': issues, 'graph_issues': graph_issues, 'ni_flags': dict(flag_counts),
               'frame_role_pairs': len(groups), 'mixed_interpretation_pairs': len(mixed),
               'rows_in_mixed_pairs': sum(sum(v.values()) for v in mixed.values()),
               'model_gate': 'MEASUREMENT_REVISION_REQUIRED',
               'reason': 'INI flags do not justify treating all specific fillers as errors; 11 source-linked INIs require interpretation/link separation.',
               'research_status': 'ACTIVE; not killed; no model finding'}
    prior = prior_diagnostic(rows, len(corpus.sentences))
    summary['prior_diagnostic'] = {k: v for k, v in prior.items() if k != 'predictions'}
    write_json(out / 'report.json', summary)
    write_json(out / 'prior_diagnostic.json', prior)
    write_json(out / 'frame_role_counts.json', [{'frame': k[0], 'role': k[1], **v} for k, v in sorted(groups.items())])
    for name, records in [('observations.jsonl', rows), ('documents.jsonl', [corpus.documents()]),
                          ('review_queue.jsonl', [r for r in rows if r['audit_flags'] or r['integrity'] != 'OK'])]:
        (out / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    manifest = {'python': sys.version, 'platform': platform.platform(), 'source': protocol['source'],
                'source_sha256': sha(source), 'companion_sha256': sha(ROOT / protocol['companion']),
                'artifacts': {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    write_json(out / 'manifest.json', manifest)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
