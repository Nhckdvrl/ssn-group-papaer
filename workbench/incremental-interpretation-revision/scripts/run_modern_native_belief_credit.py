"""E96 waits its E95 predecessor, writes native P, then scores its own frozen P pair."""
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
from modern_native_belief_credit import prompt
from reconstruction_reward import prepare, context
from run_reconstruction_reward import score


def generate(model, tok, text):
    import torch
    ids = tok.encode(text, add_special_tokens=False)
    x = torch.tensor([ids], device=model.device)
    with torch.inference_mode():
        y = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=False,
                           max_new_tokens=96, use_cache=True, pad_token_id=tok.pad_token_id)
    new = y[0, len(ids):].tolist()
    eos = model.generation_config.eos_token_id
    eos = [eos] if isinstance(eos, int) else eos or []
    stopped = bool(new and new[-1] in eos)
    return dict(text=tok.decode(new, skip_special_tokens=True), output_tokens=new,
                stopped=stopped, capped=len(new) >= 96 and not stopped,
                prompt_sha256=digest(text), prompt_tokens=len(ids), cap=96)


def run(a):
    while True:
        ensure_gpu_allowed()
        if a.after.exists() and 'predictions_sha256' in json.loads(a.after.read_text()):
            break
        time.sleep(20)
    lock = (CACHE / 'E52/gpu-slots' / str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    torch.manual_seed(96)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root / 'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [r for r in map(json.loads, data.read_text().splitlines())
            if int(digest(r['cluster_id'])[:16], 16) % a.shards == a.shard]
    assert rows
    tok = tokenizer(a.model)
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out / 'predictions.jsonl').exists()
    fixed = min(rows, key=lambda r: r['item_id'])
    fixed_prompt = prompt(fixed, 'gp', tok)
    first = generate(model, tok, fixed_prompt)
    assert generate(model, tok, fixed_prompt)['output_tokens'] == first['output_tokens']
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'),
                  data_sha256=sha(data), code_sha256=sha(Path(__file__)),
                  builder_sha256=sha(Path(__file__).with_name('modern_native_belief_credit.py')),
                  score_helper_sha256=sha(Path(__file__).with_name('run_reconstruction_reward.py')),
                  context_helper_sha256=sha(Path(__file__).with_name('reconstruction_reward.py')),
                  predecessor_config_sha256=sha(a.after), pairs=len(rows), tasks=len(rows)*6,
                  gpu=a.gpu, shard=a.shard, shards=a.shards, seed=96, dtype='bfloat16',
                  transformers=transformers.__version__, torch=torch.__version__, cap=96,
                  thinking_enabled=False, native_suffix=fixed_prompt[-120:],
                  instrument=dict(item_id=fixed['item_id'], actual_repeat_exact=True))
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i, r in enumerate(sorted(rows, key=lambda r: r['item_id'])):
            ps = {}
            for side in ['gp', 'control']:
                ensure_gpu_allowed()
                p = generate(model, tok, prompt(r, side, tok))
                p.update(item_id=r['item_id'], operation='GENERATION', source_condition=side,
                         source_unit=r['sources'][side]['source_unit'],
                         sentence_sha256=r['sources'][side]['sentence_sha256'], text_sha256=digest(p['text']))
                ps[side] = p
                f.write(json.dumps(p)+'\n')
                f.flush()
            for side in ['gp', 'control']:
                contexts = []
                for target in ['gp', 'control']:
                    ensure_gpu_allowed()
                    source = r['sources'][target]
                    z = dict(source, interpretation=ps[side]['text'].rsplit('</think>', 1)[-1])
                    task = prepare(z, tok)
                    contexts.append(context(z))
                    lp = score(model, task)
                    if i == 0 and side == target == 'gp':
                        assert score(model, task) == lp
                        config['instrument']['LP_repeat_max_delta'] = 0
                    f.write(json.dumps(dict(item_id=r['item_id'], operation='RECONSTRUCTION',
                        interpretation_condition=side, target_condition=target,
                        interpretation_sha256=digest(z['interpretation']),
                        target_sentence_sha256=source['sentence_sha256'],
                        context_sha256=task['context_sha256'], prompt_sha256=task['prompt_sha256'],
                        token_logprobs=lp, observation_tokens=len(lp), reward_sum=sum(lp), reward_mean=sum(lp)/len(lp)))+'\n')
                    f.flush()
                assert contexts[0] == contexts[1]
            print('E96', a.model.name, a.shard, i+1, '/', len(rows), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_modern_native_belief_credit.py', 'modern_native_belief_credit.py', 'reconstruction_reward.py', 'run_reconstruction_reward.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E96 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out', 'after']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
