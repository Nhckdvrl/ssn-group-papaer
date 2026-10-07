"""E93 native actual forward judgments and all three observation reconstruction grades."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time
from data import CACHE, sha
from data_v2 import digest
from current_open_baseline import tokenizer
from gpu_deadline import ensure_gpu_allowed
from belief_r_credit import forward, reconstruction, parse_answer
from run_reconstruction_reward import score


def generated(model, tok, task):
    import torch
    ids = tok.encode(task['prompt'], add_special_tokens=False)
    x = torch.tensor([ids], device=model.device)
    with torch.inference_mode():
        y = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=False,
                           max_new_tokens=task['cap'], use_cache=True, pad_token_id=tok.pad_token_id)
    new = y[0, len(ids):].tolist()
    text = tok.decode(new, skip_special_tokens=True)
    answer, status = parse_answer(text)
    eos = model.generation_config.eos_token_id
    eos = [eos] if isinstance(eos, int) else (eos or [])
    stopped = bool(new and new[-1] in eos)
    capped = len(new) >= task['cap'] and not stopped
    return dict(answer=answer, parse_status=status, output_text=text, output_tokens=new,
                stopped=stopped, capped=capped, valid=answer is not None,
                lower_correct=bool(stopped and answer == task['row']['ground_truth']),
                upper_correct=bool(not stopped or answer is None or answer == task['row']['ground_truth']),
                prompt_sha256=digest(task['prompt']), prompt_tokens=len(ids), cap=task['cap'])


def run(a):
    ensure_gpu_allowed()
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    torch.manual_seed(93)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    rows = [r for r in rows if int(digest(r['cluster_id'])[:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    prepared = {r['item_id']: dict(forward={m: forward(r, tok, m) for m in ['FORWARD_DIRECT', 'FORWARD_COT']},
                                 rec={c: reconstruction(r, c, tok) for c in 'abc'}) for r in rows}
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
    fixed = min(rows, key=lambda r: r['item_id'])
    ft = prepared[fixed['item_id']]['forward']['FORWARD_DIRECT']
    one = generated(model, tok, ft)
    assert generated(model, tok, ft)['output_tokens'] == one['output_tokens']
    rt = prepared[fixed['item_id']]['rec']['a']
    lp = score(model, rt)
    assert score(model, rt) == lp
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'), data_sha256=sha(data),
                  code_sha256=sha(Path(__file__)), builder_sha256=sha(Path(__file__).with_name('belief_r_credit.py')),
                  score_helper_sha256=sha(Path(__file__).with_name('run_reconstruction_reward.py')),
                  rows=len(rows), forward_outputs=len(rows)*2, reconstruction_scores=len(rows)*3,
                  gpu=a.gpu, shard=a.shard, shards=a.shards, seed=93, dtype='bfloat16',
                  transformers=transformers.__version__, torch=torch.__version__,
                  instrument=dict(item_id=fixed['item_id'], actual_repeat_exact=True, LP_repeat_max_delta=0),
                  forward_modes=dict(FORWARD_DIRECT=dict(max_new_tokens=64, thinking_enabled=False),
                                     FORWARD_COT=dict(max_new_tokens=256, thinking_requested=True)),
                  native_prompt_suffixes={m: prepared[fixed['item_id']]['forward'][m]['prompt'][-120:] for m in ['FORWARD_DIRECT', 'FORWARD_COT']},
                  task_scope='Author human suppression/pragmatic labels, unchanged original question/options/Gold. Prior textual state contains old two premises, not assumed-correct prior inference.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    completed = 0
    with (a.out/'predictions.jsonl').open('w') as stream:
        for r in sorted(rows, key=lambda r: r['item_id']):
            tasks = prepared[r['item_id']]
            for candidate in 'abc':
                ensure_gpu_allowed()
                task = tasks['rec'][candidate]
                values = score(model, task)
                total = sum(values)
                z = dict(item_id=r['item_id'], source_unit=r['source_unit'], operation='RECONSTRUCTION',
                         candidate=candidate, reward_sum=total, reward_mean=total/len(values),
                         token_logprobs=values, observation_tokens=len(values), context_sha256=task['context_sha256'],
                         prompt_sha256=task['prompt_sha256'])
                stream.write(json.dumps(z)+'\n')
            for mode in ['FORWARD_DIRECT', 'FORWARD_COT']:
                ensure_gpu_allowed()
                z = generated(model, tok, tasks['forward'][mode])
                z.update(item_id=r['item_id'], source_unit=r['source_unit'], operation=mode)
                stream.write(json.dumps(z)+'\n')
            completed += 1
            stream.flush()
            if completed % 8 == 0:
                print('E93', a.model.name, a.shard, completed, '/', len(rows), flush=True)
    assert completed == len(rows)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_belief_r_credit.py', 'belief_r_credit.py', 'run_reconstruction_reward.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E93 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
