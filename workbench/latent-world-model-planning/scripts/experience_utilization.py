"""E20 locked experience-use controls; no auxiliary loss or outcome selection."""
import argparse
import copy
import gc
import json
import os
import shutil
from pathlib import Path
import numpy as np
import torch
import effect_training as e
from fixed_data_train_seed import load_cache
from lewm_pilot import native_control

ROOT = Path('/home/xiang/.cache/latent-wm-results')
HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')
ARMS = ['IID-BRANCH', 'REPLAY-ONLY', 'MIX']
SOURCES = [HF/'E16_data_compute_s0/BASE100_u5650.ckpt',
           HF/'E16_fixed_data_trainseed_RTX_s1/BASE100_u5650.ckpt',
           HF/'E16_fixed_data_trainseed_RTX_s2/BASE100_u5650.ckpt']
LEGAL = np.array([0]+list(range(2, 12)))
OFFSETS = np.arange(0, 36, 5)


def data(args):
    branch_images, branch_actions, states, _ = e.load_bank(args.bank)
    images, actions, _, _, manifest, config, metadata = load_cache(args.cache)
    starts, owners = [], []
    for episode in metadata['layout']:
        ix = np.arange(episode['cache_row'], episode['cache_row']+episode['frames']-35)
        assert len(ix) and (ix[:, None]+OFFSETS).max() < episode['cache_row']+episode['frames']
        starts.extend(ix); owners.extend([episode['episode']]*len(ix))
    starts = np.asarray(starts, dtype=np.int64)
    assert len(starts) == 5795 and len(set(owners)) == 100
    assert np.isfinite(actions[starts[:, None]+np.arange(35)]).all()
    fresh = json.loads((ROOT/'20261004-E20-fresh-control-bank48/ledger.json').read_text())
    assert not set(manifest['base_episodes']) & {v['episode'] for v in fresh}
    return dict(branch_images=branch_images, branch_actions=branch_actions, states=states,
                images=images, actions=actions, starts=starts, manifest=manifest,
                config=config, metadata=metadata)


def sample(d, arm, branch_rng, replay_rng):
    new_n = 32 if arm == 'IID-BRANCH' else 0 if arm == 'REPLAY-ONLY' else 16
    old_n = 32-new_n
    anchors = branch_rng.integers(0, 32, new_n)
    branches = branch_rng.choice(LEGAL, new_n, replace=True)
    ix = replay_rng.choice(d['starts'], old_n, replace=True)
    frames = np.concatenate([d['branch_images'][anchors, branches],
                             d['images'][ix[:, None]+OFFSETS]])
    controls = np.concatenate([d['branch_actions'][anchors, branches],
                               d['actions'][ix[:, None]+np.arange(35)]])
    assert frames.shape == (32, 8, 224, 224, 3) and controls.shape == (32, 35, 2)
    assert np.isfinite(controls).all()
    return frames, controls, dict(branch_anchors=anchors.tolist(), branch_ids=branches.tolist(),
                                 replay_cache_starts=ix.tolist(), new_count=new_n, old_count=old_n)


def tensors(frames, actions, manifest, device):
    mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    raw = torch.as_tensor((actions-mean)/std, device=device).float().reshape(32, 7, 10)
    return e.normalized_pixels(frames, device), torch.cat([raw, torch.zeros_like(raw[:, :1])], 1), raw


def source(seed, d, device):
    checkpoint = torch.load(SOURCES[seed], map_location='cpu', weights_only=False)
    assert checkpoint['steps'] == 5650 and checkpoint['manifest'] == d['manifest']
    assert checkpoint['config'] == d['config'] and len(checkpoint['state_dict']) == 303
    torch.manual_seed(seed)
    model = e.architecture(checkpoint['config'])
    model.load_state_dict(checkpoint['state_dict'], strict=True)
    assert all(torch.equal(v, model.state_dict()[k]) for k, v in checkpoint['state_dict'].items())
    return model.to(device), checkpoint


