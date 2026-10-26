"""POST-HOC E134 shared-Hcal output variation; no matching or GPU evaluation."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b''):
            value.update(chunk)
    return value.hexdigest()


def run():
    source = WB / 'results/e134/necessity.json'
    summary = json.loads(source.read_text())
    names = [f'seed{i}_order0' if i else 'seed0_anchor' for i in range(5)]
    arrays, proofs, identity = {}, {}, None
    for name in names:
        setting = summary['settings'][name]
        assert setting['status'] == 'complete'
        calibration = setting['calibration']
        hcal = calibration['Hcal']
        key = tuple(hcal[k] for k in ['Hcal_sha256', 'window_hash', 'data_identity_sha256', 'prefix_hash'])
        if identity is None:
            identity = key
        assert key == identity, 'Cross-model hidden inputs differ'
        path = Path(calibration['vectors'])
        assert sha(path) == calibration['vectors_sha256']
        with np.load(path, allow_pickle=False) as data:
            arrays[name] = {k: np.asarray(data[k]).reshape(8192, 2048) for k in ['y', 'c', 'r']}
        proofs[name] = {'vectors': str(path), 'sha256': calibration['vectors_sha256'], 'Hcal': hcal}
    pairs = []
    for left, right in itertools.combinations(names, 2):
        totals = np.zeros(5, np.float64)
        max_error = 0.
        for start in range(0, 8192, 256):
            diffs = {k: arrays[left][k][start:start+256].astype(np.float64) - arrays[right][k][start:start+256].astype(np.float64) for k in ['y', 'c', 'r']}
            dy, dc, dr = (diffs[k] for k in ['y', 'c', 'r'])
            totals += [np.square(dy).sum(), np.square(dc).sum(), np.square(dr).sum(), 2 * (dc * dr).sum(), dy.size]
            max_error = max(max_error, float(np.abs(dy - dc - dr).max()))
        y, c, r, cross = totals[:4] / totals[4]
        pairs.append({'left': left, 'right': right, 'mean_square_per_coordinate': {'native_difference': float(y), 'uniform_difference': float(c), 'deviation_difference': float(r), 'cross_term': float(cross)},
                      'rms_per_coordinate': {'native_difference': float(np.sqrt(y)), 'uniform_difference': float(np.sqrt(c)), 'deviation_difference': float(np.sqrt(r))},
                      'algebra_mean_square_residual': float(y-c-r-cross), 'delta_y_minus_delta_c_minus_delta_r_max_abs': max_error})
    result = {'experiment': 'E134', 'post_hoc': True, 'source_summary_sha256': sha(source), 'script_sha256': sha(__file__),
              'scope': 'Five controlled banks on the identical 8192 training-only Hcal vectors. Ten shared-model pairs are descriptive, not ten independent samples. No held-language or knowledge-fraction claim.',
              'proofs': proofs, 'pairs': pairs}
    output = WB / 'results/e134/component_variation.json'
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'output': str(output), 'pairs': pairs}, indent=2))


if __name__ == '__main__':
    run()
