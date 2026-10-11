"""POST-HOC formatting audit; preserve all preregistered strict metrics.

This accepts only explicit Answer/Final Answer lines, after removing Markdown
decoration. It never selects prose mentions, composite codes, or gold labels.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from transformers import AutoTokenizer
from analyze_e58 import interval


def decorated_answer(text, labels, thinking):
    text = text.replace('<|im_end|>', '').replace('<|endoftext|>', '')
    if thinking and '</think>' not in text:
        return -1, 'thinking_not_closed'
    text = text.rsplit('</think>', 1)[-1]
    answers = []
    explicit = []
    for line in text.splitlines():
        clean = line.strip().replace('*', '').replace('`', '').replace('_', '')
        clean = re.sub(r'^#{1,6}\s+', '', clean).strip()
        hit = re.fullmatch(r'(?:Final\s+)?Answer\s*:\s*(.*?)\s*', clean, re.I)
        if hit:
            value = hit[1].rstrip('.!').strip().lower()
            explicit.append(value)
            if value in [s.lower() for s in labels]:
                answers.append([s.lower() for s in labels].index(value))
    if len(set(answers)) > 1:
        return -1, 'conflicting_answer_lines'
    if answers:
        # A later explicit refusal/composite code invalidates earlier guesses.
        if explicit[-1] not in [s.lower() for s in labels]:
            return -1, 'noncandidate_final_answer'
        return answers[-1], 'valid_decorated'
    return -1, 'noncandidate_final_answer' if explicit else 'no_explicit_answer_line'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('--model', required=True)
    args = ap.parse_args()
    d = Path(args.directory)
    paired = (d / 'trajectories.jsonl').exists()
    filename = 'trajectories.jsonl' if paired else 'generations.jsonl'
    rs = [json.loads(line) for line in (d / filename).read_text().splitlines()]
    prompts = {r['uid']: r for r in map(json.loads, (d / 'prompts.jsonl').read_text().splitlines())}
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True) if paired else None
    audited = []
    for r in rs:
        for horizon in ['96', '2048', '4096'] if paired else ['original']:
            strict = r['reads'][horizon] if paired else r
            text = tok.decode(r['tokens'][:int(horizon)], skip_special_tokens=False) if paired else r['text']
            labels = prompts[r['uid']]['labels']
            pred, status = decorated_answer(text, labels, r['interface'] == 'thinking_instruction')
            audited.append({'uid': r['uid'], 'context': r['context'], 'schema': r['schema'],
                            'interface': r['interface'], 'horizon': horizon, 'gold': r['gold'],
                            'strict_prediction': strict['prediction'], 'prediction': pred,
                            'parser_status': status, 'truncated': strict['truncated'],
                            'final_400_chars': text[-400:]})
    groups = sorted(set((r['schema'], r['interface'], r['horizon']) for r in audited))
    out = {'status': 'POST-HOC', 'parser_rule': decorated_answer.__doc__,
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'conditions': {}, 'limitations': ['Observed Markdown misses motivated this audit.',
            'Strict original results remain authoritative for their registered readout.',
            'Semantic parser must be fixed before independent confirmation; this audit is not confirmation.',
            'No prose inference, composite-code stripping, gold-dependent selection, or survivor filtering.']}
    for schema, interface, horizon in groups:
        rows = [r for r in audited if (r['schema'], r['interface'], r['horizon']) == (schema, interface, horizon)]
        contexts = sorted(set(r['context'] for r in rows))
        metrics = {'accuracy': [], 'valid_format': [], 'strict_accuracy': [], 'truncated': [], 'recovered_correct': [], 'lost_strict_correct': []}
        for ci in contexts:
            batch = [r for r in rows if r['context'] == ci]
            metrics['accuracy'].append(np.mean([r['prediction'] == r['gold'] for r in batch]))
            metrics['valid_format'].append(np.mean([r['prediction'] >= 0 for r in batch]))
            metrics['strict_accuracy'].append(np.mean([r['strict_prediction'] == r['gold'] for r in batch]))
            metrics['truncated'].append(np.mean([r['truncated'] for r in batch]))
            metrics['recovered_correct'].append(np.mean([r['strict_prediction'] < 0 and r['prediction'] == r['gold'] for r in batch]))
            metrics['lost_strict_correct'].append(np.mean([r['strict_prediction'] == r['gold'] and r['prediction'] != r['gold'] for r in batch]))
        out['conditions']['.'.join((schema, interface, horizon))] = {
            **{name: interval(np.array(values)) for name, values in metrics.items()},
            'parser_status_counts': dict(Counter(r['parser_status'] for r in rows))}
    (d / 'format_audit.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in audited))
    (d / 'format_audit.json').write_text(json.dumps(out, indent=2))
    print(d, {k: {stat: value[stat]['mean'] for stat in ['accuracy', 'valid_format', 'strict_accuracy', 'lost_strict_correct']}
              for k, value in out['conditions'].items() if k.endswith(('original', '4096'))})


if __name__ == '__main__':
    main()
