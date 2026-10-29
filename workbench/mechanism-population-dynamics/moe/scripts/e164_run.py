"""E164: fixed expert banks crossed with their realized routing trajectories."""
import argparse
import os
_early = argparse.ArgumentParser(add_help=False)
_early.add_argument('--physical-gpu', type=int, default=0)
_args, _ = _early.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None, '', str(_args.physical_gpu)):
    raise ValueError('Physical GPU and visibility differ')
os.environ['CUDA_VISIBLE_DEVICES'] = str(_args.physical_gpu)
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

from contextlib import ExitStack
import json
from pathlib import Path
import platform
import socket
import subprocess
import time
import traceback

import numpy as np
import torch
import e150_native as n
import e151_native as removal
import e153_harness as task
import e156_loading as loading
from e163_metrics import first_token_KL
import e164_analyze as analysis
from e164_routing import RoutingEngine, permute_trace, route_differences

ROOT = analysis.ROOT
RAW = Path.home()/'mechpop_cache/e164_runtime_routing'
FILES = ('e164_data.py', 'e164_routing.py', 'e164_run.py', 'e164_analyze.py', 'e164_verify.py', 'e164_selftest.py',
         'e150_native.py', 'e150_data.py', 'e150_restricted.py', 'e144145_common.py', 'e144145_analyze.py',
         'e123_frozen_moe.py', 'e151_native.py', 'e150_partial_mask_test.py', 'e153_harness.py',
         'e156_loading.py', 'e154_native.py', 'e154_assets.py', 'e150_prepare_assets.py',
         'e163_metrics.py', 'supervised_process.py')


def proof():
    return {name: n.sha(Path(__file__).parent/name) for name in FILES}


def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': n.sha(path), 'size_bytes': path.stat().st_size}


def read(path):
    return json.loads(Path(path).read_text())


def software():
    return {'python': platform.python_version(), 'torch': torch.__version__,
            'transformers': n.transformers.__version__, 'numpy': np.__version__}


def save_arrays(path, values, *, replace=False):
    path = Path(path)
    if path.exists() and not replace:
        raise FileExistsError('Preserve earlier E164 artifact: '+str(path))
    temporary = path.with_name(path.name+'.tmp')
    with temporary.open('wb') as f:
        np.savez_compressed(f, **values)
    os.replace(temporary, path)
    return record(path)


