"""E16 fixed BASE100, independent initialization/training RNG; one endpoint at 5650."""
import argparse, copy, hashlib, importlib.metadata, json, os, shutil, time
from pathlib import Path
import h5py, hdf5plugin, numpy as np, torch
from lewm_pilot import architecture, digest, dump, evaluate, now
from module import SIGReg

UPDATES, BATCH = 5650, 128
FILES = ['pixels.npy', 'controls.npy', 'starts.npy', 'rows.npy', 'data_manifest.json', 'eval_anchors.npz', 'architecture.json']

def export(args):
    source, cache = Path(args.source_run), Path(args.cache); cfg = json.loads((source/'config.json').read_text())
    assert json.loads((source/'complete.json').read_text())['snapshots'] == 6
    manifest = json.loads((source/'source_data_manifest.json').read_text())
    assert digest(source/'source_data_manifest.json') == cfg['source_manifest_sha256'] and digest(source/'eval_anchors.npz') == cfg['eval_anchors_sha256']
    assert manifest['seed'] == 0 and len(manifest['base_episodes']) == 100 and len(manifest['evaluation_episodes']) == 48
    assert not set(manifest['base_episodes']) & set(manifest['evaluation_episodes'])
    assert cfg['dataset'] == args.dataset and manifest['base_rows'] == 9295 and manifest['base_valid_clips'] == 7295
    partial = cache.exists()
    if partial:
        assert sorted(p.name for p in cache.iterdir()) == ['pixels.npy']; images = np.load(cache/'pixels.npy', mmap_mode='r+')
        assert images.shape == (9295, 224, 224, 3) and images.dtype == np.uint8
    else: cache.mkdir(parents=True, exist_ok=False); images = np.lib.format.open_memmap(cache/'pixels.npy', mode='w+', dtype=np.uint8, shape=(9295, 224, 224, 3))
    actions, starts, rows, layout = [], [], [], []; offset = 0; tick = time.perf_counter()
    with h5py.File(args.dataset) as f:
        assert f['pixels'].dtype == np.uint8 and f['action'].shape[1:] == (2,) and f['pixels'].shape[1:] == (224, 224, 3)
        for ep in sorted(manifest['base_episodes']):
            start, n = int(f['ep_offset'][ep]), int(f['ep_len'][ep])
            assert np.all(f['ep_idx'][start:start+n] == ep) and np.array_equal(f['step_idx'][start:start+n], np.arange(n))
            chunk = f['pixels'][start:start+n]
            if not partial: images[offset:offset+n] = chunk
            assert np.array_equal(images[offset:offset+n], chunk)
            actions.append(f['action'][start:start+n]); starts.extend(range(offset, offset+n-20)); rows.extend(range(start, start+n))
            layout.append(dict(episode=ep, source_row=start, cache_row=offset, frames=n)); offset += n
    images.flush(); del images; actions = np.concatenate(actions); starts, rows = np.asarray(starts, dtype=np.int64), np.asarray(rows, dtype=np.int64)
    assert offset == 9295 and len(starts) == 7295 and np.isfinite(actions[starts[:, None]+np.arange(20)]).all()
    by_episode = {v['episode']: actions[v['cache_row']:v['cache_row']+v['frames']] for v in layout}
    original_order = np.concatenate([by_episode[ep] for ep in manifest['base_episodes']])
    finite_order = original_order[np.isfinite(original_order).all(1)]
    assert np.array_equal(finite_order.mean(0), manifest['action_mean']) and np.array_equal(np.maximum(finite_order.std(0), 1e-6), manifest['action_std'])
    np.save(cache/'controls.npy', actions); np.save(cache/'starts.npy', starts); np.save(cache/'rows.npy', rows)
    shutil.copy2(source/'source_data_manifest.json', cache/'data_manifest.json'); shutil.copy2(source/'eval_anchors.npz', cache/'eval_anchors.npz')
    shutil.copy2(cfg['architecture_config'], cache/'architecture.json'); assert json.loads((cache/'architecture.json').read_text()) == cfg['architecture']
    metadata = {'source_run': str(source), 'source_config_sha256': digest(source/'config.json'), 'source_manifest_sha256': cfg['source_manifest_sha256'],
        'eval_anchors_sha256': cfg['eval_anchors_sha256'], 'dataset_sha256_reference': manifest['dataset_sha256'], 'dataset_rehashed_during_export': False,
        'layout': layout, 'clip_policy': 'sorted whole episodes; range(n-20); no padding', 'export_seconds': time.perf_counter()-tick,
        'pixels_dtype': 'uint8', 'pixels_shape': [9295, 224, 224, 3], 'nonfinite_action_rows_preserved': int((~np.isfinite(actions).all(1)).sum()), 'all_legal_clip_actions_finite': True,
        'files': {n: {'sha256': digest(cache/n), 'bytes': (cache/n).stat().st_size} for n in FILES}}
    dump(cache/'cache_manifest.json', metadata); dump(cache/'complete.json', {'completed': True, 'cache_manifest_sha256': digest(cache/'cache_manifest.json')})
    print('export', json.dumps({'cache': str(cache), 'manifest_sha256': digest(cache/'cache_manifest.json'), 'pixel_sha256': metadata['files']['pixels.npy']['sha256']}), flush=True)

