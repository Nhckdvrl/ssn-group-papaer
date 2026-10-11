"""Additional immutable published seeds, without changing earlier source code."""
import ast
import importlib.metadata
import logging
from pathlib import Path
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT, read, sha


def source(task, seed, device):
    assets=read(ROOT/'20261005-E01-intact-three-seed-assets/complete.json')
    record=next(v for v in assets['records'] if (v['task'],v['train_seed'])==(task,seed))
    assert sha(record['path'])==record['sha256'] and Path(record['path']).stat().st_size==record['bytes']
    if seed==0:
        net,scaler,meta=a.source(task,device)
        meta=dict(meta,published_train_seed=seed,three_seed_ledger_sha256=sha(ROOT/'20261005-E01-intact-three-seed-assets/complete.json'))
        return net,scaler,meta
    assert seed in [42,3072]
    folder=a.HF.parent/f'intact-e5-goal-seed{seed}/recovery_delta_full_{task}_s{seed}'
    cfg=read(folder/'config.json')
    metadata=read(folder/'multitask_metadata_epoch_5.json')
    manifest=next(v for v in read(a.VENDOR/'checkpoints/PAPER_E5_GOAL_MANIFEST.json')['training_seeds'] if v['seed']==seed)
    assert (metadata['epoch'],metadata['seed'],metadata['task'],metadata['shared_state_sha256'])==(5,seed,task,manifest['shared_state_sha256'])
    assert cfg['inverse_actor']['feature_layout']=='delta_condition_product' and cfg['predict_residual'] is False
    code=a.HF.parent/'intact-reference-code/vit_hf_0.1.7.txt'
    namespace=dict(nn=torch.nn,ViTConfig=a.ViTConfig,ViTModel=a.ViTModel,logging=logging,_TRANSFORMERS_AVAILABLE=True)
    exec(compile(ast.parse(code.read_text()),str(code),'exec'),namespace)
    encoder=namespace['vit_hf'](**{k:v for k,v in cfg['encoder'].items() if not k.startswith('_')})
    kwargs={k:(a.instantiate(v) if isinstance(v,dict) else v) for k,v in cfg.items() if k not in ['_target_','encoder']}
    net=a.jepa.JEPA(encoder=encoder,**kwargs)
    weights=torch.load(record['path'],map_location='cpu',weights_only=True)
    net.load_state_dict(weights,strict=True)
    shared=a.state_hash({k:v for k,v in weights.items() if k.startswith(('encoder.','projector.'))})
    assert shared==manifest['shared_state_sha256']
    assert len(weights)==len(net.state_dict()) and all(torch.isfinite(v).all() for v in weights.values())
    net=net.to(device).eval().requires_grad_(False)
    assert type(net) is a.jepa.JEPA and net.get_action_dim()==10 and net.actor_warmstart
    normpath=ROOT/f'20261002-{task}-native-s0/action_normalization.npz'
    norm=np.load(normpath)
    scaler=StandardScaler()
    scaler.mean_,scaler.scale_=norm['mean'],norm['std']
    scaler.var_,scaler.n_features_in_=scaler.scale_**2,2
    assert scaler.mean_.shape==scaler.scale_.shape==(2,) and (scaler.scale_>0).all()
    meta=dict(checkpoint=record,published_train_seed=seed,three_seed_ledger_sha256=sha(ROOT/'20261005-E01-intact-three-seed-assets/complete.json'),
        software_versions={name:importlib.metadata.version(name) for name in ['torch','transformers','numpy','stable-worldmodel','scikit-learn','pymunk']},
        model_config_sha256=sha(folder/'config.json'),metadata_sha256=sha(folder/'multitask_metadata_epoch_5.json'),normalizer_sha256=sha(normpath),
        shared_encoder_sha256=shared,vit_constructor_sha256=sha(code),vit_constructor_manifest=read(code.parent/'source_manifest.json'),
        runtime_sha256={file:sha(a.RUNTIME/file) for file in ['jepa.py','module.py','prior_only_solver.py','sitecustomize.py']},
        history_policy_sha256=sha(a.VENDOR/'history_policy.py'),model_state_keys=len(weights),parameters=sum(v.numel() for v in net.parameters()),revision=assets['resolved_revision'])
    return net,a.BlockStandardScaler(scaler),meta


def bank(task):return ROOT/f'20261005-E18-intact-fresh-bank48-{task}'