def prepare():
    if (ROOT/'plan.json').exists():
        raise FileExistsError('Preserve frozen E164 plan')
    data = read(ROOT/'data_plan.json'); tests = read(ROOT/'CPU_routing_test.json')
    fixture = read(ROOT/'CPU_statistics_fixture.json')
    if data['source_sha256'] != n.sha(Path(__file__).parent/'e164_data.py'):
        raise ValueError('Input generator changed after preparing data')
    sources = proof()
    for test in (tests, fixture):
        if test['status'] != 'passed':
            raise ValueError('Matching CPU controls required')
        for name, expected in test['source_sha256'].items():
            if sources[name] != expected:
                raise ValueError('CPU control is stale: '+name)
    previous = read(n.WB/'results/e156/plan.json')
    m156 = read(n.WB/'results/e156/manifest.json'); m159 = read(n.WB/'results/e159/manifest.json')
    selectors = read(n.WB/'results/e156/selectors.json')['raw']
    for item in (data['data'], data['texts'], previous['task_input'], previous['legacy_cal_input'],
                 m156['raw'], m159['raw'], selectors):
        if n.sha(item['path']) != item['sha256']:
            raise ValueError('Frozen input/reference changed')
    a156 = analysis.arrays(m156['raw']['path']); a159 = analysis.arrays(m159['raw']['path'])
    old_masks = analysis.arrays(selectors['path'])
    reference = {'old_natural_LL': a156['candidate_loglikelihood'][[0, 2], 0],
                 'old_natural_KL': a156['first_answer_token_KL_vs_P'][[0, 2], 0],
                 'old_S0_LL': a159['candidate_loglikelihood'][[0, 2], 3],
                 'old_masks': old_masks['masks'], 'old_mask_probabilities': old_masks['mean_probabilities']}
    target = RAW/'references.npz'
    if target.exists():
        old = analysis.arrays(target)
        if set(old) != set(reference) or any(not np.array_equal(old[k], v) for k, v in reference.items()):
            raise ValueError('Reference preparation changed')
        ref = record(target)
    else:
        ref = save_arrays(target, reference)
    legacy_data = read(n.WB/'results/e153/data_plan.json')
    mature = read(n.WB/'results/e150/asset_manifest.json')['models']
    public_models = {'P': read(n.WB/'results/e154/asset_manifest.json')['model'],
                     'B': mature['StdMoE_1b14b_1T_EmoAnnealed']}
    public = {label: {name: item for name, item in model['files'].items()
                      if name.endswith('.py') or name in ('config.json', 'model.safetensors.index.json')}
              for label, model in public_models.items()}
    for files in public.values():
        for item in files.values():
            if n.sha(item['path']) != item['sha256']:
                raise ValueError('Pinned native public source changed')
    plan = {'experiment': 'E164', 'status': 'prepared', 'source_sha256': sources,
            'numerical_source_commit': subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD'], cwd=n.WB, text=True).strip(),
            'software': software(), 'conditions': list(analysis.CONDITIONS),
            'subjects': legacy_data['subjects']+data['subjects'],
            'legacy_input': previous['task_input'], 'fresh_input': data['data'],
            'data_plan': record(ROOT/'data_plan.json'), 'references': ref,
            'legacy_cal_input': previous['legacy_cal_input'],
            'source_records': {label: previous['source_records'][label] for label in ('P', 'B')},
            'public_source_files': public,
            'pad_token_id': data['pad_token_id'], 'calibration_batch_size': 2,
            'CPU_routing_test': record(ROOT/'CPU_routing_test.json'),
            'CPU_statistics_fixture': record(ROOT/'CPU_statistics_fixture.json'),
            'gpu_limit_seconds': 14400, 'resource_wait_limit_seconds': 7200,
            'max_concurrent_gpus': 1, 'user_total_gpu_limit': 4, 'new_training': False,
            'scope': 'Common P D/G/S, R_P/R_B and their actual gate trajectories; fresh55 subjects primary, old2 secondary.'}
    n.old.immutable_json(ROOT/'plan.json', plan)
    return {'status': 'prepared', 'plan_sha256': n.sha(ROOT/'plan.json')}


def checked_plan():
    plan = read(ROOT/'plan.json')
    if plan['source_sha256'] != proof() or plan['software'] != software():
        raise ValueError('Frozen numerical source/software changed')
    for name in ('legacy_input', 'fresh_input', 'data_plan', 'references', 'legacy_cal_input',
                 'CPU_routing_test', 'CPU_statistics_fixture'):
        item = plan[name]
        if n.sha(item['path']) != item['sha256']:
            raise ValueError('Frozen E164 input changed: '+name)
    for files in plan['public_source_files'].values():
        for item in files.values():
            if n.sha(item['path']) != item['sha256']:
                raise ValueError('Pinned native public source changed')
    return plan


def hook_counts(model):
    return [(len(m._forward_pre_hooks), len(m._forward_hooks)) for m in model.modules()]


def load_cpu(labels, plan, phase):
    if torch.cuda.is_initialized():
        raise ValueError('CPU preparation must precede CUDA initialization')
    start = time.monotonic(); models, states = [], []
    for label in labels:
        model = loading.load_cpu_bf16(label, device='cpu')
        ph = n.old.tensor_hash(model.state_dict()); bh = n.old.tensor_hash(n.buffers(model))
        expected = plan['source_records'][label]
        if ph != expected['parameter_hash'] or bh != expected['buffer_hash']:
            raise ValueError('Canonical CPU model/buffer differs: '+label)
        if sum(p.numel() for p in model.parameters()) != 13568641024:
            raise ValueError('Unexpected mature parameter count')
        models.append(model); states.append({'label': label, 'parameter_hash': ph, 'buffer_hash': bh,
                                             'hooks': hook_counts(model)})
        n.old.emit('E164_CPU_source_ready', phase=phase, label=label, seconds=time.monotonic()-start)
    n.write(ROOT/('CPU_readiness_'+phase+'.json'), {'status': 'ready', 'phase': phase,
             'host': socket.gethostname(), 'pid': os.getpid(), 'seconds': time.monotonic()-start,
             'sources': states, 'CUDA_initialized': torch.cuda.is_initialized()})
    return models, states


