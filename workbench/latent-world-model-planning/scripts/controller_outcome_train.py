"""H1 matched-row training, fixed budgets, frozen published visual/control modules."""
import argparse
import copy
import hashlib
import shutil
import time
import numpy as np
import torch
from torch import nn
import intact_published_control_v3 as a
import controller_outcome_features as f
from experience_transfer_control_audit import ROOT, WB, read, save, sha

HF = a.HF.parent/'controller-outcomes'
ARMS = ['FINETUNE-WORLD', 'DIRECT-CONTROLLER']


class Outcome(nn.Module):
    def __init__(self, center, scale):
        super().__init__()
        self.register_buffer('center', center.clone())
        self.register_buffer('scale', scale.clone())
        d = len(center)
        self.net = nn.Sequential(nn.Linear(2*d+13, 512), nn.GELU(), nn.Linear(512, 512), nn.GELU(), nn.Linear(512, 5*d))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, current, goal, previous, method):
        x = torch.cat([(current-self.center)/self.scale, (goal-current)/self.scale, previous, nn.functional.one_hot(method, 3).float()], -1)
        delta = self.net(x).reshape(-1, 5, len(self.center))*self.scale
        return current[:, None]+delta


def select(data):
    return np.flatnonzero((data['anchor'] < 32) & (data['steps'] >= 5) & ~data['initial_success'])


def normalization(data, ids):
    values = torch.from_numpy(np.concatenate([data['z'][ids, 0], data['goal'][ids]])).float()
    return values.mean(0), values.std(0, unbiased=False).clamp_min(.01)


def loss(model, data, ids, arm, scale):
    z, previous, commands, mask, goal, method = [data[k][ids] for k in ['z', 'previous', 'commands', 'complete_macro', 'goal', 'method']]
    if arm == 'DIRECT-CONTROLLER':
        predicted = model(z[:, 0], goal, previous, method)
        return ((predicted-z[:, 1:])/scale).square().mean()
    imagined, history = z[:, :1], previous[:, None]
    losses = []
    for k in range(5):
        imagined, history = f.step(model, imagined, history, commands[:, k])
        error = ((imagined[:, -1]-z[:, k+1])/scale).square().mean(-1)
        valid = mask[:, k].float()
        losses.append((error*valid).sum()/valid.sum().clamp_min(1))
    return torch.stack(losses).mean()


def active_state(model, arm):
    return {k:v.detach().cpu().clone() for k,v in model.state_dict().items() if arm == 'DIRECT-CONTROLLER' or k.startswith(('predictor.', 'pred_proj.'))}


