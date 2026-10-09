"""Separate redundant relational code from an expanded answer namespace.

Fresh code words; E70's frozen shift is reused without rescaling or re-estimation.
Only natural queries are capability reads; inverted codes diagnose cue use.
"""
import argparse
import copy
from collections import Counter
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb
from e58_factorization import make_contexts
from e59_mediation import patch
from e67_prefix import HEAD, INSTRUCTION, MARKER

FRAME_SHA = 'bcec93a6282d781665716699083885caad6c636414beb65ec5da7b19f8b0f3d9'


def contexts(stage, n, seed):
    out = make_contexts(stage, n, seed)
    rng = np.random.default_rng(seed + 971)
    names = ['Alex', 'Sam'] if stage == 'discovery' else ['Alice', 'Bob']
    codes = ['Red', 'Blue'] if stage == 'discovery' else ['Left', 'Right']
    for c in out:
        perm = int(rng.integers(2))
        for d in c['demos']:
            d['linked_code'] = d['source'] ^ perm
        for source in (0, 1):
            for kind in (0, 1):
                ds = [d for d in c['demos'] if d['source'] == source and d['kind'] == kind]
                assignment = rng.permutation([0, 0, 1, 1])
                for d, code in zip(ds, assignment):
                    d['orthogonal_code'] = int(code)
        for q in c['queries']:
            q['code'] = q['source'] ^ perm
        conflicts = copy.deepcopy(c['queries'])
        for q in conflicts:
            q['code'] ^= 1
        c['queries'] += conflicts
        c.update(names=names, codes=codes, code_permutation=perm)
        for source in (0, 1):
            for kind in (0, 1):
                for code in (0, 1):
                    assert sum(d['source'] == source and d['kind'] == kind and d['orthogonal_code'] == code for d in c['demos']) == 2
    return out


def fields(tok, ex, ctx, relation, layout):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    code = ctx['codes'][ex['code'] if 'code' in ex else ex[relation + '_code']]
    tag, pref = (code, MARKER) if layout == 0 else (MARKER, code)
    ids = enc(f'Item: {ex["word"]}\nSource:')
    sites = {'source': len(ids)}
    ids += enc(' ' + ctx['names'][ex['source']]) + enc('\nTag:')
    sites['tag'] = len(ids)
    ids += enc(' ' + tag) + enc('\nLabel:')
    sites['prefix'] = len(ids)
    ids += enc(' ' + pref)
    return ids, sites


def encode(tok, ctx, labels, relation, layout, instruction=False):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    ids = enc(HEAD + (INSTRUCTION if instruction else ''))
    sites = {k: [] for k in ['source', 'tag', 'prefix', 'label']}
    bounds = []
    for ex in ctx['demos']:
        start = len(ids)
        block, st = fields(tok, ex, ctx, relation, layout)
        for k, v in st.items():
            sites[k].append(start + v)
        ids += block
        sites['label'].append(len(ids))
        label = enc(' ' + labels[ex['label']])
        assert len(label) == 1
        ids += label + enc('\n\n')
        bounds.append((start, len(ids)))
    return ids, sites, bounds


def queries(tok, ctx, relation, layout, plen):
    seqs = [fields(tok, q, ctx, relation, layout)[0] for q in ctx['queries']]
    width = max(map(len, seqs))
    ids = torch.zeros((len(seqs), width), dtype=torch.long, device='cuda')
    mask = torch.zeros((len(seqs), plen + width), dtype=torch.long, device='cuda')
    mask[:, :plen] = 1
    pos = torch.zeros_like(ids)
    for i, seq in enumerate(seqs):
        ids[i, -len(seq):] = torch.tensor(seq, device='cuda')
        mask[i, -len(seq):] = 1
        pos[i, -len(seq):] = torch.arange(plen, plen + len(seq), device='cuda')
    return ids, mask, pos


