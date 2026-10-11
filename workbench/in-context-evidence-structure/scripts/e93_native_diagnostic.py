"""E93 fixed strong-model diagnostic; all worlds, no hybrid cache intervention."""
import argparse, collections, hashlib, itertools, json, platform, re, subprocess, time
from pathlib import Path
from e93_selective_sharing import records, estimate


def parse(text):
    if '</think>' not in text: return 0, 'thinking_not_closed'
    tail = text.rsplit('</think>', 1)[1]
    tail = re.sub(r'<\|[^>]*\|>', '', tail).strip().replace('**', '').replace('__', '')
    exact = re.fullmatch(r'(?is)\s*(?:Answer:\s*)?(yes|no)[.!]?\s*', tail)
    if exact: return (1 if exact.group(1).lower() == 'yes' else -1), 'valid'
    lines = re.findall(r'(?im)^\s*Answer:\s*(yes|no)[.!]?\s*$', tail)
    if lines: return (1 if lines[-1].lower() == 'yes' else -1), 'valid_final_line'
    return 0, 'unresolved_final_answer'


def summarize(answers):
    out = {'n_rows': len(answers), 'behavior': {}, 'functional_response': {}}
    for mode in ('direct', 'thinking'):
        rr = [r for r in answers if r['mode'] == mode]; ids = sorted({r['context'] for r in rr})
        for kind in ('native', 'oracle', 'probe'):
            for rel in ((0, 1) if kind == 'native' else (None,)):
                ss = [r for r in rr if r['kind'] == kind and (rel is None or r['rel'] == rel)]; sm = {}
                for subset in ('all', 'discordant', 'concordant'):
                    bb = [r for r in ss if subset == 'all' or r['discordant'] == (subset == 'discordant')]
                    for metric in ('accuracy', 'valid_fraction'):
                        vals = []
                        for ci in ids:
                            cc = [r for r in bb if r['context'] == ci]
                            vals.append(sum((r['score']['class'] == r['gold']) if metric == 'accuracy' else r['score']['valid'] for r in cc)/len(cc))
                        sm[subset+'_'+metric] = estimate(vals)
                out['behavior'][mode+'_'+kind+('' if rel is None else '_'+('same' if rel == 0 else 'different'))] = sm
        for rel in (0, 1):
            vals = {k: [] for k in ('criterion', 'joint', 'b_preference_answer_flip', 'a_preference', 'unresolved_fraction')}
            for ci in ids:
                lut = {(r['pa'], r['cb'], r['pb'], r['query']): r for r in rr if r['kind'] == 'native' and r['rel'] == rel and r['context'] == ci}
                vv = {k: [] for k in vals}
                for (pa, cb, pb, qi), b in lut.items():
                    get = lambda r: r['score']['z'] if mode == 'direct' else r['score']['class']
                    if b['discordant']:
                        for key, other in [('criterion', lut[pa, 1-cb, pb, qi]), ('joint', lut[pa, 1-cb, -pb, qi])]:
                            vv[key].append(b['gold']*(get(b)-get(other))/2)
                    other = lut[pa, cb, -pb, qi]
                    # Unknown is preserved; invalid pairs contribute zero to the raw flip statistic.
                    vv['b_preference_answer_flip'].append(b['score']['valid'] and other['score']['valid'] and b['score']['class'] != other['score']['class'])
                    vv['a_preference'].append(b['gold']*(get(b)-get(lut[-pa, cb, pb, qi]))/2)
                    vv['unresolved_fraction'].append(not b['score']['valid'])
                for k in vals: vals[k].append(sum(vv[k])/len(vv[k]))
            out['functional_response'][mode+'_'+('same' if rel == 0 else 'different')] = {'units': 'logit nats' if mode == 'direct' else 'signed class response; unresolved=0',
                'contrasts': {k: estimate(v) for k, v in vals.items()}, 'criterion_joint_mean_algebraically_identical': True}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B'); ap.add_argument('--source', default='results/e93/qwen3_discovery/contexts.jsonl')
    ap.add_argument('--out', required=True); ap.add_argument('--n', type=int, default=4); ap.add_argument('--thinking-n', type=int, default=2)
    ap.add_argument('--batch-size', type=int, default=8); ap.add_argument('--tokens', type=int, default=1024); ap.add_argument('--continuation-tokens', type=int, default=2048); a = ap.parse_args()
    p = Path(a.out); p.mkdir(parents=True, exist_ok=True); assert not (p/'behavior.jsonl').exists()
    cs = [json.loads(s) for s in Path(a.source).read_text().splitlines()][:a.n]
    rows = [r for r in records(cs) if r['kind'] in ('native', 'oracle', 'probe')]; assert len(rows) == 96*a.n
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs)); (p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    import torch, transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True); tok.padding_side = 'left'
    if tok.pad_token_id is None: tok.pad_token_id = tok.eos_token_id
    lid = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]; assert all(len(x) == 1 for x in lid); lid = [x[0] for x in lid]
    system = "Infer the requested reviewer's rule from the examples. Return exactly yes or no."
    def prompt(r, thinking):
        return tok.apply_chat_template([{'role': 'system', 'content': system}, {'role': 'user', 'content': r['body']}], tokenize=False,
                add_generation_prompt=True, enable_thinking=thinking, reasoning_effort='medium')+('' if thinking else 'Answer:')
    (p/'preflight.json').write_text(json.dumps({'args': vars(a), 'label_ids': lid, 'n_direct': len(rows), 'n_thinking': 96*a.thinking_n,
        'example': prompt(rows[0], True), 'no_hybrid_source_masks': True}, indent=2)+'\n')
    t0 = time.time(); print('Loading model', flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16, device_map='cuda', attn_implementation='sdpa', output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'), loading
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.')) for x in loading.get('unexpected_keys', [])), loading
    (p/'loading_info.json').write_text(json.dumps(loading, indent=2, default=str)+'\n'); print('Loaded', flush=True)
    all_answers = []; max_noop = 0.; continued = 0
    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as f:
        for mode in ('direct', 'thinking'):
            rs = rows if mode == 'direct' else [r for r in rows if r['context'] in {c['context'] for c in cs[:a.thinking_n]}]
            for st in range(0, len(rs), a.batch_size):
                rr = rs[st:st+a.batch_size]; xx = tok([prompt(r, mode == 'thinking') for r in rr], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda'); width = xx.input_ids.shape[1]
                if mode == 'direct':
                    pos = (xx.attention_mask.cumsum(-1)-1).clamp_min(0)
                    lo = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float()
                    if st == 0:
                        again = model(**xx, position_ids=pos, logits_to_keep=1, use_cache=False).logits[:, -1].float(); max_noop = float((again-lo).abs().max()); assert max_noop < 1e-4
                    zs = (lo[:, lid[1]]-lo[:, lid[0]]).tolist(); tops = lo.argmax(-1).tolist()
                    scores = [{'class': 1 if t == lid[1] else -1 if t == lid[0] else 0, 'valid': t in lid, 'z': z, 'argmax_token': t} for z, t in zip(zs, tops)]
                else:
                    gen = model.generate(**xx, max_new_tokens=a.tokens, do_sample=False, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                    scores = []
                    for j, raw in enumerate(gen[:, width:].tolist()):
                        old = raw[:]; censored = tok.eos_token_id not in raw
                        if censored:
                            full = xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw; fi = torch.tensor([full], device='cuda')
                            more = model.generate(input_ids=fi, attention_mask=torch.ones_like(fi), max_new_tokens=a.continuation_tokens, do_sample=False,
                                pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)[0, len(full):].tolist()
                            raw += more; assert raw[:len(old)] == old; continued += 1
                        if tok.eos_token_id in raw: raw = raw[:raw.index(tok.eos_token_id)+1]
                        text = tok.decode(raw, skip_special_tokens=False); cl, status = parse(text)
                        scores.append({'class': cl, 'valid': cl != 0, 'parse_status': status, 'text': text, 'token_ids': raw,
                            'initial_censored': censored, 'still_censored': tok.eos_token_id not in raw})
                for r, score in zip(rr, scores):
                    d = {k: v for k, v in r.items() if k != 'body'}; d.update(mode=mode, score=score); all_answers.append(d); f.write(json.dumps(d)+'\n')
                f.flush(); print(mode, min(st+a.batch_size, len(rs)), '/', len(rs), 'continued', continued, flush=True)
    elapsed = time.time()-t0
    (p/'analysis.json').write_text(json.dumps(summarize(all_answers), indent=2)+'\n')
    run = {'args': vars(a), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_contexts_sha256': hashlib.sha256(Path(a.source).read_bytes()).hexdigest(), 'n_rows': len(all_answers), 'actual_model_type': model.config.model_type,
        'dtype': 'bfloat16', 'attention': 'sdpa', 'training': False, 'interventions': False, 'direct_noop_max': max_noop,
        'continued_all_initially_censored': continued, 'elapsed_seconds': elapsed, 'gpu_hours': elapsed/3600,
        'python': platform.python_version(), 'torch': torch.__version__, 'transformers': transformers.__version__, 'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (p/'run.json').write_text(json.dumps(run, indent=2)+'\n'); print('complete', len(all_answers), 'rows', elapsed, flush=True)


if __name__ == '__main__': main()
