"""Shared definition of "the model stops here", usable across interfaces and model families.

A translation ends in one of two ways depending on the interface:

- **chat**: the model emits an end-of-turn / EOS token;
- **few-shot plain text**: the model emits *any* token whose surface form contains a line break,
  because the translation occupies one line of the prompt's block structure.

Treating only `"\\n"` and `"\\n\\n"` as stop tokens is wrong for BPE vocabularies that merge the
line break into multi-character tokens (this silently voided an earlier few-shot sweep: the stop
symbol never fired and 60% of outputs ran to the length cap). The stop set below is therefore the
full set of vocabulary items whose decoded form contains a newline.
"""

import torch


def build_stop_set(tok, model, interface, extra_stop_ids=None):
    """Return the sorted list of token ids that terminate a translation under this interface.

    `extra_stop_ids` lets a base model be measured through a post-trained sibling's chat template:
    the base checkpoint has no end-of-turn id of its own, so the donor's is supplied.
    """
    extra = [int(e) for e in (extra_stop_ids or [])]
    if interface == "chat":
        eos = model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        ids = sorted(set([int(e) for e in eos if e is not None] + extra))
        if not ids and tok.eos_token_id is not None:
            ids = [int(tok.eos_token_id)]
        if not ids:
            raise ValueError("empty stop set for the chat interface")
        return ids
    # batch_decode over the whole vocabulary: one call into the fast tokenizer instead of
    # ~10^5 Python round-trips (the per-id loop took minutes and stalled parallel jobs)
    vocab_size = len(tok)
    all_ids = list(range(vocab_size))
    decoded = tok.batch_decode([[i] for i in all_ids])
    ids = [i for i, s in zip(all_ids, decoded) if s and "\n" in s]
    eos = model.generation_config.eos_token_id
    eos = eos if isinstance(eos, list) else [eos]
    ids.extend(int(e) for e in eos if e is not None)
    ids.extend(extra)
    if tok.eos_token_id is not None:
        ids.append(int(tok.eos_token_id))
    return sorted(set(ids))


def step0_termination_stats(logits, stop_ids):
    """Per-example termination competitiveness at the first generated position.

    Returns a dict of tensors:
      log_p_stop   logsumexp over the stop set (the probability of ending the translation now)
      log_p_top1   the largest log-probability over non-stop tokens
      margin       log_p_top1 - log_p_stop  (positive means continuing is preferred)
      rank_stop    rank of the best stop token in the full distribution (1 = argmax)
    """
    lp = torch.log_softmax(logits.float(), dim=-1)
    stop = torch.tensor(stop_ids, device=lp.device)
    stop_lp = lp[:, stop]
    log_p_stop = torch.logsumexp(stop_lp, dim=-1)
    best_stop = stop_lp.max(dim=-1).values
    masked = lp.clone()
    masked[:, stop] = -float("inf")
    log_p_top1 = masked.max(dim=-1).values
    rank_stop = (lp > best_stop.unsqueeze(-1)).sum(dim=-1) + 1
    return {"log_p_stop": log_p_stop, "log_p_top1": log_p_top1,
            "margin": log_p_top1 - log_p_stop, "rank_stop": rank_stop}
