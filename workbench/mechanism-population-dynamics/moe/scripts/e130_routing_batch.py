"""Run the 17 registered E130 N1 routing comparisons with explicit coverage."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import torch
import e124_routing as metric

WB = Path(__file__).resolve().parents[1]
ROOT = Path('/tmp/xiang-moe-20261025/e130_analysis')
IDS = ['seed0_anchor'] + [f'seed{i}_order0' for i in range(1, 5)]


def run(args):
    folder = WB / 'results/e130/routing'
    folder.mkdir(parents=True, exist_ok=True)
    hpath = ROOT / 'Hcal.npy'
    hcal, hsha = metric.load_hcal(hpath), metric.file_sha256(hpath)
    source_sha = metric.file_sha256(Path(metric.__file__))
    pairs = [(a, 'final', b, 'final', 'different_initializations') for a, b in itertools.combinations(IDS, 2)]
    pairs += [(a, 'late', a, 'final', 'same_model_late') for a in IDS]
    pairs += [('seed0_anchor', 'final', b, 'final', kind) for b, kind in [
        ('seed0_repeat', 'same_initialization_same_stream'),
        ('seed0_order1', 'same_initialization_different_stream')]]
    captures, reports, missing, errors = {}, [], [], []

    def capture(name, phase):
        key = name, phase
        if key not in captures:
            loaded = metric.load_capture(ROOT / name / (phase + '.npz'))
            seed = 0 if name.startswith('seed0_') else int(name[4])
            order = 1 if name == 'seed0_order1' else 0
            meta = loaded['metadata']
            if (meta.get('step'), meta.get('seed'), meta.get('order_seed'), meta.get('layer')) != (
                    62500 if phase == 'final' else 61440, seed, order, 9):
                raise ValueError(f'Wrong registered capture identity: {key}')
            captures[key] = loaded
        return captures[key]

    for a, sa, b, sb, kind in pairs:
        key = f'{a}_{sa}__{b}_{sb}'
        if not (ROOT / a / (sa + '.npz')).exists() or not (ROOT / b / (sb + '.npz')).exists():
            missing.append(key)
            continue
        path = folder / (key + '.json')
        try:
            ca, cb = capture(a, sa), capture(b, sb)
            old = json.loads(path.read_text()) if path.exists() else None
            cached = (old is not None and old['capture_A']['sha256'] == ca['capture_sha256']
                      and old['capture_B']['sha256'] == cb['capture_sha256'] and old['Hcal']['sha256'] == hsha
                      and old['protocol']['n_draws'] == 32 and old['protocol']['null_seed'] == 124
                      and old.get('routing_source_sha256') == source_sha and old.get('device') == args.device)
            value = old if cached else metric.analyze(ca, cb, hcal, hpath, torch.device(args.device),
                                                       ROOT.parent / 'e130_routing_cache')
            value.update(comparison_kind=kind, registered_experiment='E130', routing_source_sha256=source_sha)
            path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
            reports.append({'key': key, 'kind': kind, 'T_equal_word_mean': value['T_equal_word_mean'],
                            'T_pooled': value['T_pooled_after_within_word_centering'],
                            'raw_T': value['rawC_auxiliary']['T_equal_word_mean'],
                            'D_std': value['D_std_after_word_centering_A_B'], 'file': str(path)})
            print(json.dumps(reports[-1]), flush=True)
        except Exception as error:
            errors.append({'key': key, 'error': f'{type(error).__name__}: {error}'})
    result = {'status': 'complete' if not missing and not errors else 'partial', 'expected_pairs': 17,
              'completed_pairs': len(reports), 'missing_pairs': missing, 'failures': errors, 'pairs': reports,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'routing_source_sha256': source_sha,
              'scope': 'Registered N1 residual organization; shared-seed pairs are not independent. '
                       'The order1 control changes the input stream, not only temporal order.'}
    (folder / 'batch_summary.json').write_text(json.dumps(result, indent=2) + '\n')
    if errors or (missing and not args.available_only):
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=('cpu', 'cuda'), default='cuda')
    parser.add_argument('--available-only', action='store_true')
    run(parser.parse_args())
