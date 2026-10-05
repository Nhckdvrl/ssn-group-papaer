"""Frozen raw-text likelihood for E14, with reviewed inputs and target spans."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from data import CACHE, sha
from event_identity import digest


def prepare(data, tokenizer, expected_targets=2):
    report = json.loads(data.with_suffix('.audit.json').read_text())
    assert report['audited_sha256'] == sha(data)
    rows = list(map(json.loads, data.read_text().splitlines()))
    assert len(rows) == report['variants'] and len({r['item_id'] for r in rows}) == len(rows)
    groups = {}
    context_tokens = {}
    for r in rows:
        assert r['question'] is None and r['gold'] is None
        assert digest(r['sentence']) == r['sentence_sha256']
        encoded = tokenizer(r['sentence'], add_special_tokens=False, return_offsets_mapping=True)
        words = list(re.finditer(r'\S+', r['sentence']))
        wi = [[] for _ in words]
        for t, (a, b) in enumerate(encoded['offset_mapping']):
            if not r['sentence'][a:b].strip():
                continue
            touched = [i for i, w in enumerate(words) if a < w.end() and b > w.start()]
            assert len(touched) == 1, 'Token spans multiple source words'
            wi[touched[0]].append(t)
        assert all(wi) and wi[0][0] == 0 and all(t > 0 for ii in wi[1:] for t in ii)
        indices = r['target_span_word_indices']
        assert all(0 < i < len(words) for i in indices)
        context = encoded['input_ids'][:wi[indices[0]][0]]
        key = (r['pair_id'], r['source_np_option'], r['condition'], r['episode_anchor'])
        if key in context_tokens:
            assert context_tokens[key] == context, 'Alternatives have different pre-target causal contexts'
        context_tokens[key] = context
        if 'context_reference_sentence' in r:
            other = tokenizer(r['context_reference_sentence'], add_special_tokens=False, return_offsets_mapping=True)
            first = next(i for i, (a,b) in enumerate(other['offset_mapping']) if b > r['target_start_char'] and r['context_reference_sentence'][a:b].strip())
            assert context == other['input_ids'][:first], 'Crossover changed causal pre-target tokens'
        groups[r['item_id']] = dict(ids=encoded['input_ids'], indices=wi,
                                    token_sha256=digest(json.dumps(encoded['input_ids'], separators=(',', ':'))))
    assert len(context_tokens) * expected_targets == len(rows)
    return rows, groups


def run(args):
    assert not args.out.exists(), 'Immutable experiment run'
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side='left')
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    rows, groups = prepare(args.data, tokenizer, expected_targets=1 if args.experiment=='E16' else 2)
    args.out.mkdir(parents=True)
    torch.manual_seed(0); torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32 = False
    cfg = dict(experiment=args.experiment, task_count=len(rows), source_items=len({r['pair_id'] for r in rows}),
               model=str(args.model), model_manifest=json.loads((args.model / 'manifest.json').read_text()),
               data_sha256=sha(args.data), independent_audit_sha256=sha(args.data.with_suffix('.audit.json')),
               code_sha256={p.name: sha(p) for p in Path(__file__).parent.glob('*.py')},
               git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               frozen=True, dtype='float32', tf32=False, attention='sdpa', seed=0,
               torch=torch.__version__, transformers=transformers.__version__, gpu=torch.cuda.get_device_name(),
               batch_size=args.batch_size, input='Ordinary text, no BOS/chat template/instruction/question.',
               target_context_token_identity_verified=True, semantic_gold_labels=0,
               scoring='Full-vocabulary causal token NLL in bits, summed into original whitespace words; first word null.',
               cohort_policy='Score all reviewed variants, retain audit flags. Analyze predeclared eligible and clear-reference strata using explicit pair intersections.')
    (args.out / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    start = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
                  torch_dtype=torch.float32, attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():
        p.requires_grad_(False)
    keys = sorted(groups, key=lambda k: (len(groups[k]['ids']), k))
    byid = {r['item_id']: r for r in rows}
    scores = {}
    with torch.inference_mode():
        for offset in range(0, len(keys), args.batch_size):
            batch = keys[offset:offset + args.batch_size]
            inputs = tokenizer.pad([dict(input_ids=groups[k]['ids'], attention_mask=[1] * len(groups[k]['ids']))
                                      for k in batch], return_tensors='pt').to('cuda')
            logits = model(**inputs).logits[:, :-1, :].float()
            targets = inputs['input_ids'][:, 1:]
            bits = ((logits.logsumexp(-1) - logits.gather(-1, targets.unsqueeze(-1)).squeeze(-1)) / np.log(2)).cpu().numpy()
            if offset == 0:
                labels = torch.full_like(inputs['input_ids'], -100); values = []
                for j, k in enumerate(batch):
                    pad = inputs['input_ids'].shape[1] - len(groups[k]['ids'])
                    for i in byid[k]['target_span_word_indices']:
                        for t in groups[k]['indices'][i]:
                            labels[j, t + pad] = inputs['input_ids'][j, t + pad]
                            values.append(bits[j, t + pad - 1] * np.log(2))
                loss = float(model(**inputs, labels=labels).loss)
                manual = float(np.mean(values))
                assert abs(loss - manual) < 1e-5, 'Target span loss/indexing mismatch'
                cfg['masked_target_loss_check'] = dict(library_nats=loss, manual_nats=manual, absolute_difference=abs(loss-manual))
            for j, k in enumerate(batch):
                pad = inputs['input_ids'].shape[1] - len(groups[k]['ids'])
                values = [None] + [float(sum(bits[j, t + pad - 1] for t in ii)) for ii in groups[k]['indices'][1:]]
                assert all(np.isfinite(v) and v >= 0 for v in values[1:])
                scores[k] = values
            if offset % (args.batch_size * 12) == 0:
                print(f'{offset+len(batch)}/{len(keys)} raw inputs elapsed={time.time()-start:.1f}s', flush=True)
    with (args.out / 'scores.jsonl').open('w') as f:
        for r in rows:
            out = {k: v for k, v in r.items() if k not in ('sentence', 'context_reference_sentence', 'initial_parse_claim', 'final_parse_claim')}
            wb = scores[r['item_id']]; span = r['target_span_word_indices']
            out.update(token_sha256=groups[r['item_id']]['token_sha256'], word_bits=wb,
                       target_total_bits=sum(wb[i] for i in span), target_word_count=len(span),
                       followup_mean_bits=float(np.mean(wb[r['authored_followup_start_word']:])) )
            f.write(json.dumps(out) + '\n')
    elapsed = time.time() - start
    cfg.update(scores_sha256=sha(args.out / 'scores.jsonl'), wall_seconds=elapsed,
               gpu_hours=elapsed/3600, peak_gpu_bytes=torch.cuda.max_memory_allocated())
    (args.out / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    print('DONE', elapsed, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--experiment', choices=['E14', 'E15', 'E16', 'E17'], default='E14')
    p.add_argument('--model', type=Path, default=CACHE / 'models/Qwen3-8B')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--batch-size', type=int, default=4)
    run(p.parse_args())
