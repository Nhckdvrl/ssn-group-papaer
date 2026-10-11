"""E100 fixed current native P pair, original E95 judge interface, no teacher gate."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time

from data import CACHE, sha, write_jsonl
from data_v2 import digest
from gpu_deadline import ensure_gpu_allowed
from current_open_baseline import tokenizer
from forward_semantic_credit import prompt
from run_belief_r_credit import generated


def ready(path):
    return path.exists() and 'predictions_sha256' in json.loads(path.read_text())


def run(a):
    parent = a.root.parent/'E96'
    runs = [r for r in json.loads((parent/'runner-pids-v1.json').read_text()) if r['model'] == a.model.name]
    while not ready(a.after) or not all(ready(Path(r['out'])/'config.json') for r in runs):
        ensure_gpu_allowed()
        time.sleep(20)
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    os.environ.update(HF_ENDPOINT='https://hf-mirror.com', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    pairs = list(map(json.loads, (parent/'data-v1.jsonl').read_text().splitlines()))
    predictions, provenance = {}, []
    for r in runs:
        out = Path(r['out'])
        cfg = json.loads((out/'config.json').read_text())
        assert cfg['data_sha256'] == sha(parent/'data-v1.jsonl')
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        assert cfg['model_manifest_sha256'] == sha(a.model/'manifest.json')
        provenance.append(dict(config_sha256=sha(out/'config.json'), predictions_sha256=cfg['predictions_sha256']))
        for p in map(json.loads, (out/'predictions.jsonl').read_text().splitlines()):
            if p['operation'] == 'GENERATION':
                key = p['item_id'], p['source_condition']
                assert key not in predictions and p['text_sha256'] == digest(p['text'])
                predictions[key] = p
    assert set(predictions) == {(p['item_id'], s) for p in pairs for s in ['gp', 'control']}
    rows = []
    for pair in pairs:
        if int(digest(pair['cluster_id'])[:16], 16) % a.shards != a.shard:
            continue
        interpretations = {old: predictions[pair['item_id'], side]['text'].rsplit('</think>', 1)[-1]
                           for old, side in [('BASE_BANK', 'gp'), ('TARGET_BANK', 'control')]}
        for side in ['gp', 'control']:
            s = pair['sources'][side]
            rows.append(dict(item_id='E100:'+digest(str([a.model.name, pair['item_id'], side])),
                pair_id=pair['item_id'], source_unit=s['source_unit'], sentence=s['sentence'],
                sentence_sha256=s['sentence_sha256'], cluster_id=s['cluster_id'], construction=s['construction'],
                condition=side, questions=[q['question'] for q in pair['questions']], interpretations=interpretations,
                interpretation_sha256={k:digest(v) for k,v in interpretations.items()}, fidelity_rank=None,
                scope='Gold excluded from experimental model input; joined only by complete semantic analysis.'))
    tok = tokenizer(a.model)
    tasks = []
    for row in sorted(rows, key=lambda r:r['item_id']):
        for mode in ['NATIVE', 'RECOVERY']:
            for order in [0, 1]:
                t = prompt(row, tok, mode, order)
                t.update(mode=mode, order_index=order)
                tasks.append(t)
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    torch.manual_seed(100)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config)
        q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    first = generated(model, tok, tasks[0])
    assert generated(model, tok, tasks[0])['output_tokens'] == first['output_tokens']
    assert first['stopped'] and first['valid'], 'Instrument must give a valid actual comparison.'
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    write_jsonl(a.out/'input-v1.jsonl', rows)
    config = dict(model=a.model.name, data_sha256=sha(parent/'data-v1.jsonl'), input_sha256=sha(a.out/'input-v1.jsonl'),
        model_manifest_sha256=sha(a.model/'manifest.json'), code_sha256=sha(Path(__file__)),
        prompt_helper_sha256=sha(Path(__file__).with_name('forward_semantic_credit.py')),
        generation_helper_sha256=sha(Path(__file__).with_name('run_belief_r_credit.py')),
        E96_runs=provenance, predecessor_config_sha256=sha(a.after), tasks=len(tasks), rows=len(rows),
        gpu=a.gpu, shard=a.shard, shards=a.shards, seed=100, thinking_enabled=False, cap=64,
        dtype='bfloat16', transformers=transformers.__version__, torch=torch.__version__,
        instrument=dict(item_id=tasks[0]['row']['item_id'], repeat_exact=True, stopped_valid=True),
        scope='Matched native writer/grader; all frozen current P, both source references and candidate orders. No new teacher labels.')
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i,t in enumerate(tasks):
            ensure_gpu_allowed()
            z = generated(model, tok, t)
            z.update(item_id=t['row']['item_id'], pair_id=t['row']['pair_id'], source_condition=t['row']['condition'],
                mode=t['mode'], order_index=t['order_index'], candidate_order=t['candidate_order'])
            f.write(json.dumps(z)+'\n')
            f.flush()
            if (i+1) % 32 == 0:
                print('E100', a.model.name, a.shard, i+1, '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_native_meaning_comparison.py', 'forward_semantic_credit.py', 'run_belief_r_credit.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E100 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out', 'after']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
