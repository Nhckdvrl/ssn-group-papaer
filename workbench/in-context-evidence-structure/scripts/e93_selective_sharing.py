"""E93: orthogonal source criterion/preference, frozen before model scoring."""
import argparse, hashlib, itertools, json, math, platform, random, subprocess, time
from pathlib import Path

CELLS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
DEMO = [
    {1: ['The curry was spicy.', 'The noodles had a strong chili kick.', 'The dish was fiery.', 'The sauce had plenty of chili heat.'],
     -1: ['The curry was mild.', 'The noodles had no chili heat.', 'The dish had gentle seasoning.', 'The sauce was not spicy.']},
    {1: ['The service was quick.', 'The staff brought everything promptly.', 'The dishes arrived rapidly.', 'The team served at a fast pace.'],
     -1: ['The service was leisurely.', 'The staff took their time.', 'The dishes arrived at an unhurried pace.', 'The team served slowly.']},
]
QUERY = [
    {1: 'Our dinner had a pronounced chili burn.', -1: 'Our dinner had a mild flavor without chili heat.'},
    {1: 'We were served very quickly.', -1: 'We were served at a relaxed, leisurely pace.'},
]


def contexts(n, seed):
    rng = random.Random(seed); out = []
    for ci in range(n):
        names = ['Alice', 'Bob']; rng.shuffle(names); ds = []
        for role in (0, 1):
            cells = [CELLS[0], CELLS[3]] * 4 if role == 0 else CELLS * 2
            seen = set()
            for x in cells:
                while True:
                    parts = [rng.choice(DEMO[j][x[j]]) for j in (0, 1)]; rng.shuffle(parts)
                    text = ' '.join(parts)
                    if text not in seen: break
                seen.add(text); ds.append({'role': role, 'x': list(x), 'text': text})
        # Each source stays contiguous, but source order and within-source order vary.
        groups = [[d for d in ds if d['role'] == r] for r in (0, 1)]
        for g in groups: rng.shuffle(g)
        rng.shuffle(groups)
        qs = []
        for x in CELLS:
            parts = [QUERY[j][x[j]] for j in (0, 1)]; rng.shuffle(parts)
            qs.append({'x': list(x), 'text': ' '.join(parts)})
        out.append({'context': ci, 'names': names, 'demos': sum(groups, []), 'queries': qs})
    return out


def body(c, kind, pa, cb, pb, rel, qi, ca=None):
    na, nb = c['names']; ca = cb ^ rel if ca is None else ca
    s = ('Each reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
         'or service pace (quick or leisurely). Each reviewer has a personal preference for one of the two '
         'values of their chosen aspect. yes means the experience matches that personal preference; no means it does not. '
         'Reviewers can have different preferences even when they judge the same aspect.\n')
    if kind != 'single':
        s += f'{na} and {nb} judge {"the same aspect" if rel == 0 else "different aspects"}. Infer their rules from the examples.\n'
    if kind == 'oracle':
        aspect = 'food spiciness' if ca == 0 else 'service pace'
        pref = ('spicy' if pa == 1 else 'mild') if ca == 0 else ('quick' if pa == 1 else 'leisurely')
        s += f'{na} judges only {aspect} and prefers {pref}.\n'
    s += '\n'
    for d in c['demos']:
        if kind == 'single' and d['role'] == 1: continue
        sign = pa * d['x'][0] if d['role'] == 0 else pb * d['x'][cb]
        s += f'Reviewer: {c["names"][d["role"]]}\nReview: {d["text"]}\nLabel: {"yes" if sign == 1 else "no"}\n\n'
    if kind == 'instruction':
        s += ("Use the other reviewer's examples to infer the relevant aspect, while preserving the requested "
              "reviewer's own preference from their examples.\n\n")
    role = 1 if kind == 'probe' else 0
    s += f'Reviewer: {c["names"][role]}\nReview: {c["queries"][qi]["text"]}\nGive this reviewer\'s yes/no label for the review.\n'
    return s


