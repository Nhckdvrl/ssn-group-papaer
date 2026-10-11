"""Input-independent source state vs input-dependent query relay.

Keep cache positions fixed and mask all demo access after the capsule forms.
No trained readout, layer selection, or correctness filtering.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import NAMES, make_contexts
from e59_mediation import encode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--stage', choices=['discovery', 'confirmation'], required=True)
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--dtype', choices=['bfloat16', 'float32'], default='float32')
    a = ap.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    contexts = make_contexts(a.stage, a.n, a.seed)
    labels = ['yes', 'no'] if a.stage == 'discovery' else ['toxic', 'safe']
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True,
             dtype=getattr(torch, a.dtype), device_map='cuda', attn_implementation='eager').eval()
    label_ids = [tok.encode(' ' + s, add_special_tokens=False)[0] for s in labels]
    assert all(len(tok.encode(' ' + s, add_special_tokens=False)) == 1 for s in labels)
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    audit = {'active': False, 'masked': [], 'max_mass': 0.0}
    for layer in model.model.layers:
        def hook(module, args, kwargs, output):
            if audit['active'] and audit['masked']:
                mass = output[1][..., audit['masked']].float().sum(-1).max()
                audit['max_mass'] = max(audit['max_mass'], float(mass))
            return output
        layer.self_attn.register_forward_hook(hook, with_kwargs=True)

    def forward(cache, ids, allowed):
        cache = copy.deepcopy(cache)
        plen = cache.get_seq_length() if cache is not None else 0
        ids = torch.tensor([ids], device='cuda')
        mask = torch.ones((1, plen + ids.shape[1]), dtype=torch.long, device='cuda')
        if plen:
            mask[:, :plen] = 0
            mask[:, allowed] = 1
        audit.update(active=True, masked=[i for i in range(plen) if i not in set(allowed)])
        out = model(input_ids=ids, attention_mask=mask,
                    position_ids=torch.arange(plen, plen + ids.shape[1], device='cuda')[None],
                    past_key_values=cache, use_cache=True, logits_to_keep=1)
        audit['active'] = False
        logits = out.logits[0, -1].float()
        return out.past_key_values, float(logits[label_ids[1]] - logits[label_ids[0]])

    def prefix(ctx, donor='base', instruction=False):
        ids, _ = encode(tok, ctx, labels, 'synthetic', donor, instruction)
        cache, _ = forward(None, ids, [])
        return cache

    errors = []
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in contexts))
    with (dest / 'behavior.jsonl').open('w') as f, torch.inference_mode():
        for ci, ctx in enumerate(contexts):
            demos = {d['word'] for d in ctx['demos']}
            assert all(q['word'] not in demos for q in ctx['queries'])
            p = {'base': prefix(ctx), 'flip': prefix(ctx, 'label'), 'instruction': prefix(ctx, instruction=True)}
            single = {}
            capsules = {}
            for s in (0, 1):
                sc = dict(ctx, demos=[d for d in ctx['demos'] if d['source'] == s])
                single[s] = {'base': prefix(sc), 'flip': prefix(sc, 'label')}
                field = enc(f'Source: {NAMES[s]}\n')
                name = enc(' ' + NAMES[s])
                assert len(name) == 1 and field.count(name[0]) == 1
                ni = field.index(name[0])
                for key, parent in [(k, c) for k, c in p.items()] + [('single.' + k, c) for k, c in single[s].items()]:
                    plen = parent.get_seq_length()
                    cap, _ = forward(parent, field, list(range(plen)))
                    capsules[s, key] = (cap, plen, field, ni)
                    if key in ('base', 'single.base'):
                        null, _ = forward(parent, field, [])
                        capsules[s, key + '.null'] = (null, plen, field, ni)
            result = []
            for qi, q in enumerate(ctx['queries']):
                s = q['source']
                suffix = enc(f'Item: {q["word"]}\nLabel:')
                scores = {}
                for key in ('base', 'flip', 'instruction', 'single.base', 'single.flip'):
                    cap, plen, field, ni = capsules[s, key]
                    width = cap.get_seq_length()
                    _, scores['native.' + key] = forward(cap, suffix, list(range(width)))
                    _, scores['clause.' + key] = forward(cap, suffix, list(range(plen, width)))
                    if key in ('base', 'flip'):
                        _, scores['name.' + key] = forward(cap, suffix, [plen + ni])
                    if key in ('base', 'single.base'):
                        null = capsules[s, key + '.null'][0]
                        _, scores['clause.' + key + '.null'] = forward(null, suffix, list(range(plen, width)))
                cap, plen, field, ni = capsules[s, 'base']
                _, scores['native.unsplit'] = forward(p['base'], field + suffix, list(range(plen)))
                errors.append(abs(scores['native.base'] - scores['native.unsplit']))
                original = enc(f'Item: {q["word"]}\nSource: {NAMES[s]}\nLabel:')
                assert tok.decode([original[-1]]) == ':'
                for key in ('base', 'flip'):
                    plen = p[key].get_seq_length()
                    _, scores['original.' + key] = forward(p[key], original, list(range(plen)))
                    relay, _ = forward(p[key], original[:-1], list(range(plen)))
                    _, scores['answer.' + key] = forward(relay, original[-1:], list(range(plen, relay.get_seq_length())))
                    if key == 'base':
                        _, scores['original.split'] = forward(relay, original[-1:], list(range(relay.get_seq_length())))
                        errors.append(abs(scores['original.base'] - scores['original.split']))
                        null, _ = forward(p[key], original[:-1], [])
                        _, scores['answer.null'] = forward(null, original[-1:], list(range(plen, null.get_seq_length())))
                result.append(scores)
                if ci == 0 and qi == 0:
                    (dest / 'layout.json').write_text(json.dumps({'prefix_length': capsules[s, 'base'][1],
                        'source_field_ids': field, 'source_name_offset': ni, 'suffix_ids': suffix,
                        'query_ids': original, 'query_text': tok.decode(original)}, indent=2))
            assert audit['max_mass'] == 0.0, audit
            f.write(json.dumps({'context': ci, 'signs': [2 * q['label'] - 1 for q in ctx['queries']],
                               'scores': {k: [r[k] for r in result] for k in result[0]}}) + '\n')
            f.flush()
            if ci % 4 == 0:
                print(ci, round(time.time() - t0, 1), flush=True)
    assert max(errors) <= 0.1, max(errors)
    run = {'args': vars(a), 'seconds': time.time() - t0, 'sanity_max_error': max(errors),
           'masked_attention_mass_max': audit['max_mass'], 'torch': torch.__version__,
           'transformers': transformers.__version__, 'host': platform.node(), 'gpu': torch.cuda.get_device_name(),
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'config_sha256': hashlib.sha256((Path(a.model) / 'config.json').read_bytes()).hexdigest(),
           'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    (dest / 'run.json').write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)

if __name__ == '__main__':
    main()
