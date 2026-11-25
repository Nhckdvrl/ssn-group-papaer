"""E136: three sources in one prompt (A, B, C; 8 SST-5 demos each). B's convention varies (origin/cross worlds);
C's convention is fixed per prompt (equal to A's in half the prompts). Same token format and query engine as E123.
See experiments/E136-three-sources.md.
"""
import argparse
import copy
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD
from e118_criterion_code_feature_crossing import interval
from e136_sst_materials3 import make_contexts3

WORLDS = ['origin', 'cross']
NAMESPACES = {'shared': (['no', 'yes'], ['no', 'yes'], ['no', 'yes']), 'far': (['no', 'yes'], ['pass', 'flag'], ['no', 'yes'])}
PLAN = {'shared': ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names'], 'far': ['normal', 'answer_cross_off']}
OWNERS = [0, 1, 2]


def truth(ctx, world, owner):
    g = np.asarray([(-1 if ctx['reverse'] else 1) * (1 if k == 'positive' else -1) for _, k in ctx['q']])
    if owner == 1:
        return (g if world == 'cross' else -g).tolist()
    if owner == 2:
        return (g if ctx['c_same'] else -g).tolist()
    return g.tolist()


def analyze(dest):
    rows = []
    for path in sorted(dest.glob('behavior*.jsonl')):
        rows += [json.loads(x) for x in path.read_text().splitlines()]
    rows.sort(key=lambda r: r['context'])
    out = {'n_contexts': len(rows), 'accuracy': {}, 'delta': {}, 'contrasts': {}}

    def acc(k):
        return np.array([np.mean(r['conditions'][k]['argmax_correct']) for r in rows])

    def z(k):
        return np.array([r['conditions'][k]['z'] for r in rows])
    gA = np.array([r['conditions']['origin_shared_normal_native_0']['gold'] for r in rows])
    summ = {}
    for ns, pols in PLAN.items():
        for p in pols:
            for s in ['native', 'gate']:
                cells = {(w, o): acc(f'{w}_{ns}_{p}_{s}_{o}') for w in WORLDS for o in OWNERS}
                sm = {'all': np.mean(list(cells.values()), 0),
                      'A': (cells['origin', 0] + cells['cross', 0]) / 2, 'B': (cells['origin', 1] + cells['cross', 1]) / 2,
                      'C': (cells['origin', 2] + cells['cross', 2]) / 2,
                      'AB_conflict': (cells['origin', 0] + cells['origin', 1]) / 2}
                sm['delta'] = (.5 * (z(f'cross_{ns}_{p}_{s}_0') - z(f'origin_{ns}_{p}_{s}_0')) * gA).mean(1)
                summ[ns, p, s] = sm
                out['accuracy'][f'{ns}_{p}_{s}'] = {k: interval(v) for k, v in sm.items() if k != 'delta'}
                out['delta'][f'{ns}_{p}_{s}'] = interval(sm['delta'])
    for ns, pols in PLAN.items():
        for p in pols[1:]:
            for s in ['native', 'gate']:
                for part in ['all', 'AB_conflict']:
                    out['contrasts'][f'{ns}_{p}_minus_normal_{s}_{part}'] = interval(summ[ns, p, s][part] - summ[ns, 'normal', s][part])
                out['contrasts'][f'{ns}_{p}_delta_reduction_{s}'] = interval(summ[ns, 'normal', s]['delta'] - summ[ns, p, s]['delta'])
    for part in ['all', 'AB_conflict']:
        out['contrasts'][f'names_gain_native_{part}'] = interval(summ['shared', 'iso_names', 'native'][part] - summ['shared', 'all_cross_off', 'native'][part])
    (dest / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=32)
    ap.add_argument('--seed', type=int, default=136101)
    ap.add_argument('--materials', choices=['discovery', 'validation'], default='validation')
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--analyze-only', action='store_true')
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    shard, shards = map(int, args.shard.split('/'))
    behavior_path = dest / ('behavior.jsonl' if shards == 1 else f'behavior.shard{shard}.jsonl')
    assert not behavior_path.exists()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    cs, meta = make_contexts3(tok, args.n, args.seed, args.materials)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    words = sorted({w for t in NAMESPACES.values() for ws in t for w in ws})
    assert all(len(enc(' ' + w)) == 1 for w in words)
    wid = {w: enc(' ' + w)[0] for w in words}

    def prefix(ctx, world, ns):
        ids, roles = enc(HEAD), [-1] * len(enc(HEAD))
        labels, answers = [], [[], [], []]
        for (comment, role, y), name in zip(ctx['demos'], ctx['shown']):
            if role == 1 and world != 'origin':
                comment = ctx[world + '_map'][comment]
            block = enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            anchor = len(ids) + len(block)
            answer = enc(' ' + NAMESPACES[ns][role][y]) + enc('\n\n')
            labels.append(anchor)
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
        names_tok = []
        return ids, roles, labels, answers

    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    started = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
        device_map='cuda', attn_implementation='eager').eval()
    model.requires_grad_(False)
    dev = model.get_input_embeddings().weight.device

    def name_positions(ctx, data):
        """token indices of 'Annotator: name' spans (offset-based, as in E132)."""
        out = set()
        pos = len(enc(HEAD))
        for (comment, role, y), name in zip(ctx['demos'], ctx['shown']):
            text = f'Comment: {comment}\nAnnotator: {name}\nLabel:'
            ann = tok(text, add_special_tokens=False, return_offsets_mapping=True)
            s, e = text.index('\nAnnotator:'), text.index('\nLabel:')
            for i, (a, b) in enumerate(ann['offset_mapping']):
                mid = (a + b) / 2 if b > a else a
                if s <= mid < e:
                    out.add(pos + i)
            pos += len(ann['input_ids']) + len(enc(' ' + NAMESPACES['shared'][role][y]) + enc('\n\n'))
        return out

    def prefill(data, policy, names):
        ids, roles, labels, answers = data
        n = len(ids)
        allowed = torch.ones((n, n), dtype=torch.bool, device=dev).tril()
        R = np.array(roles)
        if policy != 'normal':
            for o in OWNERS:
                if policy == 'answer_cross_off':
                    rec = [a for a in labels if roles[a] == o]
                    snd = [i for k in OWNERS if k != o for i in answers[k]]
                else:
                    rec = np.where(R == o)[0].tolist()
                    snd = [i for i in np.where((R != o) & (R >= 0))[0].tolist() if not (policy == 'iso_names' and i in names)]
                rr = torch.tensor(rec, device=dev, dtype=torch.long)
                ss = torch.tensor(snd, device=dev, dtype=torch.long)
                if len(rr) and len(ss):
                    allowed[rr[:, None], ss[None, :]] &= ~(ss[None, :] < rr[:, None])
        mask = torch.zeros((1, 1, n, n), dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        return model(input_ids=torch.tensor([ids], device=dev), attention_mask=mask, use_cache=True,
                     logits_to_keep=1).past_key_values

    def query(cache, roles, queries, owner, gate, ids_out):
        plen, n, qlen = len(roles), len(queries), max(map(len, queries))
        ids = torch.zeros((n, qlen), dtype=torch.long, device=dev)
        positions = torch.zeros_like(ids)
        live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i, -len(q):] = torch.tensor(q, device=dev)
            positions[i, -len(q):] = torch.arange(plen, plen + len(q), device=dev)
            live[i, -len(q):] = True
        r = torch.tensor(roles, device=dev)
        keep = ((r == owner) | (r < 0)) if gate else torch.ones(plen, dtype=torch.bool, device=dev)
        allowed = torch.cat([keep[None, None].expand(n, qlen, -1),
            live[:, None].expand(-1, qlen, -1) & torch.ones((qlen, qlen), dtype=torch.bool, device=dev).tril()[None]], -1)
        mask = torch.zeros(allowed.shape, dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(n)
        logits = model(input_ids=ids, position_ids=positions, attention_mask=mask[:, None], past_key_values=cp,
                       use_cache=True, logits_to_keep=1).logits[:, -1].float()
        return (logits[:, ids_out[1]] - logits[:, ids_out[0]]).cpu().tolist(), logits.argmax(-1).cpu().tolist()

    numeric = []
    with torch.inference_mode(), behavior_path.open('w') as stream:
        for ci, ctx in enumerate(cs):
            if ci % shards != shard:
                continue
            queries = {o: [enc(f"Comment: {t}\nAnnotator: {ctx['names'][o]}\nLabel:") for t, _ in ctx['q']] for o in OWNERS}
            names = name_positions(ctx, None)
            conditions = {}
            for ns, pols in PLAN.items():
                for world in WORLDS:
                    data = prefix(ctx, world, ns)
                    for p in pols:
                        cache = prefill(data, p, names)
                        for s in ['native', 'gate']:
                            for o in OWNERS:
                                ids_out = [wid[w] for w in NAMESPACES[ns][o]]
                                z, top = query(cache, data[1], queries[o], o, s == 'gate', ids_out)
                                gold = truth(ctx, world, o)
                                conditions[f'{world}_{ns}_{p}_{s}_{o}'] = {'z': z, 'gold': gold,
                                    'argmax_correct': [t == ids_out[int(g > 0)] for t, g in zip(top, gold)]}
                        if ci < shards and world == 'origin' and p == 'normal' and ns == 'shared':
                            logits = model(input_ids=torch.tensor([data[0] + queries[0][0]], device=dev), use_cache=False,
                                           logits_to_keep=1).logits[0, -1].float()
                            ids_out = [wid[w] for w in NAMESPACES[ns][0]]
                            numeric.append(abs(float(logits[ids_out[1]] - logits[ids_out[0]]) - conditions['origin_shared_normal_native_0']['z'][0]))
                        del cache
            assert not numeric or max(numeric) <= 1e-3, numeric
            stream.write(json.dumps({'context': ci, 'conditions': conditions}) + '\n')
            stream.flush()
            print(ci + 1, '/', args.n, 'numeric', max(numeric) if numeric else None, round(time.time() - started), flush=True)
    elapsed = time.time() - started
    (dest / f'run.shard{shard}.json').write_text(json.dumps({'args': vars(args), 'model_type': model.config.model_type,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'materials': meta,
        'numeric_max_error': max(numeric) if numeric else None, 'dtype': 'float32', 'attention': 'eager',
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600}, indent=1) + '\n')
    if shards == 1:
        analyze(dest)


if __name__ == '__main__':
    main()
