"""Fresh-warm PushT goals from actual continuations, with full frozen roster."""
import argparse
import gc
import inspect
import json
import os
import shutil
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import gymnasium as gym
import h5py
import hdf5plugin
import numpy as np
import stable_worldmodel as swm
import torch
import bounded_control as b

ROOT = Path('/home/xiang/.cache/latent-wm-results')
HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')
BANK = ROOT/'20261005-E20-pusht-fresh-control-bank48'
METHODS = ['PLAIN','GLOBAL-SG','CENTER','DET-INVERSE','PROB-INVERSE']


def diagnostic(env):
    values = list(env._get_obs())
    for body in [env.agent, env.block]:
        values += [*body.position, *body.velocity, body.angle, body.angular_velocity, *body.force, body.torque]
    return np.asarray(values, dtype=np.float64)


def success(state, goal):
    angle = abs(state[4]-goal[4])
    return bool(np.linalg.norm(state[:4]-goal[:4]) < 20 and min(angle, 2*np.pi-angle) < np.pi/9)


def restore(entry, goal=None):
    env = gym.make('swm/PushT-v1', render_mode='rgb_array').unwrapped
    env.reset(seed=entry['reset_seed']); env._set_state(np.asarray(entry['initial_state']))
    assert env.relative and env.action_scale == 100 and np.array_equal(env.action_space.low, [-1,-1]) and np.array_equal(env.action_space.high, [1,1])
    if goal is not None: env._set_goal_state(np.asarray(goal))
    history = [env.render().copy()]
    for t, action in enumerate(entry['warm_actions']):
        env.step(np.asarray(action, dtype=np.float32))
        if (t+1)%5 == 0: history.append(env.render().copy())
    return env, np.asarray(history)


def prepare(args):
    torch.set_num_threads(4); out = Path(args.output)
    assert not out.exists() and not BANK.exists(); out.mkdir(parents=True)
    shutil.copy2(__file__, out/'pusht_fresh_control_used.py')
    try:
        old = json.loads((ROOT/'20261004-E20-legal-effect-bank44/ledger.json').read_text())
        excluded = {v['episode'] for v in old if v['task']=='pusht'}
        train = json.loads((ROOT/'20261002-E17-query-proposal-RTX-s0/pusht_train.json').read_text())
        excluded |= set(train['base_episodes']) | set(train['excluded_episodes'])
        rng, start_rng = np.random.default_rng(109000), np.random.default_rng(109001)
        ledger = []
        with h5py.File(args.dataset) as f:
            eligible = [i for i,n in enumerate(f['ep_len'][:]) if n>=86 and i not in excluded]
            episodes = rng.choice(eligible, 48, replace=False).tolist()
            for j, episode in enumerate(episodes):
                n, offset = int(f['ep_len'][episode]), int(f['ep_offset'][episode])
                initial_t = int(start_rng.integers(0, n-85)); row = offset+initial_t
                goal_span = 25 if j<24 else 75
                original = f['action'][row:row+10+goal_span]
                assert np.isfinite(original).all()
                actions = np.clip(original, -1, 1).astype(np.float32)
                np.save(out/f'factual_{j:03d}.npy', actions[10:])
                ledger.append(dict(anchor=j, episode=episode, source_initial_step=initial_t,
                    reset_seed=109100+j, initial_state=f['state'][row].tolist(),
                    warm_actions=actions[:10].tolist(), goal_span=goal_span,
                    clipped_source_components=int((original!=np.clip(original,-1,1)).sum()),
                    factual_action_sha256=b.sha(out/f'factual_{j:03d}.npy')))
        b.save(out/'selection_ledger.json', ledger)  # Before any simulated outcome.
        b.save(out/'config.json', dict(dataset=args.dataset, selection_seed=109000, start_seed=109001,
            n=48, excluded_source_episodes=sorted(excluded), script_sha256=b.sha(__file__),
            goal_source='actual factual continuation after common fresh reset and legal warm actions',
            scope='new source development; released pretraining split unknown; not original dataset contact-state restoration or paper replication'))
        controls = []
        for entry in ledger:
            j = entry['anchor']; factual = np.load(out/f'factual_{j:03d}.npy')
            env, history = restore(entry); warm = diagnostic(env)
            states = [warm]
            for action in factual:
                env.step(action); states.append(diagnostic(env))
            goal = np.asarray(env._get_obs()).copy(); goal_pixels = env.render().copy()
            env_hash = b.sha(inspect.getfile(type(env))); env.close()
            entry['goal_state'] = goal.tolist()
            np.save(out/f'goal_{j:03d}.npy', goal_pixels); np.save(out/f'history_{j:03d}.npy', history)
            np.save(out/f'factual_states_{j:03d}.npy', np.asarray(states))
            # Setting the evaluation goal must not perturb physical warm history or renders.
            repeated, repeat_history = restore(entry, goal)
            assert np.array_equal(history, repeat_history) and np.array_equal(warm, diagnostic(repeated))
            repeated_states = [diagnostic(repeated)]
            for action in factual:
                _, _, done, _, _ = repeated.step(action); repeated_states.append(diagnostic(repeated))
                assert bool(done) == success(repeated._get_obs(), goal)
            assert np.array_equal(np.asarray(states), np.asarray(repeated_states))
            assert np.array_equal(goal_pixels, repeated.render()) and success(repeated._get_obs(), goal)
            repeated.close()
            controls.append(dict(anchor=j, factual_success=True, all_diagnostic_states_exact=True,
                all_warm_pixels_exact=True, goal_pixels_exact=True, environment_source_sha256=env_hash,
                initial_success=success(warm[:7], goal)))
            b.save(out/'controls.json', controls); print('pusht fresh prepare', j, 'factual/repeat exact', flush=True)
        b.save(out/'ledger.json', ledger)
        b.save(out/'complete.json', dict(completed=True, n=48, factual_all_success=True, all_warm_and_replay_exact=True,
            preparation_env_steps=2*sum(10+v['goal_span'] for v in ledger)))
        shutil.copytree(out, BANK)
    except Exception as error:
        b.save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        if not BANK.exists(): shutil.copytree(out, BANK)
        raise


