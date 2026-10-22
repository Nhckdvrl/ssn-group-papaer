#!/usr/bin/env python3
"""Count native SFT input/target tokens with a fixed local tokenizer; no inference."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def file_sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def describe(values):
    ordered = sorted(values)
    def percentile(p):
        return ordered[round((len(ordered) - 1) * p)]
    return dict(min=ordered[0], median=statistics.median(ordered),
                p90=percentile(.9), p95=percentile(.95), p99=percentile(.99),
                max=ordered[-1], total=sum(ordered))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--tokenizer', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    output = Path(args.out)
    if output.exists():
        raise FileExistsError('Preserve previous token inventories')
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    if not tok.eos_token:
        raise ValueError('Tokenizer must specify the assistant end token')
    prompt_lengths, completion_lengths, ids = [], [], set()
    with Path(args.source).open() as source:
        for line in source:
            row = json.loads(line)
            if row['episode_id'] in ids:
                raise ValueError('Duplicate episode in SFT export')
            ids.add(row['episode_id'])
            if [m['role'] for m in row['messages']] != ['system', 'user']:
                raise ValueError('SFT input contains a target or unexpected turn')
            prefix = tok.apply_chat_template(row['messages'], tokenize=True, return_dict=False,
                                             add_generation_prompt=True, enable_thinking=False)
            target = tok.encode(row['completion'] + tok.eos_token, add_special_tokens=False)
            prompt_lengths.append(len(prefix))
            completion_lengths.append(len(target))
    if not ids:
        raise ValueError('Empty training export')
    full = [a + b for a, b in zip(prompt_lengths, completion_lengths)]
    token_files = {f.name: file_sha(f) for f in Path(args.tokenizer).iterdir()
                   if f.is_file() and (f.name.startswith('tokenizer') or
                                      f.name.startswith('chat_template') or f.name in ['vocab.json', 'merges.txt'])}
    result = dict(source_path=str(Path(args.source).resolve()), source_sha256=file_sha(args.source),
                  source_bytes=Path(args.source).stat().st_size, tokenizer_path=args.tokenizer,
                  tokenizer_files=token_files, script_sha256=file_sha(__file__), n_rows=len(ids),
                  prompt_tokens=describe(prompt_lengths), completion_tokens=describe(completion_lengths),
                  concatenated_tokens=describe(full),
                  context_budget_coverage={str(cap): dict(n_complete=sum(n <= cap for n in full),
                      n_over=sum(n > cap for n in full),
                      complete_tokens=sum(n for n in full if n <= cap))
                      for cap in [4096, 8192, 12288, 16384, 32768]},
                  format='Native system/user generation prefix, enable_thinking=False; separately encoded completion plus tokenizer eos_token. Prefix labels would be masked in SFT.',
                  model_calls=0, exclusions_applied=0,
                  note='Offline size inventory only. No training, truncation, sample selection or measured GPU throughput.')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['tokenizer_files']}, indent=2))


if __name__ == '__main__':
    main()
