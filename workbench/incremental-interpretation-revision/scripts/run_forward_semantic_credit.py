"""E95 queued single-GPU native comparisons, with an independent hard deadline."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time

from data import CACHE, sha
from current_open_baseline import tokenizer
from gpu_deadline import ensure_gpu_allowed
from forward_semantic_credit import prompt
from run_belief_r_credit import generated


def run(a):
    ensure_gpu_allowed()
    lock = (CACHE / 'E52/gpu-slots' / str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    torch.manual_seed(95)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root / 'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [r for r in map(json.loads, data.read_text().splitlines())
            if int(r['sentence_sha256'][:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    tasks = []
    for r in rows:
        for mode in ['NATIVE', 'RECOVERY']:
            for order in [0, 1]:
                t = prompt(r, tok, mode, order)
                t.update(mode=mode, order_index=order)
                tasks.append(t)
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out / 'predictions.jsonl').exists()
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    fixed = min(tasks, key=lambda t: (t['row']['item_id'], t['mode'], t['order_index']))
    one = generated(model, tok, fixed)
    assert generated(model, tok, fixed)['output_tokens'] == one['output_tokens']
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model / 'manifest.json'),
                  data_sha256=sha(data), code_sha256=sha(Path(__file__)),
                  builder_sha256=sha(Path(__file__).with_name('forward_semantic_credit.py')),
                  generation_helper_sha256=sha(Path(__file__).with_name('run_belief_r_credit.py')),
                  tasks=len(tasks), rows=len(rows), gpu=a.gpu, shard=a.shard, shards=a.shards,
                  seed=95, dtype='bfloat16', transformers=transformers.__version__, torch=torch.__version__,
                  instrument=dict(item_id=fixed['row']['item_id'], actual_repeat_exact=True),
                  native_prompt_suffix=fixed['prompt'][-120:], cap=64, thinking_enabled=False,
                  output_choices='a / b / c=tie; two P orders, one fixed recovery sentence',
                  scope='Actual experimental graders, not new teacher Gold; labels supplied only by prior completed Step Plan audits.')
    (a.out / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    with (a.out / 'predictions.jsonl').open('w') as stream:
        for i, task in enumerate(tasks):
            ensure_gpu_allowed()
            r = task['row']
            z = generated(model, tok, task)
            z.update(item_id=r['item_id'], source_unit=r['source_unit'], mode=task['mode'],
                     order_index=task['order_index'], candidate_order=task['candidate_order'])
            stream.write(json.dumps(z) + '\n')
            stream.flush()
            if (i + 1) % 32 == 0:
                print('E95', a.model.name, a.shard, i+1, '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out / 'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    for name in ['run_forward_semantic_credit.py', 'forward_semantic_credit.py', 'run_belief_r_credit.py']:
        (a.out / name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E95 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
