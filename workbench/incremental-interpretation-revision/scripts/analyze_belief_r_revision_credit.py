"""E104 original author conditional boundary and cached E93 LP; no new inference."""
import argparse
import json
from pathlib import Path
import re

from data import sha
from data_v2 import digest
from current_open_baseline import MODELS, tokenizer
from belief_r_credit import reconstruction
from analyze_correct_answer_carry import estimate


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def analyze(root):
    parent = root.parent/'E93'; data = parent/'data-v1.jsonl'
    rows = load(data); assert len(rows) == 1744
    assert sha(data) == '5477a87d5a03b2382cddc54058b0a9787e35bdeb17d97ecfff83241c2c7ccf41'
    runs = json.loads((parent/'runner-pids-v1.json').read_text())
    records, panels, provenance, counts = [], [], [], []
    for model in MODELS:
        tok = tokenizer(root.parent/'models'/model); index = {}
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            assert cfg['data_sha256'] == sha(data)
            provenance.append(dict(model=model, config_sha256=sha(out/'config.json'), predictions_sha256=cfg['predictions_sha256']))
            for p in load(out/'predictions.jsonl'):
                if p['operation'] != 'RECONSTRUCTION':
                    continue
                key = p['item_id'], p['candidate']; assert key not in index; index[key] = p
        assert len(index) == 1744*3
        for r in rows:
            matches = list(re.finditer(r'\bthen\b', r['new_observation'], flags=re.I))
            boundary = matches[0].start() if len(matches) == 1 else None
            scores, targets = {}, []
            for candidate in 'abc':
                task = reconstruction(r, candidate, tok); old = index[r['item_id'], candidate]
                assert task['context_sha256'] == old['context_sha256'] and task['prompt_sha256'] == old['prompt_sha256']
                lp = old['token_logprobs']; assert abs(sum(lp)-old['reward_sum']) < 1e-8
                scores[candidate] = dict(whole=sum(lp))
                if boundary is None:
                    continue
                # Prefix is exactly original reconstruction code; recover character offsets.
                # The task hash remains checked above so this is not an alternative prompt.
                prefix = ('Global Instruction: Maintain a concise faithful interpretation of observed premises.\n'
                    'Goal: '+r['goal']+'\n'
                    'Your new belief state is: <belief>'+r['options'][candidate]+'</belief>\n'
                    'Your past belief state was: <belief>'+r['initial_premises']+'</belief>\n'
                    'Your past action: <action>Read the newly provided premise.</action>\n'
                    'Your past environment feedback: <environment>\n')
                assert digest(prefix) == task['context_sha256']
                enc = tok(prefix+r['new_observation'], add_special_tokens=False, return_offsets_mapping=True)
                offsets = [(a-len(prefix), b-len(prefix)) for i in task['target_positions'] for a,b in [enc['offset_mapping'][i]]]
                assert len(offsets) == len(lp)
                targets.append(([task['ids'][i] for i in task['target_positions']], offsets))
                scores[candidate]['prefix'] = sum(v for v, (_, b) in zip(lp, offsets) if b <= boundary)
                scores[candidate]['suffix'] = sum(v for v, (_, b) in zip(lp, offsets) if b > boundary)
                assert abs(scores[candidate]['prefix']+scores[candidate]['suffix']-scores[candidate]['whole']) < 1e-8
            assert all(t == targets[0] for t in targets) if targets else True
            choose = lambda region: max('abc', key=lambda c: (scores[c][region], -ord(c)))
            whole = choose('whole'); suffix = choose('suffix') if boundary is not None else None
            w = float(whole == r['ground_truth']); lo = float(suffix == r['ground_truth']); hi = float(suffix is None or lo)
            metrics = dict(WHOLE_correct=w, SUFFIX_lower_correct=lo, SUFFIX_upper_correct=hi,
                SUFFIX_minus_WHOLE_lower_correct=lo-w, SUFFIX_minus_WHOLE_upper_correct=hi-w,
                boundary_NA=float(boundary is None))
            if r['transition'] == 'UPDATE' and boundary is not None:
                g, old = r['ground_truth'], r['initial_gold']
                for region in ['whole', 'prefix', 'suffix']:
                    metrics['Gold_minus_initial_'+region+'_margin'] = scores[g][region]-scores[old][region]
                metrics['WHOLE_negative_SUFFIX_positive'] = float(metrics['Gold_minus_initial_whole_margin'] < 0 < metrics['Gold_minus_initial_suffix_margin'])
            records.append(dict(model=model, item_id=r['item_id'], cluster_id=r['cluster_id'],
                sentence_sha256=r['sentence_sha256'], transition=r['transition'], modus=r['modus'],
                ground_truth=r['ground_truth'], initial_gold=r['initial_gold'], boundary=boundary,
                selected=dict(WHOLE=whole, SUFFIX=suffix), scores=scores, metrics=metrics))
            # All original reward sums and fixed ties reconstruct E93 raw best candidate exactly.
            assert whole == max('abc', key=lambda c: index[r['item_id'], c]['reward_sum'])
        cohort = [r for r in records if r['model'] == model]
        groups = {'ALL': cohort}
        for field in ['transition', 'ground_truth', 'modus']:
            for value in sorted({r[field] for r in cohort}):
                groups[field+':'+value] = [r for r in cohort if r[field] == value]
        for group, rs in groups.items():
            counts.append(dict(model=model, group=group, sources=len(rs), boundary_NA=sum(r['boundary'] is None for r in rs)))
            for metric in sorted({k for r in rs for k in r['metrics']}):
                used = [r for r in rs if metric in r['metrics']]
                panels.append(dict(model=model, group=group, metric=metric,
                    **estimate(used, [r['metrics'][metric] for r in used], seed=104)))
        print('E104 complete CPU family', model, flush=True)
    root.mkdir(exist_ok=True); out = root/'belief-r-revision-evidence-map-v1.json'; assert not out.exists()
    out.write_text(json.dumps(dict(models=MODELS, data_sha256=sha(data), runs=provenance,
        records=records, panels=panels, counts=counts, new_GPU_hours=0, new_API_calls=0,
        boundary='Unique author conditional then, including then; two double-then sources STRUCTURAL_NA retained in bounds.',
        limits='Author human pragmatic suppression gold, not classical entailment or world truth. Frozen options selected by cached inverse reconstruction; not actual free response capability.'), indent=2)+'\n')
    manifest = dict(map_sha256=sha(out), panels=len(panels), records=len(records), new_GPU_hours=0, new_API_calls=0)
    (root/'complete-map-v1.json').write_text(json.dumps(manifest, indent=2)+'\n'); print('E104 sealed', manifest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, required=True)
    a = p.parse_args(); analyze(a.root)
