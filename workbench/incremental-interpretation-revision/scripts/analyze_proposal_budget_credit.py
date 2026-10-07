"""E105 fixed proposal prefixes before labels; immutable E103 inputs and teacher."""
import argparse
import collections
import json
from pathlib import Path
import time

from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def analyze(root, parent_map):
    parent = root.parent/'E103'; old = json.loads(parent_map.read_text())
    assert old['models'] == MODELS
    pools = collections.defaultdict(dict)
    for run in json.loads((parent/'runner-pids-v1.json').read_text()):
        out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        for p in map(json.loads, (out/'predictions.jsonl').read_text().splitlines()):
            key = run['model'], p['item_id']
            assert p['candidate'] not in pools[key]
            pools[key][p['candidate']] = p
    records, panels = [], []
    for r in old['records']:
        pool = pools[r['model'], r['item_id']]; assert set(pool) == set(range(8))
        candidate_metrics = {int(k):v for k,v in r['candidate_metrics'].items()}
        values, choices = {}, {}
        for budget in [1, 2, 4, 8]:
            choices[budget] = {policy:max(range(budget), key=lambda j: (pool[j]['scores'][score], -j))
                for policy, score in [('WHOLE', 'whole'), ('REVISION_EVIDENCE', 'suffix')]}
            values[budget] = {policy:dict(candidate_metrics[j]) for policy,j in choices[budget].items()}
            values[budget]['UNIFORM_POOL'] = {k:sum(candidate_metrics[j][k] for j in range(budget))/budget for k in candidate_metrics[0]}
            for policy, score in [('WHOLE', 'whole'), ('REVISION_EVIDENCE', 'suffix')]:
                values[budget][policy]['maximum_reward'] = pool[choices[budget][policy]]['scores'][score]
            values[budget]['POOL_ORACLE'] = {k:max(candidate_metrics[j][k] for j in range(budget))
                for k in ['CORRECT_ROLES_lower', 'CORRECT_ROLES_upper']}
        for policy in ['WHOLE', 'REVISION_EVIDENCE']:
            assert choices[8][policy] == r['selected'][policy]
            for budget in [2, 4, 8]:
                assert values[budget][policy]['maximum_reward'] >= values[budget//2][policy]['maximum_reward']
        assert choices[1] == dict(WHOLE=0, REVISION_EVIDENCE=0)
        for metric in candidate_metrics[0]:
            assert values[8]['UNIFORM_POOL'][metric] == r['metrics']['UNIFORM_POOL/'+metric]
        metrics = {f'k{budget}/{policy}/{k}':v for budget, policies in values.items() for policy,vs in policies.items() for k,v in vs.items()}
        for after, before in [(2,1), (4,1), (8,1), (4,2), (8,4)]:
            for policy in ['WHOLE', 'REVISION_EVIDENCE', 'UNIFORM_POOL', 'POOL_ORACLE']:
                for k in values[after][policy]:
                    opposite = k[:-6]+'_upper' if k.endswith('_lower') else k[:-6]+'_lower' if k.endswith('_upper') else k
                    metrics[f'k{after}-minus-k{before}/{policy}/{k}'] = values[after][policy][k]-values[before][policy][opposite]
        records.append(dict(model=r['model'], item_id=r['item_id'], cluster_id=r['cluster_id'],
            sentence_sha256=r['sentence_sha256'], construction=r['construction'], selected=choices, metrics=metrics))
    assert len(records) == 150
    for model in MODELS:
        for ct in ['ALL', 'MVRR', 'NPZ', 'NPS']:
            rs = [r for r in records if r['model'] == model and (ct == 'ALL' or r['construction'] == ct)]
            for metric in sorted(rs[0]['metrics']):
                panels.append(dict(model=model, construction=ct, metric=metric,
                    **estimate(rs, [r['metrics'][metric] for r in rs], seed=105)))
    root.mkdir(exist_ok=True); out = root/'proposal-budget-credit-map-v1.json'; assert not out.exists()
    out.write_text(json.dumps(dict(models=MODELS, E103_map_sha256=sha(parent_map),
        E103_annotation_sha256=sha(parent/'step5/annotated.jsonl'), records=records, panels=panels,
        new_GPU_hours=0, new_API_calls=0,
        scope='Fixed candidate prefixes j0 to k-1, budgets1/2/4/8; j0 reused greedy, remaining seven sampled seeds not rerun.',
        limits='One fixed proposal ordering; not an iid pass@k law. Original T2 suffix is an oracle. All unknown/caps retained in lower/upper differences.'), indent=2)+'\n')
    manifest = dict(map_sha256=sha(out), panels=len(panels), new_GPU_hours=0, new_API_calls=0)
    (root/'complete-map-v1.json').write_text(json.dumps(manifest, indent=2)+'\n'); print('E105 sealed', manifest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, required=True); p.add_argument('--wait', action='store_true')
    a = p.parse_args(); parent_map = a.root.parent/'E103/native-pool-revision-credit-map-v1.json'
    while a.wait and not parent_map.with_name(parent_map.name+'.manifest.json').exists():
        time.sleep(20)
    analyze(a.root, parent_map)
