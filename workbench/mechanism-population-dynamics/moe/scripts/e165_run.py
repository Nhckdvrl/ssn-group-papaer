"""E165 mature OLMoE source cube, task selection, and realized-route replay."""
import argparse
import os
early = argparse.ArgumentParser(add_help=False)
early.add_argument('--physical-gpu', type=int, default=0)
visible, _ = early.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None, '', str(visible.physical_gpu)):
    raise ValueError('Physical GPU visibility differs')
os.environ['CUDA_VISIBLE_DEVICES'] = str(visible.physical_gpu)
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

from contextlib import ExitStack
import socket
import time
import traceback

import numpy as np
import torch
import e165_common as c
import e165_core as core
import e165_analyze as analysis
import e153_harness as scoring
from e163_metrics import first_token_KL


def score(model, sequences, prompt, pad, expected):
    ll, counts, first = scoring.score_candidates(model, sequences, int(prompt), pad, check_causal=True)
    if not np.array_equal(counts, expected):
        raise ValueError('Scored token population differs')
    return ll, first


def input_arrays(plan):
    return analysis.arrays(plan['input']['path'])


def preflight(physical):
    plan = c.checked_plan()
    if (c.ROOT/'preflight.json').exists() or (c.RAW/'selectors.npz').exists():
        raise FileExistsError('Preserve earlier real-interface preflight')
    a = input_arrays(plan); assets = c.read(plan['asset_manifest']['path'])
    models, states = c.load_cpu('PA', assets, plan['source_records'], 'preflight')
    original = core.blocks(models); lock = None
    try:
        lock = c.acquire(physical, plan, 'preflight')
        with c.Budget(plan, 'native_interfaces_and_parent_selectors') as budget:
            models = [model.to('cuda:0') for model in models]
            native_full, native_first = [], []
            seqs = core.sequences(a, 0); prompt = a['prompt_tokens'][0]; expected = a['answer_tokens'][0]
            for r in range(2):
                budget.check()
                ll, first = score(models[r], seqs, prompt, plan['pad_token_id'], expected)
                native_full.append(ll); native_first.append(first)
                model = core.assemble(models, original, (r, r, r))
                with core.RoutingEngine(model) as engine:
                    engine.configure(capture=True)
                    value, fp = score(model, seqs, prompt, plan['pad_token_id'], expected)
                    trace = tuple(engine.captured)
                    if not np.array_equal(value, ll) or not torch.equal(fp, first):
                        raise ValueError('Real native assembled corner differs')
                    engine.configure(trace=trace)
                    value, fp = score(model, seqs, prompt, plan['pad_token_id'], expected)
                    if not np.array_equal(value, ll) or not torch.equal(fp, first):
                        raise ValueError('Real actual-route identity differs')
                with core.zero_moe(model):
                    _, zero_first = score(model, seqs, prompt, plan['pad_token_id'], expected)
                if torch.equal(zero_first, first):
                    raise ValueError('Whole-MoE zero did not alter real prediction')
                core.restore(models, original)
            masks = np.empty((55, 16, 64), bool)
            probabilities = np.empty_like(masks, dtype=np.float64)
            counts = np.empty((55, 16), np.int64)
            for subject in range(55):
                budget.check()
                masks[subject], probabilities[subject], counts[subject] = core.greedy(
                    models[0], core.calibration(a, subject), plan['pad_token_id'], 16, 2)
                if subject % 5 == 4:
                    print(c.json.dumps({'event': 'E165_selectors', 'subjects': subject+1, 'total': 55}), flush=True)
            random = np.zeros((3, 16, 64), bool)
            for i in range(3):
                rng = np.random.default_rng(165101+i)
                for layer in range(16):
                    random[i, layer, rng.choice(64, 16, replace=False)] = True
            masked_ref, masked_hash = [], []
            for r in range(2):
                with core.restricted(models[r], masks[int(a['subject'][0])]):
                    ll, first = score(models[r], seqs, prompt, plan['pad_token_id'], expected)
                masked_ref.append(ll); masked_hash.append(c.old.tensor_hash({'first': first}))
            selectors = c.save(c.RAW/'selectors.npz', {'masks': masks, 'probabilities': probabilities,
                                                      'token_counts': counts, 'random_masks': random})
            reference = c.save(c.RAW/'preflight_reference.npz',
                               {'native_full_LL': np.array(native_full), 'native_masked_LL': np.array(masked_ref),
                                'full_first_hash': np.array([c.old.tensor_hash({'first': v}) for v in native_first]),
                                'masked_first_hash': np.array(masked_hash)})
            core.restore(models, original); c.readonly(models, states)
            peak = torch.cuda.max_memory_allocated()/1e9
        c.write(c.ROOT/'preflight.json', {'experiment': 'E165', 'status': 'complete',
                'plan_sha256': c.sha(c.ROOT/'plan.json'), 'selectors': selectors, 'reference': reference,
                'both_native_corners_and_route_replay_exact': True, 'real_zero_positive': True,
                'all55_parent_selectors_complete': True, 'source_readonly_passed': True,
                'peak_GPU_GB': peak, 'source_sha256': c.proof()})
        print(c.json.dumps({'status': 'preflight_complete', 'peak_GPU_GB': peak}), flush=True)
    finally:
        core.restore(models, original)
        if lock is not None:
            lock.close()


