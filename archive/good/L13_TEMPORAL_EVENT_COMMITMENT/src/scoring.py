"""Model loading, chat formatting, and constrained label scoring for L13.

Scoring is done on first-token log-probabilities over the candidate answer
tokens, normalised over the candidate set. No sampling is involved for any
scored quantity; the only sampling-free generation is the timeline/paraphrase
turn, which is greedy.
"""
import math

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model(model_id, device, dtype="bfloat16", revision=None):
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        revision=revision,
        torch_dtype=getattr(torch, dtype),
        device_map=None,
    ).to(device)
    model.eval()
    return tok, model


def render(tok, messages, thinking=False):
    """Apply the chat template, disabling reasoning mode where supported."""
    kwargs = dict(tokenize=False, add_generation_prompt=True)
    try:
        return tok.apply_chat_template(messages, enable_thinking=thinking, **kwargs)
    except TypeError:
        return tok.apply_chat_template(messages, **kwargs)


def _candidate_token_ids(tok, text):
    """Token ids that can begin a generation of `text` (with/without space)."""
    ids = set()
    for variant in (text, " " + text):
        enc = tok.encode(variant, add_special_tokens=False)
        if enc:
            ids.add(enc[0])
    return sorted(ids)


def build_candidate_map(tok, candidates):
    return {c: _candidate_token_ids(tok, c) for c in candidates}


@torch.no_grad()
def score_candidates(tok, model, prompts, candidate_map, device, batch_size=16):
    """Return, per prompt, a normalised distribution over the candidate strings."""
    out = []
    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        enc = tok(chunk, return_tensors="pt", padding=True, add_special_tokens=False)
        enc = {k: v.to(device) for k, v in enc.items()}
        logits = model(**enc).logits[:, -1, :].float()
        logprobs = torch.log_softmax(logits, dim=-1)
        for row in logprobs:
            raw = {}
            for cand, ids in candidate_map.items():
                vals = [row[i].item() for i in ids]
                m = max(vals)
                raw[cand] = m + math.log(sum(math.exp(v - m) for v in vals))
            m = max(raw.values())
            exp = {k: math.exp(v - m) for k, v in raw.items()}
            z = sum(exp.values())
            out.append({k: v / z for k, v in exp.items()})
    return out


@torch.no_grad()
def generate(tok, model, prompts, device, max_new_tokens=160, batch_size=8):
    """Greedy generation, used only for the timeline/paraphrase turn."""
    out = []
    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        enc = tok(chunk, return_tensors="pt", padding=True, add_special_tokens=False)
        enc = {k: v.to(device) for k, v in enc.items()}
        gen = model.generate(
            **enc,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            pad_token_id=tok.pad_token_id,
        )
        for i in range(gen.shape[0]):
            new = gen[i, enc["input_ids"].shape[1] :]
            out.append(tok.decode(new, skip_special_tokens=True).strip())
    return out
