#!/usr/bin/env python3
"""Freeze tokenized native update/motivation/interaction training; no inference."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from experience_store import ExperienceStore, file_sha
from training_targets import assistant_token_spans


def rank(value):
    return hashlib.sha256(('D-E10-training-v1|' + value).encode()).hexdigest()


def worker_init(index, tokenizer, all_turns=False):
    global worker_store, worker_tokenizer, worker_all_turns
    import os
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    from transformers import AutoTokenizer
    worker_store = ExperienceStore(index)
    worker_tokenizer = AutoTokenizer.from_pretrained(tokenizer, local_files_only=True)
    worker_all_turns=all_turns


def encode_record(m):
    c = worker_store.get(m['row_id'])['conversations']
    if [v['from'] for v in c[:3]] != ['system', 'human', 'assistant']:
        raise ValueError(('Unexpected native turns', m['row_id']))
    if m['task'] != 'interaction_generation' and len(c) != 3:
        raise ValueError(('Unexpected native single-task layout', m['row_id']))
    if worker_all_turns and m['task']=='interaction_generation':
        roles={'human':'user','system':'system','assistant':'assistant'}
        messages=[dict(role=roles[x['from']],content=x['value']) for x in c]
        rendered=worker_tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=False,enable_thinking=False)
        encoded=worker_tokenizer(rendered,add_special_tokens=False,return_offsets_mapping=True,return_attention_mask=False)
        spans=assistant_token_spans(rendered,[x['role'] for x in messages],encoded['offset_mapping'])
        if any(encoded['input_ids'][end-1]!=worker_tokenizer.eos_token_id for _,end in spans):
            raise ValueError(('Assistant span must include exact end token',m['row_id']))
        return m,spans[0][0],sum(end-begin for begin,end in spans),np.array(encoded['input_ids'],dtype='<i4'),spans
    messages = [{'role': role, 'content': value['value']}
                for role, value in zip(['system', 'user'], c[:2])]
    prefix = worker_tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
                                                  add_generation_prompt=True, enable_thinking=False)
    target = worker_tokenizer.encode(c[2]['value'] + worker_tokenizer.eos_token, add_special_tokens=False)
    return m, len(prefix), len(target), np.array(prefix + target, dtype='<i4'),None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--index', required=True)
    p.add_argument('--view-inventory', required=True)
    p.add_argument('--tokenizer', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--all-assistant-turns', action='store_true')
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    inv = json.loads(Path(a.view_inventory).read_text())
    split = {b: v['partition'] for b, v in inv['books'].items()}
    store = ExperienceStore(a.index)
    if store.metadata['source_sha256'] != inv['source_sha256']:
        raise ValueError('Different release')
    types = ['character_state_update', 'character_motivation_update', 'interaction_generation']
    metas = [dict(r) for r in store.db.execute('SELECT * FROM records ORDER BY row_id')
             if r['task'] in types and split[r['book']] in ['train', 'validation']]
    validation = defaultdict(list)
    for m in metas:
        if split[m['book']] == 'validation' and (a.all_assistant_turns or m['task'] == types[0]):
            validation[m['book'],m['task']].append(m['row_id'])
    val_ids = {uid for (book,task), ids in validation.items()
               for uid in sorted(ids, key=lambda i: rank(book + '|' + str(i)))[:32]}
    metas = [m for m in metas if split[m['book']] == 'train' or m['row_id'] in val_ids]
    counts, tokens, exclusions = Counter(), Counter(), Counter()
    offset = 0
    with ProcessPoolExecutor(max_workers=a.workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=worker_init, initargs=(a.index, a.tokenizer,a.all_assistant_turns)) as pool, \
            (out / 'tokens.bin').open('xb') as binary, (out / 'entries.jsonl').open('x') as entries, (out / 'exclusions.jsonl').open('x') as rejected:
        for m, prompt_length, target_length, ids,spans in pool.map(encode_record, metas, chunksize=16):
            part = split[m['book']]
            key = part + '/' + m['task']
            if len(ids) > 32768:
                rejected.write(json.dumps(dict(row_id=m['row_id'], book=m['book'], task=m['task'],
                    partition=part, prompt_tokens=prompt_length, target_tokens=target_length,
                    reason='complete_sequence_over_32768')) + '\n')
                exclusions[key] += 1
                continue
            binary.write(ids.tobytes())
            item = dict(row_id=m['row_id'], book=m['book'], role=m['role'], task=m['task'],
                partition=part, offset=offset, length=len(ids), prompt_length=prompt_length,
                target_length=target_length, source_record_sha256=m['sha256'])
            if spans is not None:item.update(target_spans=spans,assistant_turns=len(spans))
            entries.write(json.dumps(item, ensure_ascii=False) + '\n')
            offset += len(ids)
            counts[key] += 1
            tokens[key] += len(ids)
            if sum(counts.values()) % 2000 == 0:
                print('Tokenized', sum(counts.values()), dict(counts), flush=True)
    store.close()
    if counts['train/character_state_update'] != inv['by_partition']['train']['n_updates']:
        raise ValueError('Native update coverage changed')
    result = dict(experiment='D-E12' if a.all_assistant_turns else 'D-E10', source_revision=inv['source_revision'], source_sha256=inv['source_sha256'],
        partition_inventory_sha256=file_sha(a.view_inventory), tokenizer=a.tokenizer,
        script_sha256=file_sha(__file__), dtype='little-endian int32', n_tokens=offset,
        counts=dict(counts), total_tokens=dict(tokens), exclusions=dict(exclusions),
        native_update_two_epoch_tokens=2*tokens['train/character_state_update'],
        files={f.name: dict(sha256=file_sha(f), bytes=f.stat().st_size) for f in out.iterdir()},
        max_sequence=32768, no_truncation=True, actor_target='All assistant turns in each full native conversation' if a.all_assistant_turns else 'First assistant turn of each native segment',
        target_helper_sha256=file_sha(Path(__file__).with_name('training_targets.py')),
        model_calls=0)
    (out / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