@torch.no_grad()
def evaluate(physical):
    plan = c.checked_plan(); pre = c.read(c.ROOT/'preflight.json')
    if pre['status'] != 'complete' or pre['plan_sha256'] != c.sha(c.ROOT/'plan.json'):
        raise ValueError('Matching completed real interfaces required')
    for key in ('selectors', 'reference'):
        if c.sha(pre[key]['path']) != pre[key]['sha256']:
            raise ValueError('Preflight asset changed')
    if any(p.exists() for p in [c.ROOT/'manifest.json', c.RAW/'scores.npz', c.RAW/'partial_scores.npz']):
        raise FileExistsError('Audit earlier E165 attempt; no automatic overwrite/resume')
    a = input_arrays(plan); selectors = analysis.arrays(pre['selectors']['path'])
    reference = analysis.arrays(pre['reference']['path'])
    models, states = c.load_cpu('PA', c.read(plan['asset_manifest']['path']), plan['source_records'], 'run')
    original = core.blocks(models); lock = None
    data = {key: a[key] for key in ('subject', 'gold', 'answer_tokens', 'answer_chars')}
    data.update(candidate_loglikelihood=np.full((26, 440, 4), np.nan),
                first_answer_token_KL=np.full((26, 440), np.nan),
                natural_LL=np.full((2, 2, 440, 4), np.nan),
                conditions=np.array(analysis.CONDITIONS),
                trace_hashes=np.full((2, 2, 440), '', dtype='U64'),
                gate0_hashes=np.full((2, 2, 440), '', dtype='U64'))
    permutation = [2, 0, 3, 1]
    try:
        lock = c.acquire(physical, plan, 'run')
        with c.Budget(plan, 'mature_sources_and_actual_routes') as budget:
            models = [m.to('cuda:0') for m in models]
            for q in range(440):
                budget.check(); core.restore(models, original)
                seqs = core.sequences(a, q); prompt = a['prompt_tokens'][q]; expected = a['answer_tokens'][q]
                subject = int(a['subject'][q]); selected = selectors['masks'][subject]
                firsts = {}
                # Original native modules, before source assembly: independent real identity references.
                for r in range(2):
                    for p in range(2):
                        with ExitStack() as stack:
                            if p:
                                stack.enter_context(core.restricted(models[r], selected))
                            ll, fp = score(models[r], seqs, prompt, plan['pad_token_id'], expected)
                        data['natural_LL'][r, p, q] = ll; firsts[r, p] = fp
                        if q == 0:
                            name = 'native_full_LL' if p == 0 else 'native_masked_LL'
                            hname = 'full_first_hash' if p == 0 else 'masked_first_hash'
                            if not np.array_equal(ll, reference[name][r]) or c.old.tensor_hash({'first': fp}) != reference[hname][r]:
                                raise ValueError('Whole-worker native preflight guard differs')
                factual = firsts[0, 0]
                for p in range(2):
                    traces, trace_firsts = {}, {}
                    for index, case in enumerate(analysis.CASES):
                        budget.check(); model = core.assemble(models, original, case)
                        with ExitStack() as stack:
                            engine = stack.enter_context(core.RoutingEngine(model)) if case in ((0, 0, 0), (0, 0, 1)) else None
                            if engine is not None:
                                engine.configure(capture=True)
                            if p:
                                stack.enter_context(core.restricted(model, selected))
                            ll, fp = score(model, seqs, prompt, plan['pad_token_id'], expected)
                            if engine is not None:
                                r = case[2]; traces[r] = tuple(engine.captured); trace_firsts[r] = fp
                        data['candidate_loglikelihood'][8*p+index, q] = ll
                        data['first_answer_token_KL'][8*p+index, q] = first_token_KL(factual, fp)
                        if case in ((0, 0, 0), (1, 1, 1)):
                            r = case[0]
                            if not np.array_equal(ll, data['natural_LL'][r, p, q]) or not torch.equal(fp, firsts[r, p]):
                                raise ValueError('Native source cube corner failed exact identity')
                    for r in range(2):
                        data['trace_hashes'][p, r, q] = c.old.tensor_hash({f'layer{i}': v for i, v in enumerate(traces[r])})
                        data['gate0_hashes'][p, r, q] = c.old.tensor_hash({'gate0': traces[r][0]})
                    if data['gate0_hashes'][p, 0, q] != data['gate0_hashes'][p, 1, q]:
                        raise ValueError('First gate changed before the changed expert source could act')
                    for r in range(2):
                        model = core.assemble(models, original, (0, 0, r))
                        for g in range(2):
                            budget.check()
                            with ExitStack() as stack:
                                engine = stack.enter_context(core.RoutingEngine(model)); engine.configure(trace=traces[g])
                                if p:
                                    stack.enter_context(core.restricted(model, selected))
                                ll, fp = score(model, seqs, prompt, plan['pad_token_id'], expected)
                                if r == g:
                                    if not np.array_equal(ll, data['candidate_loglikelihood'][8*p+r, q]) or not torch.equal(fp, trace_firsts[r]):
                                        raise ValueError('Actual-route diagonal did not reproduce natural computation')
                                else:
                                    index = 16+2*p+r
                                    data['candidate_loglikelihood'][index, q] = ll
                                    data['first_answer_token_KL'][index, q] = first_token_KL(factual, fp)
                                if q == 0:
                                    engine.configure(trace=core.permute_trace(traces[g], permutation, 4))
                                    other, op = score(model, [seqs[i] for i in permutation], prompt,
                                                      plan['pad_token_id'], expected[permutation])
                                    if not np.array_equal(other, ll[permutation]) or not torch.equal(op, fp):
                                        raise ValueError('Fixed route reused future-candidate or batch-order information')
                for r in range(2):
                    model = core.assemble(models, original, (r, r, r))
                    for k in range(3):
                        budget.check()
                        with core.restricted(model, selectors['random_masks'][k]):
                            ll, fp = score(model, seqs, prompt, plan['pad_token_id'], expected)
                        data['candidate_loglikelihood'][20+3*r+k, q] = ll
                        data['first_answer_token_KL'][20+3*r+k, q] = first_token_KL(factual, fp)
                if q % 8 == 7:
                    c.save(c.RAW/'partial_scores.npz', data, replace=True)
                    print(c.json.dumps({'event': 'E165_progress', 'questions': q+1, 'total': 440}), flush=True)
            if not np.isfinite(data['candidate_loglikelihood']).all() or not np.isfinite(data['first_answer_token_KL']).all():
                raise ValueError('Incomplete final scientific population')
            core.restore(models, original); c.readonly(models, states)
            output = c.save(c.RAW/'scores.npz', data)
            peak = torch.cuda.max_memory_allocated()/1e9
        c.write(c.ROOT/'manifest.json', {'experiment': 'E165', 'status': 'complete', 'source_sha256': c.proof(),
                'plan_sha256': c.sha(c.ROOT/'plan.json'), 'raw': output,
                'preflight_sha256': c.sha(c.ROOT/'preflight.json'), 'selectors': pre['selectors'],
                'source_parameters_buffers_hooks_restored': True, 'sources': states,
                'both_native_corners_and_preflight_guard_exact': True,
                'all_actual_route_diagonals_and_causal_prefix_counts_exact': True,
                'first_question_all_route_replay_permutations_exact': True, 'first_layer_gate_identity_exact': True,
                'questions': 440, 'subjects': 55, 'conditions': list(analysis.CONDITIONS),
                'peak_GPU_GB': peak, 'host': socket.gethostname(), 'physical_gpu': physical,
                'budget': c.read(c.ROOT/'budget.json')})
        print(c.json.dumps({'event': 'E165_complete', 'peak_GPU_GB': peak, 'raw_sha256': output['sha256']}), flush=True)
    finally:
        core.restore(models, original)
        if lock is not None:
            lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'preflight', 'run'))
    parser.add_argument('--physical-gpu', type=int, default=0)
    args = parser.parse_args(); torch.set_num_threads(4)
    try:
        if args.mode == 'prepare':
            c.prepare()
        else:
            with torch.no_grad():
                preflight(args.physical_gpu) if args.mode == 'preflight' else evaluate(args.physical_gpu)
    except BaseException as error:
        c.write(c.ROOT/('failure_'+args.mode+'.json'), {'status': 'failed', 'error': type(error).__name__+': '+str(error),
                'traceback': traceback.format_exc(), 'CUDA_initialized': torch.cuda.is_initialized(),
                'host': socket.gethostname(), 'pid': os.getpid()})
        raise


if __name__ == '__main__':
    main()
