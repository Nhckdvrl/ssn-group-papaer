"""E95: two valid worlds differ only in ownership of fixed input-label rows."""
import argparse, collections, hashlib, itertools, json, math, platform, random, re, subprocess, time
from pathlib import Path
from e93_selective_sharing import CELLS, DEMO, QUERY


def contexts(n, seed):
    rng = random.Random(seed); cs = []
    for ci in range(n):
        names = ['Alice', 'Bob', 'Carol']; rng.shuffle(names)
        a = []; foreign = []; seen = set()
        def text(x):
            while True:
                parts = [rng.choice(DEMO[j][x[j]]) for j in (0, 1)]; rng.shuffle(parts)
                s = ' '.join(parts)
                if s not in seen: seen.add(s); return s
        for x in [CELLS[0], CELLS[3]] * 4:
            a.append({'a': True, 'x': list(x), 'text': text(x)})
        for x in CELLS:
            for rep in range(2):
                s = text(x)
                for y in (1, -1): foreign.append({'a': False, 'x': list(x), 'text': s, 'y': y})
        rng.shuffle(a); rng.shuffle(foreign)
        groups = [a, foreign]; rng.shuffle(groups)
        qs = []
        for x in CELLS:
            parts = [QUERY[j][x[j]] for j in (0, 1)]; rng.shuffle(parts)
            qs.append({'x': list(x), 'text': ' '.join(parts)})
        cs.append({'context': ci, 'names': names, 'demos': sum(groups, []), 'queries': qs})
    return cs


def world(c, pa, cb, pb):
    ds = []
    for d in c['demos']:
        y = pa*d['x'][0] if d['a'] else d['y']
        role = 0 if d['a'] else (1 if y == pb*d['x'][cb] else 2)
        ds.append(dict(d, y=y, role=role))
    return ds


def body(c, kind, pa, cb, pb, qi):
    s = ('Each reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
         'or service pace (quick or leisurely). All three reviewers judge the same aspect. '
         'Each reviewer has a personal preference for one of the two values of that aspect. '
         'Reviewers may have different preferences. yes means the experience matches that reviewer\'s '
         'personal preference; no means it does not. Infer their rules from the examples.\n\n')
    for d in world(c, pa, cb, pb):
        s += f'Reviewer: {c["names"][d["role"]]}\nReview: {d["text"]}\nLabel: {"yes" if d["y"] == 1 else "no"}\n\n'
    if kind == 'criterion':
        return s+'Which single aspect do all three reviewers judge? Answer food for food spiciness, or service for service pace.\n'
    if kind == 'instruction':
        s += (f'Use {c["names"][1]} and {c["names"][2]}\'s examples to infer the shared aspect, '
              f'while preserving {c["names"][0]}\'s own preference from their examples.\n\n')
    if kind == 'oracle':
        aspect = 'food spiciness' if cb == 0 else 'service pace'
        pref = ('spicy' if pa == 1 else 'mild') if cb == 0 else ('quick' if pa == 1 else 'leisurely')
        s += f'{c["names"][0]} judges only {aspect} and prefers {pref}.\n\n'
    role = 1 if kind == 'probe' else 0
    return s+f'Reviewer: {c["names"][role]}\nReview: {c["queries"][qi]["text"]}\nGive this reviewer\'s yes/no label for the review.\n'


def records(cs):
    rs = []
    for c in cs:
        for pa, cb, pb in itertools.product((1, -1), (0, 1), (1, -1)):
            for kind in ('native', 'instruction', 'oracle', 'probe', 'criterion'):
                for qi in ([None] if kind == 'criterion' else range(4)):
                    x = None if qi is None else c['queries'][qi]['x']
                    gold = (1 if cb == 1 else -1) if kind == 'criterion' else (pb if kind == 'probe' else pa)*x[cb]
                    rs.append({'context': c['context'], 'pa': pa, 'cb': cb, 'pb': pb, 'kind': kind, 'query': qi,
                               'discordant': None if x is None else x[0] != x[1], 'gold': gold,
                               'body': body(c, kind, pa, cb, pb, qi)})
    return rs


