#!/usr/bin/env python3
"""E20: original betting task; fixed parser, all generations retained."""
import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
from epitome_data import prepare
from run_native_readout import next_logits


def parse_bets(raw, choices):
    first = raw.split('\n', 1)[0].strip()
    pattern = ', '.join(re.escape(c) + ': ([0-9]+)' for c in choices)
    match = re.match(pattern, first)
    bets = [int(x) for x in match.groups()] if match else None
    valid = bets is not None and all(0 <= x <= 100 for x in bets) and sum(bets) == 100
    return {'first_line': first, 'original_regex_match': match is not None,
            'bets': bets, 'valid': valid, 'sum': sum(bets) if bets else None,
            'trailing_text': first[match.end():] if match else None}


def build(root, lo, hi):
    stimuli, _, audit = prepare(root)
    source = root/'upstream/epitome/scalar_implicature/src/models/run_gpt.py'
    tree = ast.parse(source.read_text())
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'PROMPT_INTRO' for t in n.targets)]
    assert len(assignments) == 1
    intro = ast.literal_eval(assignments[0].value)
    # Exact original warmups plus invalid tests; no provider module is executed.
    assert parse_bets('dog: 55, alligator: 1, cat: 44, whale: 0', ['dog','alligator','cat','whale'])['bets'] == [55,1,44,0]
    assert parse_bets('0: 6, 1: 25, 2: 38, 3: 25, 4: 6', list('01234'))['valid']
    assert not parse_bets('0: 51, 1: 50', list('01'))['valid']
    assert not parse_bets('\n0: 50, 1: 50', list('01'))['valid']
    selected = [r for r in stimuli if r['task'] == 'si' and lo <= r['item'] <= hi]
    assert len(selected) == (hi-lo+1)*19
    for r in selected:
        story, question = r['prompt'].rsplit('\nQ:', 1)
        assert question.endswith('\nA:')
        question = question[:-3].lstrip(' ')
        assert r['prompt'] in {story+'\nQ: '+question+'\nA:', story+'\nQ:'+question+'\nA:'}
        r['betting_prompt'] = (intro + f"Passage: {story}\nQuestion: {question}\n"
                               + f"Candidates: {', '.join(r['choices'])}\nAnswers:")
    audit.update(provider_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 intro_sha256=hashlib.sha256(intro.encode()).hexdigest(),
                 selected_si_prompt_sha256=hashlib.sha256(json.dumps([(r['key'],r['prompt']) for r in selected],ensure_ascii=False).encode()).hexdigest())
    return selected, audit


class FirstNewline(StoppingCriteria):
    def __init__(self, tok, offset):
        self.tok, self.offset = tok, offset

    def __call__(self, input_ids, scores, **kwargs):
        texts = self.tok.batch_decode(input_ids[:, self.offset:], skip_special_tokens=True)
        return torch.tensor(['\n' in x for x in texts], device=input_ids.device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--model-id')
    ap.add_argument('--revision')
    ap.add_argument('--output', type=Path)
    ap.add_argument('--item-min', type=int, default=1)
    ap.add_argument('--item-max', type=int, default=40)
    ap.add_argument('--prepare-only', action='store_true')
    ap.add_argument('--interface',choices=['bare','common-chat'],required=True)
    ap.add_argument('--common-template',type=Path,required=True)
    a = ap.parse_args()
    rows, audit = build(a.root, a.item_min, a.item_max)
    if a.prepare_only:
        print(json.dumps({'n':len(rows),'items':sorted({r['item'] for r in rows}), 'audit':audit}))
        return
    assert all([a.model,a.model_id,a.revision,a.output]) and not a.output.exists()
    a.output.mkdir(parents=True)
    start = time.monotonic()
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    seq = AutoConfig.from_pretrained(a.model, local_files_only=True).is_encoder_decoder
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True, padding_side='left', use_fast=not seq)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    template = str(a.common_template) if a.interface=='common-chat' else None
    tok.chat_template=AutoTokenizer.from_pretrained(a.common_template,local_files_only=True).chat_template if template else None
    texts = [tok.apply_chat_template([{'role':'user','content':r['betting_prompt']}],
             tokenize=False, add_generation_prompt=True, enable_thinking=False)
             if template else r['betting_prompt'] for r in rows]
    ids = [tok.encode(p, add_special_tokens=seq) for p in texts]
    cls = AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
    model = cls.from_pretrained(a.model, local_files_only=True, torch_dtype=torch.float32,
                               device_map={'':0}, weights_only=True).eval()

    def inputs(tokens):
        return tok.pad({'input_ids':tokens,'attention_mask':[[1]*len(x) for x in tokens]},
                       padding=True,return_tensors='pt').to(model.device)

    @torch.inference_mode()
    def probabilities(tokens):
        inp = inputs(tokens)
        if model.config.model_type == 'gpt2':
            inp['position_ids'] = (inp.attention_mask.long().cumsum(-1)-1).masked_fill(inp.attention_mask==0,0)
        return next_logits(model,inp).softmax(-1)

    probe = ids[:7]+ids[-1:]
    many = probabilities(probe)
    deltas = [float((probabilities([probe[i]])[0]-many[i]).abs().max()) for i in [0,7]]
    (a.output/'numerical-control.json').write_text(json.dumps({'first_last_prob_delta':deltas,'pass':max(deltas)<1e-3},indent=2))
    assert max(deltas) < 1e-3, 'Numerical gate failed before generation'
    generation = {'do_sample':False,'max_new_tokens':50,'pad_token_id':tok.pad_token_id,
                  'repetition_penalty':1.0}
    config = {'task':'epitome_native_betting','model':a.model_id,'revision':a.revision,
              'n':len(rows),'items':sorted({r['item'] for r in rows}), 'dtype':'float32','tf32':False,
              'generation':generation,'inherited_generation_defaults':model.generation_config.to_dict(),
              'enable_thinking':False,'common_template':template,'interface':a.interface,'numerical_gate_pass':True,
              'input_token_hash':hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
              'audit':audit,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'helper_sha256':hashlib.sha256((Path(__file__).parent/'epitome_data.py').read_bytes()).hexdigest()}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    valid = truncated = 0
    with (a.output/'predictions.jsonl').open('w') as f:
        for offset in range(0,len(rows),8):
            batch = rows[offset:offset+8]
            inp = inputs(ids[offset:offset+8])
            begin = 1 if seq else inp.input_ids.shape[1]
            with torch.inference_mode():
                output = model.generate(**inp,**generation,
                         stopping_criteria=StoppingCriteriaList([FirstNewline(tok,begin)]))
            generated = output[:,begin:]
            raw = tok.batch_decode(generated,skip_special_tokens=True)
            eos = model.generation_config.eos_token_id
            eos = [eos] if isinstance(eos,int) else eos or []
            for r, text, tokens in zip(batch,raw,generated):
                parsed = parse_bets(text,r['choices'])
                hit_limit = tokens.numel() >= 50 and '\n' not in text and not any(t in eos for t in tokens.tolist())
                rec = {k:v for k,v in r.items() if k not in ['prompt','betting_prompt']}
                rec.update(raw_response=text,**parsed,truncated=hit_limit,
                           prompt_sha256=hashlib.sha256(r['betting_prompt'].encode()).hexdigest())
                f.write(json.dumps(rec,ensure_ascii=False)+'\n')
                valid += int(parsed['valid']); truncated += int(hit_limit)
            f.flush()
            print(json.dumps({'done':min(offset+8,len(rows)),'total':len(rows),'valid':valid,'truncated':truncated}),flush=True)
    summary = {'n':len(rows),'valid':valid,'invalid':len(rows)-valid,'truncated':truncated}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2))
    config.update(complete=True,wall_seconds=time.monotonic()-start,
                  peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,**summary,'seconds':config['wall_seconds']}),flush=True)


if __name__ == '__main__':
    main()
