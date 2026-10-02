"""CPU audit: sequential AdamW loads must not mutate a common source state.

This reproduces the E16 optimizer-step alias and checks its deepcopy fix.
It runs no model, simulator, or CUDA operation and measures no scientific effect.
"""
import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path

import torch


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def source_state():
    parameter = torch.nn.Parameter(torch.tensor([1.], device='cpu'))
    optimizer = torch.optim.AdamW([parameter], lr=5e-5, weight_decay=1e-3,
                                 capturable=False, fused=False)
    parameter.square().sum().backward()
    optimizer.step()
    return copy.deepcopy(optimizer.state_dict())


def sequential_methods(isolate):
    common = source_state()
    source_step = common['state'][0]['step']
    initial = float(source_step)
    rows = []
    for method in range(3):
        parameter = torch.nn.Parameter(torch.tensor([1.], device='cpu'))
        optimizer = torch.optim.AdamW([parameter], lr=5e-5, weight_decay=1e-3,
                                     capturable=False, fused=False)
        optimizer.load_state_dict(copy.deepcopy(common) if isolate else common)
        step = optimizer.state[parameter]['step']
        row = {'method': method, 'begin_step': float(step),
               'source_begin_step': float(source_step),
               'step_aliases_source': step.data_ptr() == source_step.data_ptr()}
        for _ in range(2):
            optimizer.zero_grad(set_to_none=True)
            parameter.square().sum().backward()
            optimizer.step()
        row.update({'end_step': float(step), 'source_end_step': float(source_step)})
        rows.append(row)
    if isolate:
        assert all(r['begin_step'] == initial and r['end_step'] == initial+2
                   and r['source_end_step'] == initial and not r['step_aliases_source']
                   for r in rows), 'Deepcopy did not isolate optimizer state'
    else:
        assert all(r['step_aliases_source'] and r['source_end_step'] == r['end_step']
                   for r in rows), 'Legacy step alias was not reproduced'
        assert [r['begin_step'] for r in rows] == [initial, initial+2, initial+4]
    return rows


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    source = Path(__file__).resolve()
    optimizer_source = Path(inspect.getfile(torch.optim.Optimizer))
    (output/'optimizer_isolation_audit_used.py').write_text(source.read_text())
    (output/'torch_optimizer_used.py').write_text(optimizer_source.read_text())
    summary = {
        'experiment_card': 'E16_equal_budget_data_value',
        'scope': 'CPU implementation audit; not an environment or training-effect experiment',
        'device': 'cpu', 'cuda_operations': 0, 'torch_version': torch.__version__,
        'script_sha256': sha256(source),
        'torch_optimizer_source_sha256': sha256(optimizer_source),
        'legacy_no_copy': sequential_methods(False),
        'fixed_deepcopy': sequential_methods(True),
        'interpretation': 'Noncapturable/nonfused AdamW load retains the source CPU step tensor; sequential methods mutate the common checkpoint step unless the entire optimizer state is copied.',
        'cpu_scope_note': 'Other CPU optimizer tensors can also alias. This audit isolates the reported step observation; it does not claim CUDA moment tensors alias or quantify the original training effect.',
        'affected_runs': [
            '/home/xiang/.cache/latent-wm-results/20261002-E16-methods-A100-s0',
            '/home/xiang/.cache/latent-wm-results/20261002-E16-independent-s1/methods',
            '/home/xiang/.cache/latent-wm-results/20261002-E16-independent-s2/methods',
            '/tmp/latent-wm-runs/20261002-E16-objective-matrix-RTX-s0',
        ],
        'affected_code': ['acquisition_pilot.py: sequential train_one calls sharing base_state',
                          'objective_matrix.py: six methods sharing one loaded state'],
        'comparison_status': 'Original results retained; equal-optimizer data/objective attribution downgraded. Original objective matrix stopped incomplete and invalidated as a fair comparison. Complete controlled reruns are required.',
        'not_affected_by_this_bug': ['E13 frozen-model planning comparisons',
            'E18 per-fork fresh AdamW adaptation', 'E16 base training without sequential method reloads',
            'sealed acquisition selections and recorded environment branches',
            'recorded success/outcome counts as descriptive outputs of the actual trained checkpoints'],
        'fixed_code_sha256': {
            name: sha256(source.with_name(name))
            for name in ['acquisition_pilot.py', 'objective_matrix.py']
        },
        'artifact_directory': str(output.resolve()),
        'passed': True,
    }
    write_json(output/'summary.json', summary)
    write_json(output/'complete.json', {'completed': True, 'passed': True,
                                      'summary_sha256': sha256(output/'summary.json')})
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    run(parser.parse_args().output)
