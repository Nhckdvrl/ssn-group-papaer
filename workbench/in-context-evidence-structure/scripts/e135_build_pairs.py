"""E135 materials: real Measuring Hate Speech annotator pairs with their actual labels (model-independent).

Pairs = annotators who both labelled >= 6 short binary comments, with >= 1 disagreement among them; those shared
comments are the queries (both actual labels known). Demos: 8 other comments per annotator with that annotator's own
label. Selection never looks at model outputs. usage: e135_build_pairs.py OUTDIR
"""
import collections
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

SEED = 135001
# v2 (after the dev batch, 2026-11-25): random pairs failed the manipulation check (single-annotator prompts could not
# separate the two annotators on disagreement items, 50.6%). With --contrast, pairs are ranked by the difference in
# the annotators' strictness (mean of own label minus the other annotators' mean on the same comment, computed on
# comments outside the pair's queries) and the top 320 are used. Selection never looks at model outputs.
N_DEV, N_CONF = 64, 256
MAX_Q = 8


def main():
    from datasets import load_dataset
    out = Path(sys.argv[1])
    contrast = '--contrast' in sys.argv
    out.mkdir(parents=True, exist_ok=True)
    df = load_dataset('ucberkeley-dlab/measuring-hate-speech', split='train').select_columns(
        ['comment_id', 'annotator_id', 'hatespeech', 'text']).to_pandas()
    df = df[df.hatespeech != 1].copy()
    df['y'] = (df.hatespeech == 2).astype(int)
    df = df[df.text.map(lambda t: len(t.split()) <= 60)]
    # one label per (annotator, comment)
    df = df.drop_duplicates(['annotator_id', 'comment_id'])
    text = dict(zip(df.comment_id, df.text))
    lab = {(a, c): y for a, c, y in zip(df.annotator_id, df.comment_id, df.y)}
    by_ann = df.groupby('annotator_id').comment_id.apply(list).to_dict()
    pc = collections.defaultdict(list)
    for c, anns in df.groupby('comment_id').annotator_id.apply(list).items():
        if len(anns) > 20:  # skip the 70 reference comments labelled by everyone
            continue
        for a, b in itertools.combinations(sorted(anns), 2):
            pc[a, b].append(c)
    eligible = []
    for (a, b), shared in pc.items():
        if len(shared) < 6:
            continue
        if not any(lab[a, c] != lab[b, c] for c in shared):
            continue
        if len([c for c in by_ann[a] if c not in shared]) < 8 or len([c for c in by_ann[b] if c not in shared]) < 8:
            continue
        eligible.append((a, b))
    eligible.sort()
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(eligible))
    if contrast:
        cnt = df.groupby('comment_id').y.agg(['sum', 'count'])
        d2 = df.join(cnt, on='comment_id')
        d2 = d2[d2['count'] >= 2]
        resid = {(a, c): y - (s_ - y) / (n - 1) for a, c, y, s_, n in zip(d2.annotator_id, d2.comment_id, d2.y, d2['sum'], d2['count'])}
        def tendency(a, exclude):
            v = [r for (aa, c), r in resid_by[a] if c not in exclude]
            return float(np.mean(v)) if v else 0.0
        resid_by = collections.defaultdict(list)
        for (a, c), r in resid.items():
            resid_by[a].append(((a, c), r))
        gap = []
        for a, b in eligible:
            ex = set(pc[a, b])
            gap.append(abs(tendency(a, ex) - tendency(b, ex)))
        top = np.argsort(-np.asarray(gap), kind='stable')[:N_DEV + N_CONF + 40]
        order = rng.permutation(top)
        gaps = {eligible[i]: gap[i] for i in top}
    pairs = []
    for idx in order:
        if len(pairs) == N_DEV + N_CONF:
            break
        a, b = eligible[idx]
        if rng.random() < .5:
            a, b = b, a
        shared = sorted(pc[min(a, b), max(a, b)])
        q = rng.choice(shared, min(MAX_Q, len(shared)), replace=False).tolist()
        da = rng.choice([c for c in by_ann[a] if c not in shared], 8, replace=False).tolist()
        cand_b = [c for c in by_ann[b] if c not in shared and c not in da]
        if len(cand_b) < 8:
            continue
        db = rng.choice(cand_b, 8, replace=False).tolist()
        assert not (set(da) & set(db))
        demos = [(text[c], 0, lab[a, c]) for c in da] + [(text[c], 1, lab[b, c]) for c in db]
        demos = [demos[i] for i in rng.permutation(16)]
        names = rng.permutation(['Alex', 'Sam']).tolist()
        pairs.append({'annotators': [int(a), int(b)], 'demos': demos, 'names': names,
                      'shown': [names[r] for _, r, _ in demos],
                      'q': [(text[c], lab[a, c], lab[b, c]) for c in q], 'grouped_first': int(rng.integers(2))})
    dev, conf = pairs[:N_DEV], pairs[N_DEV:]
    tag = '_contrast' if contrast else ''
    for name, part in [('dev', dev), ('conf', conf)]:
        (out / f'pairs_{name}{tag}.jsonl').write_text(''.join(json.dumps(p) + '\n' for p in part))
    stats = {'eligible_pairs': len(eligible), 'dev': len(dev), 'conf': len(conf), 'seed': SEED,
             'queries_per_pair': float(np.mean([len(p['q']) for p in conf])),
             'disagreement_share': float(np.mean([np.mean([ya != yb for _, ya, yb in p['q']]) for p in conf])),
             'demo_toxic_rate_A': float(np.mean([np.mean([y for _, r, y in p['demos'] if r == 0]) for p in conf])),
             'demo_toxic_rate_B': float(np.mean([np.mean([y for _, r, y in p['demos'] if r == 1]) for p in conf])),
             'sha256': {n: hashlib.sha256((out / f'pairs_{n}{tag}.jsonl').read_bytes()).hexdigest() for n in ['dev', 'conf']}}
    if contrast:
        g = [gaps[tuple(sorted(p['annotators']))] if tuple(sorted(p['annotators'])) in gaps else gaps[tuple(p['annotators'])] for p in conf]
        stats['strictness_gap_conf'] = {'mean': float(np.mean(g)), 'min': float(np.min(g))}
    (out / f'materials{tag}.json').write_text(json.dumps(stats, indent=1) + '\n')
    print(json.dumps(stats, indent=1))


if __name__ == '__main__':
    main()
