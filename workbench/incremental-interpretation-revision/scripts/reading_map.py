"""E52 frozen model map: original-format replication and paired reading interventions."""
import argparse
import collections
import hashlib
import inspect
import itertools
import json
import math
import os
import re
from pathlib import Path
import time

import torch
import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, Gemma3ForConditionalGeneration
from data import CACHE, sha

REPAIR = 'Read the whole sentence and revise any initial interpretation before answering.'
SYSTEM = 'Read the supplied sentence and answer its comprehension question. Use the sentence as given.'
FILLER_BANK = {}
ALIAS_BANK = {}


def filler_sentence(sentence, tokenizer):
    key = tokenizer.name_or_path
    if key not in FILLER_BANK:
        bank = collections.defaultdict(list)
        # Complete, single finite-clause templates; no truncation into a new ambiguity.
        for subject, adverb, place, tail in itertools.product(
            ('A notebook', 'A small notebook', 'A small blue notebook', 'A plain old notebook'),
            ('', 'quietly ', 'peacefully ', 'undisturbed '),
            ('beside a window', 'beside a narrow window', 'beside a tall narrow window', 'beside a quiet shaded window'),
            ('', ' inside an empty room', ' inside an empty room on the upper floor',
             ' inside an empty room on the upper floor of a modest building',
             ' inside an empty room on the upper floor of a modest building near a broad avenue',
             ' inside an empty room on the upper floor of a modest building near a broad avenue in a quiet neighborhood')):
            text = f'{subject} rested {adverb}{place}{tail}.'
            bank[len(tokenizer.encode(text, add_special_tokens=False))].append(text)
        for text in ('Rain fell.', 'Rain fell softly.', 'The rain fell softly.', 'The room was quiet.',
                     'A lamp glowed.', 'A small notebook rested here.', 'A notebook rested quietly here.'):
            bank[len(tokenizer.encode(text, add_special_tokens=False))].append(text)
        FILLER_BANK[key] = bank
    n = len(tokenizer.encode(sentence, add_special_tokens=False))
    candidates = FILLER_BANK[key].get(n, [])
    # Exclude shared content words; articles/prepositions are not experimental entities.
    if not candidates: return None
    stop = {'a', 'an', 'the', 'is', 'was', 'were', 'be', 'to', 'of', 'in', 'on', 'at', 'by', 'and', 'as', 'for', 'with'}
    content = set(re.findall(r"[a-z]+", sentence.lower()))-stop
    return next((s for s in candidates if not (set(re.findall(r"[a-z]+", s.lower()))-stop) & content), None)


def shared_prefix(sequences):
    count = 0
    for tokens in zip(*sequences):
        if len(set(tokens)) != 1: break
        count += 1
    return count


def make_reading(row, reading, tokenizer):
    sentence = row['sentence']
    if reading in ('R0', 'R4', 'R6'): return sentence
    if reading == 'R1': return sentence+'\n'+sentence
    if reading == 'R2':
        index = row.get('disamb_word_index')
        if index is None or index == 0: return None
        assert 0 < index < len(sentence.split())
        return ' '.join(sentence.split()[:index])+'\n'+sentence
    if reading == 'R3':
        n = len(tokenizer.encode(sentence, add_special_tokens=False))
        filler = filler_sentence(sentence, tokenizer)
        if filler is None: return None
        assert len(tokenizer.encode(filler, add_special_tokens=False)) == n
        return filler+'\n'+sentence
    if reading == 'R5': return sentence
    raise ValueError(reading)


