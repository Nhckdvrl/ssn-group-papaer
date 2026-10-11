"""E17: demonstrated continuation costs on real/imagined endpoints; frozen Fast WM."""
import argparse
import copy
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import shutil
import h5py
import hdf5plugin
import numpy as np
import torch
from first_wave import native_info, restore, sha256, sync_time, write_json
from recovery_forks import MacroCost, controls, task_distance
from query_proposal import encode
from closed_loop import wilson

SEED = 68000
HEADS = ['REAL', 'WM-CALIBRATED', 'MIXED']
METHODS = ['EXEC-L2', 'EXEC-COS']+HEADS


def executed_actions(actions, task, norm):
    if task == 'pusht': return actions
    if task != 'tworoom': raise ValueError(task)
    mean = torch.as_tensor(norm['mean'], device=actions.device, dtype=actions.dtype)
    std = torch.as_tensor(norm['std'], device=actions.device, dtype=actions.dtype)
    physical = actions.reshape(-1, 2)*std+mean
    return ((physical.clamp(-1., 1.)-mean)/std).reshape(actions.shape)


class Head(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(torch.nn.Linear(384, 256), torch.nn.ReLU(),
            torch.nn.Linear(256, 256), torch.nn.ReLU(), torch.nn.Linear(256, 1), torch.nn.Softplus())
    def forward(self, state, goal): return self.net(torch.cat([state, goal], -1)).squeeze(-1)


class Cost(MacroCost):
    def __init__(self, model, initial, goal, method, task, norm, head=None):
        super().__init__(model, initial, goal); self.method, self.head, self.task, self.norm = method, head, task, norm
    def get_cost(self, info, actions):
        if self.method == 'NATIVE-L2': return super().get_cost(info, actions)
        actions = executed_actions(actions, self.task, self.norm)
        if self.method == 'EXEC-L2': return super().get_cost(info, actions)
        z = self.terminal(actions); goal = self.goal[:, -1:].expand_as(z); self.calls += 1
        if self.method == 'EXEC-COS': return 1-torch.nn.functional.cosine_similarity(z, goal, dim=-1)
        return self.head(z, goal)


@torch.inference_mode()
def predicted_endpoints(model, z, actions, task, norm):
    output = []
    for i in range(0, len(z), 128):
        initial = z[i:i+128].cuda().unsqueeze(1)
        action = torch.as_tensor(actions[i:i+128], device='cuda', dtype=torch.float32).reshape(-1, 1, 1, 50)
        action = executed_actions(action, task, norm)
        output.append(MacroCost(model, initial, initial).terminal(action)[:, 0].cpu())
    return torch.cat(output)


def train_heads(args, cfg, model, norm, out):
    task = cfg['task']; old = Path(args.e17_run); cache = Path(args.model_cache)
    feature_path = old/f'{task}_frozen_features.pt'; features = torch.load(feature_path, map_location='cpu', weights_only=False)
    assert features['encoder_frozen'] and features['wm_sha256'] == sha256(cfg['checkpoint'])
    z, pairs = features['latent'], features['pairs']; info = json.loads((old/f'{task}_train.json').read_text())
    assert pairs.shape[1] == 3 and torch.equal(pairs[:, 1]-pairs[:, 0], pairs[:, 2])
    assert torch.all((pairs[:, 2] >= 25) & (pairs[:, 2] <= 75) & (pairs[:, 2] % 5 == 0))
    action_rows = []; boundaries = [0]
    with h5py.File(cfg['dataset']) as f:
        lengths, offsets = f['ep_len'][:], f['ep_offset'][:]
        for ep in sorted(info['base_episodes']):
            start, n = int(offsets[ep]), int(lengths[ep]); action_rows.append(f['action'][start:start+n]); boundaries.append(boundaries[-1]+n)
    assert len(info['base_episodes']) == 100 and boundaries[-1] == len(z)
    p = pairs.numpy(); assert np.array_equal(np.searchsorted(boundaries, p[:, 0], side='right'), np.searchsorted(boundaries, p[:, 1], side='right'))
    controls_array = (np.concatenate(action_rows)-norm['mean'])/norm['std']
    starts, inverse = torch.unique(pairs[:, 0], sorted=True, return_inverse=True)
    actions = controls_array[starts.numpy()[:, None]+np.arange(25)]
    assert np.isfinite(actions).all() and torch.isfinite(z).all()
    begin = sync_time(); imagined = predicted_endpoints(model, z[starts], actions, task, norm)
    real = z[pairs[:, 0]+25]; imagined_pairs = imagined[inverse]; goal = z[pairs[:, 1]]; target = (pairs[:, 2].float()-25)/50
    feature_cache = cache/f'{task}_continuation_features.pt'
    torch.save({'latent': z, 'pairs': pairs, 'unique_starts': starts, 'imagined_endpoint': imagined,
                'encoder_frozen': True, 'wm_sha256': features['wm_sha256']}, feature_cache)
    prepare_seconds = sync_time()-begin
    torch.manual_seed(SEED); initial = copy.deepcopy(Head().state_dict()); initial_path = cache/f'{task}_head_initial.pt'; torch.save(initial, initial_path)
    ids = torch.randint(len(pairs), (2000, 128), generator=torch.Generator().manual_seed(SEED))
    common = {'base_episodes': info['base_episodes'], 'pair_count': len(pairs), 'unique_model_endpoints': len(starts),
        'original_feature_sha256': sha256(feature_path), 'feature_cache_sha256': sha256(feature_cache),
        'initial_sha256': sha256(initial_path), 'batch_ids_sha256': hashlib.sha256(ids.numpy().tobytes()).hexdigest(),
        'updates': 2000, 'pair_batch_size': 128, 'lr': 3e-4, 'weight_decay': 1e-3, 'clip': 1.,
        'target': '(expert future offset h-25)/50; demonstrated remaining, not minimum reachability',
        'feature_prepare_seconds': prepare_seconds, 'normalization': norm,
        'model_action_transform': 'physical clip[-1,1] for TwoRoom; identity for PushT'}
    real, imagined_pairs, goal, target = [x.cuda() for x in [real, imagined_pairs, goal, target]]
    heads = {}; records = {}
    for method in HEADS:
        head = Head(); head.load_state_dict(copy.deepcopy(initial)); assert all(torch.equal(head.state_dict()[k], v) for k, v in initial.items())
        head = head.cuda(); optimizer = torch.optim.AdamW(head.parameters(), lr=3e-4, weight_decay=1e-3); assert not optimizer.state
        losses = []; begin = sync_time()
        for batch in ids:
            batch = batch.cuda(); optimizer.zero_grad(set_to_none=True)
            inputs = [real] if method == 'REAL' else [imagined_pairs] if method == 'WM-CALIBRATED' else [real, imagined_pairs]
            loss = torch.stack([(head(x[batch], goal[batch])-target[batch]).square().mean() for x in inputs]).mean()
            if not torch.isfinite(loss): raise ValueError(f'Nonfinite {method} loss')
            loss.backward(); assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in head.parameters())
            torch.nn.utils.clip_grad_norm_(head.parameters(), 1.); optimizer.step(); losses.append(float(loss.detach()))
        assert all(int(s['step']) == 2000 for s in optimizer.state.values())
        head.eval().requires_grad_(False); checkpoint = cache/f'{task}_{method}.pt'; torch.save(head.state_dict(), checkpoint)
        heads[method] = head; records[method] = dict(common, checkpoint=str(checkpoint), checkpoint_sha256=sha256(checkpoint),
            parameters=sum(p.numel() for p in head.parameters()), training_seconds=sync_time()-begin, losses=losses)
        with torch.inference_mode():
            records[method]['last_batch_scores'] = {domain: {'mean': float(v.mean()), 'variance': float(v.var(unbiased=False))}
                for domain, x in [('real', real), ('imagined', imagined_pairs)] for v in [head(x[batch], goal[batch])]}
    write_json(out/f'{task}_training.json', records)
    return heads, set(info['base_episodes'])


