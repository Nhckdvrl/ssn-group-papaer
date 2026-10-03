"""E16: continue the locked BASE1000 epoch-end checkpoint to 30/100 epochs."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil

import h5py
import numpy as np
import torch
from data_compute_regimes import isolated_evaluate, nested_manifest
from lewm_pilot import architecture, digest, dump, load_training, now, pixels
from module import SIGReg

STOPS = (16950, 56500)


def steps(state):
    return [int(s['step']) for s in state['state'].values()]


def preflight(args):
    source = Path(args.source_run); config = json.loads((source/'config.json').read_text())
    c = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    assert {'state_dict', 'optimizer', 'config', 'manifest', 'steps', 'metadata', 'torch_rng', 'cuda_rng', 'numpy_rng'} <= c.keys()
    assert json.loads((source/'complete.json').read_text()) == dict(completed=True, snapshots=6, released_successes=39, released_n=48)
    summary = next(s for s in json.loads((source/'summary.json').read_text()) if s['condition']=='BASE1000' and s['updates']==5650)
    source_hash = digest(args.checkpoint); assert source_hash == summary['checkpoint_sha256']
    original = json.loads((source/'source_data_manifest.json').read_text()); manifest = c['manifest']
    assert manifest == nested_manifest(args.dataset, original) == json.loads((source/'BASE1000/data_manifest.json').read_text())
    assert c['config'] == config['architecture'] and c['steps']==5650 and c['metadata']['epoch_fraction']==10 and args.dataset==config['dataset']
    for key, value in dict(history=3, frameskip=5, batch_size=128, precision='bf16', gradient_clip=1., lr=5e-5, weight_decay=1e-3, shuffle_seed=33000, scheduler='constant LR pilot').items():
        assert config[key] == value, (key, config[key])
    assert config['objective']=='all 3 shifted MSE + .09 SIGReg(17,1024); no target detach'
    for filename, key in [('lewm_pilot.py', 'lewm_pilot_sha256'), ('build_lewm.py', 'builder_sha256')]:
        assert digest(Path(__file__).with_name(filename)) == config[key]
    anchors = np.load(source/'eval_anchors.npz'); assert digest(source/'eval_anchors.npz') == config['eval_anchors_sha256']
    assert anchors['episode'].tolist()==manifest['evaluation_episodes'] and len(anchors['episode'])==48
    assert not set(manifest['base_episodes']) & set(manifest['evaluation_episodes'])
    assert all(manifest[k]==original[k] for k in ['action_mean', 'action_std', 'dataset_sha256'])
    with h5py.File(args.dataset) as f:
        lengths = f['ep_len'][:]
    starts = []; offset = 0
    for ep in sorted(manifest['base_episodes']):
        n = int(lengths[ep]); starts.extend(range(offset, offset+n-20)); offset += n
    starts = np.asarray(starts); batches = len(starts)//128
    assert len(starts)==manifest['base_valid_clips'] and batches==565 and all(s%batches==0 for s in STOPS)
    rng = np.random.default_rng(33000)
    for _ in range(10): rng.permutation(starts)
    assert rng.bit_generator.state == c['numpy_rng']
    restored = np.random.default_rng(); restored.bit_generator.state = copy.deepcopy(c['numpy_rng'])
    order = rng.permutation(starts); assert np.array_equal(order, restored.permutation(starts))
    model = architecture(c['config']); model.load_state_dict(c['state_dict'], strict=True)
    assert all(torch.equal(v, model.state_dict()[k]) for k, v in c['state_dict'].items())
    model_hash = hashlib.sha256()
    for k, v in c['state_dict'].items(): model_hash.update(k.encode()); model_hash.update(v.numpy().tobytes())
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3)
    optimizer.load_state_dict(copy.deepcopy(c['optimizer'])); restored_state = optimizer.state_dict()
    assert len(steps(c['optimizer']))==297 and set(steps(c['optimizer']))=={5650}
    assert restored_state['param_groups'] == c['optimizer']['param_groups'] and all(g['lr']==5e-5 and g['weight_decay']==1e-3 for g in restored_state['param_groups'])
    for k, state in restored_state['state'].items():
        assert all(torch.equal(v, c['optimizer']['state'][k][name]) for name, v in state.items())
        assert state['step'].data_ptr()!=c['optimizer']['state'][k]['step'].data_ptr()
        state['step'].add_(1)
    assert set(steps(c['optimizer']))=={5650} and digest(args.checkpoint)==source_hash
    torch.Generator().set_state(c['torch_rng']); assert len(c['cuda_rng'])==1
    audit = dict(source_sha256=source_hash, source_updates=5650, source_epochs=10, optimizer_states=297,
                 valid_clips=len(starts), updates_per_epoch=batches, stops=STOPS, planned_total_epochs=[30, 100], source_model_sha256=model_hash.hexdigest(),
                 next_order_sha256=hashlib.sha256(order.tobytes()).hexdigest(), strict_model_load=True,
                 optimizer_deepclone=True, source_immutable=True, rng_10_epochs_regenerated=True,
                 eval_anchors_sha256=config['eval_anchors_sha256'], action_norm_reference='original seed0 base100', numpy_global_rng='seed0 as in source setup; source saved only permutation generator',
                 exposure_comparison='BASE100 u5650 is 100.892857 epochs; BASE1000 100 is approximate exposure match')
    return c, config, audit


def run(args):
    torch.set_num_threads(4)
    locations = [Path(p).resolve() for p in [args.output, args.durable, args.model_cache]]
    assert all(not p.exists() for p in locations)
    protected = [Path(args.source_run).resolve(), Path(args.checkpoint).resolve()]
    assert all(a!=b and a not in b.parents and b not in a.parents for a in locations for b in locations+protected if a is not b)
    c, config, audit = preflight(args)
    if args.cpu_only:
        print(json.dumps(audit, indent=2)); return
    for p in locations: p.mkdir(parents=True, exist_ok=False)
    out = Path(args.output); dump(out/'cpu_controls.json', audit)
    config.update(vars(args), stops=STOPS, continuation=audit, script_sha256=digest(__file__), optimizer='deep-cloned full-state AdamW resume', hardware=torch.cuda.get_device_name())
    dump(out/'config.json', config); dump(out/'data_manifest.json', c['manifest'])
    for name in ['data_exposure_continue.py', 'data_compute_regimes.py', 'lewm_pilot.py', 'build_lewm.py']:
        shutil.copy2(Path(__file__).with_name(name), out/name)
    shutil.copy2(Path(args.source_run)/'eval_anchors.npz', out/'eval_anchors.npz')
    cache, controls, starts, io = load_training(args.dataset, c['manifest']); assert len(starts)==audit['valid_clips']
    anchors = np.load(out/'eval_anchors.npz'); mean, std = [np.asarray(c['manifest'][k]) for k in ['action_mean', 'action_std']]
    model = architecture(c['config']); model.load_state_dict(c['state_dict'], strict=True); model = model.cuda()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); optimizer.load_state_dict(copy.deepcopy(c['optimizer']))
    assert set(steps(optimizer.state_dict()))=={5650} and set(steps(c['optimizer']))=={5650}
    sigreg = SIGReg(knots=17, num_proj=1024).cuda(); rng = np.random.default_rng()
    torch.set_rng_state(c['torch_rng']); torch.cuda.set_rng_state_all(c['cuda_rng']); rng.bit_generator.state = copy.deepcopy(c['numpy_rng']); np.random.seed(0)
    begin = now(); training_seconds = 0.; step = 5650; logs = []; summaries = []; torch.cuda.reset_peak_memory_stats()
    for epoch in range(10, 100):
        model.train().requires_grad_(True); order = rng.permutation(starts)
        for batch in range(565):
            tick = now(); ix = order[batch*128:(batch+1)*128]
            images = pixels(cache[ix[:, None]+np.array([0, 5, 10, 15])])
            actions = torch.tensor((controls[ix[:, None]+np.arange(20)]-mean)/std, device='cuda').float().reshape(128, 4, 10)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast('cuda', dtype=torch.bfloat16):
                info = model.encode({'pixels': images, 'action': actions}); emb = info['emb']
                pred = model.predict(emb[:, :3], info['act_emb'][:, :3]); mse = (pred-emb[:, 1:]).square().mean()
                reg = sigreg(emb.transpose(0, 1)); loss = mse+.09*reg
            assert torch.isfinite(loss), f'Nonfinite loss at {step}'
            loss.backward(); norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); assert torch.isfinite(norm)
            optimizer.step(); step += 1; training_seconds += now()-tick
            if step%25==0 or step in STOPS:
                logs.append(dict(step=step, epoch_fraction=epoch+(batch+1)/565, loss=float(loss), pred_mse=float(mse), sigreg=float(reg))); dump(out/'training.json', logs)
            if step in STOPS:
                assert batch==564 and set(steps(optimizer.state_dict()))=={step} and set(steps(c['optimizer']))=={5650}
                assert digest(args.checkpoint)==audit['source_sha256']
                summary = dict(condition='BASE1000', updates=step, epochs=epoch+1, epoch_fraction=epoch+1, optimizer_parameter_states=297,
                               training_seconds=training_seconds, elapsed_seconds=now()-begin, initial_hdf5_read_seconds=io,
                               cached_pixel_bytes=cache.nbytes, training_peak_vram_gib=torch.cuda.max_memory_allocated()/2**30, **audit)
                checkpoint = Path(args.model_cache)/f'BASE1000_u{step}.ckpt'
                torch.save(dict(state_dict=model.state_dict(), optimizer=optimizer.state_dict(), config=c['config'], manifest=c['manifest'], steps=step, metadata=summary,
                                torch_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(), numpy_rng=copy.deepcopy(rng.bit_generator.state), numpy_global_rng=np.random.get_state()), str(checkpoint)+'.part')
                os.replace(str(checkpoint)+'.part', checkpoint); summary.update(checkpoint=str(checkpoint), checkpoint_sha256=digest(checkpoint))
                eval_start = now(); rows = isolated_evaluate(model, anchors, mean, std, out, f'u{step}', rng)
                assert len(rows)==48; summary.update(successes=sum(r['success'] for r in rows), n=48, evaluation_seconds=now()-eval_start)
                summaries.append(summary); dump(out/'summary.json', summaries); shutil.copytree(out, args.durable, dirs_exist_ok=True)
        print('epoch', epoch+1, 'updates', step, flush=True)
    assert step==STOPS[-1] and len(summaries)==2
    dump(out/'complete.json', dict(completed=True, snapshots=2, updates=step, source_immutable=digest(args.checkpoint)==audit['source_sha256']))
    shutil.copytree(out, args.durable, dirs_exist_ok=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['dataset', 'source-run', 'checkpoint', 'model-cache', 'output', 'durable']: p.add_argument('--'+name, required=True)
    p.add_argument('--cpu-only', action='store_true'); args = p.parse_args()
    existed = Path(args.output).exists()
    try: run(args)
    except Exception as error:
        if not existed and Path(args.output).exists(): dump(Path(args.output)/'failure.json', dict(error=type(error).__name__, message=str(error)))
        raise
