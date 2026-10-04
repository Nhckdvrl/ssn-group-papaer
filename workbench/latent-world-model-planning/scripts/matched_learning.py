"""Matched complete AD-WM components and joint Bellman representation baseline.

Uses the fixed BASE100 cache and official AD-WM pure loss functions. This
constant-LR experiment does not reproduce the published training schedule.
"""
import argparse
import ast
import copy
import gc
import hashlib
import inspect
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
import torch.nn.functional as F

WB = Path(__file__).resolve().parents[1]
REPO = WB/'vendor/ad-wm'
sys.path.insert(0, str(REPO))
from jepa import JEPA
from module import MLP, SIGReg
assert Path(inspect.getfile(JEPA)).resolve() == REPO/'jepa.py'
from lewm_pilot import architecture, digest, dump, now, native_control
from fixed_data_train_seed import load_cache, normalized_pixels, objective, state_hash

ARMS = ['ABS', 'RESIDUAL', 'FULL-AD', 'VGIQL-JOINT', 'VGIQL-SEPARATE']
ROOT = Path('/home/xiang/.cache/latent-wm-results')
HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')
UPDATES, BATCH = 5650, 128


def official_functions():
    tree = ast.parse((REPO/'train.py').read_text())
    names = {'inverse_features', 'normalized_recovery_loss', 'paper_forward'}
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == names
    namespace = {'torch': torch, 'F': F}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(REPO/'train.py'), 'exec'), namespace)
    return namespace


OFFICIAL = official_functions()


def recipe(arm):
    return SimpleNamespace(wm=SimpleNamespace(history_size=3, num_preds=1), loss=SimpleNamespace(
        sigreg=SimpleNamespace(weight=.09), inverse=SimpleNamespace(enabled=arm == 'FULL-AD',
            input_mode='predicted_transition_concat', grad_mode='detach_action_encoder', weight=.1),
        mi=SimpleNamespace(enabled=arm == 'FULL-AD', grad_mode='detach_action_encoder',
            target_normalize=True, unit_variance_prior=True, learn_posterior_logvar=False,
            target_eps=1e-6, kl_weight=.01, weight=.01)))


def make_model(cfg, seed, arm):
    torch.manual_seed(seed)
    model = architecture(cfg)
    assert type(model) is JEPA and len(model.state_dict()) == 303
    common = state_hash(model.state_dict())
    source = HF/(['E16_data_compute_s0/common_cpu_initial.pt',
        'E16_fixed_data_trainseed_RTX_s1/initial_cpu.pt',
        'E16_fixed_data_trainseed_RTX_s2/initial_cpu.pt'][seed])
    initial = torch.load(source, map_location='cpu', weights_only=False)
    assert set(initial) == set(model.state_dict()) and all(torch.equal(v, initial[k]) for k, v in model.state_dict().items())
    model.residual_target = arm in ['RESIDUAL', 'FULL-AD']
    if arm == 'FULL-AD':
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(106100+seed)
            model.inverse_head = MLP(input_dim=384, output_dim=192, hidden_dim=1024, norm_fn=torch.nn.BatchNorm1d)
            model.mi_posterior_head = MLP(input_dim=384, output_dim=192, hidden_dim=1024, norm_fn=torch.nn.BatchNorm1d)
        assert len(model.state_dict()) == 321
    return model, dict(common_initial_tensor_sha256=common, initial_source_sha256=digest(source),
        initial_source=str(source), head_seed=106100+seed if arm == 'FULL-AD' else None)


class LossContext:
    def __init__(self, model, sigreg):
        self.model, self.sigreg = model, sigreg
    def log(self, *args, **kwargs):
        pass


def bellman_loss(z, goal_rows, current_rows, goal_embeddings):
    current, following = z[:, :3], z[:, 1:]
    value = -torch.linalg.vector_norm(current-goal_embeddings, dim=-1)
    continuing = (current_rows != goal_rows).to(z.dtype)
    reward = -continuing
    # A reached image goal is absorbing; an observed departure is not a bootstrap.
    target = reward + .99*continuing*(-torch.linalg.vector_norm(following-goal_embeddings, dim=-1)).detach()
    delta = target-value
    return (torch.where(delta >= 0, .9, .1)*delta.square()).mean()


