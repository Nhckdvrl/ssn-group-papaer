"""E165 immutable provenance, canonical CPU loading, and bounded GPU work."""
import ast
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import time

import numpy as np
import torch
import transformers
from transformers import OlmoeForCausalLM
import e144145_common as old
from e165_core import hook_fingerprint

WB = Path(__file__).resolve().parents[2]
ROOT = WB / 'moe/results/e165'
RAW = Path.home() / 'mechpop_cache/e165_mature_olmoe_transport'
SCRIPTS = WB / 'moe/scripts'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path); path.parent.mkdir(exist_ok=True, parents=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n'); os.replace(temporary, path)


def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'size_bytes': path.stat().st_size}


def save(path, values, replace=False):
    path = Path(path)
    if path.exists() and not replace:
        raise FileExistsError('Preserve earlier E165 arrays')
    temp = path.with_name(path.name + '.tmp')
    with temp.open('wb') as f:
        np.savez_compressed(f, **values)
    os.replace(temp, path)
    return record(path)


def proof():
    pending = ['e165_assets.py', 'e165_data.py', 'e165_core.py', 'e165_common.py',
               'e165_run.py', 'e165_analyze.py', 'e165_verify.py', 'e165_selftest.py',
               'supervised_process.py']
    result = {}
    while pending:
        name = pending.pop()
        if name in result:
            continue
        p = SCRIPTS/name; result[name] = sha(p)
        for node in ast.walk(ast.parse(p.read_text())):
            imports = [a.name for a in node.names] if isinstance(node, ast.Import) else (
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for module in imports:
                candidate = module.split('.')[0]+'.py'
                if (SCRIPTS/candidate).is_file() and candidate not in result:
                    pending.append(candidate)
    return dict(sorted(result.items()))


def software():
    modules = ('transformers.models.olmoe.modeling_olmoe', 'transformers.models.olmoe.configuration_olmoe',
               'transformers.modeling_rope_utils', 'transformers.modeling_attn_mask_utils')
    return {'python': platform.python_version(), 'torch': torch.__version__,
            'transformers': transformers.__version__, 'numpy': np.__version__,
            'native_sources': {m: record(inspect.getfile(importlib.import_module(m))) for m in modules}}


def buffers(model):
    return {k: v.detach().cpu().clone() for k, v in model.named_buffers()}


def state(model, label):
    if any(v.is_meta for v in list(model.parameters())+list(model.buffers())):
        raise ValueError('Canonical source contains unresolved meta tensors')
    return {'label': label, 'parameter_hash': old.tensor_hash(model.state_dict()),
            'buffer_hash': old.tensor_hash(buffers(model)), 'hooks': hook_fingerprint(model),
            'parameters': sum(p.numel() for p in model.parameters())}


def load_cpu(labels, assets, expected=None, phase='canonical'):
    if torch.cuda.is_initialized():
        raise ValueError('All source preparation must precede CUDA initialization')
    start = time.monotonic(); models, states = [], []
    for label in labels:
        asset = assets['models'][label]
        for name, item in asset['files'].items():
            if Path(item['path']).stat().st_size != item['size_bytes']:
                raise ValueError('Canonical source size changed')
            if not name.endswith('.safetensors') and sha(item['path']) != item['sha256']:
                raise ValueError('Pinned source metadata changed')
        model = OlmoeForCausalLM.from_pretrained(asset['directory'], local_files_only=True,
                    dtype=torch.bfloat16, low_cpu_mem_usage=False, attn_implementation='eager')
        model.eval().requires_grad_(False)
        s = state(model, label)
        if s['parameters'] != 6919161856 or (expected is not None and s != expected[label]):
            raise ValueError('Canonical OLMoE model/parameters/buffers differ: '+label)
        models.append(model); states.append(s)
        print(json.dumps({'event': 'E165_CPU_ready', 'phase': phase, 'source': label,
                          'seconds': time.monotonic()-start}), flush=True)
    write(ROOT/('CPU_readiness_'+phase+'.json'), {'status': 'ready', 'sources': states,
          'seconds': time.monotonic()-start, 'CUDA_initialized': False, 'host': socket.gethostname()})
    return models, states


def readonly(models, states):
    for model, expected in zip(models, states):
        if state(model, expected['label']) != expected:
            raise ValueError('Source parameters, buffers or hooks changed')


def acquire(physical, plan, phase):
    start = time.monotonic()
    while True:
        try:
            handle = old.gpu_lock(physical)
            write(ROOT/('GPU_wait_'+phase+'.json'), {'status': 'acquired', 'physical_gpu': physical,
                  'host': socket.gethostname(), 'wait_seconds': time.monotonic()-start,
                  'scope': 'Resource confirmation and CUDA initialization, outside work timer'})
            return handle
        except (RuntimeError, BlockingIOError) as error:
            if not isinstance(error, BlockingIOError) and 'occupied' not in str(error):
                raise
            if torch.cuda.is_initialized():
                raise RuntimeError('CUDA initialized during occupied-card wait') from error
            if time.monotonic()-start >= plan['resource_wait_limit_seconds']:
                raise TimeoutError('Prepared CPU wait limit reached') from error
            write(ROOT/('GPU_wait_'+phase+'.json'), {'status': 'waiting_with_CPU_models',
                  'wait_seconds': time.monotonic()-start, 'reason': str(error), 'GPU_reserved': False})
        time.sleep(10)


class Budget(old.Budget):
    def __init__(self, plan, phase):
        self.path, self.experiment, self.phase = ROOT/'budget.json', 'e165', phase
        self.limit = plan['gpu_limit_seconds']; self.last_write = 0.

    def check(self):
        now = time.monotonic(); self.row['gpu_seconds'] = now-self.start
        exhausted = self.prior+self.row['gpu_seconds'] >= self.limit
        if now-self.last_write >= 15 or exhausted:
            write(self.path, self.state); self.last_write = now
        if exhausted:
            raise TimeoutError('E165 registered GPU package exhausted')


def checked_plan():
    p = read(ROOT/'plan.json')
    if p['source_sha256'] != proof() or p['software'] != software():
        raise ValueError('Frozen source or native software changed')
    for key in ('asset_manifest', 'data_plan', 'input', 'CPU_tests'):
        item = p[key]
        if sha(item['path']) != item['sha256']:
            raise ValueError('Frozen provenance changed: '+key)
    return p


def prepare():
    if (ROOT/'plan.json').exists():
        raise FileExistsError('Preserve frozen E165 plan')
    from e165_analyze import CONDITIONS
    assets = read(ROOT/'asset_manifest.json'); data = read(ROOT/'data_plan.json')
    test = read(ROOT/'CPU_tests.json')
    assert assets['status'] == 'complete' and test['status'] == 'passed'
    assert test['source_sha256'] == proof()
    assert data['source_sha256'] == sha(SCRIPTS/'e165_data.py')
    models, states = load_cpu('PA', assets)
    if states[0]['parameter_hash'] == states[1]['parameter_hash']:
        raise ValueError('Identical public endpoints cannot test a historical change')
    commit = subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD'], cwd=WB, text=True).strip()
    for name, digest in proof().items():
        committed = subprocess.check_output(['git', 'show', 'HEAD:workbench/mechanism-population-dynamics/moe/scripts/'+name], cwd=WB)
        if hashlib.sha256(committed).hexdigest() != digest:
            raise ValueError('Commit all numerical sources before freezing: '+name)
    result = {'experiment': 'E165', 'status': 'prepared', 'numerical_source_commit': commit,
              'source_sha256': proof(), 'software': software(), 'conditions': list(CONDITIONS),
              'subjects': data['subjects'], 'asset_manifest': record(ROOT/'asset_manifest.json'),
              'data_plan': record(ROOT/'data_plan.json'), 'input': data['data'],
              'source_records': {s['label']: s for s in states}, 'CPU_tests': record(ROOT/'CPU_tests.json'),
              'pad_token_id': data['pad_token_id'], 'keep_count': 16, 'calibration_batch_size': 2,
              'gpu_limit_seconds': 14400, 'resource_wait_limit_seconds': 7200,
              'max_concurrent_GPUs': 1, 'user_total_GPU_limit': 4, 'new_training': False,
              'scope': 'Mature OLMoE pre/post ordinary100B annealing; full source cube and targeted actual-route cross.'}
    write(ROOT/'plan.json', result)
    del models
    print(json.dumps({'status': 'prepared', 'plan_sha256': sha(ROOT/'plan.json'), 'source_files': len(result['source_sha256'])}))
