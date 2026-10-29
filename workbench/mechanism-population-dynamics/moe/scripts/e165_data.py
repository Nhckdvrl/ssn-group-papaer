"""Re-encode the complete frozen E164 text panel with the OLMoE tokenizer."""
import hashlib
import json
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

WB = Path(__file__).resolve().parents[2]
ROOT = WB / 'moe/results/e165'
RAW = Path.home() / 'mechpop_cache/e165_mature_olmoe_transport'
TOKENIZER = Path.home() / 'mechpop_cache/hf_olmoe_mature/view_P_b99743a4'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'size_bytes': path.stat().st_size}


def flat(rows):
    return np.concatenate(rows).astype(np.uint32), np.r_[0, np.cumsum([len(x) for x in rows])]


def prepare():
    ROOT.mkdir(exist_ok=True); RAW.mkdir(exist_ok=True)
    if (ROOT / 'data_plan.json').exists():
        raise FileExistsError('Keep the prior frozen input')
    previous = WB / 'moe/results/e164/data_plan.json'
    old = json.loads(previous.read_text())
    source = Path(old['texts']['path'])
    if sha(source) != old['texts']['sha256']:
        raise ValueError('Frozen source text changed')
    names = old['subjects']
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True)
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    calibration, candidates, cal_subject, meta = [], [], [], []
    for row in rows:
        subject = names.index(row['subject'])
        if row['split'] == 'cal':
            calibration.append(np.array(tokenizer.encode(row['text'], add_special_tokens=False)))
            cal_subject.append(subject)
        else:
            prefix = tokenizer.encode(row['prompt'], add_special_tokens=False)
            tokens, chars = [], []
            for choice in row['choices']:
                continuation = ' ' + choice
                ids = tokenizer.encode(row['prompt'] + continuation, add_special_tokens=False)
                if ids[:len(prefix)] != prefix or len(ids) <= len(prefix):
                    raise ValueError('Non-causal candidate token boundary')
                candidates.append(np.asarray(ids)); tokens.append(len(ids)-len(prefix)); chars.append(len(continuation))
            meta.append({'subject': subject, 'gold': row['gold'], 'source_row': row['source_row'],
                         'prompt_tokens': len(prefix), 'answer_tokens': tokens, 'answer_chars': chars})
    if len(calibration) != 440 or len(candidates) != 1760 or len(meta) != 440:
        raise ValueError('The frozen text population changed')
    maximum = max(map(len, calibration + candidates))
    if maximum > 4096:
        raise ValueError('Untruncated input exceeds4096; revise full protocol before scoring')
    if max(int(x.max()) for x in calibration + candidates) >= 50304:
        raise ValueError('Tokens outside native vocabulary')
    if not np.all(np.bincount(cal_subject, minlength=55) == 8):
        raise ValueError('Calibration population changed')
    ids, offsets = flat(calibration); test, toff = flat(candidates)
    output = RAW / 'questions.npz'
    np.savez_compressed(output, cal_ids=ids, cal_offsets=offsets, cal_subject=np.array(cal_subject),
                        test_ids=test, test_offsets=toff,
                        **{key: np.array([x[key] for x in meta]) for key in
                           ('subject', 'gold', 'prompt_tokens', 'answer_tokens', 'answer_chars')})
    plan = {'experiment': 'E165', 'status': 'data_prepared', 'subjects': names, 'questions': 440,
            'calibration_questions': 440, 'source_text': record(source), 'E164_data_plan': record(previous),
            'tokenizer': {file: record(TOKENIZER / file) for file in
                          ('tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json')},
            'pad_token_id': tokenizer.pad_token_id, 'input_max_tokens': maximum,
            'mean_candidate_tokens': float(np.mean([len(x) for x in candidates])),
            'test_candidate_tokens': int(len(test)), 'cal_tokens': int(len(ids)),
            'data': record(output), 'source_sha256': sha(__file__),
            'text_protocol': 'Exact prior55 subjects/dev5/cal/test texts; OLMoE tokens; no truncation, BOS or chat',
            'not_new_independent_inputs_or_training_seeds': True}
    (ROOT / 'data_plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps({k: plan[k] for k in ('status', 'input_max_tokens', 'mean_candidate_tokens', 'test_candidate_tokens')}))


if __name__ == '__main__':
    prepare()
