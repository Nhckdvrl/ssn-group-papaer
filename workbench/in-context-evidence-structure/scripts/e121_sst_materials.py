"""Prospective E121 material builder; selection depends only on gold and geometry."""
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np

CACHE = Path('/home/xiang/.cache/huggingface/datasets/SetFit___sst5/default/0.0.0/e51bdcd8cd3a30da231967c1a249ba59361279a3')


def make_contexts(tok, n, seed, materials):
    from datasets import Dataset

    records = {}
    hashes = {}
    for split in ['train', 'validation', 'test']:
        path = CACHE / f'sst5-{split}.arrow'
        hashes[split] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Deduplicate by original text; do not rewrite natural-language content.
        seen = set()
        records[split] = []
        for row in Dataset.from_file(str(path)):
            text = row['text']
            if row['label'] not in [0, 4] or text in seen:
                continue
            seen.add(text)
            records[split].append((text, int(row['label'] == 4)))
    train_text = {t for t, _ in records['train']}
    validation_text = {t for t, _ in records['validation']}
    bit = 0 if materials == 'discovery' else 1
    pool = [[], []]  # Positive first, consistent with the frozen native engine.
    for text, positive in records['train']:
        if (int(hashlib.sha256(text.encode()).hexdigest()[-1], 16) & 1) != bit:
            continue
        if 5 <= len(tok.encode(text, add_special_tokens=False)) <= 64:
            pool[0 if positive else 1].append(text)
    query_split = 'validation' if materials == 'discovery' else 'test'
    query_pool = [[], []]
    for text, positive in records[query_split]:
        if text in train_text or (materials != 'discovery' and text in validation_text):
            continue
        if 5 <= len(tok.encode(text, add_special_tokens=False)) <= 64:
            query_pool[0 if positive else 1].append(text)
    bins = [defaultdict(list), defaultdict(list)]
    for kind, texts in enumerate(pool):
        for text in texts:
            block = f'Comment: {text}\nAnnotator: Alex\nLabel:'
            annotation = tok(block, add_special_tokens=False, return_offsets_mapping=True)
            left, right = len('Comment: '), len('Comment: ') + len(text)
            positions = tuple(i for i, (a, b) in enumerate(annotation['offset_mapping']) if a < right and b > left)
            outside = tuple((i, t) for i, t in enumerate(annotation['input_ids']) if i not in positions)
            bins[kind][(len(annotation['input_ids']), positions, outside)].append(text)
    valid = sorted(k for k in bins[0] if min(len(bins[0][k]), len(bins[1][k])) >= 2)
    assert len(valid) >= 2 and min(map(len, pool)) >= 12 and min(map(len, query_pool)) >= 4, {
        'valid_bins': len(valid), 'demo_pool': list(map(len, pool)), 'query_pool': list(map(len, query_pool))}
    rng = np.random.default_rng(seed)
    cs = []
    for ci in range(n):
        b, cross, within = [], {}, {}
        signatures = [valid[int(i)] for i in rng.choice(len(valid), 2, replace=False)]
        for signature in signatures:
            pos = rng.choice(bins[0][signature], 2, replace=False).tolist()
            neg = rng.choice(bins[1][signature], 2, replace=False).tolist()
            original, changed = pos + neg, neg + pos
            control = [pos[1], pos[0], neg[1], neg[0]]
            for i, text in enumerate(original):
                b.append((text, 1, int(i >= 2)))
                cross[text], within[text] = changed[i], control[i]
        used = {t for t, _, _ in b}
        a, queries = [], []
        for kind in [0, 1]:
            texts = rng.choice([t for t in pool[kind] if t not in used], 4, replace=False).tolist()
            a.extend((t, 0, int(kind == 0)) for t in texts)
            texts = rng.choice(query_pool[kind], 4, replace=False).tolist()
            queries.extend((t, 'positive' if kind == 0 else 'negative') for t in texts)
        reverse = bool(ci % 2)
        demos = [(a + b)[int(i)] for i in rng.permutation(16)]
        if reverse:
            demos = [(t, r, 1 - y) for t, r, y in demos]
        names = rng.permutation(['Alex', 'Sam']).tolist()
        assert len({t for t, _, _ in demos}) == 16
        assert not ({t for t, _ in queries} & {t for t, _, _ in demos})
        cs.append({'demos': demos, 'shown': [names[r] for _, r, _ in demos], 'names': names,
                   'q': queries, 'reverse': reverse, 'cross_map': cross, 'within_map': within,
                   'quartet_lengths': [k[0] for k in signatures]})
    return cs, {
        'dataset': 'SetFit/sst5', 'cache_build': CACHE.name, 'arrow_sha256': hashes,
        'original_labels': [0, 4], 'demo_split': 'train', 'demo_hash_parity': bit,
        'query_split': query_split, 'comment_token_range': [5, 64], 'valid_quartet_length_bins': len(valid),
        'demo_pool_sizes': list(map(len, pool)), 'query_pool_sizes': list(map(len, query_pool)),
        'selection_uses_model_outputs': False, 'original_text_retained': True,
        'scope': 'real extreme-sentiment texts; controlled private conventions, not human annotator rules',
    }
