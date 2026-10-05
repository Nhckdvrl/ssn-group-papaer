"""E13: frozen causal likelihood of original question-free two-sentence items.

No chat template, questions, new continuations, or semantic gold. Original text
and per-word scores remain cache-only; the public summary contains statistics.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from analyze import estimate
from data import CACHE, sha
from slattery import load_published


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def prepare(cache, tokenizer):
    rows, source = load_published(cache)
    normalized = cache / 'normalized/slattery2013.jsonl'
    assert rows == list(map(json.loads, normalized.read_text().splitlines()))
    review_path = Path(__file__).parents[1] / 'results/D0-Slattery-external-transcription-v2.json'
    review = json.loads(review_path.read_text())
    assert review['dataset_sha256'] == sha(normalized)
    assert review['pdf_sha256'] == source['revision_pdf_sha256']
    reviewed = [a for v in review['reviews'] for a in v['answers']]
    assert len(reviewed) == 96 and {a['item_id'] for a in reviewed} == {r['item_id'] for r in rows}
    assert all(a['faithful'] == 'Yes' and a['question_valid'] and a['certainty'] == 'clear' for a in reviewed)
    groups = {}
    for r in rows:
        words = list(re.finditer(r'\S+', r['sentence']))
        encoded = tokenizer(r['sentence'], add_special_tokens=False, return_offsets_mapping=True)
        indices = [[] for _ in words]
        for j, (a, b) in enumerate(encoded['offset_mapping']):
            if not r['sentence'][a:b].strip():
                continue
            touched = [i for i, w in enumerate(words) if a < w.end() and b > w.start()]
            assert len(touched) == 1, 'A tokenizer token spans multiple original words'
            indices[touched[0]].append(j)
        assert all(indices) and indices[0][0] == 0
        assert all(t > 0 for ii in indices[1:] for t in ii)
        start = r['second_sentence_start_word']
        assert len(words) - start == r['second_sentence_word_count']
        assert r['question'] is None and r['gold'] is None
        groups[r['item_id']] = dict(ids=encoded['input_ids'], indices=indices,
                                   sentence_sha256=digest(r['sentence']),
                                   token_sha256=digest(json.dumps(encoded['input_ids'], separators=(',', ':'))))
    assert len(groups) == 96
    return rows, groups, source, sha(normalized), sha(review_path)


def mean_region(bits, indices):
    return float(np.mean([bits[i] for i in indices])) if indices else None


def run(args):
    assert not args.out.exists(), 'Immutable run; choose a new output directory'
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side='left')
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    rows, groups, source, data_sha, review_sha = prepare(args.cache, tokenizer)
    args.out.mkdir(parents=True)
    torch.manual_seed(0)
    torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32 = False
    cfg = dict(experiment='E13', task_count=96, source_items=24,
               normalized_sha256=data_sha, external_transcription_review_sha256=review_sha,
               source_pdf_sha256=source['revision_pdf_sha256'], model=str(args.model),
               model_manifest=json.loads((args.model / 'manifest.json').read_text()),
               git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               code_sha256={p.name: sha(p) for p in Path(__file__).parent.glob('*.py')},
               dtype='float32', frozen=True, attention='sdpa', tf32=False,
               torch=torch.__version__, transformers=transformers.__version__,
               gpu=torch.cuda.get_device_name(), batch_size=args.batch_size, seed=0,
               input_format='Original ordinary text, no BOS/chat template, question or answer choices.',
               scoring='Full-vocabulary teacher-forced causal token NLL / log(2), summed into source whitespace words; first source word unscored (null).',
               primary='Mean bits of all S2 words; GP minus comma per NP option and option0 minus option1 interaction.',
               secondary='First literal reflexive/reciprocal region, up to two preceding and following S2 words; absent reference stays null.',
               semantic_gold_labels=0, proxy_used=False)
    (args.out / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    begin = time.time()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
                torch_dtype=torch.float32, attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():
        p.requires_grad_(False)
    scores = {}
    by_id = {r['item_id']: r for r in rows}
    keys = sorted(groups, key=lambda k: (len(groups[k]['ids']), k))
    with torch.inference_mode():
        for offset in range(0, len(keys), args.batch_size):
            batch = keys[offset:offset + args.batch_size]
            padded = tokenizer.pad([dict(input_ids=groups[k]['ids'], attention_mask=[1] * len(groups[k]['ids']))
                                     for k in batch], return_tensors='pt').to('cuda')
            logits = model(**padded).logits[:, :-1, :].float()
            targets = padded['input_ids'][:, 1:]
            nll = ((logits.logsumexp(-1) - logits.gather(-1, targets.unsqueeze(-1)).squeeze(-1)) / np.log(2)).cpu().numpy()
            if offset == 0:
                # Independently check causal indexing against the library's
                # masked-label loss on the complete S2 token span.
                labels = torch.full_like(padded['input_ids'], -100)
                checked = []
                for j, k in enumerate(batch):
                    pad = padded['input_ids'].shape[1] - len(groups[k]['ids'])
                    for ii in groups[k]['indices'][by_id[k]['second_sentence_start_word']:]:
                        for t in ii:
                            labels[j, t + pad] = padded['input_ids'][j, t + pad]
                            checked.append(nll[j, t + pad - 1] * np.log(2))
                library_loss = float(model(**padded, labels=labels).loss)
                manual_loss = float(np.mean(checked))
                assert abs(library_loss - manual_loss) < 1e-5, 'Causal loss indexing mismatch'
                cfg['loss_indexing_check'] = dict(items=len(batch), library_nats=library_loss,
                                                  manual_nats=manual_loss, absolute_difference=abs(library_loss - manual_loss))
            for j, k in enumerate(batch):
                pad = padded['input_ids'].shape[1] - len(groups[k]['ids'])
                bits = [None] + [float(sum(nll[j, t + pad - 1] for t in ii)) for ii in groups[k]['indices'][1:]]
                assert all(np.isfinite(v) and v >= 0 for v in bits[1:])
                scores[k] = bits
            print(f'{offset + len(batch)}/96 items elapsed={time.time() - begin:.1f}s', flush=True)
    with (args.out / 'scores.jsonl').open('w') as f:
        for r in rows:
            bits = scores[r['item_id']]
            s = r['second_sentence_start_word']
            ref = r['literal_reference_word_indices']
            before = list(range(max(s, ref[0] - 2), ref[0])) if ref else []
            after = list(range(ref[-1] + 1, min(len(bits), ref[-1] + 3))) if ref else []
            out = {k: r[k] for k in ('item_id', 'pair_id', 'source', 'construction', 'condition', 'source_np_option',
                                    'source_block', 'source_row_id', 'second_sentence_start_word',
                                    'second_sentence_word_count', 'literal_reference_word_indices')}
            out.update(sentence_sha256=groups[r['item_id']]['sentence_sha256'],
                       token_sha256=groups[r['item_id']]['token_sha256'], word_bits=bits,
                       second_sentence_mean_bits=mean_region(bits, range(s, len(bits))),
                       first_sentence_scored_mean_bits=mean_region(bits, range(1, s)),
                       literal_reference_mean_bits=mean_region(bits, ref),
                       pre_reference_mean_bits=mean_region(bits, before), post_reference_mean_bits=mean_region(bits, after))
            f.write(json.dumps(out) + '\n')
    elapsed = time.time() - begin
    cfg.update(scores_sha256=sha(args.out / 'scores.jsonl'), wall_seconds=elapsed, gpu_hours=elapsed / 3600,
               peak_gpu_bytes=torch.cuda.max_memory_allocated(), scored_source_words=sum(len(b) - 1 for b in scores.values()))
    (args.out / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    print('DONE', elapsed, flush=True)


def analyze(path):
    cfg = json.loads((path / 'config.json').read_text())
    assert cfg['scores_sha256'] == sha(path / 'scores.jsonl')
    rows = list(map(json.loads, (path / 'scores.jsonl').read_text().splitlines()))
    assert len(rows) == cfg['task_count'] == 96 and len({r['item_id'] for r in rows}) == 96
    grouped = collections.defaultdict(dict)
    for r in rows:
        grouped[r['pair_id']][r['source_np_option'], r['condition']] = r
    assert len(grouped) == 24 and all(len(d) == 4 for d in grouped.values())
    result = dict(experiment='E13', units='bits per original whitespace word', cells={}, gp_minus_comma={},
                  option0_minus_option1_gp_effect={}, itemwise={}, bootstrap_draws=10000, bootstrap_seed=20261005,
                  source_items=24, task_count=96, primary='second_sentence_mean_bits',
                  analysis_code_sha256=sha(Path(__file__)), scores_sha256=cfg['scores_sha256'],
                  interpretation='Source NP option numbers are not semantic gold. Conditional prediction is not parse accuracy. No new questions or continuations.')
    metrics = ['second_sentence_mean_bits', 'literal_reference_mean_bits', 'pre_reference_mean_bits',
               'post_reference_mean_bits', 'first_sentence_scored_mean_bits']
    def stat(v):
        assert len(v) >= 2
        return dict(estimate([v[k] for k in sorted(v)]), pair_ids=sorted(v))
    for block in ('all24', 'first12', 'last12'):
        gg = {k: d for k, d in grouped.items() if block == 'all24' or d[0, 'gp']['source_block'] == block}
        for m in metrics:
            effects = {}
            for option in (0, 1):
                v = {c: {k: d[option, c][m] for k, d in gg.items() if d[option, c][m] is not None}
                     for c in ('gp', 'explicit_cue')}
                assert v['gp'].keys() == v['explicit_cue'].keys()
                for c in v:
                    result['cells'][f'{block}/{m}/option{option}/{c}'] = stat(v[c])
                delta = {k: v['gp'][k] - v['explicit_cue'][k] for k in v['gp']}
                effects[option] = delta
                result['gp_minus_comma'][f'{block}/{m}/option{option}'] = stat(delta)
                if block == 'all24':
                    result['itemwise'][f'{m}/option{option}'] = delta
            assert effects[0].keys() == effects[1].keys()
            interaction = {k: effects[0][k] - effects[1][k] for k in effects[0]}
            result['option0_minus_option1_gp_effect'][f'{block}/{m}'] = stat(interaction)
    result['literal_reference_missing_pair_ids'] = [k for k, d in grouped.items() if not d[0, 'gp']['literal_reference_word_indices']]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--cache', type=Path, default=CACHE)
    run_parser.add_argument('--model', type=Path, default=CACHE / 'models/Qwen3-8B')
    run_parser.add_argument('--out', type=Path, required=True)
    run_parser.add_argument('--batch-size', type=int, default=4)
    analysis_parser = sub.add_parser('analyze')
    analysis_parser.add_argument('run_dir', type=Path)
    analysis_parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'run':
        run(args)
    else:
        args.out.write_text(json.dumps(analyze(args.run_dir), indent=2) + '\n')
