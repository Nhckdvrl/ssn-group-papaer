"""E91 one fixed teacher-forced sequence per observation reconstruction score."""
import argparse
import fcntl
import inspect
import json
import os
from pathlib import Path
import time
from data import CACHE, sha
from current_open_baseline import tokenizer
from gpu_deadline import ensure_gpu_allowed
from reconstruction_reward import prepare


def score(model, task):
    import torch
    x = torch.tensor([task['ids']], device=model.device)
    positions = task['target_positions']
    keep = len(positions)+1
    kwargs = dict(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:
        kwargs['logits_to_keep'] = keep
    with torch.inference_mode():
        logits = model(**kwargs).logits[0]
        offset = len(task['ids'])-len(logits)
        pred = logits[[p-1-offset for p in positions]].float().log_softmax(-1)
        ids = x[0, positions]
        values = pred.gather(1, ids[:, None]).squeeze(1).cpu().tolist()
    assert len(values) == len(positions) and all(v <= 0 for v in values)
    return values


def run(a):
    ensure_gpu_allowed()
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    torch.manual_seed(91)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    rows = [r for r in rows if int(r['sentence_sha256'][:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    tasks = [prepare(r, tok) for r in rows]
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    fixed = min(tasks, key=lambda t: (t['row']['source_unit'], t['row']['item_id']))
    first = score(model, fixed)
    assert score(model, fixed) == first
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'), data_sha256=sha(data),
                  code_sha256=sha(Path(__file__)), builder_sha256=sha(Path(__file__).with_name('reconstruction_reward.py')),
                  tasks=len(tasks), gpu=a.gpu, shard=a.shard, shards=a.shards, seed=91, dtype='bfloat16',
                  transformers=transformers.__version__, torch=torch.__version__,
                  instrument=dict(item_id=fixed['row']['item_id'], repeat_LP_max_delta=0,
                                  observation_tokens=len(first), source_LP_sum=sum(first)),
                  protocol='RAW observation reconstruction analogue, fixed prior/action; untrained modern grader, not ABBEL/ColBench reproduction.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as stream:
        for i, t in enumerate(sorted(tasks, key=lambda t: t['row']['item_id'])):
            ensure_gpu_allowed()
            lp = score(model, t)
            value = sum(lp)
            r = t['row']
            stream.write(json.dumps(dict(item_id=r['item_id'], source_unit=r['source_unit'], generator=r['generator'],
                                        operation=r['operation'], context_sha256=t['context_sha256'],
                                        prompt_sha256=t['prompt_sha256'], token_logprobs=lp,
                                        observation_tokens=len(lp), interpretation_tokens=len(tok.encode(r['interpretation'], add_special_tokens=False)),
                                        reward_sum=value, reward_mean=value/len(lp), reward_clipped=max(value, -.9)))+'\n')
            if i % 32 == 0:
                stream.flush()
                print('E91', a.model.name, a.shard, i+1, '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_reconstruction_reward.py', 'reconstruction_reward.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E91 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
