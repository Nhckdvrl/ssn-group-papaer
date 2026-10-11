"""Registered E54 paired effects; complete runs only, damage separate from repair."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np

from analyze_reading_map import estimate, load
from data import sha, write_jsonl


COMPARISONS = [('SOURCE_ALL', 'CAUSAL'), ('INSTRUCTION', 'CAUSAL'),
               ('AMBIGUOUS', 'CAUSAL'), ('NONAMBIGUOUS', 'CAUSAL'),
               ('AMBIGUOUS', 'NONAMBIGUOUS')]


def key(row):
    return row['item_id'], row['readout'], row['mapping']


def clustered(values):
    groups = collections.defaultdict(list)
    for (cluster, pair, question), value in values.items():
        groups[cluster].append(value)
    return {cluster: float(np.mean(group)) for cluster, group in groups.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--e59-runs', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    metadata = {r['item_id']: r for r in load(args.data)}
    sources = collections.defaultdict(set)
    for r in metadata.values():
        if r['condition'] == 'gp':
            sources[(r['source'], r['sentence_sha256'])].add(r['analysis_question_target'])
    multi_sources = {k for k, v in sources.items() if {'initial', 'final'} <= v}
    multi_pairs = {(r.get('analysis_pair_id', r['pair_id']), r['question'])
                   for r in metadata.values() if r['condition'] == 'gp'
                   and (r['source'], r['sentence_sha256']) in multi_sources}
    e59 = {}
    for directory in args.e59_runs:
        cfg = json.loads((directory/'config.json').read_text())
        assert cfg.get('predictions_sha256') == sha(directory/'predictions.jsonl')
        model = Path(cfg['model_path']).name
        assert model not in e59
        e59[model] = {key(r): r for r in load(directory/'predictions.jsonl')
                      if r['scope'] == 'G2' and r['reading'] == 'R0'}
    reports, effects, diagnostics, runs = {}, [], {}, []
    seen = set()
    for directory in args.runs:
        cfg = json.loads((directory/'config.json').read_text())
        assert cfg.get('predictions_sha256') == sha(directory/'predictions.jsonl'), 'Unfinished/modified run'
        assert cfg['data_sha256'] == sha(args.data)
        model = Path(cfg['model_path']).name
        assert model not in seen
        seen.add(model)
        rows = load(directory/'predictions.jsonl')
        assert len(rows) == cfg['tasks']
        index = {(r['operation'], *key(r)): r for r in rows}
        assert len(index) == len(rows), 'Duplicate task'
        assert collections.Counter(r['operation'] for r in rows) == cfg['operations']
        expected = {(uid, readout, mapping) for uid in metadata
                    for readout in ('letters', 'words') for mapping in (0, 1)}
        for operation in ('CAUSAL', 'SOURCE_ALL', 'INSTRUCTION'):
            assert {key(r) for r in rows if r['operation'] == operation} == expected
        assert {key(r) for r in rows if r['operation'] == 'AMBIGUOUS'} == {
            key(r) for r in rows if r['operation'] == 'NONAMBIGUOUS'}
        for r in rows:
            original = metadata[r['item_id']]
            assert r['question'] == original['question'] and r['sentence_sha256'] == original['sentence_sha256']
            assert r['literal_label'] == original['literal_label']
            if r['operation'] in ('CAUSAL', 'INSTRUCTION'):
                assert r['new_future_edges'] == 0
        baseline = [r for r in rows if r['operation'] == 'CAUSAL']
        assert {key(r) for r in baseline} == e59[model].keys()
        deltas = []
        flips = 0
        for r in baseline:
            old = e59[model][key(r)]
            assert r['prompt_sha256'] == old['prompt_sha256'], 'E59 G2/R0 input mismatch'
            assert r['candidate_gold'] == old['candidate_gold']
            deltas.extend(abs(a-b) for a,b in zip(r['candidate_logprobs'], old['candidate_logprobs']))
            flips += r['correct'] != old['correct']
        diagnostics[model] = dict(e59_baseline_max_lp_delta=max(deltas),
            e59_baseline_hard_flips=flips, instrument=json.loads((directory/'instrument.json').read_text()),
            edge_budget={operation: dict(n=len(v), minimum=min(v), maximum=max(v), mean=float(np.mean(v)))
                         for operation in ('SOURCE_ALL','AMBIGUOUS','NONAMBIGUOUS')
                         if (v := [r['new_future_edges'] for r in rows if r['operation']==operation])},
            locator_qa=len({r['item_id'] for r in rows if r['operation']=='AMBIGUOUS'}),
            literal_counts=dict(collections.Counter(r['literal_label'] for r in baseline if r['readout']=='words' and r['mapping']==0)))
        runs.append(dict(path=str(directory), config_sha256=sha(directory/'config.json'),
                         predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
        for construction in sorted({r['construction'] for r in rows} | {'pooled'}):
            for target in ('initial', 'final'):
                for readout in ('letters', 'words'):
                    for comparable in (False, True):
                        for purpose_scope in ('all', 'multiple_uses'):
                            subset = [r for r in rows if (construction=='pooled' or r['construction']==construction)
                                      and r['question_target']==target and r['readout']==readout
                                      and (not comparable or r['source_gold_matches_grounding'])
                                      and (purpose_scope=='all' or (r['pair_id'],r['question']) in multi_pairs)]
                            cells = collections.defaultdict(dict)
                            for r in subset:
                                cells[r['operation']][key(r)] = r
                            for metric in ('correct', 'p_correct'):
                                label = f'{model}/{construction}/{target}/{readout}/same_gold{comparable}/{purpose_scope}/{metric}'
                                report = dict(cells={}, contrasts={})

                                def summarize(raw, statistic):
                                    group = collections.defaultdict(list)
                                    for row, value in raw:
                                        group[(row['cluster_id'],row['pair_id'],row['question'])].append(float(value))
                                    paired = {q:float(np.mean(v)) for q,v in group.items()}
                                    values = clustered(paired)
                                    effects.extend(dict(report=label, statistic=statistic, cluster_id=k,value=v)
                                                   for k,v in values.items())
                                    result = estimate(values, seed=54)
                                    result.update(n_tasks=len(raw), n_question_pairs=len(paired))
                                    return result

                                for operation, group in cells.items():
                                    for condition in ('gp','control'):
                                        selected = [(r,r[metric]) for r in group.values() if r['condition']==condition]
                                        report['cells'][operation+'/'+condition] = summarize(selected,'cell/'+operation+'/'+condition)
                                for intervention, reference in COMPARISONS:
                                    a,b = cells.get(intervention,{}), cells.get(reference,{})
                                    common = a.keys() & b.keys()
                                    comparison = intervention+'-'+reference
                                    gains = {}
                                    transitions = {}
                                    for condition in ('gp','control'):
                                        selected = [(a[k],float(a[k][metric])-float(b[k][metric])) for k in common
                                                    if a[k]['condition']==condition]
                                        gains[condition] = summarize(selected,comparison+'/gain/'+condition)
                                        if metric=='correct':
                                            retained = [k for k in common if a[k]['condition']==condition]
                                            transitions[condition] = dict(n_tasks=len(retained),
                                                counts=dict(collections.Counter(('right' if b[k]['correct'] else 'wrong')+'->'+
                                                                                ('right' if a[k]['correct'] else 'wrong') for k in retained)),
                                                wrong_to_right=summarize([(a[k],not b[k]['correct'] and a[k]['correct']) for k in retained],comparison+'/wrong_to_right/'+condition),
                                                right_to_wrong=summarize([(a[k],b[k]['correct'] and not a[k]['correct']) for k in retained],comparison+'/right_to_wrong/'+condition))
                                    paired = collections.defaultdict(dict)
                                    for k in common:
                                        r=a[k]
                                        q=(r['cluster_id'],r['pair_id'],r['question'],r['mapping'])
                                        paired[q][r['condition']]=(r,float(a[k][metric])-float(b[k][metric]))
                                    reduction = [(g['gp'][0],g['gp'][1]-g['control'][1]) for g in paired.values()
                                                 if {'gp','control'} <= g.keys()]
                                    report['contrasts'][comparison] = dict(gains=gains,
                                        gap_reduction=summarize(reduction,comparison+'/gap_reduction'),transitions=transitions)
                                reports[label] = report
    assert seen == set(e59), 'All predetermined model families required'
    effect_path = args.out.with_suffix('.cluster-effects.jsonl')
    write_jsonl(effect_path,effects)
    result = dict(data_sha256=sha(args.data),runs=runs,diagnostics=diagnostics,reports=reports,
                  cluster_effects_path=str(effect_path),cluster_effects_sha256=sha(effect_path),
                  interpretation='Input-registered all/multiple-use coverage; mapping-level hard transitions before averaging; lexical-cluster equal weighting and paired 10k bootstrap. Mask changes are not ideal semantic repair. Grounding/weak cue/budget confounds retained. No automatic claim promotion.')
    args.out.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
