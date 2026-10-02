"""Frozen original 2011 IQAP development material and human response categories."""
import csv
import hashlib
import json

CATEGORIES = ['definite-yes', 'probable-yes', 'definite-no', 'probable-no']
TARGETS = ['B definitely meant to convey "Yes".', 'B probably meant to convey "Yes".',
           'B definitely meant to convey "No".', 'B probably meant to convey "No".']

def prepare(root):
    path = root/'data/iqap-data.csv'
    all_rows = list(csv.DictReader(path.open()))
    assert len(all_rows) == 215 and len({r['Item'] for r in all_rows}) == 215
    assert all(sum(int(r[k]) for k in CATEGORIES) == 30 for r in all_rows)
    rows = [r for r in all_rows if r['DevEval'] == 'DEVELOPMENT']
    assert len(rows) == 150
    # Preserve source order/text. The 65 evaluation responses are not sent to a model.
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()

def prompt(row):
    return ('Indirect Answers to Yes/No Questions\n\n'
            'In the following dialogue, speaker A asks a simple Yes/No question, '
            'but speaker B answers with something more indirect and complicated:\n\n'
            + row['Question'] + '\n' + row['Answer'] + '\n\n'
            'Which of the following best captures what speaker B meant here?\n'
            + '\n'.join(TARGETS) + '\n\n'
            'Cautionary note: in general, there is no unique right answer.\n'
            'Reply with only the selected interpretation sentence.\n')

def sequences(tok, text, interface):
    if interface == 'bare':
        original = text
        full = [text+t+tok.eos_token for t in TARGETS]
        content = [text+t for t in TARGETS]
    else:
        original = tok.apply_chat_template([{'role':'user','content':text}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        full = [tok.apply_chat_template([{'role':'user','content':text},
            {'role':'assistant','content':t}], tokenize=False,
            add_generation_prompt=False, enable_thinking=False) for t in TARGETS]
        content = [original+t for t in TARGETS]
    prefix = tok.encode(original, add_special_tokens=False)
    ids = [tok.encode(x, add_special_tokens=False) for x in full]
    content_ids = [tok.encode(x, add_special_tokens=False) for x in content]
    for x, y in zip(ids, content_ids):
        assert x[:len(prefix)] == prefix and x[:len(y)] == y
        assert len(x) > len(y) > len(prefix)
    return {'ids':ids, 'first':len(prefix), 'content_ends':[len(x) for x in content_ids],
            'prompt_sha256':hashlib.sha256(original.encode()).hexdigest()}

def common_model(root, model):
    if model.startswith('OLMoE'):return root/'models/OLMoE-1B-7B-0125-SFT'
    if model.startswith('Qwen2.5'):return root/'models/Qwen2.5-3B-Instruct'
    return root/'models'/model

def fingerprint(plans):
    return hashlib.sha256(json.dumps([p['ids'] for p in plans]).encode()).hexdigest()