@torch.inference_mode()
def heldout_audit(cfg, model, norm, data, heads, out):
    images, goals, actions, horizons = [], [], [], []
    with h5py.File(cfg['dataset']) as f:
        offsets = f['ep_offset'][:]
        for h, anchors in data.items():
            for j in range(16):
                row = int(offsets[int(anchors['episode'][j])])+int(anchors['start'][j])
                images.extend([f['pixels'][row], f['pixels'][row+25]]); goals.append(anchors['goal_pixels'][j])
                actions.append(f['action'][row:row+25]); horizons.append(h)
    z = encode(model, np.asarray(images)); goal = encode(model, np.asarray(goals)).cuda()
    predicted = predicted_endpoints(model, z[::2], (np.asarray(actions)-norm['mean'])/norm['std'], cfg['task'], norm).cuda()
    real = z[1::2].cuda(); target = torch.tensor((np.asarray(horizons)-25)/50, device='cuda'); results = []
    for h in [25, 75]:
        ix = np.flatnonzero(np.asarray(horizons) == h)
        for method, head in heads.items():
            for domain, endpoint in [('real', real), ('imagined', predicted)]:
                score = head(endpoint[ix], goal[ix]); assert torch.isfinite(score).all()
                results.append({'goal_offset': h, 'head': method, 'input_domain': domain, 'n': 16,
                    'mean': float(score.mean()), 'variance': float(score.var(unbiased=False)),
                    'rmse_demonstrated_remaining': float((score-target[ix]).square().mean().sqrt())})
    write_json(out/f'{cfg["task"]}_heldout_factual_audit.json', {'scope': 'offline source factual25, no environment execution or controller supervision', 'results': results})


