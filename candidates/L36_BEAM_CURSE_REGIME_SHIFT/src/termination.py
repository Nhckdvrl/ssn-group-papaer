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


def build_stop_set(tok, model, interface):
    """Return the sorted list of token ids that terminate a translation under this interface."""
    if interface == "chat":
        eos = model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        return sorted(set(int(e) for e in eos if e is not None))
    ids = []
    vocab_size = len(tok)
    for i in range(vocab_size):
        s = tok.convert_ids_to_tokens(i)
        if s is None:
            continue
        if "\n" in tok.convert_tokens_to_string([s]):
            ids.append(i)
    eos = model.generation_config.eos_token_id
    eos = eos if isinstance(eos, list) else [eos]
    ids.extend(int(e) for e in eos if e is not None)
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