def records(cs):
    out = []
    for c in cs:
        settings = []
        for kind in ('native', 'instruction'):
            settings += [(kind, pa, cb, pb, rel, cb ^ rel) for pa, cb, pb, rel in itertools.product((1, -1), (0, 1), (1, -1), (0, 1))]
        settings += [('probe', 1, cb, pb, 0, cb) for cb, pb in itertools.product((0, 1), (1, -1))]
        settings += [('oracle', pa, 0, 1, ca, ca) for pa, ca in itertools.product((1, -1), (0, 1))]
        settings += [('single', pa, 0, 1, 0, 0) for pa in (1, -1)]
        for kind, pa, cb, pb, rel, ca in settings:
            for qi, q in enumerate(c['queries']):
                disc = q['x'][0] != q['x'][1]
                gold = pb * q['x'][cb] if kind == 'probe' else pa * q['x'][ca]
                if kind == 'single' and disc: gold = 0
                out.append({'uid': f'{c["context"]}.{kind}.{pa}.{cb}.{pb}.{rel}.{qi}', 'context': c['context'],
                            'kind': kind, 'pa': pa, 'cb': cb, 'pb': pb, 'rel': rel, 'ca': ca, 'query': qi,
                            'x': q['x'], 'discordant': disc, 'gold': gold, 'body': body(c, kind, pa, cb, pb, rel, qi, ca)})
    assert len(out) == 168 * len(cs)
    return out


def design_audit(cs):
    cases = []
    for pa, cb, pb, rel, x in itertools.product((1, -1), (0, 1), (1, -1), (0, 1), CELLS):
        gold = pa * x[cb ^ rel]; b = pb * x[cb]
        correction = int(pa / pb) * ((x[0] * x[1]) ** rel) * b
        metric = sum((sum(x[j] * d[j] for j in (cb ^ rel,))) * pa * d[0] for d in (CELLS[0], CELLS[3])) / 2
        assert correction == metric == gold
        if x[0] != x[1]: assert b == (-pb) * x[1 - cb] and gold == -pa * x[(1 - cb) ^ rel]
        cases.append({'gold': gold, 'blind_b': b, 'correction': correction, 'metric': metric})
    for c in cs:
        assert not {d['text'] for d in c['demos']} & {q['text'] for q in c['queries']}
        for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            a = [d for d in c['demos'] if d['role'] == 0]; b = [d for d in c['demos'] if d['role'] == 1]
            compatible_a = [(k, p) for k, p in itertools.product((0, 1), (1, -1)) if all(p*d['x'][k] == pa*d['x'][0] for d in a)]
            compatible_b = [(k, p) for k, p in itertools.product((0, 1), (1, -1)) if all(p*d['x'][k] == pb*d['x'][cb] for d in b)]
            assert compatible_a == [(0, pa), (1, pa)] and compatible_b == [(cb, pb)]
            assert sum(pb*d['x'][cb] != pb*d['x'][1-cb] for d in b) == 4
            assert sum(pb*d['x'][cb] != -pb*d['x'][1-cb] for d in b) == 4
            assert sum(pa*d['x'][0] == 1 for d in a) == sum(pb*d['x'][cb] == 1 for d in b) == 4
    return {'n_contexts': len(cs), 'n_algebra_cases': len(cases), 'a_compatible_criterion_count': 2,
            'b_criterion_preference_unique': True, 'both_sources_functionally_needed': True,
            'criterion_and_joint_changed_b_labels': 4, 'joint_b_discordant_verdict_unchanged': True,
            'criterion_model_accuracy': 1.0, 'verdict_correction_accuracy': 1.0, 'metric_model_accuracy': 1.0,
            'blind_b_accuracy': sum(q['gold'] == q['blind_b'] for q in cases)/len(cases),
            'evidence_type': 'static identifiability/countermodel; not LLM evidence'}


def estimate(values):
    rng = random.Random(930); n = len(values); mean = sum(values)/n
    bs = sorted(sum(values[rng.randrange(n)] for _ in values)/n for _ in range(10000))
    return {'mean': mean, 'ci95': [bs[250], bs[9749]], 'n_contexts': n, 'per_context': values}


