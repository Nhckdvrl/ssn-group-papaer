"""E17 supervised observable geometry: frozen WM, reusable image-goal cost, aligned EX5."""
import argparse, copy, hashlib, importlib.metadata, inspect, json, shutil
from pathlib import Path
import h5py, hdf5plugin
import numpy as np
import torch
from first_wave import native_info, restore, sha256, simulator_state, sync_time, write_json
from recovery_forks import MacroCost, controls, task_distance
from query_proposal import encode, plan
from latent_observer import PrefixCost, prefix_control, plan_prefix
from commitment_cadence import shift_prior
from action_basis import solver
from closed_loop import wilson

SEED = 78000
METHODS = ['NATIVE25', 'PREFIX5', 'REAL-GEO', 'MIX-GEO', 'REAL-JOINT', 'MIX-JOINT']
EXTENT = {'tworoom': 224., 'pusht': 512.}

def geometry(state, task):
    state = torch.as_tensor(state, dtype=torch.float32)
    if task == 'tworoom': return state[..., :2]/EXTENT[task]
    return torch.cat([state[..., :4]/EXTENT[task], state[..., 4:5].sin(), state[..., 4:5].cos()], -1)

def metric(prediction, goal, task, weights=(1., 1., 1.)):
    radius = 16. if task == 'tworoom' else 20.
    d = (prediction-goal)*EXTENT[task]/radius
    cost = weights[0]*d[..., :2].square().sum(-1)
    if task == 'pusht':
        cost = cost+weights[1]*d[..., 2:4].square().sum(-1)
        cost = cost+weights[2]*(prediction[..., 4:]-goal[..., 4:]).square().sum(-1)/(2*(1-np.cos(np.pi/9)))
    return cost

class Decoder(torch.nn.Module):
    def __init__(self, task):
        super().__init__(); self.net = torch.nn.Sequential(torch.nn.Linear(192, 256), torch.nn.ReLU(),
            torch.nn.Linear(256, 256), torch.nn.ReLU(), torch.nn.Linear(256, 2 if task == 'tworoom' else 6))
    def forward(self, z): return self.net(z)

class FactorCost(PrefixCost):
    def __init__(self, model, initial, goal, head, task, joint):
        super().__init__(model, initial, goal); self.head, self.task, self.joint = head, task, joint
        self.goal_geometry = head(goal[:, -1:])
    def get_cost(self, info, actions):
        z = self.terminal(actions); self.calls += 1
        score = metric(self.head(z), self.goal_geometry, self.task)
        if self.joint: score = score+(z-self.goal[:, -1:]).square().mean(-1)
        return score

def source_features(args, cfg):
    task = cfg['task']; old = Path(args.e17_run); path = old/f'{task}_frozen_features.pt'
    features = torch.load(path, map_location='cpu', weights_only=False); info = json.loads((old/f'{task}_train.json').read_text())
    assert features['encoder_frozen'] and features['wm_sha256'] == sha256(cfg['checkpoint'])
    states, actions, rows, expected, boundary = [], [], [], [], [0]
    with h5py.File(cfg['dataset']) as f:
        for ep in sorted(info['base_episodes']):
            row, n = int(f['ep_offset'][ep]), int(f['ep_len'][ep]); offset = boundary[-1]
            assert np.all(f['ep_idx' if task == 'tworoom' else 'episode_idx'][row:row+n] == ep)
            assert np.array_equal(f['step_idx'][row:row+n], np.arange(n))
            s = f['pos_agent' if task == 'tworoom' else 'state'][row:row+n]
            assert np.array_equal(s[:, :2], f['proprio'][row:row+n, :2])
            states.append(s); actions.append(f['action'][row:row+n]); rows.extend(range(row, row+n)); boundary.append(offset+n)
            for h in range(25, 76, 5): expected.extend([offset+t, offset+t+h, h] for t in range(n-h))
    z, pairs = features['latent'], features['pairs']; assert len(info['base_episodes']) == 100 and len(z) == boundary[-1]
    assert torch.equal(pairs, torch.tensor(expected, dtype=torch.long)) and torch.isfinite(z).all()
    assert np.array_equal(np.searchsorted(boundary, pairs[:, 0]+5, side='right'), np.searchsorted(boundary, pairs[:, 1], side='right'))
    labels = geometry(np.concatenate(states), task); assert torch.isfinite(labels).all()
    return z, pairs, labels, np.concatenate(actions), set(info['base_episodes']), {'original_feature_sha256': sha256(path), 'row_mapping_sha256': hashlib.sha256(np.asarray(rows, dtype=np.int64).tobytes()).hexdigest(), 'geometry_sha256': hashlib.sha256(labels.numpy().tobytes()).hexdigest()}