def chat(tokenizer, content, thinking=False, repair=False):
    messages = [{'role': 'system', 'content': SYSTEM+(' '+REPAIR if repair else '')},
                {'role': 'user', 'content': content}]
    if tokenizer.chat_template:
        try:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
        except Exception:
            return tokenizer.apply_chat_template([{'role': 'user', 'content': messages[0]['content']+'\n\n'+content}],
                tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
    return messages[0]['content']+'\n\n'+content+'\n\nAnswer:'


def generate_tasks(rows, tokenizer, formats, readings, mode, include_repair=False, skipped=None):
    root = CACHE/'upstream/amouyal/prefixes'
    all_prefixes = {}
    for order in ('reg', 'rev'):
        suffix = '' if order == 'reg' else '_rev'
        all_prefixes[('yn', order)] = json.loads((root/f'prefixes{suffix}.json').read_text())
        all_prefixes[('2opt', order)] = json.loads((root/f'prefixes_question{suffix}.json').read_text())
    for row in rows:
        for reading in readings:
            if reading == 'R4' and row['condition'] != 'control': continue
            if reading == 'R6': continue  # Dedicated greedy thinking pass, never score pre-thinking logits as final answers.
            sentence = make_reading(row, reading, tokenizer)
            if sentence is None:
                if skipped is not None: skipped.append(dict(item_id=row['item_id'], reading=reading,
                    reason='No agreed/usable disambiguation landmark' if reading == 'R2' else 'No complete token-length-matched filler'))
                continue
            for fmt in formats:
                if fmt == 'A':
                    if row['source'] != 'amouyal': continue
                    for order in ('reg', 'rev'):
                        for index, prefix in enumerate(all_prefixes[(row['question_format'], order)]):
                            question = prefix['question'].replace('SENTENCE', sentence).replace('QUESTION', row['question'])
                            if reading == 'R5':
                                question = row['question']+'\n\n'+question if order == 'reg' else question+'\n\n'+row['question']
                            prompt = prefix['system']+'\n\n'+question+'\n\n'+prefix['suffix']
                            candidates = list(row['options'])
                            if row['question_format'] == '2opt':
                                candidates = [s.removeprefix('The ').removeprefix('the ') for s in candidates]
                            yield dict(row=row, format=fmt, reading=reading, order=order, prompt_index=index,
                                       mapping=0, repair=False, prompt=prompt, candidates=candidates,
                                       mode=mode, legacy_options=[row['source_gold'], row['options'][1-row['gold']]])
                if fmt == 'B':
                    for mapping in (0, 1):
                        options = row['options'][::1 if mapping == 0 else -1]
                        content = f'Sentence:\n{sentence}\n\nQuestion:\n{row["question"]}\nA. {options[0]}\nB. {options[1]}\nAnswer only A or B.'
                        if reading == 'R5': content = 'Question:\n'+row['question']+'\n\n'+content
                        for repair in ((False, True) if include_repair and reading == 'R0' else (False,)):
                            yield dict(row=row, format=fmt, reading=reading, order='reg', prompt_index=0,
                                mapping=mapping, repair=repair, prompt=chat(tokenizer, content, repair=repair),
                                candidates=['A', 'B'], mode='sequence',
                                candidate_gold=row['gold'] if mapping == 0 else 1-row['gold'])


def encode_choices(tokenizer, task):
    # Re-tokenize the full candidate string; trailing-space merges are part of the target.
    sequences = [tokenizer.encode(task['prompt']+choice, add_special_tokens=True) for choice in task['candidates']]
    common = shared_prefix(sequences)
    assert common > 0 and all(len(s) > common for s in sequences), 'Empty/identical candidate continuation'
    return sequences, common


def sequence_scores(model, sequences, common_lengths, pad_id):
    width = max(map(len, sequences)); keep = max(len(s)-n+1 for s, n in zip(sequences, common_lengths))
    ids = torch.full((len(sequences), width), pad_id, dtype=torch.long, device=model.device)
    mask = torch.zeros_like(ids)
    for i, sequence in enumerate(sequences):
        ids[i, -len(sequence):] = torch.tensor(sequence, device=model.device)
        mask[i, -len(sequence):] = 1
    positions = mask.cumsum(-1)-1; positions.masked_fill_(mask == 0, 0)
    kwargs = dict(input_ids=ids, attention_mask=mask, position_ids=positions, use_cache=False)
    supports_keep = 'logits_to_keep' in inspect.signature(model.forward).parameters
    if supports_keep: kwargs['logits_to_keep'] = keep
    with torch.inference_mode():
        logits = model(**kwargs).logits.float()
        logprobs = logits.log_softmax(-1)
        start = width-logits.shape[1]
        values = []
        for i, (sequence, common) in enumerate(zip(sequences, common_lengths)):
            offset = width-len(sequence)
            score = sum(logprobs[i, offset+j-1-start, sequence[j]] for j in range(common, len(sequence)))
            values.append(float(score))
    return values


def legacy_scores(model, tokenizer, tasks, processed=False):
    encoded = tokenizer([t['prompt'] for t in tasks], padding=True, return_tensors='pt').to(model.device)
    encoded.pop('token_type_ids', None)
    positions = encoded['attention_mask'].cumsum(-1)-1; positions.masked_fill_(encoded['attention_mask'] == 0, 0)
    kwargs = dict(**encoded, position_ids=positions, use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters: kwargs['logits_to_keep'] = 1
    with torch.inference_mode(): logits = model(**kwargs).logits[:, -1].float()
    if processed and model.generation_config.do_sample:
        from transformers import TemperatureLogitsWarper, TopKLogitsWarper, TopPLogitsWarper
        generation = model.generation_config
        if generation.temperature != 1: logits = TemperatureLogitsWarper(generation.temperature)(encoded['input_ids'], logits)
        if generation.top_k: logits = TopKLogitsWarper(generation.top_k)(encoded['input_ids'], logits)
        if generation.top_p < 1: logits = TopPLogitsWarper(generation.top_p)(encoded['input_ids'], logits)
    def clean(s):
        s = s.replace(' ', '').lower().strip()
        return s[1:] if s and not s[0].isascii() else s
    if tokenizer.name_or_path not in ALIAS_BANK:
        aliases_by_word = collections.defaultdict(list)
        for word, token in tokenizer.get_vocab().items(): aliases_by_word[clean(word)].append(token)
        ALIAS_BANK[tokenizer.name_or_path] = aliases_by_word
    bank = ALIAS_BANK[tokenizer.name_or_path]
    values = []
    for i, task in enumerate(tasks):
        aliases = [bank[option.lower().replace('the ', '')] for option in task['legacy_options']]
        if not all(aliases): values.append(None); continue
        a, b = [torch.logsumexp(logits[i, ids], 0) for ids in aliases]
        if not torch.isfinite(a) and not torch.isfinite(b): values.append(None); continue
        values.append([float(a), float(b)])
    return values


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--formats', nargs='+', choices=['A', 'B'], default=['A', 'B'])
    ap.add_argument('--readings', nargs='+', default=['R0', 'R1', 'R2', 'R3', 'R4', 'R5'])
    ap.add_argument('--mode', choices=['sequence', 'legacy'], default='sequence')
    ap.add_argument('--legacy-processed', action='store_true', help='Replicate upstream generate() temperature/top-k/top-p score processing.')
    ap.add_argument('--batch-size', type=int, default=16); ap.add_argument('--limit', type=int)
    ap.add_argument('--shard', default='0/1'); ap.add_argument('--repair', action='store_true')
    ap.add_argument('--dtype', choices=['bfloat16', 'float16', 'float32'], default='bfloat16'); args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True); assert not (args.out/'predictions.jsonl').exists()
    os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
    torch.manual_seed(52); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side='left')
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    config = AutoConfig.from_pretrained(args.model, local_files_only=True)
    klass = Gemma3ForConditionalGeneration if config.model_type == 'gemma3' else AutoModelForCausalLM
    start = time.monotonic()
    model = klass.from_pretrained(args.model, local_files_only=True, torch_dtype=getattr(torch, args.dtype),
                                 attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters(): p.requires_grad_(False)
    rows = [json.loads(line) for line in args.data.read_text().splitlines()]
    shard, count = map(int, args.shard.split('/')); assert 0 <= shard < count
    rows = [r for i, r in enumerate(rows) if i % count == shard]
    if args.limit: rows = rows[:args.limit]
    skipped = []
    tasks = list(generate_tasks(rows, tokenizer, args.formats, args.readings, args.mode, args.repair, skipped))
    (args.out/'missing-tasks.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in skipped))
    tasks.sort(key=lambda t: len(t['prompt']))  # Computation order only; selection remains fixed.
    run_config = dict(model_path=str(args.model), model_manifest_sha256=sha(args.model/'manifest.json'),
        data_sha256=sha(args.data), arguments=vars(args) | {'data': str(args.data), 'model': str(args.model), 'out': str(args.out)},
        torch=torch.__version__, transformers=transformers.__version__, seed=52, device=torch.cuda.get_device_name(),
        tasks=len(tasks), missing_tasks=len(skipped), missing_tasks_sha256=sha(args.out/'missing-tasks.jsonl'),
        model_load_seconds=time.monotonic()-start, code_sha256=sha(Path(__file__)))
    (args.out/'reading_map.py').write_bytes(Path(__file__).read_bytes())
    (args.out/'config.json').write_text(json.dumps(run_config, indent=2)+'\n')
    with (args.out/'predictions.jsonl').open('w') as stream:
        for begin in range(0, len(tasks), args.batch_size):
            batch = tasks[begin:begin+args.batch_size]
            if args.mode == 'legacy':
                assert all(t['format'] == 'A' for t in batch)
                scores = legacy_scores(model, tokenizer, batch, args.legacy_processed)
            else:
                enc = [encode_choices(tokenizer, t) for t in batch]
                sequences = [s for ss, n in enc for s in ss]
                common = [n for ss, n in enc for s in ss]
                scored = sequence_scores(model, sequences, common, tokenizer.pad_token_id)
                scores = [scored[i:i+2] for i in range(0, len(scored), 2)]
            for t, score in zip(batch, scores):
                row = t['row']; gold = 0 if args.mode == 'legacy' else t.get('candidate_gold', row['gold'])
                record = {k: row.get(k) for k in ('item_id', 'pair_id', 'cluster_id', 'source', 'construction',
                    'condition', 'question_target', 'source_question_type', 'source_sent_type', 'needs_revision',
                    'matched_question_exact', 'sentence_sha256', 'gold')}
                record.update({k: t[k] for k in ('format', 'reading', 'order', 'prompt_index', 'mapping', 'repair')})
                record.update(mode=args.mode, candidate_gold=gold, prompt_sha256=hashlib.sha256(t['prompt'].encode()).hexdigest(),
                    prompt=t['prompt'], candidates=t['candidates'],
                    prompt_tokens=len(tokenizer.encode(t['prompt'], add_special_tokens=True)),
                    candidate_logprobs=score, p_correct=None, correct=None)
                if score is not None:
                    normalizer = max(score)+math.log(sum(math.exp(s-max(score)) for s in score))
                    record.update(p_correct=math.exp(score[gold]-normalizer), correct=score[gold] > score[1-gold])
                stream.write(json.dumps(record)+'\n')
            stream.flush()
            if begin % (args.batch_size*20) == 0: print(begin, '/', len(tasks), flush=True)
    run_config.update(wall_seconds=time.monotonic()-start, gpu_hours=(time.monotonic()-start)/3600,
                      predictions_sha256=sha(args.out/'predictions.jsonl'), peak_memory_bytes=torch.cuda.max_memory_allocated())
    (args.out/'config.json').write_text(json.dumps(run_config, indent=2)+'\n'); print('DONE', run_config['gpu_hours'], flush=True)


if __name__ == '__main__': main()
