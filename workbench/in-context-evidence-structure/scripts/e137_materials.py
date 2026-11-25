"""E137 materials: two sources with three-class conventions on SST-5 (original labels 0 / 2 / 4).

A gets a random class->word map per prompt; B's map is A's map composed with a cyclic shift (direction random),
so the two disagree on every class. B's demonstrations come in groups that share one token-length signature and
hold one text of each class; the 'cross' world permutes texts within each group so that B's convention equals A's
while B's label words and positions stay fixed. Selection depends only on gold labels and token geometry.
"""
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np

CACHE = Path('/home/xiang/.cache/huggingface/datasets/SetFit___sst5/default/0.0.0/e51bdcd8cd3a30da231967c1a249ba59361279a3')
CLASSES = [0, 2, 4]


def make_contexts_k(tok, n, seed, materials, per_class):
    from datasets import Dataset

    records, hashes = {}, {}
    for split in ['train', 'validation', 'test']:
        path = CACHE / f'sst5-{split}.arrow'
        hashes[split] = hashlib.sha256(path.read_bytes()).hexdigest()
        seen = set()
        records[split] = []
        for row in Dataset.from_file(str(path)):
            text = row['text']
            if row['label'] not in CLASSES or text in seen:
                continue
            seen.add(text)
            records[split].append((text, CLASSES.index(int(row['label']))))
    train_text = {t for t, _ in records['train']}
    validation_text = {t for t, _ in records['validation']}
    bit = 0 if materials == 'discovery' else 1
    pool = [[], [], []]
    for text, c in records['train']:
        if (int(hashlib.sha256(text.encode()).hexdigest()[-1], 16) & 1) != bit:
            continue
        if 5 <= len(tok.encode(text, add_special_tokens=False)) <= 64:
            pool[c].append(text)
    query_split = 'validation' if materials == 'discovery' else 'test'
    query_pool = [[], [], []]
    for text, c in records[query_split]:
        if text in train_text or (materials != 'discovery' and text in validation_text):
            continue
        if 5 <= len(tok.encode(text, add_special_tokens=False)) <= 64:
            query_pool[c].append(text)
    bins = [defaultdict(list) for _ in CLASSES]
    for c, texts in enumerate(pool):
        for text in texts:
            block = f'Comment: {text}\nAnnotator: Alex\nLabel:'
            ann = tok(block, add_special_tokens=False, return_offsets_mapping=True)
            left, right = len('Comment: '), len('Comment: ') + len(text)
            positions = tuple(i for i, (a, b) in enumerate(ann['offset_mapping']) if a < right and b > left)
            outside = tuple((i, t) for i, t in enumerate(ann['input_ids']) if i not in positions)
            bins[c][(len(ann['input_ids']), positions, outside)].append(text)
    valid = sorted(k for k in bins[0] if all(len(bins[c][k]) >= 1 for c in range(3)))
    assert len(valid) >= per_class and min(map(len, query_pool)) >= 4, (len(valid), list(map(len, query_pool)))
    rng = np.random.default_rng(seed)
    cs = []
    for ci in range(n):
        a_map = rng.permutation(3).tolist()          # class -> word index for A
        d = int(rng.choice([1, 2]))
        b_map = [a_map[(c + d) % 3] for c in range(3)]  # B disagrees with A on every class
        used, b, cross = set(), [], {}
        for _ in range(per_class):
            for _try in range(1000):
                sig = valid[int(rng.integers(len(valid)))]
                cand = [[t for t in bins[c][sig] if t not in used] for c in range(3)]
                if all(cand):
                    break
            group = [cand[c][int(rng.integers(len(cand[c])))] for c in range(3)]
            used |= set(group)
            for c in range(3):
                b.append((group[c], 1, c))
                cross[group[c]] = group[(c + d) % 3]
        a, queries = [], []
        for c in range(3):
            texts = rng.choice([t for t in pool[c] if t not in used], per_class, replace=False).tolist()
            a.extend((t, 0, c) for t in texts)
            used |= set(texts)
            texts = rng.choice(query_pool[c], 4, replace=False).tolist()
            queries.extend((t, c) for t in texts)
        demos = [(a + b)[int(i)] for i in rng.permutation(6 * per_class)]
        names = rng.permutation(['Alex', 'Sam']).tolist()
        assert len({t for t, _, _ in demos}) == 6 * per_class
        assert not ({t for t, _ in queries} & {t for t, _, _ in demos})
        cs.append({'demos': demos, 'shown': [names[r] for _, r, _ in demos], 'names': names, 'q': queries,
                   'a_map': a_map, 'b_map': b_map, 'shift': d, 'cross_map': cross})
    return cs, {
        'dataset': 'SetFit/sst5', 'cache_build': CACHE.name, 'arrow_sha256': hashes, 'original_labels': CLASSES,
        'demo_split': 'train', 'demo_hash_parity': bit, 'query_split': query_split, 'comment_token_range': [5, 64],
        'per_class': per_class, 'valid_signature_bins': len(valid), 'demo_pool_sizes': list(map(len, pool)),
        'query_pool_sizes': list(map(len, query_pool)), 'selection_uses_model_outputs': False,
        'scope': 'real SST-5 texts; controlled three-class private conventions, not human annotator rules',
    }
