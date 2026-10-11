"""E16 independent seed: base training -> sealed acquisition -> four controls."""
import argparse
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import torch
from lewm_pilot import train as base_train, digest, dump
from acquisition_pilot import bank, train as method_train


def run(args):
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    previous=Path(args.previous)
    old=json.loads((previous/'config.json').read_text())
    config_path=Path('/home/xiang/.cache/huggingface/hub/models--quentinll--lewm-tworooms/snapshots/77adaae0bc31deab21c93740d1f8bb947cd0bdec/config.json')
    cache=Path('/home/xiang/.cache/huggingface/latent-wm-trained')
    checkpoint=cache/f'E16_lewm_base100_seed{args.seed}_e30.ckpt'
    dump(root/'pipeline_config.json',{'seed':args.seed,'gpu':torch.cuda.get_device_name(),
        'harness_sha256':digest(__file__),'methods':['NO-ADD','UNIFORM-COMMON-RESET','GLOBAL-U','PBB'],
        'limitation':'constant-LR pilot; seed0 first resume had a documented RNG reset'})
    base_args=SimpleNamespace(dataset=old['dataset'],previous=str(previous),architecture_config=str(config_path),
        released_checkpoint='/home/xiang/.cache/huggingface/latent-wm-derived/lewm-tworoom-object.ckpt',
        checkpoint=str(checkpoint),output=str(root/'base'),base_episodes=100,epochs=30,batch_size=128,
        eval_anchors=16,resume=None,seed=args.seed)
    base_train(base_args);torch.cuda.empty_cache()
    bank_args=SimpleNamespace(phase='bank',dataset=old['dataset'],checkpoint=str(checkpoint),output=str(root/'bank'),
        head_cache=str(cache/f'E16_heads_s{args.seed}'),model_cache=None,bank=None,base_run=str(root/'base'),
        base_cache=None,methods='NO-ADD,UNIFORM-COMMON-RESET,GLOBAL-U,PBB',seed=args.seed)
    Path(bank_args.head_cache).mkdir(parents=True,exist_ok=False)
    bank(bank_args);torch.cuda.empty_cache()
    method_args=SimpleNamespace(phase='train',dataset=old['dataset'],checkpoint=str(checkpoint),output=str(root/'methods'),
        head_cache=None,model_cache=str(cache/f'E16_methods_RTX_s{args.seed}'),bank=str(root/'bank'),
        base_run=str(root/'base'),base_cache=None,methods='NO-ADD,UNIFORM-COMMON-RESET,GLOBAL-U,PBB',seed=args.seed)
    method_train(method_args)
    dump(root/'complete.json',{'completed':True,'seed':args.seed,'independent_base_and_acquisition':True})
    target=Path('/home/xiang/.cache/latent-wm-results')/root.name
    shutil.copytree(root,target)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,choices=[1,2],required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--previous',default='/home/xiang/.cache/latent-wm-results/20261002-tworoom-native-s0')
    args=p.parse_args()
    try:run(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():dump(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
