"""Whole-query interventions on actual code-carrier mass and allocation.

Role-aligned donor weights are captured on native prompts, never chosen by gold
or correctness. Other attention conditionals and V remain live downstream.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.models.qwen3 import modeling_qwen3 as qm

from e71_relational import contexts, encode, fields, queries


def source_flip(logits, pi, demos):
    """Keep kind marginals and within-cell conditionals; swap source masses."""
    out = torch.zeros_like(pi)
    for kind in (0, 1):
        cells = [[i for i, d in enumerate(demos) if d['kind'] == kind and d['source'] == source]
                 for source in (0, 1)]
        for source in (0, 1):
            dst, other = cells[source], cells[1 - source]
            out[..., dst] = logits[..., dst].softmax(-1) * pi[..., other].sum(-1, keepdim=True)
    return out


def hashes():
    paths = [Path(__file__), Path(__file__).with_name('e71_relational.py'),
             Path(__file__).with_name('e58_factorization.py'), Path(__file__).with_name('e67_prefix.py')]
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=32)
    ap.add_argument('--seed', type=int, default=81001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args()
    start = time.time()
    source_hashes = hashes()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    ctxs = contexts('confirmation', a.n, a.seed)
    for c in ctxs:
        c['queries'] = c['queries'][:4]
    labels = ['toxic', 'safe']
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    label_ids = [tok.encode(' ' + x, add_special_tokens=False)[0] for x in labels]
    for word in ctxs[0]['names'] + ctxs[0]['codes'] + labels + ['Mark']:
        assert len(tok.encode(' ' + word, add_special_tokens=False)) == 1
    for c in ctxs:
        sequences = [encode(tok, c, labels, 'linked', layout) for layout in (0, 1)]
        assert sequences[0][1:] == sequences[1][1:]
        assert Counter(sequences[0][0]) == Counter(sequences[1][0])
        for q in c['queries']:
            x, y = [fields(tok, q, c, 'linked', layout) for layout in (0, 1)]
            assert len(x[0]) == len(y[0]) and Counter(x[0]) == Counter(y[0]) and x[1] == y[1]
    torch.manual_seed(810)
    cpu_logits = torch.randn(4, 3, 5, 16)
    cpu_pi = cpu_logits.softmax(-1)
    cpu_flip = source_flip(cpu_logits, cpu_pi, ctxs[0]['demos'])
    kind_error = max(float((cpu_pi[..., [i for i, d in enumerate(ctxs[0]['demos']) if d['kind'] == k]].sum(-1)
                           - cpu_flip[..., [i for i, d in enumerate(ctxs[0]['demos']) if d['kind'] == k]].sum(-1)).abs().max())
                     for k in (0, 1))
    assert kind_error < 2e-5 and float((cpu_flip.sum(-1) - 1).abs().max()) < 2e-5
    preflight = {'args': vars(a), 'n_contexts': len(ctxs), 'layout_checks': 'passed',
                 'kind_preservation_error': kind_error, 'source_hashes': source_hashes}
    (dest / 'preflight.json').write_text(json.dumps(preflight, indent=2))
    if a.preflight_only:
        print(json.dumps(preflight), flush=True)
        return
    torch.set_num_threads(6)
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, local_files_only=True, dtype=torch.float32, device_map='cuda', attn_implementation='eager').eval()
    original = qm.eager_attention_forward
    state = dict(active=False)
    errors = dict(self_margin=0., full_attention_self=0., full_forward=0., row_sum=0., mass_target=0.,
                  group_probability=0., masked_mass=0., kind_preservation=0.)

    def record_error(name, value):
        errors[name] = max(errors[name], float(value))

    def interface(module, query, key, value, attention_mask, scaling, dropout=0., **kw):
        out, p = original(module, query, key, value, attention_mask, scaling, dropout, **kw)
        if not state['active']:
            return out, p
        li = module.layer_idx
        group = state['group']
        valid = state['valid'][:, None, :, None]
        ks = qm.repeat_kv(key, module.num_key_value_groups)
        logits = torch.matmul(query, ks.transpose(2, 3)) * scaling
        if attention_mask is not None:
            logits += attention_mask[:, :, :, :ks.shape[-2]]
        group_logits = logits[..., group]
        m = p[..., group].sum(-1, keepdim=True)
        pi = group_logits.softmax(-1)
        mode = state['mode']
        if mode == 'native':
            state['capture'][li] = {'attention': p.clone(), 'mass': m.clone(),
                                    'pi': pi.clone(), 'group_logits': group_logits.clone()}
        else:
            own, donor = state['own'][li], state['donor'][li]
            if mode.startswith('full_attention'):
                target = own['attention'] if mode.endswith('self') else donor['attention']
                if not mode.endswith('self'):
                    target = target.clone()
                    # All demonstration columns are in the past: align code/Mark
                    # roles without permuting query columns or violating causality.
                    target[..., state['sites']['tag']] = donor['attention'][..., state['sites']['prefix']]
                    target[..., state['sites']['prefix']] = donor['attention'][..., state['sites']['tag']]
                pnew = torch.where(valid, target, p)
            else:
                tm = donor['mass'] if mode in ('mass', 'both') else own['mass']
                tp = donor['pi'] if mode in ('within', 'both') else own['pi']
                if mode == 'source_flip':
                    tp = source_flip(own['group_logits'], own['pi'], state['ctx']['demos'])
                    for kind in (0, 1):
                        cols = [j for j, d in enumerate(state['ctx']['demos']) if d['kind'] == kind]
                        record_error('kind_preservation', ((tp[..., cols].sum(-1) - own['pi'][..., cols].sum(-1))
                                                          * valid[..., 0]).abs().max())
                outside_logits = logits.clone()
                outside_logits[..., group] = -torch.inf
                outside = outside_logits.softmax(-1)
                target = (1 - tm) * outside
                target[..., group] = tm * tp
                pnew = torch.where(valid, target, p)
                record_error('mass_target', ((pnew[..., group].sum(-1, keepdim=True) - tm) * valid).abs().max())
                record_error('group_probability', ((pnew[..., group] - tm * tp) * valid).abs().max())
            record_error('row_sum', ((pnew.sum(-1) - 1) * valid[..., 0]).abs().max())
            if attention_mask is not None:
                forbidden = attention_mask[:, :, :, :ks.shape[-2]] < -1e10
                record_error('masked_mass', (pnew * forbidden * valid).sum(-1).max())
            p = pnew
            vs = qm.repeat_kv(value, module.num_key_value_groups)
            out = torch.matmul(p, vs).transpose(1, 2).contiguous()
        stats = {}
        for site, cols in [('carrier', group), ('label', state['sites']['label'])]:
            weights = p[..., cols] * valid
            total = weights.sum((1, 2, 3))
            match = state['source_match'][:, None, None, :]
            stats[site] = {
                'mass': (total / (state['valid'].sum(-1) * p.shape[1])).cpu().tolist(),
                'within_source': ((weights * match).sum((1, 2, 3)) / total.clamp_min(1e-30)).cpu().tolist(),
                'final_mass': p[:, :, -1, cols].sum(-1).mean(1).cpu().tolist(),
                'final_within_source': ((p[:, :, -1, cols] * state['source_match'][:, None, :]).sum((1, 2))
                                       / p[:, :, -1, cols].sum((1, 2)).clamp_min(1e-30)).cpu().tolist()}
        state['stats'][li] = stats
        return out, p

    qm.eager_attention_forward = interface

    def prefix(c, layout, instruction=False):
        state['active'] = False
        ids, sites, _ = encode(tok, c, labels, 'linked', layout, instruction)
        out = model(input_ids=torch.tensor([ids], device='cuda'), use_cache=True, logits_to_keep=1)
        return out.past_key_values, sites, len(ids), ids

    def score(cache, c, layout, sites, plen, mode='native', own=None, donor=None):
        ids, mask, pos = queries(tok, c, 'linked', layout, plen)
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(len(c['queries']))
        state.update(active=True, mode=mode, ctx=c, valid=mask[:, plen:].bool(), sites=sites,
                     group=sites['tag' if layout == 0 else 'prefix'], capture={}, stats={}, own=own, donor=donor,
                     source_match=torch.tensor([[q['source'] == d['source'] for d in c['demos']]
                                                for q in c['queries']], device='cuda'))
        out = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cp,
                    use_cache=True, logits_to_keep=1).logits[:, -1].float()
        state['active'] = False
        margin = (out[:, label_ids[1]] - out[:, label_ids[0]]).cpu().numpy()
        return margin, state['capture'], state['stats']

    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in ctxs))
    with (dest / 'behavior.jsonl').open('w') as stream, torch.inference_mode():
        for ci, c in enumerate(ctxs):
            caches, captured, sites, lengths, sequences = {}, {}, {}, {}, {}
            scores, attention = {}, {}
            for layout in (0, 1):
                caches[layout], sites[layout], lengths[layout], sequences[layout] = prefix(c, layout)
                key = f'D{layout}.native'
                scores[key], captured[layout], attention[key] = score(caches[layout], c, layout, sites[layout], lengths[layout])
                assert len(captured[layout]) == len(model.model.layers)
                if ci < 4:
                    for qi, q in enumerate(c['queries']):
                        seq = sequences[layout] + fields(tok, q, c, 'linked', layout)[0]
                        state['active'] = False
                        full = model(input_ids=torch.tensor([seq], device='cuda'), logits_to_keep=1).logits[0, -1].float()
                        delta = full[label_ids[1]] - full[label_ids[0]]
                        record_error('full_forward', abs(float(delta) - scores[key][qi]))
            assert sites[0] == sites[1] and lengths[0] == lengths[1]
            for layout in (0, 1):
                for mode in ['self', 'mass', 'within', 'both', 'source_flip', 'full_attention', 'full_attention_self']:
                    key = f'D{layout}.{mode}'
                    scores[key], _, attention[key] = score(caches[layout], c, layout, sites[layout], lengths[layout],
                                                           mode, captured[layout], captured[1 - layout])
                    if mode in ('self', 'full_attention_self'):
                        record_error('self_margin' if mode == 'self' else 'full_attention_self',
                                     abs(scores[key] - scores[f'D{layout}.native']).max())
                cache, st, pl, _ = prefix(c, layout, instruction=True)
                scores[f'D{layout}.instruction'], _, attention[f'D{layout}.instruction'] = score(cache, c, layout, st, pl)
            assert max(errors.values()) <= .01, errors
            for name in ['row_sum', 'mass_target', 'group_probability', 'kind_preservation']:
                assert errors[name] <= 2e-5, (name, errors)
            assert errors['masked_mass'] <= 1e-7
            stream.write(json.dumps({'context': ci, 'signs': [2*q['label'] - 1 for q in c['queries']],
                                     'scores': {k: list(map(float, v)) for k, v in scores.items()}, 'attention': attention}) + '\n')
            stream.flush()
            if ci % 4 == 0:
                print(json.dumps({'context': ci, 'elapsed_s': round(time.time() - start, 1), 'control': errors}), flush=True)
    qm.eager_attention_forward = original
    assert hashes() == source_hashes
    run = dict(args=vars(a), seconds=time.time() - start, control=errors, source_hashes=source_hashes,
               config_sha256=hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
               git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               torch=torch.__version__, transformers=transformers.__version__, host=platform.node(),
               gpu=torch.cuda.get_device_name(), n_layers=len(model.model.layers))
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