def acquire_gpu(physical, plan, phase):
    start = time.monotonic()
    while True:
        try:
            handle = n.old.gpu_lock(physical)
            n.write(ROOT/('GPU_wait_'+phase+'.json'), {'status': 'acquired', 'host': socket.gethostname(),
                    'physical_gpu': physical, 'pid': os.getpid(), 'wait_seconds': time.monotonic()-start})
            return handle
        except (RuntimeError, BlockingIOError) as error:
            if not isinstance(error, BlockingIOError) and 'occupied' not in str(error):
                raise
            if time.monotonic()-start >= plan['resource_wait_limit_seconds']:
                raise TimeoutError('Prepared CPU models retained until registered resource wait expired') from error
            n.write(ROOT/('GPU_wait_'+phase+'.json'), {'status': 'waiting_with_CPU_models',
                    'host': socket.gethostname(), 'physical_gpu': physical, 'pid': os.getpid(),
                    'wait_seconds': time.monotonic()-start, 'reason': str(error), 'gpu_seconds': 0})
        time.sleep(10)


class Budget(n.old.Budget):
    def __init__(self, plan, phase):
        self.path, self.experiment, self.phase = ROOT/'budget.json', 'e164', phase
        self.limit = plan['gpu_limit_seconds']; self.last_write = 0.

    def check(self):
        now = time.monotonic(); self.row['gpu_seconds'] = now-self.start
        exhausted = self.prior+self.row['gpu_seconds'] >= self.limit
        if now-self.last_write >= 15 or exhausted:
            n.write(self.path, self.state); self.last_write = now
        if exhausted:
            raise TimeoutError('Registered E164 GPU package exhausted')


def sequences(a, q):
    return [a['test_ids'][a['test_offsets'][4*q+i]:a['test_offsets'][4*q+i+1]] for i in range(4)]


def cal_sequences(a, subject):
    return [a['cal_ids'][a['cal_offsets'][i]:a['cal_offsets'][i+1]]
            for i in np.flatnonzero(a['cal_subject'] == subject)]


def score(model, seqs, prompt, pad, expected_count):
    values, counts, first = task.score_candidates(model, seqs, int(prompt), pad, check_causal=True)
    if not np.array_equal(counts, expected_count):
        raise ValueError('Actual scored candidate token population changed')
    return values, counts, first


def readonly(models, states):
    for model, state in zip(models, states):
        model.cpu()
        if n.old.tensor_hash(model.state_dict()) != state['parameter_hash']:
            raise ValueError('Source parameters were mutated')
        if n.old.tensor_hash(n.buffers(model)) != state['buffer_hash'] or hook_counts(model) != state['hooks']:
            raise ValueError('Source buffers/hooks were mutated')


@torch.no_grad()
def actual_P_calibration(model, plan):
    old = analysis.arrays(plan['legacy_cal_input']['path'])
    ids = torch.from_numpy(old['cal'][:2, :129].astype(np.int64)).to('cuda:0')
    valid = torch.from_numpy(old['cal_mask'][:2, :128]).to('cuda:0')
    attention = torch.cat([torch.ones((2, 1), dtype=torch.bool, device='cuda:0'), valid], 1)[:, :-1]
    item = plan['source_records']['P']['calibration']
    if n.sha(item['path']) != item['sha256']:
        raise ValueError('Legacy native P calibration changed')
    old_logits = analysis.arrays(item['path'])['logits']
    expected = torch.from_numpy(old_logits).view(torch.bfloat16).to('cuda:0')
    if not torch.equal(n.fwd(model, ids[:, :-1], attention), expected):
        raise ValueError('Native canonical P calibration failed exact replay')
    with RoutingEngine(model) as engine:
        engine.configure(capture=True)
        if not torch.equal(n.fwd(model, ids[:, :-1], attention), expected):
            raise ValueError('Gate capture changed native P computation')
        trace = tuple(engine.captured)
        engine.configure(trace=trace)
        if not torch.equal(n.fwd(model, ids[:, :-1], attention), expected):
            raise ValueError('Gate replay failed native P identity')


