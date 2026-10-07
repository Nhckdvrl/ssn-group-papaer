"""E97 one actual concise-answer condition; original budgets and parser unchanged."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time

from data import CACHE, sha
from data_v2 import digest
from gpu_deadline import ensure_gpu_allowed
from current_open_baseline import tokenizer
from belief_r_concise import prepare
from run_belief_r_credit import generated


def run(a):
    while True:
        ensure_gpu_allowed()
        if a.after.exists() and 'predictions_sha256' in json.loads(a.after.read_text()):
            break
        time.sleep(20)
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    torch.manual_seed(97)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == sha(a.root.parent/'E93/data-v1.jsonl')
    rows = [r for r in map(json.loads, data.read_text().splitlines())
            if int(digest(r['cluster_id'])[:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    tasks = [prepare(r, tok) for r in sorted(rows, key=lambda r: r['item_id'])]
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    fixed = tasks[0]
    one = generated(model, tok, fixed)
    assert generated(model, tok, fixed)['output_tokens'] == one['output_tokens']
    assert one['stopped'] and one['valid'], 'Concise-answer instrument failed; do not launch scientific forward or change wording.'
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'), data_sha256=sha(data),
        code_sha256=sha(Path(__file__)), builder_sha256=sha(Path(__file__).with_name('belief_r_concise.py')),
        generation_helper_sha256=sha(Path(__file__).with_name('run_belief_r_credit.py')),
        predecessor_config_sha256=sha(a.after), rows=len(rows), tasks=len(rows),
        gpu=a.gpu, shard=a.shard, shards=a.shards, seed=97, dtype='bfloat16',
        transformers=transformers.__version__, torch=torch.__version__, cap=64, thinking_enabled=False,
        native_suffix=fixed['prompt'][-120:], instrument=dict(item_id=fixed['row']['item_id'],
             actual_repeat_exact=True, stopped_and_parseable=True),
        scope='Single concise formatting instruction, original questions/options/author human pragmatic Gold unchanged; raw reconstruction reused.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i, task in enumerate(tasks):
            ensure_gpu_allowed()
            p = generated(model, tok, task)
            p.update(item_id=task['row']['item_id'], operation='FORMAT_ONLY')
            f.write(json.dumps(p)+'\n')
            f.flush()
            if (i+1) % 64 == 0:
                print('E97', a.model.name, a.shard, i+1, '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_belief_r_concise.py', 'belief_r_concise.py', 'run_belief_r_credit.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E97 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out', 'after']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
