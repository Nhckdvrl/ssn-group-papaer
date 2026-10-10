"""E94: criterion transport from a source's pre-input Goal field, no training."""
import argparse, hashlib, itertools, json, platform, random, subprocess, time
from pathlib import Path
from e93_selective_sharing import contexts, body, design_audit, estimate

BANDS = (16, 32, 48)
SYSTEM = "Infer the requested reviewer's rule from the examples. Return exactly yes or no."


def analyze(rows):
    ids = sorted({r['context'] for r in rows}); out = {'n_rows': len(rows), 'n_contexts': len(ids), 'conditions': {}}
    for cond in sorted({r['condition'] for r in rows}):
        rr = [r for r in rows if r['condition'] == cond]; vals = {}
        for subset in ('all', 'discordant', 'concordant'):
            ss = [r for r in rr if subset == 'all' or r['discordant'] == (subset == 'discordant')]
            for metric in ('current_binary_accuracy', 'other_binary_accuracy', 'valid_fraction', 'current_argmax_accuracy', 'other_argmax_accuracy'):
                def score(r):
                    if metric == 'valid_fraction': return r['valid']
                    if metric == 'other_binary_accuracy': return r['pred'] == r['other_gold']
                    if metric == 'other_argmax_accuracy': return r['argmax_class'] == r['other_gold']
                    return (r['argmax_class'] if metric == 'current_argmax_accuracy' else r['pred']) == r['gold']
                vals[subset+'_'+metric] = estimate([sum(score(r) for r in ss if r['context'] == ci)/sum(r['context'] == ci for r in ss) for ci in ids])
        if cond.startswith(('inv_', 'sign_', 'rand_inv_', 'rand_sign_', 'address_')):
            vals['transport_T_nats'] = estimate([sum(r['transport_T'] for r in rr if r['context'] == ci and r['discordant'])/sum(r['context'] == ci and r['discordant'] for r in rr) for ci in ids])
            if cond.startswith('address_'):
                vals['transport_T_all_nats'] = estimate([sum(r['transport_T'] for r in rr if r['context'] == ci)/sum(r['context'] == ci for r in rr) for ci in ids])
            vals['concordant_absolute_perturbation'] = estimate([sum(abs(r['z']-r['base_z']) for r in rr if r['context'] == ci and not r['discordant'])/sum(r['context'] == ci and not r['discordant'] for r in rr) for ci in ids])
            profiles = {}
            for pa, cb in itertools.product((1, -1), (0, 1)):
                ss = [r for r in rr if r['pa'] == pa and r['cb'] == cb and r['discordant']]
                profiles[f'pa{pa}_cb{cb}'] = estimate([sum(r['transport_T'] for r in ss if r['context'] == ci)/sum(r['context'] == ci for r in ss) for ci in ids])
            vals['four_profiles'] = profiles
        out['conditions'][cond] = vals
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B'); ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=4); ap.add_argument('--seed', type=int, default=94001); ap.add_argument('--batch-size', type=int, default=4); ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args(); p = Path(a.out); p.mkdir(parents=True, exist_ok=True); assert not (p/'behavior.jsonl').exists()
    cs = contexts(a.n, a.seed); audit = design_audit(cs)
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs)); (p/'design_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True); tok.padding_side = 'left'
    if tok.pad_token_id is None: tok.pad_token_id = tok.eos_token_id
    lid = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]; assert all(len(v) == 1 for v in lid); lid = [v[0] for v in lid]
    def record(c, pa, cb, pb, role, qi):
        b = body(c, 'probe' if role else 'native', pa, cb, pb, 0, qi)
        prompt = tok.apply_chat_template([{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': b}], tokenize=False, add_generation_prompt=True, enable_thinking=False)+'Answer:'
        goal = f'Reviewer: {c["names"][role]}'
        start = prompt.rfind(goal+'\nReview:'); assert start >= 0
        end = start+len(goal); prefix = prompt[:end]
        enc = tok(prefix, return_offsets_mapping=True, add_special_tokens=False); ids = enc.input_ids
        goal_start = next(i for i, (_, stop) in enumerate(enc.offset_mapping) if stop > start)
        full = tok.encode(prompt, add_special_tokens=False); assert full[:len(ids)] == ids, 'prefix is not an exact token boundary'
        x = c['queries'][qi]['x']; gold = (pb if role else pa)*x[cb]
        return {'context': c['context'], 'pa': pa, 'cb': cb, 'pb': pb, 'role': role, 'query': qi, 'discordant': x[0] != x[1],
                'gold': gold, 'other_gold': (pb if role else pa)*x[1-cb], 'prompt': prompt, 'prefix': prefix, 'prefix_ids': ids,
                'goal_start': goal_start, 'goal_length': len(ids)-goal_start, 'input_before_prefix': False}
    donor_sets = []; receiver_sets = []; preflight = []
    for c in cs:
        donors = {(pa, cb, pb): record(c, pa, cb, pb, 1, 0) for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1))}
        receivers = {cond: [record(c, pa, cb, (-pa if 'conflict' in cond else pa), role, qi)
                           for pa, cb, qi in itertools.product((1, -1), (0, 1), range(4))]
                     for cond, role in [('a_native', 0), ('b_native', 1), ('a_conflict', 0), ('b_conflict', 1)]}
        assert len({r['goal_length'] for r in donors.values()}) == 1
        assert len({len(r['prefix_ids']) for r in donors.values()}) == 1
        for rr in receivers.values():
            assert all(r['goal_length'] == next(iter(donors.values()))['goal_length'] for r in rr)
            for pa, cb in itertools.product((1, -1), (0, 1)):
                group = [r for r in rr if r['pa'] == pa and r['cb'] == cb]
                assert len({r['prefix'] for r in group}) == 1
        donor_sets.append(donors); receiver_sets.append(receivers)
        preflight.append({'context': c['context'], 'donor_count': len(donors), 'goal_tokens': next(iter(donors.values()))['goal_length'],
                          'prefix_length': len(next(iter(donors.values()))['prefix_ids']), 'all_future_inputs_excluded': True,
                          'token_prefix_and_all_four_queries_aligned': True})
    config = json.loads((Path(a.model)/'config.json').read_text()); textconfig = config.get('text_config', config)
    assert textconfig['num_hidden_layers'] == 64
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'label_ids': lid, 'bands_1based': BANDS, 'cases': preflight,
        'actual_model_type': textconfig['model_type'], 'future_input_excluded_from_directions': True,
        'context0_goal_prefix_example': next(iter(donor_sets[0].values()))['prefix'], 'projection_or_training': False}, indent=2)+'\n')
    if a.preflight_only: print('preflight passed', preflight, flush=True); return
    import torch, transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); t0 = time.time(); print('Loading float32 two-device model', flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32, device_map='auto',
            max_memory={0: '64GiB', 1: '64GiB'}, attn_implementation='eager', output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'), loading
    assert set(model.hf_device_map.values()) <= {0, 1, 'cuda:0', 'cuda:1'}, model.hf_device_map
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    (p/'loading_info.json').write_text(json.dumps(loading, indent=2, default=str)+'\n'); assert len(model.model.layers) == 64
    print('Loaded', model.hf_device_map, flush=True); errors = {'self_copy_max_nats': 0., 'non_goal_max': 0.}; all_rows = []; norms = []
    def batch(rr, prefix=False):
        xx = tok([r['prefix'] if prefix else r['prompt'] for r in rr], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda:0')
        pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
        starts = [xx.input_ids.shape[1]-int(xx.attention_mask[i].sum())+r['goal_start'] for i, r in enumerate(rr)]
        return xx, pos, starts
    def field(h, starts, rr): return torch.stack([h[i, st:st+r['goal_length']].detach().cpu() for i, (st, r) in enumerate(zip(starts, rr))])
    def forward(rr, layer=None, op=None, captured=None):
        xx, pos, starts = batch(rr); handle = None
        if layer is not None:
            def hook(module, inp, out):
                assert isinstance(out, torch.Tensor); h = out.clone()
                if op == 'capture': captured[layer] = field(h, starts, rr); return out
                for i, (st, r) in enumerate(zip(starts, rr)):
                    sl = slice(st, st+r['goal_length']); vv = op(i, r).to(h.device, dtype=h.dtype)
                    h[i, sl] = vv if captured == 'replace' else h[i, sl]+vv
                mask = torch.ones(h.shape[:2], dtype=torch.bool, device=h.device)
                for i, (st, r) in enumerate(zip(starts, rr)): mask[i, st:st+r['goal_length']] = False
                err = float((h[mask]-out[mask]).abs().max()); errors['non_goal_max'] = max(errors['non_goal_max'], err); assert err == 0
                return h
            handle = model.model.layers[layer-1].register_forward_hook(hook)
        try: lo = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float().cpu()
        finally:
            if handle is not None: handle.remove()
        return lo
    def score(rr, lo, condition, base=None, address=False):
        zs = (lo[:, lid[1]]-lo[:, lid[0]]).tolist(); tops = lo.argmax(-1).tolist()
        for j, (r, z, top) in enumerate(zip(rr, zs, tops)):
            d = {k: v for k, v in r.items() if k not in ('prompt', 'prefix', 'prefix_ids')}
            if address: d['other_gold'] = r['pb']*cs[r['context']]['queries'][r['query']]['x'][r['cb']]
            d.update(condition=condition, z=z, pred=1 if z >= 0 else -1, argmax_class=1 if top == lid[1] else -1 if top == lid[0] else 0, argmax_token=top, valid=top in lid)
            if base is not None:
                d['base_z'] = base[j]; d['transport_T'] = d['other_gold']*(z-base[j])/2
            all_rows.append(d); stream.write(json.dumps(d)+'\n')
        stream.flush()
    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as stream:
        for ci, (c, donors, receivers) in enumerate(zip(cs, donor_sets, receiver_sets)):
            rr = list(donors.values()); xx, pos, starts = batch(rr, prefix=True); caught = {}; handles = []
            for layer in BANDS:
                def collect(module, inp, out, layer=layer): caught[layer] = field(out, starts, rr)
                handles.append(model.model.layers[layer-1].register_forward_hook(collect))
            try: model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False)
            finally:
                for h in handles: h.remove()
            lookup = {layer: {key: caught[layer][j] for j, key in enumerate(donors)} for layer in BANDS}; dirs = {}
            for layer in BANDS:
                dp = {pb: sum(lookup[layer][pa, 1, pb]-lookup[layer][pa, 0, pb] for pa in (1, -1))/2 for pb in (1, -1)}
                inv = (dp[1]+dp[-1])/2; signed = (dp[1]-dp[-1])/2
                rng = torch.Generator().manual_seed(940+c['context']*100+layer); ran = torch.randn(inv.shape, generator=rng); ran /= ran.norm()
                dirs[layer] = {'inv': inv, 'sign': signed, 'rand_inv': ran*inv.norm(), 'rand_sign': ran*signed.norm()}
                norms.append({'context': c['context'], 'layer': layer, 'inv_norm': float(inv.norm()), 'sign_norm': float(signed.norm()),
                              'plus_norm': float(dp[1].norm()), 'minus_norm': float(dp[-1].norm())})
            for cond, rows in receivers.items():
                for st in range(0, len(rows), a.batch_size):
                    rb = rows[st:st+a.batch_size]; base_lo = forward(rb); base_z = (base_lo[:, lid[1]]-base_lo[:, lid[0]]).tolist(); score(rb, base_lo, cond)
                    if cond == 'a_native':
                        for layer in BANDS:
                            if ci == 0 and st == 0:
                                ref = {}; forward(rb, layer, 'capture', ref)
                                noop = forward(rb, layer, lambda j, r: ref[layer][j], 'replace'); er = float((base_lo-noop).abs().max())
                                errors['self_copy_max_nats'] = max(errors['self_copy_max_nats'], er); assert er <= .001
                            for kind in ('inv', 'sign', 'rand_inv', 'rand_sign'):
                                def operator(j, r, kind=kind, layer=layer):
                                    sign = 1 if r['cb'] == 0 else -1
                                    if kind in ('sign', 'rand_sign'): sign *= r['pa']
                                    return sign*dirs[layer][kind]
                                lo = forward(rb, layer, operator); score(rb, lo, f'{kind}_{layer}', base_z)
                    elif cond == 'a_conflict':
                        for layer in BANDS:
                            lo = forward(rb, layer, lambda j, r, layer=layer: lookup[layer][r['pa'], r['cb'], r['pb']], 'replace')
                            score(rb, lo, f'address_{layer}', base_z, address=True)
            print('context', ci+1, '/', a.n, 'rows', len(all_rows), flush=True)
    elapsed = time.time()-t0
    (p/'analysis.json').write_text(json.dumps(analyze(all_rows), indent=2)+'\n'); (p/'direction_norms.json').write_text(json.dumps(norms, indent=2)+'\n')
    run = {'args': vars(a), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'dependency_sha256': hashlib.sha256(Path('scripts/e93_selective_sharing.py').read_bytes()).hexdigest(),
        'n_rows': len(all_rows), 'dtype': 'float32', 'attention': 'eager', 'training': False, 'errors': errors, 'bands_1based': BANDS,
        'elapsed_seconds': elapsed, 'gpu_hours': 2*elapsed/3600, 'device_map': model.hf_device_map, 'torch': torch.__version__, 'transformers': transformers.__version__,
        'python': platform.python_version(), 'git_head': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()}
    (p/'run.json').write_text(json.dumps(run, indent=2)+'\n'); print('Complete', len(all_rows), 'rows; seconds', elapsed, flush=True)


if __name__ == '__main__': main()
