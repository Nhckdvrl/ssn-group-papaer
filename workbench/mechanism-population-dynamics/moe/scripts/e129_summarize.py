"""Summarize the fixed E129 endpoint; paired CE comparison is POST-HOC."""
import hashlib
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text())


def main():
    output = Path('/tmp/xiang-moe-20261025/e129_teacher_KL_seed0')
    result = read(output / 'training_summary.json')
    reference = read(WB / 'results/e127/M-cover.json')
    provenance = read(output / 'provenance.json')
    ce_provenance = read('/home/xiang/mechpop_cache/e125_M-cover_128m/provenance.json')
    assert result['status'] == 'complete' and result['step'] == 15625
    assert result['teacher_unchanged'] and result['teacher_gradients_absent']
    assert reference['step'] == 15625
    for key in ('initial_tensor_sha256', 'frozen_sample_hash', 'held_window_hash'):
        assert provenance[key] == ce_provenance[key], key
    assert result['coverage']['drawn_windows'] == 250000
    final = result['evaluations'][-1]
    assert final['step'] == 15625
    key = lambda row: (row['source'], row['file_id'], row['window'], row['tokens'])
    ce = {key(row): row for row in read(WB / 'results/e127/M-cover_sequences.json')}
    kl_rows = read(output / 'final_held_sequences.json')
    assert len(ce) == len(kl_rows) == 512 and {key(row) for row in kl_rows} == set(ce)
    groups = {}
    for row in kl_rows:
        old = ce[key(row)]
        assert abs(row['teacher_nll'] - old['teacher_nll']) < 1e-6
        values = np.array([row['kl_teacher_to_student'] - old['kl_teacher_to_student'],
                           row['student_nll'] - old['student_nll'], row['tokens']])
        groups.setdefault((row['source'], row['file_id']), np.zeros(3))[:] += values
    values = np.array(list(groups.values()))
    draws = np.random.default_rng(129).integers(0, len(values), (1000, len(values)))
    samples = values[draws].sum(1)
    ci = np.quantile(samples[:, :2] / samples[:, 2:], [.025, .05, .95, .975], axis=0)
    totals = values.sum(0)
    comparison = {name: {'mean': float(totals[i] / totals[2]),
                        'ci90': ci[[1, 2], i].tolist(), 'ci95': ci[[0, 3], i].tolist()}
                  for i, name in enumerate(('KL_change', 'GT_NLL_change'))}
    summary = {
        'experiment': 'E129', 'status': result['status'], 'step': result['step'],
        'train_tokens': 128000000, 'objective': result['objective'],
        'held': final['held'], 'POS_word_balanced': final['POS_word_balanced'],
        'engineering_nll_margin': .02,
        'recovered': final['held']['nll_gap']['ci90'][1] < .02,
        'elapsed_gpu_hours_single_gpu': result['elapsed_wall_seconds'] / 3600,
        'coverage': {k: v for k, v in result['coverage'].items() if k != 'files'},
        'teacher_unchanged': result['teacher_unchanged'],
        'teacher_gradients_absent': result['teacher_gradients_absent'],
        'input_chain_hash': result['input_chain_hash'],
        'paired_comparison_to_128m_CE': {
            'POST_HOC': True, 'direction': 'teacher-KL training minus matched GT-CE training',
            'files': len(values), 'sequences': len(kl_rows), 'bootstrap_iterations': 1000,
            **comparison,
            'scope': 'Same initialization, inputs and schedule; extra teacher forward compute. '
                     'File uncertainty only, one initialization; no seed-level inference.'},
        'decision': 'Teacher-distribution target improves fidelity but does not recover the '
                    'original predictor at the fixed 128M endpoint. Continue the registered '
                    'E128 CE endpoint; no cross-seed freedom claim or objective substitution.',
        'raw_asset_directory': str(output),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    target = WB / 'results/e129/endpoint_summary.json'
    target.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'recovered': summary['recovered'], 'paired': comparison}, indent=2))


if __name__ == '__main__':
    main()