def main():
    ap = argparse.ArgumentParser()
    for x in ['model', 'out', 'stage', 'frame_source']:
        ap.add_argument('--' + x.replace('_', '-'), required=True)
    for x in ['n', 'seed']:
        ap.add_argument('--' + x, type=int, required=True)
    a = ap.parse_args()
    assert a.stage in ['discovery', 'confirmation']
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    ctxs = contexts(a.stage, a.n, a.seed)
    labels = ['yes', 'no'] if a.stage == 'discovery' else ['toxic', 'safe']
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    tokens = [tok.encode(' ' + s, add_special_tokens=False) for s in ctxs[0]['names'] + ctxs[0]['codes'] + [MARKER] + labels]
    assert all(len(t) == 1 for t in tokens) and len({t[0] for t in tokens}) == len(tokens)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
                                               device_map='cuda', attn_implementation='eager').eval()
    frame_path = Path(a.frame_source)
    frame_sha = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    assert frame_sha == FRAME_SHA
    frozen = torch.from_numpy(np.load(frame_path)).to(device='cuda', dtype=torch.float32)
    label_ids = [t[0] for t in tokens[-2:]]
    state = dict(audit=False, measure=False, capture=False, mass_max=0.0, q={})
    errors, features, spreads, untouched = [], [], [], []

    for li, layer in enumerate(model.model.layers):
        def hook(idx):
            def h(module, args, kwargs, output):
                if state['audit']:
                    mass = (output[1].float() * state['forbidden'][None, None]).sum(-1).max()
                    state['mass_max'] = max(state['mass_max'], float(mass))
                if state['measure']:
                    record = {}
                    for site in ['prefix', 'label']:
                        p = output[1][..., state['sites'][site]].float()
                        p = p * state['qmask'][:, None, :, None]
                        denom = p.sum((1, 2, 3))
                        record[site] = {
                            'mass': (denom / (state['qmask'].sum(-1) * p.shape[1]).clamp_min(1e-9)).cpu().tolist(),
                            'within_source': ((p * state['source_match'][:, None, None]).sum((1, 2, 3)) / denom.clamp_min(1e-9)).cpu().tolist(),
                            'within_code': ((p * state['code_match'][:, None, None]).sum((1, 2, 3)) / denom.clamp_min(1e-9)).cpu().tolist()}
                    state['attention'][idx] = record
                if state['capture']:
                    hs = kwargs.get('hidden_states', args[0] if args else None)
                    q = module.q_norm(module.q_proj(hs).view(*hs.shape[:-1], -1, module.head_dim)).transpose(1, 2)
                    q, _ = apply_rotary_pos_emb(q, q, *kwargs['position_embeddings'])
                    state['q'][idx] = q.float().clone()
                return output
            return h
        layer.self_attn.register_forward_hook(hook(li), with_kwargs=True)

    def prefix(ctx, relation, layout=1, mode='native', instruction=False):
        ids, st, bounds = encode(tok, ctx, labels, relation, layout, instruction)
        pl = len(ids)
        kw = {}
        if mode != 'native':
            causal = torch.ones((pl, pl), dtype=torch.bool, device='cuda').tril()
            if mode == 'blind':
                cols = torch.zeros(pl, dtype=torch.bool, device='cuda')
                cols[st['label']] = True
                forbidden = causal & cols[None] & ~torch.eye(pl, dtype=torch.bool, device='cuda')
            elif mode == 'isolated':
                owner = torch.full((pl,), -1, dtype=torch.long, device='cuda')
                for j, (start, end) in enumerate(bounds):
                    owner[start:end] = j
                forbidden = causal & (owner[:, None] != owner[None]) & (owner[:, None] >= 0) & (owner[None] >= 0)
            else:
                assert mode == 'full'
                forbidden = torch.zeros_like(causal)
            kw['attention_mask'] = torch.zeros((pl, pl), dtype=torch.float32, device='cuda').masked_fill(~(causal & ~forbidden), torch.finfo(torch.float32).min)[None, None]
            state.update(audit=mode != 'full', forbidden=forbidden)
        out = model(input_ids=torch.tensor([ids], device='cuda'), use_cache=True, logits_to_keep=1, **kw)
        state['audit'] = False
        return out.past_key_values, st, pl

    def score(cache, ctx, relation, layout, st, pl, capture=False, measure=True):
        ids, mask, pos = queries(tok, ctx, relation, layout, pl)
        c = copy.deepcopy(cache)
        c.batch_repeat_interleave(len(ctx['queries']))
        state.update(measure=measure, capture=capture, sites=st, qmask=mask[:, pl:].float(), attention={},
                     source_match=torch.tensor([[q['source'] == d['source'] for d in ctx['demos']] for q in ctx['queries']], device='cuda'),
                     code_match=torch.tensor([[q['code'] == d[relation + '_code'] for d in ctx['demos']] for q in ctx['queries']], device='cuda'))
        logits = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=c,
                       use_cache=True, logits_to_keep=1).logits[:, -1].float()
        state.update(measure=False, capture=False)
        return (logits[:, label_ids[1]] - logits[:, label_ids[0]]).cpu().numpy(), state['attention']

    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in ctxs))
    with (dest / 'behavior.jsonl').open('w') as f, torch.inference_mode():
        for ci, ctx in enumerate(ctxs):
            sequences = {}
            reference_sites = None
            for relation in ['linked', 'orthogonal']:
                for layout in (0, 1):
                    ids, st, _ = encode(tok, ctx, labels, relation, layout)
                    sequences[relation + str(layout)] = ids
                    reference_sites = st if reference_sites is None else reference_sites
                    assert st == reference_sites
            assert all(Counter(ids) == Counter(sequences['linked0']) and len(ids) == len(sequences['linked0']) for ids in sequences.values())
            for q in ctx['queries']:
                x, xs = fields(tok, q, ctx, 'linked', 0)
                y, ys = fields(tok, q, ctx, 'linked', 1)
                assert len(x) == len(y) and Counter(x) == Counter(y) and xs == ys
            if ci == 0:
                (dest / 'layout.json').write_text(json.dumps({k: tok.decode(v) for k, v in sequences.items()}, indent=2))
            scores, attention = {}, {}
            for relation in ['linked', 'orthogonal']:
                base, st, pl = prefix(ctx, relation)
                c0, s0, p0 = prefix(ctx, relation, 0)
                scores[relation + '.D0'], attention[relation + '.D0'] = score(c0, ctx, relation, 0, s0, p0)
                scores[relation + '.D1'], attention[relation + '.D1'] = score(base, ctx, relation, 1, st, pl, capture=True)
                full, _, _ = prefix(ctx, relation, mode='full')
                v, _ = score(full, ctx, relation, 1, st, pl, measure=False)
                errors.append(float(abs(v - scores[relation + '.D1']).max()))
                blind, _, _ = prefix(ctx, relation, mode='blind')
                iso, _, _ = prefix(ctx, relation, mode='isolated')
                fc = copy.deepcopy(ctx)
                for d in fc['demos']:
                    d['label'] ^= 1
                bf, _, _ = prefix(fc, relation, mode='blind')
                nonlabel = [j for j in range(pl) if j not in st['label']]
                for x, y in zip(blind.layers, bf.layers):
                    features.extend([float((x.keys[:, :, nonlabel] - y.keys[:, :, nonlabel]).abs().max()),
                                     float((x.values[:, :, nonlabel] - y.values[:, :, nonlabel]).abs().max())])
                variant_names = ['isolated', 'blind', 'common', 'centered', 'norm', 'negative_common', 'shared_frame']
                variants = {k: copy.deepcopy(base) for k in variant_names}
                keep = [j for j in range(pl) if j not in st['prefix']]
                for li, (x, y, native) in enumerate(zip(iso.layers, blind.layers, base.layers)):
                    ps = st['prefix']
                    ik, bk = x.keys[:, :, ps], y.keys[:, :, ps]
                    delta = bk - ik
                    mean = delta.mean(2, keepdim=True)
                    mats = {'isolated': ik, 'blind': bk, 'common': ik + mean, 'centered': bk - mean,
                            'norm': ik * bk.norm(dim=-1, keepdim=True) / ik.norm(dim=-1, keepdim=True).clamp_min(1e-8),
                            'negative_common': ik - mean, 'shared_frame': ik + frozen[li]}
                    for k, m in mats.items():
                        v = variants[k].layers[li]
                        v.keys[:, :, ps] = m
                        untouched.extend([float((v.values - native.values).abs().max()), float((v.keys[:, :, keep] - native.keys[:, :, keep]).abs().max())])
                    for name in ['common', 'shared_frame']:
                        q = state['q'][li]
                        change = variants[name].layers[li].keys[:, :, ps] - ik
                        change = change.repeat_interleave(q.shape[1] // change.shape[1], dim=1)
                        logits = q @ change.transpose(-1, -2) / q.shape[-1] ** .5
                        spreads.append(float((logits.max(-1).values - logits.min(-1).values).max()))
                for k, c in variants.items():
                    scores[relation + '.' + k], attention[relation + '.' + k] = score(c, ctx, relation, 1, st, pl)
                v, _ = score(patch(base, base, st['prefix'], 'key'), ctx, relation, 1, st, pl, measure=False)
                errors.append(float(abs(v - scores[relation + '.D1']).max()))
                for layout in (0, 1):
                    c, s, p = prefix(ctx, relation, layout, instruction=True)
                    scores[relation + f'.D{layout}.instruction'], _ = score(c, ctx, relation, layout, s, p, measure=False)
                    pieces = []
                    for source in (0, 1):
                        ind = [j for j, q in enumerate(ctx['queries']) if q['source'] == source]
                        sc = dict(ctx, demos=[d for d in ctx['demos'] if d['source'] == source], queries=[ctx['queries'][j] for j in ind])
                        c, s, p = prefix(sc, relation, layout)
                        v, _ = score(c, sc, relation, layout, s, p, measure=False)
                        pieces.extend(zip(ind, map(float, v)))
                    scores[relation + f'.D{layout}.single'] = [v for _, v in sorted(pieces)]
            assert max(features) == 0 and state['mass_max'] == 0 and max(untouched) == 0
            f.write(json.dumps({'context': ci, 'signs': [2 * q['label'] - 1 for q in ctx['queries']],
                                'scores': {k: list(map(float, v)) for k, v in scores.items()}, 'attention': attention}) + '\n')
            f.flush()
            if ci % 4 == 0:
                print(ci, round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0, 'sanity_max_error': max(errors),
           'nonlabel_flip_feature_error_max': max(features), 'forbidden_attention_mass_max': state['mass_max'],
           'fixedQ_shared_relative_logit_spread_max': max(spreads), 'untouched_cache_error_max': max(untouched),
           'torch': torch.__version__, 'transformers': transformers.__version__, 'host': platform.node(),
           'gpu': torch.cuda.get_device_name(), 'frame_sha256': frame_sha,
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (dest / 'control_report.json').write_text(json.dumps(run, indent=2))
    assert max(errors) <= .1 and max(spreads) <= .02, run
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
