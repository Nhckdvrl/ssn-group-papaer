"""Strict official LeWM weight load using the published architecture recipe."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import torch
from transformers import ViTConfig, ViTModel

WB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WB/'vendor/le-wm'))
from jepa import JEPA
from module import ARPredictor, Embedder, MLP


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(source):
    cfg = json.loads((source/'config.json').read_text())
    encoder = cfg['encoder']
    if encoder['size'] != 'tiny' or encoder['pretrained']:
        raise ValueError('Only the released tiny non-pretrained recipe is supported')
    # Exact equivalent of stable-pretraining 0.1.6 vit_hf(tiny, pretrained=False).
    vit_cfg = ViTConfig(hidden_size=192, num_hidden_layers=12, num_attention_heads=3,
                        intermediate_size=768, patch_size=encoder['patch_size'], image_size=encoder['image_size'])
    vit = ViTModel(vit_cfg, add_pooling_layer=False, use_mask_token=encoder['use_mask_token'])
    vit.config.interpolate_pos_encoding = True
    def component(name, constructor):
        kwargs = {k:v for k,v in cfg[name].items() if not k.startswith('_') and k!='norm_fn'}
        if name in ('projector','pred_proj'): kwargs['norm_fn'] = torch.nn.BatchNorm1d
        return constructor(**kwargs)
    model = JEPA(encoder=vit, predictor=component('predictor',ARPredictor),
        action_encoder=component('action_encoder',Embedder),
        projector=component('projector',MLP), pred_proj=component('pred_proj',MLP))
    state = torch.load(source/'weights.pt', map_location='cpu', weights_only=True)
    model.load_state_dict(state, strict=True)
    if not all(torch.isfinite(t).all() for t in model.state_dict().values()):
        raise ValueError('Nonfinite native LeWM parameters')
    return model, cfg


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();torch.set_num_threads(4);torch.manual_seed(0)
    source, output=Path(args.source),Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists(): raise FileExistsError(output)
    model,cfg=build(source);model.eval();torch.save(model,output)
    metadata={'source_revision':source.name,'code_commit':subprocess.check_output(['git','-C',str(WB/'vendor/le-wm'),'rev-parse','HEAD'],text=True).strip(),
        'weights_sha256':digest(source/'weights.pt'),'config_sha256':digest(source/'config.json'),
        'derived_object_sha256':digest(output),'harness_sha256':digest(__file__),
        'strict_load':True,'parameters':sum(p.numel() for p in model.parameters()),'state_dict_keys':len(model.state_dict()),'model_config':cfg}
    output.with_suffix('.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metadata.items() if k!='model_config'}),flush=True)
