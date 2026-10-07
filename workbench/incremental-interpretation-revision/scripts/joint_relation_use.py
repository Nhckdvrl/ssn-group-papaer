"""E72: original qualified questions, joint versus separate source-grounded use."""
import argparse
import collections
import fcntl
import itertools
import json
import math
import os
from pathlib import Path
import time

from data import CACHE, sha, write_jsonl
from data_v2 import digest

MODELS = ['Qwen3-8B', 'gemma-3-12b-it', 'Meta-Llama-3.1-8B-Instruct']
METRICS = ['joint_correct', 'p_joint_correct', 'initial_correct', 'initial_p_correct', 'final_correct', 'final_p_correct']
SYSTEM = 'Answer Yes only if the source explicitly entails the proposition asked. Answer No if it is contradicted or unasserted. Plausibility alone is insufficient.'


def build(source, out):
    rows = [json.loads(s) for s in source.read_text().splitlines()]
    pairs = collections.defaultdict(list)
    for r in rows:
        assert r['sentence_sha256'] == digest(r['sentence'])
        pairs[r['analysis_pair_id']].append(r)
    result = []
    excluded = []
    for pid, group in sorted(pairs.items()):
        bycond = {c: [r for r in group if r['condition'] == c] for c in ['gp', 'control']}
        if any(len({r['sentence_sha256'] for r in g}) != 1 for g in bycond.values()):
            excluded.append(dict(pair_id=pid, reason='not one source per side')); continue
        questions = []
        for target in ['initial', 'final']:
            shared = set.intersection(*[{r['question'] for r in g if r['analysis_question_target'] == target} for g in bycond.values()])
            if not shared: break
            questions.append(sorted(shared)[0])
        if len(questions) != 2:
            excluded.append(dict(pair_id=pid, reason='missing shared initial/final original questions')); continue
        for condition, g in bycond.items():
            chosen = [sorted([r for r in g if r['question'] == q], key=lambda r: r['item_id'])[0] for q in questions]
            assert len({r['analysis_cluster_id'] for r in chosen}) == 1
            r = chosen[0]
            result.append(dict(item_id=digest(json.dumps([pid, condition, r['sentence_sha256'], questions])),
                sentence=r['sentence'], sentence_sha256=r['sentence_sha256'], source_unit=r['source_unit'],
                construction=r['construction'], condition=condition, cluster_id=r['analysis_cluster_id'], pair_id=pid,
                questions=questions, gold=[x['grounded_gold'] for x in chosen], original_item_ids=[x['item_id'] for x in chosen],
                literal_labels=[x['literal_label'] for x in chosen]))
    assert not out.exists()
    out.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, result)
    m = dict(source_path=str(source), source_sha256=sha(source), data_sha256=sha(out),
        units=len(result), sources=len({r['sentence_sha256'] for r in result}), pairs=len(result)//2,
        clusters=len({r['cluster_id'] for r in result}), excluded=excluded,
        gp_sources_by_construction=dict(collections.Counter(c for c, s in {(r['construction'], r['sentence_sha256']) for r in result if r['condition'] == 'gp'})),
        truth_patterns=dict(collections.Counter('/'.join(r['gold']) for r in result)),
        policy='Original published S/Q and completed G2 gold only. Paired shared questions selected lexically before model outputs. No API or new semantic labels.')
    out.with_suffix('.manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    print(json.dumps(m), flush=True)


def prepare(rows, tok):
    from shared_source_cross_use import render, source_info
    tasks = []
    prefixes = {}
    for r in rows:
        for target in range(2):
            task = SYSTEM+'\nQuestion:\n'+r['questions'][target]+'\nAnswer only Yes or No.'
            tasks.append(dict(row=r, operation='SEPARATE', order=target,
                prompt=render(tok, r['sentence'], task), candidates=['Yes', 'No']))
        for order in range(2):
            inds = [order, 1-order]
            task = SYSTEM+'\nQuestion 1:\n'+r['questions'][inds[0]]+'\nQuestion 2:\n'+r['questions'][inds[1]]
            task += '\nAnswer both questions in their displayed order. Return exactly two Yes/No answers separated by a semicolon followed by a space.'
            tasks.append(dict(row=r, operation='JOINT', order=order, prompt=render(tok, r['sentence'], task),
                candidates=[a+'; '+b for a, b in itertools.product(['Yes', 'No'], repeat=2)]))
    for t in tasks:
        add = not bool(tok.chat_template)
        seq = [tok.encode(t['prompt']+c, add_special_tokens=add) for c in t['candidates']]
        base = tok.encode(t['prompt'], add_special_tokens=add)
        n = 0
        for values in zip(base, *seq):
            if len(set(values)) != 1: break
            n += 1
        assert n and all(len(s) > n for s in seq)
        t['encoded'] = seq, n
        prefix, _ = source_info(tok, t)
        key = t['row']['sentence_sha256']
        if key in prefixes: assert prefixes[key] == prefix
        prefixes[key] = prefix
        assert all(s[:len(prefix)] == prefix for s in seq)
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, Gemma3ForConditionalGeneration
    from reading_map import sequence_scores
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a'); fcntl.flock(lock, fcntl.LOCK_EX)
    torch.manual_seed(72); torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32 = False
    rows = [json.loads(s) for s in a.data.read_text().splitlines()]
    assert json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256'] == sha(a.data)
    rows = [r for r in rows if int(r['sentence_sha256'][:16], 16) % a.shards == a.shard]
    assert rows
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True, padding_side='left')
    if tok.pad_token_id is None: tok.pad_token = tok.eos_token
    tasks = prepare(rows, tok)
    cfg = AutoConfig.from_pretrained(a.model, local_files_only=True)
    klass = Gemma3ForConditionalGeneration if cfg.model_type == 'gemma3' else AutoModelForCausalLM
    start = time.monotonic()
    model = klass.from_pretrained(a.model, local_files_only=True, torch_dtype=torch.float32, attn_implementation='eager').to('cuda').eval()
    a.out.mkdir(parents=True, exist_ok=True)
    assert not (a.out/'predictions.jsonl').exists()
    # One fixed input unit, all operations: batched LP versus individual full sequences.
    uid = sorted(r['item_id'] for r in rows)[0]
    maximum = 0.
    for t in [t for t in tasks if t['row']['item_id'] == uid]:
        seq, n = t['encoded']
        batch = sequence_scores(model, seq, [n]*len(seq), tok.pad_token_id)
        single = [sequence_scores(model, [s], [n], tok.pad_token_id)[0] for s in seq]
        maximum = max(maximum, *[abs(x-y) for x, y in zip(batch, single)])
    assert maximum < .001, maximum
    config = dict(model_path=str(a.model), model_manifest_sha256=sha(a.model/'manifest.json'),
        data_sha256=sha(a.data), code_sha256=sha(Path(__file__)), dtype='float32', attention='eager', seed=72,
        shard=a.shard, shards=a.shards, gpu=a.gpu, units=len(rows), tasks=len(tasks),
        source_prefix_identical=True, fixed_instrument_unit=uid, independent_LP_max_delta=maximum,
        dependencies={n: sha(Path(__file__).with_name(n)) for n in ['reading_map.py','shared_source_cross_use.py']})
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    tasks.sort(key=lambda t: max(map(len, t['encoded'][0])))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0, len(tasks), a.batch_size):
            batch = tasks[begin:begin+a.batch_size]
            seq = [s for t in batch for s in t['encoded'][0]]
            ns = [t['encoded'][1] for t in batch for _ in t['encoded'][0]]
            scores = sequence_scores(model, seq, ns, tok.pad_token_id)
            offset = 0
            for t in batch:
                length = len(t['candidates']); lp = scores[offset:offset+length]; offset += length
                top = max(lp); den = top+math.log(sum(math.exp(x-top) for x in lp))
                record = dict(item_id=t['row']['item_id'], operation=t['operation'], order=t['order'],
                    candidate_logprobs=lp, probabilities=[math.exp(x-den) for x in lp], prompt_sha256=digest(t['prompt']))
                f.write(json.dumps(record)+'\n')
            f.flush()
            if begin % 128 == 0: print('E72', a.model.name, a.shard, begin+len(batch), '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'), gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    (a.out/'joint_relation_use.py').write_bytes(Path(__file__).read_bytes())
    print('E72 shard complete', a.model.name, a.shard, config['gpu_hours'], flush=True)


def main():
    p = argparse.ArgumentParser(); p.add_argument('action', choices=['build','run'])
    p.add_argument('--data', type=Path, required=True); p.add_argument('--source', type=Path)
    p.add_argument('--model', type=Path); p.add_argument('--out', type=Path)
    p.add_argument('--gpu', type=int); p.add_argument('--shard', type=int, default=0); p.add_argument('--shards', type=int, default=1)
    p.add_argument('--batch-size', type=int, default=4); a = p.parse_args()
    if a.action == 'build': build(a.source, a.data)
    else: run(a)


if __name__ == '__main__': main()
