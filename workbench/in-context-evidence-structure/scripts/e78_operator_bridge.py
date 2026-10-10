"""Preregistered source-function identification, code handoff and numeric use."""
import argparse
import copy
from collections import Counter
import hashlib
import itertools
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


SCOPES = ['mixed', 'single', 'mixed_scope']
METHODS = ['input_first', 'source_first', 'empty_rule', 'auto_code', 'gold_code', 'opposite_code']
WORDS = ['copy', 'subtract']


def contexts(n, seed):
    assert n % 16 == 0
    rng = np.random.default_rng(seed)
    designs = list(itertools.product([1, -1], repeat=4)) * (n // 16)
    rng.shuffle(designs)
    out = []
    for i, ts in enumerate(designs):
        records = [{'source': s, 'input': x, 'rep': r}
                   for s in range(4) for x in [2, 7] for r in range(2)]
        rng.shuffle(records)
        out.append({'context': i, 'theta': list(ts), 'records': records,
                    'names': ['Alex', 'Sam', 'Chris', 'Dana']})
    assert Counter(tuple(c['theta']) for c in out) == Counter({p: n // 16 for p in itertools.product([1, -1], repeat=4)})
    return out


def function(x, theta):
    return x if theta == 1 else 9 - x


def prefix_text(c, scope, order, single_source=None):
    blocks = ['copy: output the input number.\n', 'subtract: output 9 minus the input number.\n']
    if order == 'subtract_first':
        blocks.reverse()
    text = 'Each named source follows one fixed rule. The two rules are:\n' + ''.join(blocks)
    text += ('Infer the requested source\'s rule from its records. When asked for Rule, answer with its name. '
             'When asked for Label, answer a number from 0 through 9. A supplied Rule field states the rule to apply; '
             'if it is empty, infer the rule from the source\'s records.\n')
    if scope == 'mixed_scope':
        text += 'Use only the records from the requested source and the stated mapping constraint.\n'
    text += '\n'
    for r in c['records']:
        s = r['source']
        if single_source is not None and s != single_source:
            continue
        text += f'Input: {r["input"]}\nSource: {c["names"][s]}\nLabel: {function(r["input"], c["theta"][s])}\n\n'
    return text


def numeric_query(c, s, x, method, chosen):
    source = f'Source: {c["names"][s]}\n'
    if method == 'input_first':
        return f'Input: {x}\n' + source + 'Label:'
    if method == 'source_first':
        return source + f'Input: {x}\nLabel:'
    if method == 'empty_rule':
        rule = ''
    elif method == 'auto_code':
        rule = ' ' + WORDS[chosen[s]]
    elif method == 'gold_code':
        rule = ' ' + WORDS[0 if c['theta'][s] == 1 else 1]
    elif method == 'opposite_code':
        rule = ' ' + WORDS[1 if c['theta'][s] == 1 else 0]
    else:
        raise ValueError(method)
    return source + f'Rule:{rule}\nInput: {x}\nLabel:'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=32)
    ap.add_argument('--seed', type=int, default=78001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    cs = contexts(a.n, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    enc = [tok.encode(' ' + str(y), add_special_tokens=False) for y in range(10)]
    space = tok.encode(' ', add_special_tokens=False)
    word_ids = [tok.encode(' ' + word, add_special_tokens=False) for word in WORDS]
    assert len(space) == 1 and all(len(e) == 2 and e[0] == space[0] for e in enc)
    assert all(len(e) == 1 for e in word_ids)
    digit_ids = [e[-1] for e in enc]
    word_ids = [e[0] for e in word_ids]
    preflight_checks = 0
    for c in cs:
        for scope in SCOPES:
            for ss in [0, 1] if scope == 'single' else [None]:
                texts = [prefix_text(c, scope, order, ss) for order in ['copy_first', 'subtract_first']]
                encoded = [tok.encode(t, add_special_tokens=False) for t in texts]
                assert len(encoded[0]) == len(encoded[1]) and Counter(encoded[0]) == Counter(encoded[1])
                sources = [ss] if ss is not None else [0, 1]
                for text, ids in zip(texts, encoded):
                    for s in sources:
                        rq = f'Source: {c["names"][s]}\nRule:'
                        for wi, word in enumerate(WORDS):
                            assert tok.encode(text + rq + ' ' + word, add_special_tokens=False) == ids + tok.encode(rq, add_special_tokens=False) + [word_ids[wi]]
                        for x in range(10):
                            for method in METHODS:
                                for chosen in [[0, 0], [1, 1]] if method == 'auto_code' else [[0, 0]]:
                                    q = numeric_query(c, s, x, method, chosen)
                                    qids = tok.encode(q, add_special_tokens=False)
                                    for y in [0, 9]:
                                        assert tok.encode(text + q + ' ' + str(y), add_special_tokens=False) == ids + qids + enc[y]
                                    preflight_checks += 1
    (d / 'preflight.json').write_text(json.dumps({'n': a.n, 'seed': a.seed, 'token_boundary_checks': preflight_checks,
                                                'digit_ids': digit_ids, 'word_ids': word_ids, 'space_id': space[0]}, indent=2))
    (d / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    if a.preflight_only:
        print('preflight passed', preflight_checks, flush=True)
        return
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
        device_map='cuda', attn_implementation='eager', output_loading_info=True)
    assert not loading.get('missing_keys') and not loading.get('unexpected_keys') and not loading.get('mismatched_keys'), loading
    model.eval()
    noops, audits = [], []

    def logits(cache, plen, qs, keep=1):
        pieces = []
        for start in range(0, len(qs), 40):
            batch = qs[start:start + 40]
            nb, w = len(batch), max(map(len, batch))
            ids = torch.zeros((nb, w), dtype=torch.long, device='cuda')
            mask = torch.zeros((nb, plen + w), dtype=torch.long, device='cuda')
            mask[:, :plen] = 1
            pos = torch.zeros_like(ids)
            for j, q in enumerate(batch):
                ids[j, -len(q):] = torch.tensor(q, device='cuda')
                mask[j, -len(q):] = 1
                pos[j, -len(q):] = torch.arange(plen, plen + len(q), device='cuda')
            cc = copy.deepcopy(cache)
            cc.batch_repeat_interleave(nb)
            pieces.append(model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cc,
                                use_cache=True, logits_to_keep=keep).logits.float().log_softmax(-1).cpu())
        return torch.cat(pieces)

    def numeric(cache, plen, qs):
        v = logits(cache, plen, [tok.encode(q, add_special_tokens=False) + space for q in qs], 2)
        return (v[:, -1, digit_ids] + v[:, -2, space[0], None]).numpy()

    def full_audit(ids, query, cached, numeric_answer):
        qids = tok.encode(query, add_special_tokens=False)
        if numeric_answer:
            inp = ids + qids + space
            v = model(input_ids=torch.tensor([inp], device='cuda'), use_cache=False, logits_to_keep=2).logits.float().log_softmax(-1)
            full = (v[0, -1, digit_ids] + v[0, -2, space[0]]).cpu().numpy()
        else:
            v = model(input_ids=torch.tensor([ids + qids], device='cuda'), use_cache=False, logits_to_keep=1).logits.float().log_softmax(-1)
            full = v[0, -1, word_ids].cpu().numpy()
        e = float(np.max(np.abs(full - cached)))
        audits.append(e)
        assert e <= .1, e

    with torch.inference_mode(), (d / 'behavior.jsonl').open('w') as f:
        for c in cs:
            results = {}
            for scope in SCOPES:
                for order in ['copy_first', 'subtract_first']:
                    r = {'rule_logp': [], 'chosen': [], 'rule_vocab_top1': [], 'numeric': {m: [] for m in METHODS}}
                    for sources in [[0], [1]] if scope == 'single' else [[0, 1]]:
                        text = prefix_text(c, scope, order, sources[0] if scope == 'single' else None)
                        ids = tok.encode(text, add_special_tokens=False)
                        cache = model(input_ids=torch.tensor([ids], device='cuda'), use_cache=True).past_key_values
                        rule_queries = [f'Source: {c["names"][s]}\nRule:' for s in sources]
                        all_rule_logits = logits(cache, len(ids), [tok.encode(q, add_special_tokens=False) for q in rule_queries])[:, -1]
                        rv = all_rule_logits[:, word_ids].numpy()
                        chosen = rv.argmax(-1).tolist()
                        choice_by_source = [0, 0]
                        for s, choice in zip(sources, chosen):
                            choice_by_source[s] = choice
                        qs = [numeric_query(c, s, x, method, choice_by_source) for method in METHODS for s in sources for x in range(10)]
                        nv = numeric(cache, len(ids), qs)
                        if c['context'] == 0:
                            repeated = numeric(cache, len(ids), qs)
                            e = float(np.max(np.abs(repeated - nv)))
                            noops.append(e)
                            assert e <= .1, e
                            for j, q in enumerate(rule_queries):
                                full_audit(ids, q, rv[j], False)
                            for mi in range(len(METHODS)):
                                j = mi * len(sources) * 10 + 3
                                full_audit(ids, qs[j], nv[j], True)
                        r['rule_logp'].extend(rv.tolist())
                        r['chosen'].extend(chosen)
                        r['rule_vocab_top1'].extend(all_rule_logits.argmax(-1).tolist())
                        nv = nv.reshape(len(METHODS), len(sources) * 10, 10)
                        for mi, method in enumerate(METHODS):
                            r['numeric'][method].extend(nv[mi].tolist())
                        del cache
                    results[scope + '.' + order] = r
            f.write(json.dumps({'context': c['context'], 'theta': c['theta'], 'results': results}) + '\n')
            f.flush()
            if c['context'] % 4 == 0:
                print(c['context'], round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0, 'no_op_max_error': max(noops),
           'full_forward_max_error': max(audits), 'audit_count': len(audits), 'torch': torch.__version__,
           'transformers': transformers.__version__, 'host': platform.node(), 'gpu': torch.cuda.get_device_name(),
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (d / 'run.json').write_text(json.dumps(run, indent=2))


if __name__ == '__main__':
    main()
