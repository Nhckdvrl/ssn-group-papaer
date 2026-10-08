"""E106 one fixed automatic credit rule; E103 frozen full-cohort blind role labels."""
import argparse
import json
from pathlib import Path
import time

from data import sha
from current_open_baseline import MODELS, tokenizer
from reconstruction_reward import prepare, context
from analyze_correct_answer_carry import estimate


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def analyze(root, parent_map, models=None, output_name='positive-innovation-credit-map-v1.json'):
    parent = root.parent/'E103'; old = json.loads(parent_map.read_text())
    models = MODELS if models is None else models
    assert models and set(models) <= set(MODELS) and old['models'] == models
    rows = {r['item_id']:r for r in load(root/'data-v1.jsonl')}
    pools = {}
    for run in json.loads((parent/'runner-pids-v1.json').read_text()):
        out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        for p in load(out/'predictions.jsonl'):
            key = run['model'], p['item_id'], p['candidate']; assert key not in pools; pools[key] = p
    baselines, provenance = {}, []
    for run in json.loads((root/'runner-pids-v1.json').read_text()):
        if run['model'] not in models:continue
        model = run['model']; tok = tokenizer(root.parent/'models'/model)
        out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl') and cfg['data_sha256'] == sha(root/'data-v1.jsonl')
        assert cfg['tasks'] == 50
        provenance.append(dict(model=model, config_sha256=sha(out/'config.json'),
            predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
        for z in load(out/'predictions.jsonl'):
            uid = z['item_id']; r = rows[uid]; task = prepare(r,tok)
            assert z['context_sha256'] == task['context_sha256'] and z['prompt_sha256'] == task['prompt_sha256']
            prefix = context(r); e = tok(prefix+r['sentence'], add_special_tokens=False, return_offsets_mapping=True)
            offsets = [(a-len(prefix),b-len(prefix)) for i in task['target_positions'] for a,b in [e['offset_mapping'][i]]]
            ids = [task['ids'][i] for i in task['target_positions']]
            assert len(ids) == len(z['token_logprobs'])
            for j in range(8):
                p = pools[model,uid,j]
                assert ids == p['scores']['target_ids']
                assert offsets == [tuple(v) for v in p['scores']['target_offsets']]
            baselines[model,uid] = z
    assert len(baselines) == 50*len(models)
    records, panels = [], []
    for r in old['records']:
        model,uid = r['model'],r['item_id']; baseline = baselines[model,uid]['token_logprobs']
        scores = {}
        for j in range(8):
            p = pools[model,uid,j]; assert len(p['token_logprobs']) == len(baseline)
            gain = [a-b for a,b in zip(p['token_logprobs'],baseline)]
            positive, negative = sum(max(0,v) for v in gain),sum(min(0,v) for v in gain)
            whole_gain = p['scores']['whole']-sum(baseline)
            assert abs(positive+negative-whole_gain) < 1e-8
            scores[j] = dict(positive=positive,negative=negative,whole_gain=whole_gain)
        selected = max(range(8),key=lambda j:(scores[j]['positive'],-j))
        assert max(range(8),key=lambda j:(scores[j]['whole_gain'],-j)) == r['selected']['WHOLE']
        candidates = {int(k):v for k,v in r['candidate_metrics'].items()}
        values = {'POSITIVE_INNOVATION':candidates[selected], 'GREEDY':candidates[0]}
        for policy in ['WHOLE','REVISION_EVIDENCE']:
            values[policy] = candidates[r['selected'][policy]]
        values['UNIFORM_POOL'] = {k:r['metrics']['UNIFORM_POOL/'+k] for k in candidates[0]}
        metrics = {'POSITIVE_INNOVATION/'+k:v for k,v in values['POSITIVE_INNOVATION'].items()}
        for before in ['WHOLE','GREEDY','UNIFORM_POOL','REVISION_EVIDENCE']:
            for k in candidates[0]:
                other = k[:-6]+'_upper' if k.endswith('_lower') else k[:-6]+'_lower' if k.endswith('_upper') else k
                metrics['POSITIVE_INNOVATION-minus-'+before+'/'+k] = values['POSITIVE_INNOVATION'][k]-values[before][other]
        metrics['selection_changed_from_WHOLE'] = float(selected != r['selected']['WHOLE'])
        records.append(dict(model=model,item_id=uid,cluster_id=r['cluster_id'],
            sentence_sha256=r['sentence_sha256'],construction=r['construction'],
            selected=selected,candidate_gain_scores=scores,metrics=metrics))
    for model in models:
        for ct in ['ALL','MVRR','NPZ','NPS']:
            rs = [r for r in records if r['model'] == model and (ct == 'ALL' or r['construction'] == ct)]
            for metric in sorted(rs[0]['metrics']):
                panels.append(dict(model=model,construction=ct,metric=metric,
                    **estimate(rs,[r['metrics'][metric] for r in rs],seed=106)))
    annotation = parent/'step5/annotated.jsonl'
    if not annotation.exists():
        assert len(models) == 1
        annotation = parent/'phase-audits-v1'/models[0]/'step5/annotated.jsonl'
        assert annotation.with_name('summary.json').exists()
    path = root/output_name; assert not path.exists()
    path.write_text(json.dumps(dict(models=models,data_sha256=sha(root/'data-v1.jsonl'),
        E103_map_sha256=sha(parent_map),E103_annotation_sha256=sha(annotation),
        runs=provenance,records=records,panels=panels,new_API_calls=0,new_P=0,
        rule='Sum positive token log-likelihood gain relative to fixed No prior information belief; zero cutoff, all tokens, no T2.',
        limits='Single fixed rule, current untrained reconstruction analogue, exact same original candidate pool; no RL training or automatic semantic faithfulness guarantee.'),indent=2)+'\n')
    manifest = dict(map_sha256=sha(path),panels=len(panels),gpu_hours=sum(r['gpu_hours'] for r in provenance),new_API_calls=0,new_P=0)
    (root/(output_name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n');print('E106 sealed',manifest,flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--wait',action='store_true')
    a = p.parse_args(); parent_map = a.root.parent/'E103/native-pool-revision-credit-map-v1.json'
    while a.wait:
        runs = json.loads((a.root/'runner-pids-v1.json').read_text())
        ready = parent_map.with_name(parent_map.name+'.manifest.json').exists() and all(
            (Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs)
        if ready:break
        time.sleep(20)
    analyze(a.root,parent_map)
