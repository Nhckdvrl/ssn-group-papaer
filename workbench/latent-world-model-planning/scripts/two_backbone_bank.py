"""E13 A6: separate-process Fast producer / released LeWM reference scorer."""
import argparse
import inspect
import json
from pathlib import Path
import shutil
import sys
import h5py
import hdf5plugin
import numpy as np
import torch
from first_wave import image_tensor, native_info, restore, sha256, sync_time, write_json

SEED = 81000
FRACTIONS = [.1, .2, .3, .5]


def normalize(actions, norm):
    mean = torch.as_tensor(norm['mean'], device=actions.device, dtype=actions.dtype)
    std = torch.as_tensor(norm['std'], device=actions.device, dtype=actions.dtype)
    return (actions-mean)/std


def physical(actions, norm, task):
    mean = torch.as_tensor(norm['mean'], device=actions.device, dtype=actions.dtype)
    std = torch.as_tensor(norm['std'], device=actions.device, dtype=actions.dtype)
    issued = actions.reshape(-1, 25, 2)*std+mean
    return issued.clamp(-1., 1.) if task == 'tworoom' else issued


class Reference:
    def __init__(self, model, initial, goal, norm): self.model, self.initial, self.goal, self.norm = model, initial, goal, norm
    def score(self, actions):
        n = len(actions); act = normalize(actions, self.norm).reshape(n, 5, 10)
        emb = self.initial.expand(n, 1, 192).clone()
        for t in range(5):
            encoded = self.model.action_encoder(act[:, :t+1])
            pred = self.model.predict(emb[:, -3:], encoded[:, -3:])[:, -1:]
            emb = torch.cat([emb, pred], 1)
        return (emb[:, -1]-self.goal[:, -1]).square().sum(-1)


def native_check(model, pixels, goal_pixels, actions, norm, score, reference):
    n = min(17, len(actions)); info = native_info(pixels, goal_pixels)
    info = {k: v.unsqueeze(1).expand(1, n, *v.shape[1:]).clone() for k, v in info.items()}
    info['consistency_loss_weight'] = 0.
    normalized = normalize(actions[:n], norm).reshape(1, n, 5 if reference else 1, 10 if reference else 50)
    expected = model.get_cost(info, normalized)[0]; actual = score(actions[:n])
    if not torch.allclose(expected, actual, rtol=1e-5, atol=1e-5): raise ValueError('Native cached scoring mismatch')
    frames = int(info['predicted_emb'].shape[2]) if reference else None
    if reference and frames != 6: raise ValueError('Expected current1 + predicted5 frames')
    return {'max_abs_error': float((expected-actual).abs().max()), 'predicted_frames': frames, 'passed': True}


def timings(score, actions, order):
    result = []
    for count in [900]+[int(900*f) for f in FRACTIONS]:
        subset = actions[order[:count]]; score(subset); seconds = []
        for _ in range(8):
            start = sync_time(); score(subset); seconds.append(sync_time()-start)
        result.append({'batch_size': count, 'warmups': 1, 'repeats': 8, 'seconds': seconds, 'median': float(np.median(seconds))})
    return result