@torch.no_grad()
def preflight(physical):
    plan = checked_plan()
    if (ROOT/'preflight.json').exists() or (RAW/'selectors.npz').exists():
        raise FileExistsError('Preserve prior E164 preflight/selector provenance')
    models, states = load_cpu(('P',), plan, 'preflight'); model = models[0]
    lock = acquire_gpu(physical, plan, 'preflight')
    try:
        with Budget(plan, 'P_interface_and_selectors') as budget:
            model.to('cuda:0'); actual_P_calibration(model, plan)
            legacy = analysis.arrays(plan['legacy_input']['path'])
            fresh = analysis.arrays(plan['fresh_input']['path']); ref = analysis.arrays(plan['references']['path'])
            masks = np.empty((57, 16, 128), bool)
            probabilities = np.empty((57, 16, 127), np.float64)
            tokens = np.empty((57, 16), np.int64)
            for topic in range(57):
                a, index = (legacy, topic) if topic < 2 else (fresh, topic-2)
                keep, prob, count = task.greedy_masks(model, cal_sequences(a, index), plan['pad_token_id'], 32, 2,
                                                     lambda *args: budget.check())
                if not np.isfinite(prob).all():
                    raise ValueError('Nonfinite native selector calibration')
                if topic < 2 and (not np.array_equal(keep, ref['old_masks'][topic])
                                  or not np.array_equal(prob, ref['old_mask_probabilities'][topic])):
                    raise ValueError('Legacy P validation selector failed exact replay')
                masks[topic], probabilities[topic], tokens[topic] = keep, prob, count
                n.old.emit('E164_P_selector', subject=topic, total=57)
            seqs = sequences(legacy, 0); prompt = int(legacy['prompt_tokens'][0])
            with RoutingEngine(model) as engine:
                for policy in range(2):
                    engine.configure(capture=True)
                    with ExitStack() as stack:
                        if policy:
                            stack.enter_context(n.restricted.restricted_gates(model, np.broadcast_to(masks[0], (4, 16, 128)).copy()))
                        values, _, first = score(model, seqs, prompt, plan['pad_token_id'], legacy['answer_tokens'][0])
                    if not np.array_equal(values, ref['old_natural_LL'][0, policy, 0]):
                        raise ValueError('Legacy P actual task interface failed')
                    trace = tuple(engine.captured); engine.configure(trace=trace)
                    with ExitStack() as stack:
                        if policy:
                            stack.enter_context(n.restricted.restricted_gates(model, np.broadcast_to(masks[0], (4, 16, 128)).copy()))
                        repeated, _, repeated_first = score(model, seqs, prompt, plan['pad_token_id'], legacy['answer_tokens'][0])
                    if not np.array_equal(values, repeated) or not torch.equal(first, repeated_first):
                        raise ValueError('Real task route replay diagonal failed')
            peak = torch.cuda.max_memory_allocated()/1e9
            readonly(models, states)
        selectors = save_arrays(RAW/'selectors.npz', {'masks': masks, 'mean_probabilities': probabilities,
                                                      'cal_token_counts': tokens})
        n.write(ROOT/'preflight.json', {'experiment': 'E164', 'status': 'complete', 'source_sha256': proof(),
                'plan_sha256': n.sha(ROOT/'plan.json'), 'selectors': selectors, 'sources': states,
                'source_parameters_buffers_hooks_restored': True, 'native_cal_capture_replay_exact': True,
                'legacy_selector_masks_and_probabilities_exact': True, 'legacy_P_task_and_replay_exact': True,
                'peak_GPU_GB': peak, 'host': socket.gethostname(), 'physical_gpu': physical})
        n.old.emit('E164_preflight_complete', peak_GPU_GB=peak)
    finally:
        lock.close()


