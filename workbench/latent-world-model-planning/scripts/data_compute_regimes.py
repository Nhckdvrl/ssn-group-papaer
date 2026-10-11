"""E16: nested data quantity x updates; constant-LR pilot, not official reproduction."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import time

import h5py
import numpy as np
import torch
from lewm_pilot import architecture, digest, dump, evaluate, load_training, now, pixels
from module import SIGReg

STOPS = (560, 1680, 5650)


def nested_manifest(path, original):
    if original['seed'] != 0 or len(original['base_episodes']) != 100:
        raise ValueError('Requires the locked seed0 base100 manifest')
    if len(original['evaluation_episodes']) != 48:
        raise ValueError('Requires all 48 original evaluation episodes')
    with h5py.File(path) as f:
        lengths = f['ep_len'][:]
    excluded = original['base_episodes'] + original['evaluation_episodes'] + original['excluded_previous_episodes']
    pool = np.setdiff1d(np.flatnonzero(lengths > 36), excluded)
    extra = np.random.default_rng(40000).choice(pool, 900, replace=False).tolist()
    manifest = copy.deepcopy(original)
    manifest.update(base_episodes=original['base_episodes'] + extra, base_episode_count=1000,
                    base_rows=int(sum(lengths[original['base_episodes'] + extra])),
                    base_valid_clips=int(sum(lengths[original['base_episodes'] + extra] - 20)),
                    extra_selection_seed=40000, normalization_reference='original seed0 base100')
    assert len(set(manifest['base_episodes'])) == 1000
    assert not set(manifest['base_episodes']) & set(original['evaluation_episodes'])
    assert manifest['action_mean'] == original['action_mean'] and manifest['action_std'] == original['action_std']
    return manifest


def isolated_evaluate(model, anchors, mean, std, out, prefix, rng):
    cpu, cuda = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    numpy_state, generator_state = np.random.get_state(), copy.deepcopy(rng.bit_generator.state)
    try:
        return evaluate(model, anchors, mean, std, out, prefix, 48, 0)
    finally:
        torch.set_rng_state(cpu); torch.cuda.set_rng_state_all(cuda)
        np.random.set_state(numpy_state); rng.bit_generator.state = generator_state
        model.train().requires_grad_(True)


def train_condition(args, name, manifest, initial, cpu_rng, anchors, cfg, provenance):
    out = Path(args.output) / name
    out.mkdir()
    dump(out/'data_manifest.json', manifest)
    cache, controls, starts, io = load_training(args.dataset, manifest)
    assert len(starts) == manifest['base_valid_clips']
    mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    model = architecture(cfg)
    model.load_state_dict(copy.deepcopy(initial), strict=True)
    assert all(torch.equal(model.state_dict()[k], v) for k, v in initial.items())
    model = model.cuda()
    sigreg = SIGReg(knots=17, num_proj=1024).cuda()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3)
    assert not optimizer.state
    torch.set_rng_state(cpu_rng); torch.cuda.manual_seed_all(0); np.random.seed(0)
    rng = np.random.default_rng(33000)
    torch.cuda.reset_peak_memory_stats()
    start = now(); training_seconds = 0.; step = 0; epoch = 0; logs = []; summaries = []; seen = set(); train_peak = 0
    batches = len(starts) // 128
    while step < STOPS[-1]:
        model.train().requires_grad_(True)
        order = rng.permutation(starts)
        for batch in range(batches):
            tick = now(); ix = order[batch*128:(batch+1)*128]
            seen.update(ix.tolist())
            images = pixels(cache[ix[:, None] + np.array([0, 5, 10, 15])])
            actions = torch.tensor((controls[ix[:, None] + np.arange(20)]-mean)/std,
                                   device='cuda').float().reshape(128, 4, 10)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast('cuda', dtype=torch.bfloat16):
                info = model.encode({'pixels': images, 'action': actions})
                emb = info['emb']; pred = model.predict(emb[:, :3], info['act_emb'][:, :3])
                mse = (pred-emb[:, 1:]).square().mean(); reg = sigreg(emb.transpose(0, 1)); loss = mse+.09*reg
            if not torch.isfinite(loss):
                raise ValueError(f'Nonfinite {name} loss at step {step}')
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); optimizer.step()
            step += 1; training_seconds += now()-tick
            if step == 1 or step % 25 == 0 or step in STOPS:
                logs.append({'step': step, 'epoch_fraction': epoch+(batch+1)/batches,
                             'loss': float(loss), 'pred_mse': float(mse), 'sigreg': float(reg)})
                dump(out/'training.json', logs)
            if step in STOPS:
                train_peak = max(train_peak, torch.cuda.max_memory_allocated()/2**30)
                steps = [int(s['step']) for s in optimizer.state.values()]
                assert steps and all(s == step for s in steps)
                summary = dict(condition=name, updates=step, epoch_fraction=epoch+(batch+1)/batches,
                               updates_per_epoch=batches, training_seconds=training_seconds,
                               elapsed_seconds=now()-start, initial_hdf5_read_seconds=io,
                               cached_pixel_bytes=cache.nbytes, distinct_clips_seen=len(seen),
                               training_peak_vram_gib=train_peak,
                               optimizer_parameter_states=len(steps), **provenance)
                checkpoint = Path(args.model_cache)/f'{name}_u{step}.ckpt'
                torch.save({'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict(),
                            'config': cfg, 'manifest': manifest, 'steps': step, 'metadata': summary,
                            'torch_rng': torch.get_rng_state(), 'cuda_rng': torch.cuda.get_rng_state_all(),
                            'numpy_rng': copy.deepcopy(rng.bit_generator.state)}, str(checkpoint)+'.part')
                os.replace(str(checkpoint)+'.part', checkpoint)
                summary.update(checkpoint=str(checkpoint), checkpoint_sha256=digest(checkpoint))
                eval_start = now(); torch.cuda.reset_peak_memory_stats()
                rows = isolated_evaluate(model, anchors, mean, std, out, f'u{step}', rng)
                summary.update(successes=sum(r['success'] for r in rows), n=48,
                               evaluation_seconds=now()-eval_start,
                               evaluation_peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
                torch.cuda.reset_peak_memory_stats()
                summaries.append(summary); dump(out/'summary.json', summaries)
                shutil.copytree(Path(args.output), Path(args.durable), dirs_exist_ok=True)
            if step == STOPS[-1]:
                break
        epoch += 1
    del model, optimizer, sigreg, cache, controls
    torch.cuda.empty_cache()
    return summaries


def run(args):
    out, source = Path(args.output), Path(args.base_run)
    locations = [Path(p).resolve() for p in [args.output, args.durable, args.model_cache]]
    assert all(a != b and a not in b.parents and b not in a.parents for i, a in enumerate(locations) for b in locations[i+1:])
    out.mkdir(parents=True, exist_ok=False)
    Path(args.model_cache).mkdir(parents=True, exist_ok=False)
    Path(args.durable).mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4); torch.manual_seed(0); np.random.seed(0)
    original = json.loads((source/'data_manifest.json').read_text())
    large = nested_manifest(args.dataset, original)
    shutil.copy2(source/'data_manifest.json', out/'source_data_manifest.json')
    shutil.copy2(source/'eval_anchors.npz', out/'eval_anchors.npz')
    anchors = np.load(out/'eval_anchors.npz')
    assert anchors['episode'].tolist() == original['evaluation_episodes']
    cfg = json.loads(Path(args.architecture_config).read_text())
    common = architecture(cfg); initial = copy.deepcopy(common.state_dict()); del common
    torch.save(initial, Path(args.model_cache)/'common_cpu_initial.pt')
    cpu_rng = torch.get_rng_state()
    provenance = dict(initial_sha256=digest(Path(args.model_cache)/'common_cpu_initial.pt'),
                      source_manifest_sha256=digest(source/'data_manifest.json'),
                      eval_anchors_sha256=digest(out/'eval_anchors.npz'),
                      dataset_sha256=original['dataset_sha256'], action_norm_reference='original seed0 base100')
    config = dict(vars(args), **provenance, seed=0, extra_seed=40000, shuffle_seed=33000,
                  stops=STOPS, objective='all 3 shifted MSE + .09 SIGReg(17,1024); no target detach',
                  history=3, frameskip=5, batch_size=128, precision='bf16', gradient_clip=1.,
                  optimizer='fresh AdamW', lr=5e-5, weight_decay=1e-3, scheduler='constant LR pilot',
                  clip_policy='existing range(n-20), whole episodes', architecture=cfg,
                  script_sha256=digest(__file__), lewm_pilot_sha256=digest(Path(__file__).with_name('lewm_pilot.py')),
                  builder_sha256=digest(Path(__file__).with_name('build_lewm.py')))
    dump(out/'config.json', config)
    shutil.copy2(__file__, out/'data_compute_regimes_used.py')
    for helper in ['lewm_pilot.py', 'build_lewm.py']:
        shutil.copy2(Path(__file__).with_name(helper), out/helper)
    results = []
    for name, manifest in [('BASE100', original), ('BASE1000', large)]:
        results.extend(train_condition(args, name, manifest, initial, cpu_rng, anchors, cfg, provenance))
        dump(out/'summary.json', results)
    released = torch.load(args.released_checkpoint, map_location='cpu', weights_only=False).cuda()
    with h5py.File(args.dataset) as f:
        actions = f['action'][:]; actions = actions[np.isfinite(actions).all(1)]
    mean, std = actions.mean(0), actions.std(0)
    dump(out/'released_action_norm.json', {'mean': mean, 'std': std, 'scope': 'full source dataset, ddof0',
                                         'checkpoint_sha256': digest(args.released_checkpoint)})
    rows = evaluate(released, anchors, mean, std, out, 'released', 48, 0)
    dump(out/'complete.json', {'completed': True, 'snapshots': len(results),
                              'released_successes': sum(r['success'] for r in rows), 'released_n': 48})
    shutil.copytree(out, Path(args.durable), dirs_exist_ok=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['dataset', 'base-run', 'architecture-config', 'released-checkpoint', 'model-cache', 'output', 'durable']:
        p.add_argument('--'+name, required=True)
    args = p.parse_args()
    try:
        run(args)
    except Exception as error:
        out = Path(args.output)
        if out.exists():
            dump(out/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