@torch.inference_mode()
def producer(args, out):
    from recovery_forks import MacroCost
    from action_basis import solver
    import gymnasium as gym
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]; ledger = []
    assert {c['task'] for c in cfgs} == {'tworoom', 'pusht'}; write_json(out/'sources.json', cfgs)
    for source, cfg in zip(args.sources, cfgs):
        task = cfg['task']; model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        if '/vendor/fast-lewm/' not in inspect.getfile(type(model)): raise ValueError('Wrong pickle implementation for Fast')
        norm = dict(np.load(Path(source)/'action_normalization.npz')); wm_sha, cfg_sha = sha256(cfg['checkpoint']), sha256(Path(source)/'config.json')
        with h5py.File(cfg['dataset']) as f: source_actions, offsets = f['action'][:], f['ep_offset'][:]
        env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
        for h in [25, 75]:
            anchors = np.load(Path(args.prepared)/f'{task}_g{h}.npz'); anchors_sha = sha256(Path(args.prepared)/f'{task}_g{h}.npz')
            for j in range(16):
                anchor = {k: anchors[k][j] for k in anchors.files}; restore(env, anchor, SEED+j); pixels = env.render().copy()
                row_start = int(offsets[anchor['episode']])+int(anchor['start']); expert = source_actions[row_start:row_start+25]
                start = sync_time(); initial = model.encode({'pixels': image_tensor(pixels[None]).unsqueeze(0).cuda()})['emb']
                goal = model.encode({'pixels': image_tensor(anchor['goal_pixels'][None]).unsqueeze(0).cuda()})['emb']; encoding = sync_time()-start
                native = MacroCost(model, initial, goal)
                def score(actions): return native.get_cost({}, normalize(actions, norm).reshape(1, -1, 1, 50))[0]
                class Capture:
                    def __init__(self): self.calls = 0; self.bank = None
                    def get_cost(self, info, actions):
                        executed = physical(actions, norm, task); scores = score(executed)
                        if self.calls == 15: self.bank = (executed.cpu().numpy(), scores.cpu().numpy())
                        self.calls += 1
                        return scores[None]
                capture = Capture(); begin = sync_time(); solver(capture, env.action_space, 25, 900, SEED+j*100, 'cuda').solve({})
                cem_seconds = sync_time()-begin; actions, scores = capture.bank; assert capture.calls == 30 and actions.shape == (900, 25, 2)
                if task == 'tworoom': assert np.max(np.abs(actions)) <= 1.
                stem = f'{task}_g{h}_{j:03d}'; np.savez_compressed(out/f'{stem}.npz', physical_actions=actions, fast_scores=scores,
                    expert_actions=expert, **dict(anchor, pixels=pixels))
                row = {'stem': stem, 'task': task, 'goal_offset': h, 'anchor': j, 'episode': int(anchor['episode']),
                    'candidate_ids': list(range(900)), 'wm_sha256': wm_sha, 'norm': norm,
                    'source_config_sha256': cfg_sha, 'anchors_sha256': anchors_sha,
                    'bank_sha256': sha256(out/f'{stem}.npz'), 'cem_seconds': cem_seconds, 'encoding_seconds': encoding,
                    'cem_cost_calls': 30, 'direct_candidate_predictions': 27000, 'unique_physical_candidates': len(np.unique(actions.reshape(900, 50), axis=0))}
                if j == 0:
                    a = torch.from_numpy(actions).cuda(); expert = torch.from_numpy(expert).float().cuda()
                    if task == 'tworoom': assert float(expert.abs().max()) <= 1.
                    row['native_control'] = native_check(model, pixels, anchor['goal_pixels'], torch.cat([expert[None], a[:16]]), norm, score, False)
                    row['heldout_prefix_max_abs_physical_action'] = float(expert.abs().max())
                    row['timings'] = timings(score, a, np.argsort(scores, kind='stable'))
                ledger.append(row); write_json(out/'ledger.json', ledger); print('fast_bank', stem, flush=True)
        env.close(); del model; torch.cuda.empty_cache()
    write_json(out/'seal.json', {'ledger_sha256': sha256(out/'ledger.json'), 'banks': len(ledger), 'truth_generated': False})