@torch.inference_mode()
def evaluate():
    # Keep the full published AD reference and all transferred models in one explicit namespace.
    import adwm_reference as ad
    import effect_transfer as transfer
    from lewm_pilot import NativeCost, native_control, pixels, architecture
    from fixed_data_train_seed import state_hash
    from gymnasium.vector.utils import batch_space
    torch.set_num_threads(4)
    assert json.loads((BANK/'complete.json').read_text())['all_warm_and_replay_exact']
    ledger = json.loads((BANK/'ledger.json').read_text())
    for method in ['RELEASED']+METHODS+['AD-REFERENCE']:
        if method=='AD-REFERENCE':
            model, mean, std, entry = ad.load('pusht'); checkpoint=Path(entry['path'])
        elif method=='RELEASED':
            model, _, mean, std, _ = transfer.load_source('cuda'); checkpoint=transfer.SOURCE
        else:
            source = f'20261004-E20-joint-pusht-{method}-RTX-s0'
            assert json.loads((ROOT/source/'complete.json').read_text()) == dict(completed=True, method=method, seed=0, updates=2000)
            checkpoint = HF/source/'u2000.ckpt'; c = torch.load(checkpoint, map_location='cpu', weights_only=False)
            assert b.sha(checkpoint) == next(v['checkpoint_sha256'] for v in json.loads((ROOT/source/'summary.json').read_text()) if v['updates']==2000)
            model=architecture(c['config']); model.load_state_dict(c['state_dict'], strict=True); model=model.cuda()
            mean, std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std'])
        model.eval().requires_grad_(False); weights=state_hash(model.state_dict())
        for interface in ['native','physical']:
            out=Path('/tmp/latent-wm-runs')/f'20261005-E20-pusht-control-{method}-{interface}-RTX-s0'
            assert not out.exists() and not (ROOT/out.name).exists(); out.mkdir(); shutil.copy2(__file__,out/'pusht_fresh_control_used.py')
            try:
                b.save(out/'config.json',dict(method=method,interface=interface,checkpoint=str(checkpoint),checkpoint_sha256=b.sha(checkpoint),
                    bank_ledger_sha256=b.sha(BANK/'ledger.json'),script_sha256=b.sha(__file__),controller_sha256=b.sha(b.__file__),
                    action_mean=mean.tolist(),action_std=std.tolist(),hardware=torch.cuda.get_device_name(),
                    scope='same 48 actual-continuation tasks; one transfer trainseed; AD published training unmatched; native may issue out-of-Box actions; not paper numeric replication'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,history=restore(entry,goal)
                    assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                    assert np.array_equal(diagnostic(env),np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                    history=list(history);past=list(entry['warm_actions']);states=[diagnostic(env)];commands=[];decisions=[]
                    reached=success(env._get_obs(),goal);goal_image=pixels(np.load(BANK/f'goal_{j:03d}.npy')[None])[None]
                    for decision in range(4):
                        if reached: break
                        h=pixels(np.asarray(history[-3:]))[None]
                        pa=torch.as_tensor((np.asarray(past[-10:])-mean)/std,device='cuda').float().reshape(1,2,10)
                        native=NativeCost(model,h,goal_image,pa)
                        if not (out/'native_parity.json').exists():b.save(out/'native_parity.json',native_control(model,h,goal_image,pa))
                        seed=109400+j*100+decision
                        if interface=='physical':
                            class Cost:
                                def get_cost(self,info,actions):
                                    return native.get_cost(info,((actions.reshape(1,-1,5,5,2)-actions.new_tensor(mean))/actions.new_tensor(std)).flatten(-2).float())
                            chosen,_=b.bounded_cem(Cost(),seed);assert (np.abs(chosen)<=1).all()
                        else:
                            solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=seed)
                            solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,
                                config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                            chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                        count=0
                        for t,action in enumerate(chosen):
                            _,_,done,truncated,_=env.step(action.astype(np.float32));assert not truncated
                            reached=success(env._get_obs(),goal);assert bool(done)==reached
                            commands.append(action);past.append(action);states.append(diagnostic(env));count+=1
                            if (t+1)%5==0:history.append(env.render().copy())
                            if reached:break
                        decisions.append(dict(decision=decision,executed_steps=count,issued_out_of_bounds_components=int((np.abs(chosen[:count])>1).sum())))
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,actions=np.asarray(commands).reshape(-1,2),states=np.asarray(states))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=success(states[0][:7],goal),env_steps=len(commands),decisions=decisions,trace_sha256=b.sha(trace)))
                    b.save(out/'rows.json',rows);print('pusht fresh control',method,interface,j,int(reached),flush=True)
                assert weights==state_hash(model.state_dict())
                b.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(r['success'] for r in rows if r['goal_span']==v)) for v in [25,75]])
                b.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,ROOT/out.name)
            except Exception as error:
                b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/out.name);raise
        del model;gc.collect();torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','evaluate']);p.add_argument('--dataset');p.add_argument('--output')
    args=p.parse_args()
    (prepare(args) if args.mode=='prepare' else evaluate())