def load_cache(path):
    path = Path(path); metadata = json.loads((path/'cache_manifest.json').read_text()); complete = json.loads((path/'complete.json').read_text())
    assert complete == {'completed': True, 'cache_manifest_sha256': digest(path/'cache_manifest.json')}
    assert all(digest(path/n) == metadata['files'][n]['sha256'] and (path/n).stat().st_size == metadata['files'][n]['bytes'] for n in FILES)
    manifest = json.loads((path/'data_manifest.json').read_text()); cfg = json.loads((path/'architecture.json').read_text())
    images, controls, starts, rows = [np.load(path/n, mmap_mode='r') for n in FILES[:4]]; anchors = np.load(path/'eval_anchors.npz')
    assert images.shape == (9295, 224, 224, 3) and images.dtype == np.uint8 and controls.shape == (9295, 2)
    expected_starts, expected_rows, offset = [], [], 0
    assert [v['episode'] for v in metadata['layout']] == sorted(manifest['base_episodes'])
    for v in metadata['layout']:
        assert v['cache_row'] == offset; expected_starts.extend(range(offset, offset+v['frames']-20)); expected_rows.extend(range(v['source_row'], v['source_row']+v['frames'])); offset += v['frames']
    assert np.array_equal(starts, expected_starts) and np.array_equal(rows, expected_rows) and len(starts) == 7295
    assert np.isfinite(controls[starts[:, None]+np.arange(20)]).all()
    assert anchors['episode'].tolist() == manifest['evaluation_episodes'] and len(anchors['episode']) == 48
    assert not set(manifest['base_episodes']) & set(manifest['evaluation_episodes'])
    assert digest(path/'data_manifest.json') == metadata['source_manifest_sha256'] and digest(path/'eval_anchors.npz') == metadata['eval_anchors_sha256']
    return images, controls, starts, anchors, manifest, cfg, metadata

def normalized_pixels(array, device):
    x = torch.as_tensor(array, device=device).movedim(-1, -3).float()/255
    return (x-x.new_tensor([.485, .456, .406]).view(3, 1, 1))/x.new_tensor([.229, .224, .225]).view(3, 1, 1)

def objective(model, sigreg, images, actions, device):
    with torch.autocast(device, dtype=torch.bfloat16):
        info = model.encode({'pixels': images, 'action': actions}); emb = info['emb']
        pred = model.predict(emb[:, :3], info['act_emb'][:, :3]); mse = (pred-emb[:, 1:]).square().mean()
        reg = sigreg(emb.transpose(0, 1)); loss = mse+.09*reg
    return loss, mse, reg

def state_hash(state):
    h = hashlib.sha256()
    for name, value in state.items(): h.update(name.encode()); h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()

def cpu_preflight(args):
    import stable_worldmodel as swm  # Main runtime dependency, beyond --help imports.
    torch.set_num_threads(4); images, controls, starts, anchors, manifest, cfg, metadata = load_cache(args.cache)
    original = torch.load(args.seed0_initial, map_location='cpu', weights_only=False); records = []; initials = []
    mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    for seed in [0, 1, 2]:
        torch.manual_seed(seed); np.random.seed(seed); model = architecture(cfg); initial = copy.deepcopy(model.state_dict()); initials.append(state_hash(initial))
        if seed == 0: assert all(torch.equal(initial[k], v) for k, v in original.items()) and set(initial) == set(original)
        optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); assert not optimizer.state
        rng = np.random.default_rng(33000+seed); order = rng.permutation(starts); ix = order[:2]
        x = normalized_pixels(images[ix[:, None]+np.array([0, 5, 10, 15])], 'cpu')
        actions = torch.tensor((controls[ix[:, None]+np.arange(20)]-mean)/std).float().reshape(2, 4, 10)
        clone = architecture(cfg); clone.load_state_dict(copy.deepcopy(initial), strict=True); sigreg = SIGReg(knots=17, num_proj=1024); loss_rng = torch.get_rng_state().clone()
        loss, mse, reg = objective(model, sigreg, x, actions, 'cpu'); torch.set_rng_state(loss_rng)
        with torch.autocast('cpu', dtype=torch.bfloat16):
            info = clone.encode({'pixels': x, 'action': actions}); emb = info['emb']; pred = clone.predict(emb[:, :3], info['act_emb'][:, :3])
            reference_mse = (pred-emb[:, 1:]).square().mean(); reference_reg = sigreg(emb.transpose(0, 1)); reference_loss = reference_mse+.09*reference_reg
        assert torch.equal(loss, reference_loss) and torch.equal(mse, reference_mse) and torch.equal(reg, reference_reg)
        assert torch.isfinite(loss); loss.backward(); assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); optimizer.step(); assert all(int(v['step']) == 1 for v in optimizer.state.values())
        assert initials[-1] == state_hash(initial); saved = copy.deepcopy(rng.bit_generator.state); probe = np.random.default_rng(); probe.bit_generator.state = copy.deepcopy(saved)
        assert np.array_equal(rng.permutation(starts), probe.permutation(starts))
        records.append(dict(seed=seed, initial_tensor_sha256=initials[-1], loss=float(loss.detach()), pred_mse=float(mse.detach()), sigreg=float(reg.detach()), bf16_actual=True, manual_source_objective_exact=True, optimizer_states=len(optimizer.state), first_clip_ids=ix.tolist()))
        del model, clone, optimizer, sigreg
    assert len(set(initials)) == 3
    dump(args.output, {'passed': True, 'no_gpu': True, 'cache_manifest_sha256': digest(Path(args.cache)/'cache_manifest.json'), 'script_sha256': digest(__file__), 'seed0_tensor_exact': True, 'records': records})

def train(args):
    import stable_worldmodel as swm
    assert args.seed in [1, 2] and importlib.metadata.version('stable-worldmodel') == '0.0.6'
    out, cache, durable = map(Path, [args.output, args.model_cache, args.durable]); locations = [p.resolve() for p in [out, cache, durable]]
    assert all(a != b and a not in b.parents and b not in a.parents for i, a in enumerate(locations) for b in locations[i+1:])
    hf_root = Path(os.environ.get('HF_HOME', str(Path.home()/'.cache/huggingface'))).resolve(); assert cache.resolve().is_relative_to(hf_root)
    out.mkdir(parents=True, exist_ok=False); cache.mkdir(parents=True, exist_ok=False); durable.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4); torch.manual_seed(args.seed); np.random.seed(args.seed)
    images, controls, starts, anchors, manifest, cfg, metadata = load_cache(args.cache); mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    model = architecture(cfg); initial = copy.deepcopy(model.state_dict()); cpu_rng = torch.get_rng_state().clone(); torch.save(initial, cache/'initial_cpu.pt')
    model = model.cuda(); sigreg = SIGReg(knots=17, num_proj=1024).cuda(); optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); assert not optimizer.state
    assert len(initial) == 303 and sum(1 for _ in model.parameters()) == 297 and all(torch.equal(v, model.state_dict()[k].cpu()) for k, v in initial.items())
    torch.set_rng_state(cpu_rng); torch.cuda.manual_seed_all(args.seed); np.random.seed(args.seed); rng = np.random.default_rng(33000+args.seed)
    config = dict(vars(args), train_seed=args.seed, eval_seed=0, shuffle_seed=33000+args.seed, updates=UPDATES, batch_size=BATCH, objective='all 3 shifted MSE + .09 SIGReg(17,1024); no target detach',
        precision='bf16', gradient_clip=1., lr=5e-5, weight_decay=1e-3, optimizer='fresh AdamW', scheduler='constant LR pilot', architecture=cfg,
        cache_manifest_sha256=digest(Path(args.cache)/'cache_manifest.json'), initial_sha256=digest(cache/'initial_cpu.pt'), initial_tensor_sha256=state_hash(initial), source=metadata,
        eval_protocol='original eval48, seed0; train RNG snapshot/restored; terminal-only evaluation', hardware=torch.cuda.get_device_name(), torch_version=torch.__version__,
        script_sha256=digest(__file__), helpers={n: digest(Path(__file__).with_name(n)) for n in ['lewm_pilot.py', 'build_lewm.py']}, vendor={n: digest(Path(__file__).resolve().parents[1]/'vendor/le-wm'/n) for n in ['jepa.py', 'module.py']})
    dump(out/'config.json', config); shutil.copy2(Path(args.cache)/'data_manifest.json', out/'data_manifest.json'); shutil.copy2(Path(args.cache)/'eval_anchors.npz', out/'eval_anchors.npz')
    for n in ['fixed_data_train_seed.py', 'lewm_pilot.py', 'build_lewm.py']: shutil.copy2(Path(__file__).with_name(n), out/n)
    logs = []; step = epoch = 0; tick = now(); batches = len(starts)//BATCH; torch.cuda.reset_peak_memory_stats()
    while step < UPDATES:
        model.train().requires_grad_(True); order = rng.permutation(starts)
        for batch in range(batches):
            ix = order[batch*BATCH:(batch+1)*BATCH]; x = normalized_pixels(images[ix[:, None]+np.array([0, 5, 10, 15])], 'cuda')
            actions = torch.tensor((controls[ix[:, None]+np.arange(20)]-mean)/std, device='cuda').float().reshape(BATCH, 4, 10)
            optimizer.zero_grad(set_to_none=True); loss, mse, reg = objective(model, sigreg, x, actions, 'cuda'); assert torch.isfinite(loss)
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); optimizer.step(); step += 1
            if step == 1 or step % 25 == 0 or step == UPDATES:
                logs.append(dict(step=step, epoch_fraction=epoch+(batch+1)/batches, loss=float(loss), pred_mse=float(mse), sigreg=float(reg))); dump(out/'training.json', logs); print('train', args.seed, step, flush=True)
            if step == UPDATES: break
        epoch += 1
    train_seconds = now()-tick; train_peak = torch.cuda.max_memory_allocated()/2**30; steps = [int(s['step']) for s in optimizer.state.values()]; assert len(steps) == 297 and all(s == UPDATES for s in steps)
    cpu_state, cuda_state, numpy_state, shuffle_state = torch.get_rng_state(), torch.cuda.get_rng_state_all(), copy.deepcopy(np.random.get_state()), copy.deepcopy(rng.bit_generator.state)
    pre_eval_weights = state_hash(model.state_dict()); pre_eval_steps = [int(s['step']) for s in optimizer.state.values()]
    rng_path = cache/'training_rng_before_evaluation.pt'; torch.save(dict(cpu=cpu_state, cuda=cuda_state, numpy=numpy_state, shuffle=shuffle_state), rng_path)
    checkpoint = cache/'BASE100_u5650.ckpt'; torch.save({'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict(), 'config': cfg, 'manifest': manifest, 'steps': step,
        'torch_rng': cpu_state, 'cuda_rng': cuda_state, 'numpy_global_rng': numpy_state, 'numpy_rng': shuffle_state, 'train_seed': args.seed}, str(checkpoint)+'.part'); os.replace(str(checkpoint)+'.part', checkpoint)
    torch.manual_seed(0); torch.cuda.manual_seed_all(0); np.random.seed(0)
    eval_before = cache/'evaluation_rng_before.pt'; torch.save(dict(cpu=torch.get_rng_state(), cuda=torch.cuda.get_rng_state_all(), numpy=np.random.get_state(), eval_seed=0), eval_before)
    tick = now(); rows = evaluate(model, anchors, mean, std, out, 'u5650', 48, 0); eval_seconds = now()-tick
    torch.save(dict(cpu=torch.get_rng_state(), cuda=torch.cuda.get_rng_state_all(), numpy=np.random.get_state(), eval_seed=0), cache/'evaluation_rng_after.pt')
    torch.set_rng_state(cpu_state); torch.cuda.set_rng_state_all(cuda_state); np.random.set_state(numpy_state); rng.bit_generator.state = shuffle_state
    assert torch.equal(torch.get_rng_state(), cpu_state) and all(torch.equal(a, b) for a, b in zip(torch.cuda.get_rng_state_all(), cuda_state)) and rng.bit_generator.state == shuffle_state
    restored_numpy = np.random.get_state(); assert restored_numpy[0] == numpy_state[0] and np.array_equal(restored_numpy[1], numpy_state[1]) and restored_numpy[2:] == numpy_state[2:]
    assert pre_eval_weights == state_hash(model.state_dict()) and pre_eval_steps == [int(s['step']) for s in optimizer.state.values()]
    dump(out/'summary.json', dict(condition='BASE100', train_seed=args.seed, updates=step, epoch_fraction=epoch-1+(batch+1)/batches, train_seconds=train_seconds,
        training_peak_vram_gib=train_peak, evaluation_seconds=eval_seconds, successes=sum(r['success'] for r in rows), n=48, checkpoint=str(checkpoint), checkpoint_sha256=digest(checkpoint), training_rng_sha256=digest(rng_path)))
    dump(out/'complete.json', {'completed': True, 'updates': step, 'n': 48, 'seed': args.seed}); shutil.copytree(out, durable, dirs_exist_ok=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--mode', choices=['export', 'cpu-preflight', 'train'], required=True); p.add_argument('--cache', required=True); p.add_argument('--seed', type=int, choices=[1, 2])
    for n in ['source-run', 'dataset', 'seed0-initial', 'model-cache', 'output', 'durable']: p.add_argument('--'+n)
    args = p.parse_args()
    try: {'export': export, 'cpu-preflight': cpu_preflight, 'train': train}[args.mode](args)
    except Exception as error:
        if args.mode == 'train' and args.output and Path(args.output).exists(): dump(Path(args.output)/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
