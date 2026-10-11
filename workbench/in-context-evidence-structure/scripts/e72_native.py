"""Native-interface pressure test; conditional scores and generation stay distinct."""
import argparse
import hashlib
import json
import platform
import re
import subprocess
import time
from pathlib import Path
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from e71_relational import contexts
from e58_factorization import HEAD as PLAIN_HEAD
from e67_prefix import HEAD as PREFIX_HEAD, INSTRUCTION


def records(stage, n, seed):
    ctxs = contexts(stage, n, seed)
    labels = ['yes', 'no'] if stage == 'discovery' else ['toxic', 'safe']
    kinds = ['animal', 'fruit'] if stage == 'discovery' else ['occupation', 'vehicle']
    out = []
    for c in ctxs:
        for schema in ['source_only', 'linked_prefix', 'orthogonal_prefix', 'entity_binding', 'single_source']:
            for qi, q in enumerate(c['queries'][:4]):
                ds = c['demos'] if schema != 'single_source' else [d for d in c['demos'] if d['source'] == q['source']]
                header = PREFIX_HEAD if schema.endswith('_prefix') else PLAIN_HEAD
                blocks = []
                for d in ds:
                    item = kinds[d['kind']] if schema == 'entity_binding' else d['word']
                    block = f'Item: {item}\nSource: {c["names"][d["source"]]}\n'
                    if schema.endswith('_prefix'):
                        relation = schema.removesuffix('_prefix')
                        code = c['codes'][d[relation + '_code']]
                        block += f'Tag: Mark\nLabel: {code} {labels[d["label"]]}\n\n'
                    else:
                        block += f'Label: {labels[d["label"]]}\n\n'
                    blocks.append(block)
                item = kinds[q['kind']] if schema == 'entity_binding' else q['word']
                query = f'Item: {item}\nSource: {c["names"][q["source"]]}\n'
                if schema.endswith('_prefix'):
                    query += f'Tag: Mark\nLabel: {c["codes"][q["code"]]}'
                else:
                    query += 'Label:'
                out.append({'uid': f'{c["context"]}.{schema}.{qi}', 'context': c['context'], 'schema': schema,
                            'query': qi, 'source': q['source'], 'kind': q['kind'], 'gold': q['label'],
                            'labels': labels, 'prompt': header + ''.join(blocks) + query})
    return ctxs, out


def parse_answer(text, labels, thinking):
    text = text.replace('<|im_end|>', '').replace('<|endoftext|>', '')
    if thinking and '</think>' not in text:
        return -1, 'thinking_not_closed'
    tail = text.rsplit('</think>', 1)[-1]
    candidates = '|'.join(re.escape(x) for x in labels)
    hits = re.findall(r'(?im)^\s*Answer:\s*(' + candidates + r')\s*[.!]?\s*$', tail)
    if not hits:
        return -1, 'no_final_answer_line'
    return labels.index(hits[-1].lower()), 'valid'


def main():
    ap = argparse.ArgumentParser()
    for x in ['model', 'out', 'stage']:
        ap.add_argument('--' + x, required=True)
    for x in ['n', 'seed']:
        ap.add_argument('--' + x, type=int, required=True)
    ap.add_argument('--batch-size', type=int, default=4)
    a = ap.parse_args()
    assert a.stage in ['discovery', 'confirmation']
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    ctxs, rows = records(a.stage, a.n, a.seed)
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in ctxs))
    (dest / 'prompts.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    tok.padding_side = 'left'
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                                        device_map='cuda', output_loading_info=True)
    model.eval()
    (dest / 'loading_info.json').write_text(json.dumps(loading, indent=2, default=str))
    assert not loading.get('missing_keys'), loading
    # The text-only compatibility loader can drop vision/MTP tensors deliberately.
    unexpected = loading.get('unexpected_keys', [])
    assert all(any(word in k for word in ['visual.', 'vision_', 'mtp.']) for k in unexpected), unexpected[:20]

    def chat(row, instructed, thinking):
        body = (INSTRUCTION if instructed else '') + row['prompt']
        body += '\n\nComplete the final record with its final classification code. Return the final answer on a line of the form Answer: <code>, using ' + ' or '.join(row['labels']) + '.'
        kwargs = dict(tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
        if thinking:
            kwargs['reasoning_effort'] = 'medium'
        return tok.apply_chat_template([{'role': 'user', 'content': body}], **kwargs)

    def score(batch, prompts):
        sequences = []
        for row, prompt in zip(batch, prompts):
            pids = tok.encode(prompt, add_special_tokens=False)
            for candidate in row['labels']:
                seq = tok.encode(prompt + ' ' + candidate, add_special_tokens=False)
                assert seq[:len(pids)] == pids
                sequences.append((seq, len(pids)))
        width = max(len(s) for s, _ in sequences)
        k = max(len(s) - start for s, start in sequences) + 1
        ids = torch.full((len(sequences), width), tok.pad_token_id, dtype=torch.long, device='cuda')
        mask = torch.zeros_like(ids)
        for j, (seq, _) in enumerate(sequences):
            ids[j, -len(seq):] = torch.tensor(seq, device='cuda')
            mask[j, -len(seq):] = 1
        # Explicit positions match real token positions for the plain text path.
        pos = (mask.cumsum(-1) - 1).clamp_min(0)
        out = model(input_ids=ids, attention_mask=mask, position_ids=pos, logits_to_keep=k, use_cache=False)
        lp = out.logits.float().log_softmax(-1)
        values = []
        reconstruction = 0.0
        for j, (seq, start) in enumerate(sequences):
            nt = len(seq) - start
            inds = torch.arange(k - 1 - nt, k - 1, device='cuda')
            terms = lp[j, inds, torch.tensor(seq[start:], device='cuda')]
            value = float(terms.sum())
            reconstruction = max(reconstruction, abs(value - sum(map(float, terms.cpu().tolist()))))
            values.append(value)
        return [values[j:j + 2] for j in range(0, len(values), 2)], reconstruction

    noops, token_errors = [], []
    with (dest / 'scores.jsonl').open('w') as f, torch.inference_mode():
        for interface in ['raw', 'raw_instruction', 'chat', 'chat_instruction']:
            for bi in range(0, len(rows), a.batch_size):
                batch = rows[bi:bi + a.batch_size]
                instructed = interface.endswith('_instruction')
                prompts = [(INSTRUCTION if instructed else '') + r['prompt'] if interface.startswith('raw')
                           else chat(r, instructed, False) + 'Answer:' for r in batch]
                values, error = score(batch, prompts)
                token_errors.append(error)
                if bi == 0:
                    repeated, _ = score(batch, prompts)
                    noops.extend(abs(x - y) for v, w in zip(values, repeated) for x, y in zip(v, w))
                for row, value in zip(batch, values):
                    f.write(json.dumps({'uid': row['uid'], 'context': row['context'], 'schema': row['schema'],
                                        'query': row['query'], 'gold': row['gold'], 'interface': interface,
                                        'candidate_lp': value}) + '\n')
                f.flush()
            print('scored', interface, round(time.time() - t0, 1), flush=True)
    controls = {'sanity_max_error': max(noops), 'token_sum_error_max': max(token_errors)}
    (dest / 'control_report.json').write_text(json.dumps(controls, indent=2))
    assert max(noops) <= .1 and max(token_errors) <= 1e-5, controls
    with (dest / 'generations.jsonl').open('w') as f, torch.inference_mode():
        for interface in ['chat', 'chat_instruction', 'thinking_instruction']:
            thinking = interface.startswith('thinking')
            instructed = interface != 'chat'
            max_new = 2048 if thinking else 96
            for bi in range(0, len(rows), a.batch_size):
                batch = rows[bi:bi + a.batch_size]
                prompts = [chat(r, instructed, thinking) for r in batch]
                ids = tok(prompts, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
                seqs = model.generate(**ids, do_sample=True, temperature=.6, top_p=.95, top_k=20,
                                      max_new_tokens=max_new, pad_token_id=tok.pad_token_id, use_cache=True)
                for row, seq, prompt in zip(batch, seqs, prompts):
                    generated = seq[ids['input_ids'].shape[1]:].cpu().tolist()
                    while generated and generated[-1] == tok.pad_token_id:
                        generated.pop()
                    text = tok.decode(generated, skip_special_tokens=False)
                    pred, status = parse_answer(text, row['labels'], thinking)
                    f.write(json.dumps({'uid': row['uid'], 'context': row['context'], 'schema': row['schema'],
                                        'query': row['query'], 'gold': row['gold'], 'interface': interface,
                                        'prediction': pred, 'parser_status': status, 'tokens': len(generated),
                                        'truncated': len(generated) >= max_new, 'text': text,
                                        'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}) + '\n')
                f.flush()
                if bi % (a.batch_size * 8) == 0:
                    print('generated', interface, bi, round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0, **controls,
           'torch': torch.__version__, 'transformers': transformers.__version__,
           'host': platform.node(), 'gpu': torch.cuda.get_device_name(), 'model_class': type(model).__name__,
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'chat_template_sha256': hashlib.sha256(tok.chat_template.encode()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
