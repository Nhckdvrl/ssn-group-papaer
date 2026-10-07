"""E100 actual comparison versus E96 raw credit, fixed same native P and semantics."""
import argparse
import collections
import json
from pathlib import Path
import time

from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def analyze(root, semantic_map=None, selected_models=None, output_name='native-meaning-comparison-map-v1.json'):
    models = MODELS if selected_models is None else selected_models
    semantic_map = root.parent/'E96/modern-native-belief-credit-map-v1.json' if semantic_map is None else semantic_map
    semantic = json.loads(semantic_map.read_text())
    assert semantic['data_sha256'] == sha(root.parent/'E96/data-v1.jsonl')
    reference = {(r['model'], r['item_id'], r['condition']):r for r in semantic['records']}
    index, inputs, provenance = {}, {}, []
    for run in json.loads((root/'runner-pids-v1.json').read_text()):
        if run['model'] not in models:
            continue
        out = Path(run['out'])
        cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        assert cfg['input_sha256'] == sha(out/'input-v1.jsonl')
        assert cfg['data_sha256'] == semantic['data_sha256']
        ps = load(out/'predictions.jsonl')
        assert len(ps) == cfg['tasks'] == 4*cfg['rows']
        provenance.append(dict(model=run['model'], shard=run['shard'], gpu_hours=cfg['gpu_hours'],
            config_sha256=sha(out/'config.json'), predictions_sha256=cfg['predictions_sha256']))
        for r in load(out/'input-v1.jsonl'):
            assert (run['model'], r['item_id']) not in inputs
            inputs[run['model'], r['item_id']] = r
        for p in ps:
            key = run['model'], p['item_id'], p['mode'], p['order_index']
            assert key not in index
            index[key] = p
    assert len(inputs) == 100*len(models) and len(index) == 400*len(models)
    panels, records, counts = [], [], []
    for model in models:
        rows = [r for (m,uid),r in inputs.items() if m == model]
        values = {}
        for r in rows:
            ref = reference[model, r['pair_id'], r['condition']]
            assert ref['sentence_sha256'] == r['sentence_sha256']
            for side, field in [('gp', 'BASE_BANK'), ('control', 'TARGET_BANK')]:
                native = next(q for q in semantic['native_quality_records'] if q['model']==model and q['item_id']==r['pair_id'] and q['condition']==side)
                assert native['atom_labels'] == ref['semantics'][side]['atom_labels']
            for mode in ['NATIVE', 'RECOVERY']:
                for order in [0,1]:
                    p = index[model, r['item_id'], mode, order]
                    known = p['stopped'] and p['valid'] and p['answer'] is not None
                    actual = None
                    if known:
                        actual = 0 if p['answer']=='c' else (1 if p['candidate_order']['ab'.index(p['answer'])]=='TARGET_BANK' else -1)
                    v = dict(actual_unknown=float(not known), actual_capped=float(p['capped']), actual_tie=float(known and actual==0))
                    choices = [actual] if known else [-1,0,1]
                    for criterion in ['fidelity', 'pattern']:
                        if criterion not in ref['metrics']:
                            continue
                        gold = ref['metrics'][criterion]['possible_ranks']
                        raw = ref['reward_rank']
                        v[criterion+'_alignment_lower'] = min(a*g for a in choices for g in gold)
                        v[criterion+'_alignment_upper'] = max(a*g for a in choices for g in gold)
                        v[criterion+'_correct_lower'] = float(all(a==g for a in choices for g in gold))
                        v[criterion+'_correct_upper'] = float(any(a==g for a in choices for g in gold))
                        v[criterion+'_actual_minus_raw_alignment_lower'] = min((a-raw)*g for a in choices for g in gold)
                        v[criterion+'_actual_minus_raw_alignment_upper'] = max((a-raw)*g for a in choices for g in gold)
                        v[criterion+'_actual_minus_raw_correct_lower'] = min(float(a==g)-float(raw==g) for a in choices for g in gold)
                        v[criterion+'_actual_minus_raw_correct_upper'] = max(float(a==g)-float(raw==g) for a in choices for g in gold)
                    values[r['item_id'], mode, order] = v
                    records.append(dict(model=model,item_id=r['item_id'],pair_id=r['pair_id'],condition=r['condition'],
                        construction=r['construction'],mode=mode,order=order,actual_rank=actual,raw_rank=ref['reward_rank'],
                        semantic_ranks={k:z['rank'] for k,z in ref['metrics'].items()},metrics=v))
        for ct in ['ALL', 'MVRR', 'NPZ', 'NPS']:
            for condition in ['gp','control']:
                base = [r for r in rows if r['condition']==condition and (ct=='ALL' or r['construction']==ct)]
                for criterion in ['fidelity','pattern']:
                    eligible = [r for r in base if criterion in reference[model,r['pair_id'],condition]['metrics']]
                    counts.append(dict(model=model,construction=ct,condition=condition,criterion=criterion,
                        sources=len(base),eligible=len(eligible),structural_NA=len(base)-len(eligible)))
                    for subset in ['ALL','CHANGED_DIAGNOSTIC','TIE_DIAGNOSTIC']:
                        sub = [r for r in eligible if subset=='ALL' or
                            (reference[model,r['pair_id'],condition]['metrics'][criterion]['rank'] in [-1,1] if subset=='CHANGED_DIAGNOSTIC' else
                             reference[model,r['pair_id'],condition]['metrics'][criterion]['rank']==0)]
                        metrics = ['actual_unknown','actual_capped','actual_tie'] + [criterion+'_'+k for k in
                            ['alignment_lower','alignment_upper','correct_lower','correct_upper',
                             'actual_minus_raw_alignment_lower','actual_minus_raw_alignment_upper',
                             'actual_minus_raw_correct_lower','actual_minus_raw_correct_upper']]
                        for mode in ['NATIVE','RECOVERY','RECOVERY-minus-NATIVE']:
                            for metric in metrics:
                                xs, expanded = [], []
                                for r in sub:
                                    for order in [0,1]:
                                        if mode=='RECOVERY-minus-NATIVE':
                                            opposite = metric[:-6]+'_upper' if metric.endswith('_lower') else metric[:-6]+'_lower' if metric.endswith('_upper') else metric
                                            x = values[r['item_id'],'RECOVERY',order][metric]-values[r['item_id'],'NATIVE',order][opposite]
                                        else:
                                            x = values[r['item_id'],mode,order][metric]
                                        expanded.append(r)
                                        xs.append(x)
                                panels.append(dict(model=model,construction=ct,condition=condition,criterion=criterion,
                                    subset=subset,mode=mode,metric=metric,**estimate(expanded,xs,seed=100)))
            for criterion in ['fidelity','pattern']:
                paired = collections.defaultdict(dict)
                for r in rows:
                    if (ct=='ALL' or r['construction']==ct) and criterion in reference[model,r['pair_id'],r['condition']]['metrics']:
                        paired[r['pair_id']][r['condition']] = r
                for mode in ['NATIVE','RECOVERY']:
                    for metric in [criterion+'_alignment_lower',criterion+'_alignment_upper',criterion+'_correct_lower',criterion+'_correct_upper']:
                        opposite = metric[:-6]+'_upper' if metric.endswith('_lower') else metric[:-6]+'_lower'
                        expanded,xs=[],[]
                        for pair in paired.values():
                            assert set(pair)=={'gp','control'}
                            g,c=pair['gp'],pair['control']
                            for order in [0,1]:
                                expanded.append(g)
                                xs.append(values[c['item_id'],mode,order][metric]-values[g['item_id'],mode,order][opposite])
                        panels.append(dict(model=model,construction=ct,condition='CUE-source-minus-GP-source',criterion=criterion,
                            subset='ALL',mode=mode,metric=metric,**estimate(expanded,xs,seed=100)))
    out = root/output_name
    assert not out.exists()
    out.write_text(json.dumps(dict(semantic_map_sha256=sha(semantic_map),models=models,runs=provenance,
        records=records,panels=panels,counts=counts,
        scope='Full three-family panel' if selected_models is None else 'INTERIM complete-family hypothesis generation, full panel continues.',
        statistics='Two candidate orders averaged within Source then original pair cluster; paired10000bootstrap seed100, all unknown bounds and structuralNA.',
        limits='Same native writer/grader comparison; registered common-Q semantics only; not full equivalence or trained self-supervision failure.'),indent=2)+'\n')
    manifest=dict(map_sha256=sha(out),actual_outputs=400*len(models),new_API_calls=0,new_LP_calls=0,
                  gpu_hours=sum(r['gpu_hours'] for r in provenance),panels=len(panels))
    (root/(output_name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    print('E100 sealed',manifest,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--wait',action='store_true')
    a=p.parse_args()
    while a.wait:
        runs=json.loads((a.root/'runner-pids-v1.json').read_text())
        ready=all((Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs)
        if ready and (a.root.parent/'E96/complete-map-v1.json').exists():break
        time.sleep(20)
    analyze(a.root)
