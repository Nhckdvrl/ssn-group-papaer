"""E103 fixed same-observation candidate pools; no teacher feedback into generation."""
import argparse
import collections
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
from modern_native_belief_credit import prompt
from reconstruction_reward import prepare, context
from run_reconstruction_reward import score


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def generate(model, tok, text, seed):
    import torch
    torch.manual_seed(seed)
    ids = tok.encode(text, add_special_tokens=False)
    x = torch.tensor([ids], device=model.device)
    with torch.inference_mode():
        y = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=True,
            temperature=.8, top_p=.95, max_new_tokens=96, use_cache=True, pad_token_id=tok.pad_token_id)
    new = y[0, len(ids):].tolist()
    eos = model.generation_config.eos_token_id
    eos = [eos] if isinstance(eos, int) else eos or []
    stopped = bool(new and new[-1] in eos)
    return dict(text=tok.decode(new, skip_special_tokens=True), output_tokens=new,
        stopped=stopped, capped=len(new) >= 96 and not stopped,
        prompt_sha256=digest(text), prompt_tokens=len(ids), seed=seed, cap=96)


def region_scores(source, text, lp, tok, boundary, old=None):
    z = dict(source, interpretation=text.rsplit('</think>', 1)[-1])
    task = prepare(z, tok)
    if old is not None:
        assert task['prompt_sha256'] == old['prompt_sha256']
        assert task['context_sha256'] == old['context_sha256']
    prefix = context(z)
    enc = tok(prefix+source['sentence'], add_special_tokens=False, return_offsets_mapping=True)
    offsets = [(a-len(prefix), b-len(prefix)) for i in task['target_positions']
               for a, b in [enc['offset_mapping'][i]]]
    assert len(lp) == len(offsets)
    word = list(re.finditer(r'\S+', source['sentence']))[boundary]
    before = sum(v for v, (_, b) in zip(lp, offsets) if b <= word.start())
    suffix = sum(v for v, (_, b) in zip(lp, offsets) if b > word.start())
    assert abs(before+suffix-sum(lp)) < 1e-8
    return dict(whole=sum(lp), before=before, suffix=suffix,
        context_sha256=task['context_sha256'], reconstruction_prompt_sha256=task['prompt_sha256'],
        target_ids=[task['ids'][i] for i in task['target_positions']], target_offsets=offsets,
        boundary=boundary, disambiguating_word=word.group())


def run(a):
    ensure_gpu_allowed()
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    ensure_gpu_allowed()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    data = a.root/'data-v1.jsonl'
    assert sha(data) == json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    parent = a.root.parent/'E96'
    assert sha(data) == sha(parent/'data-v1.jsonl')
    rows = [r for r in load(data) if int(digest(r['cluster_id'])[:16], 16) % a.shards == a.shard]
    assert rows
    positions = collections.defaultdict(set)
    for r in load(a.root.parent/'E52/qualified-v3.jsonl'):
        if r.get('step5_position_agreed'):
            positions[r['sentence_sha256']].add(r['step5_annotation']['disamb_word_index'])
    old, provenance = {}, []
    for run in json.loads((parent/'runner-pids-v1.json').read_text()):
        if run['model'] != a.model.name:
            continue
        out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        assert cfg['model_manifest_sha256'] == sha(a.model/'manifest.json')
        provenance.append(dict(config_sha256=sha(out/'config.json'), predictions_sha256=cfg['predictions_sha256']))
        for p in load(out/'predictions.jsonl'):
            if p['operation'] == 'GENERATION' and p['source_condition'] == 'gp':
                old[p['item_id'], 'P'] = p
            elif p['operation'] == 'RECONSTRUCTION' and p['interpretation_condition'] == p['target_condition'] == 'gp':
                old[p['item_id'], 'LP'] = p
    tok = tokenizer(a.model)
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    kwargs = dict(local_files_only=True, dtype=torch.bfloat16, attn_implementation='eager')
    if getattr(cfg, 'quantization_config', None):
        q = dict(cfg.quantization_config); q['dequantize'] = True
        kwargs['quantization_config'] = FineGrainedFP8Config(**q)
    start = time.monotonic()
    model = AutoModelForImageTextToText.from_pretrained(a.model, **kwargs).to('cuda').eval()
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    seed_for = lambda r, j: int(digest(json.dumps([a.model.name, r['item_id'], j]))[:16], 16) % (2**31)
    fixed = min(rows, key=lambda r: r['item_id'])
    first = generate(model, tok, prompt(fixed, 'gp', tok), seed_for(fixed, 1))
    assert generate(model, tok, prompt(fixed, 'gp', tok), seed_for(fixed, 1))['output_tokens'] == first['output_tokens']
    task = prepare(dict(fixed['sources']['gp'], interpretation=first['text'].rsplit('</think>', 1)[-1]), tok)
    assert score(model, task) == score(model, task)
    config = dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'),
        data_sha256=sha(data), code_sha256=sha(Path(__file__)), parent_runs=provenance,
        pairs=len(rows), tasks=len(rows)*8, new_candidates=len(rows)*7,
        gpu=a.gpu, shard=a.shard, shards=a.shards, cap=96, temperature=.8, top_p=.95,
        torch=torch.__version__, transformers=transformers.__version__, dtype='bfloat16',
        instrument=dict(item_id=fixed['item_id'], j=1, actual_repeat_exact=True, LP_repeat_max_delta=0),
        native_builder_sha256=sha(Path(__file__).with_name('modern_native_belief_credit.py')),
        scoring_helper_sha256=sha(Path(__file__).with_name('run_reconstruction_reward.py')),
        context_helper_sha256=sha(Path(__file__).with_name('reconstruction_reward.py')),
        T2_sha256=sha(a.root.parent/'E52/qualified-v3.jsonl'))
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i, r in enumerate(sorted(rows, key=lambda r: r['item_id'])):
            s = r['sources']['gp']; available = positions[s['sentence_sha256']]
            assert len(available) == 1 and None not in available
            boundary = next(iter(available)); targets = []
            for j in range(8):
                ensure_gpu_allowed()
                p = dict(old[r['item_id'], 'P']) if j == 0 else generate(model, tok, prompt(r, 'gp', tok), seed_for(r, j))
                assert p['prompt_sha256'] == digest(prompt(r, 'gp', tok))
                original = old[r['item_id'], 'LP'] if j == 0 else None
                task = prepare(dict(s, interpretation=p['text'].rsplit('</think>', 1)[-1]), tok)
                lp = original['token_logprobs'] if j == 0 else score(model, task)
                regions = region_scores(s, p['text'], lp, tok, boundary, original)
                targets.append((regions['target_ids'], regions['target_offsets']))
                record = dict(p, item_id=r['item_id'], model=a.model.name, candidate=j,
                    seed=None if j == 0 else seed_for(r, j), reused_greedy=j == 0,
                    cluster_id=r['cluster_id'], construction=r['construction'],
                    sentence_sha256=s['sentence_sha256'], text_sha256=digest(p['text']),
                    token_logprobs=lp, scores=regions)
                f.write(json.dumps(record)+'\n'); f.flush()
            assert all(t == targets[0] for t in targets)
            print('E103', a.model.name, a.shard, i+1, '/', len(rows), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    for name in ['run_native_revision_pool.py', 'modern_native_belief_credit.py', 'reconstruction_reward.py', 'run_reconstruction_reward.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E103 DONE', a.model.name, a.shard, config['gpu_hours'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'model', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['gpu', 'shard', 'shards']:
        p.add_argument('--'+name, type=int, required=True)
    run(p.parse_args())
