"""E90 full-scope actual answers after all eight fixed instruments pass."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time
from data import CACHE, sha
from data_v2 import digest
from current_open_baseline import tokenizer
from analyze_actual_answer import semantic_label
from frame_source_bank import prepare, blocks, capture, generate, instrument
from gpu_deadline import ensure_gpu_allowed


def run(a):
    ensure_gpu_allowed()
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    torch.manual_seed(90)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    rows = [r for r in rows if int(r['frame_locator']['GP_source_unit'].split(':')[-1][:16], 16) % a.shards == a.shard]
    tok = tokenizer(a.model)
    tasks = prepare(rows, tok)
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
    layer_path, decoder = blocks(model)
    fixed = min(tasks, key=lambda t: (t['row']['source_unit'], t['row']['item_id'], t['mapping']))
    check = instrument(model, tok, decoder, fixed)
    (a.out/'instrument.json').write_text(json.dumps(check, indent=2)+'\n')
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'),
                  data_sha256=sha(data), code_sha256=sha(Path(__file__)),
                  builder_sha256=sha(Path(__file__).with_name('frame_source_bank.py')),
                  parser_sha256=sha(Path(__file__).with_name('analyze_actual_answer.py')),
                  tasks=len(tasks)*2, QA=len(rows), gpu=a.gpu, shard=a.shard, shards=a.shards,
                  seed=90, max_new_tokens=32, do_sample=False, dtype='bfloat16',
                  thinking_enabled=False, transformers=transformers.__version__, torch=torch.__version__,
                  layer_path=layer_path, instrument=check,
                  source_cache='One identical question-free native/frame prefix per Source; same Source token IDs, all Source block outputs imported; original no-Hint consumer prompt.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    print('E90 instrument passed', a.model.name, a.shard, flush=True)
    while True:
        ensure_gpu_allowed()
        runs = json.loads((a.root/'runner-pids-v1.json').read_text())
        if len(runs) == 8 and all((Path(r['out'])/'instrument.json').exists() for r in runs):
            break
        if time.monotonic()-start > 1800:
            raise RuntimeError('Incomplete instrument barrier; do not read any partial scientific effects.')
        time.sleep(5)
    groups = {}
    for t in tasks:
        groups.setdefault(t['row']['source_unit'], []).append(t)
    completed = 0
    with (a.out/'predictions.jsonl').open('w') as stream:
        for uid, group in sorted(groups.items()):
            ensure_gpu_allowed()
            first = group[0]
            banks = {op: capture(model, decoder, first['prefixes'][op], first['positions'][op])
                     for op in ['NATIVE_BANK', 'FRAME_BANK']}
            for t in group:
                assert t['prefixes'] == first['prefixes']
                assert t['positions'] == first['positions']
                assert t['row']['frame_hint'] not in t['prompt']
                for op in ['NATIVE_BANK', 'FRAME_BANK']:
                    ensure_gpu_allowed()
                    new = generate(model, tok, t['prompt'], decoder, banks[op], t['positions']['NATIVE_BANK'])
                    text = tok.decode(new, skip_special_tokens=True)
                    label, status = semantic_label(text, t['mapping'])
                    eos = model.generation_config.eos_token_id
                    eos = [eos] if isinstance(eos, int) else (eos or [])
                    stopped = bool(new and new[-1] in eos)
                    cap = len(new) >= 32 and not stopped
                    r = t['row']
                    gold = r['grounded_gold']
                    z = dict(item_id=r['item_id'], source_unit=uid, operation=op, mapping=t['mapping'],
                             prompt_sha256=digest(t['prompt']), native_prompt_sha256=digest(t['prompt']),
                             source_prefix_sha256=digest(str(t['prefixes'][op])),
                             source_tokens=len(t['source_tokens']), output_text=text, output_token_ids=new,
                             label=label, semantic_parse_status=status, grounded_gold=gold, stopped=stopped,
                             cap=cap, valid=label is not None,
                             lower_correct=bool(stopped and label == gold),
                             upper_correct=bool(label is None or not stopped or label == gold))
                    stream.write(json.dumps(z)+'\n')
                    completed += 1
            del banks
            stream.flush()
            print('E90 progress', a.model.name, a.shard, completed, '/', len(tasks)*2, flush=True)
    assert completed == len(tasks)*2
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_frame_source_bank.py', 'frame_source_bank.py', 'analyze_actual_answer.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E90 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
