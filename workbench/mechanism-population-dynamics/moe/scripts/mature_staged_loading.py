"""Native CPU-first loading from verified node-local copies of existing assets."""
from pathlib import Path
import hashlib
import json
import socket


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def verify(manifest_path):
    path=Path(manifest_path);data=json.loads(path.read_text())
    if data.get('status')!='complete' or set(data.get('models',{}))!={'P','A','B'}:
        raise ValueError('Completed local staging of all three fixed checkpoints required')
    if data.get('host',socket.gethostname()).split('.')[0]!=socket.gethostname().split('.')[0]:
        raise ValueError('Node-local checkpoint manifest belongs to a different host')
    for label,record in data['models'].items():
        root=Path(record['execution_root'])
        if not root.is_dir() or len([x for x in record['files'] if x.endswith('.safetensors')])!=11:
            raise ValueError('Incomplete local checkpoint: '+label)
        for name,proof in record['files'].items():
            file=root/name
            if file.stat().st_size!=proof['size_bytes']:
                raise ValueError('Local checkpoint file size differs: '+str(file))
            # Each large file was independently read and SHA-verified at staging.
            # The model caller checks all resulting BF16 parameters and native
            # calibration; avoid a new 163GB disk read for every experiment.
            if not name.endswith('.safetensors') and sha(file)!=proof['sha256']:
                raise ValueError('Local code/config/index/tokenizer differs: '+str(file))
    return data


def load_cpu_bf16(label,manifest_path,device='cuda:0'):
    import torch
    import e156_loading as loading
    data=verify(manifest_path);record=data['models'][label]
    cfg_cls,cls,source_root=loading._classes(label,complete=True)
    if Path(source_root).resolve()!=Path(record['source_root']).resolve():
        raise ValueError('Local copy source differs from the pinned canonical source')
    root=Path(record['execution_root']);cfg=cfg_cls.from_json_file(root/'config.json')
    model,info=cls.from_pretrained(root,config=cfg,dtype=torch.float32,local_files_only=True,
                                  attn_implementation='sdpa',output_loading_info=True)
    keys=('missing_keys','unexpected_keys','mismatched_keys','error_msgs')
    if any(k not in info or info[k] for k in keys):raise ValueError('Checkpoint loading keys differ: '+str(info))
    return loading._cpu_bf16(model).to(device).eval().requires_grad_(False)
