"""H1 complete-matrix endpoint checks and fixed-bank selection readout."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
import controller_outcome_features as f
import controller_outcome_train as t
from experience_transfer_control_audit import ROOT, WB, read, save, sha

NAMES = ['FROZEN-WORLD', 'FINETUNE-WORLD', 'DIRECT-CONTROLLER', 'GOAL-COPY', 'CURRENT-COPY']


def hits(task, states, goal):
    if task == 'tworoom':
        return np.linalg.norm(states[:, :2]-goal, axis=-1) < 16
    angle = np.abs(states[:, 4]-goal[4])
    return (np.linalg.norm(states[:, :4]-goal[:4], axis=-1)<20) & (np.minimum(angle, 2*np.pi-angle)<np.pi/9)


@torch.inference_mode()
def run():
    a.setup()
    for task in ['tworoom', 'pusht']:
        for arm in t.ARMS:
            assert read(ROOT/f'20261005-E14-controller-outcome-{task}-{arm}-s0/complete.json')['completed']
    out = ROOT/'20261005-E14-controller-outcome-evaluation'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        training, fit, selection, differences = [], [], [], []
        bootstrap = np.random.default_rng(125003)
        for task in ['tworoom', 'pusht']:
            folder = ROOT/f'20261005-E14-controller-outcome-features-{task}'
            fc = read(folder/'config.json')
            assert fc['features_sha256'] == sha(folder/'features.npz') and fc['script_sha256'] == sha(f.__file__)
            with np.load(folder/'features.npz') as raw:
                data = {k:raw[k].copy() for k in raw.files}
            ids = np.flatnonzero((data['anchor']<32)&(data['steps']>=5)&~data['initial_success'])
            values = np.concatenate([data['z'][ids, 0], data['goal'][ids]])
            center = torch.from_numpy(values).mean(0)
            scale = torch.from_numpy(values).std(0, unbiased=False).clamp_min(.01)
            models, sampler_hashes = {}, []
            for arm in t.ARMS:
                train = ROOT/f'20261005-E14-controller-outcome-{task}-{arm}-s0'
                cfg, complete = read(train/'config.json'), read(train/'complete.json')
                assert not (train/'failure.json').exists() and read(train/'preflight.json')['passed']
                assert cfg['train_script_sha256'] == sha(t.__file__) == sha(train/'used.py') and cfg['feature_script_sha256'] == sha(f.__file__)
                assert cfg['features_sha256'] == fc['features_sha256'] and cfg['updates'] == complete['updates'] == 1000 and cfg['batch_size'] == 128 and cfg['seed'] == 0
                rng = np.random.default_rng(125001 if task == 'tworoom' else 125002)
                samples = rng.choice(ids, (1000, 128), replace=True)
                assert np.array_equal(samples, np.load(train/'sampler.npy'))
                assert cfg['sampler_sha256'] == sha(train/'sampler.npy') and cfg['valid_physical_macro_labels'] == int(data['complete_macro'][samples].sum())
                sampler_hashes.append(cfg['sampler_sha256'])
                assert sha(complete['checkpoint']) == complete['checkpoint_sha256']
                checkpoint = torch.load(complete['checkpoint'], map_location='cpu', weights_only=True)
                assert checkpoint['source'] == cfg['source'] == fc['source'] and checkpoint['arm'] == arm and checkpoint['task'] == task
                assert torch.equal(checkpoint['center'], center) and torch.equal(checkpoint['scale'], scale)
                state, initial = checkpoint['state'], torch.load(train/'initial.pt', map_location='cpu', weights_only=True)
                assert a.state_hash(state) == complete['final_active_sha256'] and a.state_hash(initial) == cfg['initial_active_sha256'] and a.state_hash(state) != a.state_hash(initial)
                assert all(torch.isfinite(v).all() for v in state.values())
                opt = checkpoint['optimizer']
                assert len(opt['param_groups']) == 1 and opt['param_groups'][0]['lr'] == cfg['learning_rate'] and opt['param_groups'][0]['weight_decay'] == .01
                assert all(int(v['step']) == 1000 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
                torch.manual_seed(0)
                model, _, source = a.source(task, 'cpu')
                assert source == cfg['source']
                if arm == 'DIRECT-CONTROLLER':
                    direct = t.Outcome(center, scale).eval()
                    assert all(torch.equal(v, initial[k]) for k,v in direct.state_dict().items())
                    assert cfg['frozen_sha256'] == a.state_hash(model.state_dict())
                    direct.load_state_dict(state, strict=True)
                    model = direct
                else:
                    expected = {k:v for k,v in model.state_dict().items() if k.startswith(('predictor.', 'pred_proj.'))}
                    assert set(expected) == set(initial) == set(state) and all(torch.equal(v, initial[k]) for k,v in expected.items())
                    frozen = {k:v for k,v in model.state_dict().items() if not k.startswith(('predictor.', 'pred_proj.'))}
                    assert cfg['frozen_sha256'] == a.state_hash(frozen)
                    all_weights = model.state_dict()
                    all_weights.update(state)
                    model.load_state_dict(all_weights, strict=True)
                    assert a.state_hash({k:v for k,v in model.state_dict().items() if not k.startswith(('predictor.', 'pred_proj.'))}) == cfg['frozen_sha256']
                active_names = list(model.named_parameters()) if arm == 'DIRECT-CONTROLLER' else [(k,p) for k,p in model.named_parameters() if k.startswith(('predictor.', 'pred_proj.'))]
                assert len(active_names) == len(opt['state']) and sum(p.numel() for _,p in active_names) == cfg['active_parameters']
                models[arm] = model.cuda().eval().requires_grad_(False)
                training.append(dict(task=task, arm=arm, passed=True, eligible_rows=len(ids), updates=1000, sampler_sha256=sha(train/'sampler.npy'), independent_initial_optimizer_norm_split_checks=True, hardware=cfg['hardware'], elapsed_seconds=complete['elapsed_seconds'], checkpoint_sha256=complete['checkpoint_sha256'], raw_artifact=str(train)))
            assert len(set(sampler_hashes)) == 1
            original, _, source = a.source(task, 'cuda')
            assert source == fc['source']
            predictions = {'FROZEN-WORLD':data['frozen'].copy(), 'GOAL-COPY':np.concatenate([data['z'][:, :1], np.repeat(data['goal'][:, None], 5, 1)], 1), 'CURRENT-COPY':np.repeat(data['z'][:, :1], 6, 1)}
            for arm in t.ARMS:
                outputs = []
                for j in range(len(data['anchor'])):
                    current, goal, previous = [torch.from_numpy(data[k][j:j+1]).cuda() for k in ['z', 'goal', 'previous']]
                    if arm == 'DIRECT-CONTROLLER':
                        future = models[arm](current[:, 0], goal, previous, torch.from_numpy(data['method'][j:j+1]).cuda())
                        pred = torch.cat([current[:, :1], future], 1)
                    else:
                        pred, _, _ = f.imagine(models[arm], original, current[:, 0], goal, previous, f.METHODS[int(data['method'][j])])
                    outputs.append(pred[0].cpu().numpy())
                predictions[arm] = np.asarray(outputs)
            np.savez_compressed(out/f'predictions_{task}.npz', **predictions)
            held = data['anchor'] >= 32
            for name in NAMES:
                for stratum, mask in [('ALL-HELD',held), ('NONINITIAL',held & ~data['initial_success']), ('FULL25',held & (data['steps']==25)), ('ABSORBED',held & ~data['initial_success'] & (data['steps']<25))]:
                    error = ((predictions[name][mask, 1:]-data['z'][mask, 1:])/scale.numpy())**2
                    fit.append(dict(task=task, predictor=name, stratum=stratum, rows=int(mask.sum()), unique_anchors=len(np.unique(data['anchor'][mask])), prefix_normalized_MSE=error.mean((0, 2)).tolist() if mask.any() else None))
            bank = ROOT/f'20261005-E14-controller-consequence-{task}'
            goals = [0]+list(range(2, 12))
            record = {(r['anchor'],r['goal_branch'],r['method']):r for r in read(bank/'rows.json')}
            per = {mode:{name:{'success':[], 'regret':[], 'recall':[]} for name in NAMES} for mode in ['INCLUDING-GOAL', 'LEAVE-GOAL-OUT']}
            for anchor in range(32, 44):
                indices = np.flatnonzero(data['anchor']==anchor)
                assert len(indices) == 33
                # Common observed start for every subgoal and controller, not only each pair.
                actual_initials = []
                traces = []
                for index in indices:
                    r = record[anchor, int(data['branch'][index]), f.METHODS[int(data['method'][index])]]
                    path = bank/f"trace_{anchor:03d}_g{int(data['branch'][index]):02d}_{r['method']}.npz"
                    assert sha(path) == r['trace_sha256']
                    with np.load(path) as raw:
                        traces.append((raw['states'].copy(), raw['commands'].copy()))
                        actual_initials.append(raw['observations'][0].copy())
                assert all(np.array_equal(image, actual_initials[0]) for image in actual_initials)
                for mode in per:
                    local = {name:{'success':[], 'regret':[], 'recall':[]} for name in NAMES}
                    support, noninitial = 0, 0
                    for goal_branch in goals:
                        target_index = next(i for i in indices if data['branch'][i] == goal_branch)
                        zgoal = data['goal'][target_index]
                        if data['initial_success'][target_index]:
                            continue
                        noninitial += 1
                        with np.load(bank/f'trace_{anchor:03d}_g{goal_branch:02d}_OPEN25.npz') as raw:
                            physical_goal = raw['goal_state'].copy()
                        valid = np.asarray([k for k,i in enumerate(indices) if mode=='INCLUDING-GOAL' or data['branch'][i] != goal_branch])
                        actual_cost = ((data['z'][indices[valid], -1]-zgoal)**2).mean(-1)
                        reachable = np.asarray([hits(task, traces[k][0], physical_goal).any() for k in valid])
                        support += int(reachable.any())
                        elite = set(np.argsort(actual_cost, kind='stable')[:3].tolist())
                        oracle = int(np.argmin(actual_cost))
                        for name in NAMES:
                            cost = ((predictions[name][indices[valid], -1]-zgoal)**2).mean(-1)
                            chosen = int(np.argmin(cost))
                            local[name]['success'].append(float(reachable[chosen]))
                            local[name]['regret'].append(float(actual_cost[chosen]-actual_cost[oracle]))
                            local[name]['recall'].append(len(elite & set(np.argsort(cost,kind='stable')[:3].tolist()))/3)
                    selection.append(dict(task=task, stratum=mode, anchor=anchor, noninitial_final_goals=noninitial, oracle_native_support=support, metrics={name:{key:float(np.mean(v)) if v else None for key,v in items.items()} for name,items in local.items()}))
                    for name in NAMES:
                        for key, vector in local[name].items():
                            per[mode][name][key].append(float(np.mean(vector)) if vector else np.nan)
            for mode in per:
                for baseline in ['FROZEN-WORLD', 'FINETUNE-WORLD', 'GOAL-COPY', 'CURRENT-COPY']:
                    for metric in ['success', 'regret', 'recall']:
                        delta = np.asarray(per[mode]['DIRECT-CONTROLLER'][metric])-np.asarray(per[mode][baseline][metric])
                        valid = delta[np.isfinite(delta)]
                        samples = bootstrap.integers(0, len(valid), (10000, len(valid)))
                        differences.append(dict(task=task, stratum=mode, method='DIRECT-CONTROLLER', baseline=baseline, metric=metric, mean_delta=float(valid.mean()), paired_held_anchor_bootstrap_95=np.quantile(valid[samples].mean(1),[.025,.975]).tolist(), unique_anchors=len(valid), train_seeds=1, source_models=1))
            print('H1 complete endpoint and held selection', task, 'PASS', flush=True)
        result = dict(completed=True, training=training, fit=fit, selection=selection, differences=differences, script_sha256=sha(__file__), full_artifact=str(out), scope='H0 task-subgoal absorption, fixed supplied-experience candidate bank. Train32/held12 anchors per task, one source0/head seed. Held queries exclude initial successes and separately leave matching subgoal out. Native labels/evaluation future actions never predictor input. This is not deployed hierarchical planning or a fixed-duration option method; H2 separates that interface. CIs over anchors omit training variation; unknown published pretraining overlap.')
        save(out/'result.json', result)
        save(WB/'results/E14_20261005_controller_outcome_learning_results.json', result)
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    run()