def preflight(args):
    torch.set_num_threads(4)
    out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out/'experience_utilization_used.py')
    try:
        d = data(args); records = []
        for arm in ARMS:
            frames, actions, ids = sample(d, arm, np.random.default_rng(104800), np.random.default_rng(108000))
            # Check against the actual immutable source arrays, including terminal +35.
            n = ids['new_count']; ix = np.asarray(ids['replay_cache_starts'], dtype=np.int64)
            assert np.array_equal(frames[n:], d['images'][ix[:, None]+OFFSETS])
            assert np.array_equal(actions[n:], d['actions'][ix[:, None]+np.arange(35)])
            assert set(ids['branch_anchors']) <= set(range(32)) and 1 not in ids['branch_ids']
            model, c = source(0, d, args.device); initial = e.state_hash(model.state_dict())
            model.train(); torch.manual_seed(0)
            if args.device == 'cuda': torch.cuda.manual_seed_all(0)
            reg = e.SIGReg(knots=17, num_proj=1024).to(args.device)
            x, a, raw = tensors(frames, actions, d['manifest'], args.device)
            cpu_rng = torch.get_rng_state(); gpu_rng = torch.cuda.get_rng_state_all() if args.device == 'cuda' else None
            with torch.autocast(args.device, dtype=torch.bfloat16):
                loss, base, regularizer, aux = e.losses(model, None, reg, x, a, raw, 'PLAIN', 8, 4)
            torch.set_rng_state(cpu_rng)
            if gpu_rng is not None: torch.cuda.set_rng_state_all(gpu_rng)
            # Independently assemble every shifted target; retain base target gradients.
            with torch.autocast(args.device, dtype=torch.bfloat16):
                info = model.encode({'pixels':x, 'action':a}); z, act = info['emb'], info['act_emb']
                preds = [model.predict(z[:, h:h+3], act[:, h:h+3])[:, -1] for h in range(5)]
                expected_base = (torch.stack(preds, 1)-z[:, 3:]).square().mean()
                expected_reg = reg(z.transpose(0, 1))
                expected = expected_base+.09*expected_reg
            assert torch.equal(base, expected_base) and torch.equal(regularizer, expected_reg) and torch.equal(loss, expected) and aux == 0
            assert torch.isfinite(loss)
            opt = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); assert not opt.state
            loss.backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
            grad = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); assert torch.isfinite(grad); opt.step()
            assert len(opt.state) == 297 and all(int(v['step']) == 1 for v in opt.state.values())
            assert initial != e.state_hash(model.state_dict())
            assert e.state_hash(c['state_dict']) == initial
            model.eval()
            parity = native_control(model, x[:1, :3], x[:1, -1:], a[:1, :2]) if args.device == 'cuda' else None
            records.append(dict(arm=arm, first_batch=ids, loss=float(loss.detach()),
                                optimizer_states=len(opt.state), native_parity=parity))
            del model, opt, reg, x, a, raw, loss, base, regularizer, info, preds, z, act, expected, expected_base, expected_reg
            gc.collect()
            if args.device == 'cuda': torch.cuda.empty_cache()
        for seed in [1, 2]:
            model, _ = source(seed, d, 'cpu'); del model
        e.dump(out/'controls.json', dict(passed=True, device=args.device, records=records,
            valid_factual_clips=5795, whole_episodes=100, no_cross_episode_clips=True,
            no_query_sampling=True, all_three_sources_strict_equal=True,
            script_sha256=e.digest(__file__), loss_helper_sha256=e.digest(e.__file__),
            cache_manifest_sha256=e.digest(Path(args.cache)/'cache_manifest.json')))
        shutil.copytree(out, ROOT/out.name)
        print('experience-use preflight PASS', args.device, flush=True)
    except Exception as error:
        e.dump(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        shutil.copytree(out, ROOT/out.name); raise


def train(args):
    torch.set_num_threads(4)
    for device in ['cpu', 'cuda']:
        controls = json.loads((ROOT/f'20261005-E20-experience-{device}-preflight/controls.json').read_text())
        assert controls['passed'] and controls['script_sha256'] == e.digest(__file__) and controls['loss_helper_sha256'] == e.digest(e.__file__)
    name = f'20261005-E20-experience-{args.arm}-A100-s{args.seed}'
    out, cache, durable = Path('/tmp/latent-wm-runs')/name, HF/name, ROOT/name
    assert all(not p.exists() for p in [out, cache, durable]); out.mkdir(); cache.mkdir()
    shutil.copy2(__file__, out/'experience_utilization_used.py')
    try:
        d = data(args); model, c = source(args.seed, d, 'cuda')
        initial = e.state_hash(model.state_dict()); source_sha = e.digest(SOURCES[args.seed])
        torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed); np.random.seed(args.seed)
        reg = e.SIGReg(knots=17, num_proj=1024).cuda()
        opt = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); assert not opt.state
        brng, rrng = np.random.default_rng(104800+args.seed), np.random.default_rng(108000+args.seed)
        cfg = dict(vars(args), updates=2000, batch=32, source_checkpoint=str(SOURCES[args.seed]),
            source_checkpoint_sha256=source_sha, initial_tensor_sha256=initial,
            script_sha256=e.digest(__file__), loss_helper_sha256=e.digest(e.__file__),
            bank_complete_sha256=e.digest(Path(args.bank)/'complete.json'),
            cache_manifest_sha256=e.digest(Path(args.cache)/'cache_manifest.json'),
            objective='PLAIN five teacher future targets + .09 SIGReg on all eight frames; base target not detached',
            train_anchors=list(range(32)), query_anchors=list(range(32,44)), duplicate_branch_excluded=True,
            factual_clips=5795, batch_rng_seed=104800+args.seed, replay_rng_seed=108000+args.seed,
            optimizer='fresh AdamW lr5e-5 wd1e-3 clip1 bf16', hardware=torch.cuda.get_device_name(),
            scope='three independent train sources; shared original data and evaluation; MIX halves new-branch exposure; controls are not novel methods')
        e.dump(out/'config.json', cfg)
        summaries, logs, exposure = [], [], dict(branch_items=0, replay_items=0)
        mean, std = np.asarray(c['manifest']['action_mean']), np.asarray(c['manifest']['action_std'])
        e.dump(out/'queries_u0.json', e.audit_candidates(model, d['branch_images'], d['branch_actions'], d['states'], mean, std))
        torch.cuda.reset_peak_memory_stats(); tick = e.now()
        for step in range(1, 2001):
            frames, actions, ids = sample(d, args.arm, brng, rrng)
            if step == 1: e.dump(out/'first_batch.json', ids)
            exposure['branch_items'] += ids['new_count']; exposure['replay_items'] += ids['old_count']
            model.train(); x, a, raw = tensors(frames, actions, c['manifest'], 'cuda'); opt.zero_grad(set_to_none=True)
            with torch.autocast('cuda', dtype=torch.bfloat16): loss, base, regularizer, aux = e.losses(model, None, reg, x, a, raw, 'PLAIN', 8, 4)
            assert torch.isfinite(loss) and aux == 0; loss.backward()
            grad = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); assert torch.isfinite(grad); opt.step()
            if step == 1 or step%25 == 0:
                logs.append(dict(step=step, loss=float(loss.detach()), base=float(base.detach()), sigreg=float(regularizer.detach())))
                e.dump(out/'training.json', logs); print('experience-use', args.arm, args.seed, step, flush=True)
            if step in [600, 2000]:
                saved = dict(cpu=torch.get_rng_state(), cuda=torch.cuda.get_rng_state_all(), numpy=copy.deepcopy(np.random.get_state()), branch=copy.deepcopy(brng.bit_generator.state), replay=copy.deepcopy(rrng.bit_generator.state))
                weight_sha = e.state_hash(model.state_dict())
                rows = e.audit_candidates(model, d['branch_images'], d['branch_actions'], d['states'], mean, std)
                assert weight_sha == e.state_hash(model.state_dict()); e.dump(out/f'queries_u{step}.json', rows)
                torch.set_rng_state(saved['cpu']); torch.cuda.set_rng_state_all(saved['cuda']); np.random.set_state(saved['numpy']); brng.bit_generator.state=saved['branch']; rrng.bit_generator.state=saved['replay']
                p = cache/f'u{step}.ckpt'
                torch.save(dict(state_dict=model.state_dict(), optimizer=opt.state_dict(), steps=step, config=c['config'], manifest=c['manifest'], rng=saved), str(p)+'.part'); os.replace(str(p)+'.part', p)
                summaries.append(dict(updates=step, successes=sum(r['success'] for r in rows), n=12, checkpoint_sha256=e.digest(p)))
                e.dump(out/'summary.json', summaries)
        assert len(opt.state) == 297 and all(int(v['step']) == 2000 for v in opt.state.values())
        assert sum(exposure.values()) == 64000 and e.digest(SOURCES[args.seed]) == source_sha
        e.dump(out/'accounting.json', dict(**exposure, train_seconds=e.now()-tick, peak_vram_gib=torch.cuda.max_memory_allocated()/2**30, final_branch_rng=brng.bit_generator.state, final_replay_rng=rrng.bit_generator.state))
        e.dump(out/'complete.json', dict(completed=True, arm=args.arm, seed=args.seed, updates=2000))
        shutil.copytree(out, durable)
    except Exception as error:
        e.dump(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        shutil.copytree(out, durable); raise


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['preflight','train'])
    p.add_argument('--cache', required=True); p.add_argument('--bank', required=True)
    p.add_argument('--device', choices=['cpu','cuda'], default='cpu'); p.add_argument('--output')
    p.add_argument('--arm', choices=ARMS); p.add_argument('--seed', type=int, choices=[0,1,2])
    args = p.parse_args(); (preflight if args.mode == 'preflight' else train)(args)
