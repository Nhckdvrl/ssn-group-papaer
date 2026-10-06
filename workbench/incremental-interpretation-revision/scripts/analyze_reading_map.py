"""E52 paired cluster-bootstrap map. Missing evidence never becomes a zero result."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha, write_jsonl


def load(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def assemble(data, annotation, out):
    rows = load(data); labels = {r['item_id']: r for r in load(annotation)}
    for row in rows:
        # Keep the immutable inference input, but correct analysis metadata for the
        # two polarity-matched depth-charge pairs instead of pooling three controls.
        row['analysis_pair_id'] = row['pair_id']
        row['analysis_condition'] = row['condition']
        if row['source'] == 'amouyal' and row['construction'] == 'DEPTH':
            typ = row['source_sent_type']
            row['analysis_pair_id'] += ':inverse' if typ.startswith('inv_') else ':regular'
            row['analysis_condition'] = 'control' if typ.endswith('_baseline') else 'gp'
        annotated = labels.get(row['item_id'])
        if annotated:
            assert annotated['sentence_sha256'] == row['sentence_sha256']
            row.update({k: v for k, v in annotated.items() if k.startswith('step5_')})
    paired = collections.defaultdict(list)
    for row in rows:
        paired[(row['analysis_pair_id'], row['question'])].append(row)
    for key, group in paired.items():
        conditions = {r['analysis_condition'] for r in group}
        for row in group:
            row['genuine'] = False
            row['semantic_stratum'] = 'published_nonrevision_control' if not row['needs_revision'] else 'unresolved'
            if row.get('step5_status') not in ('agreed', 'adjudicated'): continue
            a = row['step5_annotation']
            if row['question_format'] == 'yn':
                row['semantic_stratum'] = a['label']
            else:
                row['semantic_stratum'] = 'ENTAILED_CHOICE' if a['option_labels'][row['gold']] == 'ENTAILED' else 'UNCERTAIN_CHOICE'
            others = [r for r in group if r['analysis_condition'] != row['analysis_condition']]
            if not row['needs_revision'] or row['question_target'] != 'initial' or conditions != {'gp', 'control'} or not others: continue
            candidate = [row, *others]
            if any(r.get('step5_status') not in ('agreed', 'adjudicated') for r in candidate): continue
            if any(not r.get('step5_grammar_agreed') or r['step5_annotation']['grammar'] != 'acceptable' for r in candidate): continue
            def contradicted(r):
                annotation = r['step5_annotation']
                if r['question_format'] == 'yn': return annotation['label'] == 'CONTRADICTED' and r['options'][r['gold']] == 'No'
                return annotation['option_labels'][r['gold']] == 'ENTAILED' and annotation['option_labels'][1-r['gold']] == 'CONTRADICTED'
            row['genuine'] = all(contradicted(r) for r in candidate)
    # Align a control landmark to the GP's independently labelled word, not to an invented control ambiguity.
    for group in paired.values():
        gps = [r for r in group if r['condition'] == 'gp' and r.get('step5_status') in ('agreed', 'adjudicated')]
        if not gps: continue
        gp = gps[0]; a = gp['step5_annotation']
        if not gp.get('step5_position_agreed'): continue
        index = a['disamb_word_index']; word = a['disamb_word']
        if index is None: continue
        gp.update(disamb_word_index=index, amb_span=a['amb_span'], position_origin='two-pass Step5 agreement')
        for r in group:
            if r['condition'] != 'control': continue
            positions = [i for i, token in enumerate(r['sentence'].split()) if token.strip('.,;:').lower() == word.strip('.,;:').lower()]
            if len(positions) == 1:
                r.update(disamb_word_index=positions[0], position_origin='unique control word aligned to Step5 GP landmark')
    write_jsonl(out, rows)
    summary = dict(rows=len(rows), labelled=sum(r.get('step5_status') in ('agreed', 'adjudicated') for r in rows),
        genuine_pairs=len({r['pair_id'] for r in rows if r['genuine']}),
        semantic_strata=dict(collections.Counter(r['semantic_stratum'] for r in rows)),
        position_available=sum(r['disamb_word_index'] is not None for r in rows), data_sha256=sha(data),
        annotation_sha256=sha(annotation), assembled_sha256=sha(out))
    out.with_suffix('.manifest.json').write_text(json.dumps(summary, indent=2)+'\n'); print(json.dumps(summary))


def estimate(values, seed=52):
    if not values: return dict(estimate=None, ci95=None, n_clusters=0)
    x = np.asarray([values[k] for k in sorted(values)], dtype=float)
    if len(x) == 1: return dict(estimate=float(x[0]), ci95=None, n_clusters=1)
    rng = np.random.default_rng(seed); means = []
    for _ in range(100): means.extend(x[rng.integers(0, len(x), size=(100, len(x)))].mean(1))
    return dict(estimate=float(x.mean()), ci95=list(map(float, np.quantile(means, [.025, .975]))), n_clusters=len(x))


def analyze(data, run_dirs, out):
    metadata = {r['item_id']: r for r in load(data)}; output = dict(models={}, data_sha256=sha(data), runs=[])
    per_model = collections.defaultdict(dict)
    identities = {}
    for directory in run_dirs:
        config = json.loads((directory/'config.json').read_text())
        assert config.get('predictions_sha256') == sha(directory/'predictions.jsonl'), 'Incomplete or modified run'
        predictions = load(directory/'predictions.jsonl'); model = Path(config['model_path']).name
        identity = config['model_manifest_sha256'], config['arguments']['dtype']
        assert identities.setdefault(model, identity) == identity, 'Do not merge different model bytes/precisions'
        output['runs'].append(dict(path=str(directory), config_sha256=sha(directory/'config.json')))
        for r in predictions:
            assert r['mode'] == 'sequence', 'Legacy processed scores are instrument calibration, not primary map'
            assert metadata[r['item_id']]['sentence_sha256'] == r['sentence_sha256']
            key = tuple(r[k] for k in ('item_id', 'format', 'reading', 'order', 'prompt_index', 'mapping', 'repair'))
            assert key not in per_model[model], 'Duplicate inference task; do not pick favorable runs'
            per_model[model][key] = r
    paired_metadata = collections.defaultdict(list)
    for m in metadata.values(): paired_metadata[(m.get('analysis_pair_id', m['pair_id']), m['question'])].append(m)
    for model, keyed in per_model.items():
        predictions = list(keyed.values())
        for construction in sorted({r['construction'] for r in predictions} | {'pooled'}):
            for fmt in ('A', 'B'):
                selected = [r for r in predictions if r['format'] == fmt and (construction == 'pooled' or r['construction'] == construction)]
                for stratum in ('genuine', 'NEITHER', 'initial_all', 'final', 'nonrevision'):
                    def eligible(r):
                        m = metadata[r['item_id']]
                        if stratum == 'genuine': return m['genuine']
                        if stratum == 'NEITHER': return m['question_target'] == 'initial' and m['semantic_stratum'] == 'NEITHER'
                        if stratum == 'initial_all': return m['question_target'] == 'initial'
                        if stratum == 'final': return m['question_target'] == 'final'
                        return not m['needs_revision']
                    eligible_ids = {r['item_id'] for r in selected if eligible(r)}
                    # Require both sides of the SAME question to be in the stratum.
                    # A GP NEITHER item cannot borrow a different control question.
                    pairs = {k: g for k, g in paired_metadata.items() if
                        {m.get('analysis_condition', m['condition']) for m in g if m['item_id'] in eligible_ids} == {'gp', 'control'}}
                    subset = [r for r in selected if r['item_id'] in eligible_ids and r['correct'] is not None and not r['repair'] and
                        (metadata[r['item_id']].get('analysis_pair_id', r['pair_id']), metadata[r['item_id']]['question']) in pairs]
                    for metric in ('correct', 'p_correct'):
                        # Keep question-pair identity until computing each contrast,
                        # then average questions inside the lexical cluster.
                        items = collections.defaultdict(list)
                        for r in subset:
                            if not r['matched_question_exact']: continue
                            m = metadata[r['item_id']]
                            qkey = m.get('analysis_pair_id', r['pair_id']), m['question']
                            items[(r['reading'], m.get('analysis_condition', r['condition']), r['cluster_id'], qkey, r['item_id'])].append(float(r[metric]))
                        question_cells = collections.defaultdict(lambda: collections.defaultdict(list))
                        for (reading, condition, cluster, question, item), scores in items.items():
                            question_cells[(reading, condition)][(cluster, question)].append(np.mean(scores))
                        question_cells = {k: {q: float(np.mean(scores)) for q, scores in v.items()} for k, v in question_cells.items()}
                        def cluster_mean(values):
                            groups = collections.defaultdict(list)
                            for (cluster, question), value in values.items(): groups[cluster].append(value)
                            return {k: float(np.mean(v)) for k, v in groups.items()}
                        cells = {k: cluster_mean(v) for k, v in question_cells.items()}
                        gaps = {}
                        for reading in sorted({k[0] for k in cells}):
                            gp, control = question_cells.get((reading, 'gp'), {}), question_cells.get((reading, 'control'), {})
                            common = gp.keys() & control.keys(); gaps[reading] = {k: control[k]-gp[k] for k in common}
                        key = f'{construction}/{fmt}/{stratum}/{metric}'
                        report = dict(cells={f'{k[0]}/{k[1]}': estimate(v) for k, v in cells.items()},
                                      gaps={k: estimate(cluster_mean(v)) for k, v in gaps.items()}, reductions={}, raw_gains={})
                        for reading, gap in gaps.items():
                            if reading == 'R0': continue
                            base = gaps.get('R0', {}); common = base.keys() & gap.keys()
                            report['reductions'][reading] = estimate(cluster_mean({k: base[k]-gap[k] for k in common}))
                            report['raw_gains'][reading] = {}
                            for condition in ('gp', 'control'):
                                a, b = question_cells.get(('R0', condition), {}), question_cells.get((reading, condition), {})
                                common = a.keys() & b.keys()
                                report['raw_gains'][reading][condition] = estimate(cluster_mean({k: b[k]-a[k] for k in common}))
                        report['R1_vs_controls'] = {}
                        for reading in ('R2', 'R3'):
                            a, b = gaps.get('R1', {}), gaps.get(reading, {}); common = a.keys() & b.keys()
                            report['R1_vs_controls'][reading] = estimate(cluster_mean({k: b[k]-a[k] for k in common}))
                        output['models'].setdefault(model, {})[key] = report
    output['interpretation'] = 'NEITHER/initial_all are agreement with the published No convention, not semantic accuracy. No automatic scientific account selection.'
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--annotation', type=Path); ap.add_argument('--runs', type=Path, nargs='*')
    ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    if args.annotation: assemble(args.data, args.annotation, args.out)
    else: analyze(args.data, args.runs, args.out)
