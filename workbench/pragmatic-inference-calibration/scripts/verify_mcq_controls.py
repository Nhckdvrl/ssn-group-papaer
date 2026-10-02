#!/usr/bin/env python3
"""Prospective E08/E04 supplemental padding and generation-policy controls."""
import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from run_native_readout import next_logits
from run_multichoice_logprob import options, t5_targets, SUFFIX

ap = argparse.ArgumentParser()
ap.add_argument('--root', type=Path, required=True)
ap.add_argument('--model', type=Path, required=True)
ap.add_argument('--model-id', required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
if args.output.exists():
    raise FileExistsError(args.output)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
seq = AutoConfig.from_pretrained(args.model, local_files_only=True).is_encoder_decoder
tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side='left', use_fast=not seq)
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
cls = AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
model = cls.from_pretrained(args.model, local_files_only=True, torch_dtype=torch.float32, device_map={'': 0}).eval()
rows = list(map(json.loads, (args.root/'data/multiprageval.jsonl').read_text().splitlines()))
if seq:
    rows = [r for r in rows if r['language'] == 'english']
letter_ids = [tok.encode(c, add_special_tokens=False)[0] for c in 'ABCDE']
result = {'model': args.model_id, 'dtype': 'float32', 'tf32': False,
          'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'letter_batch_controls': [], 't5_text_controls': [], 'hu_policy_controls': [],
          'generation_defaults': model.generation_config.to_dict()}
# First 12 + last item were fixed before examining these control outcomes.
selected = rows[:12] + rows[-1:]
for condition in ['native', 'format']:
    prompts = [r['prompt'] + (SUFFIX if condition == 'format' else '') for r in selected]
    texts = prompts if seq else [tok.apply_chat_template([{'role': 'user', 'content': p}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False) for p in prompts]
    with torch.inference_mode():
        inp = tok(texts, padding=True, return_tensors='pt', add_special_tokens=seq).to(model.device)
        batch = next_logits(model, inp)[:, letter_ids].softmax(-1)
        for i, text in enumerate(texts):
            inp = tok(text, return_tensors='pt', add_special_tokens=seq).to(model.device)
            one = next_logits(model, inp)[0, letter_ids].softmax(-1)
            result['letter_batch_controls'].append({'item_id': selected[i]['item_id'],
                'language': selected[i]['language'], 'condition': condition,
                'max_prob_delta': (one-batch[i]).abs().max().item(),
                'argmax_same': one.argmax().item() == batch[i].argmax().item()})
if seq:
    for r in [rows[0], rows[-1]]:
        targets = options(r['prompt'])
        many, lengths = t5_targets(model, tok, r['prompt'], targets)
        one = [t5_targets(model, tok, r['prompt'], [t])[0][0] for t in targets]
        result['t5_text_controls'].append({'item_id': r['item_id'],
            'max_logprob_delta': max(abs(a-b) for a, b in zip(one, many)), 'lengths': lengths})
hu = list(map(json.loads, (args.root/'data/hu.jsonl').read_text().splitlines()))
for r in [hu[0], hu[-1]]:
    inp = tok(r['prompt'], return_tensors='pt').to(model.device)
    ids = [tok.encode(c, add_special_tokens=False)[0] for c in r['choices']]
    with torch.inference_mode():
        raw = next_logits(model, inp)[0, ids].softmax(-1)
        gen = model.generate(**inp, max_new_tokens=1, do_sample=False, repetition_penalty=1.,
                             return_dict_in_generate=True, output_scores=True)
        policy = gen.scores[0][0, ids].float().softmax(-1)
    result['hu_policy_controls'].append({'item_id': r['item_id'], 'phenomenon': r['phenomenon'],
        'repeat_penalty_one_max_prob_delta': (raw-policy).abs().max().item(),
        'argmax_same': raw.argmax().item() == policy.argmax().item()})
result['letter_batch_pass'] = all(r['max_prob_delta'] < 1e-3 for r in result['letter_batch_controls'])
result['t5_text_batch_pass'] = all(r['max_logprob_delta'] < 1e-3 for r in result['t5_text_controls']) if seq else None
args.output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ['model', 'letter_batch_pass', 't5_text_batch_pass', 'hu_policy_controls']}))