def audit(cs):
    pair_count = 0; solutions = []; cases = []
    for c in cs:
        assert len(c['demos']) == 24
        assert not {q['text'] for q in c['queries']} & {d['text'] for d in c['demos']}
        for pa, pb in itertools.product((1, -1), repeat=2):
            ws = [world(c, pa, cb, pb) for cb in (0, 1)]
            assert [[(d['text'], d['y']) for d in w] for w in ws][0] == [(d['text'], d['y']) for d in ws[1]]
            margins = lambda w: (collections.Counter((d['role'], tuple(d['x'])) for d in w),
                                 collections.Counter((d['role'], d['y']) for d in w))
            assert margins(ws[0]) == margins(ws[1])
            assert sum(a['role'] != b['role'] for a, b in zip(*ws)) == 8
            for cb, w in enumerate(ws):
                fits = [(cc, ps) for cc in (0, 1) for ps in itertools.product((1, -1), repeat=3)
                        if all(ps[d['role']]*d['x'][cc] == d['y'] for d in w)]
                assert fits == [(cb, (pa, pb, -pb))]; solutions.append(len(fits))
                afits = [(cc, pp) for cc in (0, 1) for pp in (1, -1)
                         if all(pp*d['x'][cc] == d['y'] for d in w if d['role'] == 0)]
                assert afits == [(0, pa), (1, pa)]
                # Three non-equivalent computations have identical correct behavior.
                wb = [sum(d['y']*d['x'][j] for d in w if d['role'] == 1)/8 for j in (0, 1)]
                wc = [sum(d['y']*d['x'][j] for d in w if d['role'] == 2)/8 for j in (0, 1)]
                assert wb == [pb if j == cb else 0 for j in (0, 1)] and wc == [-v for v in wb]
                metric_cb = max((0, 1), key=lambda j: wb[j]**2+wc[j]**2)
                for q in c['queries']:
                    gold = pa*q['x'][cb]
                    corrected = pa*pb*(pb*q['x'][cb])
                    metric = pa*q['x'][metric_cb]
                    assert gold == corrected == metric
                    cases.append({'cb': cb, 'pa': pa, 'pb': pb, 'x': q['x'], 'gold': gold,
                                  'program': gold, 'corrected_lookup': corrected, 'unoriented_metric': metric})
            pair_count += 1
    return {'n_contexts': len(cs), 'n_direct': 136*len(cs), 'world_pairs': pair_count,
            'same_pooled_input_label_sequence': True, 'same_source_input_and_source_label_marginals': True,
            'only_changed_rows_per_cb_flip': 8, 'unique_full_world_solutions': sorted(set(solutions)),
            'a_alone_criterion_solutions': 2, 'anonymous_pooling_balanced_world_accuracy_bound': .5,
            'anonymous_pooling_paired_both_correct_bound': 0., 'countermodels': cases,
            'evidence_type': 'static design enumeration; not model or neural mechanism evidence'}


def estimate(v):
    rng = random.Random(950); n = len(v)
    bs = sorted(sum(v[rng.randrange(n)] for _ in v)/n for _ in range(10000))
    return {'mean': sum(v)/n, 'ci95': [bs[250], bs[9749]], 'n_contexts': n, 'per_context': v}