def train(args, cfg, model, norm, out):
    task = cfg['task']; z, pairs, labels, actions, episodes, provenance = source_features(args, cfg)
    starts, inverse = torch.unique(pairs[:, 0], sorted=True, return_inverse=True); imagined = []; tick = sync_time()
    with torch.inference_mode():
        for i in range(0, len(starts), 128):
            ix = starts[i:i+128]; initial = z[ix].cuda().unsqueeze(1)
            a = torch.as_tensor((actions[ix[:, None]+np.arange(25)]-norm['mean'])/norm['std'], device='cuda').float().reshape(-1, 1, 1, 50)
            imagined.append(PrefixCost(model, initial, initial).terminal(a)[:, 0].cpu())
    imagined = torch.cat(imagined); cache = Path(args.model_cache); feature_path = cache/f'{task}_features.pt'
    torch.save({'pairs': pairs, 'starts': starts, 'imagined_prefix5': imagined, 'geometry': labels, 'provenance': provenance}, feature_path)
    prepare_seconds = sync_time()-tick; real, wm, goal, target, target_goal = [v.cuda() for v in [z[pairs[:, 0]+5], imagined[inverse], z[pairs[:, 1]], labels[pairs[:, 0]+5], labels[pairs[:, 1]]]]
    torch.manual_seed(SEED); initial = copy.deepcopy(Decoder(task).state_dict()); initial_path = cache/f'{task}_initial.pt'; torch.save(initial, initial_path)
    ids = torch.randint(len(pairs), (2000, 128), generator=torch.Generator().manual_seed(SEED)); heads, records = {}, {}
    for domain in ['REAL', 'MIX']:
        head = Decoder(task); head.load_state_dict(copy.deepcopy(initial)); head = head.cuda(); optimizer = torch.optim.AdamW(head.parameters(), lr=3e-4, weight_decay=1e-3)
        losses = []; tick = sync_time(); assert not optimizer.state
        for batch in ids:
            batch = batch.cuda(); optimizer.zero_grad(set_to_none=True)
            lreal = (head(real[batch])-target[batch]).square().mean(); lgoal = (head(goal[batch])-target_goal[batch]).square().mean()
            loss = .5*lreal+.5*lgoal if domain == 'REAL' else .25*lreal+.25*(head(wm[batch])-target[batch]).square().mean()+.5*lgoal
            assert torch.isfinite(loss); loss.backward(); assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in head.parameters())
            torch.nn.utils.clip_grad_norm_(head.parameters(), 1.); optimizer.step(); losses.append(float(loss.detach()))
        assert all(int(s['step']) == 2000 for s in optimizer.state.values()); head.eval().requires_grad_(False)
        checkpoint = cache/f'{task}_{domain}.pt'; torch.save(head.state_dict(), checkpoint); heads[domain] = head
        records[domain] = dict(provenance, checkpoint=str(checkpoint), checkpoint_sha256=sha256(checkpoint), losses=losses, training_seconds=sync_time()-tick,
            prepare_seconds=prepare_seconds, initial_sha256=sha256(initial_path), batch_ids_sha256=hashlib.sha256(ids.numpy().tobytes()).hexdigest(), parameters=sum(p.numel() for p in head.parameters()),
            base_episodes=sorted(episodes), pairs=len(pairs), feature_sha256=sha256(feature_path), updates=2000, extra_task_labels=True)
    write_json(out/f'{task}_training.json', records); assert all(not p.requires_grad for p in model.parameters())
    return heads, episodes

def auxiliary(env, task):
    state = np.asarray(simulator_state(env, env._get_info())); goal = np.asarray(env._get_info()['goal_state'] if task == 'tworoom' else env.goal_state)
    result = {'agent_position_error': float(np.linalg.norm(state[:2]-goal[:2]))}
    if task == 'pusht': result.update(block_position_error=float(np.linalg.norm(state[2:4]-goal[2:4])), wrapped_angle_error=float(abs(np.arctan2(np.sin(state[4]-goal[4]), np.cos(state[4]-goal[4])))))
    return result

@torch.inference_mode()
def evaluate(args, cfg, model, norm, heads, episodes, out):
    import gymnasium as gym
    task = cfg['task']; env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped; rows = []
    for h in [25, 75]:
        data = np.load(Path(args.prepared)/f'{task}_g{h}.npz'); assert not episodes & set(map(int, data['episode'][:16]))
        for j in range(16):
            anchor = {k: data[k][j] for k in data.files}; restore(env, anchor, SEED+j); image = env.render().copy()
            initial = encode(model, image[None]).cuda().unsqueeze(1); goal = encode(model, anchor['goal_pixels'][None]).cuda().unsqueeze(1)
            if h == 25 and j == 0: write_json(out/f'{task}_controls.json', {'native': controls(model, native_info(image, anchor['goal_pixels']), initial, goal), 'prefix': prefix_control(model, initial, norm)})
            common, shared = plan(model, initial, goal, env, 300, SEED+j*100); common = common.reshape(25, 2)
            for method in METHODS:
                restore(env, anchor, SEED+j); assert np.array_equal(env.render(), image); action = common.copy(); steps = 0; success = truncated = False; searches = [dict(shared, shared_initial=True)]; plans = [action.copy()]
                while steps < 2*h:
                    for command in action[:min(25 if method == 'NATIVE25' else 5, 2*h-steps)]*norm['std']+norm['mean']:
                        _, _, success, truncated, _ = env.step(command); steps += 1
                        if success or truncated: break
                    if success or truncated or steps == 2*h: break
                    tick = sync_time(); initial = encode(model, env.render()[None]).cuda().unsqueeze(1); seed = SEED+j*100+steps//5
                    prior = None if method == 'NATIVE25' else torch.as_tensor(shift_prior(action, 5), device='cuda', dtype=torch.float32)
                    if method == 'NATIVE25': planned, search = plan(model, initial, goal, env, 300, seed)
                    elif method == 'PREFIX5': planned, search = plan_prefix(model, initial, goal, env, 300, seed, prior)
                    else:
                        cost = FactorCost(model, initial, goal, heads[method.split('-')[0]], task, method.endswith('JOINT'))
                        planned = solver(cost, env.action_space, 25, 300, seed, 'cuda').solve({}, init_action=prior)['actions'].numpy(); search = {'cost_calls': cost.calls, 'candidate_evaluations': 300*cost.calls}
                    searches.append(dict(search, seconds_with_encode=sync_time()-tick, shared_initial=False)); action = planned.reshape(25, 2); plans.append(action.copy())
                np.savez_compressed(out/f'{task}_g{h}_{j:03d}_{method}.npz', normalized_plans=np.stack(plans), final_state=simulator_state(env, env._get_info()))
                rows.append(dict(task=task, goal_offset=h, anchor=j, episode=int(anchor['episode']), method=method, success=bool(success), truncated=bool(truncated), env_steps=steps, native_task_distance=task_distance(env, task), searches=searches, **auxiliary(env, task)))
                write_json(out/f'{task}_rows.json', rows); print('task_factor_cost', task, h, j, method, bool(success), flush=True)
    env.close(); reproduction = []
    old_native = json.loads((Path('/home/xiang/.cache/latent-wm-results/20261003-E13-commitment-cadence-RTX-s0')/'rows.json').read_text())
    old_prefix = json.loads((Path('/home/xiang/.cache/latent-wm-results/20261003-E11-latent-observer-RTX-s0')/'rows.json').read_text())
    for r in rows:
        if r['method'] == 'NATIVE25': old = next(x for x in old_native if x['task'] == task and x['goal_offset'] == r['goal_offset'] and x['anchor'] == r['anchor'] and x['method'] == 'EXEC25-COLD')
        elif r['method'] == 'PREFIX5' and r['goal_offset'] == 25: old = next(x for x in old_prefix if x['task'] == task and x['anchor'] == r['anchor'] and x['method'] == 'OBS-PREFIX5' and x['condition'] == 'nominal')
        else: continue
        passed = r['success'] == old['success'] and r['env_steps'] == old['env_steps'] and np.isclose(r['native_task_distance'], old['native_task_distance'], atol=1e-6, rtol=0)
        reproduction.append(dict(method=r['method'], goal_offset=r['goal_offset'], anchor=r['anchor'], passed=bool(passed)))
    write_json(out/f'{task}_baseline_reproduction.json', reproduction); assert all(r['passed'] for r in reproduction)
    return rows

def summary(rows):
    output = []; boot = np.random.default_rng(SEED+9000).integers(0, 16, (2000, 16))
    for task in EXTENT:
        for h in [25, 75]:
            group = [r for r in rows if r['task'] == task and r['goal_offset'] == h]
            for method in METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor']); assert [r['anchor'] for r in rr] == list(range(16)); s = sum(r['success'] for r in rr); comparisons = {}
                for baseline in ['NATIVE25', 'PREFIX5']:
                    base = sorted([r for r in group if r['method'] == baseline], key=lambda r: r['anchor']); delta = np.array([int(r['success'])-int(b['success']) for r, b in zip(rr, base)])
                    gain = np.array([b['native_task_distance']-r['native_task_distance'] for r, b in zip(rr, base)])
                    comparisons[baseline] = {'success_gain': delta.mean(), 'success_ci95': np.quantile(delta[boot].mean(1), [.025, .975]), 'distance_gain': gain.mean(), 'distance_ci95': np.quantile(gain[boot].mean(1), [.025, .975]), 'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0))}
                output.append(dict(task=task, goal_offset=h, method=method, n=len(rr), successes=s, wilson95=wilson(s, len(rr)), paired=comparisons))
    return output

def run(args):
    import stable_worldmodel as swm
    assert importlib.metadata.version('stable-worldmodel') == '0.0.6'; torch.set_num_threads(4)
    out = Path(args.output); cache = Path(args.model_cache); durable = Path('/home/xiang/.cache/latent-wm-results')/out.name
    assert cache.resolve().is_relative_to(Path('/home/xiang/.cache/huggingface')) and not durable.exists(); out.mkdir(parents=True, exist_ok=False); cache.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]; old = json.loads((Path(args.e17_run)/'config.json').read_text()); assert old['sources'] == cfgs and (Path(args.e17_run)/'complete.json').exists() and sorted(c['task'] for c in cfgs) == ['pusht', 'tworoom']
    helpers = ['first_wave.py', 'recovery_forks.py', 'query_proposal.py', 'latent_observer.py', 'commitment_cadence.py', 'action_basis.py', 'closed_loop.py', 'continuous_adaptation.py']
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'seed': SEED, 'methods': METHODS, 'harness_sha256': sha256(__file__), 'helper_sha256': {n: sha256(Path(__file__).with_name(n)) for n in helpers}, 'cem_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)), 'extent': EXTENT,
        'protocol': 'EX5 shifted warm/native EX25 cold; common initial native25 solve; raw action scoring shared known TwoRoom clipping limitation; REAL .5 realendpoint+.5 realgoal; MIX .25 realendpoint+.25 imaginedendpoint+.5 realgoal; extra task geometry labels; joint +latentL2/192; no deployment physical states',
        'training': {'head': '192-256-256-2/6/ReLU', 'endpoint': 5, 'updates': 2000, 'batch_size': 128, 'optimizer': 'AdamW', 'lr': 3e-4, 'weight_decay': 1e-3, 'clip': 1., 'equal_total_information': False, 'wm_pretrain_episode_overlap': 'unknown'}, 'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text())})
    for name in ['task_factor_cost.py']+helpers: shutil.copy2(Path(__file__).with_name(name), out/name.replace('.py', '_used.py'))
    rows = []
    for source, cfg in zip(args.sources, cfgs):
        model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False); norm = dict(np.load(Path(source)/'action_normalization.npz'))
        inputs = json.loads((Path(args.e17_run)/f'{cfg["task"]}_inputs.json').read_text()); assert all(np.array_equal(norm[k], inputs['normalization'][k]) for k in ['mean', 'std'])
        assert all(sha256(Path(args.prepared)/f'{cfg["task"]}_g{h}.npz') == inputs['anchors_sha256'][str(h)] for h in [25, 75])
        heads, episodes = train(args, cfg, model, norm, out); rows.extend(evaluate(args, cfg, model, norm, heads, episodes, out)); del model, heads; torch.cuda.empty_cache()
    solves = sum(len(r['searches']) for r in rows)-64*(len(METHODS)-1)
    write_json(out/'summary.json', summary(rows)); write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': sum(r['env_steps'] for r in rows), 'actual_solver_calls': solves, 'actual_candidate_evaluations': solves*300*30, 'shared_initial_solves': 64}); shutil.copytree(out, durable)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs=2, required=True)
    for name in ['prepared', 'e17-run', 'model-cache', 'output']: p.add_argument('--'+name, required=True)
    args = p.parse_args()
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
