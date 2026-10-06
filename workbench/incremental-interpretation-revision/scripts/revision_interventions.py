"""Sentence-bounded diagnostic masks; no future question/answer access.

This is an instrument helper. Scientific use requires its own experiment card.
"""
import torch


def word_character_spans(sentence):
    import re
    return [(m.start(), m.end()) for m in re.finditer(r'\S+', sentence)]


def token_region(offsets, start, end):
    return [i for i, (a, b) in enumerate(offsets) if b > a and a < end and b > start]


def sentence_regions(tokenizer, prompt, row):
    start = prompt.rfind(row['sentence'])
    assert start >= 0
    end = start+len(row['sentence'])
    encoded = tokenizer(prompt, return_offsets_mapping=True)
    offsets = encoded['offset_mapping']
    sentence_tokens = token_region(offsets, start, end)
    assert sentence_tokens
    words = word_character_spans(row['sentence'])
    span = row['amb_span']
    assert span is not None and 0 <= span[0] < span[1] <= len(words)
    ambiguous = token_region(offsets, start+words[span[0]][0], start+words[span[1]-1][1])
    assert ambiguous and set(ambiguous) <= set(sentence_tokens)
    return encoded['input_ids'], sentence_tokens, ambiguous


def oracle_mask(length, sentence_tokens, query_tokens, dtype, device='cpu'):
    """Relax only selected query rows to the sentence; all other rows stay causal."""
    assert query_tokens and set(query_tokens) <= set(sentence_tokens)
    assert all(0 <= i < length for i in sentence_tokens)
    allowed = torch.ones(length, length, dtype=torch.bool, device=device).tril()
    for query in query_tokens: allowed[query, sentence_tokens] = True
    mask = torch.zeros(length, length, dtype=dtype, device=device)
    mask.masked_fill_(~allowed, torch.finfo(dtype).min)
    return mask[None, None]


def cut_readout_mask(length, cut_tokens, answer_positions, dtype, device='cpu'):
    """Causal baseline, then cut preselected readout edges without leaking futures."""
    allowed = torch.ones(length, length, dtype=torch.bool, device=device).tril()
    for query in answer_positions:
        assert 0 <= query < length
        for source in cut_tokens:
            assert 0 <= source <= query
            allowed[query, source] = False
        assert allowed[query].any(), 'Cannot remove every key from an attention row'
    mask = torch.zeros(length, length, dtype=dtype, device=device)
    mask.masked_fill_(~allowed, torch.finfo(dtype).min)
    return mask[None, None]
