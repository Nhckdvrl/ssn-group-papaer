"""E17 baseline: frozen Fast WM, future-relabelled GCBC, native CEM init_action.

Released WM pretraining is unchanged. Held-out means whole proposal-training
source episodes, not unseen task families. No GPU experiment before E17 lock.
"""
import argparse
import inspect
import importlib.metadata
import json
from pathlib import Path
import shutil
import time
import h5py
import hdf5plugin
import numpy as np
import torch
from first_wave import image_tensor, native_info, restore, sha256, sync_time, write_json
from recovery_forks import MacroCost, controls, task_distance
from closed_loop import wilson


class Proposal(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(torch.nn.Linear(384, 256), torch.nn.ReLU(),
            torch.nn.Linear(256, 256), torch.nn.ReLU(), torch.nn.Linear(256, 50))

    def forward(self, state, goal):
        return self.net(torch.cat([state, goal], -1)).reshape(-1, 1, 50)


@torch.inference_mode()
def encode(model, images):
    chunks = []
    for start in range(0, len(images), 128):
        z = model.encode({'pixels': image_tensor(images[start:start+128]).unsqueeze(1).cuda()})['emb']
        chunks.append(z[:, -1].detach().cpu())
    return torch.cat(chunks)


def training(args, cfg, source, model, norm, data, out):
    task = cfg['task']; begin = time.perf_counter(); features, targets, pairs = [], [], []; offset = 0
    excluded = set(np.load(source/'anchors.npz')['episodes'].tolist())
    excluded.update(int(ep) for a in data.values() for ep in (a['episode'][:args.count] if task == 'tworoom' else a['episode']))
    with h5py.File(cfg['dataset']) as f:
        if task == 'tworoom':
            base = json.loads((Path(args.base_run)/'data_manifest.json').read_text())['base_episodes']
        else:
            valid = np.setdiff1d(np.flatnonzero(f['ep_len'][:] > 76), list(excluded))
            base = np.random.default_rng(68000).choice(valid, 100, replace=False).tolist()
        if len(base) != 100 or excluded.intersection(base): raise ValueError('Base100/evaluation episode overlap')
        for ep in sorted(base):
            start, n = int(f['ep_offset'][ep]), int(f['ep_len'][ep])
            z = encode(model, f['pixels'][start:start+n]); features.append(z)
            a = (f['action'][start:start+n]-norm['mean'])/norm['std']; targets.append(a)
            for h in range(25, 76, 5):
                pairs.extend([offset+t, offset+t+h, h] for t in range(n-h))
            offset += n
    z = torch.cat(features); a = torch.tensor(np.concatenate(targets), dtype=torch.float32)
    pairs = torch.tensor(pairs, dtype=torch.long)
    if not len(pairs): raise ValueError('No complete future-labelled action chunks')
    torch.save({'latent': z, 'pairs': pairs, 'encoder_frozen': True, 'wm_sha256': sha256(cfg['checkpoint'])}, out/f'{task}_frozen_features.pt')
    x, g = z[pairs[:, 0]].cuda(), z[pairs[:, 1]].cuda()
    y = a[pairs[:, 0, None]+torch.arange(25)].flatten(1).cuda()
    torch.manual_seed(args.seed); net = Proposal().cuda()
    optimizer = torch.optim.AdamW(net.parameters(), lr=3e-4, weight_decay=1e-3)
    generator = torch.Generator().manual_seed(args.seed); losses = []; start = sync_time()
    for step in range(args.updates):
        ids = torch.randint(len(pairs), (128,), generator=generator).cuda()
        optimizer.zero_grad(set_to_none=True); prediction = net(x[ids], g[ids]).flatten(1)
        loss = (prediction-y[ids]).square().mean()
        if not torch.isfinite(loss): raise ValueError('Nonfinite proposal loss')
        loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.); optimizer.step()
        losses.append(float(loss.detach()))
    net.eval().requires_grad_(False); path = Path(args.model_cache)/f'{task}_query_proposal_s{args.seed}.pt'
    if path.exists(): raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True); torch.save(net.state_dict(), path)
    write_json(out/f'{task}_train.json', {'checkpoint': path, 'sha256': sha256(path), 'pair_count': len(pairs),
        'base_episodes': base, 'excluded_episodes': sorted(excluded), 'selection_seed': 68000 if task == 'pusht' else 'E16 inherited', 'updates': args.updates, 'batch_size': 128,
        'parameters': sum(p.numel() for p in net.parameters()), 'train_seconds': sync_time()-start,
        'total_prepare_train_seconds': time.perf_counter()-begin, 'encoded_frames': len(z),
        'encoder_calls': sum((len(v)+127)//128 for v in features), 'losses': losses,
        'label': 'all same-episode future offsets25:5:75; next25 normalized actions; no padding',
        'query_input': 'current192+goal192 frozen latent only; no goal offset/deadline/oracle distance'})
    return net


@torch.inference_mode()
def plan(model, initial, goal, env, n, seed, proposal=None):
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    cost = MacroCost(model, initial, goal)
    solver = swm.solver.CEMSolver(cost, batch_size=1, num_samples=n, topk=30, n_steps=30, device='cuda', seed=seed)
    solver.configure(action_space=batch_space(env.action_space, 1), n_envs=1,
        config=swm.PlanConfig(horizon=1, receding_horizon=1, action_block=25, warm_start=True))
    start = sync_time(); result = solver.solve({}, init_action=proposal)
    return result['actions'].numpy(), {'seconds': sync_time()-start, 'cost_calls': cost.calls,
        'candidate_evaluations': n*cost.calls, 'predicted_macro_transitions': n*cost.calls}


def execute(env, action, norm):
    success = False; steps = 0
    for a in action.reshape(25, 2)*norm['std']+norm['mean']:
        _, _, done, truncated, _ = env.step(a); steps += 1
        if done or truncated: success = bool(done); break
    return success, steps


@torch.inference_mode()
def evaluation(args, cfg, model, net, norm, data, out):
    import gymnasium as gym
    import stable_worldmodel
    task = cfg['task']; env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
    methods = ['ZERO300', 'ZERO900', 'PROPOSAL300', 'GOAL-SHUFFLED300', 'GCBC-direct']; rows = []; physical = 0
    rng = np.random.default_rng(args.seed+901)
    for horizon, anchors in data.items():
        for j in range(args.count):
            anchor = {k: anchors[k][j] for k in anchors.files}; reset_seed = args.seed+j
            restore(env, anchor, reset_seed); start = sync_time()
            goal = encode(model, anchor['goal_pixels'][None]).cuda().unsqueeze(1)
            shuffled = encode(model, anchors['goal_pixels'][(j+1) % args.count][None]).cuda().unsqueeze(1)
            goal_encoding_seconds = sync_time()-start
            if horizon == 25 and j == 0:
                info = native_info(env.render(), anchor['goal_pixels']); initial = encode(model, env.render()[None]).cuda().unsqueeze(1)
                write_json(out/f'{task}_native_control.json', controls(model, info, initial, goal))
            for method in rng.permutation(methods):
                restore(env, anchor, reset_seed); success = False; steps = 0; searches = []; start = sync_time()
                for decision in range(2*horizon//25):
                    begin = sync_time(); initial = encode(model, env.render()[None]).cuda().unsqueeze(1)
                    encoding_seconds = sync_time()-begin; init = None; prior_seconds = 0.
                    if method in ['PROPOSAL300', 'GOAL-SHUFFLED300', 'GCBC-direct']:
                        begin = sync_time(); init = net(initial[:, -1], (shuffled if method == 'GOAL-SHUFFLED300' else goal)[:, -1]); prior_seconds = sync_time()-begin
                    if method == 'GCBC-direct':
                        action = init.cpu().numpy(); search = {'seconds': 0., 'cost_calls': 0, 'candidate_evaluations': 0, 'predicted_macro_transitions': 0}
                    else:
                        action, search = plan(model, initial, goal, env, 900 if method == 'ZERO900' else 300,
                            args.seed+j*100+decision, init)
                    search.update({'current_encoding_seconds': encoding_seconds, 'proposal_seconds': prior_seconds,
                        'proposal_calls': int(init is not None)}); searches.append(search)
                    success, used = execute(env, action, norm); steps += used; physical += used
                    if success or used < 25: break
                rows.append({'task': task, 'anchor': j, 'episode': int(anchor['episode']), 'goal_offset': horizon,
                    'method': method, 'success': success, 'steps': steps, 'native_task_distance': task_distance(env, task),
                    'episode_seconds': sync_time()-start, 'goal_and_shuffled_encoding_seconds': goal_encoding_seconds,
                    'searches': searches}); write_json(out/f'{task}_rows.json', rows)
            print('query_proposal', task, horizon, j, flush=True)
    env.close(); summary = []
    for horizon in [25, 75]:
        base = [r for r in rows if r['goal_offset'] == horizon and r['method'] == 'ZERO900']
        boot = np.random.default_rng(args.seed+8000).integers(0, len(base), (2000, len(base)))
        for method in methods:
            group = [r for r in rows if r['goal_offset'] == horizon and r['method'] == method]
            delta = np.array([int(a['success'])-int(b['success']) for a, b in zip(group, base)])
            s = sum(r['success'] for r in group)
            summary.append({'task': task, 'goal_offset': horizon, 'method': method, 'n': len(group), 'successes': s,
                'wilson95': wilson(s, len(group)), 'paired_gain_vs_ZERO900': float(delta.mean()),
                'paired_ci95': np.quantile(delta[boot].mean(1), [.025, .975]), 'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0))})
            direct = [r for r in rows if r['goal_offset'] == horizon and r['method'] == 'GCBC-direct']
            delta_direct = np.array([int(a['success'])-int(b['success']) for a, b in zip(group, direct)])
            summary[-1].update({'paired_gain_vs_GCBC': float(delta_direct.mean()),
                'paired_ci95_vs_GCBC': np.quantile(delta_direct[boot].mean(1), [.025, .975]),
                'helped_vs_GCBC': int(sum(delta_direct > 0)), 'harmed_vs_GCBC': int(sum(delta_direct < 0))})
    write_json(out/f'{task}_summary.json', summary)
    return len(rows), physical


def run(args):
    if args.count < 2 or args.count > 16: raise ValueError('Pilot needs 2..16 locked anchors per range')
    import stable_worldmodel as swm
    if importlib.metadata.version('stable-worldmodel') != '0.0.6': raise ValueError('Requires locked native CEM0.0.6')
    torch.set_num_threads(4); torch.manual_seed(args.seed)
    if not Path(args.model_cache).resolve().is_relative_to(Path('/home/xiang/.cache/huggingface')):
        raise ValueError('Proposal checkpoints must remain in the HF cache')
    out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'harness_sha256': sha256(__file__),
        'cem_source_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)), 'hardware': torch.cuda.get_device_name(),
        'helper_sha256': {n: sha256(Path(__file__).with_name(n)) for n in ['first_wave.py', 'recovery_forks.py']},
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text()),
        'normalization': 'source full-dataset stats used by released Fast/native baseline; all methods identical',
        'query_reuse': 'whole episodes held out from proposal training; g25/g75 goal relabel range25..75; no deadline input',
        'limitations': 'released WM may have seen evaluation data; no unseen task-family claim; one proposal training seed'})
    for name in ['query_proposal.py', 'first_wave.py', 'recovery_forks.py']:
        (out/name.replace('.py', '_used.py')).write_text(Path(__file__).with_name(name).read_text())
    episodes = 0; physical = 0
    for source_path, cfg in zip(args.sources, cfgs):
        source = Path(source_path); task = cfg['task']
        model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        norm = dict(np.load(source/'action_normalization.npz'))
        data = {h: np.load(Path(args.prepared)/f'{task}_g{h}.npz') for h in [25, 75]}
        write_json(out/f'{task}_inputs.json', {'wm_sha256': sha256(cfg['checkpoint']), 'normalization': norm,
            'anchors_sha256': {h: sha256(Path(args.prepared)/f'{task}_g{h}.npz') for h in data},
            'locked_evaluation_episodes': {h: data[h]['episode'][:args.count] for h in data},
            'shuffled_goal_indices': [(j+1) % args.count for j in range(args.count)]})
        net = training(args, cfg, source, model, norm, data, out)
        count, steps = evaluation(args, cfg, model, net, norm, data, out); episodes += count; physical += steps
        del model, net; torch.cuda.empty_cache()
    write_json(out/'complete.json', {'completed': True, 'episodes': episodes, 'physical_env_steps': physical})
    shutil.copytree(out, Path('/home/xiang/.cache/latent-wm-results')/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs='+', required=True)
    for name in ['prepared', 'base-run', 'model-cache', 'output']: p.add_argument('--'+name, required=True)
    p.add_argument('--seed', type=int, default=91000); p.add_argument('--updates', type=int, default=2000)
    p.add_argument('--count', type=int, default=16); args = p.parse_args()
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