@torch.inference_mode()
def scorer(args, out):
    if 'jepa' in sys.modules or 'module' in sys.modules: raise ValueError('LeWM requires a fresh Python process')
    import build_lewm  # register the released LeWM pickle namespace before loading
    from sklearn.preprocessing import StandardScaler
    bank = Path(args.bank); seal = json.loads((bank/'seal.json').read_text())
    assert seal['ledger_sha256'] == sha256(bank/'ledger.json')
    ledger = json.loads((bank/'ledger.json').read_text()); cfgs = json.loads((bank/'sources.json').read_text()); results = []
    checkpoints = dict(zip(['tworoom', 'pusht'], args.lewm_checkpoints))
    for cfg in cfgs:
        task = cfg['task']; checkpoint = checkpoints[task]
        metadata = json.loads(Path(checkpoint).with_suffix('.metadata.json').read_text()); wm_sha = sha256(checkpoint)
        assert metadata['strict_load'] and metadata['derived_object_sha256'] == wm_sha
        assert metadata['source_revision'] == {'tworoom': '77adaae0bc31deab21c93740d1f8bb947cd0bdec', 'pusht': '22b330c28c27ead4bfd1888615af1340e3fe9052'}[task]
        model = torch.load(checkpoint, map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        if '/vendor/le-wm/' not in inspect.getfile(type(model)): raise ValueError('Wrong pickle implementation for LeWM')
        with h5py.File(cfg['dataset']) as f: actions = f['action'][:]
        scaler = StandardScaler().fit(actions[np.isfinite(actions).all(1)]); norm = {'mean': scaler.mean_, 'std': scaler.scale_}
        write_json(out/f'{task}_reference.json', {'checkpoint': checkpoint, 'metadata': metadata, 'sha256': wm_sha, 'norm': norm,
            'normalization': 'official eval full-source StandardScaler/ddof0', 'module_file': inspect.getfile(type(model)), 'T_initial': 1, 'history_capacity': 3})
        for row in [r for r in ledger if r['task'] == task]:
            assert row['bank_sha256'] == sha256(bank/f'{row["stem"]}.npz')
            data = np.load(bank/f'{row["stem"]}.npz'); a = torch.from_numpy(data['physical_actions']).cuda()
            begin = sync_time(); initial = model.encode({'pixels': image_tensor(data['pixels'][None]).unsqueeze(0).cuda()})['emb']
            goal = model.encode({'pixels': image_tensor(data['goal_pixels'][None]).unsqueeze(0).cuda()})['emb']; encoding = sync_time()-begin
            cost = Reference(model, initial, goal, norm); begin = sync_time(); values = cost.score(a).cpu().numpy(); seconds = sync_time()-begin
            assert np.isfinite(values).all(); fast_order = np.argsort(data['fast_scores'], kind='stable'); ref_order = np.argsort(values, kind='stable')
            np.save(out/f'{row["stem"]}_lewm_scores.npy', values)
            scale = max(float(np.quantile(values, .9)-np.quantile(values, .1)), 1e-8); record = dict(row, reference_seconds=seconds, reference_encoding_seconds=encoding,
                full_reference_cost_calls=1, recursive_candidate_macro_predictions=4500, reference_best_id=int(ref_order[0]), score_scale_q90_minus_q10=scale,
                reference_scores_sha256=sha256(out/f'{row["stem"]}_lewm_scores.npy'), policies=[])
            rng = np.random.default_rng(SEED+row['anchor']+row['goal_offset'])
            pools = [('Fast-900', fast_order[:30], 0), ('LeWM-ALL', np.arange(900), 1.)]
            for fraction in FRACTIONS:
                count = int(900*fraction); pools.extend([('TOP', fast_order[:count], fraction), ('RANDOM', rng.choice(900, count, replace=False), fraction)])
            for policy, ids, fraction in pools:
                selected = int(fast_order[0] if policy == 'Fast-900' else ids[np.argmin(values[ids])]); shared = set(ids)&set(ref_order[:30])
                record['policies'].append({'policy': policy, 'promotion_fraction': fraction, 'eliteK30_recall': len(shared)/30,
                    'selected_id': selected, 'selected_reference_argmin_agreement': selected == int(ref_order[0]),
                    'reference_candidates_required': 0 if policy == 'Fast-900' else len(ids),
                    'selected_physical_action_agreement': bool(np.array_equal(data['physical_actions'][selected], data['physical_actions'][ref_order[0]])),
                    'within_reference_normalized_regret': float(values[selected]-values[ref_order[0]])/scale})
            if row['anchor'] == 0:
                check = torch.cat([torch.from_numpy(data['expert_actions']).float().cuda()[None], a[:16]])
                record['reference_native_control'] = native_check(model, data['pixels'], data['goal_pixels'], check, norm, cost.score, True)
                record['reference_timings'] = timings(cost.score, a, fast_order)
                record['diagnostic_cost_calls'] = {'timings': 45, 'cached_control': 1, 'native_control': 1}
            results.append(record); write_json(out/'rows.json', results); print('lewm_reference', row['stem'], flush=True)
        del model; torch.cuda.empty_cache()
    summary = []
    for task in ['tworoom', 'pusht']:
        for h in [25, 75]:
            group = [r for r in results if r['task'] == task and r['goal_offset'] == h]; assert len(group) == 16; boot = np.random.default_rng(SEED+h).integers(0, 16, (2000, 16))
            for i in range(10):
                rows = [r['policies'][i] for r in group]; metrics = ['eliteK30_recall', 'selected_reference_argmin_agreement', 'selected_physical_action_agreement', 'within_reference_normalized_regret']
                values = np.array([[r[m] for m in metrics] for r in rows], dtype=float); ci = np.quantile(values[boot].mean(1), [.025, .975], axis=0)
                summary.append({'task': task, 'goal_offset': h, 'count': 16, 'bootstrap_repeats': 2000, 'policy': rows[0]['policy'], 'fraction': rows[0]['promotion_fraction'], **{m: {'mean': float(values[:, k].mean()), 'bootstrap95CI': ci[:, k]} for k, m in enumerate(metrics)}})
    write_json(out/'summary.json', summary)
    write_json(out/'complete.json', {'completed': True, 'banks': len(results), 'scope': 'reference ranking only, no environment branch outcomes; no truth or speedup claim'})


def run(args):
    import stable_worldmodel as swm
    torch.set_num_threads(4); torch.manual_seed(SEED); out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    helpers = ['first_wave.py', 'recovery_forks.py', 'action_basis.py', 'build_lewm.py']
    write_json(out/'config.json', {'args': vars(args), 'seed': SEED, 'fractions': FRACTIONS, 'eliteK': 30,
        'capture_call_index': 15, 'capture_index_unit': 'zero-based; 16th of 30 native CEM iterations',
        'same_bank': 'executed physical25x2, TwoRoomclip/PushTidentity; each model own full-source norm and goal embedding',
        'harness_sha256': sha256(__file__), 'helpers': {n: sha256(Path(__file__).with_name(n)) for n in helpers},
        'cem_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)), 'hardware': torch.cuda.get_device_name(),
        'scope': 'Fast-guided conditional candidate bank; LeWM-ALL is full reference scorer, not its own native CEM controller'})
    for name in ['two_backbone_bank.py']+helpers: shutil.copy2(Path(__file__).with_name(name), out/name.replace('.py', '_used.py'))
    producer(args, out) if args.phase == 'fast' else scorer(args, out)
    shutil.copytree(out, Path('/home/xiang/.cache/latent-wm-results')/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--phase', choices=['fast', 'lewm'], required=True); p.add_argument('--output', required=True)
    p.add_argument('--sources', nargs=2); p.add_argument('--prepared'); p.add_argument('--bank'); p.add_argument('--lewm-checkpoints', nargs=2)
    args = p.parse_args()
    if args.phase == 'fast' and (not args.sources or not args.prepared): p.error('Fast requires --sources and --prepared')
    if args.phase == 'lewm' and (not args.bank or not args.lewm_checkpoints): p.error('LeWM requires sealed --bank and TwoRoom/PushT --lewm-checkpoints')
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