@torch.no_grad()
def evaluate(physical):
    plan = checked_plan(); pre = read(ROOT/'preflight.json')
    if pre['status'] != 'complete' or pre['source_sha256'] != proof() or pre['plan_sha256'] != n.sha(ROOT/'plan.json'):
        raise ValueError('Matching successful real-interface preflight required')
    if (ROOT/'manifest.json').exists() or (RAW/'scores.npz').exists() or (RAW/'partial_scores.npz').exists():
        raise FileExistsError('Preserve previous complete/partial E164 predictions before any recovery')
    if n.sha(pre['selectors']['path']) != pre['selectors']['sha256']:
        raise ValueError('Frozen selector changed')
    masks = analysis.arrays(pre['selectors']['path'])['masks']
    ref = analysis.arrays(plan['references']['path'])
    if masks.shape != (57, 16, 128) or not masks[:, :, -1].all() or not (masks.sum(-1) == 32).all():
        raise ValueError('Selector population changed')
    if not np.array_equal(masks[:2], ref['old_masks']):
        raise ValueError('Old selector differs')
    legacy = analysis.arrays(plan['legacy_input']['path']); fresh = analysis.arrays(plan['fresh_input']['path'])
    data = {'conditions': np.array(analysis.CONDITIONS), 'panel': np.r_[np.zeros(128, int), np.ones(440, int)],
            'subject': np.r_[legacy['subject'], fresh['subject']+2],
            **{k: np.concatenate([legacy[k], fresh[k]]) for k in ('gold', 'answer_tokens', 'answer_chars')},
            'candidate_loglikelihood': np.full((14, 568, 4), np.nan),
            'first_answer_token_KL': np.full((14, 568), np.nan),
            'natural_LL': np.full((2, 2, 568, 4), np.nan),
            'natural_KL': np.full((2, 2, 568), np.nan),
            'route_diagnostics': np.full((2, 568, 2, 16, 4), np.nan, np.float32),
            'trace_hashes': np.full((2, 2, 568), '', dtype='U64'),
            'gate0_hashes': np.full((2, 2, 568), '', dtype='U64')}
    models, states = load_cpu(('P', 'B'), plan, 'run'); blocks = n.original_blocks(models)
    lock = acquire_gpu(physical, plan, 'run')
    try:
        with Budget(plan, 'P_receiver_R_by_actual_routing_cross') as budget:
            models[0].to('cuda:0')
            for block in blocks[1]:
                for expert in block.experts[:-1]:
                    expert.to('cuda:0')
            actual_P_calibration(models[0], plan)
            model = models[0]
            with RoutingEngine(model) as engine:
                for q in range(568):
                    budget.check()
                    a, local = (legacy, q) if q < 128 else (fresh, q-128)
                    seqs = sequences(a, local); prompt = int(a['prompt_tokens'][local])
                    expected_count = a['answer_tokens'][local]; topic = int(data['subject'][q])
                    trajectories, firsts = {}, {}
                    def forward(r, policy, *, trace=None, capture=False, zero=False, order=None):
                        budget.check(); n.restore(models, blocks)
                        current = n.assemble(models, blocks, (0, 0, r, 0))
                        engine.configure(capture=capture, trace=trace)
                        actual = seqs if order is None else [seqs[i] for i in order]
                        count = expected_count if order is None else expected_count[order]
                        with ExitStack() as stack:
                            if zero:
                                stack.enter_context(removal.suppress(current, 'shared'))
                            if policy:
                                stack.enter_context(n.restricted.restricted_gates(current, np.broadcast_to(masks[topic], (4, 16, 128)).copy()))
                            return score(current, actual, prompt, plan['pad_token_id'], count)
                    for policy in range(2):
                        for r in range(2):
                            values, _, first = forward(r, policy, capture=True)
                            trajectories[policy, r] = tuple(engine.captured); firsts[policy, r] = first
                            data['natural_LL'][policy, r, q] = values
                            p_first = firsts[0, 0]
                            value_kl = first_token_KL(p_first, first)
                            data['natural_KL'][policy, r, q] = value_kl
                            if q < 128 and (not np.array_equal(values, ref['old_natural_LL'][r, policy, q])
                                            or value_kl != ref['old_natural_KL'][r, policy, q]):
                                raise ValueError('All-question legacy natural LL/FP64 KL guard failed')
                            trace = trajectories[policy, r]
                            data['trace_hashes'][policy, r, q] = n.old.tensor_hash({f'layer{i}': v for i, v in enumerate(trace)})
                            data['gate0_hashes'][policy, r, q] = n.old.tensor_hash({'layer0': trace[0]})
                        if not torch.equal(trajectories[policy, 0][0], trajectories[policy, 1][0]):
                            raise ValueError('Fixed P D/G must give identical first-layer gates across R sources')
                        length = max(map(len, seqs))-1
                        valid = np.arange(length)[None, :] < np.array([len(s)-1 for s in seqs])[:, None]
                        target_valid = valid & (np.arange(length)[None, :] >= prompt-1)
                        keep = masks[topic] if policy else np.ones((16, 128), bool)
                        for pos, valid_mask in enumerate((valid, target_valid)):
                            data['route_diagnostics'][policy, q, pos] = route_differences(
                                trajectories[policy, 0], trajectories[policy, 1], torch.from_numpy(keep),
                                torch.from_numpy(valid_mask).to('cuda:0'))
                    for policy in range(2):
                        for r in range(2):
                            for g in range(2):
                                values, counts, first = forward(r, policy, trace=trajectories[policy, g])
                                i = policy*4+r*2+g
                                data['candidate_loglikelihood'][i, q] = values
                                data['first_answer_token_KL'][i, q] = first_token_KL(p_first, first)
                                if r == g and (not np.array_equal(values, data['natural_LL'][policy, r, q])
                                               or not torch.equal(first, firsts[policy, r])):
                                    raise ValueError('Actual route replay diagonal failed')
                                if q in (0, 128):
                                    order = [2, 0, 3, 1]
                                    pv, pc, pf = forward(r, policy, trace=permute_trace(trajectories[policy, g], order, 4), order=order)
                                    if not np.array_equal(pv, values[order]) or not np.array_equal(pc, counts[order]) or not torch.equal(pf, first):
                                        raise ValueError('Actual replay candidate permutation failed')
                    for r in range(2):
                        values, _, first = forward(r, 0, zero=True)
                        data['candidate_loglikelihood'][8+r, q] = values
                        data['first_answer_token_KL'][8+r, q] = first_token_KL(p_first, first)
                        if q < 128 and not np.array_equal(values, ref['old_S0_LL'][r, q]):
                            raise ValueError('All-question legacy S-zero guard failed')
                        for g in range(2):
                            values, counts, first = forward(r, 0, trace=trajectories[0, g], zero=True)
                            i = 10+r*2+g
                            data['candidate_loglikelihood'][i, q] = values
                            data['first_answer_token_KL'][i, q] = first_token_KL(p_first, first)
                            if q in (0, 128):
                                order = [2, 0, 3, 1]
                                pv, pc, pf = forward(r, 0, trace=permute_trace(trajectories[0, g], order, 4), zero=True, order=order)
                                if not np.array_equal(pv, values[order]) or not np.array_equal(pc, counts[order]) or not torch.equal(pf, first):
                                    raise ValueError('S-zero replay candidate permutation failed')
                    n.restore(models, blocks); engine.configure()
                    del trajectories, firsts, p_first
                    if q % 8 == 7 or q == 567:
                        save_arrays(RAW/'partial_scores.npz', {**data, 'completed_questions': np.array(q+1)}, replace=True)
                        n.old.emit('E164_progress', questions=q+1, total=568, panel='old_guard' if q < 128 else 'fresh_primary')
            if not np.isfinite(data['candidate_loglikelihood']).all() or not np.isfinite(data['first_answer_token_KL']).all():
                raise ValueError('Incomplete/nonfinite E164 scores')
            peak = torch.cuda.max_memory_allocated()/1e9
            n.restore(models, blocks); readonly(models, states)
        output = save_arrays(RAW/'scores.npz', data)
        n.write(ROOT/'manifest.json', {'experiment': 'E164', 'status': 'complete', 'source_sha256': proof(),
                'plan_sha256': n.sha(ROOT/'plan.json'), 'raw': output, 'preflight_sha256': n.sha(ROOT/'preflight.json'),
                'selectors': pre['selectors'], 'source_parameters_buffers_hooks_restored': True, 'sources': states,
                'all_legacy_natural_LL_and_KL_exact': True, 'all_legacy_S0_LL_exact': True,
                'all_actual_route_diagonals_and_causal_prefix_counts_exact': True,
                'first_old_and_fresh_replay_permutation_exact': True, 'first_layer_gate_identity_exact': True,
                'fresh_primary_questions': 440, 'legacy_secondary_questions': 128,
                'peak_GPU_GB': peak, 'host': socket.gethostname(), 'physical_gpu': physical,
                'budget': record(ROOT/'budget.json')})
        n.old.emit('E164_complete', peak_GPU_GB=peak, raw_sha256=output['sha256'])
    finally:
        lock.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('prepare', 'preflight', 'run'))
    p.add_argument('--physical-gpu', type=int, default=0); args = p.parse_args()
    torch.set_num_threads(4)
    if args.mode == 'prepare':
        print(json.dumps(prepare(), indent=2)); return
    try:
        (preflight if args.mode == 'preflight' else evaluate)(args.physical_gpu)
    except BaseException as error:
        n.write(ROOT/('failure_'+args.mode+'.json'), {'status': 'failed', 'phase': args.mode,
                'error': type(error).__name__+': '+str(error), 'traceback': traceback.format_exc(),
                'source_sha256': proof(), 'host': socket.gethostname(), 'pid': os.getpid()})
        raise


if __name__ == '__main__':
    main()
