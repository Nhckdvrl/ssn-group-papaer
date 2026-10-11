"""E102: freeze E94's functional interface and separate address from rule content.

Donors end before the future input. Only the layer-16 Reviewer field is
replaced; all receiver demonstrations, caches and future tokens stay receiver's.
"""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import subprocess
import time
from pathlib import Path

from e93_selective_sharing import body, contexts, design_audit
from e94_coordinate_transfer import SYSTEM

LAYER_1BASED = 16


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def estimate(values):
    rng = random.Random(102001)
    bs = sorted(sum(values[rng.randrange(len(values))] for _ in values) / len(values)
                for _ in range(10000))
    return {'mean': sum(values)/len(values), 'ci95': [bs[250], bs[9749]],
            'n_contexts': len(values), 'per_context': values}


def analyze(rows):
    ids = sorted({r['context'] for r in rows})
    assert len(rows) == 112 * len(ids)
    out = {'n_rows': len(rows), 'n_contexts': len(ids), 'native': {}, 'interchange': {}}
    for role in (0, 1):
        rr = [r for r in rows if r['kind'] == 'native' and r['role'] == role]
        out['native']['A' if role == 0 else 'B'] = {
            'n': len(rr), 'argmax_accuracy': estimate([
                sum(r['argmax_class'] == r['gold'] for r in rr if r['context'] == ci)
                /sum(r['context'] == ci for r in rr) for ci in ids])}
    for dc, dp in itertools.product((0, 1), (0, 1)):
        rr = [r for r in rows if r['kind'] == 'interchange'
              and r['criterion_flip'] == dc and r['preference_flip'] == dp]
        key = f'criterion_flip{dc}_preference_flip{dp}'
        item = {'n': len(rr), 'invalid': sum(not r['valid'] for r in rr),
                'profile_predictions_all_distinct': dc == 1 and dp == 0,
                'models': {}, 'complete_profiles': {}}
        for model in ('recipient_A', 'recipient_B', 'donor_criterion', 'donor_function',
                      'actual_recipient_A', 'actual_recipient_B', 'actual_donor_B'):
            matches = [r['argmax_class'] == r['predictions'][model] for r in rr]
            item['models'][model] = {
                'matches': sum(matches), 'denominator': len(rr),
                'rate': estimate([sum(r['argmax_class'] == r['predictions'][model]
                                     for r in rr if r['context'] == ci)
                                  /sum(r['context'] == ci for r in rr) for ci in ids])}
            groups = {}
            for r in rr:
                groups.setdefault((r['context'], r['pa'], r['cr']), []).append(r)
            assert all(len(g) == 4 and {r['query'] for r in g} == set(range(4))
                       for g in groups.values())
            item['complete_profiles'][model] = {
                'all_four_match': sum(all(r['argmax_class'] == r['predictions'][model]
                                         for r in g) for g in groups.values()),
                'denominator': len(groups)}
        out['interchange'][key] = item
    patched = {(r['context'], r['pa'], r['cr'], r['query'],
                r['criterion_flip'], r['preference_flip']): r
               for r in rows if r['kind'] == 'interchange'}
    out['donor_rule_dependence'] = {}
    for factor, other in [('criterion', 'preference'), ('preference', 'criterion')]:
        metrics = {k: [] for k in ('answer_flip', 'absolute_margin_change',
                                   'donor_directed_margin_change')}
        for ci in ids:
            vv = {k: [] for k in metrics}
            for pa, cr, qi, fixed in itertools.product((1, -1), (0, 1), range(4), (0, 1)):
                a = (0, fixed) if factor == 'criterion' else (fixed, 0)
                b = (1, fixed) if factor == 'criterion' else (fixed, 1)
                r0 = patched[ci, pa, cr, qi, *a]
                r1 = patched[ci, pa, cr, qi, *b]
                vv['answer_flip'].append(r0['argmax_class'] != r1['argmax_class'])
                vv['absolute_margin_change'].append(abs(r1['z']-r0['z'])/2)
                if r0['predictions']['donor_function'] != r1['predictions']['donor_function']:
                    vv['donor_directed_margin_change'].append(
                        r1['predictions']['donor_function']*(r1['z']-r0['z'])/2)
            for k in metrics:
                metrics[k].append(sum(vv[k])/len(vv[k]))
        out['donor_rule_dependence'][factor] = {k: estimate(v) for k, v in metrics.items()}
    # Exact old-world replay is a reproducibility check, not discovery fitting.
    old_path = Path('results/e94/qwen35_discovery/behavior.jsonl')
    if old_path.exists():
        old = [json.loads(s) for s in old_path.read_text().splitlines()]
        lut = {(r['context'], r['pa'], r['cb'], r['query']): r
               for r in old if r['condition'] == 'address_16'}
        current = [r for r in rows if r['kind'] == 'interchange'
                   and r['criterion_flip'] == r['preference_flip'] == 0]
        diffs = [abs(r['z']-lut[r['context'], r['pa'], r['cr'], r['query']]['z'])
                 for r in current]
        out['e94_replay'] = {'n': len(diffs), 'max_margin_diff_nats': max(diffs),
                            'mean_margin_diff_nats': sum(diffs)/len(diffs),
                            'same_argmax': sum(r['argmax_class'] ==
                                lut[r['context'], r['pa'], r['cr'], r['query']]['argmax_class']
                                for r in current)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=4)
    ap.add_argument('--seed', type=int, default=94001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args()
    p = Path(a.out); p.mkdir(parents=True, exist_ok=True)
    assert not (p/'behavior.jsonl').exists()
    cs = contexts(a.n, a.seed)
    audit = design_audit(cs)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    tok.padding_side = 'left'
    if tok.pad_token_id is None: tok.pad_token_id = tok.eos_token_id
    lid = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]
    assert all(len(v) == 1 for v in lid)
    lid = [v[0] for v in lid]

    def record(c, pa, cr, pb, role, qi):
        user = body(c, 'probe' if role else 'native', pa, cr, pb, 0, qi)
        prompt = tok.apply_chat_template([
            {'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)+'Answer:'
        goal = f'Reviewer: {c["names"][role]}'
        st = prompt.rfind(goal+'\nReview:'); assert st >= 0
        end = st+len(goal); prefix = prompt[:end]
        enc = tok(prefix, return_offsets_mapping=True, add_special_tokens=False)
        gs = next(i for i, (_, e) in enumerate(enc.offset_mapping) if e > st)
        assert tok.encode(prompt, add_special_tokens=False)[:len(enc.input_ids)] == enc.input_ids
        x = c['queries'][qi]['x']
        return {'context': c['context'], 'pa': pa, 'cr': cr, 'pb': pb,
                'role': role, 'query': qi, 'x': x, 'gold': (pb if role else pa)*x[cr],
                'prompt': prompt, 'prefix': prefix, 'prefix_ids': enc.input_ids,
                'goal_start': gs, 'goal_length': len(enc.input_ids)-gs}

    donors = []
    natives = []
    preflight = []
    for c in cs:
        ds = {(pa, cd, pd): record(c, pa, cd, pd, 1, 0)
              for pa, cd, pd in itertools.product((1, -1), (0, 1), (1, -1))}
        nr = [record(c, pa, cr, -pa, 0, qi)
              for pa, cr, qi in itertools.product((1, -1), (0, 1), range(4))]
        nr += [record(c, pa, cr, pb, 1, qi)
               for pa, cr, pb, qi in itertools.product((1, -1), (0, 1), (1, -1), range(4))]
        assert len(nr) == 48
        assert {r['goal_length'] for r in [*ds.values(), *nr]} == {3}
        assert len({len(r['prefix_ids']) for r in [*ds.values(), *nr]}) == 1
        # No donor may see a query, and four profiles must be different on quartets.
        distinct = []
        for pa, cr in itertools.product((1, -1), (0, 1)):
            cd = 1-cr; pd = -pa
            patterns = [(tuple(sign*q['x'][cc] for q in c['queries']))
                        for sign, cc in [(pa, cr), (-pa, cr), (pa, cd), (pd, cd)]]
            assert len(set(patterns)) == 4
            distinct.append({'pa': pa, 'cr': cr, 'patterns': patterns})
        for r in ds.values():
            assert all(q['text'] not in r['prefix'] for q in c['queries'])
        for pa, cr, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            base = ds[pa, cr, pb]['prefix_ids']
            cf = ds[pa, 1-cr, pb]['prefix_ids']
            cp = ds[pa, cr, -pb]['prefix_ids']
            assert sum(i != j for i, j in zip(base, cf)) == 4
            assert sum(i != j for i, j in zip(base, cp)) == 8
        donors.append(ds); natives.append(nr)
        preflight.append({'context': c['context'], 'donors': 8, 'natives': 48,
                          'interchanges': 64, 'prefix_tokens': len(nr[0]['prefix_ids']),
                          'goal_tokens': 3, 'query_excluded': True,
                          'four_distinct_profiles': distinct})
    audit.update(expected_rows=112*a.n, expected_primary_rows=16*a.n,
                 layer_1based=LAYER_1BASED,
                 only_donor_B_labels_change=True, fitted_alignment=False)
    (p/'design_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'cases': preflight,
        'label_ids': lid, 'dtype': 'float32', 'attention': 'eager',
        'donor_prefix_example': next(iter(donors[0].values()))['prefix']}, indent=2)+'\n')
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    if a.preflight_only:
        print('preflight passed', audit['expected_rows'], 'rows', flush=True); return

    import torch, transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0)
    t0 = time.time(); print('Loading frozen float32/eager, two local GPUs', flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(
        a.model, local_files_only=True, dtype=torch.float32, device_map='auto',
        max_memory={0: '64GiB', 1: '64GiB'}, attn_implementation='eager',
        output_loading_info=True)
    model.eval(); model.requires_grad_(False)
    assert not loading.get('missing_keys'), loading
    assert set(model.hf_device_map.values()) <= {0, 1, 'cuda:0', 'cuda:1'}
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.'))
               for x in loading.get('unexpected_keys', [])), loading
    assert len(model.model.layers) == 64
    (p/'loading_info.json').write_text(json.dumps(loading, default=str, indent=2)+'\n')
    print('Loaded', model.hf_device_map, flush=True)
    errs = {'self_copy_max_nats': 0., 'non_field_max': 0., 'prefix_vs_full_field_max': 0.}
    rows = []; captured = {}

    def forward(rr, prefix=False, vectors=None, collect=False):
        xx = tok([r['prefix'] if prefix else r['prompt'] for r in rr],
                 return_tensors='pt', padding=True, add_special_tokens=False).to('cuda:0')
        pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
        starts = [xx.input_ids.shape[1]-int(xx.attention_mask[i].sum())+r['goal_start']
                  for i, r in enumerate(rr)]
        cap = []
        def hook(module, inp, out):
            assert isinstance(out, torch.Tensor)
            if collect:
                cap.extend(out[i, st:st+3].detach().cpu() for i, st in enumerate(starts))
            if vectors is None: return out
            h = out.clone()
            for i, st in enumerate(starts): h[i, st:st+3] = vectors[i].to(h)
            mask = torch.ones(out.shape[:2], dtype=torch.bool, device=out.device)
            for i, st in enumerate(starts): mask[i, st:st+3] = False
            err = float((h[mask]-out[mask]).abs().max())
            errs['non_field_max'] = max(errs['non_field_max'], err)
            assert err == 0
            return h
        handle = model.model.layers[LAYER_1BASED-1].register_forward_hook(hook)
        try:
            lo = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float().cpu()
        finally: handle.remove()
        return lo, cap

    def metrics(r, lo):
        top = int(lo.argmax()); z = float(lo[lid[1]]-lo[lid[0]])
        assert math.isfinite(z)
        d = {k: v for k, v in r.items() if k not in
             ('prompt', 'prefix', 'prefix_ids', 'goal_start', 'goal_length')}
        d.update(z=z, argmax_token=top,
                 argmax_class=1 if top == lid[1] else -1 if top == lid[0] else 0,
                 pred=1 if z >= 0 else -1, valid=top in lid)
        return d

    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as stream:
        def save(d):
            rows.append(d); stream.write(json.dumps(d)+'\n'); stream.flush()
        for ci, c in enumerate(cs):
            ds = donors[ci]; nr = natives[ci]; lut = {}
            for st in range(0, len(nr), 4):
                rb = nr[st:st+4]; lo, _ = forward(rb)
                for r, v in zip(rb, lo):
                    d = metrics(r, v); d['kind'] = 'native'; save(d)
                    lut[r['pa'], r['cr'], r['pb'], r['role'], r['query']] = d
            dr = list(ds.values()); dvec = {}
            for st in range(0, len(dr), 4):
                rb = dr[st:st+4]; _, cap = forward(rb, prefix=True, collect=True)
                for r, v in zip(rb, cap): dvec[r['pa'], r['cr'], r['pb']] = v
            # Self-copy uses the exact same forward path; separately check causality.
            rb = nr[:4]; ref, cap = forward(rb, collect=True)
            noop, _ = forward(rb, vectors=cap)
            err = float((ref-noop).abs().max()); errs['self_copy_max_nats'] = max(errs['self_copy_max_nats'], err)
            assert err <= .001
            _, pc = forward(rb, prefix=True, collect=True)
            errs['prefix_vs_full_field_max'] = max(errs['prefix_vs_full_field_max'],
                max(float((v-w).abs().max()) for v, w in zip(pc, cap)))
            assert errs['prefix_vs_full_field_max'] <= .001
            for pa, cr in itertools.product((1, -1), (0, 1)):
                rb = [r for r in nr if r['role'] == 0 and r['pa'] == pa and r['cr'] == cr]
                assert len(rb) == 4 and [r['query'] for r in rb] == list(range(4))
                for dc, dp in itertools.product((0, 1), (0, 1)):
                    cd = cr ^ dc; pd = pa if dp else -pa
                    lo, _ = forward(rb, vectors=[dvec[pa, cd, pd]]*4)
                    for r, v in zip(rb, lo):
                        d = metrics(r, v); qi = r['query']; x = r['x']
                        d.update(kind='interchange', cd=cd, pd=pd,
                                 criterion_flip=dc, preference_flip=dp,
                                 donor_prefix_sha256=hashlib.sha256(ds[pa, cd, pd]['prefix'].encode()).hexdigest(),
                                 predictions={'recipient_A': pa*x[cr], 'recipient_B': -pa*x[cr],
                                    'donor_criterion': pa*x[cd], 'donor_function': pd*x[cd],
                                    'actual_recipient_A': lut[pa, cr, -pa, 0, qi]['argmax_class'],
                                    'actual_recipient_B': lut[pa, cr, -pa, 1, qi]['argmax_class'],
                                    'actual_donor_B': lut[pa, cd, pd, 1, qi]['argmax_class']})
                        save(d)
            print('context', ci+1, '/', a.n, 'rows', len(rows), flush=True)
    assert len(rows) == 112*a.n
    (p/'analysis.json').write_text(json.dumps(analyze(rows), indent=2)+'\n')
    elapsed = time.time()-t0
    run = {'args': vars(a), 'n_rows': len(rows), 'errors': errs,
           'script_sha256': digest(__file__),
           'dependencies': {fn: digest('scripts/'+fn) for fn in
                            ('e93_selective_sharing.py', 'e94_coordinate_transfer.py')},
           'design_sha256': digest(p/'design_audit.json'),
           'model_config_sha256': digest(Path(a.model)/'config.json'),
           'layer_1based': LAYER_1BASED, 'training': False,
           'elapsed_seconds': elapsed, 'gpu_hours': 2*elapsed/3600,
           'dtype': 'float32', 'attention': 'eager', 'device_map': model.hf_device_map,
           'torch': torch.__version__, 'transformers': transformers.__version__,
           'python': platform.python_version(),
           'git_head': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()}
    (p/'run.json').write_text(json.dumps(run, indent=2)+'\n')
    print('Complete', len(rows), 'rows', elapsed, 'seconds', flush=True)


if __name__ == '__main__':
    main()