def losses(model, sigreg, x, actions, arm, device, goal_spec=None, phase='joint'):
    with torch.autocast(device, dtype=torch.bfloat16):
        if not arm.startswith('VGIQL-'):
            return OFFICIAL['paper_forward'](LossContext(model, sigreg), {'pixels': x, 'action': actions}, 'train', recipe(arm))
        encoded = model.encode({'pixels': x, 'action': actions}); z = encoded['emb']
        predicted = model.predict(z[:, :3], encoded['act_emb'][:, :3])
        pred_loss = (predicted-z[:, 1:]).square().mean(); reg = sigreg(z.transpose(0, 1))
        perm, future, self_goal, current_rows, last_rows = goal_spec
        future_z = z[:, -1:, :].expand(-1, 3, -1)
        random_z = z[perm, -1:, :].expand(-1, 3, -1)
        goals = torch.where(future[..., None], future_z, random_z)
        rows = torch.where(future, last_rows[:, None], last_rows[perm, None])
        goals = torch.where(self_goal[..., None], z[:, :3], goals)
        rows = torch.where(self_goal, current_rows, rows)
        vf = bellman_loss(z, rows, current_rows, goals)
        total = vf if phase == 'value' else pred_loss if phase == 'dynamics' else pred_loss+.09*reg+vf
        return dict(loss=total, pred_loss=pred_loss, sigreg_loss=reg, value_loss=vf)


def configure_phase(model, phase):
    model.train()
    for component in ['encoder', 'projector', 'predictor', 'action_encoder', 'pred_proj']:
        part = getattr(model, component)
        active = phase == 'joint' or (component in ['encoder', 'projector']) == (phase == 'value')
        part.requires_grad_(active)
        if not active:
            part.eval()
            for parameter in part.parameters(): parameter.grad = None


def goals_for(ix, rows, rng, device):
    n = len(ix); perm = torch.tensor(rng.permutation(n), device=device)
    future = torch.tensor(rng.random((n, 3)) < .5, device=device)
    own = torch.tensor(rng.random((n, 3)) < .2, device=device)
    current = torch.tensor(rows[ix[:, None]+np.array([0, 5, 10])], device=device)
    end = torch.tensor(rows[ix+15], device=device)
    return perm, future, own, current, end


def observation_ids(images):
    """Exact image identity, including repeated images at different source rows."""
    identities = {}
    result = []
    for image in images:
        key = hashlib.sha256(np.ascontiguousarray(image)).digest()
        if key not in identities:
            identities[key] = len(identities)
        result.append(identities[key])
    return np.asarray(result, dtype=np.int64)