def analyze(rows):
    result = {'n_rows': len(rows), 'behavior': {}, 'paired_worlds': {}}
    for mode in sorted({r['mode'] for r in rows}):
        for kind in ('native', 'instruction', 'oracle', 'probe', 'criterion'):
            rr = [r for r in rows if r['mode'] == mode and r['kind'] == kind]
            if not rr: continue
            ids = sorted({r['context'] for r in rr}); out = {}
            for subset in (('all',) if kind == 'criterion' else ('all', 'discordant', 'concordant')):
                ss = [r for r in rr if subset == 'all' or r['discordant'] == (subset == 'discordant')]
                for metric in ('accuracy', 'valid', 'binary_accuracy'):
                    def val(r):
                        if metric == 'valid': return r['score']['valid']
                        k = 'binary_class' if metric == 'binary_accuracy' and mode == 'direct' else 'class'
                        return r['score'][k] == r['gold']
                    out[subset+'_'+metric] = estimate([sum(val(r) for r in ss if r['context'] == ci)/sum(r['context'] == ci for r in ss) for ci in ids])
            result['behavior'][mode+'_'+kind] = out
            if kind not in ('native', 'instruction', 'criterion'): continue
            per = {k: [] for k in ('both_worlds_correct', 'pB_flip_rate', 'criterion_response')}
            for ci in ids:
                lut = {(r['pa'], r['cb'], r['pb'], r['query']): r for r in rr if r['context'] == ci}
                vals = {k: [] for k in per}
                for (pa, cb, pb, qi), b in lut.items():
                    other = lut[pa, 1-cb, pb, qi]; private = lut[pa, cb, -pb, qi]
                    if kind == 'criterion' or b['discordant']:
                        vals['both_worlds_correct'].append(b['score']['class'] == b['gold'] and other['score']['class'] == other['gold'])
                        get = lambda r: r['score']['z'] if mode == 'direct' else r['score']['class']
                        vals['criterion_response'].append(b['gold']*(get(b)-get(other))/2)
                    vals['pB_flip_rate'].append(b['score']['valid'] and private['score']['valid'] and b['score']['class'] != private['score']['class'])
                for k in per: per[k].append(sum(vals[k])/len(vals[k]))
            result['paired_worlds'][mode+'_'+kind] = {k: estimate(v) for k, v in per.items()}
    return result


