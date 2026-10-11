"""Source-local permutation completion with globally available answer words.

Two sources lack the same category but have different remaining outputs.
Synchronized swaps preserve global frequencies and invert inferred answers.
"""
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


def make_contexts(stage, n, seed):
    assert n % 18 == 0
    rng = np.random.default_rng(seed)
    designs = [(pair, missing) for pair in itertools.permutations(range(3), 2) for missing in range(3)] * (n // 18)
    rng.shuffle(designs)
    names = ['Alex', 'Sam', 'Chris', 'Dana'] if stage == 'discovery' else ['Alice', 'Bob', 'Casey', 'Eli']
    classes = ['north', 'south', 'east'] if stage == 'discovery' else ['oak', 'elm', 'pine']
    labels = ['Red', 'Blue', 'Green'] if stage == 'discovery' else ['one', 'two', 'three']
    out = []
    for ci, (pair, missing) in enumerate(designs):
        rest = [k for k in range(3) if k != missing]
        common = 3 - sum(pair)
        maps = []
        for source in range(2):
            perm = [None] * 3
            perm[missing] = pair[source]
            values = [pair[1 - source], common]
            rng.shuffle(values)
            for kind, value in zip(rest, values):
                perm[kind] = value
            maps.append(perm)
        maps.extend([rng.permutation(3).tolist(), rng.permutation(3).tolist()])
        demos = []
        for source in range(4):
            for kind in range(3):
                value = maps[source][kind]
                if source < 2:
                    repeats = 2
                else:
                    frequencies = {pair[0]: 4 if source == 2 else 2, pair[1]: 2 if source == 2 else 4, common: 3}
                    repeats = frequencies[value]
                demos.extend({'source': source, 'kind': kind, 'label': value, 'rep': rep} for rep in range(repeats))
        rng.shuffle(demos)
        queries = [{'source': source, 'kind': kind} for source in range(4) for kind in range(3)]
        out.append({'context': ci, 'names': names, 'classes': classes, 'labels': labels,
                    'target_pair': list(pair), 'missing_kind': missing, 'maps': maps, 'demos': demos, 'queries': queries})
    assert all(sum(c['target_pair'] == list(p) and c['missing_kind'] == m for c in out) == n // 18
               for p in itertools.permutations(range(3), 2) for m in range(3))
    return out


def variant(ctx, coverage, change):
    c = copy.deepcopy(ctx)
    pair = c['target_pair']
    exchange = {pair[0]: pair[1], pair[1]: pair[0]}
    if change in ['scope_swap', 'owned_a', 'owned_b', 'foreign_swap', 'comp_a', 'comp_b']:
        edited = {'scope_swap': [0, 1], 'owned_a': [0, 2] if coverage == 'held' else [0, 2, 3],
                  'owned_b': [1, 3] if coverage == 'held' else [1, 2, 3], 'foreign_swap': [2, 3],
                  'comp_a': [2] if coverage == 'held' else [2, 3], 'comp_b': [3] if coverage == 'held' else [2, 3]}[change]
        for source in edited:
            c['maps'][source] = [exchange.get(y, y) for y in c['maps'][source]]
    elif change == 'foreign_cycle':
        for source in [2, 3]:
            c['maps'][source] = [(y + 1) % 3 for y in c['maps'][source]]
    else:
        assert change == 'base'
    for d in c['demos']:
        d['label'] = c['maps'][d['source']][d['kind']]
    if coverage == 'held':
        c['demos'] = [d for d in c['demos'] if d['source'] >= 2 or d['kind'] != c['missing_kind']]
    else:
        assert coverage == 'full'
    assert len(c['demos']) == (26 if coverage == 'held' else 30)
    return c


def oracle(ctx, family):
    possible = list(itertools.permutations(range(3))) if family == 'bijective' else list(itertools.product(range(3), repeat=3))
    result = []
    for q in ctx['queries']:
        ds = [d for d in ctx['demos'] if d['source'] == q['source']]
        valid = [p for p in possible if all(p[d['kind']] == d['label'] for d in ds)]
        assert valid
        probs = [sum(p[q['kind']] == y for p in valid) / len(valid) for y in range(3)]
        gold = int(np.argmax(probs)) if max(probs) == 1 else 3
        result.append({'gold': gold, 'colour_posterior': probs, 'n_functions': len(valid)})
    return result


def encode(tok, ctx, family, instructed):
    classes = ', '.join(ctx['classes'])
    labels = ', '.join(ctx['labels'])
    head = f'The categories are {classes}. The label codes are {labels}. Each named source has its own fixed mapping from categories to label codes.\n'
    if family == 'bijective':
        head += 'For each source the mapping is one-to-one: each label code is used by exactly one category.\n'
    else:
        head += 'For each source the label of each category is chosen independently and uniformly from the three codes; different categories may have the same label code.\n'
    head += 'If a label cannot be determined from the records and the stated rule, answer Unknown.\n'
    if instructed:
        head += 'Use only the records from the requested source and the stated mapping constraint.\n'
    ids = tok.encode(head + '\n', add_special_tokens=False)
    sites = []
    for d in ctx['demos']:
        ids += tok.encode(f'Category: {ctx["classes"][d["kind"]]}\nSource: {ctx["names"][d["source"]]}\nLabel:', add_special_tokens=False)
        sites.append(len(ids))
        ids += tok.encode(' ' + ctx['labels'][d['label']] + '\n\n', add_special_tokens=False)
    return ids, sites


def main():
    ap = argparse.ArgumentParser()
    for x in ['model', 'out', 'stage']:
        ap.add_argument('--' + x, required=True)
    for x in ['n', 'seed']:
        ap.add_argument('--' + x, type=int, required=True)
    a = ap.parse_args()
    assert a.stage in ['discovery', 'confirmation']
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    ctxs = make_contexts(a.stage, a.n, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    labels = ctxs[0]['labels'] + ['Unknown']
    encoded = [tok.encode(' ' + label, add_special_tokens=False) for label in labels]
    assert all(len(t) == 1 for t in encoded), encoded
    label_ids = [t[0] for t in encoded]
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
                                               device_map='cuda', attn_implementation='eager').eval()
    errors, oracle_errors = [], []

    def score(cache, ctx, plen):
        qs = [tok.encode(f'Category: {ctx["classes"][q["kind"]]}\nSource: {ctx["names"][q["source"]]}\nLabel:', add_special_tokens=False) for q in ctx['queries']]
        width = max(map(len, qs))
        ids = torch.zeros((len(qs), width), dtype=torch.long, device='cuda')
        mask = torch.zeros((len(qs), plen + width), dtype=torch.long, device='cuda')
        mask[:, :plen] = 1
        pos = torch.zeros_like(ids)
        for j, q in enumerate(qs):
            ids[j, -len(q):] = torch.tensor(q, device='cuda')
            mask[j, -len(q):] = 1
            pos[j, -len(q):] = torch.arange(plen, plen + len(q), device='cuda')
        c = copy.deepcopy(cache)
        c.batch_repeat_interleave(len(qs))
        v = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=c,
                  use_cache=True, logits_to_keep=1).logits[:, -1].float().log_softmax(-1)
        return v[:, label_ids].cpu().numpy()

    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in ctxs))
    with (dest / 'behavior.jsonl').open('w') as f, torch.inference_mode():
        for ci, ctx in enumerate(ctxs):
            scores, oracles = {}, {}
            for coverage in ['full', 'held']:
                variants = {k: variant(ctx, coverage, k) for k in ['base', 'scope_swap', 'owned_a', 'owned_b', 'foreign_swap', 'foreign_cycle', 'comp_a', 'comp_b']}
                for c in variants.values():
                    if coverage == 'held':
                        for s in (0, 1):
                            target = c['maps'][s][c['missing_kind']]
                            assert all(d['label'] != target for d in c['demos'] if d['source'] == s)
                            assert any(d['label'] == target for d in c['demos'])
                            assert any(d['kind'] == c['missing_kind'] and d['source'] == 2 for d in c['demos'])
                for family in ['bijective', 'independent']:
                    for instructed in [False, True]:
                        sequences = {k: encode(tok, c, family, instructed) for k, c in variants.items()}
                        original_ids, original_sites = sequences['base']
                        for k, (ids, sites) in sequences.items():
                            assert len(ids) == len(original_ids) and sites == original_sites
                            if not k.startswith('comp_'):
                                assert Counter(ids) == Counter(original_ids)
                        computed = {}
                        for change, c in variants.items():
                            ids, _ = sequences[change]
                            key = f'{coverage}.{family}.{int(instructed)}.{change}'
                            signature = tuple(ids)
                            if signature not in computed:
                                cache = model(input_ids=torch.tensor([ids], device='cuda'), use_cache=True, logits_to_keep=1).past_key_values
                                computed[signature] = score(cache, c, len(ids))
                            scores[key] = computed[signature].copy()
                            truth = oracle(c, family)
                            for q, result in zip(c['queries'], truth):
                                missing = coverage == 'held' and q['source'] < 2 and q['kind'] == c['missing_kind']
                                expected = 3 if missing and family == 'independent' else c['maps'][q['source']][q['kind']]
                                oracle_errors.append(result['gold'] != expected)
                            oracles[key] = truth
                            if change == 'base':
                                v = score(cache, c, len(ids))
                                errors.append(float(abs(v - scores[key]).max()))
            assert not any(oracle_errors)
            f.write(json.dumps({'context': ci, 'missing_kind': ctx['missing_kind'], 'target_pair': ctx['target_pair'],
                                'scores': {k: v.tolist() for k, v in scores.items()}, 'oracles': oracles}) + '\n')
            f.flush()
            if ci % 4 == 0:
                print(ci, round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0, 'sanity_max_error': max(errors),
           'oracle_mismatches': sum(oracle_errors), 'torch': torch.__version__, 'transformers': transformers.__version__,
           'host': platform.node(), 'gpu': torch.cuda.get_device_name(),
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (dest / 'control_report.json').write_text(json.dumps(run, indent=2))
    assert max(errors) <= .1
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
