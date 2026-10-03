"""E16: data x training-object pilot, reusing RC-aux's actual rollout.

Only the multi-step component is borrowed. This is not full RC-aux replication.
"""
import argparse
import copy
from collections import Counter
import importlib.util
import json
from pathlib import Path
import shutil

import h5py
import numpy as np
import torch
from lewm_pilot import architecture, digest, dump, evaluate, load_training, now, pixels
from module import SIGReg


RC_SOURCE = Path(__file__).resolve().parents[1] / 'vendor/rc-aux/jepa.py'
spec = importlib.util.spec_from_file_location('rcaux_rollout_reference', RC_SOURCE)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
rollout = reference.JEPA.rollout_open_loop


def optimizer_steps(state_dict):
    """Detach scalar values so the common AdamW step snapshot is immutable."""
    return tuple((key, int(value['step'])) for key, value in sorted(state_dict['state'].items()) if 'step' in value)


def future_predictions(model, emb, actions, recursive):
    if recursive:
        return rollout(model, emb[:, :3], actions[:, :3], actions[:, 3:5],
                       horizon=3, history_size=3)
    return torch.cat([model.predict(emb[:, t:t+3], actions[:, t:t+3])[:, -1:]
                      for t in range(3)], dim=1)


@torch.inference_mode()
def check_rollout(model, cache, controls, mean, std):
    model.eval()
    images = pixels(cache[np.arange(0, 26, 5)][None])
    acts = torch.tensor((controls[:25] - mean) / std, device='cuda').float().reshape(1, 5, 10)
    info = model.encode({'pixels': images, 'action': acts})
    emb, action = info['emb'], info['act_emb']
    recursive = future_predictions(model, emb, action, True)
    teacher = future_predictions(model, emb, action, False)
    context = emb[:, :3]
    manual = []
    for step in range(3):
        pred = model.predict(context[:, -3:], action[:, step:step+3])[:, -1:]
        manual.append(pred)
        context = torch.cat([context, pred], dim=1)
    manual = torch.cat(manual, dim=1)
    if not torch.allclose(recursive, manual, atol=1e-5, rtol=1e-5):
        raise ValueError('Official RC-aux rollout does not match independent recurrence')
    if not torch.allclose(recursive[:, :1], teacher[:, :1], atol=1e-5, rtol=1e-5):
        raise ValueError('Teacher-forced and recursive first step must agree')
    return {'rc_vs_manual_max_abs': float((recursive-manual).abs().max()),
            'tf_vs_open_first_step_max_abs': float((recursive[:, :1]-teacher[:, :1]).abs().max()),
            'future_target_frames': [15, 20, 25], 'action_blocks': 5}


