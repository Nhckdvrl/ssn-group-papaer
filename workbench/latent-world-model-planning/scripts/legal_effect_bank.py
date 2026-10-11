"""E20 common fresh-reset + legal warm history; all small-bank outcomes retained."""
import argparse, hashlib, inspect, json, os, shutil
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='', SDL_VIDEODRIVER='dummy', PYGAME_HIDE_SUPPORT_PROMPT='1')
import gymnasium as gym
import h5py, hdf5plugin, numpy as np
import stable_worldmodel

SEED = 104200

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, x):
    Path(p).write_text(json.dumps(x, indent=2, allow_nan=False)+'\n')

def diagnostic(env, task):
    public = np.asarray(env._get_obs(), dtype=np.float64)
    if task == 'tworoom': return public
    bodies = []
    for b in [env.agent, env.block]:
        bodies.extend([*b.position, *b.velocity, b.angle, b.angular_velocity, *b.force, b.torque])
    return np.concatenate([public, bodies])  # Does not serialize contact/solver memory.

def proposals(factual, rng):
    zero = np.zeros((25, 2), dtype=np.float32)
    basis = [np.tile(a, (25, 1)).astype(np.float32) for a in [[1,0],[-1,0],[0,1],[0,-1]]]
    smooth = np.stack([np.interp(np.arange(25), [0,12,24], rng.uniform(-1,1,3)) for _ in range(2)], -1).astype(np.float32)
    iid = rng.uniform(-1,1,(25,2)).astype(np.float32)
    actions = np.stack([zero, zero.copy(), factual.astype(np.float32), *basis, smooth, -smooth,
        np.tile(rng.uniform(-1,1,2),(25,1)).astype(np.float32), iid, iid[::-1].copy()])
    assert actions.shape == (12,25,2) and np.isfinite(actions).all() and (np.abs(actions)<=1).all()
    return actions

