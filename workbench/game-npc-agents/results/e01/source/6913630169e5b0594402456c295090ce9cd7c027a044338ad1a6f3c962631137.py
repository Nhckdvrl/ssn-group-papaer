#!/usr/bin/env python3
"""Real inference for the frozen E01 messages; no gold fields reach either model."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
import scope_probe as probe

STEP_ENDPOINT = 'https://api.stepfun.com/step_plan/v1/chat/completions'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def append(path, data):
    with Path(path).open('a') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def step_payload(task, args):
    return dict(model='step-5-preview', messages=task['messages'], temperature=0,
                reasoning_effort='medium', max_tokens=args.max_tokens, stream=False)


def run_step(tasks, args, out, meta):
    import requests
    secret = os.environ.get('STEPFUN_API_KEY')
    if not secret:
        import getpass
        secret = getpass.getpass('Step Plan API key (hidden): ')
    if not secret:
        raise ValueError('Missing Step Plan credential')
    session = requests.Session()
    session.trust_env = False
    for i, task in enumerate(tasks):
        start = time.monotonic()
        payload = step_payload(task, args)
        row = dict(task_id=task['task_id'], model='step-5-preview', started_utc=now(),
                   endpoint=STEP_ENDPOINT, request=payload)
        try:
            response = session.post(STEP_ENDPOINT, json=payload,
                headers={'Authorization': 'Bearer ' + secret}, timeout=(20, 240),
                allow_redirects=False)
            row['http_status'] = response.status_code
            row['request_id'] = response.headers.get('x-request-id')
            # Never store headers, request credentials, or exception request objects.
            row['response_body'] = response.json()
            if response.status_code != 200:
                row['error'] = 'HTTP ' + str(response.status_code)
            else:
                body = row['response_body']
                choice = body['choices'][0]
                row.update(raw=choice['message'].get('content') or '',
                           finish_reason=choice.get('finish_reason'),
                           usage=body.get('usage', {}), returned_model=body.get('model'))
        except Exception as exc:
            row['error'] = type(exc).__name__  # credential-safe failure record
        row['latency_s'] = time.monotonic() - start
        row['action_id'], row['utterance'] = probe.parse_reply(row.get('raw', ''))
        append(out / 'responses.jsonl', row)
        print(f"{i+1}/{len(tasks)} {task['task_id']} finish={row.get('finish_reason')} error={row.get('error')}", flush=True)
        if row.get('error'):
            # Fail closed on billing, auth, redirect, or transport failure. No fallback.
            raise RuntimeError('Step Plan request failed; inspect saved credential-free record')


def run_hf(tasks, args, out, meta):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    set_seed(0)
    torch.set_num_threads(8)
    checkpoint = Path(args.checkpoint).resolve()
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True)
    tokenizer.padding_side = 'left'
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(checkpoint, local_files_only=True,
            dtype=torch.bfloat16, attn_implementation='sdpa', device_map={'': 0}).eval()
    # Explicitly override generation defaults that otherwise suggest sampling.
    meta.update(checkpoint=str(checkpoint), revision=checkpoint.name,
        torch=torch.__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
        generation_config=model.generation_config.to_dict(),
        asset_files=[dict(name=p.name, size=p.stat().st_size,
                         cache_blob=p.resolve().name) for p in sorted(checkpoint.iterdir()) if p.is_file()],
        tokenizer_template_sha256=hashlib.sha256(str(tokenizer.chat_template).encode()).hexdigest(),
        config_sha256=sha(checkpoint / 'config.json'))
    dump(out / 'metadata.json', meta)
    for offset in range(0, len(tasks), args.batch_size):
        block = tasks[offset:offset+args.batch_size]
        rendered = [tokenizer.apply_chat_template(t['messages'], tokenize=False,
                    add_generation_prompt=True, enable_thinking=False) for t in block]
        inputs = tokenizer(rendered, return_tensors='pt', padding=True,
                           add_special_tokens=False).to(model.device)
        start = time.monotonic()
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False,
                max_new_tokens=args.max_tokens, pad_token_id=tokenizer.pad_token_id,
                temperature=None, top_p=None, top_k=None)
        torch.cuda.synchronize()
        elapsed = time.monotonic() - start
        eos = model.generation_config.eos_token_id
        eos = set(eos if isinstance(eos, list) else [eos])
        for j, task in enumerate(block):
            ids = generated[j, inputs.input_ids.shape[1]:].tolist()
            end = next((k+1 for k,t in enumerate(ids) if t in eos), len(ids))
            ids = ids[:end]
            raw = tokenizer.decode(ids, skip_special_tokens=True)
            action, utterance = probe.parse_reply(raw)
            row = dict(task_id=task['task_id'], model=args.model, revision=checkpoint.name,
                started_utc=now(), raw=raw, action_id=action, utterance=utterance,
                finish_reason='stop' if ids and ids[-1] in eos else 'length',
                usage=dict(prompt_tokens=int(inputs.attention_mask[j].sum()),
                           completion_tokens=len(ids)),
                batch_latency_s=elapsed, batch_size=len(block),
                rendered_prompt=rendered[j], generated_token_ids=ids)
            append(out / 'responses.jsonl', row)
        print(f'{offset+len(block)}/{len(tasks)} batch_s={elapsed:.2f}', flush=True)
    meta['peak_allocated_bytes'] = torch.cuda.max_memory_allocated()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend', choices=['hf','step-plan'], required=True)
    p.add_argument('--tasks', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--checkpoint')
    p.add_argument('--max-tokens', type=int, required=True)
    p.add_argument('--batch-size', type=int, default=8)
    args = p.parse_args()
    tasks = probe.read_jsonl(args.tasks)
    assert len({t['task_id'] for t in tasks}) == len(tasks)
    if args.backend == 'step-plan' and args.model != 'step-5-preview':
        raise ValueError('Only the explicitly authorized Step5 model is supported')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'responses.jsonl').exists() or (out / 'metadata.json').exists():
        raise FileExistsError('Use a new output directory; never overwrite prior attempts')
    meta = dict(started_utc=now(), args=vars(args), argv=sys.argv,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        tasks_sha256=sha(args.tasks), runner_sha256=sha(__file__),
        python=sys.version, packages={k:importlib.metadata.version(k) for k in
            ['requests'] if importlib.util.find_spec(k)}, seed=0,
        config=dict(temperature=0, do_sample=False, dtype='bfloat16', attention='sdpa',
                    enable_thinking=False) if args.backend=='hf' else
               dict(endpoint=STEP_ENDPOINT, reasoning_effort='medium', temperature=0,
                    redirects=False, cash_fallback=False))
    if args.backend=='hf':
        meta['packages']['transformers']=importlib.metadata.version('transformers')
    dump(out / 'metadata.json', meta)
    start=time.monotonic()
    try:
        (run_hf if args.backend=='hf' else run_step)(tasks,args,out,meta)
        meta['complete']=True
    finally:
        meta.update(finished_utc=now(),wall_s=time.monotonic()-start)
        dump(out / 'metadata.json',meta)


if __name__ == '__main__':
    main()