def run(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    state = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    source_steps = optimizer_steps(state['optimizer'])
    bank = Path(args.bank)
    if state['epoch'] != 30 or not (bank/'complete.json').exists():
        raise ValueError('Requires the complete, locked common-base30 acquisition bank')
    bank_config = json.loads((bank/'config.json').read_text())
    seal = json.loads((bank/'selection_seal.json').read_text())['sha256']
    if bank_config['base_sha256'] != digest(args.checkpoint) or seal != digest(bank/'selection_ledger.json'):
        raise ValueError('Checkpoint or sealed acquisition ledger mismatch')
    manifest = state['manifest']
    cache, controls, _, io = load_training(args.dataset, manifest)
    # Both objectives see the same complete 25-step clips, without cross-episode labels.
    starts = []
    with h5py.File(args.dataset) as f:
        lengths = f['ep_len'][:]
        offset = 0
        for episode in sorted(manifest['base_episodes']):
            n = int(lengths[episode])
            starts.extend(range(offset, offset+n-25))
            offset += n
    starts = np.asarray(starts)
    ledger = json.loads((bank/'selection_ledger.json').read_text())['UNIFORM-COMMON-RESET']
    branch_pixels, branch_actions = [], []
    with h5py.File(bank/'hidden_branches.h5') as f:
        for anchor, candidate in ledger:
            item = f[f'a{anchor:03d}_c{candidate:03d}']
            im, a = item['pixels'][:], item['actions'][:]
            if len(im) != 26 or len(a) != 25:
                raise ValueError('A purchased branch must contain exactly 25 transitions')
            branch_pixels.append(im[np.arange(0, 26, 5)])
            branch_actions.append(a)
    branch_pixels, branch_actions = np.asarray(branch_pixels), np.asarray(branch_actions)
    mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    config = vars(args).copy()
    config.update({'hardware': torch.cuda.get_device_name(), 'torch': torch.__version__,
        'harness_sha256': digest(__file__), 'helper_sha256': digest(Path(__file__).with_name('lewm_pilot.py')),
        'base_checkpoint_sha256': digest(args.checkpoint), 'selection_ledger_sha256': seal,
        'hidden_branch_sha256': digest(bank/'hidden_branches.h5'), 'base_manifest': manifest,
        'rcaux_commit': 'cbdf3786b149df8145d6c7314f32f460d43c9695', 'rcaux_jepa_sha256': digest(RC_SOURCE),
        'data_policies': ['NO-ADD', 'UNIFORM'], 'objectives': ['ONE-STEP', 'TF-LONG', 'OPEN-LONG'],
        'batch_size': 128, 'branch_samples_per_uniform_batch': 13, 'base_complete_clips': len(starts),
        'logical_new_env_steps': {'NO-ADD': 0, 'UNIFORM': 2000}, 'reused_bank_no_new_interaction': True,
        'frames': [0, 5, 10, 15, 20, 25], 'actual_action_steps': 25,
        'optimizer': 'common-state AdamW, constant LR5e-5, WD1e-3, clip1, bf16',
        'long_objective': 'native all3 anchor MSE + .5*linear-weighted 3-future MSE + .09 six-frame SIGReg',
        'one_step_objective': 'native all3 anchor MSE + .09 first-four-frame SIGReg',
        'scope': 'single exploratory seed; gradient steps matched, not wall-clock; no reachability head',
        'initial_hdf5_read_seconds': io,
        'optimizer_source_step_counts': dict(Counter(v for _, v in source_steps))})
    dump(out/'config.json', config)
    (out/'objective_matrix_used.py').write_text(Path(__file__).read_text())
    (out/'rcaux_jepa_used.py').write_text(RC_SOURCE.read_text())
    anchors = np.load(Path(args.base_run)/'eval_anchors.npz')
    results = []
    for policy in config['data_policies']:
        for objective in config['objectives']:
            dest = out/f'{policy}_{objective}'
            dest.mkdir(exist_ok=False)
            torch.manual_seed(51000+args.seed)
            rng = np.random.default_rng(52000+args.seed)
            model = architecture(state['config']).cuda()
            model.load_state_dict(state['state_dict'], strict=True)
            dump(dest/'rollout_control.json', check_rollout(model, cache, controls, mean, std))
            optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3)
            # AdamW CPU step tensors are otherwise shared and increment the
            # common checkpoint state when sequential methods call step().
            optimizer.load_state_dict(copy.deepcopy(state['optimizer']))
            begin_steps = optimizer_steps(optimizer.state_dict())
            if begin_steps != source_steps or optimizer_steps(state['optimizer']) != source_steps:
                raise ValueError('Method optimizer must begin at the immutable source steps')
            step_counts = {'source': dict(Counter(v for _, v in source_steps)),
                'begin': dict(Counter(v for _, v in begin_steps)), 'parameter_states': len(source_steps)}
            dump(dest/'optimizer_steps.json', step_counts)
            sigreg = SIGReg(knots=17, num_proj=1024).cuda()
            model.train().requires_grad_(True)
            log = []
            torch.cuda.reset_peak_memory_stats()
            begin = now()
            actual_steps = 0
            for step in range(args.steps):
                ix = rng.choice(starts, 128, replace=True)
                image_batch = cache[ix[:, None]+np.arange(0, 26, 5)].copy()
                action_batch = controls[ix[:, None]+np.arange(25)].copy()
                bi = rng.integers(0, len(ledger), 13)
                if policy == 'UNIFORM':
                    image_batch[:13] = branch_pixels[bi]
                    action_batch[:13] = branch_actions[bi]
                p = pixels(image_batch)
                a = torch.tensor((action_batch-mean)/std, device='cuda').float().reshape(128, 5, 10)
                optimizer.zero_grad(set_to_none=True)
                with torch.autocast('cuda', dtype=torch.bfloat16):
                    encoded = model.encode({'pixels': p, 'action': a})
                    emb, act = encoded['emb'], encoded['act_emb']
                    anchor_prediction = model.predict(emb[:, :3], act[:, :3])
                    anchor_loss = (anchor_prediction-emb[:, 1:4]).square().mean()
                    long_loss = emb.new_zeros(())
                    if objective != 'ONE-STEP':
                        predicted = future_predictions(model, emb, act, objective == 'OPEN-LONG')
                        step_loss = (predicted-emb[:, 3:6]).square().mean(dim=(0, 2))
                        long_loss = (step_loss*emb.new_tensor([1/6, 2/6, 3/6])).sum()
                    reg = sigreg(emb[:, :4 if objective == 'ONE-STEP' else 6].transpose(0, 1))
                    loss = anchor_loss+.5*long_loss+.09*reg
                if not torch.isfinite(loss):
                    raise ValueError('Nonfinite objective-matrix loss')
                loss.backward()
                grad = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                if not torch.isfinite(grad):
                    raise ValueError('Nonfinite gradient')
                optimizer.step()
                actual_steps += 1
                if step % 100 == 0 or step == args.steps-1:
                    row = {'step': step, 'anchor_mse': float(anchor_loss), 'long_mse': float(long_loss),
                           'sigreg': float(reg), 'loss': float(loss), 'unclipped_gradient_norm': float(grad)}
                    log.append(row)
                    dump(dest/'training.json', log)
                    print(policy, objective, row, flush=True)
            end_steps = optimizer_steps(optimizer.state_dict())
            if optimizer_steps(state['optimizer']) != source_steps:
                raise ValueError('Method training mutated the common optimizer source steps')
            if end_steps != tuple((key, value+actual_steps) for key, value in begin_steps):
                raise ValueError('Method optimizer end steps do not equal begin plus actual updates')
            step_counts.update({'end': dict(Counter(v for _, v in end_steps)),
                'actual_updates': actual_steps, 'source_unchanged': True})
            dump(dest/'optimizer_steps.json', step_counts)
            ckpt = Path(args.model_cache)/f'E16_{policy}_{objective}_seed{args.seed}.pt'
            ckpt.parent.mkdir(parents=True, exist_ok=True)
            torch.save({'state_dict': model.state_dict(), 'config': state['config'], 'manifest': manifest,
                        'policy': policy, 'objective': objective}, ckpt)
            train = {'steps': args.steps, 'seconds': now()-begin, 'checkpoint': str(ckpt), 'sha256': digest(ckpt),
                     'predictor_calls_per_train_step': 1 if objective == 'ONE-STEP' else 4,
                     'peak_vram_gib': torch.cuda.max_memory_allocated()/2**30,
                     'optimizer_step_counts': step_counts}
            dump(dest/'train_summary.json', train)
            rows = evaluate(model, anchors, mean, std, dest, 'evaluation', 48, args.seed)
            dump(dest/'complete.json', {'completed': True})
            results.append({'policy': policy, 'objective': objective, 'successes': sum(r['success'] for r in rows),
                            'n': 48, 'training': train})
            dump(out/'summary.json', results)
            del model, optimizer, sigreg
            torch.cuda.empty_cache()
    dump(out/'complete.json', {'completed': True, 'methods': len(results)})
    durable = Path('/home/xiang/.cache/latent-wm-results')/out.name
    shutil.copytree(out, durable)
    print('durable_results', durable, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['dataset', 'checkpoint', 'bank', 'base-run', 'model-cache', 'output']:
        p.add_argument('--'+name, required=True)
    p.add_argument('--steps', type=int, default=600)
    p.add_argument('--seed', type=int, default=0)
    args = p.parse_args()
    try:
        run(args)
    except Exception as error:
        out = Path(args.output)
        if out.exists():
            dump(out/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
