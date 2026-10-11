"""Disentangle private source operation and a shared, context-learned codebook."""
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


WORDS = ['red', 'blue', 'green', 'yellow', 'white', 'black', 'orange', 'purple', 'pink', 'brown']
MODES = ['mixed', 'mixed_scope', 'own_dictionary', 'direct']
ORDERS = ['copy_first', 'subtract_first']
CHANGES = ['base', 'owned_a', 'owned_b', 'owned_ab', 'lexical', 'owned_ab_lexical', 'foreign_d', 'dictionary_reorder']


def function(x, theta):
    return x if theta == 1 else 9 - x


def contexts(n, seed):
    assert n % 8 == 0
    rng = np.random.default_rng(seed)
    designs = list(itertools.product([1, -1], repeat=3)) * (n // 8)
    rng.shuffle(designs)
    cs = []
    for i, (a, b, d) in enumerate(designs):
        rs = [{'source': s, 'input': x, 'rep': r} for s in [0, 1] for x in [2, 7] for r in [0, 1]]
        rs += [{'source': s, 'input': x, 'rep': 0} for s in [2, 3] for x in range(10)]
        rng.shuffle(rs)
        cs.append({'context': i, 'theta': [a, b, 1, d], 'codebook': rng.permutation(10).tolist(),
                   'records': rs, 'names': ['Alice', 'Bob', 'Casey', 'Eli']})
    assert Counter((c['theta'][0], c['theta'][1], c['theta'][3]) for c in cs) == Counter({t: n // 8 for t in itertools.product([1, -1], repeat=3)})
    return cs


def variant(c, change):
    ts, g = c['theta'].copy(), c['codebook'].copy()
    flipped = {'base': [], 'owned_a': [0], 'owned_b': [1], 'owned_ab': [0, 1],
               'lexical': [], 'owned_ab_lexical': [0, 1], 'foreign_d': [3], 'dictionary_reorder': []}[change]
    for s in flipped:
        ts[s] *= -1
    if change in ['lexical', 'owned_ab_lexical']:
        g = [c['codebook'][9 - x] if x not in [2, 7] else c['codebook'][x] for x in range(10)]
    rs = []
    for r in c['records']:
        s = r['source']
        x = 9 - r['input'] if s in flipped else r['input']
        if change == 'dictionary_reorder' and s == 2 and x not in [2, 7]:
            x = 9 - x
        rs.append({**r, 'input': x, 'word_index': g[function(x, ts[s])]})
    # Casey's complete known-copy records uniquely identify g. The remaining
    # sources' relations then uniquely identify one of the two operations.
    decoded = {r['input']: r['word_index'] for r in rs if r['source'] == 2}
    assert [decoded[x] for x in range(10)] == g and len(set(g)) == 10
    for s in [0, 1, 3]:
        consistent = [t for t in [1, -1] if all(g[function(r['input'], t)] == r['word_index'] for r in rs if r['source'] == s)]
        assert consistent == [ts[s]], (s, consistent, ts)
    return ts, g, rs


def encode(tok, c, change, mode, order, owner=None):
    ts, g, rs = variant(c, change)
    blocks = ['copy: use the input number.\n', 'subtract: use 9 minus the input number.\n']
    if order == 'subtract_first':
        blocks.reverse()
    text = ('All sources use the same codebook: each number from 0 through 9 has one unique label word. '
            'Each source applies one fixed operation before converting the result with this shared codebook. '
            'The two operations are:\n') + ''.join(blocks)
    text += ('Casey always copies the input number. Infer the other sources\' operations and the shared codebook from the records. '
             'Use the requested source\'s operation for the final input, then return its label word.\n')
    if mode == 'mixed_scope':
        text += 'Use only the requested source to infer its operation, and use Casey to infer the shared codebook.\n'
    if mode == 'direct':
        for s in [0, 1, 3]:
            text += c['names'][s] + ' always ' + ('copies the input number' if ts[s] == 1 else 'subtracts the input number from 9') + '.\n'
    ids = tok.encode(text + '\n', add_special_tokens=False)
    sites = []
    for r in rs:
        s = r['source']
        if owner is not None and s not in [owner, 2]:
            continue
        ids += tok.encode(f'Input: {r["input"]}\nSource: {c["names"][s]}\nLabel:', add_special_tokens=False)
        sites.append(len(ids))
        ids += tok.encode(' ' + WORDS[r['word_index']] + '\n\n', add_special_tokens=False)
    return ids, sites, ts, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=79001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    cs = contexts(a.n, a.seed)
    we = [tok.encode(' ' + w, add_special_tokens=False) for w in WORDS]
    assert all(len(e) == 1 for e in we), we
    wids = [e[0] for e in we]
    checks = 0
    for c in cs:
        for mode in MODES:
            for owner in [0, 1] if mode == 'own_dictionary' else [None]:
                base, sites, _, _ = encode(tok, c, 'base', mode, 'copy_first', owner)
                for order in ORDERS:
                    for change in CHANGES:
                        ids, ss, ts, g = encode(tok, c, change, mode, order, owner)
                        if mode != 'direct':
                            assert len(ids) == len(base) and Counter(ids) == Counter(base) and ss == sites
                        text = tok.decode(ids)
                        for s in [0, 1, 2] if owner is None else [owner, 2]:
                            for x in [0, 2, 3, 7, 9]:
                                q = f'Input: {x}\nSource: {c["names"][s]}\nLabel:'
                                assert tok.encode(text + q + ' ' + WORDS[g[function(x, ts[s])]], add_special_tokens=False) == ids + tok.encode(q, add_special_tokens=False) + [wids[g[function(x, ts[s])]]]
                                checks += 1
                # Verify the output-level XOR at all novel query values.
                bts, bg, _ = variant(c, 'base')
                ats, ag, _ = variant(c, 'owned_ab')
                lts, lg, _ = variant(c, 'lexical')
                both_ts, both_g, _ = variant(c, 'owned_ab_lexical')
                for s in [0, 1]:
                    for x in set(range(10)) - {2, 7}:
                        b = bg[function(x, bts[s])]
                        assert ag[function(x, ats[s])] == lg[function(x, lts[s])] != b
                        assert both_g[function(x, both_ts[s])] == b
    (d / 'preflight.json').write_text(json.dumps({'args': vars(a), 'checks': checks, 'words': WORDS, 'word_ids': wids}, indent=2))
    (d / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    if a.preflight_only:
        print('preflight passed', checks, flush=True)
        return
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
        device_map='cuda', attn_implementation='eager', output_loading_info=True)
    assert not loading.get('missing_keys') and not loading.get('unexpected_keys') and not loading.get('mismatched_keys'), loading
    model.eval()
    noops, audits = [], []

    def score(cache, plen, c, sources):
        qs = [tok.encode(f'Input: {x}\nSource: {c["names"][s]}\nLabel:', add_special_tokens=False) for s in sources for x in range(10)]
        nb, width = len(qs), max(map(len, qs))
        ids = torch.zeros((nb, width), dtype=torch.long, device='cuda')
        mask = torch.zeros((nb, plen + width), dtype=torch.long, device='cuda')
        mask[:, :plen] = 1
        pos = torch.zeros_like(ids)
        for i, q in enumerate(qs):
            ids[i, -len(q):] = torch.tensor(q, device='cuda')
            mask[i, -len(q):] = 1
            pos[i, -len(q):] = torch.arange(plen, plen + len(q), device='cuda')
        cc = copy.deepcopy(cache)
        cc.batch_repeat_interleave(nb)
        v = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cc,
                  use_cache=True, logits_to_keep=1).logits.float().log_softmax(-1)
        return v[:, -1, wids].cpu().numpy()

    with torch.inference_mode(), (d / 'behavior.jsonl').open('w') as f:
        for c in cs:
            scores, gold, computed = {}, {}, {}
            for mode in MODES:
                for order in ORDERS:
                    for change in CHANGES:
                        result = np.zeros((30, 10), dtype=np.float32)
                        for owner in [0, 1] if mode == 'own_dictionary' else [None]:
                            sources = [0, 1, 2] if owner is None else ([0, 2] if owner == 0 else [1])
                            ids, _, ts, g = encode(tok, c, change, mode, order, owner)
                            sig = (tuple(ids), tuple(sources))
                            if sig not in computed:
                                cache = model(input_ids=torch.tensor([ids], device='cuda'), use_cache=True).past_key_values
                                v = score(cache, len(ids), c, sources)
                                if c['context'] == 0 and change == 'base':
                                    e = float(np.max(np.abs(score(cache, len(ids), c, sources) - v)))
                                    noops.append(e)
                                    assert e <= .1, e
                                    for j, s in enumerate(sources):
                                        q = tok.encode(f'Input: 3\nSource: {c["names"][s]}\nLabel:', add_special_tokens=False)
                                        full = model(input_ids=torch.tensor([ids + q], device='cuda'), use_cache=False, logits_to_keep=1).logits.float().log_softmax(-1)[0, -1, wids].cpu().numpy()
                                        ae = float(np.max(np.abs(full - v[j * 10 + 3])))
                                        audits.append(ae)
                                        assert ae <= .1, ae
                                computed[sig] = v
                                del cache
                            result[np.concatenate([np.arange(s * 10, s * 10 + 10) for s in sources])] = computed[sig]
                        key = mode + '.' + order + '.' + change
                        scores[key] = result.tolist()
                        gold[key] = [g[function(x, ts[s])] for s in [0, 1, 2] for x in range(10)]
            f.write(json.dumps({'context': c['context'], 'theta': c['theta'], 'codebook': c['codebook'], 'scores': scores, 'gold': gold}) + '\n')
            f.flush()
            print(c['context'], round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0, 'no_op_max_error': max(noops), 'full_forward_max_error': max(audits),
           'audit_count': len(audits), 'torch': torch.__version__, 'transformers': transformers.__version__,
           'host': platform.node(), 'gpu': torch.cuda.get_device_name(), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (d / 'run.json').write_text(json.dumps(run, indent=2))


if __name__ == '__main__':
    main()
