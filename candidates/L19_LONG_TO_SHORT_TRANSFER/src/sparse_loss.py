"""Completion-only loss without materialising the full vocabulary logit tensor.

At 24k context the logits alone would be 24k x 128k x 2 bytes = 6 GB per sequence
(more in fp32), which dominates memory even though only a handful of positions carry
a label. We run the transformer body, gather the hidden states at labelled positions,
and apply the LM head only there. Mathematically identical to the dense computation.
"""
import torch, torch.nn.functional as F


def sparse_causal_loss(model, input_ids, labels, attention_mask=None):
    out = model.model(input_ids=input_ids, attention_mask=attention_mask)
    h = out.last_hidden_state                       # [B, T, H]
    # next-token prediction: position t predicts labels[t+1]
    tgt = labels[:, 1:]
    hs = h[:, :-1, :]
    sel = tgt != -100
    if sel.sum() == 0:
        return h.sum() * 0.0
    hsel = hs[sel]                                  # [N, H]
    tsel = tgt[sel]                                 # [N]
    logits = model.lm_head(hsel).float()            # [N, V]
    return F.cross_entropy(logits, tsel)
