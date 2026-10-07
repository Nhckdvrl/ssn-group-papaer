"""E90: identical sentence tokens, question-free source trajectories, native consumer."""
from contextlib import contextmanager
import inspect
from current_open_baseline import prepare as native_prepare
from predicate_frame_hint import prepare as frame_prepare


def prepare(rows, tok):
    native = [t for t in native_prepare(rows, tok)
              if t['operation'] == 'DIRECT' and t['readout'] == 'words']
    early = {(t['row']['item_id'], t['mapping']): t
             for t in frame_prepare(rows, tok) if t['operation'] == 'EARLY_FRAME'}
    tasks = []
    for t in native:
        donor = early[t['row']['item_id'], t['mapping']]
        prefixes = {}
        positions = {}
        tokens = {}
        for name, prompt in [('NATIVE_BANK', t['prompt']), ('FRAME_BANK', donor['prompt'])]:
            prefix = prompt[:prompt.index('\n\nTask:\n')]
            sentence = t['row']['sentence']
            start = prefix.index('\nSentence:\n') + len('\nSentence:\n')
            assert prefix[start:] == sentence
            # Slice the native full tokenization: punctuation/newline tokens can merge
            # at the string cut. No Task/Q token is included in this causal prefix.
            encoded = tok(prompt, add_special_tokens=False, return_offsets_mapping=True)
            pos = [i for i, (a, b) in enumerate(encoded['offset_mapping'])
                   if b > start and a < start + len(sentence)]
            assert pos and all(encoded['offset_mapping'][i][0] >= start for i in pos)
            assert encoded['offset_mapping'][pos[-1]][1] <= prompt.index('Task:', start)
            prefixes[name] = encoded['input_ids'][:pos[-1] + 1]
            positions[name] = pos
            tokens[name] = [encoded['input_ids'][i] for i in pos]
        assert tokens['NATIVE_BANK'] == tokens['FRAME_BANK']
        tasks.append(dict(t, prefixes=prefixes, positions=positions,
                          source_tokens=tokens['NATIVE_BANK']))
    return tasks


def blocks(model):
    found = [(name, module) for name, module in model.named_modules()
             if name.endswith('language_model.layers')]
    assert len(found) == 1, [name for name, _ in found]
    return found[0]


def hidden(output):
    return output[0] if isinstance(output, tuple) else output


def capture(model, decoder, ids, positions):
    import torch
    bank = {}
    handles = []
    for layer, block in enumerate(decoder):
        def hook(module, inputs, output, layer=layer):
            bank[layer] = hidden(output)[0, positions].detach().clone()
        handles.append(block.register_forward_hook(hook))
    try:
        x = torch.tensor([ids], device=model.device)
        kwargs = dict(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False)
        if 'logits_to_keep' in inspect.signature(model.forward).parameters:
            kwargs['logits_to_keep'] = 1
        with torch.inference_mode():
            model(**kwargs)
    finally:
        for h in handles:
            h.remove()
    assert len(bank) == len(decoder)
    return bank


@contextmanager
def hooks(decoder, bank, positions, verify=False):
    import torch
    handles = []
    counts = [0] * len(decoder)
    for layer, block in enumerate(decoder):
        def hook(module, inputs, output, layer=layer):
            original = hidden(output)
            # Cached decoding consists of one new token; only the prefill contains Source.
            if original.shape[1] <= max(positions):
                return output
            assert original.shape[0] == 1
            counts[layer] += 1
            patched = original.clone()
            patched[0, positions] = bank[layer]
            if verify:
                assert torch.equal(patched[0, positions], bank[layer])
                mask = torch.ones(original.shape[1], device=original.device, dtype=torch.bool)
                mask[positions] = False
                assert torch.equal(patched[0, mask], original[0, mask])
            return (patched, *output[1:]) if isinstance(output, tuple) else patched
        handles.append(block.register_forward_hook(hook))
    try:
        yield counts
    finally:
        for h in handles:
            h.remove()


def generate(model, tok, prompt, decoder=None, bank=None, positions=None, verify=False):
    import torch
    ids = tok.encode(prompt, add_special_tokens=False)
    x = torch.tensor([ids], device=model.device)
    def run():
        with torch.inference_mode():
            y = model.generate(input_ids=x, attention_mask=torch.ones_like(x),
                               do_sample=False, max_new_tokens=32, use_cache=True,
                               pad_token_id=tok.pad_token_id)
        return y[0, len(ids):].tolist()
    if bank is None:
        return run()
    with hooks(decoder, bank, positions, verify) as counts:
        result = run()
        assert counts == [1] * len(decoder), counts
    return result


def instrument(model, tok, decoder, task):
    from data_v2 import digest
    ids = tok.encode(task['prompt'], add_special_tokens=False)
    pos = task['positions']['NATIVE_BANK']
    native = generate(model, tok, task['prompt'])
    assert generate(model, tok, task['prompt']) == native
    self_bank = capture(model, decoder, ids, pos)
    assert generate(model, tok, task['prompt'], decoder, self_bank, pos, True) == native
    del self_bank
    # Prefix layout may differ numerically in BF16; record it and use the matched native bank.
    prefix_bank = capture(model, decoder, task['prefixes']['NATIVE_BANK'], pos)
    bank_answer = generate(model, tok, task['prompt'], decoder, prefix_bank, pos, True)
    return dict(item_id=task['row']['item_id'], prompt_sha256=digest(task['prompt']),
                native_tokens=native, native_prefix_bank_tokens=bank_answer,
                self_bank_exact_match=True, native_repeat_exact_match=True,
                prefix_bank_answer_matches_native=bank_answer == native,
                source_tokens=len(pos), layers=len(decoder))
