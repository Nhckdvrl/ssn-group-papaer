"""Registered E131 functional trajectory comparisons, with fixed-cal word intervals."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import e124_compare as metric
import e130_word_uncertainty as uncertainty

WB = Path(__file__).resolve().parents[1]
TMP = Path('/tmp/xiang-moe-20261025')
FROZEN = {
    'e124_compare.py': '1cd3df24aea09e1fb2db86d9e4db52fe53ca42d7564141a0987ff6ccd7313671',
    'e130_word_uncertainty.py': '56f97a8881b1b97771e00941894eb980b996f38a0a34f250b9c403f468507658',
}


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b''): value.update(chunk)
    return value.hexdigest()


def captures():
    values = {'parent': (TMP/'e131_parent_function.npz', 4096)}
    for branch in ('ordered', 'permuted'):
        folder = TMP/('e131_' + branch)
        for phase, filename, step in (
            ('pulse', 'pulse_function.npz', 5120),
            ('common24576', 'diagnostic_common24576.npz', 24576),
            ('late', 'functional_late.npz', 61440),
            ('final', 'functional_final.npz', 62500)):
            values[branch+'_'+phase] = folder/filename, step
    return values


def pairs():
    result = [('parent_vs_'+b+'_pulse', 'parent', b+'_pulse', 'parent_pulse') for b in ('ordered', 'permuted')]
    result += [('ordered_vs_permuted_'+p, 'ordered_'+p, 'permuted_'+p,
                'diagnostic_cross_mid' if p == 'common24576' else 'primary_cross_branch')
               for p in ('pulse', 'common24576', 'final')]
    for branch in ('ordered', 'permuted'):
        result += [(branch+'_pulse_vs_common24576', branch+'_pulse', branch+'_common24576', 'diagnostic_pulse_mid'),
                   ('parent_vs_'+branch+'_final', 'parent', branch+'_final', 'parent_final'),
                   (branch+'_pulse_vs_final', branch+'_pulse', branch+'_final', 'primary_history'),
                   (branch+'_common24576_vs_final', branch+'_common24576', branch+'_final', 'diagnostic_mid_final'),
                   (branch+'_late_vs_final', branch+'_late', branch+'_final', 'late_reference')]
    return result


def run(args):
    for name, expected in FROZEN.items():
        if sha(WB/'scripts'/name) != expected: raise ValueError('Frozen comparison helper differs: '+name)
    locations, loaded, report = captures(), {}, {}
    def load(name):
        if name not in loaded:
            path, step = locations[name]
            data = metric.load_capture(path); header = data['metadata']
            if (header.get('step'), header.get('layer'), header.get('experts'), header.get('top_k')) != (step, 9, 64, 8):
                raise ValueError('Wrong registered capture stage: '+name)
            if header.get('script_sha256') != '4b4f861990e3e17dd6dd3fb98bb4aa69b6ee488d63d75b871276ef257d68dbae':
                raise ValueError('Functional capture source differs')
            if header.get('backbone_sample_hash') != '565b9dacb123aab3e1f296bcc1bad8928fa7811492b80aface1809530a0b6c03':
                raise ValueError('E131 shared frozen backbone differs')
            loaded[name] = data, {'path': str(path), 'sha256': sha(path), 'step': step, 'metadata': header}
        return loaded[name]
    folder = WB/'results/e131/comparison/batch'; folder.mkdir(parents=True, exist_ok=True)
    for key, left, right, kind in pairs():
        if not all(locations[name][0].is_file() for name in (left, right)):
            report[key] = {'status': 'missing', 'kind': kind}; continue
        a, pa = load(left); b, pb = load(right)
        value = metric.compare(a, b, permutations=199, random_maps=199, seed=124, min_std=1e-8)
        mapping = value['mapping_A_to_B']; ia = np.array([i for i,j in enumerate(mapping) if j is not None], dtype=int)
        ib = np.array([mapping[i] for i in ia], dtype=int)
        cal, held, words = a['split']=='cal', a['split']=='held', a['word']
        intervals = {}
        for role in ('U', 'A'):
            x, hx, _ = metric.residualize(a[role], words, cal, held)
            y, hy, _ = metric.residualize(b[role], words, cal, held)
            use = hx & hy
            intervals[role] = uncertainty.interval(x[use][:, ia], y[use][:, ib], words[use])
        value.update(experiment='E131', pair_id=key, kind=kind, captures={'A': pa, 'B': pb},
                     word_intervals=intervals, frozen_sources=FROZEN, analysis_sha256=sha(__file__))
        output = folder/(key+'.json'); output.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        report[key] = {'status': 'complete', 'kind': kind, 'path': str(output), 'sha256': sha(output),
                       'U': value['function']['U']['held_conditional_columns'],
                       'A': value['function']['A']['held_conditional_columns'], 'word_intervals': intervals}
    completed = sum(value['status']=='complete' for value in report.values())
    result = {'experiment': 'E131', 'status': 'complete' if completed==15 else 'partial',
              'completed_pairs': completed, 'expected_pairs': 15, 'pairs': report, 'analysis_sha256': sha(__file__),
              'scope': 'One parent/pulse. Fixed-cal held-word uncertainty only, not a seed CI; no scientific score gate. Diagnostic pairs are supplementary.'}
    (WB/'results/e131/functional_batch.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': result['status'], 'completed_pairs': completed, 'expected_pairs': 15}))
    if completed!=15 and not args.available_only: raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--available-only', action='store_true')
    run(parser.parse_args())