def rollout(task, entry, actions):
    env = gym.make('swm/TwoRoom-v1' if task=='tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
    env.reset(seed=entry['reset_seed']); env._set_state(np.asarray(entry['initial_state']))
    env._set_goal_state(np.asarray(entry['goal_state']))
    assert np.array_equal(env.action_space.low, [-1,-1]) and np.array_equal(env.action_space.high, [1,1])
    if task == 'pusht': assert env.relative and env.action_scale==100
    history = [env.render().copy()]; history_states = [diagnostic(env,task)]
    for t,a in enumerate(entry['warm_actions']):
        env.step(np.asarray(a,dtype=np.float32))
        if (t+1)%5==0: history.append(env.render().copy()); history_states.append(diagnostic(env,task))
    pixels = [env.render().copy()]; states = [diagnostic(env,task)]; flags = []; rewards = []
    for a in actions:
        assert env.action_space.contains(a)
        _,reward,done,truncated,_ = env.step(a)
        pixels.append(env.render().copy()); states.append(diagnostic(env,task)); flags.append([bool(done),bool(truncated)]); rewards.append(float(reward))
    source = inspect.getfile(type(env)); env.close()
    return dict(history=np.stack(history), history_states=np.stack(history_states), pixels=np.stack(pixels),
        diagnostic_states=np.stack(states), issued_actions=actions, flags=np.asarray(flags), rewards=np.asarray(rewards)), sha(source)

def run(args):
    import torch
    torch.set_num_threads(4)
    out, durable = Path(args.output), Path(args.durable)
    assert not out.exists() and not durable.exists() and out.resolve()!=durable.resolve()
    out.mkdir(parents=True); ledger = []; sources = {}; all_steps = 0; records = []
    for task in ['tworoom','pusht']:
        native_cfg_path=Path(f'/home/xiang/.cache/latent-wm-results/20261002-{task}-native-s0/config.json')
        native_cfg=json.loads(native_cfg_path.read_text()); data=Path(native_cfg['dataset']); assert data.exists()
        train_path = Path('/home/xiang/.cache/latent-wm-results/20261002-E17-query-proposal-RTX-s0')/(task+'_train.json')
        train = json.loads(train_path.read_text()); rng = np.random.default_rng(SEED+(task=='pusht'))
        episodes = rng.choice(train['base_episodes'],args.anchors,replace=False).tolist()
        sources[task] = dict(dataset=str(data), native_config_sha256=sha(native_cfg_path), training_manifest_sha256=sha(train_path), selected_training_episodes=episodes,
            excluded_evaluation_episodes=train['excluded_episodes'], dataset_rehashed=False)
        assert not set(episodes)&set(train['excluded_episodes'])
        with h5py.File(data) as f:
            for j, ep in enumerate(episodes[:1 if args.preflight else args.anchors]):
                n,start = int(f['ep_len'][ep]),int(f['ep_offset'][ep]); assert n>36
                t = int(rng.integers(10,n-25)); key='state' if 'state' in f else 'proprio'
                controls=f['action'][start+t-10:start+t+25]; assert controls.shape==(35,2) and np.isfinite(controls).all()
                legal = np.clip(controls,-1,1).astype(np.float32)
                action = proposals(legal[10:],rng); np.save(out/f'{task}_{j:03d}_locked_actions.npy',action)
                entry=dict(task=task,anchor=j,episode=ep,source_step=t,reset_seed=SEED+j+(100 if task=='pusht' else 0),
                    initial_state=f[key][start+t-10].tolist(),goal_state=f[key][start+t+25].tolist(),warm_actions=legal[:10].tolist(),
                    source_actions_clipped_components=int((controls!=np.clip(controls,-1,1)).sum()),
                    actions_sha256=sha(out/f'{task}_{j:03d}_locked_actions.npy'))
                ledger.append(entry)
    save(out/'ledger.json',ledger)  # Locked before any simulator outcome exists.
    save(out/'config.json',dict(seed=SEED,preflight=args.preflight,anchors_per_task=args.anchors,sources=sources,script_sha256=sha(__file__),
        branches=12,horizon=25,warmup=10,history_offsets=[-10,-5,0],duplicate_branch=1,
        supervision='pixels+actual actions; physical quantities diagnostic only',
        scope='common fresh reset then identical legal warm rollout; original dataset full-state identity not asserted'))
    shutil.copy2(__file__,out/'legal_effect_bank_used.py')
    for entry in ledger:
        task,j=entry['task'],entry['anchor']; actions=np.load(out/f'{task}_{j:03d}_locked_actions.npy'); first=None
        for k,a in enumerate(actions):
            trace,code_hash=rollout(task,entry,a); all_steps+=35
            if first is None: first=trace
            assert np.array_equal(first['history'],trace['history']) and np.array_equal(first['history_states'],trace['history_states'])
            if k==1: assert all(np.array_equal(first[n],trace[n]) for n in trace), 'Duplicate replay mismatch'
            path=out/f'{task}_{j:03d}_b{k:02d}.npz'; np.savez_compressed(path,**trace)
            state_delta=float(np.max(np.abs(trace['diagnostic_states']-first['diagnostic_states'])))
            record=dict(task=task,anchor=j,branch=k,trace_sha256=sha(path),env_source_sha256=code_hash,
                same_action_repeat=k==1,max_diagnostic_delta_vs_zero=state_delta,
                max_pixel_delta_vs_zero=int(np.max(np.abs(trace['pixels'].astype(int)-first['pixels'].astype(int)))))
            records.append(record)
        repeated,_=rollout(task,entry,actions[0]);all_steps+=35
        assert all(np.array_equal(first[n],repeated[n]) for n in first),'End-of-bank replay mismatch'
        save(out/'rows.json',records); print('legal_effect_bank',task,j,'all12+replay exact',flush=True)
    save(out/'summary.json',dict(anchors=len(ledger),branches=len(records),env_steps=all_steps,repeats_exact=True,
        anchors_with_any_diagnostic_difference=sum(any(r['max_diagnostic_delta_vs_zero']>0 for r in records if r['task']==e['task'] and r['anchor']==e['anchor']) for e in ledger),
        limitations='Not full-state equivalence, model comparison or control evidence; duplicate zero excluded from later training; diagnostic state omits solver/contact cache'))
    save(out/'complete.json',dict(completed=True,stage='preflight' if args.preflight else 'bank',anchors=len(ledger),branches=len(records),env_steps=all_steps))
    shutil.copytree(out,durable)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--durable',required=True);p.add_argument('--preflight',action='store_true');p.add_argument('--anchors',type=int,choices=[6,44],default=6);args=p.parse_args()
    try: run(args)
    except Exception as error:
        out=Path(args.output)
        if out.exists(): save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise
