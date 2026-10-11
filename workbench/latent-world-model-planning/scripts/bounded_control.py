"""E20: matched physical-action CEM and fresh-episode control validation.

The optimizer is the native CEM recipe with bounds applied before scoring
and elite updates. This interface repair is a control, not a new method.
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
import numpy as np

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ARTIFACTS = Path('/home/xiang/.cache/latent-wm-results')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''): h.update(block)
    return h.hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def restore(entry):
    import gymnasium as gym
    import stable_worldmodel  # Registers the environments.
    env = gym.make('swm/TwoRoom-v1', render_mode='rgb_array').unwrapped
    env.reset(seed=entry['reset_seed'])
    env._set_state(np.asarray(entry['initial_state']))
    env._set_goal_state(np.asarray(entry['goal_state']))
    history = [env.render().copy()]
    for t, action in enumerate(entry['warm_actions']):
        env.step(np.asarray(action, dtype=np.float32))
        if (t+1) % 5 == 0: history.append(env.render().copy())
    return env, np.stack(history)


def prepare(args):
    import h5py, hdf5plugin
    out = Path(args.output); assert not out.exists(); out.mkdir(parents=True)
    excluded = set(); provenance = []
    manifests = [ARTIFACTS/'20261002-E16-data-compute-RTX-s0/BASE1000/data_manifest.json',
                 ARTIFACTS/'20261002-E17-query-proposal-RTX-s0/tworoom_train.json']
    for p in manifests:
        d = json.loads(p.read_text()); provenance.append(dict(file=str(p), sha256=sha(p)))
        for k in ['base_episodes', 'evaluation_episodes', 'excluded_previous_episodes', 'excluded_episodes']:
            excluded.update(d.get(k, []))
    ledger = []
    with h5py.File(args.dataset) as f:
        lengths, offsets = f['ep_len'][:], f['ep_offset'][:]
        eligible = np.setdiff1d(np.flatnonzero(lengths > 95), sorted(excluded))
        episodes = np.random.default_rng(105200).choice(eligible, 48, replace=False)
        rng = np.random.default_rng(105201)
        for j, ep in enumerate(episodes):
            span = 25 if j < 24 else 75
            t = int(rng.integers(10, int(lengths[ep])-span)); row = int(offsets[ep])+t
            raw = f['action'][row-10:row+span]
            assert raw.shape == (10+span, 2) and np.isfinite(raw).all()
            actions = np.clip(raw, -1, 1).astype(np.float32)
            goal = f['pixels'][row+span]
            np.save(out/f'goal_{j:03d}.npy', goal)
            np.save(out/f'factual_{j:03d}.npy', actions[10:])
            ledger.append(dict(anchor=j, episode=int(ep), source_step=t, goal_span=span,
                reset_seed=105300+j, initial_state=f['proprio'][row-10].tolist(),
                goal_state=f['proprio'][row+span].tolist(), warm_actions=actions[:10].tolist(),
                clipped_components=int((raw != np.clip(raw, -1, 1)).sum()),
                goal_sha256=sha(out/f'goal_{j:03d}.npy'), factual_sha256=sha(out/f'factual_{j:03d}.npy')))
    save(out/'ledger.json', ledger)  # Sealed before any simulator/model outcome.
    save(out/'config.json', dict(selection_seed=105200, start_seed=105201, n=48,
        dataset=args.dataset, dataset_rehashed=False, excluded_episodes=sorted(excluded), sources=provenance,
        horizon=25, execution=25, max_new_env_steps=100, warm_env_steps=10,
        sampling='300 samples, 30 elites, 30 iterations; physical bounded CEM',
        scope='fresh episode development set; released pretraining split unknown', script_sha256=sha(__file__)))
    controls = []
    for e in ledger:
        j = e['anchor']; env, history = restore(e); initial = env.agent_position.numpy().copy()
        repeated, h2 = restore(e)
        assert np.array_equal(history, h2) and np.array_equal(initial, repeated.agent_position.numpy())
        repeated.close(); np.save(out/f'history_{j:03d}.npy', history)
        initially_succeeded = np.linalg.norm(initial-np.asarray(e['goal_state'])) < 16
        success = bool(initially_succeeded); states = [initial]
        for action in np.load(out/f'factual_{j:03d}.npy'):
            _, _, done, truncated, _ = env.step(action)
            assert not truncated
            states.append(env.agent_position.numpy().copy()); success |= bool(done)
        distance = float(np.linalg.norm(states[-1]-np.asarray(e['goal_state'])))
        pixel_exact = np.array_equal(env.render(), np.load(out/f'goal_{j:03d}.npy'))
        assert distance < 1e-4 and pixel_exact and success, 'Factual restore contract failed'
        env.close(); np.save(out/f'factual_states_{j:03d}.npy', np.asarray(states))
        controls.append(dict(anchor=j, success=success, initially_succeeded=bool(initially_succeeded),
            terminal_distance=distance, goal_pixel_exact=bool(pixel_exact), warm_repeat_exact=True))
        save(out/'controls.json', controls)
    save(out/'complete.json', dict(completed=True, n=48, all_factual_exact=True,
        preparation_env_steps=sum(e['goal_span']+20 for e in ledger)))
    shutil.copy2(__file__, out/'bounded_control_used.py')
    shutil.copytree(out, ARTIFACTS/out.name)


def bounded_cem(cost, seed, device='cuda', n=300, k=30, iterations=30, capture=False):
    import torch
    rng = torch.Generator(device=device).manual_seed(seed)
    mean = torch.zeros(1, 5, 10, device=device); std = torch.ones_like(mean); banks = []
    with torch.inference_mode():
        for iteration in range(iterations):
            candidates = torch.randn(1, n, 5, 10, device=device, generator=rng)*std[:, None]+mean[:, None]
            candidates[:, 0] = mean; candidates = candidates.clamp(-1, 1)
            scores = cost.get_cost({}, candidates)
            assert scores.shape == (1, n) and torch.isfinite(scores).all()
            elites = scores.topk(k, dim=1, largest=False).indices
            selected = candidates[torch.arange(1, device=device)[:, None], elites]
            next_mean, next_std = selected.mean(1), selected.std(1)
            assert (next_mean.abs() <= 1).all() and torch.isfinite(next_std).all()
            if capture:
                banks.append(dict(actions=candidates[0].cpu().numpy(), costs=scores[0].cpu().numpy(),
                    elite=elites[0].cpu().numpy(), mean=next_mean[0].cpu().numpy(), std=next_std[0].cpu().numpy()))
            mean, std = next_mean, next_std
    return mean.cpu().numpy().reshape(25, 2), banks


def evaluate(args):
    import torch
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    from lewm_pilot import architecture, NativeCost, pixels, now, native_control
    from fixed_data_train_seed import state_hash
    torch.set_num_threads(4)
    bank, out = Path(args.bank), Path(args.output); assert not out.exists(); out.mkdir(parents=True)
    assert json.loads((bank/'complete.json').read_text())['all_factual_exact']
    ledger = json.loads((bank/'ledger.json').read_text())
    checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    if isinstance(checkpoint, dict):
        model = architecture(checkpoint['config']); model.load_state_dict(checkpoint['state_dict'], strict=True)
        mean, std = np.asarray(checkpoint['manifest']['action_mean']), np.asarray(checkpoint['manifest']['action_std'])
        assert not set(checkpoint['manifest']['base_episodes']) & {e['episode'] for e in ledger}
        updates = checkpoint['steps']; source_scope = 'own trained split disjoint'
    else:
        model = checkpoint
        norm = json.loads((ARTIFACTS/'20261002-E16-data-compute-RTX-s0/released_action_norm.json').read_text())
        assert norm['checkpoint_sha256'] == sha(args.checkpoint) and len(model.state_dict()) == 303
        mean, std = np.asarray(norm['mean']), np.asarray(norm['std'])
        updates = None; source_scope = 'released checkpoint pretraining split unknown'
    model = model.cuda().eval().requires_grad_(False); initial_hash = state_hash(model.state_dict())
    config = dict(vars(args), bank_ledger_sha256=sha(bank/'ledger.json'), checkpoint_sha256=sha(args.checkpoint),
        action_mean=mean.tolist(), action_std=std.tolist(), script_sha256=sha(__file__),
        model_tensor_sha256=initial_hash, hardware=torch.cuda.get_device_name(), model_training_updates=updates, source_scope=source_scope,
        scope='new episode development; joint method components, not full SMWM/AD-WM reproduction')
    save(out/'config.json', config); shutil.copy2(__file__, out/'bounded_control_used.py'); rows = []
    with torch.inference_mode():
        for e in ledger:
            j = e['anchor']; env, history = restore(e)
            assert np.array_equal(history, np.load(bank/f'history_{j:03d}.npy'))
            history = list(history); past = list(e['warm_actions'])
            goal = pixels(np.load(bank/f'goal_{j:03d}.npy')[None]).unsqueeze(0)
            success = bool(np.linalg.norm(env.agent_position.numpy()-e['goal_state']) < 16)
            controls = []; states = [env.agent_position.numpy().copy()]; times = []; decision_rows = []
            for decision in range(4):
                if success: break
                start = now(); h = pixels(np.asarray(history[-3:]))[None]
                p = torch.as_tensor((np.asarray(past[-10:])-mean)/std, device='cuda').float().reshape(1, 2, 10)
                native = NativeCost(model, h, goal, p)
                if j == 0 and decision == 0: save(out/'native_parity.json', native_control(model, h, goal, p))
                if args.interface == 'physical':
                    class PhysicalCost:
                        def get_cost(self, info, actions):
                            normalized = (actions.reshape(1, -1, 5, 5, 2)-actions.new_tensor(mean))/actions.new_tensor(std)
                            return native.get_cost(info, normalized.flatten(-2).float())
                    actions, banks = bounded_cem(PhysicalCost(), 105400+j*100+decision, capture=j==0)
                    if banks: np.savez_compressed(out/f'candidate_a{j}_d{decision}.npz',
                        **{f'{key}_{it}': value for it, b in enumerate(banks) for key, value in b.items()})
                else:
                    solver = swm.solver.CEMSolver(native, num_samples=300, topk=30, n_steps=30, device='cuda', seed=105400+j*100+decision)
                    solver.configure(action_space=batch_space(env.action_space, 1), n_envs=1,
                        config=swm.PlanConfig(horizon=5, receding_horizon=5, action_block=5, warm_start=True))
                    actions = solver.solve({})['actions'][0].numpy().reshape(25, 2)*std+mean
                times.append(now()-start)
                if args.interface == 'physical': assert (np.abs(actions) <= 1).all()
                count = 0
                for t, a in enumerate(actions):
                    _, _, done, truncated, _ = env.step(a.astype(np.float32)); count += 1
                    past.append(a); controls.append(a); states.append(env.agent_position.numpy().copy())
                    if (t+1) % 5 == 0: history.append(env.render().copy())
                    if done or truncated: success = bool(done); break
                decision_rows.append(dict(decision=decision, executed_steps=count,
                    out_of_bounds_components=int((np.abs(actions)>1).sum())))
                if done or truncated: break
            env.close(); trace = out/f'trace_{j:03d}.npz'
            np.savez_compressed(trace, actions=np.asarray(controls).reshape(-1,2), states=np.asarray(states))
            rows.append(dict(anchor=j, episode=e['episode'], goal_span=e['goal_span'], success=success,
                env_steps=len(controls), planning_seconds=times, decisions=decision_rows, trace_sha256=sha(trace)))
            save(out/'rows.json', rows); print('bounded_control', args.interface, out.name, j, int(success), flush=True)
    assert initial_hash == state_hash(model.state_dict())
    save(out/'summary.json', [dict(goal_span=span, n=sum(r['goal_span']==span for r in rows),
        successes=sum(r['success'] for r in rows if r['goal_span']==span)) for span in [25,75]])
    save(out/'complete.json', dict(completed=True, n=48, model_unchanged=True))
    shutil.copytree(out, ARTIFACTS/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['prepare', 'evaluate'])
    p.add_argument('--output', required=True); p.add_argument('--dataset'); p.add_argument('--bank')
    p.add_argument('--checkpoint'); p.add_argument('--interface', choices=['physical','native'], default='physical')
    args = p.parse_args()
    try: (prepare if args.mode=='prepare' else evaluate)(args)
    except Exception as error:
        out = Path(args.output)
        if out.exists(): save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise
