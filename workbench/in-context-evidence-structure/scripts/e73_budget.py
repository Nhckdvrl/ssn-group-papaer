"""A paired censoring test; token horizons share a sampled autoregressive path."""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from e72_native import records, parse_answer
from e67_prefix import INSTRUCTION


def json_default(value):
    return sorted(value) if isinstance(value, set) else str(value)


def main():
    ap = argparse.ArgumentParser()
    for x in ['model', 'out', 'stage']:
        ap.add_argument('--' + x, required=True)
    for x in ['n', 'seed']:
        ap.add_argument('--' + x, type=int, required=True)
    ap.add_argument('--batch-size', type=int, default=4)
    a = ap.parse_args()
    assert a.stage in ['discovery', 'confirmation']
    t0 = time.time()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    cs, rows = records(a.stage, a.n, a.seed)
    schemas = ['source_only', 'orthogonal_prefix', 'entity_binding', 'single_source']
    rows = [r for r in rows if r['schema'] in schemas]
    assert len(rows) == 16 * a.n
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cs))
    (dest / 'prompts.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    tok.padding_side = 'left'
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                                        device_map='cuda', output_loading_info=True)
    model.eval()
    assert not loading.get('missing_keys'), loading
    assert all(any(word in k for word in ['visual.', 'vision_', 'mtp.']) for k in loading.get('unexpected_keys', [])), loading
    assert model.generation_config.forced_eos_token_id is None
    assert model.generation_config.forced_bos_token_id is None
    eos = model.generation_config.eos_token_id
    eos = [eos] if isinstance(eos, int) else list(eos)
    (dest / 'loading_info.json').write_text(json.dumps(loading, indent=2, default=json_default))

    def prompt(row, interface):
        instructed = interface != 'chat'
        thinking = interface == 'thinking_instruction'
        body = (INSTRUCTION if instructed else '') + row['prompt']
        body += '\n\nComplete the final record with its final classification code. Return the final answer on a line of the form Answer: <code>, using ' + ' or '.join(row['labels']) + '.'
        kw = dict(tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
        if thinking:
            kw['reasoning_effort'] = 'medium'
        return tok.apply_chat_template([{'role': 'user', 'content': body}], **kw)

    def tokens(seq, width):
        ids = seq[width:].cpu().tolist()
        stop = next((i + 1 for i, token in enumerate(ids) if token in eos), len(ids))
        ids = ids[:stop]
        # Keep an actual EOS even when pad and EOS are aliased.
        if not any(token in eos for token in ids):
            while ids and ids[-1] == tok.pad_token_id:
                ids.pop()
        return ids

    def generate(inputs, budget):
        return model.generate(**inputs, do_sample=True, temperature=.6, top_p=.95, top_k=20,
                              num_beams=1, max_new_tokens=budget, pad_token_id=tok.pad_token_id,
                              disable_compile=True, use_cache=True)

    audits = []
    with (dest / 'trajectories.jsonl').open('w') as f, torch.inference_mode():
        for mi, interface in enumerate(['chat', 'chat_instruction', 'thinking_instruction']):
            for bi in range(0, len(rows), a.batch_size):
                batch = rows[bi:bi + a.batch_size]
                texts = [prompt(r, interface) for r in batch]
                inputs = tok(texts, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
                decode_seed = 730000 + mi * 10000 + bi // a.batch_size
                torch.manual_seed(decode_seed)
                rng_cpu = torch.get_rng_state().clone()
                rng_cuda = torch.cuda.get_rng_state().clone()
                long = generate(inputs, 4096)
                long_ids = [tokens(seq, inputs['input_ids'].shape[1]) for seq in long]
                # Prespecified first and third batches, regardless of outcome.
                if bi in [0, 2 * a.batch_size]:
                    for horizon in [96, 2048]:
                        torch.set_rng_state(rng_cpu)
                        torch.cuda.set_rng_state(rng_cuda)
                        short = generate(inputs, horizon)
                        for row, seq, whole in zip(batch, short, long_ids):
                            part = tokens(seq, inputs['input_ids'].shape[1])
                            same = part == whole[:horizon]
                            audits.append({'uid': row['uid'], 'interface': interface, 'horizon': horizon,
                                           'short_tokens': len(part), 'matching_prefix': same})
                    (dest / 'prefix_audit.json').write_text(json.dumps(audits, indent=2))
                    assert all(r['matching_prefix'] for r in audits), audits[-8:]
                for row, whole, text in zip(batch, long_ids, texts):
                    reads = {}
                    thinking = interface.startswith('thinking')
                    for horizon in [96, 2048, 4096]:
                        part = whole[:horizon]
                        decoded = tok.decode(part, skip_special_tokens=False)
                        pred, status = parse_answer(decoded, row['labels'], thinking)
                        reads[str(horizon)] = {'prediction': pred, 'parser_status': status,
                                               'tokens': len(part), 'ended': bool(part and part[-1] in eos),
                                               'truncated': len(part) >= horizon and part[-1] not in eos}
                    f.write(json.dumps({'uid': row['uid'], 'context': row['context'], 'schema': row['schema'],
                                        'query': row['query'], 'gold': row['gold'], 'interface': interface,
                                        'decode_seed': decode_seed, 'reads': reads, 'tokens': whole,
                                        'text': tok.decode(whole, skip_special_tokens=False),
                                        'prompt_sha256': hashlib.sha256(text.encode()).hexdigest()}) + '\n')
                f.flush()
                print(interface, bi, round(time.time() - t0, 1), flush=True)
    run = {'args': vars(a), 'seconds': time.time() - t0,
           'prefix_audits': len(audits), 'prefix_mismatches': sum(not r['matching_prefix'] for r in audits),
           'torch': torch.__version__, 'transformers': transformers.__version__, 'model_class': type(model).__name__,
           'host': platform.node(), 'gpu': torch.cuda.get_device_name(),
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'dependency_sha256': {p: hashlib.sha256((Path(__file__).parent / p).read_bytes()).hexdigest() for p in ['e72_native.py', 'e71_relational.py', 'e58_factorization.py', 'e67_prefix.py']},
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'chat_template_sha256': hashlib.sha256(tok.chat_template.encode()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    assert run['prefix_mismatches'] == 0
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == '__main__':
    main()
