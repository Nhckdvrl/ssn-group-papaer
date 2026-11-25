"""E135: formation/reading policies on real Measuring Hate Speech annotator pairs with their actual labels.

See experiments/E135-real-annotator-pairs-mechanism.md. Materials from e135_build_pairs.py (model-independent).
usage: e135_real_pairs.py --model M --pairs results/e135/pairs_conf.jsonl --out DIR [--shard i/k]
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

NAMESPACES = {'shared': (['safe', 'toxic'], ['safe', 'toxic']), 'far': (['safe', 'toxic'], ['pass', 'flag'])}
PLAN = [('shared', 'mix', 'normal', ['native', 'gate']), ('shared', 'mix', 'answer_cross_off', ['native', 'gate']),
        ('shared', 'mix', 'all_cross_off', ['native']), ('far', 'mix', 'normal', ['native', 'gate']),
        ('shared', 'grouped', 'normal', ['native', 'gate']), ('shared', 'single', 'normal', ['native'])]


def cond_name(ns, order, policy, scope):
    return f'{ns}_{order}_{policy}_{scope}'


def analyze(dest):
    rows = []
    for path in sorted(dest.glob('behavior*.jsonl')):
        rows += [json.loads(x) for x in path.read_text().splitlines()]
    rows.sort(key=lambda r: r['pair'])
    out = {'n_pairs': len(rows), 'conditions': {}, 'contrasts': {}}
    names = [cond_name(ns, o, p, s) for ns, o, p, ss in PLAN for s in ss]
    per = {}
    for name in names:
        dis_acc, agr_acc, dis_acc_full, sep = [], [], [], []
        for r in rows:
            c = r['conditions'][name]
            ya, yb = np.array(r['gold'][0]), np.array(r['gold'][1])
            za, zb = np.array(c['z'][0]), np.array(c['z'][1])
            ca, cb = np.array(c['argmax_correct'][0]), np.array(c['argmax_correct'][1])
            dis = ya != yb
            if dis.any():
                dis_acc.append(np.mean(np.r_[((za > 0) == ya)[dis], ((zb > 0) == yb)[dis]]))
                dis_acc_full.append(np.mean(np.r_[ca[dis], cb[dis]]))
                sep.append(np.mean((.5 * (za - zb) * np.sign(ya - yb))[dis]))
            else:
                dis_acc.append(np.nan); dis_acc_full.append(np.nan); sep.append(np.nan)
            agr = ~dis
            agr_acc.append(np.mean(np.r_[((za > 0) == ya)[agr], ((zb > 0) == yb)[agr]]) if agr.any() else np.nan)
        per[name] = {k: np.array(v) for k, v in [('disagree_acc', dis_acc), ('disagree_acc_fullvocab', dis_acc_full),
                                                ('separation', sep), ('agree_acc', agr_acc)]}
    ok = ~np.isnan(per[names[0]]['disagree_acc'])
    oka = ~np.isnan(per[names[0]]['agree_acc'])
    for name in names:
        out['conditions'][name] = {k: interval(v[ok if k != 'agree_acc' else oka]) for k, v in per[name].items()}
    single = cond_name('shared', 'single', 'normal', 'native')
    normal = cond_name('shared', 'mix', 'normal', 'native')
    for name in names:
        for k in ['disagree_acc', 'separation', 'agree_acc']:
            m = ok if k != 'agree_acc' else oka
            out['contrasts'][f'{name}_minus_mixed_normal_{k}'] = interval(per[name][k][m] - per[normal][k][m])
            out['contrasts'][f'{name}_minus_single_{k}'] = interval(per[name][k][m] - per[single][k][m])
    gate = cond_name('shared', 'mix', 'normal', 'gate')
    selgate = cond_name('shared', 'mix', 'answer_cross_off', 'gate')
    for k in ['disagree_acc', 'separation']:
        out['contrasts'][f'gate_minus_single_{k}'] = interval(per[gate][k][ok] - per[single][k][ok])
        out['contrasts'][f'gate_minus_selective_gate_{k}'] = interval(per[gate][k][ok] - per[selgate][k][ok])
    out['contrasts']['retention_separation'] = {n: float(np.mean(per[n]['separation'][ok]) / np.mean(per[single]['separation'][ok])) for n in names}
    (dest / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--pairs', required=True)
    ap.add_argument('--out', required=True)
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
    pairs = [json.loads(x) for x in Path(args.pairs).read_text().splitlines()]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    first = {w: enc(' ' + w)[0] for a, b in NAMESPACES.values() for w in a + b}
    assert len(set(first.values())) == len(first), first
    ns_ids = {ns: ([first[w] for w in a], [first[w] for w in b]) for ns, (a, b) in NAMESPACES.items()}

    def prefix(p, ns, order, single=None):
        ids, roles = enc(HEAD), [-1] * len(enc(HEAD))
        labels, answers = [], [[], []]
        demos = list(zip(p['demos'], p['shown']))
        if order == 'grouped':
            f = p['grouped_first']
            demos = [d for d in demos if d[0][1] == f] + [d for d in demos if d[0][1] != f]
        for (comment, role, y), name in demos:
            if single is not None and role != single:
                continue
            block = enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            anchor = len(ids) + len(block)
            answer = enc(' ' + NAMESPACES[ns][role][y]) + enc('\n\n')
            labels.append(anchor)
            answers[role].extend(range(anchor, anchor + len(answer)))
            ids.extend(block + answer)
            roles.extend([role] * (len(block) + len(answer)))
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

    def prefill(data, policy):
        ids, roles, labels, answers = data
        n = len(ids)
        allowed = torch.ones((n, n), dtype=torch.bool, device=dev).tril()
        R = np.array(roles)
        if policy != 'normal':
            for owner in [0, 1]:
                if policy == 'answer_cross_off':
                    rec, snd = [a for a in labels if roles[a] == owner], answers[1 - owner]
                else:
                    rec, snd = np.where(R == owner)[0].tolist(), np.where(R == 1 - owner)[0].tolist()
                rr = torch.tensor(rec, device=dev, dtype=torch.long)
                ss = torch.tensor(snd, device=dev, dtype=torch.long)
                if len(rr) and len(ss):
                    allowed[rr[:, None], ss[None, :]] &= ~(ss[None, :] < rr[:, None])
        mask = torch.zeros((1, 1, n, n), dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        return model(input_ids=torch.tensor([ids], device=dev), attention_mask=mask, use_cache=True,
                     logits_to_keep=1).past_key_values

    def query(cache, roles, queries, owner, gate, ids_out, other_ids):
        plen, n, qlen = len(roles), len(queries), max(map(len, queries))
        ids = torch.zeros((n, qlen), dtype=torch.long, device=dev)
        positions = torch.zeros_like(ids)
        live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i, -len(q):] = torch.tensor(q, device=dev)
            positions[i, -len(q):] = torch.arange(plen, plen + len(q), device=dev)
            live[i, -len(q):] = True
        keep = torch.tensor(roles, device=dev) != 1 - owner if gate else torch.ones(plen, dtype=torch.bool, device=dev)
        allowed = torch.cat([keep[None, None].expand(n, qlen, -1),
            live[:, None].expand(-1, qlen, -1) & torch.ones((qlen, qlen), dtype=torch.bool, device=dev).tril()[None]], -1)
        mask = torch.zeros(allowed.shape, dtype=torch.float32, device=dev).masked_fill_(~allowed, float('-inf'))
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(n)
        logits = model(input_ids=ids, position_ids=positions, attention_mask=mask[:, None], past_key_values=cp,
                       use_cache=True, logits_to_keep=1).logits[:, -1].float()
        top = logits.argmax(-1).cpu().tolist()
        return (logits[:, ids_out[1]] - logits[:, ids_out[0]]).cpu().tolist(), top

    numeric = []
    with torch.inference_mode(), behavior_path.open('w') as stream:
        for pi, p in enumerate(pairs):
            if pi % shards != shard:
                continue
            queries = {o: [enc(f"Comment: {t}\nAnnotator: {p['names'][o]}\nLabel:") for t, _, _ in p['q']] for o in [0, 1]}
            gold = [[int(q[1]) for q in p['q']], [int(q[2]) for q in p['q']]]
            conditions = {}
            for ns, order, policy, scopes in PLAN:
                caches = {}
                if order == 'single':
                    for o in [0, 1]:
                        data = prefix(p, ns, order, single=o)
                        caches[o] = (prefill(data, policy), data)
                else:
                    data = prefix(p, ns, order)
                    c = prefill(data, policy)
                    caches = {0: (c, data), 1: (c, data)}
                for scope in scopes:
                    res = {'z': [None, None], 'argmax_correct': [None, None], 'other_source_word': [None, None]}
                    for o in [0, 1]:
                        cache, data = caches[o]
                        ids_out, other = ns_ids[ns][o], ns_ids[ns][1 - o]
                        z, top = query(cache, data[1], queries[o], o, scope == 'gate', ids_out, other)
                        res['z'][o] = z
                        res['argmax_correct'][o] = [t == ids_out[g] for t, g in zip(top, gold[o])]
                        res['other_source_word'][o] = [t in other and t not in ids_out for t in top]
                    conditions[cond_name(ns, order, policy, scope)] = res
                    if pi < shards and ns == 'shared' and order == 'mix' and policy == 'normal' and scope == 'native':
                        d = caches[0][1]
                        logits = model(input_ids=torch.tensor([d[0] + queries[0][0]], device=dev), use_cache=False,
                                       logits_to_keep=1).logits[0, -1].float()
                        numeric.append(abs(float(logits[ns_ids[ns][0][1]] - logits[ns_ids[ns][0][0]]) - res['z'][0][0]))
                del caches
            assert not numeric or max(numeric) <= 1e-3, numeric
            stream.write(json.dumps({'pair': pi, 'gold': gold, 'conditions': conditions}) + '\n')
            stream.flush()
            if pi % 16 == shard:
                print(pi + 1, '/', len(pairs), 'numeric', max(numeric) if numeric else None, round(time.time() - started), flush=True)
    elapsed = time.time() - started
    (dest / f'run.shard{shard}.json').write_text(json.dumps({'args': vars(args), 'model_type': model.config.model_type,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'pairs_sha256': hashlib.sha256(Path(args.pairs).read_bytes()).hexdigest(),
        'numeric_max_error': max(numeric) if numeric else None, 'dtype': 'float32', 'attention': 'eager',
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__,
        'elapsed_seconds': elapsed, 'gpu_hours': elapsed / 3600}, indent=1) + '\n')
    if shards == 1:
        analyze(dest)


if __name__ == '__main__':
    main()