def preflight(args):
    torch.set_num_threads(4)
    data = load_cache(args.cache); images, actions, starts, anchors, manifest, cfg, metadata = data
    device = args.device; mean, std = np.asarray(manifest['action_mean']), np.asarray(manifest['action_std'])
    ix = starts[:4]; x = normalized_pixels(images[ix[:, None]+np.array([0, 5, 10, 15])], device)
    ids = observation_ids(images)
    assert len(ids) == len(images)
    synthetic = np.zeros((3, 2, 2, 3), dtype=np.uint8); synthetic[2] = 1
    assert observation_ids(synthetic).tolist() == [0, 0, 1]
    a = torch.tensor((actions[ix[:, None]+np.arange(20)]-mean)/std, device=device).float().reshape(4, 4, 10)
    records = []; initial_hashes = []
    for arm in ARMS:
        model, init = make_model(cfg, 0, arm); initial_hashes.append(init['common_initial_tensor_sha256'])
        model = model.to(device).train(); sigreg = SIGReg(knots=17, num_proj=1024).to(device)
        clone = copy.deepcopy(model); rng_state = torch.get_rng_state(); gpu_state = torch.cuda.get_rng_state_all() if device == 'cuda' else None
        spec = goals_for(ix, ids, np.random.default_rng(106800), device)
        phase = 'value' if arm == 'VGIQL-SEPARATE' else 'joint'
        configure_phase(model, phase)
        values = losses(model, sigreg, x, a, arm, device, spec, phase)
        torch.set_rng_state(rng_state)
        if gpu_state is not None: torch.cuda.set_rng_state_all(gpu_state)
        if arm in ['ABS','RESIDUAL']:
            reference, mse, reg = objective(clone, sigreg, x, a, device)
            assert torch.equal(values['loss'], reference) and torch.equal(values['pred_loss'], mse) and torch.equal(values['sigreg_loss'], reg)
        elif arm == 'FULL-AD':
            with torch.autocast(device, dtype=torch.bfloat16):
                encoded = clone.encode({'pixels':x, 'action':a}); z, ae = encoded['emb'], encoded['act_emb']
                pred = clone.predict(z[:,:3], ae[:,:3]); mse = (pred-z[:,1:]).square().mean(); reg=sigreg(z.transpose(0,1))
                inv=F.mse_loss(clone.inverse(torch.cat([z[:,:3],pred],-1)), ae[:,:3].detach())
                target=ae[:,:3].detach(); flat=target.reshape(-1,192)
                target=(target-flat.mean(0))/flat.std(0,unbiased=False).clamp_min(1e-6)
                mu=clone.mi_posterior(torch.cat([z[:,:3],pred],-1))
                mi=.5*((target-mu).square()+torch.log(mu.new_tensor(2*torch.pi))).sum(-1).mean()+.01*.5*mu.square().sum(-1).mean()
                reference=mse+.09*reg+.1*inv+.01*mi
            assert torch.equal(values['loss'],reference) and torch.equal(values['inverse_loss'],inv) and torch.equal(values['mi_loss'],mi)
        assert all(torch.isfinite(v) for v in values.values())
        optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3); assert not optimizer.state
        values['loss'].backward(); assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
        torch.nn.utils.clip_grad_norm_(model.parameters(),1); optimizer.step();assert all(int(v['step'])==1 for v in optimizer.state.values())
        if arm == 'VGIQL-SEPARATE':
            configure_phase(model, 'dynamics'); optimizer=torch.optim.AdamW(model.parameters(),lr=5e-5,weight_decay=1e-3)
            second=losses(model,sigreg,x,a,arm,device,spec,'dynamics');second['loss'].backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
            torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step()
            assert all(int(v['step'])==1 for v in optimizer.state.values())
        model.eval().requires_grad_(False)
        if device == 'cuda': parity=native_control(model,x[:1,:3],x[:1,-1:],a[:1,:2])
        else: parity=None
        records.append(dict(arm=arm,init=init,losses={k:float(v.detach()) for k,v in values.items()},keys=len(model.state_dict()),parameters=sum(p.numel() for p in model.parameters()),optimizer_states=len(optimizer.state),native_parity=parity))
        del model,clone,optimizer;gc.collect()
        if device=='cuda':torch.cuda.empty_cache()
    assert len(set(initial_hashes))==1
    for seed in [1,2]:
        model,init=make_model(cfg,seed,'ABS');records.append(dict(seed_initial_control=seed,init=init));del model
    c=torch.randn(2,3,192,device=device,requires_grad=True);p=torch.randn_like(c,requires_grad=True);ae=torch.randn_like(c,requires_grad=True)
    model,_=make_model(cfg,0,'FULL-AD');model=model.to(device)
    mi=OFFICIAL['normalized_recovery_loss'](model,c,p,ae,recipe('FULL-AD'));mi.backward();assert ae.grad is None and c.grad is not None and p.grad is not None
    z=torch.tensor([[[0.],[1.],[2.],[3.]]],device=device,requires_grad=True);current_rows=torch.tensor([[0,1,2]],device=device);goal_rows=torch.tensor([[3,3,3]],device=device)
    vf=bellman_loss(z,goal_rows,current_rows,z[:,-1:,:].expand(-1,3,-1));expected=torch.tensor(.9*(.02**2+.01**2)/3,device=device)
    assert torch.allclose(vf,expected,atol=1e-8);vf.backward();assert z.grad is not None and torch.isfinite(z.grad).all()
    identity=-torch.linalg.vector_norm(z[:,:3]-z[:,:3],dim=-1);assert (identity==0).all()
    terminal_loss=bellman_loss(z,current_rows,current_rows,z[:,:3]);assert terminal_loss==0
    out=Path(args.output);assert not out.exists();out.mkdir(parents=True);shutil.copy2(__file__,out/'matched_learning_used.py')
    dump(out/'controls.json',dict(passed=True,device=device,records=records,sg_recovery_target=True,bellman_toy_manual=True,identity_value_exact_zero=True,absorbing_goal_target_exact_zero=True,exact_pixel_identity_including_duplicate_rows=True,separate_two_phase_fresh_optimizer=True,common_backbone_initial_equal=True,source_sha256=digest(__file__),official_train_sha256=digest(REPO/'train.py'),cache_manifest_sha256=digest(Path(args.cache)/'cache_manifest.json')))
    print('matched-learning preflight PASS',device,flush=True)


