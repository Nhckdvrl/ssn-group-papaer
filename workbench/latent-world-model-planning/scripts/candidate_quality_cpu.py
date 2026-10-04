"""E13 A6: locked argmin candidate outcomes; no model, GPU, or CEM update."""
import argparse
import hashlib
import inspect
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import gymnasium as gym
import h5py
import hdf5plugin
import numpy as np
import stable_worldmodel
import torch
from first_wave import restore, sha256, write_json

SEED = 81000


def execute(row, data, actions, method, out):
    task = row['task']; env = gym.make('swm/TwoRoom-v1' if task=='tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
    restore(env, data, SEED+row['anchor']); first = env.render().copy()
    public = np.asarray(env._get_info()['proprio'] if task=='tworoom' else env._get_obs()).copy()
    states = [np.asarray(env._get_obs()).copy()]; hashes = [hashlib.sha256(first.tobytes()).hexdigest()]; flags = []; rewards = []
    success = truncated = False
    for action in actions:
        _, reward, done, truncated, info = env.step(action.copy()); success |= bool(done)
        states.append(np.asarray(env._get_obs()).copy()); frame = env.render().copy()
        hashes.append(hashlib.sha256(frame.tobytes()).hexdigest()); flags.append([bool(done), bool(truncated)]); rewards.append(float(reward))
        if done or truncated: break
    state = np.asarray(env._get_info()['proprio'] if task=='tworoom' else env._get_obs()).copy(); goal = data['goal_state']
    native_distance = float(info['distance_to_target']) if task=='tworoom' else float(env.eval_state(env.goal_state, state)[1])
    position = float(np.linalg.norm(state[:2 if task=='tworoom' else 4]-goal[:2 if task=='tworoom' else 4]))
    angle = None if task=='tworoom' else float(abs(np.arctan2(np.sin(state[4]-goal[4]), np.cos(state[4]-goal[4]))))
    trace = out/f'{row["stem"]}_{method}_trace.npz'
    np.savez_compressed(trace, issued_actions=actions[:len(flags)], states=states, pixel_sha256=hashes, flags=flags, rewards=rewards, first_pixels=first, final_pixels=frame)
    result = dict(stem=row['stem'], task=task, goal_offset=row['goal_offset'], anchor=row['anchor'], method=method,
        success=success, final_native_success=bool(flags[-1][0]), truncated=bool(truncated), env_steps=len(flags), native_return=sum(rewards),
        native_state_distance=native_distance, pure_position_distance=position, wrapped_angle_distance=angle,
        start_state_max_abs_error=float(np.max(np.abs(public-data['state']))), start_pixel_max_abs_error=int(np.max(np.abs(first.astype(int)-data['pixels'].astype(int)))),
        start_pixel_mae=float(np.abs(first.astype(float)-data['pixels']).mean()), trace=str(trace), trace_sha256=sha256(trace),
        env_source=inspect.getfile(type(env)), env_source_sha256=sha256(inspect.getfile(type(env))))
    env.close(); return result


def same_trace(a, b):
    x, y = np.load(a['trace']), np.load(b['trace'])
    checks = {k: bool(np.array_equal(x[k], y[k])) for k in x.files}
    assert all(checks.values()), checks
    return checks


def summarize(rows):
    result = []
    for task in ['tworoom', 'pusht']:
        for h in [25, 75]:
            group = [r for r in rows if r['task']==task and r['goal_offset']==h]; methods = {m: sorted([r for r in group if r['method']==m], key=lambda r:r['anchor']) for m in ['Fast', 'LeWM', 'FACTUAL']}
            assert all(len(v)==16 for v in methods.values())
            delta = np.array([int(b['success'])-int(a['success']) for a,b in zip(methods['Fast'], methods['LeWM'])])
            boot = np.random.default_rng(SEED+h).integers(0, 16, (2000, 16))
            result.append(dict(task=task, goal_offset=h, n=16, successes={m:sum(r['success'] for r in v) for m,v in methods.items()},
                helped=int((delta>0).sum()), harmed=int((delta<0).sum()), paired_success_gain=float(delta.mean()), paired_success_ci95=np.quantile(delta[boot].mean(1), [.025,.975]),
                primary=h==25, scope='selected25 candidate outcomes; g75 distance is proxy, FACTUAL uses full goal offset; not CEM elite mean or optimal regret'))
    return result


def run(args):
    torch.set_num_threads(4); bank, reference, out, durable = map(Path, [args.bank, args.reference, args.output, args.durable])
    locations = [p.resolve() for p in [bank, reference, out, durable]]
    assert all(a!=b and a not in b.parents and b not in a.parents for i,a in enumerate(locations) for b in locations[i+1:])
    assert not out.exists() and not durable.exists()
    seal = json.loads((bank/'seal.json').read_text()); assert seal['banks']==64 and not seal['truth_generated'] and seal['ledger_sha256']==sha256(bank/'ledger.json')
    ledger = json.loads((bank/'ledger.json').read_text()); assert len(ledger)==64
    assert {(r['task'],r['goal_offset'],r['anchor']) for r in ledger}=={(t,h,j) for t in ['tworoom','pusht'] for h in [25,75] for j in range(16)}
    assert json.loads((reference/'complete.json').read_text())['completed'] and json.loads((reference/'complete.json').read_text())['banks']==64
    reference_rows = {r['stem']:r for r in json.loads((reference/'rows.json').read_text())}; assert set(reference_rows)=={r['stem'] for r in ledger}
    sources = {c['task']:c for c in json.loads((bank/'sources.json').read_text())}; selections = []
    for row in ledger:
        path = bank/f'{row["stem"]}.npz'; scores = reference/f'{row["stem"]}_lewm_scores.npy'
        assert sha256(path)==row['bank_sha256'] and sha256(scores)==reference_rows[row['stem']]['reference_scores_sha256']
        data = np.load(path); ref = np.load(scores); fast = data['fast_scores']; assert ref.shape==fast.shape==(900,) and np.isfinite(ref).all() and np.isfinite(fast).all()
        selections.append(dict(stem=row['stem'], Fast=int(np.argmin(fast)), LeWM=int(np.argmin(ref)),
            Fast_min=float(fast.min()), LeWM_min=float(ref.min()), Fast_min_exact_ties=int((fast==fast.min()).sum()), LeWM_min_exact_ties=int((ref==ref.min()).sum()),
            Fast_top2_gap=float(np.diff(np.sort(fast)[:2])[0]), LeWM_top2_gap=float(np.diff(np.sort(ref)[:2])[0])))
    out.mkdir(parents=True); durable.mkdir(parents=True); write_json(out/'locked_selections.json', selections)
    config = dict(vars(args), seed=SEED, expected_anchors=64, planned_max_environment_steps=6400, script_sha256=sha256(__file__),
        bank_seal_sha256=sha256(bank/'seal.json'), reference_complete_sha256=sha256(reference/'complete.json'), reference_rows_sha256=sha256(reference/'rows.json'),
        bank_config_sha256=sha256(bank/'config.json'), reference_config_sha256=sha256(reference/'config.json'), restore_helper_sha256=sha256(Path(__file__).with_name('first_wave.py')),
        source_datasets={t:c['dataset'] for t,c in sources.items()}, packages={n:importlib.metadata.version(n) for n in ['stable-worldmodel','gymnasium','pymunk','numpy','torch']},
        scope='all64 retained; expert future only positive control; no model or GPU; PushT public setter lacks dataset contact memory',
        distance_definition='native installed state distance; separate 2D navigation or 4D agent/block position norm and 2pi wrapped angle, no symmetry correction')
    write_json(out/'config.json', config); shutil.copy2(__file__, out/'candidate_quality_cpu_used.py'); rows = []; preflight = []
    for row, selected in zip(ledger, selections):
        if args.preflight_only and row['anchor']!=0: continue
        data = np.load(bank/f'{row["stem"]}.npz'); physical = data['physical_actions']; assert physical.shape==(900,25,2) and np.isfinite(physical).all()
        if args.preflight_only:
            actions = physical[selected['Fast']]; a = execute(row, data, actions, 'REPLAY_A', out); b = execute(row, data, actions, 'REPLAY_B', out)
            checks = same_trace(a,b); preflight.append(dict(stem=row['stem'], checks=checks, first=a, second=b)); write_json(out/'preflight.json', preflight); continue
        with h5py.File(sources[row['task']]['dataset']) as f:
            ep, start, h = int(data['episode']), int(data['start']), row['goal_offset']; offset = int(f['ep_offset'][ep])+start
            assert start+h<int(f['ep_len'][ep]); factual = f['action'][offset:offset+h]; assert factual.shape==(h,2) and np.isfinite(factual).all()
        current = []
        for method, actions in [('Fast',physical[selected['Fast']]), ('LeWM',physical[selected['LeWM']]), ('FACTUAL',factual)]:
            record = execute(row, data, actions, method, out); record.update(selection=selected, selected_id=None if method=='FACTUAL' else selected[method]); rows.append(record); current.append(record)
            assert record['start_pixel_max_abs_error']==0, record
            write_json(out/'rows.json', rows)
        firsts = [np.load(r['trace']) for r in current]
        assert all(np.array_equal(firsts[0]['states'][0],x['states'][0]) and np.array_equal(firsts[0]['first_pixels'],x['first_pixels']) for x in firsts[1:])
        shutil.copytree(out, durable, dirs_exist_ok=True); print('candidate_quality', row['stem'], flush=True)
    if args.preflight_only:
        assert len(preflight)==4; write_json(out/'complete.json', dict(completed=True, phase='four fixed anchor replay preflight', pairs=4, model_loaded=False, GPU_used=False))
    else:
        assert len(rows)==192 and sum(r['env_steps'] for r in rows)<=6400; write_json(out/'summary.json', summarize(rows))
        write_json(out/'complete.json', dict(completed=True, anchors=64, branches=192, environment_steps=sum(r['env_steps'] for r in rows), model_loaded=False, GPU_used=False))
    shutil.copytree(out, durable, dirs_exist_ok=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['bank', 'reference', 'output', 'durable']: p.add_argument('--'+name, required=True)
    p.add_argument('--preflight-only', action='store_true'); args = p.parse_args(); existed = Path(args.output).exists()
    try: run(args)
    except Exception as error:
        if not existed and Path(args.output).exists(): write_json(Path(args.output)/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise
