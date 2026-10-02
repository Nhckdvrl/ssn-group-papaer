#!/usr/bin/env python3
"""Gold-blind annotation drafts, never evaluation ground truth."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RUBRIC = '''Annotate a public pragmatic comprehension item. Do not answer its multiple-choice question.
The gold answer and category are deliberately hidden. Distinguish what is said from what is inferred.
inference_licensed is yes only when the context supports a specific nonliteral speaker meaning;
no only when the warranted interpretation remains literal; ambiguous if evidence is insufficient.
For each of options A through E assign one semantic class:
literal: compatible with what is explicitly said and entails no added speaker intent;
pragmatic-supported: goes beyond literal content and is supported by the context;
pragmatic-unsupported: adds speaker intent or implication without contextual support;
contradiction: conflicts with explicit facts (not just a different intention);
irrelevant: does not interpret the utterance;
none-of-above: a meta-option that asserts none of the other options is correct.
None-of-above is not a literal interpretation. Be conservative about licensing and keep ambiguity.
Return one JSON object only, with keys inference_licensed (yes/no/ambiguous),
option_classes (object with keys A,B,C,D,E), rationale (brief text), confidence (low/medium/high).
Item:
'''
CLASSES = set('literal pragmatic-supported pragmatic-unsupported contradiction irrelevant none-of-above'.split())


def decode_json(raw):
    for i, ch in enumerate(raw):
        if ch != '{':
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(raw[i:])
            assert obj['inference_licensed'] in {'yes', 'no', 'ambiguous'}
            assert set(obj['option_classes']) == set('ABCDE')
            assert all(v in CLASSES for v in obj['option_classes'].values())
            assert obj['confidence'] in {'low', 'medium', 'high'}
            assert isinstance(obj['rationale'], str)
            return obj
        except (ValueError, KeyError, TypeError, AssertionError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--model-id', required=True)
    ap.add_argument('--revision', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    data = args.root / 'data/multiprageval.jsonl'
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    cells = {}
    for r in sorted((r for r in rows if r['language']=='english'), key=lambda r:int(r['item_id'])):
        cells.setdefault((r['phenomenon'], r['gold']), r)
    assert len(cells)==25
    chosen = list(cells.values())
    start = time.monotonic()
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side='left')
    if tok.pad_token_id is None:
        tok.pad_token=tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        torch_dtype=torch.bfloat16, device_map={'':0}, attn_implementation='sdpa').eval()
    prompts = [tok.apply_chat_template([{'role':'user','content':RUBRIC+r['prompt']}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in chosen]
    manifest = {'model':args.model_id,'revision':args.revision,'n':25,'gold_visible':False,
        'rubric':RUBRIC,'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prompt_sha256':hashlib.sha256(json.dumps(prompts).encode()).hexdigest(),
        'decoding':{'do_sample':False,'max_new_tokens':1024,'batch_size':5,'enable_thinking':False},
        'item_ids':[r['item_id'] for r in chosen], 'status':'draft; human review pending; not gold'}
    (args.output/'config.json').write_text(json.dumps(manifest,indent=2)+'\n')
    outputs=[]
    with (args.output/'annotations.jsonl').open('w') as f:
        for i in range(0,25,5):
            inp=tok(prompts[i:i+5],padding=True,return_tensors='pt',add_special_tokens=False).to(model.device)
            with torch.inference_mode():
                gen=model.generate(**inp,do_sample=False,max_new_tokens=1024,pad_token_id=tok.pad_token_id)
            for r, tokens in zip(chosen[i:i+5],gen[:,inp.input_ids.shape[1]:]):
                raw=tok.decode(tokens,skip_special_tokens=True)
                rec={'item_id':r['item_id'],'raw':raw,'annotation':decode_json(raw)}
                outputs.append(rec)
                f.write(json.dumps(rec,ensure_ascii=False)+'\n')
            f.flush()
            print(json.dumps({'done':len(outputs)}),flush=True)
    manifest.update(wall_seconds=time.monotonic()-start,schema_valid=sum(r['annotation'] is not None for r in outputs))
    (args.output/'config.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest | {'rubric':'saved in config.json'}))


if __name__=='__main__':
    main()
