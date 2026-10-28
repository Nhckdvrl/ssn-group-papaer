"""Restart interrupted E160 with unchanged numerical code and separate ledgers.

The parent attempt is preserved verbatim. Only the numerical driver's output
directory (plan, budget, manifest) changes; its inputs and condition grid do not.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'evaluate', 'analyze', 'audit'))
    parser.add_argument('--physical-gpu', type=int, default=1)
    args = parser.parse_args()
    import e160_run as original
    parent = original.RESULT
    retry = parent / 'retry_1'
    if args.mode == 'prepare':
        ledger = original.n.read(parent/'budget.json')
        if len(ledger['attempts']) != 1 or ledger['attempts'][0]['status'] != 'running':
            raise ValueError('Expected the single preserved interrupted attempt')
        pid = ledger['attempts'][0]['pid']
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise RuntimeError('Previous process still exists; refusing a duplicate')
        if (original.RAW/'scores.npz').exists() or (parent/'manifest.json').exists():
            raise ValueError('Parent scientific result exists; not an interruption')
        plan = original.n.read(parent/'plan.json')
        if plan['source_sha256'] != original.proof():
            raise ValueError('The original frozen numerical code has changed')
        retry.mkdir(exist_ok=False)
        for name in ('plan.json', 'self_test.json'):
            (retry/name).write_bytes((parent/name).read_bytes())
        record = {
            'experiment': 'E160', 'kind': 'operational_retry_before_any_result_read',
            'observed_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'parent_budget_path': str(parent/'budget.json'),
            'parent_budget_sha256': original.n.sha(parent/'budget.json'),
            'parent_budget_unmodified': ledger,
            'old_log': original.record(original.RAW/'evaluation.log'),
            'parent_pid_absent': True, 'parent_manifest_and_scores_absent': True,
            'last_completed_question_progress': 32,
            'parent_recorded_gpu_seconds_lower_bound': ledger['attempts'][0]['gpu_seconds'],
            'parent_exact_duration_and_exit_code': 'unknown; supervisor was not present',
            'cause': 'unknown; log has no traceback; no privileged kernel log available',
            'retry_output_directory': str(retry), 'retry_limit_gpu_seconds': 10800,
            'resource_amendment': 'Additional execution allowance for one complete unchanged rerun. Parent cost remains separately visible and unknown above its recorded lower bound. No exact combined cost or original aggregate cap compliance is claimed.',
            'numerical_code': '55960d57; all original source hashes unchanged',
            'adapter_sha256': original.n.sha(__file__),
            'conditions_inputs_statistics_selection': 'unchanged; no partial outcome arrays exist or were inspected'
        }
        original.n.write(retry/'recovery.json', record)
        print(json.dumps({'status':'prepared','retry_root':str(retry)}, indent=2))
        return
    if not (retry/'recovery.json').is_file():
        raise ValueError('Prepare and freeze the recovery record first')
    recovery = original.n.read(retry/'recovery.json')
    if original.n.sha(parent/'budget.json') != recovery['parent_budget_sha256'] or original.n.sha(__file__) != recovery['adapter_sha256']:
        raise ValueError('Preserved parent or frozen adapter changed')
    original.RESULT = retry
    original.torch.set_num_threads(4)
    if args.mode == 'evaluate':
        result = original.evaluate(args.physical_gpu)
    elif args.mode == 'analyze':
        original.analysis.ROOT = retry
        result = original.analysis.analyze()
    else:
        spec = importlib.util.spec_from_file_location('e160_independent_retry', parent.parent/'e160_independent_audit/audit.py')
        independent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(independent)
        independent.ROOT = retry
        result = independent.audit()
        plan = independent.read(retry/'plan.json')
        manifest = independent.read(retry/'manifest.json')
        with independent.np.load(manifest['raw']['path'], allow_pickle=False) as file:
            raw = {key:file[key] for key in file.files}
        result['comparison'] = independent.compare_summary(raw, independent.read(retry/'summary.json'), manifest, retry/'plan.json')
        original.n.write(retry/'independent_report.json', result)
        if result['comparison']['status'] != 'passed':
            raise ValueError('Independent comparison failed')
        result = {'status':'passed', 'comparison':result['comparison']}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
