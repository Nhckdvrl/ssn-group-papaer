"""E137: two sources with three-class conventions (SST-5 0/2/4), same query engine and policies as E136.
See experiments/E137-three-label-rules.md.
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
from e137_materials import make_contexts_k

WORLDS = ['origin', 'cross']
NAMESPACES = {'shared': (['red', 'green', 'blue'], ['red', 'green', 'blue']),
              'far': (['red', 'green', 'blue'], ['one', 'two', 'three'])}
PLAN = {'shared': ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names'], 'far': ['normal', 'answer_cross_off']}
OWNERS = [0, 1]
# 'alt' changes the header and every field name of the prompt format; the comment texts are the same.
TEMPLATES = {'default': (HEAD, 'Comment', 'Annotator', 'Label'),
             'alt': ('Below are movie reviews and the ratings that individual raters gave them.\n\n', 'Review', 'Rater', 'Rating')}


def gold_index(ctx, world, owner):
    m = ctx['a_map'] if (owner == 0 or world == 'cross') else ctx['b_map']
    return [m[c] for _, c in ctx['q']]


def analyze(dest):
    rows = []
    for path in sorted(dest.glob('behavior*.jsonl')):
        rows += [json.loads(x) for x in path.read_text().splitlines()]
    rows.sort(key=lambda r: r['context'])
    out = {'n_contexts': len(rows), 'accuracy': {}, 'delta': {}, 'contrasts': {}}

    def acc(k):
        return np.array([np.mean(r['conditions'][k]['argmax_correct']) for r in rows])

    def lp(k):
        return np.array([np.mean(r['conditions'][k]['lp_gold']) for r in rows])
    summ = {}
    for ns, pols in PLAN.items():
        for p in pols:
            for s in ['native', 'gate']:
                cells = {(w, o): acc(f'{w}_{ns}_{p}_{s}_{o}') for w in WORLDS for o in OWNERS}
                sm = {'all': np.mean(list(cells.values()), 0),
                      'A': (cells['origin', 0] + cells['cross', 0]) / 2,
                      'B': (cells['origin', 1] + cells['cross', 1]) / 2,
                      'AB_conflict': (cells['origin', 0] + cells['origin', 1]) / 2}
                sm['delta'] = .5 * (lp(f'cross_{ns}_{p}_{s}_0') - lp(f'origin_{ns}_{p}_{s}_0'))
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
    ap.add_argument('--per-class', type=int, default=3)
    ap.add_argument('--seed', type=int, default=137101)
    ap.add_argument('--materials', choices=['discovery', 'validation'], default='validation')
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--analyze-only', action='store_true')
    ap.add_argument('--template', choices=list(TEMPLATES), default='default')
    ap.add_argument('--bos', action='store_true', help='prepend BOS (Gemma-2) when not run through run_gemma.py')
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
    cs, meta = make_contexts_k(tok, args.n, args.seed, args.materials, args.per_class)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    words = sorted({w for t in NAMESPACES.values() for ws in t for w in ws})
    assert all(len(enc(' ' + w)) == 1 for w in words), [(w, enc(' ' + w)) for w in words]
    wid = {w: enc(' ' + w)[0] for w in words}
    head, F_C, F_A, F_L = TEMPLATES[args.template]
    blk = lambda c, n: f'{F_C}: {c}\n{F_A}: {n}\n{F_L}:'
    head_ids = ([tok.bos_token_id] if args.bos else []) + enc(head)

    def word(ctx, ns, role, c):
        m = ctx['a_map'] if role == 0 else ctx['b_map']
        return NAMESPACES[ns][role][m[c]]

    def prefix(ctx, world, ns):
        ids, roles = list(head_ids), [-1] * len(head_ids)
        labels, answers, names = [], [[], []], set()
        for (comment, role, c), name in zip(ctx['demos'], ctx['shown']):
            w = word(ctx, ns, role, c)  # label words and positions fixed across worlds
            if role == 1 and world == 'cross':
                comment = ctx['cross_map'][comment]
            text = blk(comment, name)
            ann = tok(text, add_special_tokens=False, return_offsets_mapping=True)
            block = ann['input_ids']
            assert block == enc(text)
            s, e = text.index(f'\n{F_A}:'), text.index(f'\n{F_L}:')
            for i, (a, b) in enumerate(ann['offset_mapping']):
                mid = (a + b) / 2 if b > a else a
                if s <= mid < e:
                    names.add(len(ids) + i)
            anchor = len(ids) + len(block)
            answer = enc(' ' + w) + enc('\n\n')
            labels.append(anchor)
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
        return ids, roles, labels, answers, names

    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    started = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
        device_map='cuda', attn_implementation='eager').eval()
    model.requires_grad_(False)
    dev = model.get_input_embeddings().weight.device

    def prefill(data, policy):
        ids, roles, labels, answers, names = data
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
        lp3 = torch.log_softmax(logits[:, ids_out], -1)
        return lp3.cpu().tolist(), logits.argmax(-1).cpu().tolist(), logits[:, ids_out].cpu().tolist()

    numeric = []
    with torch.inference_mode(), behavior_path.open('w') as stream:
        for ci, ctx in enumerate(cs):
            if ci % shards != shard:
                continue
            queries = {o: [enc(blk(t, ctx['names'][o])) for t, _ in ctx['q']] for o in OWNERS}
            conditions = {}
            for ns, pols in PLAN.items():
                for world in WORLDS:
                    data = prefix(ctx, world, ns)
                    for p in pols:
                        cache = prefill(data, p)
                        for s in ['native', 'gate']:
                            for o in OWNERS:
                                ids_out = [wid[w] for w in NAMESPACES[ns][o]]
                                lp3, top, raw = query(cache, data[1], queries[o], o, s == 'gate', ids_out)
                                gold = gold_index(ctx, world, o)
                                conditions[f'{world}_{ns}_{p}_{s}_{o}'] = {
                                    'gold': gold, 'lp_gold': [v[g] for v, g in zip(lp3, gold)], 'logits3': raw,
                                    'argmax_correct': [t == ids_out[g] for t, g in zip(top, gold)]}
                                if ci < shards and world == 'origin' and p == 'normal' and ns == 'shared' and s == 'native' and o == 0:
                                    full = model(input_ids=torch.tensor([data[0] + queries[0][0]], device=dev), use_cache=False,
                                                 logits_to_keep=1).logits[0, -1].float()
                                    numeric.append(float((full[ids_out].cpu() - torch.tensor(raw[0])).abs().max()))
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
