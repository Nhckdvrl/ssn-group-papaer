"""E164 fixed, previously unused MMLU subjects; cached inputs only, no models."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
from transformers import AutoTokenizer

MOE = Path(__file__).resolve().parents[1]
ROOT = MOE / 'results/e164'
RAW = Path.home() / 'mechpop_cache/e164_runtime_routing'
CACHE = Path.home() / '.cache/huggingface/datasets/cais___mmlu'
OLD = ('high_school_biology', 'high_school_mathematics')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'size_bytes': path.stat().st_size}


def question_sha(row):
    return hashlib.sha256(json.dumps({'question': row['question'], 'choices': row['choices']},
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def context(subject, demos, row):
    def query(x):
        return 'Question: '+x['question']+'\nAnswer:'
    header = 'The following are multiple choice questions (with answers) about '+subject.replace('_', ' ')+'.\n\n'
    return header+'\n\n'.join(query(x)+' '+x['choices'][int(x['answer'])] for x in demos)+'\n\n'+query(row)


def arrow(path):
    with pa.memory_map(str(path), 'r') as stream:
        return ipc.open_stream(stream).read_all().to_pylist()


def flatten(sequences):
    lengths = np.array([len(v) for v in sequences], np.int64)
    return np.concatenate(sequences).astype(np.uint32), np.r_[0, lengths.cumsum()]


def prepare():
    if (ROOT/'data_plan.json').exists() or (RAW/'questions.npz').exists():
        raise FileExistsError('Preserve the existing E164 input freeze')
    names = sorted(p.name for p in CACHE.iterdir() if p.is_dir() and p.name != 'all')
    if len(names) != 57 or not set(OLD) <= set(names):
        raise ValueError('Require the complete pinned 57-subject MMLU cache')
    fresh = [name for name in names if name not in OLD]
    rows, files, version = {}, {}, None
    for name in names:
        infos = sorted((CACHE/name).glob('*/*/dataset_info.json'))
        if len(infos) != 1:
            raise ValueError('Require exactly one pinned dataset version per subject')
        root = infos[0].parent
        if version is None:
            version = root.name
        if root.name != version:
            raise ValueError('Mixed dataset cache revisions')
        rows[name] = {}
        for split in ('dev', 'validation', 'test'):
            path = root/('mmlu-'+split+'.arrow')
            files[name+'/'+split] = record(path)
            rows[name][split] = arrow(path)
        if len(rows[name]['dev']) != 5:
            raise ValueError('Five original demonstrations required')
    old_plan_path = MOE/'results/e153/data_plan.json'
    old_plan = json.loads(old_plan_path.read_text())
    old_test = {x['question_sha256'] for x in old_plan['test_questions']}
    forbidden = old_test | {question_sha(x) for name in names for split in ('dev', 'validation')
                            for x in rows[name][split]}
    p_asset_path = MOE/'results/e154/asset_manifest.json'
    asset = json.loads(p_asset_path.read_text())['model']
    tokenizer_root = Path(asset['path'])
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_root, local_files_only=True, trust_remote_code=False)
    if sha(tokenizer_root/'tokenizer.json') != old_plan['tokenizer_sha256']:
        raise ValueError('Legacy tokenizer differs')
    calibration, candidates, cal_meta, test_meta, texts, excluded = [], [], [], [], [], {}
    selected_test_hashes = set()
    for topic, name in enumerate(fresh):
        item = rows[name]
        cal_pool = [i for i, x in enumerate(item['validation']) if question_sha(x) not in old_test]
        test_pool = [i for i, x in enumerate(item['test'])
                     if question_sha(x) not in forbidden | selected_test_hashes]
        if len(cal_pool) < 8 or len(test_pool) < 8:
            raise ValueError('Insufficient disjoint fixed samples: '+name)
        cal_indices = sorted(np.random.default_rng(164101+topic).choice(cal_pool, 8, replace=False).tolist())
        test_order = np.random.default_rng(164001+topic).permutation(test_pool).tolist()
        test_indices = []
        for index in test_order:
            digest = question_sha(item['test'][index])
            if digest in selected_test_hashes:
                continue
            selected_test_hashes.add(digest)
            test_indices.append(index)
            if len(test_indices) == 8:
                break
        if len(test_indices) != 8:
            raise ValueError('Insufficient unique held items: '+name)
        test_indices.sort()
        excluded[name] = {'validation_old_held_duplicates': len(item['validation'])-len(cal_pool),
                          'test_forbidden_or_prior_subject_duplicates': len(item['test'])-len(test_pool)}
        for index in cal_indices:
            row = item['validation'][index]
            text = context(name, item['dev'], row)+' '+row['choices'][int(row['answer'])]
            ids = np.asarray(tokenizer.encode(text, add_special_tokens=False), np.uint32)
            calibration.append(ids)
            cal_meta.append({'subject': topic, 'source_row': index, 'question_sha256': question_sha(row)})
            texts.append(json.dumps({'split': 'cal', 'subject': name, 'source_row': index, 'text': text}, ensure_ascii=False))
        for index in test_indices:
            row = item['test'][index]
            prompt = context(name, item['dev'], row)
            prefix = tokenizer.encode(prompt, add_special_tokens=False)
            lengths, chars = [], []
            for choice in row['choices']:
                continuation = ' '+choice
                ids = tokenizer.encode(prompt+continuation, add_special_tokens=False)
                if ids[:len(prefix)] != prefix or len(ids) <= len(prefix):
                    raise ValueError('Candidate token boundary is not a strict causal prefix')
                candidates.append(np.asarray(ids, np.uint32))
                lengths.append(len(ids)-len(prefix)); chars.append(len(continuation))
            test_meta.append({'subject': topic, 'source_row': index, 'question_sha256': question_sha(row),
                              'gold': int(row['answer']), 'prompt_tokens': len(prefix),
                              'answer_tokens': lengths, 'answer_chars': chars})
            texts.append(json.dumps({'split': 'test', 'subject': name, 'source_row': index,
                                     'prompt': prompt, 'choices': row['choices'], 'gold': int(row['answer'])}, ensure_ascii=False))
    maximum = max(map(len, calibration+candidates))
    if maximum > 4096:
        raise ValueError('Untruncated five-shot input exceeds4096; revise the full input rule before any model readout')
    if any(int(x.max()) >= 100352 for x in calibration+candidates):
        raise ValueError('Token outside the native vocabulary')
    cal_ids, cal_offsets = flatten(calibration)
    test_ids, test_offsets = flatten(candidates)
    values = {'cal_ids': cal_ids, 'cal_offsets': cal_offsets,
              'cal_subject': np.array([x['subject'] for x in cal_meta]),
              'test_ids': test_ids, 'test_offsets': test_offsets,
              **{k: np.array([x[k] for x in test_meta]) for k in ('subject', 'gold', 'prompt_tokens', 'answer_tokens', 'answer_chars')}}
    RAW.mkdir(parents=True, exist_ok=True); ROOT.mkdir(parents=True, exist_ok=True)
    target = RAW/'questions.npz'; np.savez_compressed(target, **values)
    text_path = RAW/'questions.jsonl'; text_path.write_text('\n'.join(texts)+'\n')
    plan = {'experiment': 'E164', 'status': 'data_prepared', 'source_sha256': sha(__file__),
            'subjects': fresh, 'test_questions_each': 8, 'cal_questions_each': 8,
            'test_questions': test_meta, 'cal_questions': cal_meta, 'exclusions': excluded,
            'cached_arrow_files': files, 'cache_revision': version,
            'data': record(target), 'texts': record(text_path), 'legacy_data_plan': record(old_plan_path),
            'P_asset_manifest': record(p_asset_path), 'tokenizer_sha256': sha(tokenizer_root/'tokenizer.json'),
            'pad_token_id': tokenizer.pad_token_id, 'input_max_tokens': maximum,
            'input_mean_candidate_tokens': float(np.mean([len(v) for v in candidates])),
            'test_candidate_tokens': int(sum(map(len, candidates))), 'cal_tokens': int(sum(map(len, calibration))),
            'prompt_rule': 'Original E153 RC text + fixed dev5; no BOS/chat/truncation; fresh55 subjects; no model scores used'}
    (ROOT/'data_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
    return {k: plan[k] for k in ('status', 'input_max_tokens', 'input_mean_candidate_tokens', 'test_candidate_tokens', 'cal_tokens')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare',))
    parser.parse_args()
    print(json.dumps(prepare(), indent=2))
