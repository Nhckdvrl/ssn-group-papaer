"""E98 direct actual uses; no hidden patch, no LP proxy, independent deadline."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import time

from data import CACHE, sha
from data_v2 import digest
from gpu_deadline import ensure_gpu_allowed
from current_open_baseline import tokenizer
from query_guidance_fidelity import prepare, MODES


def generate(model, tok, task):
    import torch
    ids = tok.encode(task['prompt'], add_special_tokens=False)
    x = torch.tensor([ids], device=model.device)
    with torch.inference_mode():
        y = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=False,
                           max_new_tokens=task['cap'], use_cache=True, pad_token_id=tok.pad_token_id)
    new = y[0, len(ids):].tolist()
    eos = model.generation_config.eos_token_id
    eos = [eos] if isinstance(eos, int) else eos or []
    stopped = bool(new and new[-1] in eos)
    text = tok.decode(new, skip_special_tokens=True)
    match = re.fullmatch(r'\s*(yes|no)\s*[.!。]?\s*', text, flags=re.I)
    answer = match.group(1).title() if match else None
    return dict(text=text, text_sha256=digest(text), output_tokens=new, answer=answer,
                stopped=stopped, capped=len(new) >= task['cap'] and not stopped,
                prompt_sha256=digest(task['prompt']), prompt_tokens=len(ids), cap=task['cap'])


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
    torch.manual_seed(98)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [r for r in map(json.loads, data.read_text().splitlines())
            if int(digest(r['cluster_id'])[:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    tasks = []
    for r in sorted(rows, key=lambda r: r['item_id']):
        for mode in MODES:
            pair = [prepare(r, tok, mode, readout) for readout in ['QA', 'PARAPHRASE']]
            assert pair[0]['source_prefix_tokens'] == pair[1]['source_prefix_tokens']
            tasks.extend(pair)
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    instrument = []
    for task in tasks[:6]:
        first = generate(model, tok, task)
        assert generate(model, tok, task)['output_tokens'] == first['output_tokens']
        assert first['text'].strip(), 'Empty instrument output.'
        if task['readout'] == 'QA':
            assert first['stopped'] and first['answer'] in ['Yes', 'No'], 'Actual QA instrument unparseable.'
        instrument.append(dict(mode=task['mode'], readout=task['readout'], repeat_exact=True,
                               stopped=first['stopped'], capped=first['capped'], text_sha256=first['text_sha256'],
                               parseable_QA=task['readout'] != 'QA' or first['answer'] is not None))
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'), data_sha256=sha(data),
        code_sha256=sha(Path(__file__)), builder_sha256=sha(Path(__file__).with_name('query_guidance_fidelity.py')),
        predecessor_config_sha256=sha(a.after), rows=len(rows), tasks=len(tasks),
        gpu=a.gpu, shard=a.shard, shards=a.shards, seed=98, dtype='bfloat16',
        transformers=transformers.__version__, torch=torch.__version__, thinking_enabled=False,
        cap=dict(QA=64, PARAPHRASE=96), source_prefix_same_per_mode=True, instrument=instrument,
        instrument_amendment='One fixed first-P cap is an unknown outcome, not a reason to select or discard a shard; full100Source scope retained, QA strict gate unchanged.',
        scope='Actual native uses; equal source prefix across QA/role, not evidence of one unique latent parse. No new source labels.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i, task in enumerate(tasks):
            ensure_gpu_allowed()
            p = generate(model, tok, task)
            p.update(item_id=task['row']['item_id'], mode=task['mode'], readout=task['readout'],
                     sentence_sha256=task['row']['sentence_sha256'])
            f.write(json.dumps(p)+'\n')
            f.flush()
            if (i+1) % 32 == 0:
                print('E98', a.model.name, a.shard, i+1, '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_query_guidance_fidelity.py', 'query_guidance_fidelity.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E98 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out', 'after']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
