"""Preregistered structural replay of label and intra-query attention.

Code-carrier probabilities are identical across the factorial conditions.
Outside conditional log probabilities are spliced, then renormalized; this is
not a pure edge mediation or an abstract algorithm transplantation.
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


def align_roles(x, sites):
    out = x.clone()
    out[..., sites['tag']] = x[..., sites['prefix']]
    out[..., sites['prefix']] = x[..., sites['tag']]
    return out


def mix_outside(own, donor, columns, final_only=False):
    out = own.clone()
    if final_only:
        out[..., -1, columns] = donor[..., -1, columns]
    else:
        out[..., columns] = donor[..., columns]
    return out.softmax(-1)


def hashes():
    paths = [Path(__file__), Path(__file__).with_name('e71_relational.py'),
             Path(__file__).with_name('e58_factorization.py'), Path(__file__).with_name('e67_prefix.py')]
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=32)
    ap.add_argument('--seed', type=int, default=82001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
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
        seq = [encode(tok, c, labels, 'linked', layout) for layout in (0, 1)]
        assert seq[0][1:] == seq[1][1:]
        assert Counter(seq[0][0]) == Counter(seq[1][0])
        for q in c['queries']:
            x, y = [fields(tok, q, c, 'linked', layout) for layout in (0, 1)]
            assert len(x[0]) == len(y[0]) and Counter(x[0]) == Counter(y[0]) and x[1] == y[1]
    torch.manual_seed(820)
    logits = torch.randn(4, 3, 5, 24)
    logits[..., 0] = -torch.inf
    own = logits.log_softmax(-1)
    donor = (logits + torch.randn_like(logits)).log_softmax(-1)
    whole = mix_outside(own, donor, list(range(1, 24)))
    self_out = mix_outside(own, own, [3, 5, 7])
    cpu_error = max(float((whole - donor.exp()).abs().max()),
                    float((self_out - own.exp()).abs().max()))
    assert cpu_error <= 2e-6
    preflight = dict(args=vars(a), n_contexts=len(ctxs), layout_checks='passed',
                     cpu_reconstruction_error=cpu_error, source_hashes=source_hashes)
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
    errors = dict(self_margin=0., full_attention_self=0., full_reconstruction=0.,
                  full_forward=0., row_sum=0., carrier_probability=0., masked_mass=0.)

    def error(name, value):
        errors[name] = max(errors[name], float(value))

    def interface(module, query, key, value, attention_mask, scaling, dropout=0., **kw):
        out, p = original(module, query, key, value, attention_mask, scaling, dropout, **kw)
        if not state['active']:
            return out, p
        li = module.layer_idx
        group = state['group']
        valid = state['valid'][:, None, :, None]
        mode = state['mode']
        if mode == 'native' or mode == 'carrier_live':
            ks = qm.repeat_kv(key, module.num_key_value_groups)
            logits = torch.matmul(query, ks.transpose(2, 3)) * scaling
            if attention_mask is not None:
                logits += attention_mask[:, :, :, :ks.shape[-2]]
            logits[..., group] = -torch.inf
            log_r = logits.log_softmax(-1)
        if mode == 'native':
            state['capture'][li] = dict(attention=p.clone(), log_r=log_r.clone())
        else:
            own = state['own'][li]
            donor = state['donor'][li]
            donor_p = align_roles(donor['attention'], state['sites'])
            donor_r = align_roles(donor['log_r'], state['sites'])
            code = donor_p[..., group]
            mass = code.sum(-1, keepdim=True)
            if mode == 'full_attention_self':
                target = own['attention']
            else:
                if mode == 'self':
                    code = own['attention'][..., group]
                    mass = code.sum(-1, keepdim=True)
                    r = own['log_r'].softmax(-1)
                elif mode == 'carrier_live':
                    r = log_r.softmax(-1)
                elif mode == 'full':
                    r = donor_r.softmax(-1)
                else:
                    cols = []
                    if mode in ('label', 'label_query', 'label_final'):
                        cols += state['sites']['label']
                    if mode in ('query', 'label_query'):
                        cols += list(range(state['plen'], p.shape[-1]))
                    assert mode in ('frozen_base', 'label', 'query', 'label_query', 'label_final')
                    r = mix_outside(own['log_r'], donor_r, cols, final_only=mode == 'label_final')
                target = (1 - mass) * r
                target[..., group] = code
                if mode == 'full':
                    error('full_reconstruction', ((target - donor_p) * valid).abs().max())
            pnew = torch.where(valid, target, p)
            error('row_sum', ((pnew.sum(-1) - 1) * valid[..., 0]).abs().max())
            if mode not in ('self', 'full_attention_self'):
                error('carrier_probability', ((pnew[..., group] - donor_p[..., group]) * valid).abs().max())
            if attention_mask is not None:
                forbidden = attention_mask[:, :, :, :p.shape[-1]] < -1e10
                error('masked_mass', (pnew * forbidden * valid).sum(-1).max())
            p = pnew
            vs = qm.repeat_kv(value, module.num_key_value_groups)
            out = torch.matmul(p, vs).transpose(1, 2).contiguous()
        stats = {}
        for site, cols in [('carrier', group), ('label', state['sites']['label'])]:
            weights = p[..., cols] * valid
            total = weights.sum((1, 2, 3))
            stats[site] = dict(mass=(total / (state['valid'].sum(-1) * p.shape[1])).cpu().tolist(),
                               final_mass=p[:, :, -1, cols].sum(-1).mean(1).cpu().tolist())
            for factor in ['source', 'kind']:
                match = state[factor + '_match'][:, None, None, :]
                stats[site]['within_' + factor] = ((weights * match).sum((1, 2, 3))
                                                   / total.clamp_min(1e-30)).cpu().tolist()
                stats[site]['final_within_' + factor] = ((p[:, :, -1, cols] * match[:, :, 0]).sum((1, 2))
                        / p[:, :, -1, cols].sum((1, 2)).clamp_min(1e-30)).cpu().tolist()
        qweights = p[..., state['plen']:] * valid
        stats['query'] = dict(mass=(qweights.sum((1, 2, 3)) / (state['valid'].sum(-1) * p.shape[1])).cpu().tolist(),
                              final_mass=p[:, :, -1, state['plen']:].sum(-1).mean(1).cpu().tolist())
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
        state.update(active=True, mode=mode, valid=mask[:, plen:].bool(), sites=sites, plen=plen,
                     group=sites['tag' if layout == 0 else 'prefix'], capture={}, stats={}, own=own, donor=donor)
        for factor in ['source', 'kind']:
            state[factor + '_match'] = torch.tensor([[q[factor] == d[factor] for d in c['demos']]
                                                      for q in c['queries']], device='cuda')
        out = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cp,
                    use_cache=True, logits_to_keep=1).logits[:, -1].float()
        state['active'] = False
        return (out[:, label_ids[1]] - out[:, label_ids[0]]).cpu().numpy(), state['capture'], state['stats']

    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in ctxs))
    (dest / 'native_features').mkdir(exist_ok=True)
    with (dest / 'behavior.jsonl').open('w') as stream, torch.inference_mode():
        for ci, c in enumerate(ctxs):
            caches, captured, sites, lengths, sequences = {}, {}, {}, {}, {}
            scores, attention = {}, {}
            for layout in (0, 1):
                caches[layout], sites[layout], lengths[layout], sequences[layout] = prefix(c, layout)
                k = f'D{layout}.native'
                scores[k], captured[layout], attention[k] = score(caches[layout], c, layout, sites[layout], lengths[layout])
                assert len(captured[layout]) == len(model.model.layers)
                if ci < 4:
                    for qi, q in enumerate(c['queries']):
                        seq = sequences[layout] + fields(tok, q, c, 'linked', layout)[0]
                        state['active'] = False
                        full = model(input_ids=torch.tensor([seq], device='cuda'), logits_to_keep=1).logits[0, -1].float()
                        error('full_forward', abs(float(full[label_ids[1]] - full[label_ids[0]]) - scores[k][qi]))
            assert sites[0] == sites[1] and lengths[0] == lengths[1]
            for mode in ['self', 'full_attention_self', 'carrier_live', 'frozen_base',
                         'label', 'query', 'label_query', 'label_final', 'full']:
                k = 'D0.' + mode
                scores[k], _, attention[k] = score(caches[0], c, 0, sites[0], lengths[0], mode,
                                                    captured[0], captured[1])
                if mode in ('self', 'full_attention_self'):
                    error('self_margin' if mode == 'self' else 'full_attention_self',
                          abs(scores[k] - scores['D0.native']).max())
            for layout in (0, 1):
                cache, st, pl, _ = prefix(c, layout, instruction=True)
                k = f'D{layout}.instruction'
                scores[k], _, attention[k] = score(cache, c, layout, st, pl)
            assert max(errors.values()) <= .01, errors
            for k in ['row_sum', 'carrier_probability', 'full_reconstruction']:
                assert errors[k] <= 2e-5, (k, errors)
            assert errors['masked_mass'] <= 1e-7
            native_features = {}
            for layout in (0, 1):
                native_features[f'D{layout}_label_log_r'] = torch.stack([
                    captured[layout][li]['log_r'][..., sites[layout]['label']].cpu()
                    for li in range(len(model.model.layers))]).numpy()
            np.savez_compressed(dest / 'native_features' / f'{ci:03d}.npz', **native_features)
            stream.write(json.dumps(dict(context=ci, signs=[2*q['label']-1 for q in c['queries']],
                                         scores={k: list(map(float, v)) for k, v in scores.items()}, attention=attention)) + '\n')
            stream.flush()
            if ci % 4 == 0:
                print(json.dumps(dict(context=ci, elapsed_s=round(time.time()-t0, 1), control=errors)), flush=True)
    qm.eager_attention_forward = original
    assert hashes() == source_hashes
    run = dict(args=vars(a), seconds=time.time()-t0, control=errors, source_hashes=source_hashes,
               config_sha256=hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
               git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               torch=torch.__version__, transformers=transformers.__version__, host=platform.node(),
               gpu=torch.cuda.get_device_name(), n_layers=len(model.model.layers))
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