@torch.inference_mode()
def evaluate_task(args, cfg, model, norm, heads, training_episodes, out):
    import gymnasium as gym
    from action_basis import solver
    task = cfg['task']; data = {h: np.load(Path(args.prepared)/f'{task}_g{h}.npz') for h in [25, 75]}
    assert not training_episodes & {int(ep) for a in data.values() for ep in a['episode'][:16]}
    heldout_audit(cfg, model, norm, data, heads, out)
    env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
    methods = (['NATIVE-L2'] if task == 'tworoom' else [])+METHODS
    rows = []; order = np.random.default_rng(SEED+901)
    for h, anchors in data.items():
        for j in range(16):
            anchor = {k: anchors[k][j] for k in anchors.files}; restore(env, anchor, SEED+j)
            goal = encode(model, anchor['goal_pixels'][None]).cuda().unsqueeze(1)
            if h == 25 and j == 0:
                initial = encode(model, env.render()[None]).cuda().unsqueeze(1)
                write_json(out/f'{task}_native_control.json', controls(model, native_info(env.render(), anchor['goal_pixels']), initial, goal))
            for method in order.permutation(methods):
                restore(env, anchor, SEED+j); success = False; steps = 0; searches = []
                for decision in range(2*h//25):
                    begin = sync_time(); initial = encode(model, env.render()[None]).cuda().unsqueeze(1)
                    cost = Cost(model, initial, goal, method, task, norm, heads.get(method)); cem = solver(cost, env.action_space, 25, 300, SEED+j*100+decision, 'cuda')
                    action = cem.solve({})['actions'].numpy().reshape(25, 2)*norm['std']+norm['mean']
                    searches.append({'seconds_with_encode': sync_time()-begin, 'cost_calls': cost.calls, 'candidate_evaluations': 300*cost.calls})
                    for command in action:
                        _, _, done, truncated, _ = env.step(command); steps += 1
                        if done or truncated: success = bool(done); break
                    if done or truncated: break
                rows.append({'task': task, 'goal_offset': h, 'anchor': j, 'method': method, 'episode': int(anchor['episode']),
                    'success': success, 'env_steps': steps, 'native_task_distance': task_distance(env, task), 'searches': searches})
                write_json(out/f'{task}_rows.json', rows); print('continuation_cost', task, h, j, method, success, flush=True)
    env.close(); old_rows = json.loads((Path(args.e17_run)/f'{task}_rows.json').read_text()); reproduction = []
    for r in [r for r in rows if r['method'] == ('NATIVE-L2' if task == 'tworoom' else 'EXEC-L2')]:
        prior = next(x for x in old_rows if x['method'] == 'ZERO300' and x['anchor'] == r['anchor'] and x['goal_offset'] == r['goal_offset'])
        reproduction.append({'goal_offset': r['goal_offset'], 'anchor': r['anchor'], 'success_equal': r['success'] == prior['success'], 'steps_equal': r['env_steps'] == prior['steps']})
    write_json(out/f'{task}_native_l2_reproduction.json', reproduction)
    return rows


def summary(rows):
    results = []; boot = np.random.default_rng(SEED+8000).integers(0, 16, (2000, 16))
    for task in ['tworoom', 'pusht']:
        for h in [25, 75]:
            group = [r for r in rows if r['task'] == task and r['goal_offset'] == h]; base = {r['anchor']: r for r in group if r['method'] == 'EXEC-L2'}
            for method in (['NATIVE-L2'] if task == 'tworoom' else [])+METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor']); s = sum(r['success'] for r in rr)
                delta = np.array([int(r['success'])-int(base[r['anchor']]['success']) for r in rr]); utility = np.array([base[r['anchor']]['native_task_distance']-r['native_task_distance'] for r in rr])
                results.append({'task': task, 'goal_offset': h, 'method': method, 'n': 16, 'successes': s, 'wilson95': wilson(s, 16),
                    'paired_success_gain': float(delta.mean()), 'paired_success_ci95': np.quantile(delta[boot].mean(1), [.025, .975]),
                    'paired_distance_gain': float(utility.mean()), 'paired_distance_ci95': np.quantile(utility[boot].mean(1), [.025, .975]),
                    'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0))})
    return results


def run(args):
    import stable_worldmodel as swm
    assert importlib.metadata.version('stable-worldmodel') == '0.0.6'
    torch.set_num_threads(4); out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    cache = Path(args.model_cache); assert cache.resolve().is_relative_to(Path('/home/xiang/.cache/huggingface')); cache.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]; assert sorted(c['task'] for c in cfgs) == ['pusht', 'tworoom']
    e17 = json.loads((Path(args.e17_run)/'config.json').read_text()); assert e17['args']['seed'] == SEED and e17['sources'] == cfgs
    assert (Path(args.e17_run)/'complete.json').exists()
    helpers = ['first_wave.py', 'recovery_forks.py', 'query_proposal.py', 'action_basis.py', 'closed_loop.py']
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'seed': SEED, 'methods': METHODS, 'updates': 2000, 'head': '384-256-256-1/ReLU/Softplus',
        'cem': 'native H25/N300/K30/30, execute25, no proposal', 'label': 'expert (h-25)/50, h25:5:75; not minimum reachability',
        'tworoom_extra_method': 'NATIVE-L2 reproduces E17 raw-action scoring; all main methods score executed physical clip[-1,1]',
        'pusht_transform': 'identity; no physical clamp', 'issued_actions': 'unaltered CEM output denormalized; native environment executes it',
        'source_sha256': {c['task']: {'wm': sha256(c['checkpoint']), 'norm': sha256(Path(s)/'action_normalization.npz')} for s, c in zip(args.sources, cfgs)},
        'harness_sha256': sha256(__file__), 'cem_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)),
        'helpers': {n: sha256(Path(__file__).with_name(n)) for n in helpers}, 'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text()),
        'scope': 'frozen WM and encoder; same 100 episodes/pairs/batchids/init; MIXED averages two input losses per update; WM pretraining overlap unknown'})
    for name in ['continuation_cost.py']+helpers: shutil.copy2(Path(__file__).with_name(name), out/name.replace('.py', '_used.py'))
    rows = []
    for source, cfg in zip(args.sources, cfgs):
        model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False); norm = dict(np.load(Path(source)/'action_normalization.npz'))
        old_inputs = json.loads((Path(args.e17_run)/f'{cfg["task"]}_inputs.json').read_text())
        assert all(np.array_equal(norm[k], old_inputs['normalization'][k]) for k in ['mean', 'std'])
        assert all(sha256(Path(args.prepared)/f'{cfg["task"]}_g{h}.npz') == old_inputs['anchors_sha256'][str(h)] for h in [25, 75])
        heads, episodes = train_heads(args, cfg, model, norm, out); assert all(not p.requires_grad for p in model.parameters())
        rows.extend(evaluate_task(args, cfg, model, norm, heads, episodes, out)); del model, heads; torch.cuda.empty_cache()
    write_json(out/'summary.json', summary(rows)); write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': sum(r['env_steps'] for r in rows)})
    shutil.copytree(out, Path('/home/xiang/.cache/latent-wm-results')/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs=2, required=True)
    for name in ['prepared', 'e17-run', 'model-cache', 'output']: p.add_argument('--'+name, required=True)
    args = p.parse_args()
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