def parse(text, labels):
    if '</think>' not in text: return 0, 'thinking_not_closed'
    tail = re.sub(r'<\|[^>]*\|>', '', text.rsplit('</think>', 1)[1]).strip().replace('**', '').replace('__', '')
    names = '|'.join(labels)
    m = re.fullmatch(r'(?is)\s*(?:Answer:\s*)?('+names+r')[.!]?\s*', tail)
    if m: return (-1 if m.group(1).lower() == labels[0] else 1), 'valid'
    ms = re.findall(r'(?im)^\s*Answer:\s*('+names+r')[.!]?\s*$', tail)
    if ms: return (-1 if ms[-1].lower() == labels[0] else 1), 'valid_final_line'
    return 0, 'unresolved_final_answer'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--n', type=int, default=4); ap.add_argument('--seed', type=int, default=95001); ap.add_argument('--batch-size', type=int, default=8)
    ap.add_argument('--thinking-n', type=int, default=2); ap.add_argument('--design-only', action='store_true'); a = ap.parse_args()
    p = Path(a.out); p.mkdir(parents=True, exist_ok=True); cs = contexts(a.n, a.seed); rs = records(cs); design = audit(cs)
    (p/'design_audit.json').write_text(json.dumps(design, indent=2)+'\n')
    (p/'example.json').write_text(json.dumps({'names': cs[0]['names'], 'world0': body(cs[0], 'criterion', 1, 0, 1, None),
        'world1': body(cs[0], 'criterion', 1, 1, 1, None)}, indent=2)+'\n')
    if a.design_only: print(json.dumps({k: v for k, v in design.items() if k != 'countermodels'})); return
    assert not (p/'behavior.jsonl').exists()
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs)); (p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rs))
    import torch, transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True); tok.padding_side = 'left'
    if tok.pad_token_id is None: tok.pad_token_id = tok.eos_token_id
    candidates = {'criterion': ('food', 'service'), 'judgment': ('no', 'yes')}; lids = {}
    for k, labels in candidates.items():
        enc = [tok.encode(' '+s, add_special_tokens=False) for s in labels]; assert all(len(x) == 1 for x in enc), enc
        lids[k] = [x[0] for x in enc]
    def prompt(r, thinking):
        return tok.apply_chat_template([{'role': 'system', 'content': 'Infer rules from the examples. Return only the requested one-word answer.'},
            {'role': 'user', 'content': r['body']}], tokenize=False, add_generation_prompt=True, enable_thinking=thinking,
            reasoning_effort='medium')+('' if thinking else 'Answer:')
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'label_ids': lids, 'n_direct': len(rs),
        'n_thinking': 72*a.thinking_n, 'example': prompt(rs[0], False), 'no_hybrid_cache_interventions': True}, indent=2)+'\n')
    t0 = time.time(); print('Loading', flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16, device_map='cuda',
        attn_implementation='sdpa', output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'), loading
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    (p/'loading_info.json').write_text(json.dumps(loading, indent=2, default=str)+'\n'); print('Loaded', flush=True)
    out = []; noop = 0.; continued = 0
    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as f:
        for mode in ('direct', 'thinking'):
            rows = rs if mode == 'direct' else [r for r in rs if r['context'] < a.thinking_n and r['kind'] in ('native', 'criterion', 'probe')]
            for st in range(0, len(rows), a.batch_size):
                rr = rows[st:st+a.batch_size]; xx = tok([prompt(r, mode == 'thinking') for r in rr], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda'); width = xx.input_ids.shape[1]
                if mode == 'direct':
                    pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
                    lo = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float()
                    if st == 0:
                        again = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float(); noop = float((again-lo).abs().max()); assert noop <= .001
                    scores = []
                    for j, r in enumerate(rr):
                        li = lids['criterion' if r['kind'] == 'criterion' else 'judgment']; z = float(lo[j, li[1]]-lo[j, li[0]]); top = int(lo[j].argmax())
                        scores.append({'class': 1 if top == li[1] else -1 if top == li[0] else 0, 'binary_class': 1 if z >= 0 else -1,
                                       'valid': top in li, 'z': z, 'argmax_token': top})
                else:
                    gen = model.generate(**xx, max_new_tokens=1024, do_sample=False, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                    scores = []
                    for j, raw in enumerate(gen[:, width:].tolist()):
                        censored = tok.eos_token_id not in raw; old = raw[:]
                        if censored:
                            full = xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw; fi = torch.tensor([full], device='cuda')
                            more = model.generate(input_ids=fi, attention_mask=torch.ones_like(fi), max_new_tokens=2048, do_sample=False,
                                pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)[0, len(full):].tolist()
                            raw += more; assert raw[:len(old)] == old; continued += 1
                        if tok.eos_token_id in raw: raw = raw[:raw.index(tok.eos_token_id)+1]
                        s = tok.decode(raw, skip_special_tokens=False); labels = candidates['criterion' if rr[j]['kind'] == 'criterion' else 'judgment']; cl, status = parse(s, labels)
                        scores.append({'class': cl, 'valid': cl != 0, 'parse_status': status, 'text': s, 'token_ids': raw,
                                       'initial_censored': censored, 'still_censored': tok.eos_token_id not in raw})
                for r, score in zip(rr, scores):
                    d = {k: v for k, v in r.items() if k != 'body'}; d.update(mode=mode, score=score); out.append(d); f.write(json.dumps(d)+'\n')
                f.flush(); print(mode, min(st+a.batch_size, len(rows)), '/', len(rows), 'continued', continued, flush=True)
            (p/('analysis_'+mode+'.json')).write_text(json.dumps(analyze(out), indent=2)+'\n')
    elapsed = time.time()-t0
    (p/'analysis.json').write_text(json.dumps(analyze(out), indent=2)+'\n')
    (p/'run.json').write_text(json.dumps({'args': vars(a), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'n_rows': len(out), 'actual_model_type': model.config.model_type, 'dtype': 'bfloat16', 'attention': 'sdpa', 'training': False,
        'noop_max': noop, 'continued': continued, 'elapsed_seconds': elapsed, 'gpu_hours': elapsed/3600, 'python': platform.python_version(),
        'torch': torch.__version__, 'transformers': transformers.__version__, 'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}, indent=2)+'\n')
    print('complete', len(out), elapsed, flush=True)


if __name__ == '__main__': main()