def analyze(rows):
    assert all(math.isfinite(r['z']) for r in rows)
    ids = sorted({r['context'] for r in rows}); result = {'n_rows': len(rows), 'n_contexts': len(ids), 'behavior': {}, 'functional_contrasts': {}}
    for kind in ('native', 'instruction', 'probe', 'oracle', 'single'):
        for rel in ((0, 1) if kind in ('native', 'instruction') else (None,)):
            rs = [r for r in rows if r['kind'] == kind and (rel is None or r['rel'] == rel)]
            sm = {}
            for subset in ('all', 'discordant', 'concordant'):
                ss = [r for r in rs if subset == 'all' or r['discordant'] == (subset == 'discordant')]
                for metric in ('binary_accuracy', 'argmax_accuracy', 'valid_fraction'):
                    if kind == 'single' and subset != 'concordant' and metric != 'valid_fraction': continue
                    def score(r):
                        if metric == 'valid_fraction': return r['valid']
                        return (r['pred'] if metric == 'binary_accuracy' else r['argmax_class']) == r['gold']
                    vals = [sum(score(r) for r in ss if r['context'] == ci)/sum(r['context'] == ci for r in ss) for ci in ids]
                    sm[subset+'_'+metric] = estimate(vals)
            result['behavior'][kind+('' if rel is None else '_'+('same' if rel == 0 else 'different'))] = sm
    for kind, rel in itertools.product(('native', 'instruction'), (0, 1)):
        per = {k: [] for k in ('criterion', 'joint', 'b_preference_magnitude', 'b_preference_answer_flip', 'a_preference')}
        for ci in ids:
            lut = {(r['pa'], r['cb'], r['pb'], r['query']): r for r in rows if r['kind'] == kind and r['rel'] == rel and r['context'] == ci}
            v = {k: [] for k in per}
            for (pa, cb, pb, qi), base in lut.items():
                if base['discordant']:
                    for key, other in [('criterion', lut[pa, 1-cb, pb, qi]), ('joint', lut[pa, 1-cb, -pb, qi])]:
                        v[key].append(base['gold']*(base['z']-other['z'])/2)
                other = lut[pa, cb, -pb, qi]
                v['b_preference_magnitude'].append(abs(base['z']-other['z'])/2)
                v['b_preference_answer_flip'].append(base['pred'] != other['pred'])
                v['a_preference'].append(base['gold']*(base['z']-lut[-pa, cb, pb, qi]['z'])/2)
            for k in per: per[k].append(sum(v[k])/len(v[k]))
        result['functional_contrasts'][kind+'_'+('same' if rel == 0 else 'different')] = {k: estimate(v) for k, v in per.items()}
    return result


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--model', default='/tmp/ices_models/Qwen3-8B'); ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=8); ap.add_argument('--seed', type=int, default=93001); ap.add_argument('--batch-size', type=int, default=16); ap.add_argument('--design-only', action='store_true')
    a = ap.parse_args(); p = Path(a.out); p.mkdir(parents=True, exist_ok=True)
    cs = contexts(a.n, a.seed); audit = design_audit(cs); rows = records(cs)
    (p/'design_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    if a.design_only: print(json.dumps(audit)); return
    assert not (p/'behavior.jsonl').exists()
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    (p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    import torch, transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True); tok.padding_side = 'left'
    if tok.pad_token_id is None: tok.pad_token_id = tok.eos_token_id
    labels = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]; assert all(len(x) == 1 for x in labels); lid = [x[0] for x in labels]
    system = 'Infer the requested reviewer\'s rule from the examples. Return exactly yes or no.'
    def prompt(r): return tok.apply_chat_template([{'role': 'system', 'content': system}, {'role': 'user', 'content': r['body']}], tokenize=False, add_generation_prompt=True, enable_thinking=False)+'Answer:'
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'n_records': len(rows), 'label_ids': lid, 'example': prompt(rows[0])}, indent=2)+'\n')
    t0 = time.time(); model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, torch_dtype=torch.float32, device_map='cuda', attn_implementation='eager', output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys') and not loading.get('unexpected_keys'), loading
    max_noop = 0.; scored = []
    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as f:
        for st in range(0, len(rows), a.batch_size):
            rr = rows[st:st+a.batch_size]; xx = tok([prompt(r) for r in rr], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
            pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
            lo = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float()
            if st == 0:
                again = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float(); max_noop = float((again-lo).abs().max()); assert max_noop <= .001
            zs = (lo[:, lid[1]]-lo[:, lid[0]]).tolist(); top = lo.argmax(-1).tolist()
            for r, z, t in zip(rr, zs, top):
                d = {k: v for k, v in r.items() if k != 'body'}
                d.update(z=z, pred=1 if z >= 0 else -1, argmax_token=t, argmax_class=1 if t == lid[1] else -1 if t == lid[0] else 0, valid=t in lid)
                scored.append(d); f.write(json.dumps(d)+'\n')
            f.flush(); print(min(st+a.batch_size, len(rows)), '/', len(rows), flush=True)
    elapsed = time.time()-t0; res = analyze(scored)
    run = {'args': vars(a), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'n_rows': len(scored), 'max_noop_nats': max_noop,
           'elapsed_seconds': elapsed, 'gpu_hours': elapsed/3600, 'dtype': 'float32', 'attention': 'eager', 'training': False,
           'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__, 'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (p/'analysis.json').write_text(json.dumps(res, indent=2)+'\n'); (p/'run.json').write_text(json.dumps(run, indent=2)+'\n')
    print('complete', len(scored), 'rows; seconds', elapsed, flush=True)


if __name__ == '__main__': main()