def run(task, arm):
    a.setup()
    out = ROOT/f'20261005-E14-controller-outcome-{task}-{arm}-s0'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        audit = read(WB/'results/E14_20261005_controller_consequence_results.json')
        assert audit['completed'] and audit['new_continuations'] == 2904
        folder = ROOT/f'20261005-E14-controller-outcome-features-{task}'
        cfg = read(folder/'config.json')
        assert read(folder/'complete.json')['n'] == 1452 and cfg['features_sha256'] == sha(folder/'features.npz')
        assert cfg['script_sha256'] == sha(f.__file__)
        with np.load(folder/'features.npz') as raw:
            data = {k:raw[k].copy() for k in raw.files}
        ids = select(data)
        assert len(ids) and np.all(data['anchor'][ids] < 32)
        center, scale = normalization(data, ids)
        corrupted = {k:v.copy() for k,v in data.items()}
        held = data['anchor'] >= 32
        for key in ['z', 'goal', 'previous', 'commands']:
            corrupted[key][held] = 123456
        assert np.array_equal(select(corrupted), ids)
        assert all(torch.equal(x, y) for x,y in zip(normalization(corrupted, ids), [center, scale]))
        rng = np.random.default_rng(125001 if task == 'tworoom' else 125002)
        sample_ids = rng.choice(ids, (1000, 128), replace=True)
        np.save(out/'sampler.npy', sample_ids)
        torch.manual_seed(0)
        original, _, source = a.source(task, 'cuda')
        assert source == cfg['source']
        if arm == 'DIRECT-CONTROLLER':
            model = Outcome(center, scale).cuda().eval()
            with torch.no_grad():
                subset = {k:torch.from_numpy(v[:4]).cuda() for k,v in data.items()}
                assert torch.equal(model(subset['z'][:, 0], subset['goal'], subset['previous'], subset['method']), subset['z'][:, :1].expand(-1, 5, -1))
            frozen_before = a.state_hash(original.state_dict())
        else:
            model = copy.deepcopy(original)
            for name, parameter in model.named_parameters():
                parameter.requires_grad_(name.startswith(('predictor.', 'pred_proj.')))
            frozen_before = a.state_hash({k:v for k,v in model.state_dict().items() if not k.startswith(('predictor.', 'pred_proj.'))})
        initial = active_state(model, arm)
        initial_hash = a.state_hash(initial)
        torch.save(initial, out/'initial.pt')
        active = [p for p in model.parameters() if p.requires_grad]
        assert active and all(not p.requires_grad for p in original.parameters())
        optimizer = torch.optim.AdamW(active, lr=1e-3 if arm == 'DIRECT-CONTROLLER' else 1e-4, weight_decay=.01)
        assert {id(p) for group in optimizer.param_groups for p in group['params']} == {id(p) for p in active}
        cpu_model = copy.deepcopy(model).cpu().eval()
        cpu_data = {k:torch.from_numpy(v[:0].copy()) for k,v in data.items()}
        # A real first sampled batch on both devices, without any optimizer update.
        pre_ids = sample_ids[0, :4]
        cpu_data = {k:torch.from_numpy(v[pre_ids].copy()) for k,v in data.items()}
        cpu_loss = loss(cpu_model, cpu_data, torch.arange(4), arm, scale)
        cpu_loss.backward()
        tensors = {k:torch.from_numpy(v).cuda() for k,v in data.items()}
        device_scale = scale.cuda()
        cuda_loss = loss(model, tensors, torch.from_numpy(pre_ids).cuda(), arm, device_scale)
        cuda_loss.backward()
        np.testing.assert_allclose(cuda_loss.detach().cpu().numpy(), cpu_loss.detach().numpy(), atol=2e-4, rtol=1e-5)
        assert all(p.grad is None for p in model.parameters() if not p.requires_grad)
        assert all(torch.isfinite(p.grad).all() for p in active if p.grad is not None)
        assert sum(float(p.grad.abs().sum()) for p in active if p.grad is not None) > 0
        optimizer.zero_grad(set_to_none=True)
        del cpu_model, cpu_data
        save(out/'preflight.json', dict(passed=True, real_CPU_CUDA_loss=True, nonzero_finite_gradient=True, frozen_gradient_absent=True, held_mutation_train_invariance=True, zero_head_current_copy=True if arm == 'DIRECT-CONTROLLER' else None, optimizer_active_only=True))
        save(out/'config.json', dict(task=task, arm=arm, seed=0, updates=1000, batch_size=128, learning_rate=optimizer.param_groups[0]['lr'], weight_decay=.01, clip=1, source=source, features_config_sha256=sha(folder/'config.json'), features_sha256=cfg['features_sha256'], feature_script_sha256=sha(f.__file__), train_script_sha256=sha(__file__), sampler_sha256=sha(out/'sampler.npy'), initial_active_sha256=initial_hash, frozen_sha256=frozen_before, active_parameters=sum(p.numel() for p in active), eligible_rows=len(ids), unique_train_anchors=len(np.unique(data['anchor'][ids])), excluded_initial_rows=int(((data['anchor']<32)&data['initial_success']).sum()), excluded_short_rows=int(((data['anchor']<32)&~data['initial_success']&(data['steps']<5)).sum()), valid_physical_macro_labels=int(data['complete_macro'][sample_ids].sum()), direct_absorbing_prefix_labels=640000, hardware=torch.cuda.get_device_name(), feature_cache=str(folder), scope='One train seed; frozen published source0 visual/control modules, all controllers retained. Same row sampler, different predictive objects and active capacity. Train32/held12 anchors, pretraining overlap unknown. No evaluation future actions are model inputs.'))
        started = time.monotonic()
        metrics = []
        for update, batch in enumerate(sample_ids):
            optimizer.zero_grad(set_to_none=True)
            value = loss(model, tensors, torch.from_numpy(batch).cuda(), arm, device_scale)
            assert torch.isfinite(value)
            value.backward()
            torch.nn.utils.clip_grad_norm_(active, 1, error_if_nonfinite=True)
            optimizer.step()
            if update % 100 == 0 or update == 999:
                metrics.append(dict(update=update+1, loss=float(value.detach())))
                save(out/'metrics.json', metrics)
                print('H1 training', task, arm, update+1, float(value.detach()), flush=True)
        assert all(int(state['step']) == 1000 for state in optimizer.state.values()) and len(optimizer.state) == len(active)
        after = a.state_hash(original.state_dict()) if arm == 'DIRECT-CONTROLLER' else a.state_hash({k:v for k,v in model.state_dict().items() if not k.startswith(('predictor.', 'pred_proj.'))})
        assert after == frozen_before
        final = active_state(model, arm)
        assert all(torch.isfinite(v).all() for v in final.values()) and a.state_hash(final) != initial_hash
        folder_model = HF/f'{task}-{arm}-s0'
        assert not folder_model.exists()
        folder_model.mkdir(parents=True)
        path = folder_model/'model.pt'
        torch.save(dict(state=final, center=center, scale=scale, optimizer=optimizer.state_dict(), task=task, arm=arm, source=source), path)
        save(out/'complete.json', dict(completed=True, checkpoint=str(path), checkpoint_sha256=sha(path), frozen_unchanged=True, updates=1000, elapsed_seconds=time.monotonic()-started, final_active_sha256=a.state_hash(final)))
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
    p.add_argument('--arm', choices=ARMS, required=True)
    args = p.parse_args()
    run(args.task, args.arm)