def train(args):
    torch.set_num_threads(4)
    run=f'20261004-E01-matched-{args.arm}-A100-s{args.seed}' if not args.arm.startswith('VGIQL-') else f'20261004-E14-{args.arm}-A100-s{args.seed}'
    out=Path('/tmp/latent-wm-runs')/run;cache=HF/run;durable=ROOT/run
    assert all(not p.exists() for p in [out,cache,durable]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'matched_learning_used.py')
    try:
        images,controls,starts,anchors,manifest,cfg,metadata=load_cache(args.cache)
        rows=observation_ids(images) if args.arm.startswith('VGIQL-') else None
        if rows is not None: np.save(out/'observation_identity_ids.npy',rows)
        model,initial=make_model(cfg,args.seed,args.arm);initial_cpu_rng=torch.get_rng_state().clone();torch.save(model.state_dict(),cache/'initial_cpu.pt')
        model=model.cuda();sigreg=SIGReg(knots=17,num_proj=1024).cuda();opt=torch.optim.AdamW(model.parameters(),lr=5e-5,weight_decay=1e-3);assert not opt.state
        phase='value' if args.arm=='VGIQL-SEPARATE' else 'joint';configure_phase(model,phase);phase_history=[]
        torch.set_rng_state(initial_cpu_rng);torch.cuda.manual_seed_all(args.seed);np.random.seed(args.seed)
        rng=np.random.default_rng(33000+args.seed);goal_rng=np.random.default_rng(106800+args.seed)
        mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std']);steps=epoch=0;logs=[];first_ix=None
        dump(out/'config.json',dict(vars(args),arm=args.arm,seed=args.seed,updates=UPDATES,batch_size=BATCH,initial=initial,hardware=torch.cuda.get_device_name(),torch_version=torch.__version__,architecture=cfg,data_manifest=manifest,cache_manifest_sha256=digest(Path(args.cache)/'cache_manifest.json'),script_sha256=digest(__file__),official_train_sha256=digest(REPO/'train.py'),vendor={n:digest(REPO/n) for n in ['jepa.py','module.py']},optimizer='fresh AdamW constant lr5e-5 wd1e-3 bf16 clip1',shuffle_seed=33000+args.seed,goal_seed=106800+args.seed,scope='matched local constant-LR training; full objective components, not original published schedule numeric reproduction'))
        shutil.copy2(Path(args.cache)/'data_manifest.json',out/'data_manifest.json');torch.cuda.reset_peak_memory_stats();tick=now()
        while steps<UPDATES:
            configure_phase(model,phase);order=rng.permutation(starts)
            for batch in range(len(starts)//BATCH):
                ix=order[batch*BATCH:(batch+1)*BATCH]
                if first_ix is None:first_ix=ix.tolist()
                x=normalized_pixels(images[ix[:,None]+np.array([0,5,10,15])],'cuda')
                a=torch.tensor((controls[ix[:,None]+np.arange(20)]-mean)/std,device='cuda').float().reshape(BATCH,4,10)
                if args.arm=='VGIQL-SEPARATE' and steps==2825:
                    assert all(int(v['step'])==2825 for v in opt.state.values());phase_history.append(dict(phase=phase,updates=2825,optimizer_states=len(opt.state)))
                    torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),steps=steps),cache/'value_phase_u2825.ckpt')
                    phase='dynamics';configure_phase(model,phase);opt=torch.optim.AdamW(model.parameters(),lr=5e-5,weight_decay=1e-3);assert not opt.state
                spec=goals_for(ix,rows,goal_rng,'cuda') if args.arm.startswith('VGIQL-') else None
                opt.zero_grad(set_to_none=True);v=losses(model,sigreg,x,a,args.arm,'cuda',spec,phase);assert torch.isfinite(v['loss']);v['loss'].backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step();steps+=1
                if steps==1 or steps%50==0 or steps==UPDATES:
                    logs.append(dict(step=steps,epoch_fraction=epoch+(batch+1)/(len(starts)//BATCH),**{k:float(t.detach()) for k,t in v.items()}));dump(out/'training.json',logs);print('matched-learning',args.arm,args.seed,steps,flush=True)
                if steps==UPDATES:break
            epoch+=1
        seconds=now()-tick;optimizer_steps=[int(v['step']) for v in opt.state.values()];assert len(optimizer_steps)==sum(1 for p in model.parameters() if p.requires_grad) and all(k==(2825 if args.arm=='VGIQL-SEPARATE' else UPDATES) for k in optimizer_steps)
        checkpoint=cache/'u5650.ckpt';torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),config=cfg,manifest=manifest,steps=steps,matched_method=args.arm,train_seed=args.seed,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),numpy_global_rng=np.random.get_state(),numpy_rng=copy.deepcopy(rng.bit_generator.state),goal_rng=copy.deepcopy(goal_rng.bit_generator.state)),str(checkpoint)+'.part');os.replace(str(checkpoint)+'.part',checkpoint)
        dump(out/'summary.json',dict(arm=args.arm,seed=args.seed,updates=steps,train_seconds=seconds,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30,checkpoint=str(checkpoint),checkpoint_sha256=digest(checkpoint),initial=initial,first_clip_ids=first_ix,final_shuffle_rng=rng.bit_generator.state,optimizer_states=len(opt.state),optimizer_expected_steps=2825 if args.arm=='VGIQL-SEPARATE' else UPDATES,phase_history=phase_history))
        dump(out/'complete.json',dict(completed=True,training_updates=steps,simulator_episodes=0));shutil.copytree(out,durable)
    except Exception as error:
        dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train']);p.add_argument('--cache',required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--output');p.add_argument('--arm',choices=ARMS);p.add_argument('--seed',type=int,choices=[0,1,2]);args=p.parse_args()
    if args.mode=='preflight':preflight(args)
    else:train(args)
